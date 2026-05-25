from sklearn.model_selection import train_test_split

from analyses.section5 import df_prepared


CIBLE       = 'outcome'
TEST_SIZE   = 0.2          # 80% train / 20% test
RANDOM_SEED = 42           # reproductibilité

# Séparation X / y
_X = df_prepared.drop(columns=[CIBLE]).to_numpy()
_y = df_prepared[CIBLE].to_numpy()

NOMS_FEATURES = df_prepared.drop(columns=[CIBLE]).columns.tolist()


def decouper(test_size=TEST_SIZE, random_state=RANDOM_SEED):
    """
    Découpe stratifiée X/y selon la proportion de test demandée.
    stratify=_y garde la même proportion de classes dans train et test : sans ça,
    un déséquilibre 70/30 peut devenir 75/25 d'un côté par hasard et fausser
    l'évaluation. On la rend paramétrable pour le slider de l'interface.
    """
    return train_test_split(_X, _y, test_size=test_size,
                            random_state=random_state, stratify=_y)


def compter(test_size=TEST_SIZE):
    """
    Tailles (n_train, n_test) pour une proportion de test donnée, sans refaire la
    découpe complète ni le graphe. Sert à rafraîchir les cartes pendant qu'on
    déplace le slider (rapide même appelé en continu).
    """
    n = len(_y)
    n_test = int(round(n * test_size))
    return n - n_test, n_test


# Split COURANT (modifiable depuis l'interface via reentrainer()). Au démarrage
# c'est la découpe par défaut 80/20. Les sections 8 à 12 lisent ce split via le
# module analyses.section7 (et non par copie), pour que tout reste cohérent quand
# on change la proportion depuis le slider de la section 7.
X_train, X_test, y_train, y_test = decouper()


def reentrainer(test_size):
    """
    Recalcule le split courant pour une nouvelle proportion de test et le stocke
    dans les variables de module. Les sections suivantes ont chacune leur propre
    reentrainer() qui repart de ce split (X_train/X_test/y_train/y_test mis à jour
    ici). On l'appelle EN PREMIER dans la chaîne de ré-entraînement.
    """
    global X_train, X_test, y_train, y_test
    X_train, X_test, y_train, y_test = decouper(test_size)


# ── Infos pour les cartes en bas de l'onglet ──────────────────────────────────

def get_info_section7():
    return [
        (len(X_train),                 "train",     "#4A7FA5"),
        (len(X_test),                  "test",      "#C07835"),
        (len(NOMS_FEATURES),           "features",  "#444444"),
        (f"{int(TEST_SIZE * 100)}%",   "test_size", "#7A5A9A"),
    ]
