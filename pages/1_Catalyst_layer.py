# pages/1_Catalyst_layer.py

import os
import json
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime

from utils.optimization import run_optimization

st.set_page_config(page_title="PEM Electrolyzer Optimization", layout="wide")
st.write("powered by S2D2 Lab | Penn State")
st.title("PEM Electrolyzer Design playground: Catalyst layer Design Optimization")
# st.write("Optimization of Electrolyzer Design for PEM Electrolyzer using 21-Constraint Model")
st.write("""
Welcome to the PEM Electrolyzer Design Playground.  
This tool allows you to explore optimization of the catalyst layer design using a 21-constraint (or 22 with j_lim) multiobjective model.  
Select from scalarization methods (Weighted Sum, Goal Seeking) or Pareto-based methods (NSGA2, MOEA/D, SPEA2) in the navigation.
""")
st.write("---")
# Add a button to clear the cache
if st.sidebar.button("Clear Cache"):
    st.cache_data.clear()
    st.success("Cache cleared!")

RESULTS_DIR = "results_logs"
os.makedirs(RESULTS_DIR, exist_ok=True)

###############################################################################
# Visualization & Metrics
###############################################################################

def create_dataframe(X, F, var_names, obj_names):
    df_vars = pd.DataFrame(X, columns=var_names)
    df_objs = pd.DataFrame(F, columns=obj_names)
    return pd.concat([df_vars, df_objs], axis=1)

def compute_hypervolume(F, ref_point=(1e5,1e5)):
    from pymoo.indicators import Hypervolume
    if F is None or len(F)==0:
        return None
    hv = Hypervolume(ref_point=ref_point)
    return hv.do(F)

def compute_c_metric(F, F2=None):
    from pymoo.indicators import CMetric
    if F is None or len(F)==0:
        return None
    if F2 is None:
        F2=F
    c_val = CMetric().do(F, F2)
    return c_val

def compute_euclidean_distance(F, reference=(0,0)):
    if F is None or len(F)==0:
        return None
    dists = np.linalg.norm(F - np.array(reference), axis=1)
    return np.mean(dists)

###############################################################################
# Method Category
###############################################################################
st.sidebar.header("Select Optimization Method ")
method_category = st.sidebar.selectbox("Optimization Category",
                                       ["Scalarization","Pareto-based"])

if method_category=="Scalarization":
    method_name = st.sidebar.selectbox("Scalarization Method",
                                       ["Weighted Sum","Goal Seeking"])
else:
    method_name = st.sidebar.selectbox("Pareto-based Method",
                                       ["NSGA2","MOEA/D","SPEA2"])

###############################################################################
# Scalarization Params
###############################################################################
scalar_params={}
if method_category=="Scalarization":
    if method_name=="Weighted Sum":
        w1 = st.sidebar.slider("Weight for Cost (w1)",0.0,1.0,0.5)
        w2 = 1.0 - w1
        scalar_params["w1"]=w1
        scalar_params["w2"]=w2
    elif method_name=="Goal Seeking":
        c_goal=st.sidebar.number_input("Cost Goal",value=10.0)
        eta_goal=st.sidebar.number_input("Overpotential Goal",value=0.5)
        scalar_params["goals"] = (c_goal, eta_goal)
st.sidebar.write("--- ")
###############################################################################
# Operating & Catalyst parameters
###############################################################################
st.sidebar.header("Design & Operating Parameters ") #& Catalyst & Constraints

A_cell = st.sidebar.number_input("Cell Active Area (cm²)", value=50.0)
j      = st.sidebar.number_input("Current Density j (A/cm²)", value=2.0)
R      = 8.314 # J/(mol*K)
T      = st.sidebar.number_input("Temperature (K) ", value=353.0)
st.sidebar.write(f" {T-273.15:.2f} °C")
# n_e    = st.sidebar.number_input("Number of Electrons (n)", value=2)
n_e=int(2)
F_const= 96485.0 # Faraday Constant


# C_bulk_a=st.sidebar.number_input("Anode Bulk Conc (mol/cm³)",format="%.4f", value=0.056) #Concentration ≈ rho/molar mass = (1 g/cm³) / (18 g/mol) ≈ **0.056 mol/cm³** (or 56 mol/L)
# D_a=     st.sidebar.number_input("Anode Diffusivity (cm²/s)",format="%.4f" ,value=0.26) #Bulk Diffusivity of Water Vapor (D): 0.26 cm²/s at 80°C and 1 atm. ld value 1e-2
# tau_a=   st.sidebar.number_input("Anode Tortuosity",value=1.2) #  1.27 to 2.13

# C_bulk_c=st.sidebar.number_input("Cathode Bulk Conc (mol/cm³)",format="%.4f", value=0.001) #**0.001-0.002 mol/cm³** # formally 0.01
# D_c=     st.sidebar.number_input("Cathode Diffusivity (cm²/s)",format="%.6f", value=2e-5) #For water at room temperature, it's around 2×10−5cm2​/s #old =1e-2

# tau_c=   st.sidebar.number_input("Cathode Tortuosity", value=1.27) #  1.27 to 2.13

# ------make catalyst customizable 
# Catalyst anode
# rho_cat_a= st.sidebar.number_input("Anode Catalyst Density (g/cm³)", value=11.66)
# c_cat_a  = st.sidebar.number_input("Anode Catalyst Cost ($/g)", value=100.0)
# j0_a     = st.sidebar.number_input("Anode j0 (A/cm²_active)",value=1e-3)
# a_a      = st.sidebar.number_input("Anode Tafel a (V)",value=0.1)
# b_a      = st.sidebar.number_input("Anode Tafel b (V)",value=0.05)

# # Catalyst cathode
# rho_cat_c= st.sidebar.number_input("Cathode Catalyst Density (g/cm³)", value=21.45)
# c_cat_c  = st.sidebar.number_input("Cathode Catalyst Cost ($/g)",value=60.0)
# j0_c     = st.sidebar.number_input("Cathode j0 (A/cm²_active)", value=1e-3)
# a_c      = st.sidebar.number_input("Cathode Tafel a (V)",value=0.08)
# b_c      = st.sidebar.number_input("Cathode Tafel b (V)",value=0.04)

st.sidebar.header("Anode Catalyst Selection")
anode_catalyst = st.sidebar.selectbox("Anode Catalyst", ["IrO2", "RuO2", "Custom"])
if anode_catalyst == "IrO2":
    rho_cat_a = 11.66 #Cathode Catalyst Density (g/cm³)"
    c_cat_a = 100.0 #Anode Catalyst Cost ($/g)
    j0_a = 1e-2 #Cathode exchange current densit j0 (A/cm²_active) **0.1 to 10 mA/cm²**
    # S_cat_a = 100000.0
    
    a_a      = 0.1
    b_a      = 0.05
elif anode_catalyst == "RuO2":
    rho_cat_a = 6.97 #Cathode Catalyst Density (g/cm³)" 
    c_cat_a = 80.0 #Anode Catalyst Cost ($/g)
    j0_a = 1e-2 #Cathode j0 (A/cm²_active)
    
    # S_cat_a = 100000.0
    a_a      =0.1
    b_a      =0.05
else:
    rho_cat_a = st.sidebar.number_input("Anode Catalyst Density (g/cm³)", value=10.0)
    c_cat_a = st.sidebar.number_input("Anode Catalyst Cost ($/g)", value=50.0)
    j0_a = st.sidebar.number_input("Anode Exchange Current Density (A/cm²_active)", value=1e-2)
    
    S_cat_a = st.sidebar.number_input("Anode Specific Surface Area (cm²_active/g)", value=100000.0)
    a_a      = st.sidebar.number_input("Anode Tafel a (V)",value=0.1)
    b_a      = st.sidebar.number_input("Anode Tafel b (V)",value=0.05)

st.sidebar.header("Cathode Catalyst Selection")
cathode_catalyst = st.sidebar.selectbox("Cathode Catalyst", ["Pt", "Pt-Ru", "Custom"])
if cathode_catalyst == "Pt":
    rho_cat_c = 21.45 #Cathode Catalyst Density (g/cm³)"
    c_cat_c = 60.0 #Anode Catalyst Cost ($/g) **$27.30 to $59.00 per gram**
    j0_c = 1e-2 # "Cathode j0 (A/cm²_active 
    # S_cat_c = 100000.0
    
    a_c      = 0.08
    b_c      = 0.04
elif cathode_catalyst == "Pt-Ru":
    rho_cat_c = 16.0 #Cathode Catalyst Density (g/cm³)" #10 to 15 g/cm³
    c_cat_c = 55.0 # Anode Catalyst Cost ($/g)
    j0_c = 1e-2 # "Cathode j0 (A/cm²_active **0.1 to 450 mA/cm²**
    S_cat_c = 100000.0
    
    a_c      = 0.08
    b_c      = 0.04
else:
    rho_cat_c = st.sidebar.number_input("Cathode Catalyst Density (g/cm³)", value=21.45)
    c_cat_c = st.sidebar.number_input("Cathode Catalyst Cost ($/g)", value=60.0)
    j0_c = st.sidebar.number_input("Cathode Exchange Current Density (A/cm²_active)", value=1e-2)
    S_cat_c = st.sidebar.number_input("Cathode Specific Surface Area (cm²active/g)", value=100000.0)
    a_c      = st.sidebar.number_input("Cathode Tafel a (V)",value=0.08)
    b_c      = st.sidebar.number_input("Cathode Tafel b (V)",value=0.04)


with st.sidebar.expander("More Customizations"):
    alpha  = st.number_input("Charge Transfer Coeff alpha",value=0.5) #0.5 to 1, For the anode (oxidation reaction), the charge transfer coefficient is often around 2, while for the cathode (reduction reaction), it is approximately 0.51

    C_bulk_a = st.number_input("Anode Bulk Conc (mol/cm³)", format="%.4f", value=0.056) #Concentration ≈ rho/molar mass = (1 g/cm³) / (18 g/mol) ≈ **0.056 mol/cm³** (or 56 mol/L)
    D_a = st.number_input("Anode Diffusivity (cm²/s)", format="%.4f", value=0.26) #Bulk Diffusivity of Water Vapor (D): 0.26 cm²/s at 80°C and 1 atm. ld value 1e-2
    tau_a = st.number_input("Anode Tortuosity", value=1.2) #  1.27 to 2.13

    C_bulk_c = st.number_input("Cathode Bulk Conc (mol/cm³)", format="%.4f", value=0.001) #**0.001-0.002 mol/cm³** # formally 0.01
    D_c = st.number_input("Cathode Diffusivity (cm²/s)", format="%.6f", value=2e-5) #For water at room temperature, it's around 2×10−5cm2​/s #old =1e-2
    tau_c = st.number_input("Cathode Tortuosity", value=1.27) #  1.27 to 2.13



###############################################################################
# 21-Constraint Bounds
###############################################################################
st.sidebar.write("-----")
st.sidebar.header("21 Constraints Bounds")
# Global
eta_max= st.sidebar.number_input("Max Overpotential (V)", value=2.0)
j_min, j_max= st.sidebar.slider("Operating current density j range",0.0,9.0,(0.1,6.0),format="%.2f")

# Anode
st.sidebar.header("Anode Layer Constraints")
eps_a_min, eps_a_max= st.sidebar.slider("Anode Porosity Range, %", 0.001,0.999,(0.301,0.600),format="%.3f")#35-50%
delta_a_min,delta_a_max= st.sidebar.slider("Anode Thickness, μm",1,100,(1,30), format="%.2f") #4-10 μm
# Convert delta from microns to centimeters
delta_a_min_cm, delta_a_max_cm = delta_a_min * 1e-4, delta_a_max * 1e-4
Scat_a_min,Scat_a_max= st.sidebar.slider("Anode S_cat Range (m²/g)",10,1000,(100,300),format="%.3f")   # 200-800 m²/g 100 - 300 m²/g <sub>Ir</sub>
Scat_a_min,Scat_a_max=Scat_a_min * 1e4, Scat_a_max* 1e4     #m2/g to cm2/g      
L_a_min,L_a_max= st.sidebar.slider("Anode Catalyst Loading range, (g/cm^2)",0.0,0.05,(0.001,0.02),format="%.3f")
SA_a_min= st.sidebar.number_input("Anode Effective Surface Min (m²/g)",value=5.0,) #15-80 m²/g
SA_a_min =SA_a_min * 1e4#(m²/g) to (cm²/g)
# Cathode
st.sidebar.header("Cathode Layer Constraints")
eps_c_min, eps_c_max= st.sidebar.slider("Cathode Porosity Range %",0.001,0.999,(0.300,0.700),format="%.3f")
delta_c_min,delta_c_max= st.sidebar.slider("Cathode Thickness μm",1,100,(1,30),format="%.2f")#4-10 μm
delta_c_min,delta_c_max= delta_c_min * 1e-4, delta_c_max* 1e-4
Scat_c_min,Scat_c_max= st.sidebar.slider("Cathode S_cat Range",10,1000,(50,200),format="%.3f") #- Cathode: 50 - 200 m²/g Pt
Scat_a_min,Scat_a_max=Scat_a_min * 1e4, Scat_a_max* 1e4    #m2/g to cm2/g
L_c_min,L_c_max= st.sidebar.slider("Cathode Catalyst Loading range, (g/cm^2)",0.0,0.05,(0.001,0.02),format="%.3f")
SA_c_min= st.sidebar.number_input("Cathode Effective Surface Min (cm²)",value=10.0) #15-80 m²/g
SA_c_min =SA_c_min * 1e4   


###############################################################################
# Pareto-based settings
###############################################################################
st.sidebar.write("-----")
st.sidebar.header("Algorithm Settings (Pareto-based only)")
pop_size=st.sidebar.number_input("Population Size",value=40,min_value=10)
n_gen=   st.sidebar.number_input("Number of Gens",value=30,min_value=10)

###############################################################################
# RUN
###############################################################################
if st.button("Run Optimization"):
    with st.spinner("Running..."):
        run_kwargs= dict(
            category=method_category,
            method=method_name,
            # Problem parameters
            A_cell=A_cell,
            j=j,
            R=R,
            T=T,
            alpha=alpha,
            n=n_e,
            F=F_const,
            # anode side
            C_bulk_a=C_bulk_a,
            D_a=D_a,
            tau_a=tau_a,
            # cathode side
            C_bulk_c=C_bulk_c,
            D_c=D_c,
            tau_c=tau_c,
            eta_max=eta_max,
            # catalyst anode
            rho_cat_a=rho_cat_a,
            c_cat_a=c_cat_a,
            j0_a=j0_a,
            a_a=a_a,
            b_a=b_a,
            # catalyst cathode
            rho_cat_c=rho_cat_c,
            c_cat_c=c_cat_c,
            j0_c=j0_c,
            a_c=a_c,
            b_c=b_c,
            # constraints
            eps_a_min=eps_a_min, eps_a_max=eps_a_max,
            delta_a_min=delta_a_min, delta_a_max=delta_a_max,
            Scat_a_min=Scat_a_min, Scat_a_max=Scat_a_max,
            L_a_min=L_a_min, L_a_max=L_a_max,
            SA_a_min=SA_a_min,

            eps_c_min=eps_c_min, eps_c_max=eps_c_max,
            delta_c_min=delta_c_min, delta_c_max=delta_c_max,
            Scat_c_min=Scat_c_min, Scat_c_max=Scat_c_max,
            L_c_min=L_c_min, L_c_max=L_c_max,
            SA_c_min=SA_c_min,

            j_min=j_min, j_max=j_max,

            # 21 constraints => n_constr=21 in PEMProblem
            # plus we define if tau is a direct param
            # tau_a=tau_a, tau_c=tau_c,

            # pass scalar_params
            scalar_params=scalar_params
        )

        # If Pareto-based => pass pop_size/n_gen
        if method_category=="Pareto-based":
            try:
                res = run_optimization(**run_kwargs, pop_size=pop_size, n_gen=n_gen)
            except Exception as e:
                st.error(f"Error in Pareto-based: {e}")
                st.stop()
        else:
            # scalar => WeightedSum or GoalSeeking
            try:
                res = run_optimization(**run_kwargs)
            except Exception as e:
                st.error(f"Error in Scalarization: {e}")
                st.stop()

    if res.X is None or res.F is None:
        st.error("No feasible solutions or solver failure.")
    else:
        st.success("Optimization complete!")
        if method_category=="Scalarization":
            # single best solution
            st.write("**Best Single-Objective Solution**")
            var_names= ["delta_a","eps_a","S_cat_a","delta_c","eps_c","S_cat_c"]
            for var,val in zip(var_names, res.X):
                st.write(f" - **{var}**: {val:.6f}")
            st.write("Objective Value:", res.F[0])
        else:
            # Pareto front
            F = res.F
            X = res.X
            if F.ndim==1 or len(F)==1:
                st.write("Single solution found => possibly infeasible or dominated.")
                st.write("X:",X)
                st.write("F:",F)
            else:
                var_names=["delta_a","eps_a","S_cat_a","delta_c","eps_c","S_cat_c"]
                obj_names=["Cost","Overpotential"]
                df = create_dataframe(X,F,var_names,obj_names)

                st.subheader("Pareto Front (Objectives)")
                fig_obj = px.scatter(df, x="Cost", y="Overpotential",
                                     hover_data=df.columns)
                st.plotly_chart(fig_obj, use_container_width=True)

                st.subheader("Decision Variables")
                fig_par = px.parallel_coordinates(df,color="Cost",
                    labels={col:col for col in df.columns})
                st.plotly_chart(fig_par,use_container_width=True)

                st.subheader("Performance Metrics")
                metric_choice= st.selectbox("Choose a metric:",
                                            ["None","Hypervolume","C-Metric","Euclidean Distance"])
                if metric_choice=="Hypervolume":
                    refp=(1.1*max(F[:,0]),1.1*max(F[:,1]))
                    hv_val = compute_hypervolume(F, ref_point=refp)
                    st.write(f"Hypervolume ~ {hv_val:.4f}")
                elif metric_choice=="C-Metric":
                    c_val = compute_c_metric(F,F2=F)
                    st.write(f"C-Metric Self= {c_val:.4f}")
                elif metric_choice=="Euclidean Distance":
                    dist_val = compute_euclidean_distance(F,(0,0))
                    st.write(f"Avg Distance => {dist_val:.4f}")

                st.subheader("All Pareto Solutions")
                st.dataframe(df)

                sums = F[:,0]+F[:,1]
                idx_sorted=np.argsort(sums)
                top3=idx_sorted[:3]
                st.markdown("### Top 3 Solutions by Cost+Overpotential")
                for rank, idx in enumerate(top3):
                    st.markdown(f"**Rank {rank+1}** => Cost={F[idx,0]:.4f}, Overpot={F[idx,1]:.4f}")
                    st.json({var_names[i]: X[idx][i] for i in range(len(var_names))})


###############################################################################
# SAVE, LOAD, CLEAR
###############################################################################
st.sidebar.header("Results I/O")

if "results_data" not in st.session_state:
    st.session_state["results_data"] = None

def save_results(data, fname=None):
    if fname is None:
        now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname=f"results_{now_str}.json"
    path = os.path.join(RESULTS_DIR,fname)
    with open(path,"w") as f:
        json.dump(data,f,indent=2)
    return fname

def load_results(fname):
    path=os.path.join(RESULTS_DIR,fname)
    if not os.path.exists(path):
        return None
    with open(path,"r") as f:
        return json.load(f)

def clear_all_results(pattern="results_*.json"):
    import glob
    files=glob.glob(os.path.join(RESULTS_DIR,pattern))
    for file in files:
        os.remove(file)

c1,c2,c3= st.sidebar.columns(3)
with c1:
    if st.button("Save Results"):
        st.sidebar.warning("No direct 'res' object in scope. Consider your approach to storing final results.")
with c2:
    if st.button("Load Results"):
        flist=[f for f in os.listdir(RESULTS_DIR) if f.endswith(".json")]
        if not flist:
            st.sidebar.warning("No results found.")
        else:
            latest=max(flist, key=lambda x: os.path.getctime(os.path.join(RESULTS_DIR,x)))
            loaded=load_results(latest)
            if loaded:
                st.session_state["results_data"]=loaded
                st.sidebar.info(f"Loaded => {latest}")
            else:
                st.sidebar.warning(f"Failed to load => {latest}")

with c3:
    if st.button("Clear Results"):
        clear_all_results()
        st.session_state["results_data"]=None
        st.sidebar.warning("All results cleared.")

if st.session_state["results_data"] is not None:
    st.sidebar.markdown("---")
    st.sidebar.write("### Loaded Results Data")
    st.sidebar.json(st.session_state["results_data"])



#----------------
from utils.visualization import  create_full_dataframe, design_space_scatter_matrix, design_space_parallel_coordinates, compute_hypervolume, compute_c_metric, compute_euclidean_distance
from utils.optimization import PEMProblem
# After your optimization run is complete and you have "res"
if res.X is not None and res.F is not None:
    st.success("Optimization complete!")
    # Display best solution or Pareto front as you already do...
    
    # --- Now, re-create the problem instance for visualization.
    # You can re-use the same run_kwargs that were used for the optimization.
    # For demonstration, we assume run_kwargs is available or you can reassemble it.
    problem_vis = PEMProblem(**run_kwargs)  # Make sure run_kwargs contains the same keys used by PEMProblem.
    
    # Create a full DataFrame that includes constraint values.
    df_full = create_full_dataframe(problem_vis, res.X, res.F)
    
    st.subheader("Full Design Space (Decision Variables, Objectives, Constraints)")
    st.dataframe(df_full)
    
    # Create a scatter matrix (you can choose which columns to include)
    dims = ["Cost", "Overpotential"] + [col for col in df_full.columns if col.startswith("G")]
    fig_scatter = design_space_scatter_matrix(df_full, dimensions=dims, color="Cost")
    st.subheader("Scatter Matrix Plot")
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Create a parallel coordinates plot
    fig_parallel = design_space_parallel_coordinates(df_full, dimensions=dims, color="Cost")
    st.subheader("Parallel Coordinates Plot")
    st.plotly_chart(fig_parallel, use_container_width=True)


#--------------
# st.write("---")
# st.markdown("<footer><p style='text-align: right;'> 2025 S2D2 Lab | Penn State</p></footer>", unsafe_allow_html=True)