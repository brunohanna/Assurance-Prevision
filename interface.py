import tkinter as tk
from tkinter import ttk

import analyses.section4 as s4


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


def _bouton_stat(parent, nombre, label, commande, couleur_bord):
    """Petit bouton avec nombre en gros + label, bordure colorée."""
    cadre = tk.Frame(parent, bg=couleur_bord, padx=2, pady=2)
    inner = tk.Frame(cadre, bg=CARD_BG, cursor="hand2")
    inner.pack(fill='both', expand=True)

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

    # Conteneur principal qui couvre tout l'onglet
    main = tk.Frame(tab, bg=CARD_BG)
    main.pack(fill='both', expand=True, padx=28, pady=22)

    # ── Histogramme ──────────────────────────────────────────────────────────
    _bouton(main, "Histogramme", s4.show_histogrammes).pack(fill='x', pady=(0, 8))

    # ── Type de donnée ───────────────────────────────────────────────────────
    _bouton(main, "Type de donnée", s4.show_types_donnees).pack(fill='x', pady=(0, 8))

    # ── Données manquantes  |  [X NA]  [X Ab] ────────────────────────────────
    row = tk.Frame(main, bg=CARD_BG)
    row.pack(fill='x', pady=(0, 8))

    # On pack les boutons droits EN PREMIER pour que le bouton gauche remplisse le reste
    _bouton_stat(row, s4.AB_COUNT, "Ab", s4.show_aberantes,
                 "#C0392B").pack(side='right')
    _bouton_stat(row, s4.NA_COUNT, "NA", s4.show_na,
                 "#2E9E4F").pack(side='right', padx=(0, 8))
    _bouton(row, "Données manquantes", s4.show_donnees_manquantes).pack(
        side='left', fill='x', expand=True, padx=(0, 8))

    # ── Séparateur ───────────────────────────────────────────────────────────
    tk.Frame(main, bg="#DDDDDD", height=1).pack(fill='x', pady=(14, 14))

    # ── Cartes de stats en bas ───────────────────────────────────────────────
    nb_lignes, cartes_dtype = s4.get_info_dataset()

    bas = tk.Frame(main, bg=CARD_BG)
    bas.pack(fill='x')

    # Carte verte : nombre d'éléments
    _carte_info(bas, nb_lignes, "éléments", "#4A8C4A").pack(
        side='left', fill='both', expand=True, padx=(0, 4))

    # Cartes colorées : une par type de donnée
    for i, (count, dtype_label, couleur) in enumerate(cartes_dtype):
        padx = (0, 4) if i < len(cartes_dtype) - 1 else (0, 0)
        _carte_info(bas, count, f"col. {dtype_label}", couleur).pack(
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

    root.mainloop()
