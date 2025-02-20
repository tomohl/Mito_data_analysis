# Student_microscopy_analysis

## Installation:
clone git repo:   


Open Command Prompt

Navigate to the main folder in which you want to put the Python scipts:   
cd "Pathname"

Run:  

git clone https://gitlab.ethz.ch/kwentinck/student_microscopy_analysis.git

## make virtual environment
cd Student_microscopy_analysis   
python -m venv env

## activate virtual environment (do this always before using):
.\env\Scripts\activate

## install dependencies:
pip install -r requirements.txt  
pip install "napari[all]"

## use scripts: 
python "script.py"

