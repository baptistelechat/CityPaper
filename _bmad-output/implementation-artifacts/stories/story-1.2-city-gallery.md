# Story 1.2: Galerie des Villes (Homepage)

Status: completed

<!-- Note: La validation est optionnelle. Lancez validate-create-story pour un contrôle qualité avant dev-story. -->

## Story

En tant qu'utilisateur,
Je veux voir une grille de cartes minimalistes sur la page d'accueil,
Afin de découvrir les villes disponibles d'un coup d'œil.

## Acceptance Criteria

1. **Données**: Étant donné un fichier `data/cities.json` contenant des villes exemples (Paris, Lyon)
2. **Affichage**: Quand j'arrive sur la page d'accueil, alors je vois une grille de cartes
3. **Design Carte**: Chaque carte respecte le ratio 5:7 (Poster standard) et affiche l'image, le nom et le pays
4. **Responsive**: La grille s'adapte : 1 colonne (mobile), 2 colonnes (tablette), 3+ colonnes (desktop)
5. **Interaction**: Au survol d'une carte, l'image grossit légèrement (1.05x)

## Tâches / Sous-tâches

- [x] Créer les données mockées (AC: 1)
  - [x] Créer `src/data/cities.json` avec Paris et Lyon (images placeholder)
  - [x] Définir le type TypeScript `City`
- [x] Créer le composant Carte Ville (AC: 3, 5)
  - [x] Créer `src/components/city-card.tsx`
  - [x] Appliquer le ratio 5:7
  - [x] Ajouter l'effet de zoom au survol (Tailwind `hover:scale-105`)
- [x] Implémenter la Grille Homepage (AC: 2, 4)
  - [x] Modifier `src/app/page.tsx`
  - [x] Utiliser CSS Grid avec breakpoints Tailwind (`grid-cols-1 md:grid-cols-2 lg:grid-cols-3`)
  - [x] Charger les données depuis le JSON

## Notes de Développement

- **Composants** : Utiliser `shadcn/ui` Card si pertinent, ou une `div` simple pour un contrôle total du ratio.
- **Images** : Utiliser `next/image` avec `object-cover`. Pour les placeholders, utiliser des images libres (Unsplash ou placeholders locaux).
- **Responsive** : Utiliser les classes utilitaires Tailwind `grid` et `gap`.

## Dev Agent Record

### Agent Model Used

Trae AI (Gemini-3-Pro-Preview)

### Debug Log References

- None (Build successful on first attempt)

### Completion Notes List

- Implemented `CityCard` component with 5:7 aspect ratio and hover zoom effect.
- Created `src/data/cities.json` with mock data for Paris and Lyon.
- Defined `City` type in `src/types/city.ts`.
- Implemented responsive grid in `src/app/page.tsx` (1 col mobile, 2 cols tablet, 3 cols desktop).
- Verified build with `pnpm build`.
- [Refactor] Added `aria-label` to Search Input for accessibility.
- [Data] Updated `cities.json` with distinct and valid Unsplash images for all 9 cities (resolved redirects to avoid 403 errors).
- [Fix] Corrected Tailwind v4 syntax for aspect ratio in `CityCard`.

### File List

- src/data/cities.json
- src/types/city.ts
- src/components/city-card.tsx
- src/app/page.tsx
