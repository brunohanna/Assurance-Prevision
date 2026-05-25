import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold, cross_val_score

import analyses.section7 as s7
import analyses.section9 as s9
from analyses.section7 import RANDOM_SEED


# Validation croisée 5 plis sur le jeu d'apprentissage.
# Le principe : on découpe en 5, on entraîne sur 4 morceaux et on teste sur le
# 5e, et on tourne. Ça donne 5 scores -> moyenne plus fiable qu'une seule découpe.
N_PLIS = 5
_kf = KFold(n_splits=N_PLIS, shuffle=True, random_state=RANDOM_SEED)
_modele = LogisticRegression(max_iter=1000, random_state=RANDOM_SEED)

SCORES     = cross_val_score(_modele, s7.X_train, s7.y_train, cv=_kf, scoring='accuracy')
CV_MOYENNE = float(SCORES.mean())
CV_ECART   = float(SCORES.std())


def reentrainer():
    """
    Recalcule la validation croisée sur le jeu d'apprentissage COURANT (s7.X_train,
    mis à jour pour la proportion choisie en §7) et met à jour SCORES/CV_MOYENNE/
    CV_ECART. cross_val_score clone le modèle à chaque appel, donc réutiliser
    _modele est sans effet de bord.
    """
    global SCORES, CV_MOYENNE, CV_ECART
    SCORES     = cross_val_score(_modele, s7.X_train, s7.y_train, cv=_kf, scoring='accuracy')
    CV_MOYENNE = float(SCORES.mean())
    CV_ECART   = float(SCORES.std())


# ── Fonctions ouvertes par les boutons ────────────────────────────────────────

def show_scores_cv():
    """
    Accuracy de chaque pli, la moyenne de la validation croisée, et le score
    obtenu par l'évaluation simple de la section 9 (pour comparer).
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.suptitle(f"Validation croisée {N_PLIS} plis — accuracy par pli", fontsize=11)

    x    = np.arange(1, len(SCORES) + 1)
    bars = ax.bar(x, SCORES, color='#4A7FA5', edgecolor='#333333')

    ax.axhline(CV_MOYENNE, color='#C0392B', linestyle='--',
               label=f"Moyenne CV = {CV_MOYENNE:.3f}")
    ax.axhline(s9.ACCURACY, color='#4A8C4A', linestyle=':',
               label=f"Éval simple (section 9) = {s9.ACCURACY:.3f}")

    ax.set_xticks(x)
    ax.set_xticklabels([f"Pli {i}" for i in x])
    ax.set_ylim(0, 1)
    ax.set_ylabel("Accuracy")
    ax.legend(fontsize=8)

    for bar, v in zip(bars, SCORES):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.02,
                f"{v:.3f}", ha='center', fontsize=8)

    plt.tight_layout()
    plt.show()


# ── Infos pour les cartes en bas de l'onglet ──────────────────────────────────

def get_info_section10():
    return [
        (str(N_PLIS),         "plis (KFold)", "#444444"),
        (f"{CV_MOYENNE:.3f}", "moyenne CV",   "#4A7FA5"),
        (f"±{CV_ECART:.3f}",  "écart-type",   "#C07835"),
    ]
