# Document de Design UX - CityPaper

**Date :** 02/02/2026
**Statut :** Brouillon
**Rôle :** UX Designer

## 1. Stratégie de Design

### Philosophie Centrale

**"La galerie d'abord, l'outil ensuite."**
L'interface doit ressembler à une galerie d'art : calme, spacieuse et centrée sur le contenu visuel. Les éléments de l'interface utilisateur (UI) doivent être discrets, utilisant une palette monochrome stricte pour laisser les designs de cartes se démarquer.

### Public Cible

- **Les Amateurs de Design :** Recherchent une esthétique de haute qualité, sans friction.
- **Les Professionnels :** Veulent des fichiers fiables et imprimables.

### Standards d'Accessibilité

- **Conformité :** WCAG 2.1 AA.
- **Focus :** Contraste élevé (Noir & Blanc strict), états de focus clairs, HTML sémantique pour les lecteurs d'écran (vital pour les sites riches en images).

---

## 2. Flux Utilisateurs (User Flows)

### Flux 1 : Découverte & Téléchargement (Le "Happy Path")

**But :** L'utilisateur trouve une ville spécifique et la télécharge.

1.  **Arrivée :** L'utilisateur arrive sur l'Accueil.
2.  **Recherche :** L'utilisateur tape "Lyon" dans la barre de recherche (ou parcourt la grille).
3.  **Sélection :** L'utilisateur clique sur la carte "Lyon".
4.  **Aperçu :** L'utilisateur voit la vue détaillée avec un aperçu haute résolution.
5.  **Action :** L'utilisateur clique sur "Télécharger PDF (Impression)".
6.  **Résultat :** Le fichier se télécharge immédiatement. Pas d'inscription, pas de paiement.

### Flux 2 : Demande Personnalisée (Le Flux Asynchrone)

**But :** L'utilisateur veut une ville qui n'existe pas encore.

1.  **Échec Recherche :** L'utilisateur cherche "Saint-Glinglin".
2.  **État Vide :** Le résultat affiche "Aucune carte trouvée pour 'Saint-Glinglin'".
3.  **CTA :** Le bouton "Demander cette Ville" apparaît.
4.  **Formulaire :** L'utilisateur entre le Nom de la Ville (pré-rempli) et son Email (optionnel).
5.  **Confirmation :** "Demande ajoutée à la file d'attente ! Nous vous notifierons quand elle sera prête (~24h)."
6.  **Boucle Asynchrone :** (Système génère la carte -> Site se met à jour) -> L'utilisateur reçoit un lien par email.

---

## 3. Plan du Site (Sitemap)

1.  **Accueil (/)**
    - Section Hero
    - Recherche/Filtre
    - Grille Galerie
    - "Demander une ville" (Action flottante ou lien pied de page)
2.  **Détail Ville (/city/[slug])**
    - Grand Aperçu
    - Métadonnées (Pays, Coordonnées)
    - Options de Téléchargement
    - Villes Similaires
3.  **Demande (/request)**
    - Formulaire Simple
    - Statut de la File (optionnel, ex: "5 cartes en cours de génération...")
4.  **À Propos (/about)**
    - Philosophie du projet
    - Explication Technique (RPi + OSM)

---

## 4. Maquettes (Wireframes)

### A. Page d'Accueil

```
┌─────────────────────────────────────────────────────────────┐
│  CITYPAPER                                     [Demander]   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│           CARTES MINIMALISTES POUR VOS MURS                 │
│           [ Rechercher votre ville...     ]                 │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │              │  │              │  │              │   │
│  │    APERÇU    │  │    APERÇU    │  │    APERÇU    │   │
│  │              │  │              │  │              │   │
│  │    PARIS     │  │   LONDRES    │  │    TOKYO     │   │
│  │    France    │  │      RU      │  │    Japon     │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │              │  │              │  │              │   │
│  │    APERÇU    │  │    APERÇU    │  │    APERÇU    │   │
│  │              │  │              │  │              │   │
│  │     ROME     │  │    BERLIN    │  │      NY      │   │
│  │    Italie    │  │   Allemagne  │  │     USA      │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### B. Page Détail Ville

```
┌─────────────────────────────────────────────────────────────┐
│  < Retour à la Galerie                                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────────────────┐   PARIS                       │
│   │                         │   France                      │
│   │                         │   48.8566° N, 2.3522° E       │
│   │                         │                               │
│   │      GRAND APERÇU       │   ┌───────────────────────┐   │
│   │        CARTE            │   │ Télécharger PDF (Print)│  │
│   │                         │   └───────────────────────┘   │
│   │                         │                               │
│   │                         │   ┌───────────────────────┐   │
│   │                         │   │ Télécharger Wallpaper │   │
│   │                         │   └───────────────────────┘   │
│   │                         │                               │
│   └─────────────────────────┘   Licence : ODbL (OpenStreetMap)
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  Vous aimerez aussi :                                       │
│  [Lyon] [Marseille] [Bordeaux]                              │
└─────────────────────────────────────────────────────────────┘
```

### C. Modal / Page de Demande

```
┌─────────────────────────────────────────────────────────────┐
│                                           [X]               │
│   DEMANDER UNE VILLE                                        │
│                                                             │
│   Vous ne trouvez pas votre ville ? Ajoutez-la à la file.   │
│                                                             │
│   Nom de la Ville :                                         │
│   [_______________________________________]                 │
│                                                             │
│   Pays :                                                    │
│   [_______________________________________]                 │
│                                                             │
│   Email (pour la notification) :                            │
│   [_______________________________________]                 │
│                                                             │
│   [ ENVOYER LA DEMANDE ]                                    │
│                                                             │
│   * Les cartes sont générées quotidiennement par notre worker.
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Spécifications du Système de Design

### Typographie

- **Police Principale :** `Inter` ou `Geist Sans` (Graisse variable).
- **Titres :** Gras, majuscules, espacement large (letter-spacing).
- **Corps :** Regular, hauteur de ligne lisible (1.5).

### Palette de Couleurs

| Rôle         | Couleur  | Hex       | Usage                           |
| ------------ | -------- | --------- | ------------------------------- |
| Fond         | Blanc    | `#FFFFFF` | Fond principal                  |
| Premier Plan | Noir     | `#111111` | Texte principal, Titres         |
| Muet (Muted) | Gris-500 | `#71717a` | Texte secondaire, Métadonnées   |
| Bordure      | Gris-200 | `#e4e4e7` | Bordures de cartes, Séparateurs |
| Accent       | Noir     | `#000000` | Boutons Primaires (Noir Solide) |

### Composants

#### 1. Carte Ville (Card)

- **Ratio d'Aspect :** 5:7 (Correspond au standard poster 50x70).
- **Comportement :** Au survol, l'image grossit légèrement (1.05x).
- **Contenu :** Minimal. Juste l'image + Nom + Pays.

#### 2. Boutons

- **Primaire :** Noir Solide, Texte Blanc, Coins carrés (Style Brutaliste/Suisse).
- **Secondaire :** Blanc, Bordure Noire.

#### 3. Barre de Recherche

- **Style :** Ligne minimale ou boîte épurée.
- **Interaction :** Filtrage instantané (côté client si liste < 500 éléments).

---

## 6. Notes sur le Responsive & l'Accessibilité

### Responsive

- **Mobile (<768px) :**
  - La grille passe en 1 colonne.
  - La page détail s'empile (Image en haut, détails en bas).
  - "Demander" passe dans une barre fixe en bas ou menu hamburger.
- **Tablette (768px - 1024px) :**
  - Grille : 2 colonnes.
- **Desktop (>1024px) :**
  - Grille : 3 ou 4 colonnes.

### Vérification Accessibilité

- **Images :** Toutes les images de cartes DOIVENT avoir `alt="Carte de [Nom Ville]"`.
- **Contraste :** Le Noir sur Blanc passe le niveau AAA. S'assurer que le texte Gris-500 est assez grand ou assez foncé pour le AA.
- **Clavier :** S'assurer que le "Focus Ring" est visible (style personnalisé : contour noir épais).
- **Formulaires :** Les étiquettes doivent être associées aux entrées (via `<label for="...">`).

---

## 7. Prochaines Étapes

1.  **Revue :** Valider avec le Product Manager (Utilisateur).
2.  **Passation :** Transmettre à l'Architecte Système pour confirmer la structure de données pour les "Demandes".
3.  **Dév :** Configurer le thème Tailwind avec ces couleurs/polices.
