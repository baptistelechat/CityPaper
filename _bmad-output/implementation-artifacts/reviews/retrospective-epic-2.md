# Rétrospective Épic 2 - CityPaper

**Date:** 2026-02-04
**Épic:** 2 - Automation (Génération & Stockage)
**Statut:** Terminé
**Participants:** Baptiste (User), Trae (AI)

## 📊 Résumé
L'objectif de cet Épic était de mettre en place le pipeline de génération automatisée des cartes, leur stockage, et la mise à jour de la base de données.

*   **Total Story Points:** ~20 (Estimé)
*   **Stories complétées:** 4/4
*   **Délai:** Respecté

## 🟢 Ce qui a bien fonctionné (Keep doing)
*   **Pivot Stratégique Stockage :** Le remplacement de Cloudflare R2 par **Hugging Face Datasets** a été un succès majeur. Cela offre un stockage gratuit (~10GB+) et une API simple, sans carte de crédit.
*   **Pipeline de Génération :** L'utilisation d'OSMnx et Matplotlib permet de générer des cartes esthétiques avec un "cadrage intelligent" (Smart Framing) basé sur la géométrie des lieux.
*   **Automatisation Git :** Le worker est capable de mettre à jour `cities.json` et de déclencher un déploiement Vercel via un push Git automatique, fermant la boucle de production.
*   **Tests :** Bonne couverture de tests unitaires pour les parties critiques (DB, Git Ops).

## 🔴 Ce qui a moins bien fonctionné (Stop doing / Improve)
*   **Compatibilité Windows :** Quelques soucis d'encodage (Unicode) avec `subprocess` sous Windows, résolus en forçant l'encodage UTF-8.
*   **Deprecations Python :** Avertissements liés à `datetime.utcnow()` qui ont dû être corrigés en cours de route.
*   **Complexité de configuration :** La gestion des tokens (HF_TOKEN) et des clés SSH/HTTPS pour Git demande une attention particulière lors du déploiement.

## 💡 Idées d'amélioration (Start doing)
*   **Monitoring :** Surveiller la taille du fichier `cities.json` à mesure que le nombre de villes augmente.
*   **Optimisation :** La génération de cartes est séquentielle ; envisager la parallélisation si le volume augmente drastiquement.
*   **Sécurité :** S'assurer que les tokens ne fuient jamais dans les logs ou les commits (déjà géré via .env, mais à surveiller).

## 📝 Actions pour l'Épic 3
1.  [ ] Mettre en place la base de données Supabase pour gérer les demandes utilisateurs.
2.  [ ] Créer le formulaire de demande sur le Frontend.
3.  [ ] Connecter le Worker à Supabase pour traiter les demandes en attente (Polling).
