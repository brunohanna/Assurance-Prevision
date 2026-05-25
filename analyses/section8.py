import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LogisticRegression

import analyses.section7 as s7
from analyses.section7 import NOMS_FEATURES, RANDOM_SEED


# Entraînement du modèle de régression logistique sur le jeu d'apprentissage.
# max_iter=1000 : marge confortable pour la convergence du solveur L-BFGS.
# On lit le split via s7.X_train (et pas une copie) pour que reentrainer() suive
# bien la proportion choisie dans la section 7.
modele_logit = LogisticRegression(max_iter=1000, random_state=RANDOM_SEED)
modele_logit.fit(s7.X_train, s7.y_train)


# Petit récapitulatif théorique (réponses aux 3 questions du PDF §8) :
#
# 1) Hypothèse du logit :
#    log( p(y=1|x) / p(y=0|x) ) = w·x + b
#    Autrement dit, le log-rapport des probabilités est linéaire en x.
#
# 2) Minimisation de la fonction de coût :
#    On minimise la log-vraisemblance négative. Pas de solution analytique,
#    donc méthode itérative (descente de gradient, Newton, L-BFGS par défaut
#    dans scikit-learn).
#
# 3) Paramètres appris :
#    Les poids w (un par variable d'entrée) et le biais b.

POIDS = modele_logit.coef_[0]           # un poids par feature
BIAIS = float(modele_logit.intercept_[0])
SCORE_TRAIN = float(modele_logit.score(s7.X_train, s7.y_train))


def reentrainer():
    """
    Ré-entraîne le modèle logit sur le split COURANT de la section 7 et met à jour
    l'état du module (modele_logit, POIDS, BIAIS, SCORE_TRAIN). Appelé par le
    bouton de la §7 après s7.reentrainer(). Les sections 9 (évaluation) et 10
    (validation croisée) repartent ensuite de ce modèle à jour.
    """
    global modele_logit, POIDS, BIAIS, SCORE_TRAIN
    modele_logit = LogisticRegression(max_iter=1000, random_state=RANDOM_SEED)
    modele_logit.fit(s7.X_train, s7.y_train)
    POIDS = modele_logit.coef_[0]
    BIAIS = float(modele_logit.intercept_[0])
    SCORE_TRAIN = float(modele_logit.score(s7.X_train, s7.y_train))


# ── Fonctions ouvertes par les boutons ────────────────────────────────────────

def show_coefficients():
    """
    Affiche les poids appris par le modèle COURANT, triés par |valeur|.
    Lecture : barre à droite = pousse vers outcome=1 ; à gauche = vers outcome=0.
    La magnitude indique l'importance de la variable dans la décision.
    Reflète toujours la dernière proportion choisie en section 7.
    """
    # Proportion train/test courante, reconstruite depuis les tailles du split.
    n_tr, n_te = len(s7.X_train), len(s7.X_test)
    pct_test   = round(100 * n_te / (n_tr + n_te))
    info_split = f"split {100 - pct_test}/{pct_test}"

    # Tri par importance (valeur absolue)
    ordre   = np.argsort(np.abs(POIDS))
    noms    = [NOMS_FEATURES[i] for i in ordre]
    valeurs = POIDS[ordre]

    couleurs = ['#C0392B' if v > 0 else '#2C5F8D' for v in valeurs]

    fig, ax = plt.subplots(figsize=(9, 6))
    fig.suptitle("Régression logistique — Coefficients appris", fontsize=11)

    y_pos = np.arange(len(noms))
    bars  = ax.barh(y_pos, valeurs, color=couleurs, edgecolor='#333333')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(noms, fontsize=9)
    ax.axvline(0, color='black', linewidth=0.8)
    ax.set_xlabel("Poids w")
    ax.set_title(f"Biais b = {BIAIS:+.3f}   |   "
                 f"Accuracy sur train = {SCORE_TRAIN:.3f}   |   {info_split}",
                 fontsize=9)

    vmax   = np.abs(valeurs).max()
    offset = vmax * 0.02
    for bar, val in zip(bars, valeurs):
        align = 'left' if val >= 0 else 'right'
        ax.text(val + (offset if val >= 0 else -offset),
                bar.get_y() + bar.get_height() / 2,
                f"{val:+.3f}", va='center', ha=align, fontsize=8)

    plt.tight_layout()
    plt.show()


# ── Infos pour les cartes en bas de l'onglet ──────────────────────────────────

def get_info_section8():
    idx_max = int(np.argmax(np.abs(POIDS)))
    return [
        (len(NOMS_FEATURES),         "coefficients",   "#4A7FA5"),
        (NOMS_FEATURES[idx_max],     "+ influente",    "#C0392B"),
        (f"{BIAIS:+.2f}",            "biais b",         "#444444"),
        (f"{SCORE_TRAIN:.3f}",       "acc. train",      "#4A8C4A"),
    ]
