---
stepsCompleted:
  - 1
inputDocuments: []
workflowType: "research"
lastStep: 1
research_type: "technical"
research_topic: "async-generation-pipeline"
research_goals: "Valider la faisabilité du pipeline Low-Tech (Notion -> RPi -> Git -> Vercel) et les performances de maptoposter."
user_name: "Baptiste"
date: "2026-02-02"
web_research_enabled: true
source_verification: true
---

# Rapport de Recherche : Faisabilité Technique - Pipeline Asynchrone

**Date :** 02/02/2026
**Auteur :** Baptiste
**Type de Recherche :** technical

---

## Vue d'ensemble

Ce rapport étudie la faisabilité technique d'un pipeline "Low-Tech / Haute Performance" utilisant un Raspberry Pi 5 comme worker, Notion comme base de données/file d'attente, et Vercel pour l'hébergement statique. L'objectif est d'assurer que cette architecture peut passer à l'échelle pour des centaines de villes avec zéro coût de calcul cloud.

---

## 1. Validation de l'Architecture

### Le Pipeline Global

`Demande Utilisateur (Web)` -> `Base Notion` -> `RPi 5 (Worker)` -> `Génération Carte` -> `Stockage (R2)` -> `Git Commit (JSON)` -> `Vercel Rebuild`

### Architecture Interne du Générateur (maptoposter)

Le cœur de la génération repose sur le script `maptoposter`. Voici son fonctionnement interne :

```text
 ┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
 │   CLI Parser    │────▶│  Geocoding   │────▶│  Data Fetching  │
 │   (argparse)    │     │  (Nominatim) │     │    (OSMnx)      │
 └─────────────────┘     └──────────────┘     └─────────────────┘
                                                      │
                         ┌──────────────┐             ▼
                         │    Output    │◀────┌─────────────────┐
                         │  (matplotlib)│     │   Rendering     │
                         └──────────────┘     │  (matplotlib)   │
                                              └─────────────────┘
```

**Composants Clés :**

- **CLI Parser** : Point d'entrée pour le worker (arguments: ville, style, couleur).
- **Geocoding (Nominatim)** : Résolution de nom (ex: "Paris") vers Bounding Box. _Attention aux limites d'API ici aussi._
- **Data Fetching (OSMnx)** : Récupération des graphes de rues et géométries.
- **Rendering (matplotlib)** : Moteur de rendu graphique.

### Évaluation de Faisabilité

- **Notion comme Base de Données/File d'attente** : **FAISABLE**
  - **Rate Limits** : 3 requêtes/sec en moyenne. Suffisant pour un worker qui "poll" toutes les 30-60s.
  - **SDK** : `notion-client` (Python) supporte async/await.
  - **Contrainte** : Pas de webhooks natifs pour les changements DB (nécessite du polling).
- **Raspberry Pi 5 (Worker)** : **FAISABLE & PUISSANT**
  - **Performance** : 2-3x plus rapide que le RPi 4. La génération Python/Matplotlib sera raisonnablement rapide (est. 10-60s par carte).
  - **Mémoire** : 4Go/8Go de RAM suffisent pour la manipulation d'images haute résolution (50x70cm @ 300dpi est lourd mais gérable).
- **GitOps (Le Mécanisme de Livraison)** : **FAISABLE AVEC AJUSTEMENT**
  - Le RPi peut faire un `git push` standard.
  - **Vercel Trigger** : Pousser sur `main` déclenche automatiquement un déploiement.
  - **Latence** : L'étape "Git -> Vercel" prend 1-3 minutes (temps de build). Acceptable pour un flux asynchrone ("on vous envoie un email quand c'est prêt").

## 2. Le Problème du Stockage & Git

### Pourquoi Git ne suffit pas (Certitude : 100%)

- **Taille du Repo** : GitHub impose une limite stricte (soft limit à 1Go, hard limit plus haut mais risqué).
- **Calcul** : 100 villes x 50 Mo (PNG Haute Def) = **5 Go**.
- **Conséquence** : Votre repo sera bloqué par GitHub. De plus, cloner 5Go à chaque build Vercel (CI/CD) explosera les quotas de bande passante et ralentira tout.
- **Git LFS (Large File Storage)** : Le tiers gratuit est limité à 1 Go de stockage et 1 Go de bande passante/mois. C'est insuffisant.

### Comparatif Stockage Gratuit (R2 vs Supabase)

Puisque vous avez déjà des projets Supabase, voici la comparaison pour le Free Tier :

| Feature                     | **Cloudflare R2** (Recommandé)     | **Supabase Storage**                                                   |
| :-------------------------- | :--------------------------------- | :--------------------------------------------------------------------- |
| **Stockage Gratuit**        | **10 Go** / mois                   | 500 Mo (ou 1Go selon projet)                                           |
| **Bande Passante (Egress)** | **Illimitée / Gratuite**           | 2 Go / mois (Free Tier)                                                |
| **Frais de Sortie**         | 0 $                                | Payant au-delà du quota                                                |
| **Usage CityPaper**         | Parfait pour stocker des gros PNG. | Trop juste pour des fichiers HD (50Mo x 40 downloads = quota explosé). |

**Verdict** : Utilisez **Cloudflare R2** pour stocker les fichiers images (PNG/PDF). Utilisez Supabase pour la base de données ou l'Auth si besoin, mais pas pour le stockage de masse des posters gratuits.

## 3. Considérations de Performance

### Vitesse de Génération (RPi 5)

- **Outils** : `ankur/maptoposter` (Python) utilise probablement `matplotlib` + `cartopy` ou `osmnx`.
- **Goulot d'étranglement** : Récupérer les données OpenStreetMap (API Overpass) est la partie la plus lente.
- **Optimisation** :
  - Mettre en cache les données OSM localement pour les régions populaires.
  - Utiliser des dumps PBF au lieu de l'API live pour la génération en masse.
  - **Rate Limits** : L'API Overpass a des limites strictes. Le RPi doit implémenter un backoff/file d'attente.

## 4. Sélection des Outils

- **Langage** : Python (pour l'écosystème `maptoposter`).
- **Bibliothèques** :
  - `notion-client` : Pour la gestion de la file d'attente.
  - `matplotlib` / `osmnx` / `contextily` : Pour la génération de cartes.
  - `boto3` (ou compatible S3) : Pour uploader sur Cloudflare R2.
- **Matériel** : Raspberry Pi 5 (Refroidissement actif recommandé pour les jobs par lots continus).

## 5. Conclusion & Recommandations

1.  **Architecture Validée** : Le flux Notion -> RPi -> Vercel fonctionne.
2.  **Pivot Stockage Requis** : Ne **JAMAIS** commiter de PNG haute résolution dans le repo Git.
    - **Nouveau Flux** : Le RPi génère l'image -> Upload sur R2 -> Commit une nouvelle entrée dans `cities.json` (avec l'URL R2) -> Vercel Rebuild.
3.  **Stratégie de File d'Attente** : Poller Notion toutes les 60s. Gérer les limites de l'API Overpass avec élégance.

---

**Prochaines Étapes :**

- Revoir les contraintes du Domaine (Licences/Specs d'impression).
