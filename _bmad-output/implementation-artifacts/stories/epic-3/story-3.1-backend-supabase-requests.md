# Backend Supabase (Table Requests)

**ID:** STORY-3.1
**Épic:** EPIC-3
**Priorité:** Must Have
**Story Points:** 2

## Récit Utilisateur (User Story)

En tant que développeur,
Je veux configurer Supabase avec une table `requests` sécurisée,
Afin de pouvoir stocker les demandes des utilisateurs en attente de traitement.

## Critères d'Acceptation

- [ ] Créer la table `requests` avec toutes les colonnes : `id`, `city`, ..., `email`, `status`, `metadata`
- [ ] Configurer les politiques RLS pour autoriser l'INSERT public (anonyme)
- [ ] Configurer les politiques RLS pour interdire le SELECT/UPDATE public
- [ ] Le script de migration est commité dans le dépôt

## Notes Techniques

- **Schéma de la Table :**
  - `id`: uuid, clé primaire, défaut `gen_random_uuid()`
  - `city`: text, non nul
  - `email`: text, nullable (optionnel)
  - `status`: text, défaut `'pending'` (enum/text : pending, processing, completed, error)
  - `metadata`: jsonb, défaut `{}` (stocke les options de cadrage, etc.)
  - `created_at`: timestamptz, défaut `now()`
  - Un maximum de donnée lié a l'api OSM pour avoir la requete de generation la plus complète possible

- **Politiques RLS :**
  - Activer la sécurité au niveau des lignes (RLS) sur la table `requests`.
  - **Politique 1 (Insert) :** Autoriser l'insertion publique.
    - Rôle : `anon`, `authenticated` (si applicable, mais probablement juste anon pour le formulaire public)
    - Vérification : `true` (ou valider l'entrée si possible)
  - **Politique 2 (Select/Update) :** Refuser l'accès public.
    - Le comportement par défaut est le refus si aucune politique n'existe.
    - Le rôle de service (utilisé par le Worker) contournera la RLS.

- **Outils :**
  - Utiliser les migrations Supabase (`supabase/migrations/YYYYMMDDHHMMSS_create_requests_table.sql`).
  - Ou utiliser `mcp_supabase` pour appliquer si le fichier de migration est géré différemment.

## Dépendances

- Configuration du projet Supabase (supposée).

## Définition de Fini (DoD)

- [ ] Fichier de migration créé dans `supabase/migrations/`
- [ ] Migration appliquée au projet Supabase
- [ ] Politiques RLS vérifiées (insertion possible, sélection impossible)
