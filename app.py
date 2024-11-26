import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

rkcolors  = ["#792427",
             "#54828e",
             "#d1bda2",
             "#80a198"]
custom_colors = [rkcolors[2], rkcolors[1]] # yellow reference, blue modified

change_colors = { # red negative, blue positive
    'Positive': rkcolors[3], 
    'Negative': rkcolors[0] 
}

# Read the CSV file to get the column names
#data_columns = pd.read_csv("./streamlit/performances.csv", nrows=0).columns

# Define the data types: all columns as strings except "performance"
#dtype_mapping = {col: str for col in data_columns if col != "performance"}

# Read the CSV with the specified data types
data_both = pd.read_csv("./streamlit/performances.csv", #dtype=dtype_mapping, 
                        na_values=[], keep_default_na=False) # avoid "None" to be converted to NA

#st.title("Comparison of decoding performance between two preprocessing pipelines")

# Create sidebar widgets for "reference" and "modified" filters
#st.sidebar.header("Select preprocessing steps")

# Add a decoder filter to filter the entire dataset
decoder_filter = st.sidebar.selectbox(
    "Select decoding model:",
    options=data_both['decoder'].unique(), #.dropna()
    index=0
)

# Apply the decoder filter to the DataFrame
data = data_both[data_both['decoder'] == decoder_filter]

if decoder_filter == "EEGNet":
    performance_metric = "Accuracy"
elif decoder_filter == "Time-Resolved":
    performance_metric = "T-Sum"

# Add a text comment
st.sidebar.text("Choose reference steps and modified steps:")

# Extract unique values for each column
filters = {}

# Split the sidebar into two columns for Reference and Modified filters
ref_col, mod_col = st.sidebar.columns(2)  # Create two columns

# Add titles to each column
with ref_col:
    st.markdown("### Reference Pipeline")  # Title for the Reference column
with mod_col:
    st.markdown("### Modified Pipeline")  # Title for the Modified column



for col in data.columns[:-3]:  # Exclude the "Accuracy" AND experiment column
    unique_values = data[col].unique()
    with ref_col:  # Place Reference filters in the first column
        filters[col] = {
            'reference': st.selectbox(f"{col}", unique_values, key=f"ref_{col}")
            #'reference': st.selectbox(f"Reference: {col}", unique_values, key=f"ref_{col}")
        }
    with mod_col:  # Place Modified filters in the second column
        filters[col]['modified'] = st.selectbox(f"{col}", unique_values, key=f"mod_{col}")
        #filters[col]['modified'] = st.selectbox(f"Modified: {col}", unique_values, key=f"mod_{col}")

    # filters[col] = {
    #     'reference': st.sidebar.selectbox(f"Reference: {col}", unique_values, key=f"ref_{col}"),
    #     'modified': st.sidebar.selectbox(f"Modified: {col}", unique_values, key=f"mod_{col}")
    # }

# Filter DataFrame based on selections
reference_filter = {col: filters[col]['reference'] for col in data.columns[:-3]}
modified_filter = {col: filters[col]['modified'] for col in data.columns[:-3]}

df_reference = data.loc[(data[list(reference_filter)] == pd.Series(reference_filter)).all(axis=1)]
df_modified = data.loc[(data[list(modified_filter)] == pd.Series(modified_filter)).all(axis=1)]


# Ensure there are values to compare
if not df_reference.empty and not df_modified.empty:
    ref_accuracies = df_reference['performance'].values
    mod_accuracies = df_modified['performance'].values

    # Create a bar plot
    plot_data = pd.DataFrame({
        'Pipeline': ['Reference'] * len(ref_accuracies) + ['Modified'] * len(mod_accuracies),
        'Performance': np.concatenate([ref_accuracies, mod_accuracies]),
        "Experiment": np.concatenate([df_reference['experiment'].values, df_modified['experiment'].values])
    })

    st.subheader("Performance comparison")
    #sns.barplot(x='Type', y='Accuracy', data=plot_data, palette=custom_colors) #palette="viridis")
    #plot_data.plot(x = "Type", y="Accuracy", kind='bar', stacked=True, color=sns.color_palette("tab10"), figsize=(8, 6)) #color=custom_colors, 
    plt.figure(figsize=(10, 4))
    
    # 1st, violin plot of all data points
    sns.violinplot(
        x='experiment',
        y='performance',
        data=data,  # Use your violin plot DataFrame
        inner=None,  # Removes inner markers to avoid clutter
        color="lightgray",  # Base color for the violin plot
        scale="width"  # Optional: Adjusts violin width proportional to sample size # TODO check
    )
    
    sns.scatterplot(x='Experiment', y="Performance", data=plot_data, hue='Pipeline', palette=custom_colors)
    plt.title("Reference pipeline vs. modified pipeline decoding performance")
    plt.ylabel(performance_metric)
    if performance_metric == "Accuracy":
        plt.axhline(0.5, color='k', linestyle='--', label="Chance level")
    plt.xlabel("Experiment")
    st.pyplot(plt.gcf())
    
    # barplot of changes
    st.subheader("Performance changes")
    change_data = pd.DataFrame({
        'Experiment': df_reference['experiment'].values,
        'Performance change': mod_accuracies - ref_accuracies
    })
    # performance change positive = blue, negative = red
    change_data['Direction'] = change_data['Performance change'].apply(lambda x: 'Positive' if x > 0 else 'Negative')
    plt.figure(figsize=(10, 4))
    sns.barplot(x='Experiment', y='Performance change', data=change_data, hue="Direction", palette=change_colors)
    plt.title("Performance changes between reference and modified pipelines")
    plt.axhline(0., color='k', linestyle='-')
    plt.legend().remove()
    st.pyplot(plt.gcf())
    
else:
    st.warning("Please select valid filter combinations for both reference and modified rows.")
    
    