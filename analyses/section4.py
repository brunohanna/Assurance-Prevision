import matplotlib.pyplot as plt
from analyses.data import df


# ── Calculs faits une fois à l'import ────────────────────────────────────────

def _compter_aberrants_par_col():
    """IQR : valeurs en dehors de [Q1 - 1.5*IQR, Q3 + 1.5*IQR]."""
    cols = [c for c in df.select_dtypes(include=['number']).columns
            if c not in ('id', 'outcome')]
    result = {}
    for col in cols:
        serie = df[col].dropna()
        Q1, Q3 = serie.quantile(0.25), serie.quantile(0.75)
        IQR = Q3 - Q1
        n = int(((df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)).sum())
        if n > 0:
            result[col] = n
    return result


_na_par_col     = df.isna().sum()
_ab_par_col     = _compter_aberrants_par_col()

NA_COUNT = int(_na_par_col.sum())
AB_COUNT = sum(_ab_par_col.values())


# ── Helpers internes ──────────────────────────────────────────────────────────

def _tableau_matplotlib(titre, entetes, lignes, ligne_total):
    """Affiche un tableau propre dans une figure matplotlib."""
    toutes_lignes = lignes + [ligne_total]
    h = max(3.0, len(toutes_lignes) * 0.55 + 1.5)

    fig, ax = plt.subplots(figsize=(9, h))
    ax.axis('off')
    fig.suptitle(titre, fontsize=11, y=0.98)

    table = ax.table(
        cellText=toutes_lignes,
        colLabels=entetes,
        loc='center',
        cellLoc='center'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.2, 1.7)

    idx_total = len(lignes)  # la ligne total dans le tableau (après header = row 0)

    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor('#CCCCCC')
        if row == 0:
            cell.set_facecolor('#2E2E2E')
            cell.set_text_props(color='white', fontweight='bold')
        elif row == idx_total + 1:   # ligne totale (dernière)
            cell.set_facecolor('#DDDDDD')
            cell.set_text_props(fontweight='bold')
        elif row % 2 == 0:
            cell.set_facecolor('#F5F5F5')
        else:
            cell.set_facecolor('#FFFFFF')

    plt.tight_layout()


# ── Fonctions ouvertes par les boutons ────────────────────────────────────────

def show_histogrammes():
    """Distribution de chaque variable numérique, colorée par outcome."""
    COUNT_COLS_LIMITS = {
        'children': 5, 'speeding_violations': 16,
        'duis': 5, 'past_accidents': 12,
    }

    cols = [c for c in df.select_dtypes(include=['number']).columns
            if c not in ('outcome', 'id')]

    n_cols = 3
    n_rows = (len(cols) + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(14, 3 * n_rows))
    fig.suptitle(
        "Distribution des variables numériques\nVert = pas de sinistre  |  Rouge = sinistre",
        fontsize=11
    )
    axes = axes.flatten()

    for i, col in enumerate(cols):
        d0 = df[df['outcome'] == 0][col].dropna()
        d1 = df[df['outcome'] == 1][col].dropna()

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

    plt.tight_layout()
    plt.show()


def show_types_donnees():
    """Tableau des types de chaque colonne."""
    types = df.dtypes.reset_index()
    types.columns = ['Variable', 'Type']
    types['Catégorie'] = types['Type'].apply(
        lambda t: 'Numérique' if str(t) in ('int64', 'float64') else 'Qualitatif'
    )

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.axis('off')
    fig.suptitle("Types des variables", fontsize=12, y=0.97)

    table = ax.table(
        cellText=types.values,
        colLabels=types.columns,
        loc='center', cellLoc='left'
    )
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


def show_donnees_manquantes():
    """Vue d'ensemble : NA + aberrants côte à côte."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    fig.suptitle("Qualité des données — Vue d'ensemble", fontsize=11)

    # NA
    na = _na_par_col[_na_par_col > 0]
    if na.empty:
        ax1.text(0.5, 0.5, "Aucun NA ✓", ha='center', va='center',
                 fontsize=12, color='#2E9E4F')
        ax1.axis('off')
    else:
        bars1 = ax1.barh(na.index, na.values, color='#888888', edgecolor='#333333')
        ax1.set_title("Valeurs manquantes (NA)")
        ax1.set_xlabel("Nombre de NA")
        for bar, val in zip(bars1, na.values):
            ax1.text(bar.get_width() + na.values.max() * 0.01, bar.get_y() + bar.get_height() / 2,
                     str(val), va='center', fontsize=9)

    # Aberrants
    if not _ab_par_col:
        ax2.text(0.5, 0.5, "Aucun aberrant ✓", ha='center', va='center',
                 fontsize=12, color='#2E9E4F')
        ax2.axis('off')
    else:
        ab = list(_ab_par_col.items())
        cols_ab, vals_ab = zip(*ab)
        bars2 = ax2.barh(cols_ab, vals_ab, color='#AAAAAA', edgecolor='#333333')
        ax2.set_title("Valeurs aberrantes (IQR)")
        ax2.set_xlabel("Nombre d'aberrants")
        max_ab = max(vals_ab)
        for bar, val in zip(bars2, vals_ab):
            ax2.text(bar.get_width() + max_ab * 0.01, bar.get_y() + bar.get_height() / 2,
                     str(val), va='center', fontsize=9)

    plt.tight_layout()
    plt.show()


def show_na():
    """Tableau détaillé des valeurs NA : colonne, count, cumulatif, %."""
    na = _na_par_col[_na_par_col > 0].sort_values(ascending=False)

    if na.empty:
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.text(0.5, 0.5, "Aucune valeur NA dans le dataset ✓",
                ha='center', va='center', fontsize=13, color='#2E9E4F')
        ax.axis('off')
        plt.tight_layout()
        plt.show()
        return

    n_lignes = len(df)
    lignes = []
    cumul = 0
    for col, count in na.items():
        cumul += count
        pct_col = f"{count / n_lignes * 100:.2f}%"
        lignes.append([col, count, cumul, pct_col])

    total = na.sum()
    ligne_total = ["TOTAL", total, total,
                   f"{total / (n_lignes * len(df.columns)) * 100:.2f}% du dataset"]

    _tableau_matplotlib(
        "Valeurs manquantes (NA) — Détail par colonne",
        ["Colonne", "Nb NA", "Cumulatif", "% de la colonne"],
        lignes, ligne_total
    )
    plt.show()


def show_aberantes():
    """Box plots + tableau des valeurs aberrantes par colonne."""
    cols = [c for c in df.select_dtypes(include=['number']).columns
            if c not in ('id', 'outcome')]

    n_cols = 3
    n_rows = (len(cols) + n_cols - 1) // n_cols

    # ── Figure 1 : box plots ─────────────────────────────────────────────────
    fig1, axes = plt.subplots(n_rows, n_cols, figsize=(14, 3 * n_rows))
    fig1.suptitle("Détection des valeurs aberrantes — Box plots", fontsize=11)
    axes = axes.flatten()

    for i, col in enumerate(cols):
        axes[i].boxplot(
            df[col].dropna(),
            patch_artist=True,
            boxprops=dict(facecolor='#DDDDDD', color='#333333'),
            medianprops=dict(color='black', linewidth=2),
            flierprops=dict(marker='o', color='#888888', markersize=4)
        )
        axes[i].set_title(col, fontsize=9)
        axes[i].set_xticks([])

    for j in range(len(cols), len(axes)):
        axes[j].set_visible(False)

    fig1.tight_layout()

    # ── Figure 2 : tableau ───────────────────────────────────────────────────
    if not _ab_par_col:
        fig2, ax2 = plt.subplots(figsize=(5, 3))
        ax2.text(0.5, 0.5, "Aucune valeur aberrante détectée ✓",
                 ha='center', va='center', fontsize=13, color='#2E9E4F')
        ax2.axis('off')
        fig2.tight_layout()
    else:
        ab_sorted = sorted(_ab_par_col.items(), key=lambda x: x[1], reverse=True)
        lignes = []
        cumul = 0
        n_lignes = len(df)
        for col, count in ab_sorted:
            cumul += count
            pct = f"{count / n_lignes * 100:.2f}%"
            lignes.append([col, count, cumul, pct])

        total = sum(_ab_par_col.values())
        ligne_total = ["TOTAL", total, total, "—"]

        _tableau_matplotlib(
            "Valeurs aberrantes (méthode IQR) — Détail par colonne",
            ["Colonne", "Nb aberrants", "Cumulatif", "% des lignes"],
            lignes, ligne_total
        )

    plt.show()


def get_info_dataset():
    """Infos pour les cartes de stats en bas de l'interface."""
    couleurs_dtype = {
        'int64':   '#4A7FA5',
        'float64': '#5A9A6E',
        'object':  '#C07835',
        'bool':    '#8A5FB0',
    }
    cartes_dtype = []
    for dtype, count in df.dtypes.value_counts().items():
        couleur = couleurs_dtype.get(str(dtype), '#777777')
        cartes_dtype.append((count, str(dtype), couleur))

    return df.shape[0], cartes_dtype
