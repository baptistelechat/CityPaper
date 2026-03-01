# 🔑 Guide de Récupération des Clés API

Ce guide explique comment récupérer les clés nécessaires pour faire fonctionner le Worker de CityPaper.

## 1. Clé Supabase Service Role (Base de données)

Le Worker a besoin de droits d'écriture privilégiés pour mettre à jour les statuts des demandes, ce que la clé publique (`anon`) ne permet pas toujours selon les règles RLS.

1.  Allez sur votre tableau de bord [Supabase](https://supabase.com/dashboard/projects).
2.  Sélectionnez votre projet **CityPaper**.
3.  Allez dans **Project Settings** (l'icône d'engrenage tout en bas à gauche).
4.  Cliquez sur **API** dans le menu latéral.
5.  Dans la section **Project API keys**, vous verrez deux clés :
    - `anon` `public` (Celle que vous avez déjà)
    - `service_role` `secret` (Celle qu'il nous faut)
6.  Cliquez sur le bouton **Reveal** à côté de `service_role`.
7.  Copiez cette clé.
8.  Collez-la dans votre fichier `.env.local` :
    ```env
    SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    ```

⚠️ **Attention** : Cette clé donne un accès total à votre base de données. Ne la partagez jamais et ne la mettez jamais dans le code côté client (frontend).

## 2. URLs Supabase

Pour information, `NEXT_PUBLIC_SUPABASE_URL` et `SUPABASE_URL` doivent avoir la même valeur (l'URL de votre projet Supabase).

- `NEXT_PUBLIC_SUPABASE_URL` est utilisée par le Frontend (Next.js).
- `SUPABASE_URL` est utilisée par le Worker (Python).
