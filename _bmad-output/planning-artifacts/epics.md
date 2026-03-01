---
stepsCompleted:
  - step-01-validate-prerequisites
  - step-02-design-epics
inputDocuments:
  - _bmad-output/planning-artifacts/docs/prd-cityposter.md
  - _bmad-output/planning-artifacts/docs/architecture-citypaper-2026-02-02.md
  - _bmad-output/planning-artifacts/ux-design-cityposter.md
---

# CityPaper - Découpage en Épics

## Vue d'Ensemble

Ce document présente le découpage complet en épics et user stories pour CityPaper, décomposant les exigences du PRD, du Design UX et de l'Architecture en stories implémentables.

## Inventaire des Exigences

### Exigences Fonctionnelles

FR1: [Frontend] Galerie filtrable et recherchable des villes disponibles (Top 50 FR initialement).
FR2: [Frontend] Pages détails ville avec prévisualisation (Zoom 1.05x au survol) et boutons de téléchargement (PDF/PNG, Wallpaper).
FR3: [Frontend] Formulaire de demande "Custom" (Ville, Pays, Email optionnel) stocké dans Supabase.
FR4: [Frontend] Affichage du statut des demandes ou notification par email (flux asynchrone).
FR5: [Backend] Script Worker (Python/RPi) surveillant la file d'attente Supabase.
FR6: [Backend] Génération de la carte via `maptoposter` avec gestion des erreurs (timeout OSM).
FR7: [Backend] Upload des assets générés sur Cloudflare R2.
FR8: [Backend] Mise à jour du fichier `data/cities.json` et commit automatique sur Git.
FR9: [Infra] Rebuild automatique du site statique sur commit du Worker (Webhook Vercel).

### Exigences Non-Fonctionnelles

NFR1: [Performance] Score Lighthouse > 95, chargement instantané (SSG).
NFR2: [Coût] Architecture optimisée pour le coût zéro (Vercel Hobby, Cloudflare R2 Free, Supabase Free).
NFR3: [Fiabilité] Le worker doit gérer les erreurs réseau/OSM sans planter (mécanisme de retry).
NFR4: [Accessibilité] Conformité WCAG 2.1 AA, contraste élevé, navigation clavier, alt text.
NFR5: [Responsive] Mobile (1 col), Tablette (2 col), Desktop (3-4 col).

### Exigences Supplémentaires

- [Architecture] Stack: Next.js 15, Tailwind 4, shadcn/ui, Supabase, Cloudflare R2, Python 3.11+.
- [Architecture] Données: Table Supabase `requests` pour la file d'attente, `data/cities.json` pour le contenu site.
- [Architecture] Sécurité: Supabase RLS pour les demandes, Worker en outbound-only.
- [UX] Design minimaliste/monochrome ("Galerie d'abord").
- [UX] Ratio des cartes 5:7 (Poster standard).
- [UX] Typographie: Inter ou Geist Sans.
- [UX] Boutons "Brutalistes" (Noir solide, coins carrés).

### Carte de Couverture des FR

FR1: Épic 1 - Galerie & Recherche
FR2: Épic 1 - Détail & Téléchargement (Formats Pros)
FR3: Épic 3 - Formulaire Custom (Options Cadrage)
FR4: Épic 3 - Notification Email (Resend)
FR5: Épic 3 - Worker Queue Processing
FR6: Épic 2 - Génération Carte (Auto-Cadrage)
FR7: Épic 2 - Upload R2
FR8: Épic 2 - Update Git/JSON
FR9: Épic 2 - Trigger Rebuild

## Liste des Épics

### Épic 1 : Expérience Galerie & Téléchargement (MVP Frontend)
Mettre en ligne la "vitrine" du projet pour que les utilisateurs puissent parcourir, rechercher et télécharger des cartes de haute qualité (PDF Vectoriel/PNG 300dpi) instantanément.
**FRs couverts :** FR1, FR2, FR9 (Setup), NFR1, NFR4, NFR5

### Épic 2 : Usine de Cartes Automatisée (Core Backend)
Industrialiser la création de contenu via un Worker autonome qui génère les cartes (avec cadrage intelligent), les héberge sur R2 et met à jour le site, remplaçant l'ajout manuel.
**FRs couverts :** FR6, FR7, FR8, FR9 (Trigger), NFR2, NFR3

### Épic 3 : Système de Demandes & Boucle de Notification
Rendre la plateforme interactive en permettant aux utilisateurs de demander des villes spécifiques (avec préférences de cadrage) et d'être notifiés proactivement par email (via Resend) lors de la disponibilité.
**FRs couverts :** FR3, FR4, FR5

## Épic 1: Expérience Galerie & Téléchargement (MVP Frontend)

**Objectif :** Mettre en ligne la "vitrine" du projet pour que les utilisateurs puissent parcourir, rechercher et télécharger des cartes de haute qualité (PDF Vectoriel/PNG 300dpi) instantanément.

### Story 1.1: Setup du Projet et Design System

En tant que développeur,
Je veux initialiser le projet Next.js avec Tailwind et shadcn/ui en suivant la charte graphique,
Afin d'avoir une base solide et cohérente pour construire les pages.

**Critères d'Acceptation :**

**Étant donné** un environnement de développement local Node.js
**Quand** j'initialise le projet
**Alors** Next.js 15, Tailwind 4 et shadcn/ui sont installés
**Et** la police "Inter" ou "Geist Sans" est configurée comme police par défaut
**Et** les couleurs (Noir, Blanc, Gris-500) sont définies dans la config Tailwind
**Et** le composant Bouton "Brutaliste" (Noir solide, carré) est créé

### Story 1.2: Galerie des Villes (Homepage)

En tant qu'utilisateur,
Je veux voir une grille de cartes minimalistes sur la page d'accueil,
Afin de découvrir les villes disponibles d'un coup d'œil.

**Critères d'Acceptation :**

**Étant donné** un fichier `data/cities.json` contenant quelques villes exemples (Paris, Lyon)
**Quand** j'arrive sur la page d'accueil
**Alors** je vois une grille de cartes (Ratio 5:7) avec l'image, le nom et le pays
**Et** la grille est responsive (1 col mobile, 2 col tablette, 3+ desktop)
**Et** au survol d'une carte, l'image grossit légèrement (1.05x)

### Story 1.3: Recherche et Filtrage Instantané

En tant qu'utilisateur,
Je veux filtrer la grille en tapant le nom d'une ville,
Afin de trouver rapidement si ma ville est disponible sans scroller.

**Critères d'Acceptation :**

**Étant donné** une liste de villes affichée
**Quand** je tape "Pa" dans la barre de recherche
**Alors** seules les villes correspondant ("Paris", "Pau") restent affichées
**Et** le filtrage est instantané (côté client)
**Et** si aucune ville ne correspond, un message "Aucune ville trouvée" s'affiche

### Story 1.4: Page Détail Ville et Téléchargement

En tant que visiteur (Pro ou Amateur),
Je veux voir les détails d'une ville et télécharger les fichiers haute définition,
Afin d'imprimer un poster ou de changer mon fond d'écran.

**Critères d'Acceptation :**

**Étant donné** que je clique sur une carte dans la galerie
**Quand** j'arrive sur la page détail `/city/[slug]`
**Alors** je vois un grand aperçu de la carte
**Et** je vois deux boutons de téléchargement distincts : "Télécharger PDF (Print)" et "Télécharger Wallpaper"
**Et** les liens pointent vers les URLs R2 définies dans le JSON

## Épic 2: Usine de Cartes Automatisée (Core Backend)

**Objectif :** Industrialiser la création de contenu via un Worker autonome qui génère les cartes (avec cadrage intelligent), les héberge sur R2 et met à jour le site, remplaçant l'ajout manuel.

### Story 2.1: Script Python de Génération (Base)

En tant que développeur,
Je veux un script Python capable de générer une carte minimaliste à partir du nom d'une ville,
Afin d'automatiser la création des visuels.

**Critères d'Acceptation :**

**Étant donné** un environnement Python avec `maptoposter` ou `osmnx`
**Quand** j'exécute le script avec "Lyon" en entrée
**Alors** un fichier PNG haute résolution et un PDF vectoriel sont générés localement
**Et** le style de la carte respecte le thème (Noir & Blanc, Minimaliste)

### Story 2.2: Cadrage Intelligent (Bounding Box)

En tant que créateur de contenu,
Je veux que le script cadre automatiquement la ville avec une marge esthétique,
Afin d'éviter les cartes coupées ou mal centrées sans intervention manuelle.

**Critères d'Acceptation :**

**Étant donné** le script de génération
**Quand** je demande une ville (ex: "Paris")
**Alors** le script récupère la "Bounding Box" administrative via OSM
**Et** il applique un padding (marge) de ~10% autour
**Et** la carte générée montre la ville entière centrée

### Story 2.3: Intégration Cloudflare R2

En tant que système,
Je veux uploader automatiquement les fichiers générés sur Cloudflare R2,
Afin de les rendre accessibles publiquement pour le téléchargement.

**Critères d'Acceptation :**

**Étant donné** des fichiers générés localement (PNG, PDF)
**Quand** la génération est terminée
**Alors** les fichiers sont envoyés sur le bucket R2
**Et** les URLs publiques sont retournées par le script

### Story 2.4: Mise à jour Git Automatique

En tant que système,
Je veux mettre à jour le fichier `data/cities.json` et commiter les changements,
Afin que le nouveau contenu apparaisse sur le site sans action manuelle.

**Critères d'Acceptation :**

**Étant donné** une nouvelle ville générée et uploadée
**Quand** le processus est fini
**Alors** le script ajoute une entrée dans `data/cities.json` avec les URLs R2
**Et** le script effectue un `git commit` et `git push` vers le repo
**Et** cela déclenche un déploiement Vercel (via Webhook implicite)

## Épic 3: Système de Demandes & Boucle de Notification

**Objectif :** Rendre la plateforme interactive en permettant aux utilisateurs de demander des villes spécifiques (avec préférences de cadrage) et d'être notifiés proactivement par email (via Resend) lors de la disponibilité.

### Story 3.1: Backend Supabase (Table Requests)

En tant que développeur,
Je veux configurer Supabase avec une table `requests` sécurisée,
Afin de stocker les demandes des utilisateurs en attente de traitement.

**Critères d'Acceptation :**

**Étant donné** un projet Supabase
**Quand** j'exécute le script de migration
**Alors** la table `requests` est créée avec les colonnes (id, city, email, status, metadata)
**Et** les politiques RLS permettent l'INSERT public (anonyme) mais interdisent le SELECT/UPDATE public

### Story 3.2: Formulaire de Demande (Frontend)

En tant qu'utilisateur,
Je veux demander une ville qui n'existe pas via un formulaire,
Afin qu'elle soit ajoutée à la file d'attente de génération.

**Critères d'Acceptation :**

**Étant donné** qu'une recherche ne donne aucun résultat
**Quand** je clique sur "Demander cette ville"
**Alors** un formulaire s'ouvre (Ville, Email optionnel)
**Et** je peux choisir une option "Vue" (Centre-ville vs Agglomération)
**Et** à la soumission, la demande est enregistrée dans Supabase avec le statut "pending"

### Story 3.3: Worker Polling & Notification Email

En tant que système,
Je veux que le Worker traite les demandes en attente et notifie l'utilisateur,
Afin de boucler la boucle d'interaction.

**Critères d'Acceptation :**

**Étant donné** des demandes en statut "pending" dans Supabase
**Quand** le Worker Python s'exécute
**Alors** il récupère la plus ancienne demande
**Et** il lance la génération (Épic 2) avec les paramètres demandés
**Et** si un email est présent, il envoie un message via l'API Resend avec le lien vers la nouvelle page ville
**Et** il met à jour le statut de la demande à "completed"
