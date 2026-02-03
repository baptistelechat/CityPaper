# Story 2.1: Script Python de Génération (Base)

**ID:** STORY-2.1
**Epic:** Epic 2 - Usine de Cartes Automatisée
**Priority:** Must Have
**Story Points:** 5 (Complexité modérée - Setup Python + Logiciel de carte)

## User Story

En tant que développeur,
Je veux un script Python qui utilise `maptoposter` pour générer des cartes,
Afin d'obtenir automatiquement des visuels variés et esthétiques pour n'importe quelle ville.

## Acceptance Criteria

- [ ] **Environnement Python** : Le script tourne sous Python 3.11+ et intègre la librairie/outil `maptoposter`.
- [ ] **Input** : Le script accepte un nom de ville et de pays (ex: `python generate.py --city "Lyon" --country "France"`).
- [ ] **Style (Thèmes)** : Le script doit être capable de générer **tous les styles** disponibles dans `maptoposter` (ex: `noir`, `minimal`, `terracotta`, `blueprint`, etc.) ou un style spécifique passé en paramètre.
- [ ] **Output** : Le script doit conserver **tous les fichiers générés** par `maptoposter` (PNG, PDF, SVG si dispo).
- [ ] **Richesse Visuelle** : Ne pas se limiter au Noir & Blanc, exploiter la diversité des thèmes de la librairie.

## Technical Notes

- **Outil Core** : `maptoposter` (https://github.com/originalankur/maptoposter).
- **Intégration** :
  - Cloner ou installer `maptoposter` dans le dossier `/worker`.
  - Gérer les dépendances via `uv` ou `pip` (`requirements.txt`).
- **Commande** : S'inspirer de la CLI de maptoposter : `uv run ./create_map_poster.py --city "Paris" --country "France" --all-themes`.
- **Performance** : Attention au temps de génération si l'option `--all-themes` est activée (peut être long).

## Dependencies

- Dépendance externe : Repo `maptoposter` et API OpenStreetMap.

## Definition of Done

- [ ] L'outil `maptoposter` est fonctionnel dans `/worker`.
- [ ] Un script wrapper (ou l'utilisation directe) permet de lancer la génération.
- [ ] Test manuel : Générer "Paris" avec plusieurs thèmes et vérifier la présence des fichiers de sortie.
