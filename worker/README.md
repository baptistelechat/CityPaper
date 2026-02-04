# Guide d'utilisation du Worker (Générateur de Cartes)

Ce dossier contient le script Python permettant de générer les posters de cartes.
Il utilise la librairie `maptoposter` (qui sera automatiquement installée/mise à jour lors de l'exécution).

## Pré-requis

1.  **Python 3.11+** installé sur votre machine.
2.  C'est tout ! Le script s'occupe de créer l'environnement virtuel et d'installer les dépendances automatiquement.
3.  **Hugging Face Token** : Assurez-vous d'avoir défini `HF_TOKEN` dans votre environnement.

## Lancer une génération

Utilisez le script principal `main.py` qui gère tout pour vous (installation, mise à jour, dépendances, upload HF, git).

### 1. Génération + Upload Hugging Face (Sans déploiement)

Cette commande génère les cartes pour les villes listées dans le fichier JSON, les upload sur Hugging Face, et met à jour la base de données locale (`data/cities.json`), mais **ne pousse pas** les changements sur GitHub.

```bash
# Depuis la racine du projet
python worker/main.py --source-json cities_to_process.json
```

### 2. Génération + Upload Hugging Face + Déploiement (Git Push)

C'est la commande principale à utiliser pour la production. Elle fait tout comme la précédente, mais **pousse aussi** les changements (`data/cities.json`) sur GitHub, ce qui déclenche le redéploiement Vercel.

```bash
# Depuis la racine du projet
python worker/main.py --source-json cities_to_process.json --push
```

### 3. Génération unitaire (Test rapide)

Pour tester une seule ville rapidement :

```bash
python worker/main.py --city "Nantes" --country "France" --theme "noir"
```

## Configuration du fichier JSON

Le fichier `cities_to_process.json` doit être à la racine du projet et suivre ce format :

```json
[
  {
    "name": "Paris",
    "country": "France"
  },
  {
    "name": "Lyon",
    "country": "France"
  }
]
```

## Résultat

1.  **Images** : Uploadées sur Hugging Face (Dataset `citypaper-maps`).
2.  **Base de données** : Le fichier `data/cities.json` est mis à jour avec les nouveaux liens.
3.  **Git** : Si `--push` est utilisé, `data/cities.json` est commité et poussé.
