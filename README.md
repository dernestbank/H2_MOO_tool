# H2_MOO_tool
A opensource Multiobjectve optimization tool to explore Sustainable Hydrogen Production


Below is the complete mathematical formulation for our PEM electrolyzer membrane design multiobjective optimization problem. In this formulation, we have three objectives—maximizing energy efficiency, minimizing capital cost, and minimizing environmental impact—while enforcing a minimum lifetime (durability) constraint as well as a mechanical (stress‐based) constraint. The following sections detail the decision variables, dependent equations, and constraints.

---

## 1. Decision Variables

Let

\[
x = \begin{bmatrix} t \\ i \end{bmatrix},
\]

where

- \( t \) is the membrane thickness (m),
- \( i \) is the operating current density (A/cm\(^2\)).

The design space is bounded by practical limits:

\[
t_{\min} \le t \le t_{\max}, \quad i_{\min} \le i \le i_{\text{lim}}.
\]

For example, one might set
\[
t \in [50 \times 10^{-6}, \,300 \times 10^{-6}]\,\text{m}, \quad i \in [0.5,\, 6.0]\,\text{A/cm}^2.
\]

---

## 2. Objective Functions

### 2.1 Energy Efficiency

The energy efficiency of the electrolyzer is defined as the ratio of the chemical energy stored in the produced hydrogen (using its higher heating value) to the electrical energy input. For a given cell, the hydrogen production rate is expressed as

\[
\dot{m}_{H_2} = \frac{i \cdot A_{\text{cell}} \cdot 3600 \cdot MW_{H_2} \cdot \eta_F}{2F},
\]

where  
- \(A_{\text{cell}}\) is the cell active area (cm\(^2\)),  
- \(MW_{H_2}\) is the molecular weight of hydrogen (kg/mol),  
- \(\eta_F\) is the Faradaic efficiency (typically close to 1),  
- \(F \approx 96485\,\text{C/mol}\) is Faraday’s constant.

Assuming that a stack of \(N_{\text{cell}}\) cells is operated in series and that the overall cell current is \(I_{\text{cell}} = i\cdot A_{\text{cell}}\), the energy efficiency becomes

\[
\eta_{\text{energy}} = \frac{HHV_{H_2} \cdot \bigl(N_{\text{cell}} \cdot \dot{m}_{H_2}\bigr)}{V_{\text{cell}} \cdot \bigl(i\cdot A_{\text{cell}} \bigr)\cdot N_{\text{cell}}}
= \frac{HHV_{H_2} \cdot 3600 \cdot MW_{H_2} \cdot \eta_F}{2F \cdot V_{\text{cell}}(t,i)},
\]

where \(HHV_{H_2}\) is the higher heating value of hydrogen (J/kg).  
The cell voltage \(V_{\text{cell}}(t,i)\) is modeled as

\[
V_{\text{cell}}(t,i) = V_{oc} + \Delta V_{act}(i) + \Delta V_{ohm}(t,i) + \Delta V_{conc}(i),
\]

with

- **Open‐circuit voltage:** \(V_{oc}\) (≈1.23 V),
- **Activation overpotential:** For instance, using a Tafel equation,
  
  \[
  \Delta V_{act}(i) = \frac{RT}{\alpha F}\ln\left(\frac{i}{i_0}\right),
  \]
  
  where \(R\) is the gas constant, \(T\) the temperature, \(\alpha\) the transfer coefficient, and \(i_0\) the exchange current density.
- **Ohmic overpotential:** Summing contributions from the membrane and electrodes,
  
  \[
  \Delta V_{ohm}(t,i) = i\left(\frac{t}{\sigma_{mem}} + \frac{t_{el}}{\sigma_{el}}\right),
  \]
  
  where \(\sigma_{mem}\) is the membrane conductivity, \(t_{el}\) is the electrode thickness, and \(\sigma_{el}\) is the electrode conductivity.
- **Concentration overpotential:** \(\Delta V_{conc}(i)\) (a known function of \(i\), approaching significant values as \(i\) nears the limiting current density).

Because we wish to maximize efficiency, we define our first objective as the negative of efficiency:

\[
f_1(x) = -\eta_{\text{energy}}(t,i) = -\frac{HHV_{H_2}\cdot3600\cdot MW_{H_2}\cdot\eta_F}{2F \cdot V_{\text{cell}}(t,i)}.
\]

---

### 2.2 Cost Objective

We focus on the manufacturing cost per unit membrane area. Using an NREL‐inspired annual cost model, the total annualized cost is given by

\[
C_{\text{annualized}} = CRF_{\text{equipment}} \cdot \Bigl( S_{req} \cdot C_{\text{mfg line}} \,(1+R_{installation}) \Bigr)
+ CRF_{\text{building}} \cdot \Bigl( S_{req} \cdot R_{buildings} \cdot M_{footprint} \Bigr)
+ C_{\text{energy}} + C_{\text{labor}} + C_{\text{materials}},
\]

where:

- \(CRF(i,n) = \dfrac{i(1+i)^n}{(1+i)^n - 1}\) is the capital recovery factor for a given interest rate \(i\) and period \(n\).
- \(S_{req}\) is the number of manufacturing lines required, determined as

  \[
  S_{req} = \frac{A_{\text{annual}}}{L_{cap}},
  \]
  
  with \(A_{\text{annual}}\) the total membrane area produced annually and \(L_{cap}\) the production capacity per line.
- \(C_{\text{mfg line}}\) is the cost of a manufacturing line.
- \(R_{installation}\) is the installation cost fraction.
- \(CRF_{\text{equipment}}\) and \(CRF_{\text{building}}\) are the capital recovery factors for equipment and building costs, respectively.
- \(R_{buildings}\) is the building cost per unit area and \(M_{footprint}\) is the required footprint.
- \(C_{\text{energy}}\) and \(C_{\text{labor}}\) are annual energy and labor costs.
- \(C_{\text{materials}}\) is the cost of the membrane materials:

  \[
  C_{\text{materials}} = c_{ionomer} \cdot \rho_{mem} \cdot t \cdot A_{\text{cell}}.
  \]

For our model—where we normalize per unit area—the cost objective simplifies to a function primarily of \(t\):

\[
f_2(x) = \frac{C_{\text{annualized}}(x)}{A_{\text{annual}}(x)} \approx c_{ionomer}\,\rho_{mem}\,t + c_{manuf},
\]

where \(c_{manuf}\) aggregates the fixed manufacturing costs per m². (In a more detailed model, the dependence on production throughput and other factors would be explicitly included.)

---

### 2.3 Environmental Impact Objective

Assuming that the environmental impact is largely driven by the mass of the membrane produced, we define an environmental impact (in kg CO₂‐eq per m²) as

\[
f_3(x) = c_E \cdot \rho_{mem} \cdot t,
\]

where \(c_E\) is the environmental impact factor (kg CO₂‐eq/kg).

---

## 3. Constraints

### 3.1 Lifetime (Durability) Constraint

Let the membrane lifetime be modeled by

\[
L(t,i) = L_{base} + \alpha_L \, t - \beta_L \, i,
\]

where
- \(L_{base}\) is a baseline lifetime (hours),
- \(\alpha_L\) quantifies the beneficial effect of increased thickness,
- \(\beta_L\) quantifies the detrimental effect of high current density.

We require

\[
L(t,i) \ge L_{min},
\]

which can be expressed as a constraint function

\[
g_1(x) = L_{min} - \Bigl(L_{base} + \alpha_L \, t - \beta_L \, i\Bigr) \le 0.
\]

### 3.2 Mechanical Durability Constraint

Using a simplified stress model for a thin plate subject to a pressure difference \(\Delta P\), the approximate stress is

\[
\sigma \approx k\,\frac{\Delta P \, r^2}{t^2},
\]

where:
- \(r\) is a characteristic dimension (e.g., effective radius),
- \(k\) is a geometric constant.

The allowable stress is \(\sigma_{\text{allow}} = \sigma_{tensile}/SF\) where \(SF\) is the safety factor. We then impose:

\[
k\,\frac{\Delta P \, r^2}{t^2} \le \frac{\sigma_{tensile}}{SF}.
\]

Rearranging gives a lower bound on \(t\):

\[
t \ge t_{\text{mech,min}} = r\,\sqrt{\frac{k\,\Delta P\,SF}{\sigma_{tensile}}}.
\]

This constraint is written as:

\[
g_2(x) = t_{\text{mech,min}} - t \le 0.
\]

### 3.3 Variable Bounds

We also enforce:

\[
t_{\min} \le t \le t_{\max}, \quad i_{\min} \le i \le i_{\text{lim}}.
\]

---

## 4. Final Multiobjective Optimization Problem

The full optimization problem is stated as follows:

### Decision Variables

\[
x = \begin{bmatrix} t \\ i \end{bmatrix}, \quad t \in [t_{\min}, t_{\max}], \quad i \in [i_{\min}, i_{\text{lim}}].
\]

### Objectives

We wish to minimize the following three objective functions:

1. **Negative Energy Efficiency (to maximize efficiency):**

\[
f_1(x) = -\eta_{\text{energy}}(t,i) = -\frac{HHV_{H_2}\cdot3600\cdot MW_{H_2}\cdot\eta_F}{2F \cdot \left(V_{oc} + \Delta V_{act}(i) + i\left(\frac{t}{\sigma_{mem}}+\frac{t_{el}}{\sigma_{el}}\right) + \Delta V_{conc}(i)\right)}.
\]

2. **Capital Cost per Unit Area:**

\[
f_2(x) = c_{ionomer}\,\rho_{mem}\,t + c_{manuf},
\]

where \(c_{manuf}\) represents the aggregated manufacturing cost per m².

3. **Environmental Impact per Unit Area:**

\[
f_3(x) = c_E \,\rho_{mem}\,t.
\]

### Constraints

1. **Lifetime Constraint:**

\[
g_1(x) = L_{min} - \Bigl(L_{base} + \alpha_L\,t - \beta_L\,i\Bigr) \le 0.
\]

2. **Mechanical Durability Constraint:**

\[
g_2(x) = t_{\text{mech,min}} - t \le 0, \quad \text{with } t_{\text{mech,min}} = r\,\sqrt{\frac{k\,\Delta P\,SF}{\sigma_{tensile}}}.
\]

3. **Bounds:**

\[
t_{\min} \le t \le t_{\max}, \quad i_{\min} \le i \le i_{\text{lim}}.
\]

---

## 5. Parameter Definitions and Data Sources

- **Constants for Efficiency:**
  - \(HHV_{H_2}\): Higher Heating Value of hydrogen (e.g., 142 MJ/kg).
  - \(MW_{H_2}\): Molecular weight of hydrogen (0.002016 kg/mol).
  - \(\eta_F\): Faradaic efficiency (typically ~0.95–1).
  - \(F\): Faraday's constant (96485 C/mol).
  - \(V_{oc}\): Open-circuit voltage (≈1.23 V).
  - \(\Delta V_{act}(i)\): Activation overpotential (via Tafel relation).
  - \(\Delta V_{ohm}(t,i) = i \left(\frac{t}{\sigma_{mem}} + \frac{t_{el}}{\sigma_{el}}\right)\).
  - \(\Delta V_{conc}(i)\): Concentration overpotential.

- **Cost Parameters:**
  - \(c_{ionomer}\): Cost of ionomer (\$/kg).
  - \(\rho_{mem}\): Membrane density (kg/m³).
  - \(c_{manuf}\): Manufacturing cost per m² (\$/m²).

- **Environmental Parameters:**
  - \(c_E\): Environmental impact factor (kg CO₂-eq/kg).

- **Lifetime Model:**
  - \(L_{base}\): Baseline lifetime (hours).
  - \(\alpha_L\): Lifetime increase per unit thickness.
  - \(\beta_L\): Lifetime decrease per unit current density.
  - \(L_{min}\): Minimum acceptable lifetime (hours).

- **Mechanical Constraint Parameters:**
  - \(r\): Characteristic dimension (m).
  - \(k\): Geometric constant.
  - \(\Delta P\): Pressure difference across the membrane (Pa).
  - \(SF\): Safety factor.
  - \(\sigma_{tensile}\): Tensile strength (Pa).

- **Variable Bounds:**
  - \(t_{\min}\), \(t_{\max}\): Minimum and maximum membrane thickness.
  - \(i_{\min}\), \(i_{\text{lim}}\): Minimum and limiting current density.

Data for these parameters is typically sourced from experimental measurements, manufacturer datasheets, and published literature (e.g., NREL reports, Bessarabov & Millet, 2018).

---

## 6. Summary of the Full Formulation

\[
\boxed{
\begin{aligned}
\textbf{Decision Variables:} \quad & x = \begin{bmatrix} t \\ i \end{bmatrix}, \quad t \in [t_{\min}, t_{\max}], \quad i \in [i_{\min}, i_{\text{lim}}]. \\
\\[1mm]
\textbf{Objective Functions:} \quad & \text{Minimize } F(x) = \begin{bmatrix}
f_1(x) \\ f_2(x) \\ f_3(x)
\end{bmatrix} \quad \text{with:} \\
& f_1(x) = -\frac{HHV_{H_2}\cdot3600\cdot MW_{H_2}\cdot\eta_F}{2F \cdot \left(V_{oc} + \Delta V_{act}(i) + i\left(\frac{t}{\sigma_{mem}}+\frac{t_{el}}{\sigma_{el}}\right) + \Delta V_{conc}(i)\right)}, \\
& f_2(x) = c_{ionomer}\,\rho_{mem}\,t + c_{manuf}, \\
& f_3(x) = c_E \,\rho_{mem}\,t. \\
\\[1mm]
\textbf{Constraints:} \quad & g_1(x) = L_{min} - \Bigl(L_{base} + \alpha_L\,t - \beta_L\,i\Bigr) \le 0, \\
& g_2(x) = t_{\text{mech,min}} - t \le 0, \quad \text{with } t_{\text{mech,min}} = r\,\sqrt{\frac{k\,\Delta P\,SF}{\sigma_{tensile}}}, \\
& t_{\min} \le t \le t_{\max}, \quad i_{\min} \le i \le i_{\text{lim}}.
\end{aligned}
}
\]

