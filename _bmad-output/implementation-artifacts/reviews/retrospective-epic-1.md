# Rétrospective Épic 1 - CityPaper

**Date:** 2026-02-03
**Épic:** 1 - Vitrine (MVP Frontend)
**Statut:** Terminé
**Participants:** Baptiste (User), Trae (AI)

## 📊 Résumé
L'objectif de cet Épic était de lancer la "Vitrine" (MVP Frontend) pour permettre la visualisation et le filtrage des posters de villes.

*   **Total Story Points:** 15
*   **Stories complétées:** 4/4
*   **Délai:** Respecté

## 🟢 Ce qui a bien fonctionné (Keep doing)
*   *Mise en place rapide de la stack technique (Next.js 15, Tailwind 4, Shadcn).*
*   *L'approche modulaire avec les composants UI a facilité l'assemblage des pages.*
*   *Le système de mock data (cities.json) a permis d'avancer sans backend.*
*   *La recherche instantanée côté client est fluide et réactive.*

## 🔴 Ce qui a moins bien fonctionné (Stop doing / Improve)
*   *Pas de bloquants majeurs, mais le switch de contexte vers Python pour l'Épic 2 demandera une bonne configuration initiale.*
*   *Les données mockées (JSON) devront être migrées vers une structure plus robuste.*

## 💡 Idées d'amélioration (Start doing)
*   *Préparer les types TypeScript pour l'intégration future avec le backend Python.*
*   *Ajouter des tests unitaires pour les composants critiques (ex: logique de filtrage).*
*   *Documenter l'API attendue entre le front et le script Python.*

## 📝 Actions pour l'Épic 2
1.  [ ] Initialiser l'environnement Python pour la génération de cartes.
2.  [ ] Définir le format exact des données échangées entre le script Python et le frontend.
