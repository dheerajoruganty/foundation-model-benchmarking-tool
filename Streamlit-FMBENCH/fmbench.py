import streamlit as st
import os
import glob

st.set_page_config(
    page_title="Foundation Model Benchmarking Tool",
    page_icon="👋",
)

st.write("# Foundation Model Benchmarking Tool")

st.markdown(
    """
`FMBench` is a Python package for running performance benchmarks for any Foundation Model (FM) deployed on any AWS Generative AI service, be it Amazon SageMaker, Amazon Bedrock, Amazon EKS, or Amazon EC2. The FMs could be deployed on these platforms either directly through FMbench, or, if they are already deployed then also they could be benchmarked through the Bring your own endpoint mode supported by FMBench.

Here are some salient features of **FMBench**:

- Highly flexible: in that it allows for using any combinations of instance types (g5, p4d, p5, Inf2), inference containers (DeepSpeed, TensorRT, HuggingFace TGI and others) and parameters such as tensor parallelism, rolling batch etc. as long as those are supported by the underlying platform.

- Benchmark any model: it can be used to be benchmark open-source models, third party models, and proprietary models trained by enterprises on their own data.

- Run anywhere: it can be run on any AWS platform where we can run Python, such as Amazon EC2, Amazon SageMaker, or even the AWS CloudShell. It is important to run this tool on an AWS platform so that internet round trip time does not get included in the end-to-end response time latency.
"""
)