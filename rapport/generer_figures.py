"""
Génère les figures du rapport (PNG) à partir du code des sections.

On réutilise directement les fonctions show_xxx() des modules d'analyse pour que
les figures du rapport soient EXACTEMENT celles de l'application, sans dupliquer le
code de tracé. Astuce : ces fonctions se terminent par plt.show() ; on remplace
donc temporairement plt.show par une sauvegarde de la figure courante dans img_use/.

À lancer depuis la racine du projet :   .venv/bin/python rapport/generer_figures.py
"""
import os
import sys

# Permettre l'import du package `analyses` quel que soit le dossier d'exécution.
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RACINE)

import matplotlib
matplotlib.use('Agg')          # backend sans fenêtre : on sauvegarde au lieu d'afficher
import matplotlib.pyplot as plt

IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img_use')
os.makedirs(IMG, exist_ok=True)

# Cible courante : nom du fichier vers lequel le prochain plt.show() sera redirigé.
_cible = {'nom': None}


def _sauver_au_lieu_dafficher(*args, **kwargs):
    fig = plt.gcf()
    chemin = os.path.join(IMG, _cible['nom'])
    fig.savefig(chemin, dpi=130, bbox_inches='tight')
    plt.close(fig)


plt.show = _sauver_au_lieu_dafficher


def generer(nom_fichier, fonction):
    """Appelle la fonction de tracé ; son plt.show() sauvegarde dans img_use/nom_fichier."""
    _cible['nom'] = nom_fichier
    fonction()
    print(f"  img_use/{nom_fichier}")


# Les imports déclenchent les calculs de chaque section (modèle, métriques, CV...).
from analyses import section4, section6, section8, section9, section10, section11

print("Génération des figures du rapport :")

# Section 4 — examen des données
generer('histogrammes.png',          section4.show_histogrammes)
generer('aberrants.png',             section4.show_aberantes)

# Section 6 — corrélations
generer('heatmap.png',               section6.show_heatmap_correlations)
generer('correlations_outcome.png',  section6.show_correlations_outcome)
generer('scatter_matrix.png',        section6.show_scatter_matrix)

# Section 8 — régression logistique
generer('coefficients.png',          section8.show_coefficients)

# Section 9 — évaluation
generer('matrice_confusion.png',     section9.show_matrice_confusion)
generer('metriques.png',             section9.show_metriques)

# Section 10 — validation croisée
generer('scores_cv.png',             section10.show_scores_cv)

# Section 11 — comparaison d'algorithmes
generer('comparaison.png',           section11.show_comparaison)

print("Terminé.")
