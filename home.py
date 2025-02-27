import streamlit as st

st.set_page_config(
    page_title="PEM Electrolyzer Optimization Playground",
    page_icon="⚡",
    layout="wide",
)

# --- HEADER ---
col1, col2= st.columns([1,1])
with col1:
    st.write("S2D2 Lab | Penn State", )
st.title("PEM Electrolyzer Optimization Playground")
st.write("##### *A Platform for Exploring Sustainable Hydrogen Production*")


# st.image("https://biologic.net/wp-content/uploads/2023/11/scheme-electrolyzer-01.png",
#          caption="Basic schema of a PEM electrolyzer. Source: Biologic", use_column_width=True)  
col1,col2,col3 = st.columns([1,2,1])

with col2:
    st.image("app\images\scheme-electrolyzer-01.png",
             caption="Basic schema of a PEM electrolyzer. Source: Biologic",width=300, use_container_width=True )

# st.image("app\images\scheme-electrolyzer-01.png",
        #  caption="Basic schema of a PEM electrolyzer. Source: Biologic",width=300, use_container_width=0.7 )  

with col3:
    if st.button("Catalyst Layer Design"):
        st.switch_page("pages/1_Catalyst_layer.py")#1_Main_App.py
    if st.button("Membrane Design"):
        st.switch_page("pages/2_Membrane_layer.py")


    
# --- INTRODUCTION ---
st.header("Introduction")
st.write("""
Green hydrogen, produced through water electrolysis using renewable energy, is poised to play a pivotal role in decarbonizing various sectors. Proton Exchange Membrane (PEM) electrolyzers are a leading technology for this purpose, offering advantages like high efficiency, fast response, and compact design. However, challenges related to cost, durability, and performance remain. 

This interactive playground, developed by the **Sustainable Design, Systems, and Decision-making (S2D2) Lab** at Penn State, provides a platform to explore the intricate design space of PEM electrolyzers. By leveraging multi-objective optimization and simulation, we aim to unlock the full potential of this technology for a sustainable hydrogen future.

""")
st.write("---")

# --- OPPORTUNITIES WITH PEM ELECTROLYZERS ---
st.header("Opportunities for Sustainable Hydrogen Production")
st.write("""
PEM electrolyzers offer a unique pathway to sustainable hydrogen production, enabling:

*   **Integration with Renewable Energy:** Their fast response time makes them ideal for coupling with intermittent renewable sources like solar and wind, storing excess energy as hydrogen.
*   **Decarbonization of Industries:** Green hydrogen can replace fossil fuels in industries like steel, cement, and chemical production, significantly reducing their carbon footprint.
*   **Clean Transportation:** Fuel cell vehicles powered by green hydrogen offer a zero-emission alternative for transportation.
*   **Energy Storage:** Hydrogen can serve as a long-term energy storage medium, ensuring grid stability and resilience.

""")
with st.expander("Learn more about the advantages of PEM Electrolyzers"):
    st.write("""
        PEM electrolyzers have several advantages, including:
        - **Compact design:** PEM electrolyzers are more compact than alkaline electrolyzers. 
        - **High current density:** PEM electrolyzers can operate at high current densities. 
        - **Fast response:** PEM electrolyzers can be started, stopped, and ramped up and down quickly. 
        - **Pure hydrogen:** PEM electrolyzers can produce hydrogen that is 99.99% pure. 
    
        However, PEM electrolyzers are more expensive than alkaline electrolyzers because they require expensive materials like platinum and iridium.
    """)

# --- THE NEED FOR OPTIMIZATION ---
st.header("The Need for Optimization")
st.write("""
This playground focuses on optimizing the catalyst layer, a critical component influencing both cost and performance. The optimization problem involves:

*   **Minimizing Cost:** Reducing the amount of expensive catalyst materials (e.g., platinum, iridium).
*   **Maximizing Performance:** Minimizing the overpotential (a measure of energy loss) to enhance efficiency.

""")

# with st.expander("Learn more about the optimization parameters"):
#     st.write("""
#         The total overpotential (η_total) is the sum of the activation overpotential (η_act) and the concentration overpotential (η_conc):
        
#         η_total  = η_act  + η_conc
        
#         1. **Catalyst Layer Thickness (δ):**
            
#         	Activation Overpotential (η_act ): Increasing δ generally decreases η_act. This is because a thicker layer provides more catalyst material and thus more active sites for the reaction. However, this effect diminishes beyond a certain thickness where mass transport limitations become dominant.
#         	Concentration Overpotential (η_conc): Increasing δ generally increases η_conc. This is because a thicker layer increases the diffusion path for reactants and products, making it harder for them to reach or leave the reaction sites.
#         	Net Effect: The optimal thickness represents a balance between minimizing activation losses (favored by thicker layers) and minimizing mass transport losses (favored by thinner layers).
        
#         2. **Porosity (ε):**
            
#         	Activation Overpotential ( η_act  ): Increasing ε generally increases η_act. Higher porosity means less catalyst material per unit volume, reducing the number of active sites.
#         	Concentration Overpotential (η_conc ): Increasing ε generally decreases η_conc. Higher porosity improves mass transport by providing more open pathways for reactants and products.
#         	Net Effect: The optimal porosity represents a balance between maximizing active sites (favored by lower porosity) and minimizing mass transport resistance (favored by higher porosity).
        
#         3. **Specific Surface Area (Scat):**
        
#         	Activation Overpotential (η_act): Increasing Scat directly and significantly decreases η_act. Higher specific surface area means more active sites per unit mass of catalyst, leading to a higher reaction rate and lower activation losses. 
#         	Concentration Overpotential (η_conc): Scat has a minor indirect effect on η_conc. It can influence the overall catalyst layer structure, which might slightly affect mass transport, but the primary effect of Scat is on the activation overpotential.
#         	Net Effect: Increasing Scat is almost always beneficial for performance, as it directly reduces activation losses with minimal negative impact on mass transport. However, there are practical limits to how high Scat can be achieved.
        
#         **Surface Area Definitions:**
        
#         	Specific Surface Area (Scat): This is the surface area of the catalyst material per unit mass (typically m²/g). It's an intrinsic property of the catalyst material itself. For example, a catalyst with smaller nanoparticles will have a higher specific surface area than the same mass of catalyst with larger particles.   
        
#         	Effective Surface Area (SA_eff): This is the surface area of the catalyst that is actually available for the electrochemical reaction per unit geometric area of the electrode (typically cm²/cm³). It takes into account the porosity and thickness of the catalyst layer:
        
#         	SA_eff  = Scat * (1 - ε) * δ
        
#         	(1 - ε) represents the solid volume fraction of the catalyst layer.
#         	Multiplying by δ gives the effective surface area per unit geometric area of the electrode.
        
#         	Geometric Surface Area (A_cell): This is the macroscopic area of the electrode (typically cm²). It's the area that you would measure with a ruler. It is used to calculate the current density:
        
#         	j =I/A_cell   
        
#         Where I is the current.
        
#         In summary:
        
#         	δ: Affects both activation and concentration overpotentials in opposing ways. Optimal δ balances these effects.
#         	ε: Affects both activation and concentration overpotentials in opposing ways. Optimal ε balances these effects.
#         	Scat: Primarily affects activation overpotential, with higher Scat leading to lower η_act .
#         """
#         )
st.write("\n \n \n ")
st.write("---")
# --- THE S2D2 LAB ---
st.header("About the S2D2 Lab")
st.write("""
The Sustainable Design, Systems, and Decision-making (S2D2) Lab at Penn State is at the forefront of research on leveraging tools and technologies for sustainability transformation. Our work spans:

*   **Sustainable Design and Optimization**
*   **Industrial Biotechnology**
*   **Food-Energy-Water Systems**
*   **Plastics Recycling**
*   **Waste Valorization**

We navigate decision-making by linking engineering metrics with sustainability analyses, including life cycle assessment (LCA) and techno-economic analysis (TEA), under uncertainty.
""")
st.markdown("[Learn more about the S2D2 Lab(https://s2d2lab.notion.site/THE-S2D2-LAB-PSU-b90a0c2efb834588af281424e5ff5e53)")

# --- EXPLORE THE PLAYGROUND ---
st.header("Explore the Playground")
st.write("""
Dive into the interactive features of this playground to:

*   **Visualize the Design Space:** Understand the interplay between key parameters like catalyst loading, porosity, and thickness.
*   **Run Simulations:** Experiment with different optimization algorithms and parameters.
*   **Analyze Results:** Evaluate the trade-offs between cost and performance and identify optimal design configurations.
""")

# Add buttons/links to other pages if you have them
# For example:
# st.button("Start Exploring", key="explore_button", on_click=lambda: st.switch_page("main"))

st.write("---")
st.write("© 2025 S2D2 Lab | Penn State")