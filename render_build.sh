#!/usr/bin/env bash
# exit on error
set -o errexit

# First uninstall any existing numpy and pandas
pip uninstall -y numpy pandas

# Install specific versions that are known to work together
pip install numpy==1.20.3
pip install pandas==1.3.3

# Install xlsxwriter for Excel support
pip install xlsxwriter==3.0.3

# Then install the rest of the requirements
pip install -r requirements.txt

# Make sure we have the correct versions
pip list | grep numpy
pip list | grep pandas 