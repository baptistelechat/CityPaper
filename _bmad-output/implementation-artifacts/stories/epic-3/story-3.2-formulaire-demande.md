# Story 3.2: Formulaire de Demande (Frontend)

Status: ready-for-dev

<!-- Note: La validation est optionnelle. Exécutez validate-create-story pour un contrôle qualité avant dev-story. -->

## Story (Récit Utilisateur)

En tant qu'**Utilisateur**,
Je veux **demander une ville qui n'existe pas via un formulaire**,
Afin qu'**elle soit ajoutée à la file d'attente de génération**.

## Critères d'Acceptation

1. **Condition de Déclenchement :**
   - Afficher un bouton/CTA "Demander cette ville" lorsque la recherche ne donne aucun résultat.
   - Alternativement, fournir un bouton "Demander une ville" persistant dans l'UI (ex: pied de page ou en-tête).

2. **Interface du Formulaire :**
   - Le clic sur le bouton ouvre un formulaire (Dialog ou vue dédiée).
   - **Champs :**
     - Code Postal (Requis)
     - Nom de la ville (Requis)
     - Pays (Requis)
     - Un select avec les réponses de l'API OSM qui rempli automatiquement d'autres champs en mode disable (county, state) afin de remplir toute les collones de Supabase et avoir la requete la plus complète possible
     - Email (Optionnel, pour notification)

3. **Gestion de la Soumission :**
   - À la soumission, valider les entrées avec Zod.
   - Appeler une Server Action pour insérer les données dans la table Supabase `requests`.
   - Le statut par défaut est "pending".
   - Le champ `metadata` stocke la Préférence de vue.

4. **Retour & Gestion des Erreurs :**
   - Afficher un état de chargement pendant la soumission.
   - Afficher un message de succès ("Demande envoyée ! Vous serez notifié si vous avez fourni un email.") en cas de réussite.
   - Gérer les erreurs gracieusement (ex: problèmes réseau) avec une notification toast.

## Tâches / Sous-tâches

- [ ] **Tâche 1 : Configuration Schéma de Validation & Server Action** (CA: #3)
  - [ ] Définir le schéma Zod pour le formulaire de demande (`city`, `country`, `email`, `view_preference`).
  - [ ] Créer la Server Action `submitCityRequest` dans `app/actions/requests.ts` (ou similaire).
  - [ ] Implémenter la logique d'insertion Supabase en utilisant le client Supabase.
  - [ ] S'assurer que le JSONB `metadata` est correctement construit à partir des champs du formulaire.

- [ ] **Tâche 2 : Créer le Composant Formulaire de Demande** (CA: #2, #4)
  - [ ] Créer `components/request-city-dialog.tsx` en utilisant shadcn/ui `Dialog`, `Form`, `Input`, `Select`/`RadioGroup`.
  - [ ] Implémenter la logique du formulaire avec `react-hook-form` et le résolveur `zod`.
  - [ ] Connecter la soumission du formulaire à la Server Action.
  - [ ] Implémenter les notifications toast pour les états succès/erreur.

- [ ] **Tâche 3 : Intégrer dans l'UI** (CA: #1)
  - [ ] Localiser l'état "Aucun résultat" dans le composant Grille de Ville/Recherche.
  - [ ] Ajouter le bouton CTA "Demander cette ville" ou similaire.
  - [ ] Connecter le bouton pour ouvrir le `RequestCityDialog`.

## Notes de Développement

- **Modèles d'Architecture :**
  - Utiliser les **Server Actions** pour la soumission du formulaire afin de garder le bundle client léger et gérer les secrets/accès DB de manière sécurisée.
  - Utiliser les composants **Shadcn UI** pour la cohérence (Dialog, Form, Input, Button).
  - Utiliser **Zod** pour la validation côté client et côté serveur.

- **Intégration Supabase :**
  - La table `requests` existe déjà (Story 3.1).
  - Les politiques RLS autorisent l'`INSERT` public. Aucune authentification requise pour l'utilisateur.
  - Utiliser `createClient` de `@supabase/ssr` ou le helper client configuré du projet.

- **Considérations UX :**
  - Le formulaire doit être simple et rapide.

### Notes sur la Structure du Projet

- **Composants :** Placer dans `components/` (ex: `components/request-city-form.tsx`).
- **Actions :** Placer les Server Actions dans `app/actions.ts` ou un répertoire dédié `app/actions/` si établi.
- **Lib :** Les schémas Zod peuvent aller dans `lib/validations.ts` ou à côté de l'action/composant si spécifique.

### Références

- [Document d'Architecture](file:///c%3A/Users/DM/Desktop/DEV/perso/CityPaper/_bmad-output/planning-artifacts/docs/architecture-citypaper-2026-02-02.md#41-schéma-de-base-de-données-supabase)
- [Story 3.1](file:///c%3A/Users/DM/Desktop/DEV/perso/CityPaper/_bmad-output/implementation-artifacts/stories/epic-3/story-3.1-backend-supabase-requests.md) (Schéma de Table)

## Dev Agent Record

### Agent Model Used

Trae AI (Gemini-3-Pro-Preview)

### Completion Notes List

- S'appuie sur la configuration Supabase existante de la Story 3.1.
- Se concentre sur l'implémentation Frontend (Next.js/React).

### File List

- `components/request-city-dialog.tsx` (Nouveau)
- `app/actions/submit-request.ts` (Nouveau/Modifié)
- `components/city-grid.tsx` (Modifié)
- `lib/validations/request.ts` (Nouveau - optionnel, ou inline)
