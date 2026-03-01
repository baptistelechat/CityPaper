# Guide d'utilisation du Worker (Générateur de Cartes)

Ce dossier contient le script Python permettant de générer les posters de cartes.
Il utilise la librairie `maptoposter` (qui sera automatiquement installée/mise à jour lors de l'exécution).

## Pré-requis

1.  **Python 3.11+** installé sur votre machine.
2.  C'est tout ! Le script s'occupe de créer l'environnement virtuel et d'installer les dépendances automatiquement.
3.  **Hugging Face Token** : Assurez-vous d'avoir défini `HF_TOKEN` dans votre environnement.

## Lancer une génération

Utilisez le script principal `main.py` qui gère tout pour vous (installation, mise à jour, dépendances, upload HF, git).

### 1. Mode Surveillance (Production)

C'est le mode principal à utiliser pour que le worker écoute Supabase en continu et traite les requêtes entrantes.

```bash
# Lance le démon de surveillance
python worker/main.py watch --push
```

Ce mode :

- Vérifie les nouvelles requêtes toutes les 10 secondes.
- Génère les cartes.
- Upload sur Hugging Face.
- Pousse automatiquement les mises à jour Git pour la base de données.

### 2. Mode Test (Développement / One-Shot)

Pour tester la génération d'une seule ville localement sans passer par Supabase.

```bash
# Test simple
python worker/main.py test "Nantes" "France"

# Test avec code postal (plus précis)
python worker/main.py test "Paris" "France" --postcode 75001

# Test avec un thème spécifique et upload Git
python worker/main.py test "Lyon" "France" --theme "noir" --push
```

## Résultat

1.  **Images** : Uploadées sur Hugging Face (Dataset `citypaper-maps`).
2.  **Base de données** : Le fichier `data/cities.json` est mis à jour avec les nouveaux liens.
3.  **Git** : Si `--push` est utilisé, `data/cities.json` est commité et poussé.
