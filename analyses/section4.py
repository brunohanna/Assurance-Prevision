import matplotlib.pyplot as plt
import pandas as pd
from analyses.data import df, ORDRE_ENCODAGE


# ── Encodage des variables texte ──────────────────────────────────────────────

def _encoder_qualitatives(data):
    """
    Convertit les colonnes texte en entiers selon l'ordre logique (ORDRE_ENCODAGE),
    le même mapping que la préparation (section 5). Sans ça, la section 4 laisserait
    de côté ces 5 variables car ses graphes ne prennent que les colonnes numériques.
    On examine ainsi TOUTES les variables. No-op sur une colonne déjà numérique
    (donc sans effet sur le dataset préparé).
    """
    data = data.copy()
    for col, ordre in ORDRE_ENCODAGE.items():
        if col in data.columns and not pd.api.types.is_numeric_dtype(data[col]):
            data[col] = data[col].map({categorie: code for code, categorie in enumerate(ordre)})
    return data


# Dataset de travail de la section 4 : les 5 colonnes texte sont converties en int
# pour qu'elles soient examinées comme les autres variables.
df_num = _encoder_qualitatives(df)


# ── Calculs (référence pour section5) ─────────────────────────────────────────

def _compter_aberrants_par_col(data=None):
    """IQR : valeurs en dehors de [Q1 - 1.5*IQR, Q3 + 1.5*IQR]."""
    if data is None:
        data = df_num
    cols = [c for c in data.select_dtypes(include=['number']).columns
            if c not in ('id', 'outcome')]
    result = {}
    for col in cols:
        serie = data[col].dropna()
        Q1, Q3 = serie.quantile(0.25), serie.quantile(0.75)
        IQR = Q3 - Q1
        n = int(((data[col] < Q1 - 1.5 * IQR) | (data[col] > Q3 + 1.5 * IQR)).sum())
        if n > 0:
            result[col] = n
    return result


_na_par_col = df.isna().sum()
_ab_par_col = _compter_aberrants_par_col()

NA_COUNT = int(_na_par_col.sum())
AB_COUNT = sum(_ab_par_col.values())


# ── Compteurs dynamiques (utilisés quand on change de dataset) ────────────────

def get_na_count(data=None):
    if data is None:
        return NA_COUNT
    return int(data.isna().sum().sum())


def get_ab_count(data=None):
    if data is None:
        return AB_COUNT
    return sum(_compter_aberrants_par_col(data).values())


# ── Helper tableau matplotlib ─────────────────────────────────────────────────

def _tableau_matplotlib(titre, entetes, lignes, ligne_total):
    toutes_lignes = lignes + [ligne_total]
    h = max(3.0, len(toutes_lignes) * 0.55 + 1.5)

    fig, ax = plt.subplots(figsize=(9, h))
    ax.axis('off')
    fig.suptitle(titre, fontsize=11, y=0.98)

    table = ax.table(cellText=toutes_lignes, colLabels=entetes,
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
        elif row == idx_total + 1:
            cell.set_facecolor('#DDDDDD')
            cell.set_text_props(fontweight='bold')
        elif row % 2 == 0:
            cell.set_facecolor('#F5F5F5')
        else:
            cell.set_facecolor('#FFFFFF')

    plt.tight_layout()


# ── Fonctions ouvertes par les boutons ────────────────────────────────────────

def show_histogrammes(data=None):
    """Distribution de chaque variable (texte converti en int), colorée par outcome."""
    if data is None:
        data = df
    data = _encoder_qualitatives(data)

    COUNT_COLS_LIMITS = {
        'children': 5, 'speeding_violations': 16,
        'duis': 5, 'past_accidents': 12,
    }

    cols = [c for c in data.select_dtypes(include=['number']).columns
            if c not in ('outcome', 'id')]

    n_cols = 3
    n_rows = (len(cols) + n_cols - 1) // n_cols

    # constrained_layout gère l'espacement entre les sous-graphes et réserve la
    # place du suptitre : sans ça les titres se chevauchaient avec le graphe du dessus.
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(14, 3.2 * n_rows),
                             constrained_layout=True)
    fig.suptitle(
        "Distribution des variables\nVert = pas de sinistre  |  Rouge = sinistre",
        fontsize=11
    )
    axes = axes.flatten()

    for i, col in enumerate(cols):
        d0 = data[data['outcome'] == 0][col].dropna()
        d1 = data[data['outcome'] == 1][col].dropna()

        if col in COUNT_COLS_LIMITS:
            m = COUNT_COLS_LIMITS[col]
            d0, d1 = d0.clip(upper=m), d1.clip(upper=m)
            bins = range(0, m + 2)
        else:
            bins = 20

        axes[i].hist([d0, d1], bins=bins, stacked=True,
                     color=['#4CAF50', '#F44336'],
                     label=['Pas de sinistre', 'Sinistre'])
        axes[i].set_title(col)
        axes[i].legend(fontsize=7)

    for j in range(len(cols), len(axes)):
        axes[j].set_visible(False)

    plt.show()


def show_types_donnees(data=None):
    """
    Tableau des types de chaque colonne, avec l'encodage str -> int appliqué aux
    variables qualitatives (rappel du mapping de la section 5).
    """
    if data is None:
        data = df

    types = data.dtypes.reset_index()
    types.columns = ['Variable', 'Type']
    types['Catégorie'] = types['Type'].apply(
        lambda t: 'Numérique' if str(t) in ('int64', 'float64') else 'Qualitatif'
    )

    # Rappel du mapping pour les colonnes qu'on convertit en entiers.
    def _mapping(col):
        if col not in ORDRE_ENCODAGE:
            return ''
        return ', '.join(f"{v}={i}" for i, v in enumerate(ORDRE_ENCODAGE[col]))
    types['Encodage (str → int)'] = types['Variable'].apply(_mapping)

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.axis('off')
    fig.suptitle("Types des variables", fontsize=12, y=0.97)

    table = ax.table(cellText=types.values, colLabels=types.columns,
                     loc='center', cellLoc='left')
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.3, 1.6)

    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor('#CCCCCC')
        if row == 0:
            cell.set_facecolor('#2E2E2E')
            cell.set_text_props(color='white', fontweight='bold')
        elif types.iloc[row - 1]['Catégorie'] == 'Numérique':
            cell.set_facecolor('#F0F0F0')
        else:
            cell.set_facecolor('#FFFFFF')

    plt.tight_layout()
    plt.show()


def show_donnees_manquantes(data=None):
    """Vue d'ensemble : NA + aberrants côte à côte."""
    if data is None:
        data = df
    data = _encoder_qualitatives(data)

    na     = data.isna().sum()
    na     = na[na > 0]
    ab_col = _compter_aberrants_par_col(data)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    fig.suptitle("Qualité des données — Vue d'ensemble", fontsize=11)

    if na.empty:
        ax1.text(0.5, 0.5, "Aucun NA ✓", ha='center', va='center',
                 fontsize=12, color='#2E9E4F')
        ax1.axis('off')
    else:
        bars1 = ax1.barh(na.index, na.values, color='#888888', edgecolor='#333333')
        ax1.set_title("Valeurs manquantes (NA)")
        ax1.set_xlabel("Nombre de NA")
        for bar, val in zip(bars1, na.values):
            ax1.text(bar.get_width() + na.values.max() * 0.01,
                     bar.get_y() + bar.get_height() / 2,
                     str(val), va='center', fontsize=9)

    if not ab_col:
        ax2.text(0.5, 0.5, "Aucun aberrant ✓", ha='center', va='center',
                 fontsize=12, color='#2E9E4F')
        ax2.axis('off')
    else:
        cols_ab, vals_ab = zip(*ab_col.items())
        bars2 = ax2.barh(cols_ab, vals_ab, color='#AAAAAA', edgecolor='#333333')
        ax2.set_title("Valeurs aberrantes (IQR)")
        ax2.set_xlabel("Nombre d'aberrants")
        for bar, val in zip(bars2, vals_ab):
            ax2.text(bar.get_width() + max(vals_ab) * 0.01,
                     bar.get_y() + bar.get_height() / 2,
                     str(val), va='center', fontsize=9)

    plt.tight_layout()
    plt.show()


def show_na(data=None):
    """Tableau détaillé des valeurs NA : colonne, count, cumulatif, %."""
    if data is None:
        data = df

    na = data.isna().sum()
    na = na[na > 0].sort_values(ascending=False)

    if na.empty:
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.text(0.5, 0.5, "Aucune valeur NA dans le dataset ✓",
                ha='center', va='center', fontsize=13, color='#2E9E4F')
        ax.axis('off')
        plt.tight_layout()
        plt.show()
        return

    n_lignes = len(data)
    lignes, cumul = [], 0
    for col, count in na.items():
        cumul += count
        lignes.append([col, count, cumul, f"{count / n_lignes * 100:.2f}%"])

    total = na.sum()
    ligne_total = ["TOTAL", total, total,
                   f"{total / (n_lignes * len(data.columns)) * 100:.2f}% du dataset"]

    _tableau_matplotlib("Valeurs manquantes (NA) — Détail par colonne",
                        ["Colonne", "Nb NA", "Cumulatif", "% de la colonne"],
                        lignes, ligne_total)
    plt.show()


def show_aberantes(data=None):
    """Box plots + tableau des valeurs aberrantes par colonne."""
    if data is None:
        data = df
    data = _encoder_qualitatives(data)

    cols   = [c for c in data.select_dtypes(include=['number']).columns
              if c not in ('id', 'outcome')]
    ab_col = _compter_aberrants_par_col(data)

    n_cols = 3
    n_rows = (len(cols) + n_cols - 1) // n_cols

    fig1, axes = plt.subplots(n_rows, n_cols, figsize=(14, 3 * n_rows))
    fig1.suptitle("Détection des valeurs aberrantes — Box plots", fontsize=11)
    axes = axes.flatten()

    for i, col in enumerate(cols):
        axes[i].boxplot(data[col].dropna(), patch_artist=True,
                        boxprops=dict(facecolor='#DDDDDD', color='#333333'),
                        medianprops=dict(color='black', linewidth=2),
                        flierprops=dict(marker='o', color='#888888', markersize=4))
        axes[i].set_title(col, fontsize=9)
        axes[i].set_xticks([])

    for j in range(len(cols), len(axes)):
        axes[j].set_visible(False)
    fig1.tight_layout()

    if not ab_col:
        fig2, ax2 = plt.subplots(figsize=(5, 3))
        ax2.text(0.5, 0.5, "Aucune valeur aberrante détectée ✓",
                 ha='center', va='center', fontsize=13, color='#2E9E4F')
        ax2.axis('off')
        fig2.tight_layout()
    else:
        ab_sorted = sorted(ab_col.items(), key=lambda x: x[1], reverse=True)
        lignes, cumul = [], 0
        for col, count in ab_sorted:
            cumul += count
            lignes.append([col, count, cumul, f"{count / len(data) * 100:.2f}%"])
        _tableau_matplotlib("Valeurs aberrantes (IQR) — Détail par colonne",
                            ["Colonne", "Nb aberrants", "Cumulatif", "% des lignes"],
                            lignes, ["TOTAL", sum(ab_col.values()), sum(ab_col.values()), "—"])

    plt.show()


def get_info_dataset(data=None):
    """Infos pour les cartes de stats en bas de l'interface."""
    if data is None:
        data = df

    couleurs_dtype = {
        'int64': '#4A7FA5', 'float64': '#5A9A6E',
        'object': '#C07835', 'bool': '#8A5FB0',
    }
    cartes_dtype = []
    for dtype, count in data.dtypes.value_counts().items():
        couleur = couleurs_dtype.get(str(dtype), '#777777')
        cartes_dtype.append((count, str(dtype), couleur))

    return data.shape[0], cartes_dtype
