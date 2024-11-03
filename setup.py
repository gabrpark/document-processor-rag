# setup.py
from setuptools import setup, find_packages

setup(
    name="document-processor",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "pinecone-client>=3.0.0",
        "python-dotenv>=1.0.0",
        "tiktoken>=0.5.0",
        "langchain>=0.1.0",
        "numpy>=1.24.0",
        "tenacity>=8.2.0",
        "tqdm>=4.65.0",
    ],
)
