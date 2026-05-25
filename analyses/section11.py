import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LogisticRegression, Perceptron
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import KFold, cross_val_score

import analyses.section7 as s7
from analyses.section7 import RANDOM_SEED


# On compare plusieurs algorithmes avec la MÊME validation croisée (5 plis) pour
# que ce soit juste. Pour le KNN on teste plusieurs valeurs de k (le nombre de
# voisins) car c'est son principal réglage.
_kf = KFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)

_modeles = {
    "Régression logistique": LogisticRegression(max_iter=1000, random_state=RANDOM_SEED),
    "Perceptron":            Perceptron(random_state=RANDOM_SEED),
    "KNN (k=3)":             KNeighborsClassifier(n_neighbors=3),
    "KNN (k=5)":             KNeighborsClassifier(n_neighbors=5),
    "KNN (k=7)":             KNeighborsClassifier(n_neighbors=7),
    "KNN (k=11)":            KNeighborsClassifier(n_neighbors=11),
}


def _comparer():
    """Lance la CV de tous les modèles sur le jeu d'apprentissage courant (s7)."""
    resultats = {}
    for nom, modele in _modeles.items():
        scores = cross_val_score(modele, s7.X_train, s7.y_train, cv=_kf, scoring='accuracy')
        resultats[nom] = (float(scores.mean()), float(scores.std()))
    meilleur = max(resultats, key=lambda n: resultats[n][0])
    return resultats, meilleur, resultats[meilleur][0]


# Score moyen et écart-type de chaque modèle (calculés une fois à l'import).
# Meilleur modèle = meilleur score moyen. Réutilisé tel quel en section 12.
RESULTATS, MEILLEUR_NOM, MEILLEUR_SCORE = _comparer()


def reentrainer():
    """
    Relance la comparaison des algorithmes sur le jeu d'apprentissage COURANT
    (proportion choisie en §7) et met à jour RESULTATS / MEILLEUR_NOM /
    MEILLEUR_SCORE. La section 12 repart ensuite du meilleur recalculé.
    """
    global RESULTATS, MEILLEUR_NOM, MEILLEUR_SCORE
    RESULTATS, MEILLEUR_NOM, MEILLEUR_SCORE = _comparer()


# ── Fonctions ouvertes par les boutons ────────────────────────────────────────

def show_comparaison():
    """
    Barres horizontales du score moyen de chaque modèle, avec une barre d'erreur
    (l'écart-type entre les plis). Le meilleur modèle est mis en vert.
    """
    noms     = list(RESULTATS.keys())
    moyennes = [RESULTATS[n][0] for n in noms]
    ecarts   = [RESULTATS[n][1] for n in noms]
    couleurs = ['#4A8C4A' if n == MEILLEUR_NOM else '#4A7FA5' for n in noms]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    fig.suptitle("Comparaison d'algorithmes — accuracy (validation croisée 5 plis)",
                 fontsize=11)

    y = np.arange(len(noms))
    ax.barh(y, moyennes, xerr=ecarts, color=couleurs, edgecolor='#333333',
            error_kw={'ecolor': '#333333'})
    ax.set_yticks(y)
    ax.set_yticklabels(noms, fontsize=9)
    ax.invert_yaxis()                # le premier modèle en haut
    ax.set_xlim(0, 1)
    ax.set_xlabel("Accuracy moyenne")

    for i, (m, e) in enumerate(zip(moyennes, ecarts)):
        ax.text(m + e + 0.01, i, f"{m:.3f}", va='center', fontsize=8)

    plt.tight_layout()
    plt.show()


# ── Infos pour les cartes en bas de l'onglet ──────────────────────────────────

def get_info_section11():
    return [
        (str(len(RESULTATS)),     "modèles testés", "#444444"),
        (MEILLEUR_NOM,            "meilleur",       "#4A8C4A"),
        (f"{MEILLEUR_SCORE:.3f}", "son score CV",   "#4A7FA5"),
    ]
