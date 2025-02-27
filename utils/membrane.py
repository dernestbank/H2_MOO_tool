# membrane.py
import numpy as np

class MembraneModel:
    """
    Mathematical model for PEM electrolyzer membrane design.
    
    Decision variables:
      x[0] = t: membrane thickness (m)
      x[1] = j: operating current density (A/cm²)
      
    Objectives (per unit area):
      f1: negative energy efficiency (-η_energy) to maximize efficiency.
      f2: negative lifetime (-L) to maximize durability.
      f3: capital cost = cost of membrane material + manufacturing cost.
      f4: environmental impact = material impact per unit area.
      
    Constraint:
      Mechanical durability: t must be at least t_mech_min.
    """
    def __init__(self,
                 HHV_H2=285000.0,    # Higher Heating Value of H2 (J/mol)
                 alpha=1e-6,         # scaling for hydrogen production rate (mol/(s·(A/cm²)))
                 beta=100.0,         # scaling factor for thickness effect on production rate
                 V_base=1.3,         # Base cell voltage (V)
                 k1=0.005,           # Coefficient for current density contribution (V per (A/cm²))
                 k2=0.1,             # Coefficient for inverse thickness term (V·m)
                 L_base=10000.0,     # Baseline lifetime (hours)
                 k3=10.0,            # Lifetime gain per micron thickness (hours/µm)
                 c_ionomer=300.0,     # Cost of ionomer ($/kg)
                 rho=2000.0,         # Density of membrane (kg/m³)
                 c_manuf=20.0,       # Manufacturing cost ($/m²)
                 c_E=10.0,           # Environmental impact factor (kg CO₂-eq per kg)
                 t_mech_min=158e-6   # Minimum thickness from mechanical constraint (m)
                 ):
        self.HHV_H2 = HHV_H2
        self.alpha = alpha
        self.beta = beta
        self.V_base = V_base
        self.k1 = k1
        self.k2 = k2
        self.L_base = L_base
        self.k3 = k3
        self.c_ionomer = c_ionomer
        self.rho = rho
        self.c_manuf = c_manuf
        self.c_E = c_E
        self.t_mech_min = t_mech_min

    def evaluate_objectives(self, x):
        """
        Evaluate the four objective functions at decision vector x.
        
        x[0] = t : membrane thickness (m)
        x[1] = j : current density (A/cm²)
        
        Returns:
          numpy array [f1, f2, f3, f4] where:
            f1 = -η_energy  (to maximize efficiency)
            f2 = -L         (to maximize lifetime)
            f3 = Capital cost per m²
            f4 = Environmental impact per m²
        """
        t = x[0]
        j = x[1]
        
        # Compute cell voltage (V) using a simplified model.
        V_cell = self.V_base + self.k1 * j + self.k2 / t
        
        # Hydrogen production rate (mol/s) modeled as:
        # r_H2 = alpha * j / (1 + beta * t)
        r_H2 = self.alpha * j / (1.0 + self.beta * t)
        
        # Energy efficiency: η = (HHV_H2 * r_H2) / (V_cell * j)
        # (Assuming I_cell = j for unit area, so j cancels out partially)
        eta_energy = (self.HHV_H2 * r_H2) / (V_cell * j)
        
        # Lifetime (hours): assume it increases linearly with thickness (converted to microns)
        L = self.L_base + self.k3 * (t * 1e6)
        
        # Capital cost per m²: material cost + manufacturing cost.
        # Material cost = c_ionomer * density * thickness.
        C_capital = self.c_ionomer * self.rho * t + self.c_manuf
        
        # Environmental impact per m² (kg CO₂-eq): impact factor * (density * thickness)
        E_material = self.c_E * self.rho * t
        
        # For maximization objectives (efficiency, lifetime) we use negatives:
        f1 = -eta_energy   # maximize efficiency => minimize -η
        f2 = -L            # maximize lifetime => minimize -L
        f3 = C_capital
        f4 = E_material
        
        return np.array([f1, f2, f3, f4])
    
    def evaluate_constraints(self, x):
        """
        Evaluate constraint functions.
        
        Mechanical durability constraint:
          t >= t_mech_min.
        For pymoo, constraints are formulated as g(x) <= 0.
        We define:
          g(x) = t_mech_min - t <= 0.
        """
        t = x[0]
        g1 = self.t_mech_min - t
        return np.array([g1])
