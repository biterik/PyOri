"""
Setup configuration for PyOri - grain boundary misorientation analysis package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="pyori",
    version="0.1.0",
    author="Converted from Fortran (A. Rollett et al.)",
    description="PyOri - Grain boundary misorientation analysis for cubic crystals",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/biterik/PyOri",
    package_dir={'': 'src'},  # Tell setuptools packages are under src/
    packages=[''],  # Empty string means the src directory itself
    py_modules=['quaternions', 'symmetry', 'csl', 'misorientation', 'cli'],  # List individual modules
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
        ],
    },
)