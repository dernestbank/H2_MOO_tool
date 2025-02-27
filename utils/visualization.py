# utils/visualization.py

import pandas as pd
import plotly.express as px

def create_dataframe(X, F, var_names=None, obj_names=None):
    """
    Create a combined DataFrame of decision variables (X) and objectives (F).
    var_names: list of decision variable names
    obj_names: list of objective names
    """
    N, D = X.shape
    M = F.shape[1]

    if var_names is None:
        var_names = [f"Var_{i+1}" for i in range(D)]
    if obj_names is None:
        obj_names = [f"Obj_{j+1}" for j in range(M)]

    df = pd.DataFrame(X, columns=var_names)
    for j, name in enumerate(obj_names):
        df[name] = F[:, j]
    return df

def scatter_matrix_plot(df, dimensions=None, color=None):
    """
    Plotly scatter matrix.
    dimensions: columns to include
    color: column name for coloring points
    """
    if dimensions is None:
        dimensions = df.columns
    fig = px.scatter_matrix(df, dimensions=dimensions, color=color)
    return fig

def parallel_coordinates_plot(df, dimensions=None, color=None):
    """
    Plotly parallel coordinates plot.
    """
    if dimensions is None:
        dimensions = df.columns
    fig = px.parallel_coordinates(df, dimensions=dimensions, color=color)
    return fig

def heatmap_plot(df, x_var, y_var, z_var):
    """
    Heatmap using pivot_table to aggregate z_var over x_var,y_var
    """
    pivot_df = df.pivot_table(index=y_var, columns=x_var, values=z_var, aggfunc='mean')
    fig = px.imshow(pivot_df, aspect='auto', color_continuous_scale='Viridis', 
                    labels=dict(color=z_var), title=f"Heatmap of {z_var}")
    return fig

def glyph_plot(df, x, y, size_col=None, color_col=None):
    """
    Scatter plot as a 'glyph' plot with size and color encodings.
    """
    fig = px.scatter(df, x=x, y=y, size=size_col, color=color_col, 
                     title="Glyph Plot", hover_data=df.columns)
    return fig




# appended these functions to visualize design space

import numpy as np
import pandas as pd
import plotly.express as px

def create_full_dataframe(problem, X, F):
    """
    Given a problem instance and arrays X (decision variables) and F (objectives)
    (both from an optimization run), evaluate the constraints for each solution
    and return a DataFrame that includes decision variables, objectives, and constraints.
    
    Parameters:
      - problem: an instance of PEMProblem (or your problem class)
      - X: 2D array of decision variable values (num_solutions x num_vars)
      - F: 2D array of objective values (num_solutions x num_objs)
    
    Returns:
      A pandas DataFrame with columns for decision variables, objectives, and constraint violations.
    """
    # Evaluate constraints for each solution
    G_list = []
    for x in X:
        out = {}
        # Evaluate the problem at x; _evaluate expects x and writes to out["G"]
        problem._evaluate(x, out)
        G_list.append(out["G"])
    G_array = np.array(G_list)
    
    # Define names for columns
    var_names = ["delta_a", "eps_a", "S_cat_a", "delta_c", "eps_c", "S_cat_c"]
    obj_names = ["Cost", "Overpotential"]
    # Use generic names for constraint columns: G1, G2, ...
    cons_names = [f"G{i+1}" for i in range(G_array.shape[1])]
    
    df_vars = pd.DataFrame(X, columns=var_names)
    df_objs = pd.DataFrame(F, columns=obj_names)
    df_cons = pd.DataFrame(G_array, columns=cons_names)
    
    return pd.concat([df_vars, df_objs, df_cons], axis=1)

def design_space_scatter_matrix(df, dimensions=None, color=None):
    """
    Create a scatter matrix plot of the given DataFrame.
    """
    if dimensions is None:
        dimensions = df.columns
    fig = px.scatter_matrix(df, dimensions=dimensions, color=color)
    return fig

def design_space_parallel_coordinates(df, dimensions=None, color=None):
    """
    Create a parallel coordinates plot of the given DataFrame.
    """
    if dimensions is None:
        dimensions = df.columns
    fig = px.parallel_coordinates(df, dimensions=dimensions, color=color)
    return fig
