# Mise à jour Git Automatique

**ID:** STORY-2.4
**Epic:** Epic 2
**Priority:** Must Have
**Story Points:** 3

## User Story

En tant que système
Je veux mettre à jour le fichier `data/cities.json` et commiter les changements
Afin que le nouveau contenu apparaisse sur le site sans action manuelle

## Acceptance Criteria

- [ ] Le script ajoute une entrée dans `data/cities.json` avec les URLs Hugging Face
- [ ] Le script effectue un `git commit` et `git push` vers le repo (uniquement `git commit` en mode dev puis on active `git push` une fois le script fonctionnelle)
- [ ] Cela déclenche un déploiement Vercel (via Webhook implicite)

## Technical Notes

- Utiliser `gitpython` ou subprocess pour les commandes git
- S'assurer que le token ou la clé SSH est configurée dans l'environnement du worker
- Le format JSON doit être respecté strictement
- Gérer les conflits éventuels (peu probables si worker unique)

## Dependencies

- Story 2.3 (Intégration Hugging Face) - pour avoir les URLs
- Story 2.1 (Script Python) - base du script

## Definition of Done

- [ ] Code complete
- [ ] Tests written and passing (mock git push)
- [ ] Code reviewed
- [ ] Documentation updated
- [ ] Deployed to dev/prod environment
