---
stepsCompleted:
  - 1
inputDocuments: []
workflowType: "research"
lastStep: 1
research_type: "domain"
research_topic: "print-data-constraints"
research_goals: "Analyser la licence OpenStreetMap (usage commercial), les exigences de qualité d'impression (DPI) et les sources de données."
user_name: "Baptiste"
date: "2026-02-02"
web_research_enabled: true
source_verification: true
---

# Rapport de Recherche : Contraintes du Domaine - Impression & Données

**Date :** 02/02/2026
**Auteur :** Baptiste
**Type de Recherche :** domain

---

## Vue d'ensemble

Ce rapport définit les contraintes légales et physiques pour les produits CityPaper : la conformité à la licence OpenStreetMap ODbL et les spécifications techniques pour une impression de qualité professionnelle.

---

## 1. Licences de Données (OpenStreetMap)

### La Licence : ODbL (Open Database License)

Les données OpenStreetMap sont **libres d'utilisation** à des fins commerciales, MAIS elles viennent avec des exigences d'attribution strictes.

### Exigences pour CityPaper

1.  **Attribution** : Vous **DEVEZ** créditer OpenStreetMap.
    - *Sur le Site Web* : "Maps data © OpenStreetMap contributors".
    - *Sur le Produit* : L'affiche physique/numérique **devrait** contenir une petite ligne de crédit (ex: "Data © OpenStreetMap contributors" dans un coin).
    - *Risque Légal* : L'absence d'attribution est une violation du droit d'auteur.
2.  **Œuvres Dérivées** :
    - Si vous modifiez les *données* (ex: corriger un nom de rue), vous devez partager cela en retour.
    - Si vous ne faites que *styliser* les données (représentation visuelle), l'**œuvre artistique** est à vous, mais le crédit des **données sous-jacentes** reste obligatoire.
    - *Conclusion* : Les cartes stylisées de CityPaper sont des "Œuvres Produites". Nous possédons les droits du design, OSM possède les droits des données.

## 2. Spécifications d'Impression

### Mathématiques de la Résolution

Pour une impression "Fine Art" de haute qualité, le standard est **300 DPI** (Dots Per Inch / Points par pouce).

- **Affiche 50 x 70 cm** :
  - Pouces : ~19.7" x 27.6"
  - Pixels @ 300 DPI : **5906 x 8268 pixels**
  - Total Mégapixels : ~48.8 MP
- **Affiche 30 x 40 cm** :
  - Pixels @ 300 DPI : **3543 x 4724 pixels**

### Implications pour la Génération

- **Raster (PNG/JPG)** :
  - Générer une image de 49MP nécessite une RAM significative.
  - Taille de fichier : JPG ~10-20 Mo, PNG ~50-100 Mo.
- **Vecteur (PDF/SVG)** :
  - Préféré pour l'impression. Mise à l'échelle infinie.
  - *Défis* : `matplotlib` peut sortir du PDF/SVG, mais la taille du fichier peut être énorme si la carte a trop de détails (millions de segments de rue).
  - *Recommandation* : Commencer avec du **Raster Haute Résolution (PNG)** pour la simplicité. Cela garantit un rendu cohérent sur tous les appareils.

## 3. Sources de Données

### Primaire : OpenStreetMap (OSM)

- **Méthodes d'Accès** :
  - **API Overpass** : Bon pour les petites zones / requêtes en direct. Rate limited.
  - **Extraits Planet.osm / Geofabrik** : Mieux pour la génération en masse. Télécharger le `.pbf` pour "France", charger dans un outil local/DB (ex: `osmium` ou `PostGIS` sur le RPi).
  - *Recommandation* : Pour le worker RPi, récupérer les données via **Overpass** est le plus simple pour les requêtes "À la demande". Pour la "Collection Standard" (Top 50 villes), télécharger un extrait de pays est plus robuste.

## 4. Conclusion & Recommandations

1.  **Légal** : Ajouter "© OpenStreetMap contributors" en bas de chaque image générée. C'est non-négociable.
2.  **Qualité** : Viser **5906 x 8268 px** (50x70cm @ 300dpi) comme résolution "Master".
    - Fournir des versions réduites pour les Fonds d'écran (4K : 3840x2160).
3.  **Stockage** : Confirme le besoin de stockage externe (R2). 50 Mo par ville * 100 villes = 5 Go. Trop gros pour Git.

---

**Prochaines Étapes :**

- Passer à la Phase de Planification (PRD) pour définir les spécifications exactes du produit basées sur ces conclusions.
