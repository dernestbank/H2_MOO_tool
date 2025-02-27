# utils/optimization.py

import numpy as np

# Pareto-based algorithms
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.algorithms.moo.spea2 import SPEA2
from pymoo.algorithms.moo.moead import MOEAD

# Single-objective GA
from pymoo.algorithms.soo.nonconvex.ga import GA

from pymoo.termination import get_termination
from pymoo.core.problem import ElementwiseProblem
from pymoo.optimize import minimize

from utils.models import cost_function, eta_total

###############################################################################
# PEMProblem with 21 Constraints
###############################################################################

class PEMProblem(ElementwiseProblem):
    """
    PEM Problem with 21 constraints for an anode + cathode design + global constraints:
    - Decision Variables (6):
        x = [delta_a, eps_a, S_cat_a, delta_c, eps_c, S_cat_c]

    - 2 Objectives:
        1) cost_total
        2) overpotential_total

    - 21 Constraints total:
      Anode (9):
        1)  0.001 ≤ eps_a ≤ 0.999 => 2 constraints
        2)  delta_a_min ≤ delta_a ≤ delta_a_max => 2
        3)  Scat_a_min ≤ S_cat_a ≤ Scat_a_max => 2
        4)  S_cat_a*(1-eps_a)*delta_a >= SA_a_min => 1
        5)  L_a_min ≤ rho_cat_a * delta_a * (1-eps_a) ≤ L_a_max => 2

      Cathode (9):
        same structure => total 9

      Global (3):
        j_min ≤ j ≤ j_max => 2
        eta_total ≤ eta_max => 1
    """

    def __init__(self,
                 # Operating, geometry, etc.
                 A_cell, j, R, T, alpha, n, F,
                 # Anode
                 C_bulk_a, D_a, #tau_a,
                 # Cathode
                 C_bulk_c, D_c, #tau_c,
                 eta_max,
                 # Catalyst Anode
                 rho_cat_a, c_cat_a, j0_a, a_a, b_a,
                 # Catalyst Cathode
                 rho_cat_c, c_cat_c, j0_c, a_c, b_c,
                 # Constraints
                 eps_a_min, eps_a_max,
                 eps_c_min, eps_c_max,
                 delta_a_min, delta_a_max,
                 delta_c_min, delta_c_max,
                 Scat_a_min, Scat_a_max,
                 Scat_c_min, Scat_c_max,
                 L_a_min, L_a_max,
                 L_c_min, L_c_max,
                 SA_a_min, SA_c_min,
                 j_min, j_max,
                 # we do not forcibly link tau to eps here
                 # we let user specify or choose some correlation if wanted
                 tau_a, tau_c,
                 # We have 21 constraints
                 n_var=6, n_obj=2, n_constr=22):
        # x = [δ_a, eps_a, S_cat_a, δ_c, eps_c, S_cat_c]
        super().__init__(
            n_var=n_var,
            n_obj=n_obj,
            n_constr=n_constr,
            xl=[delta_a_min, eps_a_min, Scat_a_min,
                delta_c_min, eps_c_min, Scat_c_min],
            xu=[delta_a_max, eps_a_max, Scat_a_max,
                delta_c_max, eps_c_max, Scat_c_max]
        )
        self.A_cell = A_cell
        self.j = j
        self.R = R
        self.T = T
        self.alpha = alpha
        self.n = n
        self.F = F

        # Anode side
        self.C_bulk_a = C_bulk_a
        self.D_a = D_a
        self.tau_a = tau_a

        # Cathode side
        self.C_bulk_c = C_bulk_c
        self.D_c = D_c
        self.tau_c = tau_c

        self.eta_max = eta_max

        # Catalyst anode
        self.rho_cat_a = rho_cat_a
        self.c_cat_a   = c_cat_a
        self.j0_a      = j0_a
        self.a_a       = a_a
        self.b_a       = b_a

        # Catalyst cathode
        self.rho_cat_c = rho_cat_c
        self.c_cat_c   = c_cat_c
        self.j0_c      = j0_c
        self.a_c       = a_c
        self.b_c       = b_c

        # Bounds for constraints
        self.eps_a_min, self.eps_a_max = eps_a_min, eps_a_max
        self.eps_c_min, self.eps_c_max = eps_c_min, eps_c_max
        self.delta_a_min, self.delta_a_max = delta_a_min, delta_a_max
        self.delta_c_min, self.delta_c_max = delta_c_min, delta_c_max
        self.Scat_a_min, self.Scat_a_max   = Scat_a_min, Scat_a_max
        self.Scat_c_min, self.Scat_c_max   = Scat_c_min, Scat_c_max
        self.L_a_min, self.L_a_max         = L_a_min, L_a_max
        self.L_c_min, self.L_c_max         = L_c_min, L_c_max
        self.SA_a_min = SA_a_min
        self.SA_c_min = SA_c_min
        self.j_min, self.j_max = j_min, j_max

    def _evaluate(self, x, out, *args, **kwargs):
        # x= [delta_a, eps_a, Scat_a, delta_c, eps_c, Scat_c]
        delta_a, eps_a, Scat_a, delta_c, eps_c, Scat_c = x

        # 1) cost: sum anode + cathode
        # cost_function(rho_cat, delta, eps, A_cell, c_cat)
        cost_a = cost_function(self.rho_cat_a, delta_a, eps_a, self.A_cell, self.c_cat_a)
        cost_c = cost_function(self.rho_cat_c, delta_c, eps_c, self.A_cell, self.c_cat_c)
        cost_total = cost_a + cost_c

        # 2) Overpotential sum
        # anode
        eta_a = eta_total(
            j=self.j, j0=self.j0_a, S_cat=Scat_a, epsilon=eps_a, delta=delta_a,
            a=self.a_a, b=self.b_a, R=self.R, T=self.T,
            n=self.n, F=self.F, C_bulk=self.C_bulk_a, D=self.D_a, tau=self.tau_a,rho_cat=self.rho_cat_a
        )
        # cathode
        eta_c = eta_total(
            j=self.j, j0=self.j0_c, S_cat=Scat_c, epsilon=eps_c, delta=delta_c,
            a=self.a_c, b=self.b_c, R=self.R, T=self.T,
            n=self.n, F=self.F, C_bulk=self.C_bulk_c, D=self.D_c, tau=self.tau_c ,rho_cat=self.rho_cat_c
        )
        eta_sum = eta_a + eta_c
        
        #troubleshoting and fixing infeasible solutions
        
        

        # 2 objectives
        out["F"] = [cost_total, eta_sum]

        # Now build 21 constraints => G <= 0 means feasible
        G = []

        # Anode (9 constraints):
        # 1) 0.001 ≤ eps_a ≤ 0.999 => 2
        g_eps_a_min = self.eps_a_min - eps_a      # eps_a >= eps_a_min => eps_a_min - eps_a <=0
        g_eps_a_max = eps_a - self.eps_a_max      # eps_a <= eps_a_max => eps_a - eps_a_max <=0

        # 2) delta_a_min ≤ delta_a ≤ delta_a_max => 2
        g_da_min = self.delta_a_min - delta_a
        g_da_max = delta_a - self.delta_a_max

        # 3) Scat_a_min ≤ S_cat_a ≤ Scat_a_max => 2
        g_scat_a_min = self.Scat_a_min - Scat_a
        g_scat_a_max = Scat_a - self.Scat_a_max

        # 4) Effective Surface area => S_cat_a*(1-eps_a)*delta_a >= SA_a_min => SA_a_min - ...
        eff_a = Scat_a*(1-eps_a)*delta_a
        g_eff_a = self.SA_a_min - eff_a

        # 5) Catalyst Loading => L_a_min ≤ rho_cat_a*delta_a*(1-eps_a) ≤ L_a_max => 2
        L_a = self.rho_cat_a*delta_a*(1-eps_a)
        g_La_min = self.L_a_min - L_a
        g_La_max = L_a - self.L_a_max

        # total => 2+2+2+1+2 = 9 (anode)

        # Cathode (9 constraints, same pattern)
        g_eps_c_min = self.eps_c_min - eps_c
        g_eps_c_max = eps_c - self.eps_c_max

        g_dc_min = self.delta_c_min - delta_c
        g_dc_max = delta_c - self.delta_c_max

        g_scat_c_min = self.Scat_c_min - Scat_c
        g_scat_c_max = Scat_c - self.Scat_c_max

        eff_c = Scat_c*(1-eps_c)*delta_c
        g_eff_c = self.SA_c_min - eff_c

        L_c = self.rho_cat_c*delta_c*(1-eps_c)
        g_Lc_min = self.L_c_min - L_c
        g_Lc_max = L_c - self.L_c_max

        # total => 9 for cathode

        # Global (3 constraints):
        # 1) j_min ≤ j ≤ j_max => 2 => j_min-j <=0, j-j_max<=0
        g_j_min = self.j_min - self.j
        g_j_max = self.j - self.j_max

        # 2) eta_total <= eta_max => 1
        g_eta = eta_sum - self.eta_max

        # Add them all in correct order => total 21
        # Anode(9):
        G += [g_eps_a_min, g_eps_a_max,
              g_da_min, g_da_max,
              g_scat_a_min, g_scat_a_max,
              g_eff_a,
              g_La_min, g_La_max]
        # Cathode(9):
        G += [g_eps_c_min, g_eps_c_max,
              g_dc_min, g_dc_max,
              g_scat_c_min, g_scat_c_max,
              g_eff_c,
              g_Lc_min, g_Lc_max]
        # Global(3):
        G += [g_j_min, g_j_max, g_eta]
        
         # 8) Hard constraint j <= j_lim
    #    j_lim for anode => j_lim_a = (nF * (eps_a/tau_a)*D_a*C_bulk_a)/delta_a
    #    j_lim for cathode => j_lim_c = ...
        j_lim_a = (self.n*self.F*(eps_a/self.tau_a)*self.D_a*self.C_bulk_a)/(delta_a+1e-15)
        j_lim_c = (self.n*self.F*(eps_c/self.tau_c)*self.D_c*self.C_bulk_c)/(delta_c+1e-15)
        j_lim_global = min(j_lim_a, j_lim_c)

        # => j <= j_lim_global => j - j_lim_global <= 0
        g_jlim = self.j - j_lim_global

    # Add it to G
        G.append(g_jlim)

        out["G"] = G


###############################################################################
# Scalarization: WeightedSum, GoalSeeking
###############################################################################

def weighted_sum_optimization(base_problem, w1=0.5, w2=0.5):
    """
    Weighted Sum approach => single-objective
    Minimizes f = w1*cost + w2*overpotential
    """
    class WeightedSumProblem(ElementwiseProblem):
        def __init__(self, problem, w1, w2):
            super().__init__(
                n_var=problem.n_var,
                n_obj=1,
                n_constr=problem.n_constr,  # same 21 constraints
                xl=problem.xl,
                xu=problem.xu
            )
            self.base = problem
            self.w1 = w1
            self.w2 = w2

        def _evaluate(self, x, out, *args, **kwargs):
            out_mo = {}
            self.base._evaluate(x, out_mo, *args, **kwargs)
            cost = out_mo["F"][0]
            eta  = out_mo["F"][1]
            f = self.w1 * cost + self.w2 * eta
            out["F"] = [f]
            out["G"] = out_mo["G"]

    single_obj_problem = WeightedSumProblem(base_problem, w1, w2)
    algo = GA(pop_size=30)
    term = get_termination("n_gen", 30)
    return minimize(single_obj_problem, algo, term, seed=1, verbose=False)


def goal_seeking_optimization(base_problem, goals=(10.0, 0.5)):
    """
    Minimizes f = (cost - goals[0])^2 + (eta - goals[1])^2
    """
    class GoalProblem(ElementwiseProblem):
        def __init__(self, problem, goals):
            super().__init__(
                n_var=problem.n_var,
                n_obj=1,
                n_constr=problem.n_constr,
                xl=problem.xl,
                xu=problem.xu
            )
            self.base = problem
            self.c_goal, self.eta_goal = goals

        def _evaluate(self, x, out, *args, **kwargs):
            out_mo = {}
            self.base._evaluate(x, out_mo, *args, **kwargs)
            cost = out_mo["F"][0]
            eta  = out_mo["F"][1]
            f = (cost - self.c_goal)**2 + (eta - self.eta_goal)**2
            out["F"] = [f]
            out["G"] = out_mo["G"]

    single_obj_problem = GoalProblem(base_problem, goals)
    algo = GA(pop_size=30)
    term = get_termination("n_gen", 30)
    return minimize(single_obj_problem, algo, term, seed=1, verbose=False)


###############################################################################
# Pareto-based: NSGA2, MOEA/D, SPEA2
###############################################################################

def multiobjective_optimization(base_problem, method, pop_size=40, n_gen=30):
    if method == "NSGA2":
        alg = NSGA2(pop_size=pop_size)
    elif method == "MOEA/D":
        alg = MOEAD(pop_size=pop_size, n_neighbors=15, decomposition="pbi")
    elif method == "SPEA2":
        alg = SPEA2(pop_size=pop_size)
    else:
        # fallback
        alg = NSGA2(pop_size=pop_size)

    term = get_termination("n_gen", n_gen)
    return minimize(base_problem, alg, term, seed=1, verbose=False)


###############################################################################
# Master run_optimization
###############################################################################

def run_optimization(category, method, **kwargs):
    """
    Creates a fresh PEMProblem (21 constraints) each run,
    then calls either scalarization or multiobjective approach.

    We exclude e-Constraint method here (as requested).

    scalar_params => Weighted Sum, Goal Seeking
    """
    scalar_params = kwargs.pop("scalar_params", {})

    if category == "Pareto-based":
        pop_size = kwargs.pop("pop_size", 40)
        n_gen    = kwargs.pop("n_gen", 30)
    else:
        pop_size = None
        n_gen    = None

    # Build a new problem => 21 constraints
    problem = PEMProblem(**kwargs)

    if category == "Scalarization":
        if method == "Weighted Sum":
            w1 = scalar_params.get("w1", 0.5)
            w2 = scalar_params.get("w2", 0.5)
            return weighted_sum_optimization(problem, w1, w2)
        elif method == "Goal Seeking":
            goals = scalar_params.get("goals", (10.0, 0.5))
            return goal_seeking_optimization(problem, goals)
        else:
            raise ValueError(f"Unrecognized scalarization method: {method}")
    else:
        # Pareto-based
        return multiobjective_optimization(problem, method, pop_size, n_gen)
