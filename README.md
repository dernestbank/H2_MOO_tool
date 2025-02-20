# H2_MOO_tool
A opensource Multiobjectve optimization tool to explore Sustainable Hydrogen Production

## Optimization Objectives

We aim to achieve the following objectives:

### Primary Objectives

1. **Maximize Energy Efficiency**: Reduce energy consumption while maintaining operational viability.
2. **Minimize Capital Cost**: Optimize investment expenditures to ensure cost-effectiveness.
3. **Minimize Environmental Impact**: Limit ecological footprint through responsible resource utilization.

### Constraints

- **Minimum Lifetime (Durability) Constraint**: Ensure a minimum lifetime of the product or system to guarantee its functionality and performance over time.
- **Mechanical (Stress‐Based) Constraint**: Comply with stress-based limits to prevent mechanical failure and ensure component longevity.

---

## 1. Decision Variables

Let

$$x = \begin{bmatrix} t \\ i \end{bmatrix},$$

where

- $t$ is the membrane thickness (m),
- $i$ is the operating current density ($A/cm^2$).

The design space is bounded by practical limits:

$$t_{\min} \le t \le t_{\max}, \quad i_{\min} \le i \le i_{\text{lim}}.$$ 

For example, one might set:

$$t \in [50 \times 10^{-6}, 300 \times 10^{-6}]\,\text{m}, \quad i \in [0.5, 6.0] \text{ A/cm}^2.$$ 

---

## 2. Objective Functions

### 2.1 Energy Efficiency

The energy efficiency of the electrolyzer is defined as the ratio of the chemical energy stored in the produced hydrogen (using its higher heating value) to the electrical energy input. For a given cell, the hydrogen production rate is expressed as:

$$
\dot{m}_{H_2} = \frac{i \cdot A_{\text{cell}} \cdot 3600 \cdot MW_{H_2} \cdot \eta_F}{2F},
$$

where:

- $A_{\text{cell}}$ is the cell active area ($cm^2$),
- $MW_{H_2}$ is the molecular weight of hydrogen (kg/mol),
- $\eta_F$ is the Faradaic efficiency (typically close to 1),
- $F \approx 96485\,\text{C/mol}$ is Faraday’s constant.

Assuming that a stack of $N_{\text{cell}}$ cells is operated in series and that the overall cell current is $I_{\text{cell}} = i \cdot A_{\text{cell}}$, the energy efficiency becomes:

$$
\eta_{\text{energy}} = \frac{HHV_{H_2} \cdot 3600 \cdot MW_{H_2} \cdot \eta_F}{2F \cdot V_{\text{cell}}(t,i)},
$$

where $HHV_{H_2}$ is the higher heating value of hydrogen (J/kg).  
The cell voltage $V_{\text{cell}}(t,i)$ is modeled as:

$$
V_{\text{cell}}(t,i) = V_{oc} + \Delta V_{act}(i) + \Delta V_{ohm}(t,i) + \Delta V_{conc}(i),
$$

with:

- **Open‐circuit voltage:** $V_{oc}$ (≈1.23 V),
- **Activation overpotential:**
    $$
    \Delta V_{act}(i) = \frac{RT}{\alpha F}\ln\left(\frac{i}{i_0}\right),
    $$
- **Ohmic overpotential:**
    $$
    \Delta V_{ohm}(t,i) = i\left(\frac{t}{\sigma_{mem}} + \frac{t_{el}}{\sigma_{el}}\right),
    $$
- **Concentration overpotential:** $\Delta V_{conc}(i)$.

We define our first objective as the negative of efficiency:

$$
 f_1(x) = -\eta_{\text{energy}}(t,i) = -\frac{HHV_{H_2}\cdot3600\cdot MW_{H_2}\cdot\eta_F}{2F \cdot V_{\text{cell}}(t,i)}.
$$

---

### 2.2 Cost Objective

Using a cost model, the cost per unit area is:

$$
 f_2(x) = c_{ionomer}\,\rho_{mem}\,t + c_{manuf},
$$

where $c_{manuf}$ aggregates the fixed manufacturing costs per $m^2$.

---

### 2.3 Environmental Impact Objective

Assuming that the environmental impact is largely driven by the mass of the membrane produced, we define:

$$
 f_3(x) = c_E \cdot \rho_{mem} \cdot t,
$$

where $c_E$ is the environmental impact factor (kg CO₂‐eq per m²).

---

## 3. Constraints

### 3.1 Lifetime (Durability) Constraint

Let the membrane lifetime be modeled as:

$$
 L(t,i) = L_{base} + \alpha_L \, t - \beta_L \, i.
$$

We require:

$$
 L(t,i) \ge L_{min},
$$

which can be rewritten as:

$$
 g_1(x) = L_{min} - (L_{base} + \alpha_L \, t - \beta_L \, i) \le 0.
$$

### 3.2 Mechanical Durability Constraint

Using a simplified stress model:

$$
 \sigma \approx k\,\frac{\Delta P \, r^2}{t^2}.
$$

The allowable stress is:

$$
 \frac{\sigma_{tensile}}{SF}.
$$

Imposing:

$$
 k\,\frac{\Delta P \, r^2}{t^2} \le \frac{\sigma_{tensile}}{SF},
$$

we obtain a lower bound:

$$
 t \ge t_{\text{mech,min}} = r\,\sqrt{\frac{k\,\Delta P\,SF}{\sigma_{tensile}}}.
$$

Thus, the constraint is:

$$
 g_2(x) = t_{\text{mech,min}} - t \le 0.
$$

---

## 4. Final Multiobjective Optimization Problem

### Decision Variables

$$
 x = \begin{bmatrix} t \\ i \end{bmatrix}, \quad t \in [t_{\min}, t_{\max}], \quad i \in [i_{\min}, i_{\text{lim}}].
$$

### Objectives

$$
 \text{Minimize } F(x) = \begin{bmatrix} f_1(x) \\ f_2(x) \\ f_3(x) \end{bmatrix}.
$$

### Constraints

$$
 g_1(x) \le 0, \quad g_2(x) \le 0.
$$

This formulation integrates energy efficiency, cost, environmental impact, and durability into a structured optimization problem.
