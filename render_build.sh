#!/usr/bin/env bash
# exit on error
set -o errexit

# Install numpy first to ensure compatibility
pip install numpy==1.22.4

# Then install the rest of the requirements
pip install -r requirements.txt

# Make sure pandas is properly installed with compatible dependencies
pip install pandas==1.3.3 --force-reinstall 