"""
Setup script for the Flask Portfolio API
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="flask-portfolio-api",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Advanced Flask API for portfolio showcase",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/flask-portfolio-api",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Flask",
    ],
    python_requires=">=3.8",
)