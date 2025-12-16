# Y2K Video Editor

A retro-themed web-based video editor with a 90s arcade aesthetic. Create videos from images with audio and transitions.

![Y2K Video Editor](frontend/static/images/logo.png)

## ✨ Features

- 🎬 **Video Creation** - Combine images into videos with customizable durations
- 🎵 **Multi-Audio Support** - Add multiple audio tracks that play sequentially
- 🎨 **Retro UI** - 90s arcade aesthetic with neon colors and twinkling stars
- 📱 **Responsive** - Works on desktop and mobile devices
- 🔐 **User Accounts** - Personal media library and project management

## 🛠 Tech Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | SvelteKit 5 + TypeScript |
| **Backend** | FastAPI (Python 3.11+) |
| **Database** | PostgreSQL (Supabase) |
| **Video Processing** | moviepy 2.x + FFmpeg + OpenCV |
| **Styling** | Custom CSS with arcade theme |

## 📁 Project Structure

```
project-y2k/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application
│   │   ├── config.py        # Pydantic settings
│   │   ├── database.py      # SQLAlchemy connection
│   │   ├── models.py        # Database models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── dependencies.py  # Auth middleware
│   │   ├── routers/         # API endpoints
│   │   └── utils/           # Helpers (security, video_creator)
│   └── temp/                # Temp files for video rendering
│
├── frontend/
│   ├── src/
│   │   ├── routes/          # SvelteKit pages
│   │   ├── lib/components/  # Reusable Svelte components
│   │   ├── lib/api.ts       # API client
│   │   └── app.css          # Global styles
│   ├── static/              # Static assets (images, fonts)
│   └── package.json
│
├── .env                     # Environment variables (gitignored)
├── .env.example             # Template for .env
└── pyproject.toml           # Python dependencies
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **FFmpeg** (for video processing)
- **uv** (Python package manager - recommended)

### 1. Clone and Setup Environment

```bash
cd project-y2k

# Create Python virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or: .venv\Scripts\activate  # Windows

# Install Python dependencies
pip install -e .
```

### 2. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your database credentials:

```env
DATABASE_URL=postgresql://user:pass@host:6543/db?sslmode=require
DIRECT_URL=postgresql://user:pass@host:5432/db?sslmode=require
JWT_SECRET=your-secret-key-at-least-32-chars
```

### 4. Install FFmpeg

```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# Fedora
sudo dnf install ffmpeg

# macOS
brew install ffmpeg

# Windows (via Chocolatey)
choco install ffmpeg
```

### 5. Run the Application

**Terminal 1 - Backend:**
```bash
source .venv/bin/activate
uvicorn backend.app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 6. Access the App

| URL | Description |
|-----|-------------|
| http://localhost:5173 | Frontend (SvelteKit dev) |
| http://localhost:8000 | Backend API |
| http://localhost:8000/docs | API Documentation |

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Create account |
| POST | `/api/auth/login` | User login |
| GET | `/api/auth/logout` | User logout |
| GET | `/api/auth/check` | Check auth status |

### Media
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/media/upload` | Upload images/audio |
| GET | `/api/media/images` | List user images |
| GET | `/api/media/audios` | List user audios |
| DELETE | `/api/media/images` | Delete images |
| DELETE | `/api/media/audios` | Delete audios |

### Video
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/video/render` | Render video from timeline |
| GET | `/api/video/view` | View/download rendered video |
| GET | `/api/video/editor-data` | Get editor data |

### Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/users` | List all users |
| GET | `/api/admin/media` | List all media |

## 🗄 Database Schema

The app uses PostgreSQL (via Supabase) with these tables:

- **users** - User accounts (username, email, password hash, admin flag)
- **images** - User uploaded images (stored as binary)
- **audios** - User uploaded audio files (stored as binary)

## 🎨 Theming

The app uses a custom 90s arcade theme with:
- Neon cyan (#40e0d0) and pink (#e066a0) accents
- VT323 monospace font for headings
- Press Start 2P for display elements
- CRT scanline overlay effect
- Twinkling star background

## 📝 Development Notes

- **Temp folder**: `backend/temp/` is used during video rendering - contents can be cleared
- **Video quality**: 360p, 720p, and 1080p options available
- **Audio**: Multiple audio clips are concatenated sequentially

## 📄 License

MIT License
