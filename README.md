<h1 align="center">CityPaper 🌍📰</h1>

<p align="center">
  <b>Turn any city into a beautiful piece of art.</b><br>
  <i>An interactive platform to request, generate, and view artistic city maps based on OpenStreetMap data.</i>
</p>

<p align="center">
  <a href="https://citypaper-v1.vercel.app">🔗 Visit Website</a>
</p>

---

## 📸 Screenshots

> _Add screenshots here_

## 🚀 Key Features

### 🗺️ Map Generation

- **Automated Pipeline**: Converts OSM data into high-resolution artistic maps using [maptoposter](https://github.com/originalankur/maptoposter).
- **Asynchronous Processing**: Python worker handles heavy rendering tasks in the background.
- **Global Coverage**: Request any city, village, or town worldwide.

### ⚡ Modern Architecture

- **Queue System**: Supabase-powered request queue for scalable processing.
- **Smart Storage**: Uses **Hugging Face Datasets** for unlimited, free storage of generated assets.
- **Live Updates**: Real-time status tracking from "Pending" to "Published".

## 💻 Technical Stack

| Category       | Technologies                                                                                                                                                             |
| :------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Frontend**   | ![Next.js](https://img.shields.io/badge/Next.js-16-black) ![React](https://img.shields.io/badge/React-19-blue) ![Tailwind](https://img.shields.io/badge/Tailwind-4-cyan) |
| **Backend**    | ![Supabase](https://img.shields.io/badge/Supabase-Database-green) ![Python](https://img.shields.io/badge/Python-3.11+-yellow)                                            |
| **Worker**     | `matplotlib`, `osmnx`, `pandas`, `gitpython`                                                                                                                             |
| **Storage**    | **Hugging Face Datasets** (Asset Storage)                                                                                                                                |
| **Deployment** | **Vercel** (Frontend) + **Raspberry Pi** (Worker)                                                                                                                        |

---

## 📦 Installation & Getting Started

### Frontend Development

Make sure you have **Node.js** and **PNPM** installed.

1. **Clone the project**

   ```bash
   # 1. Clone the repository
   git clone https://github.com/baptistelechat/CityPaper.git
   cd CityPaper

   # 2. Setup Environment Variables
   # Create .env.local and fill in SUPABASE_URL, SUPABASE_KEY, HF_TOKEN, etc.
   cp .env.example .env.local
   nano .env.local
   ```

2. **Install dependencies**

   ```bash
   pnpm install
   ```

3. **Start the development server**

   ```bash
   pnpm dev
   ```

4. **Build for production**
   ```bash
   pnpm build
   ```

Open [http://localhost:3001](http://localhost:3001) with your browser to see the result.

## 🛠️ Worker Setup (Raspberry Pi 5)

The worker is a Python script that polls Supabase for map generation requests, generates the maps, and pushes the results to GitHub/Hugging Face.

### Prerequisites

1.  **Git** installed.
2.  **Python 3.11+** installed.
3.  **PM2** installed globally (`npm install -g pm2`).
4.  A configured `.env.local` file in the root directory (see `.env.example`).

### 📦 Installation

```bash
# 1. Clone the repository
git clone https://github.com/baptistelechat/CityPaper.git
cd CityPaper

# 2. Setup Environment Variables
# Create .env.local and fill in SUPABASE_URL, SUPABASE_KEY, HF_TOKEN, etc.
cp .env.example .env.local
nano .env.local
```

### ⚙️ Running with PM2

To ensure the worker runs continuously and restarts automatically on crash or reboot, use PM2.

```bash
# Start the worker in watch mode
# This will poll Supabase for new requests
# --push is required to push changes to git remote (GitHub)
pm2 start worker/main.py --name "citypaper-worker" --interpreter python3 -- watch --push

# Save the PM2 list to resurrect on reboot
pm2 save

# Setup PM2 startup script (follow instructions printed by this command)
pm2 startup
```

### 🔍 Monitoring

```bash
# Check status
pm2 status citypaper-worker

# View logs
pm2 logs citypaper-worker

# Stop the worker
pm2 stop citypaper-worker

# Restart
pm2 restart citypaper-worker
```

---

## 🛡️ Best Practices

This project follows defined code standards:

- **Linting**: `pnpm lint` to check code quality.
- **Architecture**: Clear separation between UI, Logic (Hooks/Store), and Data.
- **Clean Code**: Explicit variables, short functions, and strict typing.

---

## 😸 Maintainers

Made with ❤️ by [Baptiste LECHAT](https://github.com/baptistelechat)

## 📝 License

This project is MIT licensed.
