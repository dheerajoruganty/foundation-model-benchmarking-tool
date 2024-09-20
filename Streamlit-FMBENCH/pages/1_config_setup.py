import streamlit as st
import os
import glob

st.set_page_config(
    page_title="Config Setup",
    page_icon="📈",
)

# Define the root directory to search for config files
root_directory = "../src/fmbench/configs"

# Step 1: Folder Selection
# Get a list of all subdirectories in the root directory
folders = [f.path for f in os.scandir(root_directory) if f.is_dir()]

# Extract just the folder names for the dropdown
folder_names = [os.path.relpath(folder, root_directory) for folder in folders]

selected_folder = st.selectbox("Select Folder", folder_names)

# Define the path to the selected folder
selected_folder_path = os.path.join(root_directory, selected_folder)

# Step 2: Parameter Subfolder Selection (if any)
# Check for subfolders in the selected folder
parameter_subfolders = [f.path for f in os.scandir(selected_folder_path) if f.is_dir()]

if parameter_subfolders:
    # If subfolders exist, show another dropdown to select a parameter subfolder
    parameter_names = [
        os.path.relpath(folder, selected_folder_path) for folder in parameter_subfolders
    ]
    selected_parameter = st.selectbox("Select Parameter Subfolder", parameter_names)
    selected_parameter_path = os.path.join(selected_folder_path, selected_parameter)
else:
    # If no subfolders, use the selected folder directly
    selected_parameter_path = selected_folder_path

# Step 3: Config File Selection
# Use glob to find all config files matching 'config*' in the selected folder or subfolder
config_files = glob.glob(os.path.join(selected_parameter_path, "config*"))

# Extract just the filenames for display in the dropdown
config_file_names = [os.path.relpath(file, root_directory) for file in config_files]

if config_file_names:
    selected_config_file = st.selectbox("Select Config File", config_file_names)
else:
    st.warning("No config files found in the selected folder or subfolder.")

# Display the selected config file
if config_file_names:
    st.write(f"Selected config file: {selected_config_file}")

st.button("Re-run")