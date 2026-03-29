#  SMART SHELF - Assistant d'Inventaire IA (Frontend)

> Application mobile de **gestion d'inventaire anti-gaspillage** développée avec **Expo Go (React Native)**, connectée à un backend **FastAPI** et propulsée par un modèle **VLM (Vision Language Model)**.

---

##  Fonctionnalités Principales

-  **Inventaire en temps réel** — Suivi complet des produits avec leurs dates de péremption (DLC).
-  **Scan hybride** — Détection instantanée des QR Codes / codes-barres via la caméra.
-  **Mode "Vrac" (IA)** — Comptage des produits frais sans code-barres (ex : fruits, légumes) et estimation automatique de la DLC grâce au modèle VLM.
-  **Notifications locales** — Alertes automatiques avant l'expiration de vos produits.

---

##  Prérequis & Installation

### 1. Node.js

Assurez-vous d'avoir **Node.js** (v18 ou supérieur) installé sur votre machine.
 [Télécharger Node.js](https://nodejs.org/)

### 2. Installer les dépendances

Dans le dossier `smart-shelf/`, exécutez :

```bash
npm install
# ou si vous utilisez yarn :
yarn install
```

### 3. Émulateur Android

Pour tester l'application sur un appareil virtuel, installez **Android Studio** :
 [Télécharger Android Studio](https://docs.expo.dev/workflow/android-studio-emulator/)

Après l'installation :
1. Ouvrez Android Studio → `Virtual Device Manager` (icône téléphone en haut à droite).
2. Cliquez sur **Create Device** et suivez l'assistant pour créer un AVD (Android Virtual Device).
3. Démarrez le Virtual Device avant de lancer l'application.

---

##  Configuration de l'Adresse IP (CRITIQUE)

> [!IMPORTANT]
> L'application mobile ne peut **pas** utiliser `localhost` pour communiquer avec le backend, car elle tourne sur un appareil (physique ou virtuel) séparé de votre machine. Vous devez renseigner l'**adresse IP locale** de votre ordinateur.

### Trouver votre adresse IP locale

**Sur Windows :**
```bash
ipconfig
```
→ Repérez la ligne `Adresse IPv4` dans votre interface réseau active (ex: `192.168.1.42`).


### Modifier la configuration

Ouvrez le fichier **`config/api.ts`** et remplacez l'IP par la vôtre :

```typescript
// config/api.ts
// si ce repertoire n'existe pas, créez-le et ajoutez la ligne de code ci-dessous
export const API_BASE_URL = "http://192.168.1.X:8000/api/v1";
//                                   ^^^^^^^^^^^^
//                          Remplacez par votre IP locale
```

> ⚠️ L'application mobile ET le serveur FastAPI doivent être sur le **même réseau Wi-Fi**.

---

##  Lancement de l'Application

```bash
npx expo start
```

Cette commande exécute `expo start --go` et affiche un **barre code** dans le terminal.

### Options de lancement :

| Méthode | Instructions |
|---|---|
| **Téléphone physique** | Installez l'app **Expo Go** ([Android](https://play.google.com/store/apps/details?id=host.exp.exponent) / [iOS](https://apps.apple.com/app/expo-go/id982107779)) et scannez le QR Code dans le terminal. |
| **Émulateur Android** | Appuyez sur la touche **`a`** dans le terminal après `npx expo start` (Android Studio doit être ouvert avec un AVD démarré). |

---

##  Structure du Projet

```
smart-shelf/
├── app/                  # Écrans (Expo Router)
│   ├── (tabs)/           # Navigation principale
│   │   ├── index.tsx     #  Écran Inventaire
│   │   └── scan.tsx      #  Écran Scan
│   └── _layout.tsx
├── config/
│   └── api.ts            #  URL du backend (à configurer)
├── services/
│   └── api.ts            # Fonctions d'appel API
└── package.json
```

---

##  Lien avec le Backend

Ce frontend communique avec l'API FastAPI disponible dans le dossier `backend/` (ou `api/`) du repository. Assurez-vous que le backend est bien lancé avant de démarrer l'application mobile.

```bash
# Dans le dossier backend :
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
