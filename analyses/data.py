import os
import pandas as pd

# On remonte d'un cran depuis analyses/ pour trouver src/car_insurance.csv
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, 'src', 'car_insurance.csv')

df = pd.read_csv(CSV_PATH)
