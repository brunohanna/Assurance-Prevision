import tkinter as tk
from tkinter import ttk

import analyses.section4 as s4
import analyses.section5 as s5
import analyses.section6 as s6
import analyses.section7 as s7
import analyses.section8 as s8
import analyses.section9 as s9
import analyses.section10 as s10
import analyses.section11 as s11
import analyses.section12 as s12


# ── Palette monochrome ───────────────────────────────────────────────────────
BG      = "#EFEFEF"
CARD_BG = "#FFFFFF"
BTN_BG  = "#FFFFFF"
BTN_FG  = "#1A1A1A"
BTN_HOV = "#E4E4E4"
TAB_SEL = "#1A1A1A"
# ────────────────────────────────────────────────────────────────────────────


def _appliquer_styles(root):
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TNotebook", background=BG, borderwidth=0)
    style.configure("TNotebook.Tab",
                    background="#CCCCCC", foreground="#444444",
                    padding=[12, 5], font=("Segoe UI", 9))
    style.map("TNotebook.Tab",
              background=[("selected", TAB_SEL)],
              foreground=[("selected", "#FFFFFF")])
    style.configure("TFrame", background=BG)
    style.configure("Card.TFrame", background=CARD_BG)


# ── Widgets boutons ───────────────────────────────────────────────────────────

def _bouton(parent, texte, commande):
    """Bouton standard monochrome, s'étire en largeur via pack(fill='x')."""
    btn = tk.Button(
        parent, text=texte, command=commande,
        bg=BTN_BG, fg=BTN_FG,
        activebackground=BTN_HOV, activeforeground=BTN_FG,
        font=("Segoe UI", 9), relief="solid", bd=1,
        cursor="hand2", pady=7, anchor='w', padx=14
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=BTN_HOV))
    btn.bind("<Leave>", lambda e: btn.config(bg=BTN_BG))
    return btn


def _bouton_stat(parent, nombre, label, commande, couleur_bord, textvariable=None):
    """Petit bouton avec nombre en gros + label, bordure colorée.
    Si textvariable est fourni, le nombre se met à jour automatiquement."""
    cadre = tk.Frame(parent, bg=couleur_bord, padx=2, pady=2)
    inner = tk.Frame(cadre, bg=CARD_BG, cursor="hand2")
    inner.pack(fill='both', expand=True)

    if textvariable:
        lbl_n = tk.Label(inner, textvariable=textvariable, bg=CARD_BG, fg=BTN_FG,
                         font=("Segoe UI", 13, "bold"), cursor="hand2")
    else:
        lbl_n = tk.Label(inner, text=str(nombre), bg=CARD_BG, fg=BTN_FG,
                         font=("Segoe UI", 13, "bold"), cursor="hand2")
    lbl_n.pack(padx=16, pady=(6, 0))

    lbl_t = tk.Label(inner, text=label, bg=CARD_BG, fg="#666666",
                     font=("Segoe UI", 8), cursor="hand2")
    lbl_t.pack(padx=16, pady=(0, 6))

    def _click(e):  commande()
    def _enter(e):
        for w in (inner, lbl_n, lbl_t): w.config(bg=BTN_HOV)
    def _leave(e):
        for w in (inner, lbl_n, lbl_t): w.config(bg=CARD_BG)

    for w in (inner, lbl_n, lbl_t):
        w.bind("<Button-1>", _click)
        w.bind("<Enter>", _enter)
        w.bind("<Leave>", _leave)

    return cadre


def _carte_info(parent, valeur, label, couleur):
    """Carte de stat non cliquable (cartes du bas).
    Si `valeur` est une StringVar, la carte se met à jour automatiquement."""
    frame = tk.Frame(parent, bg=couleur, padx=6, pady=10)
    if isinstance(valeur, tk.StringVar):
        tk.Label(frame, textvariable=valeur, bg=couleur, fg='white',
                 font=("Segoe UI", 16, "bold")).pack()
    else:
        tk.Label(frame, text=str(valeur), bg=couleur, fg='white',
                 font=("Segoe UI", 16, "bold")).pack()
    tk.Label(frame, text=label, bg=couleur, fg='white',
             font=("Segoe UI", 8)).pack()
    return frame


# Rafraîchisseurs des cartes : chaque onglet (dont les chiffres dépendent du
# modèle) enregistre ici une fonction qui relit ses get_info_sectionN(). Le bouton
# de ré-entraînement de la section 7 les appelle tous pour mettre à jour TOUTE
# l'interface d'un coup.
_rafraichisseurs = []


def _construire_cartes(parent, get_info):
    """
    Construit la rangée de cartes du bas à partir d'une fonction get_info_sectionN.
    Les valeurs sont des StringVar et on enregistre un rafraîchisseur : après un
    ré-entraînement (§7), on relit get_info() et les cartes se mettent à jour
    sans reconstruire l'onglet.
    """
    infos = get_info()
    variables = []
    for i, (valeur, label, couleur) in enumerate(infos):
        var = tk.StringVar(value=str(valeur))
        variables.append(var)
        padx = (0, 4) if i < len(infos) - 1 else (0, 0)
        _carte_info(parent, var, label, couleur).pack(
            side='left', fill='both', expand=True, padx=padx)

    def _refresh():
        for var, info in zip(variables, get_info()):
            var.set(str(info[0]))

    _rafraichisseurs.append(_refresh)


# ── Construction des onglets ──────────────────────────────────────────────────

def build_tab_section4(notebook):
    tab = ttk.Frame(notebook, style="Card.TFrame")
    notebook.add(tab, text="  Section 4  ")

    main = tk.Frame(tab, bg=CARD_BG)
    main.pack(fill='both', expand=True, padx=28, pady=22)

    # ── Sélecteur de dataset ──────────────────────────────────────────────────
    choix = tk.StringVar(value="original")

    def get_data():
        """Retourne le bon dataframe selon la sélection."""
        if choix.get() == "prepare":
            return s5.df_prepared
        return None  # les fonctions section4 utilisent df par défaut

    row_choix = tk.Frame(main, bg=CARD_BG)
    row_choix.pack(fill='x', pady=(0, 14))

    tk.Label(row_choix, text="Dataset :", bg=CARD_BG, fg=BTN_FG,
             font=("Segoe UI", 9, "bold")).pack(side='left')

    for valeur, texte in [("original", "Données originales"), ("prepare", "Données préparées")]:
        tk.Radiobutton(
            row_choix, text=texte, variable=choix, value=valeur,
            bg=CARD_BG, fg=BTN_FG, selectcolor=CARD_BG,
            activebackground=CARD_BG, font=("Segoe UI", 9), cursor="hand2"
        ).pack(side='left', padx=(12, 0))

    # ── Histogramme ──────────────────────────────────────────────────────────
    _bouton(main, "Histogramme",
            lambda: s4.show_histogrammes(get_data())).pack(fill='x', pady=(0, 8))

    # ── Type de donnée ───────────────────────────────────────────────────────
    _bouton(main, "Type de donnée",
            lambda: s4.show_types_donnees(get_data())).pack(fill='x', pady=(0, 8))

    # ── Données manquantes  |  [X NA]  [X Ab] ────────────────────────────────
    # StringVars pour les compteurs — mis à jour quand on change de dataset
    na_var = tk.StringVar(value=str(s4.NA_COUNT))
    ab_var = tk.StringVar(value=str(s4.AB_COUNT))

    def _maj_compteurs(*_):
        data = get_data()
        na_var.set(str(s4.get_na_count(data)))
        ab_var.set(str(s4.get_ab_count(data)))

    choix.trace_add("write", _maj_compteurs)

    row = tk.Frame(main, bg=CARD_BG)
    row.pack(fill='x', pady=(0, 8))

    _bouton_stat(row, None, "Ab", lambda: s4.show_aberantes(get_data()),
                 "#C0392B", textvariable=ab_var).pack(side='right')
    _bouton_stat(row, None, "NA", lambda: s4.show_na(get_data()),
                 "#2E9E4F", textvariable=na_var).pack(side='right', padx=(0, 8))
    _bouton(row, "Données manquantes",
            lambda: s4.show_donnees_manquantes(get_data())).pack(
        side='left', fill='x', expand=True, padx=(0, 8))

    # ── Séparateur ───────────────────────────────────────────────────────────
    tk.Frame(main, bg="#DDDDDD", height=1).pack(fill='x', pady=(14, 14))

    # ── Cartes de stats en bas ───────────────────────────────────────────────
    nb_lignes, cartes_dtype = s4.get_info_dataset()

    bas = tk.Frame(main, bg=CARD_BG)
    bas.pack(fill='x')

    _carte_info(bas, nb_lignes, "éléments", "#4A8C4A").pack(
        side='left', fill='both', expand=True, padx=(0, 4))

    for i, (count, dtype_label, couleur) in enumerate(cartes_dtype):
        padx = (0, 4) if i < len(cartes_dtype) - 1 else (0, 0)
        _carte_info(bas, count, f"col. {dtype_label}", couleur).pack(
            side='left', fill='both', expand=True, padx=padx)

    return tab


def build_tab_section5(notebook):
    tab = ttk.Frame(notebook, style="Card.TFrame")
    notebook.add(tab, text="  Section 5  ")

    main = tk.Frame(tab, bg=CARD_BG)
    main.pack(fill='both', expand=True, padx=28, pady=22)

    # ── Traitement NA ─────────────────────────────────────────────────────────
    row_na = tk.Frame(main, bg=CARD_BG)
    row_na.pack(fill='x', pady=(0, 8))

    _bouton_stat(row_na, s5.NB_NA_TRAITES, "col. traitées", s5.show_traitement_na,
                 "#2E9E4F").pack(side='right')
    _bouton(row_na, "Traitement NA", s5.show_traitement_na).pack(
        side='left', fill='x', expand=True, padx=(0, 8))

    # ── Traitement aberrants ──────────────────────────────────────────────────
    row_ab = tk.Frame(main, bg=CARD_BG)
    row_ab.pack(fill='x', pady=(0, 8))

    _bouton_stat(row_ab, s5.NB_AB_TRAITES, "col. écrêtées", s5.show_traitement_aberrants,
                 "#C0392B").pack(side='right')
    _bouton(row_ab, "Traitement aberrants", s5.show_traitement_aberrants).pack(
        side='left', fill='x', expand=True, padx=(0, 8))

    # ── Encodage qualitatif ───────────────────────────────────────────────────
    row_enc = tk.Frame(main, bg=CARD_BG)
    row_enc.pack(fill='x', pady=(0, 8))

    _bouton_stat(row_enc, s5.NB_ENCODES, "col. encodées", s5.show_encodage,
                 "#4A7FA5").pack(side='right')
    _bouton(row_enc, "Encodage qualitatif", s5.show_encodage).pack(
        side='left', fill='x', expand=True, padx=(0, 8))

    # ── Normalisation ─────────────────────────────────────────────────────────
    row_norm = tk.Frame(main, bg=CARD_BG)
    row_norm.pack(fill='x', pady=(0, 8))

    _bouton_stat(row_norm, s5.NB_SCALES, "col. normalisées", s5.show_normalisation,
                 "#7A5A9A").pack(side='right')
    _bouton(row_norm, "Normalisation", s5.show_normalisation).pack(
        side='left', fill='x', expand=True, padx=(0, 8))

    # ── Données préparées ─────────────────────────────────────────────────────
    _bouton(main, "Données après préparation", s5.show_donnees_preparees).pack(
        fill='x', pady=(0, 8))

    # ── Séparateur ────────────────────────────────────────────────────────────
    tk.Frame(main, bg="#DDDDDD", height=1).pack(fill='x', pady=(10, 14))

    # ── Cartes de stats en bas ────────────────────────────────────────────────
    bas = tk.Frame(main, bg=CARD_BG)
    bas.pack(fill='x')

    cartes = s5.get_info_section5()
    for i, (valeur, label, couleur) in enumerate(cartes):
        padx = (0, 4) if i < len(cartes) - 1 else (0, 0)
        _carte_info(bas, valeur, label, couleur).pack(
            side='left', fill='both', expand=True, padx=padx)

    return tab


def _construire_onglet_simple(notebook, titre, boutons, get_info):
    """
    Construit un onglet générique :
    - une liste de boutons pleine largeur (texte → callback)
    - un séparateur
    - une rangée de cartes d'info en bas (rafraîchies après un ré-entraînement)
    `get_info` est la fonction get_info_sectionN (passée sans l'appeler).
    Utilisé pour les sections 6, 8, 9, 10 et 11 qui ont la même structure simple.
    """
    tab = ttk.Frame(notebook, style="Card.TFrame")
    notebook.add(tab, text=titre)

    main = tk.Frame(tab, bg=CARD_BG)
    main.pack(fill='both', expand=True, padx=28, pady=22)

    for texte, commande in boutons:
        _bouton(main, texte, commande).pack(fill='x', pady=(0, 8))

    tk.Frame(main, bg="#DDDDDD", height=1).pack(fill='x', pady=(14, 14))

    bas = tk.Frame(main, bg=CARD_BG)
    bas.pack(fill='x')
    _construire_cartes(bas, get_info)

    return tab


def build_tab_section6(notebook):
    return _construire_onglet_simple(
        notebook, "  Section 6  ",
        boutons=[
            ("Heatmap des corrélations",       s6.show_heatmap_correlations),
            ("Corrélations avec outcome",       s6.show_correlations_outcome),
            ("Scatter matrix (top 5 variables)", s6.show_scatter_matrix),
        ],
        get_info=s6.get_info_section6,
    )


def build_tab_section7(notebook, test_pct):
    """
    Onglet section 7 sur mesure : un slider "administrateur" pour régler la
    proportion train/test, des cartes qui se mettent à jour en direct, et le
    bouton qui trace la répartition pour la valeur choisie.
    Le slider (test_pct) est partagé avec la section 8 (bouton ré-entraîner).
    """
    tab = ttk.Frame(notebook, style="Card.TFrame")
    notebook.add(tab, text="  Section 7  ")

    main = tk.Frame(tab, bg=CARD_BG)
    main.pack(fill='both', expand=True, padx=28, pady=22)

    # ── Slider de proportion de test ──────────────────────────────────────────
    ligne_titre = tk.Frame(main, bg=CARD_BG)
    ligne_titre.pack(fill='x', pady=(0, 2))
    tk.Label(ligne_titre, text="Proportion de test :", bg=CARD_BG, fg=BTN_FG,
             font=("Segoe UI", 9, "bold")).pack(side='left')
    resume_var = tk.StringVar()
    tk.Label(ligne_titre, textvariable=resume_var, bg=CARD_BG, fg="#666666",
             font=("Segoe UI", 9)).pack(side='right')

    tk.Scale(main, from_=10, to=50, resolution=5, orient='horizontal',
             variable=test_pct, bg=CARD_BG, fg=BTN_FG, troughcolor="#DDDDDD",
             highlightthickness=0, showvalue=False, sliderrelief='solid',
             length=300).pack(fill='x', pady=(0, 12))

    # ── Bouton : ré-entraîne TOUT le pipeline avec la proportion choisie ───────
    # On ne rouvre PAS de fenêtre matplotlib : on relance les sections 7→12 dans
    # l'ordre (chacune a son reentrainer()), on rafraîchit les cartes de tous les
    # onglets, et on affiche le résumé dans un label. Les graphes des autres
    # onglets liront le nouvel état la prochaine fois qu'on les ouvre.
    resultat_var = tk.StringVar(value="Clique pour ré-entraîner tout le pipeline (§7 à §12) avec cette proportion.")

    def _reevaluer():
        pct = test_pct.get()
        s7.reentrainer(pct / 100)   # nouveau split courant
        s8.reentrainer()            # régression logistique
        s9.reentrainer()            # métriques sur le test
        s10.reentrainer()           # validation croisée
        s11.reentrainer()           # comparaison d'algos
        s12.reentrainer()           # meilleur modèle réentraîné
        for rafraichir in _rafraichisseurs:
            rafraichir()
        resultat_var.set(
            f"Pipeline ré-entraîné ({100 - pct}/{pct}).   "
            f"Train §8 = {s8.SCORE_TRAIN:.3f}    "
            f"Test §9 = {s9.ACCURACY:.3f}    "
            f"CV §10 = {s10.CV_MOYENNE:.3f} ± {s10.CV_ECART:.3f}    "
            f"Meilleur §11 = {s11.MEILLEUR_NOM}")

    _bouton(main, "Ré-entraîner tout le pipeline avec cette proportion (§7 → §12)",
            _reevaluer).pack(fill='x', pady=(0, 6))
    tk.Label(main, textvariable=resultat_var, bg=CARD_BG, fg="#444444",
             font=("Segoe UI", 9), justify='left', wraplength=820).pack(fill='x', pady=(0, 8))

    # ── Séparateur ────────────────────────────────────────────────────────────
    tk.Frame(main, bg="#DDDDDD", height=1).pack(fill='x', pady=(14, 14))

    # ── Cartes dynamiques (train / test / features / test_size) ───────────────
    bas = tk.Frame(main, bg=CARD_BG)
    bas.pack(fill='x')

    train_var, test_var, pct_var = tk.StringVar(), tk.StringVar(), tk.StringVar()
    cartes = [
        (train_var,                 "train",     "#4A7FA5"),
        (test_var,                  "test",      "#C07835"),
        (str(len(s7.NOMS_FEATURES)), "features",  "#444444"),
        (pct_var,                   "test_size", "#7A5A9A"),
    ]
    for i, (valeur, label, couleur) in enumerate(cartes):
        padx = (0, 4) if i < len(cartes) - 1 else (0, 0)
        _carte_info(bas, valeur, label, couleur).pack(
            side='left', fill='both', expand=True, padx=padx)

    # ── Mise à jour en direct quand on bouge le slider ────────────────────────
    def _maj(*_):
        pct = test_pct.get()
        n_train, n_test = s7.compter(pct / 100)
        train_var.set(str(n_train))
        test_var.set(str(n_test))
        pct_var.set(f"{pct}%")
        resume_var.set(f"{100 - pct}% train  /  {pct}% test")

    test_pct.trace_add("write", _maj)
    _maj()

    return tab


def build_tab_section8(notebook):
    return _construire_onglet_simple(
        notebook, "  Section 8  ",
        boutons=[
            ("Coefficients appris (poids w)", s8.show_coefficients),
        ],
        get_info=s8.get_info_section8,
    )


def build_tab_section9(notebook):
    return _construire_onglet_simple(
        notebook, "  Section 9  ",
        boutons=[
            ("Matrice de confusion",     s9.show_matrice_confusion),
            ("Métriques d'évaluation",   s9.show_metriques),
        ],
        get_info=s9.get_info_section9,
    )


def build_tab_section10(notebook):
    return _construire_onglet_simple(
        notebook, "  Section 10  ",
        boutons=[
            ("Scores de validation croisée", s10.show_scores_cv),
        ],
        get_info=s10.get_info_section10,
    )


def build_tab_section11(notebook):
    return _construire_onglet_simple(
        notebook, "  Section 11  ",
        boutons=[
            ("Comparaison des algorithmes", s11.show_comparaison),
        ],
        get_info=s11.get_info_section11,
    )


def build_tab_section12(notebook):
    """
    Section 12 sur mesure : le bilan de sauvegarde s'affiche DANS l'onglet
    (label texte), pas dans une fenêtre matplotlib.
    """
    tab = ttk.Frame(notebook, style="Card.TFrame")
    notebook.add(tab, text="  Section 12  ")

    main = tk.Frame(tab, bg=CARD_BG)
    main.pack(fill='both', expand=True, padx=28, pady=22)

    resultat = tk.StringVar(
        value="Clique sur le bouton pour sauvegarder le meilleur modèle\n"
              "et vérifier qu'il se recharge à l'identique.")
    label_resultat = tk.Label(main, textvariable=resultat, bg=CARD_BG, fg="#444444",
                              font=("Courier", 9), justify='left', anchor='w')

    def _faire():
        ok, texte = s12.bilan_texte()
        resultat.set(texte)
        label_resultat.config(fg="#2E7D32" if ok else "#C0392B")

    _bouton(main, "Sauvegarder et vérifier le modèle", _faire).pack(fill='x', pady=(0, 12))
    label_resultat.pack(fill='x', pady=(0, 12))

    tk.Frame(main, bg="#DDDDDD", height=1).pack(fill='x', pady=(4, 14))

    bas = tk.Frame(main, bg=CARD_BG)
    bas.pack(fill='x')
    _construire_cartes(bas, s12.get_info_section12)

    return tab


def lancer_interface():
    root = tk.Tk()
    root.title("Assurance Prévision — Projet Science des données")
    root.geometry("880x460")
    root.configure(bg=BG)
    root.resizable(True, True)
    root.minsize(520, 380)

    _appliquer_styles(root)

    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)

    # Slider test_size partagé entre la section 7 (réglage) et la section 8 (ré-entraînement)
    test_pct = tk.IntVar(value=int(s7.TEST_SIZE * 100))

    build_tab_section4(notebook)
    build_tab_section5(notebook)
    build_tab_section6(notebook)
    build_tab_section7(notebook, test_pct)
    build_tab_section8(notebook)
    build_tab_section9(notebook)
    build_tab_section10(notebook)
    build_tab_section11(notebook)
    build_tab_section12(notebook)

    root.mainloop()
