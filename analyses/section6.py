import matplotlib.pyplot as plt
import numpy as np
from pandas.plotting import scatter_matrix

from analyses.section5 import df_prepared


# On travaille sur le dataset déjà préparé : toutes les colonnes sont numériques,
# pas de NA, donc corr() peut être appelée directement.

CIBLE = 'outcome'

# Corrélations calculées une fois à l'import (pas très lourd : 17 x 17)
_matrice_corr = df_prepared.corr()
_corr_outcome = _matrice_corr[CIBLE].drop(CIBLE).sort_values(key=abs, ascending=False)

# Constantes exposées pour les cartes d'info de l'UI
TOP_VAR        = _corr_outcome.index[0]
TOP_CORR       = round(_corr_outcome.iloc[0], 3)
NB_VARIABLES   = len(_corr_outcome)


# ── Fonctions ouvertes par les boutons ────────────────────────────────────────

def show_heatmap_correlations():
    """
    Heatmap de la matrice de corrélation complète.
    On annote chaque case avec la valeur pour faciliter la lecture.
    """
    cols = _matrice_corr.columns.tolist()
    n    = len(cols)

    fig, ax = plt.subplots(figsize=(10, 9))
    fig.suptitle("Matrice des corrélations (Pearson)", fontsize=11)

    # Palette divergente : bleu = négatif, rouge = positif, blanc = 0
    im = ax.imshow(_matrice_corr.values, cmap='RdBu_r', vmin=-1, vmax=1)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(cols, rotation=45, ha='right', fontsize=8)
    ax.set_yticklabels(cols, fontsize=8)

    # Annotation des valeurs (on cache les valeurs trop petites pour ne pas surcharger)
    for i in range(n):
        for j in range(n):
            v = _matrice_corr.values[i, j]
            if abs(v) >= 0.05:
                couleur = 'white' if abs(v) > 0.5 else 'black'
                ax.text(j, i, f"{v:.2f}", ha='center', va='center',
                        fontsize=7, color=couleur)

    plt.tight_layout()
    plt.show()


def show_correlations_outcome():
    """
    Tableau trié des corrélations de chaque variable avec la cible `outcome`.
    Le signe indique le sens, la magnitude indique la force.
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    fig.suptitle(f"Corrélation de chaque variable avec '{CIBLE}'", fontsize=11)

    valeurs = _corr_outcome.values
    noms    = _corr_outcome.index.tolist()

    # Couleur selon le signe : rouge pour positif, bleu pour négatif
    couleurs = ['#C0392B' if v > 0 else '#2C5F8D' for v in valeurs]

    # On inverse l'ordre pour que la plus forte soit en haut
    y_pos = np.arange(len(noms))[::-1]
    bars  = ax.barh(y_pos, valeurs, color=couleurs, edgecolor='#333333')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(noms, fontsize=9)
    ax.axvline(0, color='black', linewidth=0.8)
    ax.set_xlabel("Coefficient de corrélation")
    ax.set_xlim(-1, 1)

    # Étiquettes de valeur au bout de chaque barre
    for bar, val in zip(bars, valeurs):
        offset = 0.02 if val >= 0 else -0.02
        align  = 'left' if val >= 0 else 'right'
        ax.text(val + offset, bar.get_y() + bar.get_height() / 2,
                f"{val:+.3f}", va='center', ha=align, fontsize=8)

    plt.tight_layout()
    plt.show()


def show_scatter_matrix():
    """
    Scatter matrix sur les 5 variables les plus corrélées à `outcome`.
    Les points sont colorés selon la classe pour voir si les nuages se séparent.
    """
    # Top 5 variables les plus prédictives + la cible pour la coloration
    top_cols = _corr_outcome.index[:5].tolist()
    sous_df  = df_prepared[top_cols + [CIBLE]]

    # Coloration par classe
    couleurs = sous_df[CIBLE].map({0: '#4CAF50', 1: '#F44336'})

    axes = scatter_matrix(
        sous_df[top_cols],
        figsize=(11, 11),
        diagonal='hist',
        color=couleurs,
        alpha=0.4,
        s=8,
        hist_kwds={'bins': 20, 'color': '#888888', 'edgecolor': '#333333'},
    )

    plt.suptitle("Scatter matrix — 5 variables les plus corrélées à outcome\n"
                 "Vert = pas de sinistre  |  Rouge = sinistre",
                 fontsize=11, y=0.995)

    # Lisibilité des labels
    for ax in axes.flatten():
        ax.xaxis.label.set_size(8)
        ax.yaxis.label.set_size(8)
        ax.tick_params(labelsize=7)

    plt.show()


# ── Infos pour les cartes en bas de l'onglet ──────────────────────────────────

def get_info_section6():
    return [
        (NB_VARIABLES,        "variables",         "#444444"),
        (TOP_VAR,             "+ corrélée",        "#4A7FA5"),
        (f"{TOP_CORR:+.2f}",  f"corr. avec {CIBLE}", "#C0392B" if TOP_CORR > 0 else "#2C5F8D"),
    ]
