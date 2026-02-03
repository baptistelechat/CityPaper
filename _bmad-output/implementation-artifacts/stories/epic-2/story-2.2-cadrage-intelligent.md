# Story 2.2: Cadrage Intelligent & Multi-Formats

**ID:** STORY-2.2
**Epic:** Epic 2 - Usine de Cartes Automatisée
**Priority:** Must Have
**Story Points:** 5 (Complexité augmentée - Calcul géospatial + Gestion formats)

## User Story

En tant que créateur de contenu,
Je veux que le script calcule automatiquement la distance idéale pour englober la ville et génère les visuels dans plusieurs formats standards,
Afin d'obtenir des fichiers prêts à l'emploi pour Instagram, le Print et les Wallpapers sans ajustement manuel.

## Acceptance Criteria

### 1. Calcul Intelligent du Rayon (Distance)

- [ ] **Récupération BBox** : Le script récupère la Bounding Box administrative (via `osmnx` ou Overpass) pour obtenir `(north, south, east, west)`.
- [ ] **Calcul Centre** : Détermine le centre géographique : `lat = (north + south) / 2`, `lon = (east + west) / 2`.
- [ ] **Calcul Distance** : Calcule la distance (rayon) nécessaire pour couvrir la diagonale de la BBox + une marge (padding) de ~10%.
- [ ] **Application** : Passe ces valeurs calculées à `maptoposter` via les arguments `--latitude`, `--longitude` et `--distance`.

### 2. Gestion Multi-Formats

- [ ] Le script doit générer les cartes pour les formats suivants (configurables) en utilisant les paramètres `-W` (Largeur) et `-H` (Hauteur) :
  - **Instagram Post** : 1080x1080px (`-W 3.6 -H 3.6`)
  - **Mobile Wallpaper** : 1080x1920px (`-W 3.6 -H 6.4`)
  - **HD Wallpaper** : 1920x1080px (`-W 6.4 -H 3.6`)
  - **4K Wallpaper** : 3840x2160px (`-W 12.8 -H 7.2`)
  - **A4 Print** : 2480x3508px (`-W 8.3 -H 11.7`)

### 3. Organisation des Sorties

- [ ] Les fichiers générés doivent être triés dans une arborescence stricte :
      `output/{Pays}/{Region}/{Departement}/{Ville}/{Format}/`
  - _Exemple :_ `output/France/Auvergne-Rhone-Alpes/Rhone/Lyon/Mobile_Wallpaper/lyon-mobile.png`
- [ ] Le script doit tenter de récupérer la "Region" et le "Département" selon le pays via les métadonnées OSM (Admin Level 6 pour France, Level 4 pour autres souvent). Si introuvable, utiliser une velur fallback logique.

## Technical Notes

- **Calcul Distance** : Utiliser la formule de Haversine pour calculer la distance entre le Centre `(lat, lon)` et un coin `(north, east)`. Cette distance sera la valeur `--distance`.
- **Arguments maptoposter** :
  - Utiliser `--latitude` et `--longitude` pour forcer le centre calculé.
  - Utiliser `--distance` pour le rayon.
  - Ne PAS utiliser `--city` pour le géocodage de `maptoposter` (qui prendrait le centre par défaut), mais uniquement pour l'affichage (`--display-city`).
- **OSMnx** : `gdf = osmnx.geocode_to_gdf(query)` retourne les colonnes `bbox_north`, `bbox_south`, etc. et souvent les infos hiérarchiques (display_name contenant le département).
- **Structure Dossier** : Utiliser `pathlib` pour créer l'arborescence proprement.

## Architecture Compliance

- **Language** : Python 3.11+
- **Environment** : Worker (local/RPi)
- **Dependencies** : `osmnx`, `geopy` (pour distance geodesique si besoin), `pandas` (dépendance osmnx).

## Definition of Done

- [ ] Le script prend une ville en entrée et génère TOUS les formats demandés.
- [ ] Les images ne sont pas coupées (la ville entière est visible).
- [ ] Les fichiers sont rangés dans `output/Pays/Departement/Ville/Format/`.
- [ ] Le calcul de la distance est loggué dans la console pour vérification.
