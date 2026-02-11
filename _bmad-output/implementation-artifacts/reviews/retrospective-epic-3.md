# Rétrospective Épic 3 - CityPaper

**Date:** 2026-02-11
**Épic:** 3 - Système de Demandes & Boucle de Notification
**Statut:** Terminé
**Participants:** Baptiste (User), Trae (AI)

## 📊 Résumé
L'objectif de cet Épic était de rendre la plateforme interactive en permettant aux utilisateurs de demander des villes spécifiques et d'automatiser leur traitement via le worker Python et Supabase.

*   **Total Story Points:** ~15 (Estimé)
*   **Stories complétées:** 3/3
*   **Délai:** Respecté

## 🟢 Ce qui a bien fonctionné (Keep doing)
*   *Intégration fluide de Supabase (Database & Auth) pour gérer la file d'attente.*
*   *Le script Python du worker s'intègre bien avec la logique de génération de cartes existante.*
*   *Le formulaire frontend est simple et efficace, respectant le design system.*
*   *La sécurité via RLS assure que les demandes sont protégées.*

## 🔴 Ce qui a moins bien fonctionné (Stop doing / Improve)
*   *La fonctionnalité de notification par email a été annulée en cours de route, ce qui simplifie le scope mais réduit l'interaction utilisateur.*
*   *La gestion des erreurs réseau (OSM timeouts) dans le worker nécessite une surveillance continue.*

## 💡 Idées d'amélioration (Start doing)
*   *Ajouter un dashboard admin pour visualiser les demandes en attente et les erreurs.*
*   *Réévaluer l'intégration email dans une phase future si la demande utilisateur le justifie.*
*   *Optimiser le temps de génération des cartes pour réduire le délai d'attente utilisateur.*

## 📝 Actions Suivantes
1.  [ ] Surveiller les logs du worker en production pour identifier les edge cases.
2.  [ ] Envisager une migration vers une architecture serverless complète si le worker local devient une contrainte.
3.  [ ] Préparer le lancement officiel !
