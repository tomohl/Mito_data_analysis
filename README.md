# Mitochondrial Microscopy Data Analysis

## Installation:
clone git repo:   


Open Command Prompt

Navigate to the main folder in which you want to put the Python scipts:   
cd "Pathname"

Run:  

git clone https://github.com/kleele-lab/Mito_data_analysis.git

## make virtual environment
cd Mito_data_analysis
python -m venv env

## activate virtual environment (do this always before using):
.\env\Scripts\activate

## install dependencies:
pip install -r requirements.txt  
pip install --use-pep517 git+https://github.com/SchmollerLab/python-javabridge-windows

## use scripts: 
python "script.py"

