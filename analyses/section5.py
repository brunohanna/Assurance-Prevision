import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler

from analyses.data import df, BASE_DIR, ORDRE_ENCODAGE
from analyses.section4 import _na_par_col, _ab_par_col

PREPARED_PATH = os.path.join(BASE_DIR, 'src', 'car_insurance_prepared.csv')


# ── Préparation complète des données (calculée une fois à l'import) ───────────

def _preparer_donnees():
    """
    Applique toutes les étapes de préparation sur une copie du dataset.
    On garde l'original intact pour pouvoir comparer avant/après.
    """
    data = df.copy()

    # 1. Suppression de la colonne id (identifiant, inutile pour la classification)
    data = data.drop(columns=['id'])

    # 2. Traitement des valeurs manquantes
    #    - Variables numériques  → remplacement par la médiane
    #    - Variables qualitatives → remplacement par la valeur la plus fréquente (mode)
    na_info = {}
    for col in data.columns:
        n_na = int(data[col].isna().sum())
        if n_na > 0:
            if data[col].dtype in ['int64', 'float64']:
                valeur  = data[col].median()
                methode = f"médiane ({valeur:.2f})"
            else:
                valeur  = data[col].mode()[0]
                methode = f"mode ('{valeur}')"
            data[col] = data[col].fillna(valeur)
            na_info[col] = (n_na, methode)

    # 3. Traitement des aberrants — la méthode dépend de la nature de la colonne.
    #    Toutes sont numériques mais pas de même type : certaines sont des
    #    catégories codées (gender, age...), d'autres des comptages (nombre
    #    d'infractions...), d'autres vraiment continues (credit_score).
    #    Appliquer l'IQR partout écrase les colonnes "gonflées de zéros" : duis
    #    a 81% de 0, donc Q1 = Q3 = 0 et tout serait ramené à 0. On adapte donc.
    cols_num = [c for c in data.select_dtypes(include=['number']).columns
                if c != 'outcome']
    ab_info = {}
    for col in cols_num:
        serie      = data[col]
        n_distinct = serie.nunique()
        est_entier = bool((serie.dropna() % 1 == 0).all())

        # a) Catégorie / ordinal codé : peu de modalités entières. Chaque valeur a
        #    un sens (0/1, tranche d'âge...), on n'y touche pas.
        if est_entier and n_distinct <= 10:
            continue

        # b) Comptage discret étalé (entier) : on rabote seulement les vraies queues
        #    aux percentiles 1%/99% sans toucher au cœur de la distribution.
        # c) Variable continue : écrêtage IQR classique à 1.5 * IQR.
        if est_entier:
            b_inf, b_sup = serie.quantile(0.01), serie.quantile(0.99)
            methode = 'percentile 1/99'
        else:
            Q1, Q3 = serie.quantile(0.25), serie.quantile(0.75)
            IQR = Q3 - Q1
            b_inf, b_sup = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
            methode = 'IQR 1.5x'

        # Garde-fou anti-effondrement : si les deux bornes se rejoignent, écrêter
        # transformerait la colonne en constante -> on saute.
        if b_inf >= b_sup:
            continue

        n_ab = int(((serie < b_inf) | (serie > b_sup)).sum())
        if n_ab > 0:
            data[col]    = serie.clip(lower=b_inf, upper=b_sup)
            ab_info[col] = (n_ab, round(b_inf, 2), round(b_sup, 2), methode)

    # 4. Encodage des variables qualitatives selon l'ordre logique (ORDRE_ENCODAGE).
    #    On mappe chaque catégorie vers son indice dans la liste : l'ordre ordinal
    #    est ainsi respecté, contrairement au LabelEncoder alphabétique.
    cols_quali = data.select_dtypes(include=['object']).columns.tolist()
    for col in cols_quali:
        # Colonne non prévue : on retombe sur un ordre alphabétique par défaut.
        ordre   = ORDRE_ENCODAGE.get(col, sorted(data[col].dropna().unique()))
        mapping = {categorie: code for code, categorie in enumerate(ordre)}
        data[col] = data[col].map(mapping)

    # 5. Normalisation StandardScaler sur toutes les variables (sauf outcome)
    cols_scale = [c for c in data.select_dtypes(include=['number']).columns
                  if c != 'outcome']
    scaler = StandardScaler()
    data[cols_scale] = scaler.fit_transform(data[cols_scale])

    return data, na_info, ab_info, cols_quali, cols_scale, scaler


def _charger_ou_preparer():
    """
    Prépare les données puis exporte le résultat en CSV.
    On recalcule systématiquement (10 000 lignes, c'est instantané) : ainsi toute
    modification de la préparation est réellement prise en compte, et le CSV reste
    un export fidèle du dataset préparé. On évite ainsi de relire un ancien CSV
    devenu obsolète après un changement de code.
    """
    data, na_info, ab_info, cols_quali, cols_scale, scaler = _preparer_donnees()
    data.to_csv(PREPARED_PATH, index=False)
    return data, na_info, ab_info, cols_quali, cols_scale, scaler


df_prepared, _na_info, _ab_info, _cols_quali, _cols_scale, _scaler = _charger_ou_preparer()

# Constantes exposées pour les boutons stat de l'interface
NB_NA_TRAITES = len(_na_info)
NB_AB_TRAITES = len(_ab_info)
NB_ENCODES    = len(_cols_quali)
NB_SCALES     = len(_cols_scale)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _tableau_matplotlib(titre, entetes, lignes, ligne_total=None):
    """Affiche un tableau propre dans une figure matplotlib."""
    toutes = lignes + ([ligne_total] if ligne_total else [])
    h = max(3.0, len(toutes) * 0.55 + 1.5)

    fig, ax = plt.subplots(figsize=(10, h))
    ax.axis('off')
    fig.suptitle(titre, fontsize=11, y=0.98)

    table = ax.table(cellText=toutes, colLabels=entetes,
                     loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.2, 1.7)

    idx_total = len(lignes)
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor('#CCCCCC')
        if row == 0:
            cell.set_facecolor('#2E2E2E')
            cell.set_text_props(color='white', fontweight='bold')
        elif ligne_total and row == idx_total + 1:
            cell.set_facecolor('#DDDDDD')
            cell.set_text_props(fontweight='bold')
        elif row % 2 == 0:
            cell.set_facecolor('#F5F5F5')
        else:
            cell.set_facecolor('#FFFFFF')

    plt.tight_layout()


# ── Fonctions ouvertes par les boutons ────────────────────────────────────────

def show_traitement_na():
    """
    Avant / après le traitement des NA.
    Gauche : comptage avant  |  Droite : tableau de ce qui a été fait
    """
    na_avant = _na_par_col[_na_par_col > 0]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    fig.suptitle("Traitement des valeurs manquantes", fontsize=11)

    # Avant
    bars = ax1.barh(na_avant.index, na_avant.values,
                    color='#AAAAAA', edgecolor='#333333')
    ax1.set_title("Avant traitement")
    ax1.set_xlabel("Nombre de NA")
    for bar, val in zip(bars, na_avant.values):
        ax1.text(bar.get_width() + na_avant.values.max() * 0.01,
                 bar.get_y() + bar.get_height() / 2,
                 str(val), va='center', fontsize=9)

    # Tableau du traitement appliqué
    ax2.axis('off')
    ax2.set_title("Traitement appliqué")
    lignes = [[col, nb, methode] for col, (nb, methode) in _na_info.items()]
    if lignes:
        table = ax2.table(
            cellText=lignes,
            colLabels=["Colonne", "Nb NA", "Remplacement"],
            loc='center', cellLoc='center'
        )
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.2, 1.7)
        for (row, col), cell in table.get_celld().items():
            cell.set_edgecolor('#CCCCCC')
            cell.set_facecolor('#2E2E2E' if row == 0 else
                               '#F5F5F5' if row % 2 == 0 else '#FFFFFF')
            if row == 0:
                cell.set_text_props(color='white', fontweight='bold')

    plt.tight_layout()
    plt.show()


def show_traitement_aberrants():
    """
    Box plots avant / après écrêtage IQR pour les colonnes concernées.
    """
    cols = list(_ab_info.keys())
    if not cols:
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.text(0.5, 0.5, "Aucun aberrant traité ✓",
                ha='center', va='center', fontsize=13, color='#2E9E4F')
        ax.axis('off')
        plt.tight_layout()
        plt.show()
        return

    n = len(cols)
    fig, axes = plt.subplots(2, n, figsize=(max(10, n * 2.5), 6))
    fig.suptitle("Valeurs aberrantes — Avant / Après écrêtage IQR", fontsize=11)

    # Si une seule colonne, axes n'est pas 2D → on force la forme
    if n == 1:
        axes = axes.reshape(2, 1)

    for i, col in enumerate(cols):
        axes[0, i].boxplot(df[col].dropna(), patch_artist=True,
                           boxprops=dict(facecolor='#DDDDDD', color='#555555'),
                           medianprops=dict(color='black', linewidth=2),
                           flierprops=dict(marker='o', color='#999999', markersize=4))
        axes[0, i].set_title(f"{col}\n({_ab_info[col][3]})", fontsize=9)
        axes[0, i].set_xticks([])

        axes[1, i].boxplot(df_prepared[col].dropna(), patch_artist=True,
                           boxprops=dict(facecolor='#BBDDBB', color='#2E6B2E'),
                           medianprops=dict(color='black', linewidth=2),
                           flierprops=dict(marker='o', color='#999999', markersize=4))
        axes[1, i].set_xticks([])

    axes[0, 0].set_ylabel("Avant", fontsize=9)
    axes[1, 0].set_ylabel("Après", fontsize=9)

    plt.tight_layout()
    plt.show()


def show_encodage():
    """
    Tableau des variables qualitatives encodées :
    colonne, valeurs originales → code numérique, dans l'ordre logique choisi.
    """
    lignes = []
    for col in _cols_quali:
        ordre  = ORDRE_ENCODAGE.get(col, sorted(df[col].dropna().unique()))
        apercu = ', '.join(f"'{v}' → {i}" for i, v in enumerate(ordre))
        lignes.append([col, len(ordre), apercu])

    _tableau_matplotlib(
        "Encodage ordinal des variables qualitatives",
        ["Colonne", "Nb classes", "Mapping (ordre logique)"],
        lignes
    )
    plt.show()


def show_normalisation():
    """
    Histogrammes avant / après StandardScaler pour quelques variables clés.
    """
    # On choisit les variables les plus représentatives
    cols_apercu = _cols_scale[:6]
    n = len(cols_apercu)
    n_cols_grid = 3
    n_rows_grid = (n + n_cols_grid - 1) // n_cols_grid

    fig, axes = plt.subplots(n_rows_grid * 2, n_cols_grid,
                             figsize=(13, n_rows_grid * 4))
    fig.suptitle("Normalisation StandardScaler — Avant / Après", fontsize=11)
    axes = axes.flatten()

    for i, col in enumerate(cols_apercu):
        # Avant (données brutes sans les NA)
        axes[i].hist(df[col].dropna(), bins=25,
                     color='#AAAAAA', edgecolor='#555555')
        axes[i].set_title(f"{col} — avant", fontsize=8)

        # Après (données normalisées)
        axes[i + n_cols_grid * n_rows_grid].hist(df_prepared[col].dropna(), bins=25,
                                                  color='#6699BB', edgecolor='#335577')
        axes[i + n_cols_grid * n_rows_grid].set_title(f"{col} — après", fontsize=8)

    # Cacher les axes vides
    for j in range(n, n_cols_grid * n_rows_grid):
        axes[j].set_visible(False)
        axes[j + n_cols_grid * n_rows_grid].set_visible(False)

    plt.tight_layout()
    plt.show()


def show_donnees_preparees():
    """
    Histogrammes de toutes les variables du dataset préparé.
    Même structure que section 4 pour comparer visuellement.
    """
    cols = [c for c in df_prepared.columns if c != 'outcome']
    n_cols_grid = 3
    n_rows_grid = (len(cols) + n_cols_grid - 1) // n_cols_grid

    fig, axes = plt.subplots(n_rows_grid, n_cols_grid,
                             figsize=(14, 3 * n_rows_grid))
    fig.suptitle("Dataset préparé — Distribution des variables\n"
                 "Vert = pas de sinistre  |  Rouge = sinistre", fontsize=11)
    axes = axes.flatten()

    for i, col in enumerate(cols):
        d0 = df_prepared[df_prepared['outcome'] == 0][col].dropna()
        d1 = df_prepared[df_prepared['outcome'] == 1][col].dropna()
        axes[i].hist([d0, d1], bins=25, stacked=True,
                     color=['#4CAF50', '#F44336'],
                     label=['Pas de sinistre', 'Sinistre'])
        axes[i].set_title(col, fontsize=9)
        axes[i].legend(fontsize=7)

    for j in range(len(cols), len(axes)):
        axes[j].set_visible(False)

    plt.tight_layout()
    plt.show()


def get_info_section5():
    """Infos pour les cartes de stats en bas de l'interface."""
    return [
        (df_prepared.shape[0],            "éléments",         "#4A8C4A"),
        (df_prepared.shape[1] - 1,        "variables",        "#444444"),
        (NB_ENCODES,                       "encodées",         "#4A7FA5"),
        (NB_SCALES,                        "normalisées",      "#7A5A9A"),
    ]
