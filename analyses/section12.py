import os
import pickle

import numpy as np
from sklearn.linear_model import LogisticRegression, Perceptron
from sklearn.neighbors import KNeighborsClassifier

import analyses.section7 as s7
import analyses.section11 as s11
from analyses.data import BASE_DIR
from analyses.section7 import RANDOM_SEED


MODELE_PATH = os.path.join(BASE_DIR, 'modele.pkl')


def _construire_meilleur():
    """
    Recrée le meilleur modèle désigné par la section 11, à partir de son nom.
    On le réentraîne ensuite sur le jeu d'apprentissage courant avant de sauver.
    """
    nom = s11.MEILLEUR_NOM
    if nom.startswith("KNN"):
        k = int(nom.split("=")[1].rstrip(")"))
        return KNeighborsClassifier(n_neighbors=k)
    if nom == "Perceptron":
        return Perceptron(random_state=RANDOM_SEED)
    return LogisticRegression(max_iter=1000, random_state=RANDOM_SEED)


modele_final = _construire_meilleur()
modele_final.fit(s7.X_train, s7.y_train)


def reentrainer():
    """
    Reconstruit le meilleur modèle (désigné par la §11 ré-évaluée) et le ré-entraîne
    sur le jeu d'apprentissage COURANT. Ne sauvegarde PAS sur disque : l'écriture
    du .pkl reste l'action explicite du bouton "Sauvegarder et vérifier".
    """
    global modele_final
    modele_final = _construire_meilleur()
    modele_final.fit(s7.X_train, s7.y_train)


def sauvegarder():
    """Écrit le modèle entraîné sur le disque avec pickle. Renvoie le chemin."""
    with open(MODELE_PATH, 'wb') as f:
        pickle.dump(modele_final, f)
    return MODELE_PATH


def verifier():
    """
    Recharge le modèle sauvegardé et vérifie qu'il prédit la même chose que
    l'original sur 5 échantillons de test. C'est la preuve que la sauvegarde est
    fidèle. Renvoie (ok, prédictions origine, prédictions rechargé).
    """
    with open(MODELE_PATH, 'rb') as f:
        modele_recharge = pickle.load(f)

    echantillon   = s7.X_test[:5]
    pred_origine  = modele_final.predict(echantillon)
    pred_recharge = modele_recharge.predict(echantillon)
    ok = bool(np.array_equal(pred_origine, pred_recharge))
    return ok, pred_origine, pred_recharge


def bilan_texte():
    """
    Sauvegarde + recharge + vérifie, et renvoie (ok, texte) prêt à afficher dans
    l'onglet tkinter (pas de figure matplotlib pour cette section).
    """
    chemin             = sauvegarder()
    ok, p_orig, p_rech = verifier()

    verdict = ("IDENTIQUE — le modèle est correctement sauvegardé" if ok
               else "DIFFÉRENT — problème de sauvegarde")
    texte = (
        f"Meilleur modèle : {s11.MEILLEUR_NOM}  (accuracy CV = {s11.MEILLEUR_SCORE:.3f})\n"
        f"Fichier         : {os.path.basename(chemin)}\n\n"
        f"Vérification après rechargement (5 échantillons de test) :\n"
        f"   modèle d'origine : {[int(v) for v in p_orig]}\n"
        f"   modèle rechargé  : {[int(v) for v in p_rech]}\n\n"
        f"   -> {verdict}"
    )
    return ok, texte


# ── Infos pour les cartes en bas de l'onglet ──────────────────────────────────

def get_info_section12():
    return [
        (s11.MEILLEUR_NOM,            "modèle sauvé", "#4A8C4A"),
        (f"{s11.MEILLEUR_SCORE:.3f}", "accuracy CV",  "#4A7FA5"),
        ("modele.pkl",               "fichier",      "#444444"),
    ]
