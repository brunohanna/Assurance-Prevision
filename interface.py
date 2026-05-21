import tkinter as tk
from tkinter import ttk

import analyses.section4 as s4
import analyses.section5 as s5


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
    """Carte de stat non cliquable (cartes du bas)."""
    frame = tk.Frame(parent, bg=couleur, padx=6, pady=10)
    tk.Label(frame, text=str(valeur), bg=couleur, fg='white',
             font=("Segoe UI", 16, "bold")).pack()
    tk.Label(frame, text=label, bg=couleur, fg='white',
             font=("Segoe UI", 8)).pack()
    return frame


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


def lancer_interface():
    root = tk.Tk()
    root.title("Assurance Prévision — Projet Science des données")
    root.geometry("660x420")
    root.configure(bg=BG)
    root.resizable(True, True)
    root.minsize(500, 360)

    _appliquer_styles(root)

    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)

    build_tab_section4(notebook)
    build_tab_section5(notebook)

    root.mainloop()
