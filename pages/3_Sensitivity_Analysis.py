# pages/2_Sensitivity_Analysis.py

import streamlit as st
import numpy as np
from utils.optimization import run_optimization
from utils.visualization import create_dataframe, scatter_matrix_plot, parallel_coordinates_plot, heatmap_plot, glyph_plot
import plotly.express as px
st.set_page_config(page_title="Sensitivity Analysis", layout="wide")

st.title("Sensitivity Analysis")

st.write(
    "This page allows you to perform sensitivity analysis by varying one parameter "
    "and observing the impact on the optimization results."
)

# Choose which parameter to vary
parameter_to_vary = st.selectbox(
    "Select parameter to vary",
    ["C_bulk", "D", "tau", "eta_max", "J_min"],
    key="sens_param_select"
)

# Range of values
st.sidebar.header("Sensitivity Analysis Settings")
param_min = st.sidebar.number_input(f"Minimum {parameter_to_vary}", value=0.05, key="sens_min")
param_max = st.sidebar.number_input(f"Maximum {parameter_to_vary}", value=0.15, key="sens_max")
steps = st.sidebar.number_input("Number of Steps", value=5, min_value=2, key="sens_steps")

# Run button
run_sens = st.button("Run Sensitivity Analysis", key="run_sens")

# Fixed default parameters (to keep example simple)
A_cell = 50.0
R = 8.314
T = 353.0
alpha = 0.5
n = 2
F = 96485.0
C_bulk_default = 0.1
D_default = 1e-2
tau_default = 1.2
eta_max_default = 2.0
J_min_default = 0.0001

rho_cat_a = 11.66
c_cat_a = 100.0
j0_a = 1e-2
S_cat_a = 40000.0
L_max_a = 0.01
delta_max_a = 0.001

rho_cat_c = 21.45
c_cat_c = 60.0
j0_c = 1e-2
S_cat_c = 40000.0
L_max_c = 0.01
delta_max_c = 0.001

method = "NSGA2"
pop_size = 20
n_gen = 20

if run_sens:
    st.write(f"Varying **{parameter_to_vary}** from {param_min} to {param_max} in {steps} steps.")
    param_values = np.linspace(param_min, param_max, steps)
    results = []

    for val in param_values:
        # Adjust parameter before each optimization run
        if parameter_to_vary == "C_bulk":
            current_C_bulk = val
            current_D = D_default
            current_tau = tau_default
            current_eta_max = eta_max_default
            current_J_min = J_min_default
        elif parameter_to_vary == "D":
            current_D = val
            current_C_bulk = C_bulk_default
            current_tau = tau_default
            current_eta_max = eta_max_default
            current_J_min = J_min_default
        elif parameter_to_vary == "tau":
            current_tau = val
            current_C_bulk = C_bulk_default
            current_D = D_default
            current_eta_max = eta_max_default
            current_J_min = J_min_default
        elif parameter_to_vary == "eta_max":
            current_eta_max = val
            current_C_bulk = C_bulk_default
            current_D = D_default
            current_tau = tau_default
            current_J_min = J_min_default
        elif parameter_to_vary == "J_min":
            current_J_min = val
            current_C_bulk = C_bulk_default
            current_D = D_default
            current_tau = tau_default
            current_eta_max = eta_max_default

        # Run optimization using Pareto-based method (NSGA2)
        res = run_optimization(
            category="Pareto-based",
            method=method,
            A_cell=A_cell, R=R, T=T, alpha=alpha, n=n, F=F,
            C_bulk=current_C_bulk, D=current_D, tau=current_tau,
            eta_max=current_eta_max, J_min=current_J_min,
            rho_cat_a=rho_cat_a, c_cat_a=c_cat_a, j0_a=j0_a, S_cat_a=S_cat_a,
            L_max_a=L_max_a, delta_max_a=delta_max_a,
            rho_cat_c=rho_cat_c, c_cat_c=c_cat_c, j0_c=j0_c, S_cat_c=S_cat_c,
            L_max_c=L_max_c, delta_max_c=delta_max_c,
            scalar_params=None,
            pop_size=pop_size, n_gen=n_gen
        )

        if res.F is not None and len(res.F) > 0:
            # For simplicity, record the minimal cost and minimal overpotential
            min_cost = np.min(res.F[:, 0])
            min_eta = np.min(res.F[:, 1])
            results.append((val, min_cost, min_eta))
        else:
            # If no solutions found, record None
            results.append((val, None, None))

    # Display results
    st.write("**Sensitivity Analysis Results:**")
    st.write(f"**Parameter:** {parameter_to_vary}")
    st.write("**(Parameter Value, Min Cost, Min Overpotential)**")
    for r in results:
        st.write(r)

    # Prepare lists for plotting
    valid_results = [r for r in results if r[1] is not None]
    if len(valid_results) > 0:
        vals = [r[0] for r in valid_results]
        costs = [r[1] for r in valid_results]
        etas = [r[2] for r in valid_results]

        st.subheader("Sensitivity Plots")
        fig_cost = px.line(
            x=vals, y=costs, 
            labels={'x': parameter_to_vary, 'y': 'Min Cost (C)'},
            title=f"Min Cost vs. {parameter_to_vary}"
        )
        st.plotly_chart(fig_cost, use_container_width=True)

        fig_eta = px.line(
            x=vals, y=etas, 
            labels={'x': parameter_to_vary, 'y': 'Min Overpotential (V)'},
            title=f"Min Overpotential vs. {parameter_to_vary}"
        )
        st.plotly_chart(fig_eta, use_container_width=True)
    else:
        st.warning("No feasible solutions found in the given parameter range.")
