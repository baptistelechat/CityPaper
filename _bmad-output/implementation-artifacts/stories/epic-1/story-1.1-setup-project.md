# Story 1.1: Setup du Projet et Design System

Status: completed

<!-- Note: La validation est optionnelle. Lancez validate-create-story pour un contrôle qualité avant dev-story. -->

## Story

En tant que développeur,
Je veux initialiser le projet Next.js avec Tailwind et shadcn/ui en suivant la charte graphique,
Afin d'avoir une base solide et cohérente pour construire les pages.

## Acceptance Criteria

1. **Environnement**: Étant donné un environnement de développement local Node.js
2. **Init**: Quand j'initialise le projet, alors Next.js 15, Tailwind 4 et shadcn/ui sont installés
3. **Polices**: La police "Inter" ou "Geist Sans" est configurée comme police par défaut
4. **Couleurs**: Les couleurs (Noir, Blanc, Gris-500) sont définies dans la config Tailwind
5. **Composants**: Le composant Bouton "Brutaliste" (Noir solide, carré) est créé

## Tâches / Sous-tâches

- [x] Initialiser le projet Next.js 15 (AC: 1, 2)
  - [x] Exécuter `pnpm create next-app@latest`
  - [x] Vérifier la structure
- [x] Installer et configurer Tailwind CSS 4 (AC: 2)
  - [x] Installer les dépendances (utiliser `pnpm`)
  - [x] Configurer `globals.css`
- [x] Installer et configurer shadcn/ui (AC: 2)
  - [x] Exécuter `pnpm dlx shadcn@latest init`
  - [x] Vérifier le dossier components
- [x] Configurer les polices et couleurs (AC: 3, 4)
  - [x] Ajouter la police Inter/Geist
  - [x] Mettre à jour la config Tailwind pour les couleurs
- [x] Créer le composant Bouton Brutaliste (AC: 5)
  - [x] Créer une variante ou un composant personnalisé `components/ui/button.tsx`
  - [x] Styler avec noir solide et coins carrés

## Notes de Développement

- **Architecture** : Structure Next.js 15 App Router.
- **Style** : Tailwind CSS v4 (vérifier la compatibilité avec shadcn/ui, peut nécessiter le mode compatibilité v3 ou une config spécifique).
- **Bibliothèque** : Utiliser l'installation standard shadcn/ui.

### Notes sur la Structure du Projet

- Alignement avec la structure de projet unifiée (chemins, modules, nommage).
- Suivre la convention de répertoire `src/` si préféré (défaut Next.js).

### Références

- [Source: _bmad-output/planning-artifacts/epics.md#Story 1.1: Setup du Projet et Design System]
- [Source: _bmad-output/planning-artifacts/docs/architecture-citypaper-2026-02-02.md]

## Dev Agent Record

### Agent Model Used

Trae AI (Gemini-3-Pro-Preview)

### Debug Log References

- Build passed successfully with Next.js 16.1.6 and React 19.2.3
- Tailwind 4 configured via CSS variables in globals.css

### Completion Notes List

- Validated environment: Node.js and pnpm present.
- Initialized Next.js project with App Router and TypeScript.
- Configured Tailwind CSS v4 with brutalist color scheme (Black/White).
- Configured Geist fonts in layout.tsx.
- Created Brutalist Button component (square corners, solid black).
- Validated build with `pnpm build`.

### File List

- src/app/layout.tsx
- src/app/globals.css
- src/components/ui/button.tsx
- package.json
