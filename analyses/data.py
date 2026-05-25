import os
import pandas as pd

# On remonte d'un cran depuis analyses/ pour trouver src/car_insurance.csv
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, 'src', 'car_insurance.csv')

df = pd.read_csv(CSV_PATH)


# Ordre logique d'encodage des variables qualitatives (str -> int).
# Placé ici (et non dans une section) car c'est une métadonnée du dataset utilisée
# à la fois par la section 4 (pour examiner ces variables comme les autres) et par
# la section 5 (pour l'encodage de la préparation). L'indice dans la liste = le code.
# LabelEncoder coderait par ordre alphabétique, ce qui n'a aucun sens pour des
# variables ordinales (ex : 'none' < 'high school' < 'university'). On fixe donc l'ordre.
ORDRE_ENCODAGE = {
    'driving_experience': ['0-9y', '10-19y', '20-29y', '30y+'],
    'education':          ['none', 'high school', 'university'],
    'income':             ['poverty', 'working class', 'middle class', 'upper class'],
    'vehicle_year':       ['before 2015', 'after 2015'],
    'vehicle_type':       ['sedan', 'sports car'],
}
