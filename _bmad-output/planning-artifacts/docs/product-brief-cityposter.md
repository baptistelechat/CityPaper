# Product Brief: CityPaper

**Date:** 2026-02-02
**Version:** 1.0
**Status:** Draft

## 1. Vision & Core Value

**CityPaper** transforme la donnée géographique brute en objets graphiques élégants et intemporels.
L'objectif est de créer une "bibliothèque visuelle de villes" accessible à tous, pensée pour la décoration d'intérieur (print) et numérique (wallpapers), loin de l'esthétique technique des cartes traditionnelles.

## 2. Le Problème

- Les cartes disponibles sont souvent soit trop techniques (OpenStreetMap, Google Maps), soit trop chères (services de posters personnalisés haut de gamme).
- La génération de cartes haute résolution à la demande est coûteuse en ressources serveur et complexe à maintenir à grande échelle.
- Manque d'outils simples pour obtenir des visuels cartographiques épurés sans compétences en design.

## 3. La Solution

Une plateforme de **génération asynchrone** de posters et wallpapers minimalistes.

- **Approche "Maker" & Low-Cost :** Utilisation d'un Raspberry Pi 5 comme worker de génération déporté.
- **Performance absolue :** Le site utilisateur est 100% statique (fichiers pré-générés).
- **Scalabilité "Humaine" :** Les demandes custom sont traitées en file d'attente sans impacter le site de production.

## 4. Cibles & Utilisateurs

- **Cible principale (B2C) :** Amateurs de design, décoration minimaliste, urbanisme. Personnes cherchant des fonds d'écran épurés ou des posters à imprimer soi-même.
- **Cible secondaire (B2B) :** Agences immobilières, boutiques locales, hôtels cherchant une décoration locale et stylisée.

## 5. Fonctionnalités Clés (MVP)

### A. Collection Standard (Le "Stock")

- **Top 50 Villes Françaises :** Disponibles immédiatement au téléchargement.
- **Formats multiples :** Wallpapers (Desktop/Mobile), Posters (A4/A3 PDF/PNG).
- **Styles prédéfinis :** issue de la configuration de `maptoposter`.

### B. Workflow Custom (La "Commande")

1.  **Formulaire de demande :** L'utilisateur saisit Ville + Style souhaité.
2.  **Confirmation visuelle :** Message "Demande prise en compte".
3.  **Traitement Asynchrone :**
    - Enregistrement dans une DB légère (Notion/GSheet/Supabase).
    - Le Raspberry Pi détecte la demande.
    - Génération du visuel via `maptoposter`.
    - Commit Git automatique du nouveau fichier.
4.  **Publication :** Rebuild automatique Vercel/Cloudflare. La ville devient disponible pour tous.

### C. Modèle Économique

- **Gratuit (Freemium) :** Téléchargement numérique gratuit pour tous.
- **Futur :** Vente de tirages papier (Print-on-demand).

## 6. Architecture Technique

- **Frontend/Hébergement :** Next.js / Vite (Statique) sur Vercel ou Cloudflare Pages.
- **Génération (Worker) :** Raspberry Pi 5 local ou hébergé.
- **Moteur :** Fork de `ankur/maptoposter`.
- **Base de données (Queue) :** Notion API, Google Sheets, ou Supabase.
- **Pipeline :** GitOps (Commit -> Deploy).

## 7. Critères de Succès

- **Fiabilité :** Le pipeline de génération -> publication fonctionne sans intervention humaine.
- **Qualité :** Les rendus sont esthétiques et lisibles quel que soit le niveau de zoom/ville.
- **Performance :** Score Lighthouse 100/100 (site statique).
