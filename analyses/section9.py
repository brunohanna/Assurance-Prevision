import matplotlib.pyplot as plt
from sklearn.metrics import (accuracy_score, confusion_matrix,
                             precision_score, recall_score, f1_score)

import analyses.section7 as s7
import analyses.section8 as s8


# Évaluation du modèle sur le jeu de TEST (jamais vu pendant l'entraînement) :
# c'est ça qui mesure la vraie capacité à généraliser. On lit le split (s7) et le
# modèle (s8) via leur module pour suivre les ré-entraînements de la section 7.
_y_pred = s8.modele_logit.predict(s7.X_test)

# La classe positive est 1 (= sinistre), c'est elle qui nous intéresse.
ACCURACY  = float(accuracy_score(s7.y_test, _y_pred))
PRECISION = float(precision_score(s7.y_test, _y_pred))
RECALL    = float(recall_score(s7.y_test, _y_pred))
F1        = float(f1_score(s7.y_test, _y_pred))
_MATRICE  = confusion_matrix(s7.y_test, _y_pred)


def reentrainer():
    """
    Réévalue le modèle COURANT (s8.modele_logit, déjà ré-entraîné) sur le jeu de
    test courant et met à jour les métriques + la matrice de confusion. À appeler
    APRÈS s8.reentrainer().
    """
    global ACCURACY, PRECISION, RECALL, F1, _MATRICE
    y_pred    = s8.modele_logit.predict(s7.X_test)
    ACCURACY  = float(accuracy_score(s7.y_test, y_pred))
    PRECISION = float(precision_score(s7.y_test, y_pred))
    RECALL    = float(recall_score(s7.y_test, y_pred))
    F1        = float(f1_score(s7.y_test, y_pred))
    _MATRICE  = confusion_matrix(s7.y_test, y_pred)


# ── Fonctions ouvertes par les boutons ────────────────────────────────────────

def show_matrice_confusion():
    """
    Matrice de confusion (heatmap). Lignes = réalité, colonnes = prédiction.
    Diagonale = bonnes prédictions ; hors diagonale = erreurs (FP en haut à
    droite, FN en bas à gauche).
    """
    fig, ax = plt.subplots(figsize=(6, 5))
    fig.suptitle("Matrice de confusion (jeu de test)", fontsize=11)

    im = ax.imshow(_MATRICE, cmap='Blues')
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    labels = ["0\npas de sinistre", "1\nsinistre"]
    ax.set_xticks([0, 1]); ax.set_xticklabels(labels, fontsize=9)
    ax.set_yticks([0, 1]); ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("Prédiction")
    ax.set_ylabel("Réalité")

    # Annotation des 4 cases (texte blanc sur fond foncé pour rester lisible)
    vmax = _MATRICE.max()
    for i in range(2):
        for j in range(2):
            couleur = 'white' if _MATRICE[i, j] > vmax / 2 else 'black'
            ax.text(j, i, str(_MATRICE[i, j]), ha='center', va='center',
                    fontsize=15, color=couleur)

    plt.tight_layout()
    plt.show()


def show_metriques():
    """Les 4 métriques d'évaluation en barres (toutes entre 0 et 1)."""
    noms     = ['Accuracy', 'Précision', 'Rappel', 'F1-score']
    valeurs  = [ACCURACY, PRECISION, RECALL, F1]
    couleurs = ['#4A8C4A', '#4A7FA5', '#C07835', '#7A5A9A']

    fig, ax = plt.subplots(figsize=(8, 5))
    fig.suptitle("Métriques d'évaluation (jeu de test)", fontsize=11)

    bars = ax.bar(noms, valeurs, color=couleurs, edgecolor='#333333')
    ax.set_ylim(0, 1)
    ax.set_ylabel("Score")
    for bar, v in zip(bars, valeurs):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.02,
                f"{v:.3f}", ha='center', fontsize=10)

    plt.tight_layout()
    plt.show()


# ── Infos pour les cartes en bas de l'onglet ──────────────────────────────────

def get_info_section9():
    return [
        (f"{ACCURACY:.3f}",  "accuracy",  "#4A8C4A"),
        (f"{PRECISION:.3f}", "précision", "#4A7FA5"),
        (f"{RECALL:.3f}",    "rappel",    "#C07835"),
        (f"{F1:.3f}",        "f1-score",  "#7A5A9A"),
    ]
