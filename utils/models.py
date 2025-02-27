# models.py

import numpy as np
import math

def cost_function(rho_cat, delta, eps, A_cell, c_cat):
    """
    Catalyst Cost Function
    ----------------------
    Parameters:
      - rho_cat (g/cm³): Catalyst density
      - delta   (cm)   : Layer thickness
      - eps     (dimensionless): Porosity
      - A_cell  (cm²)  : Cell active area
      - c_cat   ($/g)  : Catalyst cost per gram
      - L        (g/cm^2)    : Catalyst loading [not always used explicitly if derived from δ, (1-ε), etc.]

    Returns:
      cost ($): The cost contribution for that catalyst layer
    """
    # mass per area = rho_cat * delta * (1 - eps)
    # cost = mass/area * area * c_cat
    # => cost_layer = [rho_cat*delta*(1-eps) * A_cell * c_cat]
    mass_per_area = rho_cat * delta * (1.0 - eps) 
    return mass_per_area * A_cell * c_cat


def eta_total(
    j,         # (A/cm²) operating current density
    j0,        # (A/cm²_active) exchange current density (active area basis)
    S_cat,     # (cm²_active/g or cm²_active/cm³) specific surface area
    epsilon,   # (dimensionless) porosity
    delta,     # (cm) thickness
    a, b,      # (V) Tafel constants
     T,      # R (J/(mol*K)), T (K)
     rho_cat,    # (g/cm³) catalyst density
  
    C_bulk,    # (mol/cm³) bulk concentration
    D,         # (cm²/s) diffusivity
    tau,        # (dimensionless) tortuosity
    alpha=0.5,  # (dimensionless) activation coefficient
    R = 8.314,  # (J/(mol*K)) gas constant  [J/(mol*K)]
      n=2, F=96500,      # n (dimensionless), F (C/mol)
    
):
    """
    Total Overpotential Model (Simple Tafel + Simple Concentration)
    ----------------------------------------------------------------
    Activation Overpotential (Tafel form): η_act = a + b * ln(j / j0_geo)
        a= RT/BnF
        b= RT/(nF)
      j0_geo = j0 * S_cat * (1-epsilon)*delta ----------check unit here
      eta_act = (R*T/(alpha*n*F)) * ln(J/(j0_geo))
      
     Parameters:
    - j       (A/cm^2)    : Operating current density per geometric area
    - j0      (A/cm^2_active) : Exchange current density per active surface area
    - S_cat   (cm^2_active/cm^3 or cm^2_active/g, etc.): Specific surface area
    - epsilon (dimensionless) : Porosity
    - delta   (cm)        : Layer thickness
    - a       (V)         : Tafel coefficient (constant term)
    - b       (V)         : Tafel slope (associated with log term)


    Concentration Overpotential
    ---------------------------
    η_conc = (R*T/(n*F)) * ln(1 - j/j_lim)
    where j_lim = (n*F*D_eff*C_bulk)/delta
          D_eff = (epsilon/tau) * D
      
    Parameters:
    - j       (A/cm^2)    : Operating current density (geometric)
    - R       (J/(mol*K)) : Gas constant
    - T       (K)         : Temperature
    - n       (dimensionless) : Number of electrons per reaction
    - F       (C/mol)     : Faraday constant
    - C_bulk  (mol/cm^3)  : Bulk concentration of reactant
    - D       (cm^2/s)    : Diffusivity in free medium
    - epsilon (dimensionless) : Porosity
    - tau     (dimensionless) : Tortuosity
    - delta   (cm)        : Layer thickness

    Summation: η_total = η_act + η_conc

    Returns:
      eta (V) total
    """
    # 1) Tafel Activation
    Eact= 76000 # activation energy (J/mol) (Crespi et al., 2023)
    K_io = 2160000 # pre-exponential factor (A/cm2)
    
    jo= K_io*math.exp(Eact/(R*T))
    #Pressure and Temperature dependence
    #add eqns from notes
    
    
    # j0_geo = j0 * S_cat * (1 - epsilon) * delta  # Exchange current density per geometric area
    L= rho_cat * delta * (1 - epsilon)
    j0_geo = j0 * S_cat * L * (1 - epsilon)
    if j0_geo <= 1e-15:  # avoid log(0)
        print(' -----j0_geo <= 0, j_geo:{j0_geo} ')
        return 1e6  # large penalty
    

    # a + b ln( j / j0_geo )
    # eta_act = a + b * np.log(j / j0_geo) if (j>0 and j0_geo>0) else 1e6
    
    val = j/(j0_geo)
    if val <= 0:
        print(' -----val <= 0, val:{val} ')
        return 1e6  # Large penalty if infeasible
    else:
        eta_act = (R * T / (alpha * n * F)) * np.log(val)





    # 2) Concentration Overpotential
    eta_conc = 1e6  # default penalty
    # j_lim = nF * (epsilon/tau*D) * C_bulk / delta
    D_eff = (epsilon/tau)*D # effective diffusivity (cm^2/s)
    # limiting current density (A/cm^2)
    j_lim = (n*F*D_eff*C_bulk)/delta
    # j_lim = 6 #A/cm2

     # check validity to avoid log(0)
    if j_lim <= j or j_lim<=0:
        pass
        # eta_conc = 1e6 # large penalty or infeasible
        # print(f'infeasible solution, j_lim <= j or j_lim <= 0 @ j_lim:{j_lim}, j:{j} ')
        #print all parameters in terminal
        # print(f'epsilon:{epsilon}, tau:{tau}, delta:{delta}, D_eff:{D_eff}, C_bulk:{C_bulk}')
    else:
        fac = (R*T)/(n*F)
        # (R*T/(nF)) ln(1 - j / j_lim)
        part = 1 - (j/j_lim)
        if part <= 1e-15:
            eta_conc = 1e6
            print(f'infeasible solution, part <= 1e-15 part:{part}, j:{j}, j_lim:{j_lim}')
          
            
        else:
            eta_conc = fac * np.log(part)

    return eta_act + eta_conc


#notes:
# 1) Tafel Activation
# 2) Concentration Overpotential
# limiting current density (A/cm^2)
# must be greater than j

def eta_activation(J, j0, L, S_cat, R, T, alpha=0.5, n=2, F=96500):
    """
    Activation overpotential:
    eta_act = (R*T/(alpha*n*F)) * ln(J/(j0*L*S_cat))
    
    Activation Overpotential (Tafel form)
    -------------------------------------
    η_act = a + b * log( j / j0_geo )
    where j0_geo = j0 * S_cat * (1 - epsilon) * delta

    Parameters:
    - j       (A/cm^2)    : Operating current density per geometric area
    - j0      (A/cm^2_active) : Exchange current density per active surface area
    - S_cat   (cm^2_active/cm^3 or cm^2_active/g, etc.): Specific surface area
    - epsilon (dimensionless) : Porosity
    - delta   (cm)        : Layer thickness
    - a       (V)         : Tafel coefficient (constant term)
    - b       (V)         : Tafel slope (associated with log term)

    Returns:
    - η_act (V)
    
    """
    val = J/(j0 * L * S_cat)
    
    if val <= 0:
        return 1e6  # Large penalty if infeasible
    return (R * T / (alpha * n * F)) * np.log(val)


def eta_concentration(J, delta, epsilon, tau, C_bulk, D, R=8.314, T=315, n=2, F=96500):
    """
    Concentration overpotential:
    eta_conc = (R*T/(n*F))*ln( C_bulk / (C_bulk - (J*delta*n*F / D_eff)) )
    where D_eff = D * (epsilon/tau)
    
    Concentration Overpotential
    ---------------------------
    η_conc = (R*T/(n*F)) * ln(1 - j/j_lim)
    where j_lim = (n*F*D_eff*C_bulk)/delta
          D_eff = (epsilon/tau) * D

    Parameters:
    - j       (A/cm^2)    : Operating current density (geometric)
    - R       (J/(mol*K)) : Gas constant
    - T       (K)         : Temperature
    - n       (dimensionless) : Number of electrons per reaction
    - F       (C/mol)     : Faraday constant
    - C_bulk  (mol/cm^3)  : Bulk concentration of reactant
    - D       (cm^2/s)    : Diffusivity in free medium
    - epsilon (dimensionless) : Porosity
    - tau     (dimensionless) : Tortuosity
    - delta   (cm)        : Layer thickness

    Returns:
    - η_conc (V)
    """
    
    
    D_eff = D * (epsilon / tau)
    denom = C_bulk - (J * delta * n * F / D_eff)
    if denom <= 0 or denom >= C_bulk:
        return 1e6
    return (R*T/(n*F))*np.log(C_bulk/denom)
