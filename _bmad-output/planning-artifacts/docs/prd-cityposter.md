# Product Requirements Document - CityPaper

**Date:** 2026-02-02
**Status:** Draft

## 1. Introduction

CityPaper est une plateforme de distribution de posters et wallpapers de cartes minimalistes. Le projet vise à offrir une alternative esthétique et gratuite aux cartes techniques, avec une architecture optimisée pour le coût et la performance (Génération asynchrone sur RPi, hébergement statique).

## 2. User Personas

- **L'Amateur de Design (Primary):** Cherche une déco murale ou un fond d'écran épuré. Veut du "beau" immédiat sans configuration complexe.
- **Le Professionnel (Secondary):** Agent immobilier ou commerçant voulant une carte stylisée de son quartier.

## 3. User Stories

- **US-01 (Browse):** En tant qu'utilisateur, je veux parcourir une galerie de villes populaires (Top 50 FR) pour trouver une carte qui me plaît.
- **US-02 (Download):** En tant qu'utilisateur, je veux télécharger gratuitement la carte en haute définition (PDF/PNG) ou en format wallpaper.
- **US-03 (Request Custom):** En tant qu'utilisateur, je veux demander une ville spécifique non listée, en remplissant un formulaire simple.
- **US-04 (Track Custom):** En tant qu'utilisateur, je veux être notifié (ou voir sur le site) quand ma demande a été traitée.

## 4. Functional Requirements

### F-01: Frontend (Public)

- **F-01-A:** Galerie filtrable/recherchable des villes disponibles.
- **F-01-B:** Pages détails ville avec prévisualisation et boutons de téléchargement.
- **F-01-C:** Formulaire de demande "Custom" (Ville, Style).

### F-02: Backend (Worker & Generation)

- **F-02-A:** Script de surveillance de la base de demandes (Notion/Supabase).
- **F-02-B:** Génération de la carte via `maptoposter` (Python).
- **F-02-C:** Commit automatique des assets générés dans le repo Git.

### F-03: Infrastructure & Data

- **F-03-A:** Hébergement statique (Vercel/Cloudflare).
- **F-03-B:** Rebuild automatique sur commit du Worker.

## 5. Non-Functional Requirements

- **NF-01 (Performance):** Score Lighthouse > 95. Chargement instantané (Statique).
- **NF-02 (Cost):** Coût d'hébergement proche de zéro (Tier gratuit).
- **NF-03 (Reliability):** Le worker RPi doit gérer les erreurs (timeout OSM) et réessayer sans planter.

## 6. Epics

- **E-01:** Mise en place Pipeline & Worker (Le coeur du système).
- **E-02:** Frontend Galerie & Téléchargement (Le MVP public).
- **E-03:** Gestion des Demandes Custom (Le flux asynchrone).
