#!/usr/bin/env python
from setuptools import setup, find_packages

# Read the long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Define package requirements
requirements = [
    "requests>=2.28.0",
]

# Additional requirements for development
dev_requirements = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "coverage>=6.0.0",
    "black>=23.0.0",
    "isort>=5.10.0",
    "flake8>=5.0.0",
    "mypy>=1.0.0",
]

setup(
    name="kroger-python",
    version="0.1.0",  # Initial version, update as appropriate
    author="Your Name",  # Replace with your name
    author_email="your.email@example.com",  # Replace with your email
    description="Python client for the Kroger API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CodingPenguin1/kroger-python",  # Replace with your repo URL
    project_urls={
        "Bug Tracker": "https://github.com/CodingPenguin1/kroger-python/issues",
        "Documentation": "https://github.com/CodingPenguin1/kroger-python/blob/main/README.md",
        "Source Code": "https://github.com/CodingPenguin1/kroger-python",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
    },
    keywords="kroger, api, client, retail, grocery, shopping",
)
