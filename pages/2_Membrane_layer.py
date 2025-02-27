# streamlit_app.py
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from utils.membrane_optimization import run_optimization

st.title("PEM Electrolyzer Membrane Design Optimization")

st.sidebar.header("Optimization Settings")

# Choose optimization method
method_options = ["NSGA2", "MOEAD", "SPEA2", "WeightedSum", "GoalSeeking"]
method_choice = st.sidebar.selectbox("Select Optimization Method", options=method_options)

# Set population size and number of generations
pop_size = st.sidebar.slider("Population Size", min_value=50, max_value=300, value=100, step=10)
n_gen = st.sidebar.slider("Number of Generations", min_value=10, max_value=200, value=100, step=10)
seed = st.sidebar.number_input("Random Seed", value=1, step=1)

st.sidebar.header("Decision Variable Bounds")
t_lb = st.sidebar.number_input("Lower bound for membrane thickness (m)", value=50e-6, format="%.6e")
t_ub = st.sidebar.number_input("Upper bound for membrane thickness (m)", value=300e-6, format="%.6e")
j_lb = st.sidebar.number_input("Lower bound for current density (A/cm²)", value=0.5)
j_ub = st.sidebar.number_input("Upper bound for current density (A/cm²)", value=3.0)

bounds = {
    't_lb': t_lb,
    't_ub': t_ub,
    'j_lb': j_lb,
    'j_ub': j_ub
}

st.sidebar.header("Mechanical Durability Constraint")
# Display (but not change) the default minimum thickness from mechanical considerations.
default_t_mech_min = 158e-6
st.sidebar.write(f"Mechanical durability constraint: t ≥ {default_t_mech_min:.2e} m")

st.sidebar.header("Scalarization Parameters")
scalar_params = {}
if method_choice in ["WeightedSum", "GoalSeeking"]:
    if method_choice == "WeightedSum":
        weights_input = st.sidebar.text_input("Enter weights (comma separated for f1,f2,f3,f4)", "0.25, 0.25, 0.25, 0.25")
        try:
            weights = [float(w.strip()) for w in weights_input.split(",")]
        except:
            weights = [0.25, 0.25, 0.25, 0.25]
        scalar_params["weights"] = weights
    elif method_choice == "GoalSeeking":
        goals_input = st.sidebar.text_input("Enter goals (comma separated for f1,f2,f3,f4)", "-0.1, -15000, 15, 3")
        try:
            goals = [float(g.strip()) for g in goals_input.split(",")]
        except:
            goals = [-0.1, -15000, 15, 3]
        scalar_params["goals"] = goals
###############################################################################
# Place holder for LCA and Environmental Impact Assessment
###############################################################################

# Placeholder for LCA and Environmental Impact Assessment
st.sidebar.header("Environmental Impact Assessment")
st.sidebar.write("Placeholder: This section is under construction. Please check back later.")
# LCA Scope Selection
with st.sidebar.expander("LCA Scope & Boundaries"):
    lca_scope = st.selectbox(
        "Life Cycle Assessment Scope",
        ["Cradle-to-Gate", "Cradle-to-Grave", "Cradle-to-Cradle", "Gate-to-Gate"]
    )
    
    geographical_scope = st.selectbox(
        "Geographical Scope",
        ["Global", "Europe", "North America", "Asia", "Custom Region"]
    )
    
    if geographical_scope == "Custom Region":
        countries = st.multiselect(
            "Select Countries",
            ["USA", "Germany", "China", "Japan", "UK", "France", "South Korea", "Canada"]
        )

# Life Cycle Inventory
with st.sidebar.expander("Life Cycle Inventory"):
    inventory_db = st.selectbox(
        "Inventory Database",
        ["ecoinvent 3.8", "GaBi", "USLCI", "ELCD", "Custom"]
    )
    
    impact_method = st.selectbox(
        "Impact Assessment Method",
        ["ReCiPe Midpoint (E)", "ReCiPe Endpoint (H)", "ILCD 2011", "TRACI 2.1"]
    )

# Impact Categories
with st.sidebar.expander("Impact Categories"):
    st.write("Select Impact Categories to Consider:")
    
    impact_weights = {}
    
    impact_weights['gwp'] = st.slider(
        "Global Warming Potential (CO₂-eq)",
        0.0, 1.0, 0.2, 0.1,
        help="Climate change impact weight"
    )
    
    impact_weights['marine'] = st.slider(
        "Marine Ecotoxicity (1,4-DCB-eq)",
        0.0, 1.0, 0.15, 0.1
    )
    
    impact_weights['human_carc'] = st.slider(
        "Human Carcinogenic (1,4-DCB-eq)",
        0.0, 1.0, 0.15, 0.1
    )
    
    impact_weights['human_noncarc'] = st.slider(
        "Human Non-carcinogenic (1,4-DCB-eq)",
        0.0, 1.0, 0.15, 0.1
    )
    
    impact_weights['land_use'] = st.slider(
        "Land Use (m² × year)",
        0.0, 1.0, 0.15, 0.1
    )
    
    impact_weights['fossil'] = st.slider(
        "Fossil Resource Scarcity (kg oil-eq)",
        0.0, 1.0, 0.2, 0.1
    )

# Environmental Constraints
with st.sidebar.expander("Environmental Constraints"):
    max_gwp = st.number_input(
        "Maximum GWP (kg CO₂-eq/kg H₂)",
        value=10.0,
        help="Maximum allowed Global Warming Potential"
    )
    
    max_energy = st.number_input(
        "Maximum Energy Use (MJ/kg H₂)",
        value=200.0
    )
    
    water_consumption = st.number_input(
        "Maximum Water Consumption (L/kg H₂)",
        value=25.0
    )
model_params = {}
# Add environmental parameters to model_params
model_params.update({
    "lca_scope": lca_scope,
    "geographical_scope": geographical_scope,
    "inventory_db": inventory_db,
    "impact_method": impact_method,
    "impact_weights": impact_weights,
    "environmental_constraints": {
        "max_gwp": max_gwp,
        "max_energy": max_energy,
        "water_consumption": water_consumption
    }
})




###############################################################################
# Membrane Model Parameters
###############################################################################
st.sidebar.header("Membrane Model Parameters")
# Allow user to adjust some key membrane parameters
c_ionomer = st.sidebar.number_input("Cost of ionomer ($/kg)", value=300.0)
rho = st.sidebar.number_input("Density of membrane (kg/m³)", value=2000.0)
c_manuf = st.sidebar.number_input("Manufacturing cost ($/m²)", value=20.0)
c_E = st.sidebar.number_input("Environmental impact factor (kg CO₂-eq/kg)", value=10.0)

model_params = {
    "c_ionomer": c_ionomer,
    "rho": rho,
    "c_manuf": c_manuf,
    "c_E": c_E,
    "t_mech_min": default_t_mech_min
}

if st.button("Run Optimization"):
    st.write("Running optimization, please wait...")
    res = run_optimization(method=method_choice,
                           model_params=model_params,
                           bounds=bounds,
                           scalar_params=scalar_params,
                           pop_size=pop_size,
                           n_gen=n_gen,
                           seed=seed)
    st.write("Optimization Completed!")
    
    # Retrieve objective values from the result
    F = res.F
    X = res.X
    
    st.subheader("Optimization Result (Decision Variables)")
    st.write("Each row corresponds to [membrane thickness (m), current density (A/cm²)]:")
    st.write(X)
    
    if method_choice in ["NSGA2", "MOEAD", "SPEA2"]:
        st.subheader("Pareto Front (Objective Values)")
        st.write("Columns: [-Efficiency, -Lifetime, Capital Cost, Environmental Impact]")
        st.write(F)
        
        # Plot two selected objective pairs. Here we plot Efficiency vs. Cost.
        efficiency = -F[:, 0]  # since we minimized negative efficiency
        cost = F[:, 2]
        
        fig, ax = plt.subplots()
        sc = ax.scatter(cost, efficiency, c=-F[:, 1], cmap="viridis")  # color by lifetime (maximizing lifetime)
        ax.set_xlabel("Capital Cost ($/m²)")
        ax.set_ylabel("Energy Efficiency")
        cbar = plt.colorbar(sc, ax=ax)
        cbar.set_label("Lifetime (hours)")
        st.pyplot(fig)
    else:
        st.subheader("Scalarized Objective Value")
        st.write("The scalar objective (weighted sum or goal-seeking) is shown for each solution:")
        st.write(F)
        
        # For scalar problems, we can show the best solution
        best_idx = np.argmin(F)
        st.write("Best solution:")
        st.write(f"Decision vector: {X[best_idx, :]}")
        st.write(f"Objective value: {F[best_idx, 0]}")

