# Guide d'utilisation du Worker (Générateur de Cartes)

Ce dossier contient le script Python permettant de générer les posters de cartes.
Il utilise la librairie `maptoposter` (qui sera automatiquement installée/mise à jour lors de l'exécution).

## Pré-requis

1.  **Python 3.11+** installé sur votre machine.
2.  C'est tout ! Le script s'occupe de créer l'environnement virtuel et d'installer les dépendances automatiquement.

## Lancer une génération

Utilisez le script wrapper `generate_city.py` qui gère tout pour vous (installation, mise à jour, dépendances).

**Commande de base :**

```bash
# Depuis la racine du projet
python worker/generate_city.py --city "Ville" --country "Pays"
```

**Exemple :**

```bash
python worker/generate_city.py --city "Paris" --country "France"
```

Par défaut, cela générera **tous les thèmes** disponibles.

**Options disponibles :**

- `--theme "nom_du_theme"` : Pour générer un seul thème spécifique (ex: `noir`).
- `--all-themes` : Force la génération de tous les thèmes (comportement par défaut si aucun thème n'est précisé).

## Résultat

Les fichiers générés (PNG) seront automatiquement déplacés dans :
`output/maps/` (à la racine du projet)
