# Story 2.3: Intégration Cloudflare R2

**ID:** STORY-2.3
**Epic:** Epic 2: Usine de Cartes Automatisée
**Status:** Ready for Dev
**Priority:** High
**Story Points:** 3

## User Story

En tant que système,
Je veux uploader automatiquement les fichiers générés sur Cloudflare R2,
Afin de les rendre accessibles publiquement pour le téléchargement.

## Acceptance Criteria

- [ ] Étant donné des fichiers générés localement (PNG, PDF)
- [ ] Quand la génération est terminée
- [ ] Alors les fichiers sont envoyés sur le bucket R2
- [ ] Et les URLs publiques sont retournées par le script

## Technical Notes

- Utiliser une librairie compatible S3 (ex: `boto3` pour Python)
- Credentials via variables d'environnement (`R2_ENDPOINT`, `R2_ACCESS_KEY`, `R2_SECRET_KEY`)
- Structure des fichiers sur R2: `/{country}/{region}/{state}/{county}/{postcode}/{village}/{filename}` ou une structure mieux adapté
- Gérer les Content-Type corrects (image/png, application/pdf)

## Definition of Done

- [ ] Code implémenté dans le script de génération
- [ ] Upload fonctionnel vers R2
- [ ] Gestion des erreurs (ex: credentials invalides, réseau)
- [ ] Variables d'environnement configurées
