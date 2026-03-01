# Story 1.4: Page Détail Ville et Téléchargement

Status: done

<!-- Note: La validation est optionnelle. Lancez validate-create-story pour un contrôle qualité avant dev-story. -->

## Story

En tant qu'utilisateur,
Je veux cliquer sur une ville pour voir son poster en grand et pouvoir le télécharger,
Afin de l'imprimer ou de le sauvegarder.

## Acceptance Criteria

1. **Navigation**: En cliquant sur une carte dans la galerie, je suis redirigé vers une page de détail (ex: `/city/paris`).
2. **Affichage**: La page affiche le poster en grand format (haute qualité visuelle).
3. **Téléchargement**: Des boutons "Télécharger" sont présents (ex: PDF, PNG). Pour le MVP, ces liens peuvent pointer vers des fichiers statiques ou des placeholders.
4. **Retour**: Un bouton "Retour à la galerie" permet de revenir à la liste sans perdre le contexte.
5. **SEO/Titre**: Le titre de la page reflète la ville (ex: "Paris - CityPaper").

## Tâches / Sous-tâches

- [x] Créer la route dynamique (AC: 1, 5)
  - [x] Créer `src/app/city/[id]/page.tsx` (utiliser `id` comme slug).
  - [x] Importer `cities` depuis `@/data/cities.json`.
  - [x] Implémenter `generateStaticParams` pour le rendu statique (SSG) de toutes les villes connues.
  - [x] Gérer le cas "Ville non trouvée" (notFound()).
- [x] UI Page Détail (AC: 2, 4)
  - [x] Layout responsive : Image à gauche (ou haut mobile), infos et actions à droite (ou bas mobile).
  - [x] Afficher l'image en grand avec `next/image` (priority=true).
  - [x] Bouton "Retour" (Link vers `/`).
- [x] Actions de Téléchargement (AC: 3)
  - [x] Boutons "Télécharger PDF" et "Télécharger JPG" (shadcn Button).
  - [x] Mock : Liens vers l'URL de l'image (ou `#`) avec attribut `download` si possible.
- [x] Mettre à jour `CityCard` (AC: 1)
  - [x] Envelopper la carte ou ajouter un lien vers `/city/[id]`.

## Notes de Développement

- **Routing** : Utiliser `[id]` car c'est la clé dans `cities.json`.
- **SSG** : Comme on a un fichier JSON statique, `generateStaticParams` est recommandé pour la performance.
- **Images** : Attention au layout shift, définir width/height ou fill.
- **UI** : Réutiliser le style "minimaliste".

## Dev Agent Record

### File List

- `src/app/city/[id]/page.tsx`
- `src/components/city-card.tsx`

### Review Notes

Implemented city detail page with SSG, responsive layout, download buttons (mock), and back navigation. Updated CityCard to link to detail page.
Verified build with `pnpm build` (Next.js 16.1.6).
