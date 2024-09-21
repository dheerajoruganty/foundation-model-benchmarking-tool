import streamlit as st
import subprocess

# Streamlit app layout
st.title("First Time Setup")

st.markdown("This page is designed to get you up and running on EC2.")

# Use columns to place text and button side by side
col1, col2 = st.columns([3, 1])

with col1:
    st.write("")
    st.write(
        """This button Creates a local directory structure needed for FMBench 
            and copies all publicly available dependencies from the AWS S3 bucket for FMBench.
            This is done by running the copy_s3_content.sh script available as part of the FMBench repo. 
        """
    )

with col2:
    if st.button("Run Setup Command"):
        # Define the curl command
        curl_command = "curl -s https://raw.githubusercontent.com/aws-samples/foundation-model-benchmarking-tool/main/copy_s3_content.sh | sh -s -- /tmp"

        # Execute the curl command and capture the output
        result = subprocess.run(
            curl_command, shell=True, capture_output=True, text=True
        )

        # Display the command output
        st.write("### Command Output:")
        st.code(result.stdout)

        # Display the command error, if any
        if result.stderr:
            st.write("### Command Error:")
            st.code(result.stderr)

# Divider
st.write("---")


# Upload Section for Huggingface API File
st.header("Upload Hugging Face Token")

# File uploader to upload hf_token file
hf_token_file = st.file_uploader(f"Upload Hugging Face Token", type=["txt"])

if hf_token_file is not None:
    # Save the uploaded file temporarily or process it as needed
    save_path = f"/tmp/{hf_token_file.name}"
    with open(save_path, "wb") as f:
        f.write(hf_token_file.getbuffer())
    st.success(f"File '{hf_token_file.name}' uploaded successfully'!")

    # Display uploaded file details
    st.write("### Uploaded File Details:")
    st.write(f"File name: {hf_token_file.name}")
    st.write(f"File type: {hf_token_file.type}")
    st.write(f"File size: {hf_token_file.size} bytes")

st.write("---")

# Upload Section for Tokenizer Files
st.header("Upload Tokenizer for Specific Models")

# List of models
models = ["LLaMA 3", "Claude", "Other"]

# Dropdown to select the model
model_selected = st.selectbox("Select the Model", models)

# File uploader to upload tokenizer file
tokenizer_file = st.file_uploader(
    f"Upload the Tokenizer for {model_selected}", type=["json"]
)

if tokenizer_file is not None:
    # Save the uploaded file temporarily or process it as needed
    save_path = f"/tmp/{tokenizer_file.name}"
    with open(save_path, "wb") as f:
        f.write(tokenizer_file.getbuffer())
    st.success(
        f"File '{tokenizer_file.name}' uploaded successfully for model '{model_selected}'!"
    )

    # Display uploaded file details
    st.write("### Uploaded File Details:")
    st.write(f"File name: {tokenizer_file.name}")
    st.write(f"File type: {tokenizer_file.type}")
    st.write(f"File size: {tokenizer_file.size} bytes")

st.write("---")

# Upload Section for Tokenizer Files
st.header("Upload Config File for Selected Model")

# File uploader to upload tokenizer file
config_file = st.file_uploader(
    f"Upload the config file for {model_selected}", type=["json"]
)

if config_file is not None:
    # Save the uploaded file temporarily or process it as needed
    save_path_dict = {'Llama3' : 'llama3/tokenizer'}
    #WIP SAVE PATH DICT MAPPING
    save_path = f"/tmp/fmbench-read/{config_file.name}"
    with open(save_path, "wb") as f:
        f.write(config_file.getbuffer())
    st.success(
        f"File '{config_file.name}' uploaded successfully for model '{model_selected}'!"
    )

    # Display uploaded file details
    st.write("### Uploaded File Details:")
    st.write(f"File name: {config_file.name}")
    st.write(f"File type: {config_file.type}")
    st.write(f"File size: {config_file.size} bytes")

st.write("---")
