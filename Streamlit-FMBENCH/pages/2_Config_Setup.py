import os
import time
import glob
import subprocess
import streamlit as st

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
    CONFIG_FILE_PATH = 'src/fmbench/configs/' + selected_config_file



if st.button("Run FMBENCH with Selected Config"):
    command = [
        "fmbench", 
        "--config-file", CONFIG_FILE_PATH, 
        "--local-mode", "yes", 
        "--write-bucket", "placeholder", 
        "--tmp-dir", "/tmp"
    ]

    LOGFILE="fmbench.log"

    # Function to run the subprocess
    def run_subprocess_and_tail():
    # Start the subprocess
        with open(LOGFILE, "w") as log:
            process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)

        # Display live log output in Streamlit
        log_placeholder = st.empty()
        while process.poll() is None:  # While the process is running
            with open(LOGFILE, "r") as log_file:
                log_file.seek(0, os.SEEK_END)  # Go to the end of the file
                log_content = log_file.read()
                log_placeholder.text_area("Live Log Output", log_content, height=400)
            time.sleep(1)  # Sleep for 1 second before next check

        # After completion, display the final log
        with open(LOGFILE, "r") as log_file:
            log_content = log_file.read()
            log_placeholder.text_area("Final Log Output", log_content, height=400)
        st.success("Command completed!")

    def stop_subprocess():
        if st.session_state.process and st.session_state.process.poll() is None:
            st.session_state.process.terminate()
            st.success("Subprocess terminated.")

    
    # Streamlit App
    st.title("Run and Stop fmbench with Streamlit")

    # Button to start the subprocess and show live log
    if st.button("Run Command and Show Live Log"):
        if st.session_state.process is None or st.session_state.process.poll() is not None:
            st.write("Running the command...")
            run_subprocess_and_tail()
        else:
            st.warning("A process is already running.")

    # Button to stop the subprocess
    if st.button("Stop Command"):
        stop_subprocess()
    
    
    
    
    
    
    
    # # Streamlit App Layout
    # st.title("Run fmbench Command and Display Log Output")

    # # Button to trigger the command
    # if st.button("Run Command"):
    #     st.write("Running the command...")
    #     run_subprocess_and_tail()
    #     st.success("Command completed!")

    # # Button to display log file content
    # if os.path.exists(LOGFILE):
    #     if st.button("Display Log File"):
    #         with open(LOGFILE, "r") as log_file:
    #             log_content = log_file.read()
    #             st.text_area("Log Output", log_content, height=400)
    # else:
    #     st.write("Log file not found. Run the command first.")

