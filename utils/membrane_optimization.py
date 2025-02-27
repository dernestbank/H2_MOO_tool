# membrane_optimization.py
import numpy as np
from pymoo.core.problem import Problem
from utils.membrane import MembraneModel

# Base multiobjective problem for PEM membrane design.
class MembraneOptimizationProblem(Problem):
    def __init__(self, model: MembraneModel, xl=None, xu=None):
        # Decision variables: x[0] = t (thickness in m), x[1] = j (current density in A/cm²)
        if xl is None:
            xl = np.array([50e-6, 0.5])
        if xu is None:
            xu = np.array([300e-6, 3.0])
        super().__init__(n_var=2, n_obj=4, n_constr=1, xl=xl, xu=xu)
        self.model = model

    def _evaluate(self, X, out, *args, **kwargs):
        F = np.zeros((X.shape[0], 4))
        G = np.zeros((X.shape[0], 1))
        for i in range(X.shape[0]):
            x = X[i, :]
            F[i, :] = self.model.evaluate_objectives(x)
            # Constraint: t >= t_mech_min  ->  t_mech_min - t <= 0.
            G[i, 0] = self.model.t_mech_min - x[0]
        out["F"] = F
        out["G"] = G

# Scalarization: Weighted Sum transformation.
class WeightedSumProblem(MembraneOptimizationProblem):
    def __init__(self, model: MembraneModel, weights, **kwargs):
        super().__init__(model, **kwargs)
        self.weights = np.array(weights)  # weights should be of length 4
    
    def _evaluate(self, X, out, *args, **kwargs):
        F_multi = np.zeros((X.shape[0], 4))
        for i in range(X.shape[0]):
            F_multi[i, :] = self.model.evaluate_objectives(X[i, :])
        # Weighted sum: scalar objective = sum(w_i * f_i)
        F_scalar = np.sum(self.weights * F_multi, axis=1).reshape(-1, 1)
        # No multiobjective now, but we preserve constraints
        G = np.zeros((X.shape[0], 1))
        for i in range(X.shape[0]):
            G[i, 0] = self.model.t_mech_min - X[i, 0]
        out["F"] = F_scalar
        out["G"] = G

# Scalarization: Goal Seeking transformation.
class GoalSeekingProblem(MembraneOptimizationProblem):
    def __init__(self, model: MembraneModel, goals, **kwargs):
        super().__init__(model, **kwargs)
        self.goals = np.array(goals)  # goals should be of length 4
    
    def _evaluate(self, X, out, *args, **kwargs):
        F_multi = np.zeros((X.shape[0], 4))
        for i in range(X.shape[0]):
            F_multi[i, :] = self.model.evaluate_objectives(X[i, :])
        # Goal seeking: scalar objective = sum((f_i - goal_i)^2)
        F_scalar = np.sum((F_multi - self.goals) ** 2, axis=1).reshape(-1, 1)
        G = np.zeros((X.shape[0], 1))
        for i in range(X.shape[0]):
            G[i, 0] = self.model.t_mech_min - X[i, 0]
        out["F"] = F_scalar
        out["G"] = G

def run_optimization(method="NSGA2", model_params=None, bounds=None,
                     scalar_params=None, pop_size=100, n_gen=100, seed=1):
    """
    Run the optimization using pymoo.
    
    Parameters:
      method: one of ["NSGA2", "MOEAD", "SPEA2", "WeightedSum", "GoalSeeking"]
      model_params: dictionary of parameters for MembraneModel (if None, use defaults)
      bounds: dictionary with keys 't_lb', 't_ub', 'j_lb', 'j_ub' (if None, use defaults)
      scalar_params: dictionary for scalarization methods:
           for WeightedSum, provide 'weights': list of 4 numbers,
           for GoalSeeking, provide 'goals': list of 4 numbers.
      pop_size: population size
      n_gen: number of generations
      seed: random seed
      
    Returns:
      Optimization result from pymoo.optimize.minimize.
    """
    from pymoo.optimize import minimize
    from pymoo.termination import get_termination
    # Import algorithms from pymoo (latest versions)
    from pymoo.algorithms.moo.nsga2 import NSGA2
    from pymoo.algorithms.moo.moead import MOEAD
    from pymoo.algorithms.moo.spea2 import SPEA2
    
    # Create MembraneModel instance
    if model_params is None:
        model = MembraneModel()
    else:
        model = MembraneModel(**model_params)
    
    # Define bounds for decision variables
    if bounds is None:
        xl = np.array([50e-6, 0.5])
        xu = np.array([300e-6, 3.0])
    else:
        xl = np.array([bounds.get('t_lb', 50e-6), bounds.get('j_lb', 0.5)])
        xu = np.array([bounds.get('t_ub', 300e-6), bounds.get('j_ub', 3.0)])
    
    # Choose problem type
    if method in ["WeightedSum", "GoalSeeking"]:
        # Scalarization transformation; use WeightedSumProblem or GoalSeekingProblem.
        if method == "WeightedSum":
            if scalar_params is None or "weights" not in scalar_params:
                weights = [0.25, 0.25, 0.25, 0.25]
            else:
                weights = scalar_params["weights"]
            problem = WeightedSumProblem(model=model, weights=weights, xl=xl, xu=xu)
        elif method == "GoalSeeking":
            if scalar_params is None or "goals" not in scalar_params:
                # Default goal values (these can be adjusted):
                goals = [ -0.1, -15000, 15, 3 ]  
                # Note: f1 and f2 are negative of efficiency and lifetime.
            else:
                goals = scalar_params["goals"]
            problem = GoalSeekingProblem(model=model, goals=goals, xl=xl, xu=xu)
    else:
        # Multiobjective problem
        problem = MembraneOptimizationProblem(model=model, xl=xl, xu=xu)
    
    # Select algorithm
    if method.upper() == "NSGA2":
        algorithm = NSGA2(pop_size=pop_size, seed=seed)
    elif method.upper() == "MOEAD":
        algorithm = MOEAD(pop_size=pop_size, seed=seed)
    elif method.upper() == "SPEA2":
        algorithm = SPEA2(pop_size=pop_size, seed=seed)
    else:
        # For scalarization methods, we use NSGA2 on a single objective.
        algorithm = NSGA2(pop_size=pop_size, seed=seed)
    
    termination = get_termination("n_gen", n_gen)
    
    res = minimize(problem,
                   algorithm,
                   termination,
                   seed=seed,
                   verbose=True)
    return res
