# Story 1.3: Recherche et Filtrage Instantané

Status: done

<!-- Note: La validation est optionnelle. Lancez validate-create-story pour un contrôle qualité avant dev-story. -->

## Story

En tant qu'utilisateur,
Je veux filtrer la grille en tapant le nom d'une ville,
Afin de trouver rapidement si ma ville est disponible sans scroller.

## Acceptance Criteria

1. **Filtrage**: Étant donné une liste de villes affichée, Quand je tape "Pa" dans la barre de recherche, Alors seules les villes correspondant ("Paris", "Pau") restent affichées
2. **Instantaneité**: Le filtrage est instantané (côté client)
3. **Empty State**: Si aucune ville ne correspond, un message "Aucune ville trouvée" s'affiche

## Tâches / Sous-tâches

- [x] Ajouter le composant Input (AC: 1)
  - [x] Installer/Vérifier `shadcn/ui` Input (`npx shadcn@latest add input`)
  - [x] Ajouter un champ de recherche au-dessus de la grille dans `src/app/page.tsx`
- [x] Implémenter la logique de filtrage (AC: 1, 2)
  - [x] Ajouter un état `searchQuery` avec `useState`
  - [x] Filtrer la liste `cities` en fonction du nom (insensible à la casse)
- [x] Gérer l'état vide (AC: 3)
  - [x] Si la liste filtrée est vide, afficher un message centré "Aucune ville trouvée"

## Notes de Développement

- **Composants** : Utiliser le composant `Input` de `shadcn/ui`.
- **Performance** : Le filtrage côté client est suffisant pour < 100 villes. Pas besoin de debounce complexe pour l'instant.
- **UX** : Ajouter un placeholder explicite (ex: "Rechercher une ville...").
- **Accessibilité** : S'assurer que le champ a un label (visible ou `aria-label`).

## Dev Agent Record

### File List
- `src/components/city-catalog.tsx`
- `src/components/ui/input.tsx`

### Review Notes
- Tests unitaires ignorés sur demande utilisateur ("pas de test unitaire").
- Implémentation réalisée dans `CityCatalog` au lieu de `page.tsx` pour une meilleure encapsulation.
