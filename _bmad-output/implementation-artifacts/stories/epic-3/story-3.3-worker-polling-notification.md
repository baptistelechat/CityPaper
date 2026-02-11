# Story 3.3 : Polling du Worker & Notification Email

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

En tant que Système,
Je veux que le Worker traite les demandes en attente et notifie l'utilisateur,
Afin de boucler la boucle d'interaction et que les utilisateurs reçoivent leurs cartes demandées.

## Critères d'Acceptation

1.  **Mécanisme de Polling** : Le worker sonde la table `requests` de Supabase pour les entrées avec `status: 'pending'`.
2.  **Traitement FIFO** : Il traite les demandes dans l'ordre Premier-Entré-Premier-Sorti (le plus ancien `created_at` en premier).
3.  **Déclenchement de la Génération** : Pour chaque demande en attente, il déclenche le processus de génération de carte (utilisant la logique de l'Épic 2).
4.  **~~Notification par Email~~** : (Annulé) La fonctionnalité d'email a été retirée (décision produit).
5.  **Mises à jour de Statut** d'abord `updated_at` puis :
    - Met à jour le statut à `processing` au démarrage.
    - Met à jour le statut à `completed` une fois terminé avec succès.
    - Met à jour le statut à `failed` si des erreurs de génération surviennent.
6.  **Gestion des Erreurs** : Le worker ne doit pas planter sur un seul échec mais le journaliser et passer à la demande suivante (après l'avoir marquée comme échouée).

## Tâches / Sous-tâches

- [ ] **Configuration de l'Intégration Resend**
  - [ ] Obtenir la clé API Resend et l'ajouter au `.env` sur le Worker (RPi).
  - [ ] Installer le paquet Python `resend` (ou utiliser `requests`).
  - [ ] Créer la fonction `send_notification_email(to_email, city_name, city_url)`.

- [ ] **Implémenter la Logique de Polling**
  - [ ] Créer la fonction `poll_requests()` dans `worker/src/db.py` ou `worker/src/main.py`.
  - [ ] Requêter Supabase pour `status='pending'` trié par `created_at` ASC limite 1.
  - [ ] Mettre à jour le statut à `processing`.

- [ ] **Intégrer le Pipeline de Génération**
  - [ ] Extraire nom de ville/pays/métadonnées de la demande.
  - [ ] Appeler les fonctions de génération existantes (`generate_map`, `upload_to_r2`).

- [ ] **Finaliser la Boucle de Demande**
  - [ ] En cas de succès : Mettre à jour le statut Supabase à `completed` et envoyer l'email.
  - [ ] En cas d'échec : Capturer les exceptions, mettre à jour le statut Supabase à `failed`, et journaliser l'erreur.
  - [ ] Implémenter un intervalle de veille (ex: 60s) entre les sondages si aucune demande n'est trouvée.

## Notes de Développement

- **Modèles d'Architecture** :
  - **Worker** : Sondage sortant uniquement (Section 6).
  - **Supabase** : Utiliser la table `requests` définie dans la Story 3.1.
  - **Resend** : Service d'email transactionnel standard.
- **Arborescence Source** :
  - `worker/src/` : Logique python principale.
  - `worker/src/db.py` : Interactions base de données.
  - `worker/src/notify.py` : (Nouveau) Logique email.

### Notes sur la Structure du Projet

- S'assurer que les dépendances Python (`resend`, `supabase`) sont dans `worker/requirements.txt`.
- Garder le worker sans état concernant la file d'attente (Supabase est la source de vérité).

### Références

- [Document d'Architecture : 2.1 Flux de Données](file:///c:/Users/DM/Desktop/DEV/perso/CityPaper/_bmad-output/planning-artifacts/docs/architecture-citypaper-2026-02-02.md#21-flux-de-données-haut-niveau)
- [Document d'Architecture : 4.1 Schéma Base de Données](file:///c:/Users/DM/Desktop/DEV/perso/CityPaper/_bmad-output/planning-artifacts/docs/architecture-citypaper-2026-02-02.md#41-schéma-de-base-de-données-supabase)
- [Structure Table Supabase](file:///c:/Users/DM/Desktop/DEV/perso/CityPaper/_bmad-output/planning-artifacts/epics.md#story-31-backend-supabase-requests)

## Enregistrement Agent Dev

### Modèle d'Agent Utilisé

Gemini-3-Pro-Preview (via Trae)

### Références Logs Debug

N/A

### Notes de Complétion

- [ ] Confirmé que la clé API Resend fonctionne.
- [ ] Confirmé que la boucle de polling récupère les demandes.
- [ ] Confirmé les transitions de statut dans Supabase.

### Liste de Fichiers

- `worker/src/main.py`
- `worker/src/notify.py` (Nouveau)
- `worker/requirements.txt`
