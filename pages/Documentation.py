import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="PEM Electrolyzer Optimization Documentation",
    page_icon="📚",
    layout="wide",
)

# --- HEADER ---
st.title("📚 Documentation")
st.markdown("""
 **PEM Electrolyzer Multi-objective Optimization(MOO) Tool** documentation.  \n
This documentaon will guide your throught the overview, ntallation and contribution towards this framework. provides insights into **multi-objective optimization algorithms**, **design parameters**, and the **implementation** of this tool.
""")

# Sidebar Navigation
st.sidebar.header("📖 Table of Contents")
page = st.sidebar.radio("Navigate to:", 
    ["Project Overview", 
     "Optimization Algorithms",
     "Design Parameters",
     "Installation Guide",
     "Contributing",
     "Future Development",
     "References"])

# --- PROJECT OVERVIEW ---
if page == "Project Overview":
    st.header(" Project Overview")
    
    st.subheader("🔍 Objectives")
    st.markdown("""
    The **PEM Electrolyzer Optimization Playground** is designed to:
    - **Optimize** the design of **Membrane Electrode Assemblies (MEA)** for PEM electrolyzers.
    - **Balance trade-offs** between efficiency, cost, and environmental impact.
    - **Provide interactive visualization tools** for design analysis.
    - **Facilitate research and industrial applications** in hydrogen production.
    """)

    st.subheader("📌 Scope")
    st.markdown("""
    This tool enables users to:
    - Optimize **catalyst layer design** using advanced multi-objective optimization.
    - Model **performance characteristics** of key PEM electrolyzer components.
    - Conduct **cost-performance trade-off analysis**.
    - Explore **different system configurations** interactively.
    """)

    st.subheader(" Applications")
    st.markdown("""
    **Ideal for:**
    - **R&D teams** working on PEM electrolyzer development.
    - **Manufacturers** seeking cost-effective designs.
    - **Academics & researchers** studying electrolysis technology.
    - **Policy analysts** evaluating hydrogen sustainability.
    """)

# --- OPTIMIZATION ALGORITHMS ---
elif page == "Optimization Algorithms":
    st.header(" Multi-Objective Optimization Algorithms")

    st.markdown("""
    Multi-objective optimization (MOO) is essential for **balancing efficiency, cost, and environmental impact**.     The tool implements both **evolutionary algorithms** and **scalarization methods** to explore the **Pareto front** of optimal solutions.
    """)

    st.subheader("🔵  Evolutionary Algorithms (Genetic Algorithms)")
    
    st.image("https://miro.medium.com/v2/resize:fit:640/format:webp/1*1eXlFkAn9gy4rgdmetXqqw.png", caption= "Demonstration of a Genetic Algorithm, Source: pastmke.com", use_container_width=True)
    
    st.markdown("""
     The genetic algorithm is a class of stochastic, parallel search heuristics method for solving both constrained and unconstrained optimization problems that is based on natural selection  and evolution. 
     It's a search technique that can find approximate or exact solutions to optimization and search problems.            
                
    **Genetic Algorithms (GAs)** mimic natural selection, evolving solutions over generations through selection, crossover, and mutation.    These are particularly effective for **multi-objective problems** where trade-offs must be considered.
    
    
    The simulated evolution of the population goes as follows:
    
        1. Generation of the initial population: Start with a random population of solutions 
        
        2. Repeat until some user specified criterion or a certain number of generations have been exceeded:
        Evaluate each solution's fitness, or how well it solves the problem 
        
        - Evaluation of the individuals by applying the objective score (fitness function)

        - Selection of one or more parent individuals

        - Application of genetic operators to build the next generation population
        
            Mutation: Randomly change the genetic information of some individuals 
            Crossover: Swap genetic material between individuals 
            Selection: Only allow the fittest individuals to survive and reproduce
        
Key concepts: 
- Genetic diversity: Mutation and crossover help maintain genetic diversity within the population.
- Fitness: The algorithm favors solutions with higher fitness values.
- Termination condition: The algorithm may terminate when it reaches a desired fitness level or exceeds a specified number of iterations.

    
Reference:
John Holland is generally considered the father of genetic algorithms.    [link](https://link.springer.com/10.1007/978-3-642-11274-4_629#:~:text=John%20Holland%20is%20generally%20accepted,Fogel)
    """)

    with st.expander("🔵 NSGA-II (Non-dominated Sorting Genetic Algorithm II)"):
        st.markdown("""
        **NSGA-II** is one of the most widely used **Pareto-based** evolutionary algorithms for multi-objective optimization.
         It effectively finds a set of diverse Pareto optimal solutions by employing a non-dominated sorting approach, making it particularly useful for problems with multiple conflicting objectives where you need to find a range of good solutions rather than just one "best" solution; 
         
         - **Princples**:
            - Uses **fast non-dominated sorting** to classify solutions.
            - Implements **crowding distance** to maintain diversity.
            - Preserves **elitism**, ensuring high-quality solutions persist.
         
         Key points about NSGA-II:
        - Multi-objective optimization:
        Designed to solve problems with multiple objectives that might contradict each other, aiming to find a set of solutions that represent the best trade-offs between these objectives. 
        - Non-dominated sorting:
        The core mechanism where solutions are ranked based on their dominance relationships, meaning a solution is considered better than another if it is not dominated by it in any objective. 
        - Crowding distance:
        A metric used to maintain diversity within a non-dominated front, ensuring that solutions across the entire Pareto front are represented. 
        - Elitism:
        Retains the best solutions from the previous generation to guide the search towards better solutions. 
        - Genetic operators:
        Uses standard genetic operators like crossover and mutation to generate new solutions and explore the search space. 
            
        ![NSGA-II](https://ars.els-cdn.com/content/image/1-s2.0-S0016236123014394-gr13.jpg)      
        
        - **Specializations**:
            - Handles **nonlinear and non-convex** optimization problems.
            - Provides **well-distributed Pareto fronts**.
            - Suitable for problems with **many conflicting objectives**.

        - **Application to PEM Electrolyzers**:
            - Identifies optimal trade-offs between **efficiency, cost, and environmental impact**.
            - Helps in refining **electrode materials and structure**.
        """)

    with st.expander(" 🔵 MOEA/D (Multi-objective Evolutionary Algorithm based on Decomposition)"):
        st.markdown("""
        **MOEA/D** decomposes a **multi-objective problem** into **multiple single-objective subproblems**, solving them concurrently.
        It solves multi-objective problems by dividing the original complex problem into a set of simpler, scalarized subproblems which are then optimized simultaneously, effectively allowing the algorithm to find a diverse set of near-optimal solutions along the Pareto front.
        It breaks down a multi-objective problem into smaller, more manageable single-objective problems that can be solved collaboratively to approximate the best possible solutions across all objectives. 
            
        Key concepts
        - Decomposition approach:
            The core idea is to decompose the multi-objective problem into multiple single-objective subproblems using weight vectors, which guide the search towards different parts of the Pareto optimal set. 
        - Neighboring information:
            Each subproblem interacts with its neighboring subproblems to maintain diversity and explore the solution space effectively. 
        - Scalarization:
            Each subproblem is transformed into a single-objective problem using a scalarization function (like weighted sum or Tchebycheff) based on its assigned weight vector. 
        ![MOEA/D](https://ars.els-cdn.com/content/image/1-s2.0-S0360835222004302-gr2.jpg)
            
        - **How It Works**:
            1. Initialize population:
            Generate a population of solutions and assign weight vectors to each individual. 
            2. Decomposition:
            For each individual, calculate its corresponding scalarized objective function using the assigned weight vector. 
            3. Evolutionary process:
            Selection: Select individuals based on their performance in the scalarized objective function. 
            Variation: Apply genetic operators like crossover and mutation to generate new offspring. 
            Update population: Update the population by incorporating new offspring, often using a neighborhood-based mechanism to maintain diversity. 

        - **Specializations**:
            - More efficient for **large-scale optimization problems**.
            - Provides **better diversity control** than NSGA-II.
            - Suitable for cases where **objectives have different scales**.
            
            - Efficient handling of complex problems:
            By decomposing the problem, MOEA/D can tackle multi-objective optimization problems with a large number of objectives or complex constraints. 
            - Good diversity:
            The use of weight vectors helps to maintain diversity in the population, ensuring a good spread of solutions across the Pareto front. 
            - Computational efficiency:
            Compared to other multi-objective algorithms, MOEA/D can often be computationally efficient due to its decomposition approach

        - **Application to PEM Electrolyzers**:
            - Allows **customized weighting** for different trade-offs.
            - Supports **fine-tuning of PEM electrolyzer operational parameters**.
        """)

    with st.expander("🔵 SPEA2 (Strength Pareto Evolutionary Algorithm 2)"):
        st.markdown("""
        **SPEA2** improves upon earlier Pareto-based methods by enhancing solution diversity and robustness.
          It approximats the Pareto-optimal set for multiobjective optimization problems. This is an improved version of the original SPEA algorithm, incorporating a more refined fitness assignment strategy and density estimation techniques to achieve better diversity in the solution set.
             
         Key ponts about SPEA2:
        - Pareto-based:
        It aims to identify the Pareto optimal front, which represents the set of solutions that cannot be improved in any objective without worsening another.    
        - Fitness assignment:
        SPEA2 uses a sophisticated fitness calculation that considers both dominance relationships and the density of solutions in the objective space, ensuring a good balance between convergence and diversity. 
        - Archive management:
        A key component of SPEA2 is a non-dominated archive that stores the best solutions found so far, which is updated and truncated to maintain a diverse set of non-dominated solutions.    
        
        ![SPEA2](https://ars.els-cdn.com/content/image/1-s2.0-S0898122112000843-gr1.jpg)
            
        - **How It Works**:
            - Assigns **fitness scores** based on Pareto dominance.
            - Uses **density estimation** to avoid overcrowding.
            - Maintains an **external archive** of optimal solutions.

                    
            
        - **Applications**:
            - Helps in **fine-tuning design choices**.
            - Ensures **long-term durability and economic feasibility**.
            - SPEA2 has been used to design waveforms for radar systems that perform multiple missions simultaneously. 
            - Engineering design optimization (e.g., designing a mechanical component with multiple performance criteria)
            - Portfolio optimization (balancing risk and return)
            - Resource allocation problems
            - Machine learning hyperparameter tuning 
        """)

    st.subheader(" Scalarization-Based Methods")
    with st.expander("🔵 Weighted Sum Method"):
        st.markdown("""
          The weighted sum method is a decision-making tool that evaluates multiple options by assigning weights to each option's criteria. It's also known as the weighted linear combination or simple additive weighting method.           
       
        ![Weighted Sum](https://media.geeksforgeeks.org/wp-content/uploads/20240607142923/Weighted-Average-Formula-768.png)
        
        - Converts multiple objectives into a **single weighted function**.
        - Best suited for **well-defined trade-offs**.
        - **Limitations**:
            - Can **miss solutions in non-convex Pareto fronts**.
        """)

    with st.expander("🔵 Goal-Seeking Method"):
        st.markdown("""
          "Goal-Seeking Method" is a technique where you specify a desired outcome (the "goal") and then work backwards to find the input values that would produce that result, essentially using trial and error to adjust variables until the calculated output matches your target goal          
         it's commonly used in spreadsheet programs like Excel with a feature called "Goal Seek" to solve problems where you know the desired result but need to find the necessary input to achieve it.
        
        - Converts multiple objectives into a **single weighted function**.
        - Finds solutions **closest to pre-defined target values**.
        - Practical for industries that need **specific performance benchmarks**.
        """)

# --- DESIGN PARAMETERS ---
elif page == "Design Parameters":
    st.header(" Key Design Parameters for Optimization")

    with st.expander(" Catalyst Layer Parameters"):
        st.markdown("""
        ### Physical Parameters
        1. **Layer Thickness (δ)**
           - Range: 5-30 µm
           - Impact: Mass transport and active site availability
           
        2. **Porosity (ε)**
           - Range: 0.3-0.7
           - Impact: Reactant transport and catalyst utilization
           
        3. **Specific Surface Area**
           - Range: 50-800 m²/g
           - Impact: Active site density and reaction kinetics
        
        ### Material Properties
        1. **Catalyst Loading**
           - Anode (IrO₂): 0.1-2.0 mg/cm²
           - Cathode (Pt): 0.05-0.4 mg/cm²
           
        2. **Exchange Current Density**
           - Anode: 10⁻²-10⁻³ A/cm²
           - Cathode: 10⁻³-10⁻⁴ A/cm²
        """)

    with st.expander(" Operating Conditions"):
        st.markdown("""
        - **Temperature Range**: 50-80°C.
        - **Pressure Range**: 1-30 bar.
        - **Current Density**: 0.5-2 A/cm².
        """)

# --- INSTALLATION GUIDE ---
elif page == "Installation Guide":
    
    st.subheader("Dependencies")
    st.markdown("""
    - Python 3.8+
    - streamlit
    - pymoo
    - numpy
    - plotly
    - pandas
    """)
    
    st.header("🖥️ Installation Guide")
    st.code("""
    git clone https://github.com/dernestbank/H2_MOO_tool.git
    cd PEM-electrolyzer-Python
    python -m venv env
    source env/bin/activate  # Linux/Mac
    env\\Scripts\\activate    # Windows
    pip install -r requirements.txt
    """)

# --- CONTRIBUTING ---
elif page == "Contributing":
    st.header("🤝 Contributing")
    st.markdown("""
    1. **Fork the repository**.
    2. **Create a feature branch**.
    3. **Make changes and test locally**.
    4. **Submit a pull request**.
    """)
    
    

# --- FUTURE DEVELOPMENT ---
elif page == "Future Development":
    st.header(" Future Development Roadmap")
    st.markdown("""
    - **Machine Learning-Assisted Optimization**.
    - **Life Cycle Assessment (LCA) Integration**.
    - **Techno-economic Modeling Enhancements**.
    """)

# --- REFERENCES ---
elif page == "References":
    st.header("📚 References")
    st.markdown("""
    
    - Chammam, A.; Kumar Tripathi, A.; Nuñez Alvarez, J. R.; O. Alsaab, H.; Romero-Parra, R. M.; Mohammad Mayet, A.; Abdullaev, S. S. Multiobjective Optimization and Performance Assessment of a PEM Fuel Cell-Based Energy System for Multiple Products. _Chemosphere_ **2023**, _337_, 139348. [https://doi.org/10.1016/j.chemosphere.2023.139348](https://doi.org/10.1016/j.chemosphere.2023.139348).
    
    - Li, H.; Xu, B.; Lu, G.; Du, C.; Huang, N. Multi-Objective Optimization of PEM Fuel Cell by Coupled Significant Variables Recognition, Surrogate Models and a Multi-Objective Genetic Algorithm. _Energy Conversion and Management_ **2021**, _236_, 114063. [https://doi.org/10.1016/j.enconman.2021.114063](https://doi.org/10.1016/j.enconman.2021.114063).
    
    - Lee, J.; Seol, C.; Kim, J.; Jang, S.; Kim, S. M. Optimizing Catalyst Loading Ratio between the Anode and Cathode for Ultralow Catalyst Usage in Polymer Electrolyte Membrane Fuel Cell. _Energy Technology_ **2021**, _9_ (7), 2100113. [https://doi.org/10.1002/ente.202100113](https://doi.org/10.1002/ente.202100113).
    
    - Nawale, S. M.; Dlamini, M. M.; Weng, F.-B. Analyses of the Effects of Electrolyte and Electrode Thickness on High Temperature Proton Exchange Membrane Fuel Cell (H-TPEMFC) Quality. _Membranes_ **2023**, _13_ (1), 12. [https://doi.org/10.3390/membranes13010012](https://doi.org/10.3390/membranes13010012).
    
    - Xia, Z.; Wang, Y.; Ma, L.; Zhu, Y.; Li, Y.; Tao, J.; Tian, G. A Hybrid Prognostic Method for Proton-Exchange-Membrane Fuel Cell with Decomposition Forecasting Framework Based on AEKF and LSTM. _Sensors_ **2023**, _23_ (1), 166. [https://doi.org/10.3390/s23010166](https://doi.org/10.3390/s23010166).
    
    - Rabascall, J. B.; Mirlekar, G. Sustainability Analysis and Simulation of a Polymer Electrolyte Membrane (PEM) Electrolyser for Green Hydrogen Production; 2023; pp 110–117. [https://doi.org/10.3384/ecp200015](https://doi.org/10.3384/ecp200015).
    
    - Ruiz-Mercado, G. J.; Gonzalez, M. A.; Smith, R. L. Expanding GREENSCOPE beyond the Gate: A Green Chemistry and Life Cycle Perspective. _Clean Techn Environ Policy_ **2014**, _16_ (4), 703–717. [https://doi.org/10.1007/s10098-012-0533-y](https://doi.org/10.1007/s10098-012-0533-y).

    - Prospective LCA of Alkaline and PEM Electrolyser Systems. _International Journal of Hydrogen Energy_ **2024**, _55_, 26–41. [https://doi.org/10.1016/j.ijhydene.2023.10.192](https://doi.org/10.1016/j.ijhydene.2023.10.192).

    - Critical and Strategic Raw Materials for Electrolysers, Fuel Cells, Metal Hydrides and Hydrogen Separation Technologies. _International Journal of Hydrogen Energy_ **2024**, _71_, 433–464. [https://doi.org/10.1016/j.ijhydene.2024.05.096](https://doi.org/10.1016/j.ijhydene.2024.05.096).
    - Badgett, A.; Brauch, J.; Thatte, A.; Rubin, R.; Skangos, C.; Wang, X.; Ahluwalia, R.; Pivovar, B.; Ruth, M. _Updated Manufactured Cost Analysis for Proton Exchange Membrane Water Electrolyzers_; NREL/TP--6A20-87625, 2311140, MainId:88400; 2024; p NREL/TP--6A20-87625, 2311140, MainId:88400. [https://doi.org/10.2172/2311140](https://doi.org/10.2172/2311140).
    
    - Chen, Y.; Liu, C.; Xu, J.; Xia, C.; Wang, P.; Xia, B. Y.; Yan, Y.; Wang, X. Key Components and Design Strategy for a Proton Exchange Membrane Water Electrolyzer. _Small Structures_ **2023**, _4_ (6), 2200130. [https://doi.org/10.1002/sstr.202200130](https://doi.org/10.1002/sstr.202200130).
    
    """)

st.write("---")
st.markdown("🔗 [GitHub Repository](https://github.com/dernestbank/H2_MOO_tool)")
