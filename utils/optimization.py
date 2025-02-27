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
# PEMProblem with 21 + 1 (hard j_lim) constraints = 22 total
###############################################################################
class PEMProblem(ElementwiseProblem):
    """
    PEM Problem for Catalyst Layer Optimization.
    
    Decision Variables (6):
      x = [delta_a, eps_a, S_cat_a, delta_c, eps_c, S_cat_c]

    Objectives:
      F0: Total Cost (Anode + Cathode)
      F1: Total Overpotential (Anode + Cathode)

    Constraints (22 total):
      - Anode (9 constraints)
      - Cathode (9 constraints)
      - Global (3 constraints)
      - Hard mass transport constraint: j <= j_lim_global (1 constraint)
    """
    def __init__(self,
                 A_cell, j, R, T, alpha, n, F,
                 # Anode parameters
                 C_bulk_a, D_a, tau_a,
                 # Cathode parameters
                 C_bulk_c, D_c, tau_c,
                 eta_max,
                 # Catalyst properties anode
                 rho_cat_a, c_cat_a, j0_a, a_a, b_a,
                 # Catalyst properties cathode
                 rho_cat_c, c_cat_c, j0_c, a_c, b_c,
                 # Anode constraints
                 eps_a_min, eps_a_max,
                 delta_a_min, delta_a_max,
                 Scat_a_min, Scat_a_max,
                 L_a_min, L_a_max,
                 SA_a_min,
                 # Cathode constraints
                 eps_c_min, eps_c_max,
                 delta_c_min, delta_c_max,
                 Scat_c_min, Scat_c_max,
                 L_c_min, L_c_max,
                 SA_c_min,
                 # Global constraints
                 j_min, j_max,
                 # Total number of constraints: 9+9+3+1 = 22
                 n_var=6, n_obj=2, n_constr=22):
        super().__init__(
            n_var=n_var,
            n_obj=n_obj,
            n_constr=n_constr,
            xl=[delta_a_min, eps_a_min, Scat_a_min, delta_c_min, eps_c_min, Scat_c_min],
            xu=[delta_a_max, eps_a_max, Scat_a_max, delta_c_max, eps_c_max, Scat_c_max]
        )
        self.A_cell = A_cell
        self.j = j
        self.R = R
        self.T = T
        self.alpha = alpha
        self.n = n
        self.F = F

        self.C_bulk_a = C_bulk_a
        self.D_a = D_a
        self.tau_a = tau_a

        self.C_bulk_c = C_bulk_c
        self.D_c = D_c
        self.tau_c = tau_c

        self.eta_max = eta_max

        self.rho_cat_a = rho_cat_a
        self.c_cat_a = c_cat_a
        self.j0_a = j0_a
        self.a_a = a_a
        self.b_a = b_a

        self.rho_cat_c = rho_cat_c
        self.c_cat_c = c_cat_c
        self.j0_c = j0_c
        self.a_c = a_c
        self.b_c = b_c

        self.eps_a_min, self.eps_a_max = eps_a_min, eps_a_max
        self.delta_a_min, self.delta_a_max = delta_a_min, delta_a_max
        self.Scat_a_min, self.Scat_a_max = Scat_a_min, Scat_a_max
        self.L_a_min, self.L_a_max = L_a_min, L_a_max
        self.SA_a_min = SA_a_min

        self.eps_c_min, self.eps_c_max = eps_c_min, eps_c_max
        self.delta_c_min, self.delta_c_max = delta_c_min, delta_c_max
        self.Scat_c_min, self.Scat_c_max = Scat_c_min, Scat_c_max
        self.L_c_min, self.L_c_max = L_c_min, L_c_max
        self.SA_c_min = SA_c_min

        self.j_min, self.j_max = j_min, j_max

    def _evaluate(self, x, out, *args, **kwargs):
        delta_a, eps_a, Scat_a, delta_c, eps_c, Scat_c = x

        # Calculate cost
        cost_a = cost_function(self.rho_cat_a, delta_a, eps_a, self.A_cell, self.c_cat_a)
        cost_c = cost_function(self.rho_cat_c, delta_c, eps_c, self.A_cell, self.c_cat_c)
        cost_total = cost_a + cost_c

        # Calculate overpotential
        eta_a = eta_total(
            j=self.j, j0=self.j0_a, S_cat=Scat_a, epsilon=eps_a, delta=delta_a,
            a=self.a_a, b=self.b_a, T=self.T, rho_cat=self.rho_cat_a,
            C_bulk=self.C_bulk_a, D=self.D_a, tau=self.tau_a,
            alpha=self.alpha, R=self.R, n=self.n, F=self.F
        )
        eta_c = eta_total(
            j=self.j, j0=self.j0_c, S_cat=Scat_c, epsilon=eps_c, delta=delta_c,
            a=self.a_c, b=self.b_c, T=self.T, rho_cat=self.rho_cat_c,
            C_bulk=self.C_bulk_c, D=self.D_c, tau=self.tau_c,
            alpha=self.alpha, R=self.R, n=self.n, F=self.F
        )
        eta_sum = eta_a + eta_c

        out["F"] = [cost_total, eta_sum]

        # Build constraints
        G = []
        # --- Anode (9 constraints)
        g_eps_a_min = self.eps_a_min - eps_a
        g_eps_a_max = eps_a - self.eps_a_max
        g_da_min = self.delta_a_min - delta_a
        g_da_max = delta_a - self.delta_a_max
        g_scat_a_min = self.Scat_a_min - Scat_a
        g_scat_a_max = Scat_a - self.Scat_a_max
        eff_a = Scat_a * (1.0 - eps_a) * delta_a
        g_eff_a = self.SA_a_min - eff_a
        L_a = self.rho_cat_a * delta_a * (1.0 - eps_a)
        g_La_min = self.L_a_min - L_a
        g_La_max = L_a - self.L_a_max
        G += [g_eps_a_min, g_eps_a_max,
              g_da_min, g_da_max,
              g_scat_a_min, g_scat_a_max,
              g_eff_a,
              g_La_min, g_La_max]

        # --- Cathode (9 constraints)
        g_eps_c_min = self.eps_c_min - eps_c
        g_eps_c_max = eps_c - self.eps_c_max
        g_dc_min = self.delta_c_min - delta_c
        g_dc_max = delta_c - self.delta_c_max
        g_scat_c_min = self.Scat_c_min - Scat_c
        g_scat_c_max = Scat_c - self.Scat_c_max
        eff_c = Scat_c * (1.0 - eps_c) * delta_c
        g_eff_c = self.SA_c_min - eff_c
        L_c = self.rho_cat_c * delta_c * (1.0 - eps_c)
        g_Lc_min = self.L_c_min - L_c
        g_Lc_max = L_c - self.L_c_max
        G += [g_eps_c_min, g_eps_c_max,
              g_dc_min, g_dc_max,
              g_scat_c_min, g_scat_c_max,
              g_eff_c,
              g_Lc_min, g_Lc_max]

        # --- Global constraints (3 constraints)
        g_j_min = self.j_min - self.j
        g_j_max = self.j - self.j_max
        g_eta = eta_sum - self.eta_max
        G += [g_j_min, g_j_max, g_eta]

        # --- Hard current transport constraint:
        # Compute limiting current for anode and cathode:
        j_lim_a = (self.n * self.F * (eps_a / self.tau_a) * self.D_a * self.C_bulk_a) / (delta_a + 1e-15)
        j_lim_c = (self.n * self.F * (eps_c / self.tau_c) * self.D_c * self.C_bulk_c) / (delta_c + 1e-15)
        j_lim_global = min(j_lim_a, j_lim_c)
        g_jlim = self.j - j_lim_global   # require j <= j_lim_global
        G.append(g_jlim)

        out["G"] = G

###############################################################################
# Scalarization: Weighted Sum & Goal Seeking
###############################################################################
def weighted_sum_optimization(base_problem, w1=0.5, w2=0.5):
    class WeightedSumProblem(ElementwiseProblem):
        def __init__(self, p, w1, w2):
            super().__init__(
                n_var=p.n_var,
                n_obj=1,
                n_constr=p.n_constr,
                xl=p.xl,
                xu=p.xu
            )
            self.base = p
            self.w1 = w1
            self.w2 = w2

        def _evaluate(self, x, out, *args, **kwargs):
            out_mo = {}
            self.base._evaluate(x, out_mo, *args, **kwargs)
            cost = out_mo["F"][0]
            eta = out_mo["F"][1]
            f = self.w1 * cost + self.w2 * eta
            out["F"] = [f]
            out["G"] = out_mo["G"]

    prob = WeightedSumProblem(base_problem, w1, w2)
    algo = GA(pop_size=30)
    term = get_termination("n_gen", 30)
    return minimize(prob, algo, term, seed=1, verbose=False)


def goal_seeking_optimization(base_problem, goals=(10.0, 0.5)):
    class GoalProblem(ElementwiseProblem):
        def __init__(self, p, goals):
            super().__init__(
                n_var=p.n_var,
                n_obj=p.n_obj,
                n_constr=p.n_constr,
                xl=p.xl,
                xu=p.xu
            )
            self.base = p
            self.c_goal, self.eta_goal = goals

        def _evaluate(self, x, out, *args, **kwargs):
            out_mo = {}
            self.base._evaluate(x, out_mo, *args, **kwargs)
            cost = out_mo["F"][0]
            eta = out_mo["F"][1]
            f = (cost - self.c_goal)**2 + (eta - self.eta_goal)**2
            out["F"] = [f]
            out["G"] = out_mo["G"]

    prob = GoalProblem(base_problem, goals)
    algo = GA(pop_size=30)
    term = get_termination("n_gen", 30)
    return minimize(prob, algo, term, seed=1, verbose=False)

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
        alg = NSGA2(pop_size=pop_size)
    term = get_termination("n_gen", n_gen)
    return minimize(base_problem, alg, term, seed=1, verbose=False)

###############################################################################
# Master run_optimization
###############################################################################
def run_optimization(category, method, **kwargs):
    """
    Creates a fresh PEMProblem (22 constraints total) and runs the selected optimization.
    For scalarization, only Weighted Sum and Goal Seeking are available.
    For Pareto-based, NSGA2, MOEA/D, and SPEA2 are available.
    """
    scalar_params = kwargs.pop("scalar_params", {})
    if category == "Pareto-based":
        pop_size = kwargs.pop("pop_size", 40)
        n_gen = kwargs.pop("n_gen", 30)
    else:
        pop_size = None
        n_gen = None

    base_problem = PEMProblem(**kwargs)

    if category == "Scalarization":
        if method == "Weighted Sum":
            w1 = scalar_params.get("w1", 0.5)
            w2 = scalar_params.get("w2", 0.5)
            return weighted_sum_optimization(base_problem, w1, w2)
        elif method == "Goal Seeking":
            goals = scalar_params.get("goals", (10.0, 0.5))
            return goal_seeking_optimization(base_problem, goals)
        else:
            raise ValueError(f"Unknown scalarization method: {method}")
    else:
        return multiobjective_optimization(base_problem, method, pop_size, n_gen)
