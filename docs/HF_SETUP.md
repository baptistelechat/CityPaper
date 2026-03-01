# ☁️ Configuration Hugging Face pour CityPaper

Ce guide explique comment configurer un **Dataset Hugging Face** pour stocker gratuitement et à l'infini les cartes générées par CityPaper.

## 1. Créer un Compte Hugging Face

Si ce n'est pas déjà fait :
1. Allez sur [huggingface.co/join](https://huggingface.co/join).
2. Créez un compte (gratuit).
3. Validez votre email.

## 2. Créer un Token d'Accès (Write)

Pour que le Worker puisse uploader des fichiers, il lui faut une clé d'accès.

1. Allez dans **Settings** > **Access Tokens** (ou [cliquez ici](https://huggingface.co/settings/tokens)).
2. Cliquez sur **Create new token**.
3. Choisissez le type **Write** (c'est important pour pouvoir uploader).
4. Nommez-le (ex: `citypaper-worker-token`).
5. Copiez le token généré (il commence par `hf_...`).
   - *Note : C'est la valeur pour `HF_TOKEN`.*

## 3. Choisir le nom du Repository

Vous n'avez pas besoin de créer le repository manuellement, le script le fera pour vous s'il n'existe pas. Mais vous devez choisir son nom.

Le format est toujours : `NomUtilisateur/NomDuDataset`.

Exemple : `Baptiste/citypaper-maps`

## 4. Mettre à jour le fichier `.env`

Créez ou modifiez le fichier `worker/.env` avec les valeurs :

```ini
# Hugging Face Configuration
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
HF_REPO_ID=Baptiste/citypaper-maps
```

## 5. Vérification

Au premier lancement d'une génération :
1. Le script va vérifier si le dataset `Baptiste/citypaper-maps` existe.
2. S'il n'existe pas, il va le créer automatiquement (en mode "Dataset").
3. Il va uploader les cartes générées.
4. Les fichiers seront accessibles publiquement via des URLs comme :
   `https://huggingface.co/datasets/Baptiste/citypaper-maps/resolve/main/France/Paris/75000/Paris/4K_Wallpaper/Paris-4k_wallpaper-noir.png`

---
✅ **Avantages de cette solution :**
- **Gratuit** : Pas de limite de 10Go comme sur R2.
- **Pas de CB** : Aucune carte bancaire requise.
- **Visualisation** : Vous pouvez voir vos fichiers directement sur le site Hugging Face.
- **Versioning** : Chaque upload est un commit Git, vous avez l'historique !
