# AROGYA — AI Wellness Assistant

<p align="center">
  <img src="https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=white" />
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/LangChain-1C3C3C?style=flat-square&logo=langchain&logoColor=white" />
  <img src="https://img.shields.io/badge/Groq-F55036?style=flat-square&logo=groq&logoColor=white" />
  <img src="https://img.shields.io/badge/YouTube API-FF0000?style=flat-square&logo=youtube&logoColor=white" />
  <img src="https://img.shields.io/badge/Tailwind CSS-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white" />
</p>

<p align="center">
  A multi-agent AI orchestration framework built with LangChain and Groq.<br/>
  Coordinates specialized agents to analyze symptoms and deliver personalized wellness guidance<br/>
  across diet, fitness, lifestyle, and health consultation.
</p>

<p align="center">
  <a href="https://arogya-wellness.vercel.app/"><img src="https://img.shields.io/badge/Live App-111827?style=flat-square&logo=vercel&logoColor=white" /></a>
  &nbsp;
  <a href="https://arogya-care-zuzs.onrender.com"><img src="https://img.shields.io/badge/Backend API-16A34A?style=flat-square&logo=node.js&logoColor=white" /></a>
  &nbsp;
  <a href="https://github.com/venkata-arjun/arogya-wellness-assistant"><img src="https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white" /></a>
</p>

---

## Table of Contents

- [Overview](#overview)
- [Live Links](#live-links)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Agent Workflow](#agent-workflow)
- [API Endpoints](#api-endpoints)
- [Folder Structure](#folder-structure)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Application Flow](#application-flow)
- [Future Improvements](#future-improvements)
- [Contributing](#contributing)
- [Developer](#developer)

---

## Overview

Arogya is an AI-powered health and wellness consultation platform built on a **multi-agent orchestration framework** using LangChain.

Four specialized agents — Symptom, Lifestyle, Diet, and Fitness — run sequentially and share context through a common memory layer. Each agent reads the outputs of previous agents before generating its response, ensuring advice is coherent, cumulative, and personalized to the user's full health picture.

The platform combines a Flask REST API backend with a React frontend, persistent health profiles, conversation history, RAG-enhanced responses, and YouTube-based educational recommendations.

---

## Live Links

| Service | URL |
|---|---|
| Live App | https://arogya-wellness.vercel.app |
| Backend API | https://arogya-care-zuzs.onrender.com |
| GitHub | https://github.com/venkata-arjun/arogya-wellness-assistant |

---

## Features

### Authentication

- User registration and login
- Secure session management
- Protected routes and endpoints

### AI Health Consultation

- Multi-agent orchestration via LangChain
- Symptom analysis powered by Groq LLM
- Personalized diet, fitness, and lifestyle guidance
- RAG-enhanced responses from a curated health knowledge base
- Streamed AI responses via `/chat_stream`

### Health Profiles

- Persistent user health profiles
- Store medical history, conditions, and preferences
- Profile-aware AI recommendations

### Conversation History

- Full consultation history per user
- Review past AI interactions and guidance

### YouTube Recommendations

- Context-aware health video suggestions
- Integrated via YouTube Data API
- Surfaced alongside AI consultation responses

---

## Tech Stack

**Frontend**

| Tool | Purpose |
|---|---|
| React + Vite | UI framework and build tool |
| Tailwind CSS | Utility-first styling |
| Axios | HTTP requests |

**Backend**

| Tool | Purpose |
|---|---|
| Python + Flask | Server and REST API |
| LangChain | Multi-agent orchestration framework |
| Groq (llama-3.3-70b-versatile) | LLM for all agent responses |
| RAG (knowledge.json) | Retrieval-Augmented Generation knowledge base |
| JSON Storage | Lightweight persistence for users, profiles, and history |
| YouTube Data API | Health video recommendations |

---

## Architecture

```
┌──────────────────────────────────┐
│        React Frontend            │
└─────────────────┬────────────────┘
                  │  Axios  REST API
┌─────────────────▼────────────────┐
│       Flask  Backend             │
└──────┬───────────────────────────┘
       │
┌──────▼──────────────────────────────────────┐
│          LangChain Orchestrator              │
│                                             │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │Symptom  │→ │Lifestyle │→ │  Diet    │→ │ Fitness  │ │
│  │ Agent   │  │  Agent   │  │  Agent   │  │  Agent   │ │
│  └─────────┘  └──────────┘  └──────────┘  └──────────┘ │
│                   Shared Memory Layer                    │
└──────┬──────────────────────┬───────────────────────────┘
       │                      │
  ┌────▼──────┐        ┌──────▼──────────────┐
  │  Groq LLM │        │  RAG Knowledge Base │
  │  (llama)  │        │  + YouTube API      │
  └───────────┘        └─────────────────────┘
```

---

## Agent Workflow

Every user health query passes through four agents in sequence. Each agent reads all prior context from shared memory before generating its response.

```
User Query
    │
    ▼
Symptom Agent     — analyzes symptoms, queries LLM + knowledge base, writes to shared memory
    │
    ▼
Lifestyle Agent   — reads symptom context, adds lifestyle advice, updates memory
    │
    ▼
Diet Agent        — reads symptom + lifestyle context, provides nutrition guidance, updates memory
    │
    ▼
Fitness Agent     — reads all prior context, recommends exercises, updates memory
    │
    ▼
Orchestrator      — combines all agent outputs into a comprehensive markdown response
    │
    ▼
Final Response    — returned to frontend for display
```

---

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/login` | Authenticate a user |
| POST | `/register` | Register a new user |

### User Profile

| Method | Endpoint | Description |
|---|---|---|
| GET | `/profile/<username>` | Retrieve a user's health profile |
| POST | `/profile/<username>` | Update a user's health profile |

### Health Consultation

| Method | Endpoint | Description |
|---|---|---|
| POST | `/chat_stream` | Stream AI-generated health guidance |
| POST | `/health-assist` | Return structured health guidance |
| GET | `/history/<username>` | Retrieve user conversation history |

### Recommendations

| Method | Endpoint | Description |
|---|---|---|
| POST | `/youtube-recommendations` | Return health-related YouTube video suggestions |

---

## Folder Structure

```
arogya-wellness-assistant/
│
├── assets/                            # Project documentation assets
│   ├── arogya-logo.png
│   └── architecture-flow.png
│
├── backend/                           # Flask REST API backend
│   ├── app.py                         # Flask application and endpoints
│   ├── wsgi.py                        # Production WSGI configuration
│   ├── config/
│   │   ├── settings.py                # Environment and API configuration
│   │   └── logging.py                 # Logging setup
│   ├── services/
│   │   ├── agents.py                  # Multi-agent system (symptom, lifestyle, diet, fitness)
│   │   ├── orchestrator.py            # Agent orchestration and coordination
│   │   ├── memory.py                  # Conversation memory management
│   │   ├── rag.py                     # Retrieval-Augmented Generation
│   │   ├── api_key_pool.py            # API key management and quota handling
│   │   ├── history_store.py           # Conversation history persistence
│   │   ├── user_auth_store.py         # User authentication and credentials
│   │   ├── user_profile_store.py      # User health profile management
│   │   └── youtube_recommendations.py # YouTube content integration
│   ├── utils/
│   │   └── exceptions.py              # Custom exception classes
│   └── storage/
│       ├── users.json                 # User credentials
│       ├── user_profiles.json         # User health profiles
│       ├── history.json               # Conversation history
│       └── knowledge.json             # RAG knowledge base
│
├── frontend/                          # React + Vite frontend
│   └── src/
│       ├── components/
│       │   ├── HomePage.jsx
│       │   ├── LoginPage.jsx
│       │   ├── WellnessPage.jsx
│       │   ├── HistoryPage.jsx
│       │   ├── ProfilePage.jsx
│       │   ├── YouTubeRecommendations.jsx
│       │   └── NavBar.jsx
│       ├── styles/
│       ├── config.js
│       └── App.jsx
│
├── requirements.txt
├── README.md
└── .env
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/venkata-arjun/arogya-wellness-assistant.git
cd arogya-wellness-assistant
```

### 2. Backend (Flask)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
python -m backend.app
```

Backend runs at `http://127.0.0.1:5000`

### 3. Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`

Make sure all environment variables are configured and the backend terminal is kept running before starting the frontend.

---

## Environment Variables

### Backend — `backend/.env`

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL_NAME=llama-3.3-70b-versatile
YOUTUBE_API_KEY=your_youtube_api_key
```

> Multiple Groq API keys can be registered in `api_key_pool.py` for quota management and load balancing.

---

## Application Flow

**User journey**

```
Home  →  Register / Login  →  Wellness Consultation  →  Multi-Agent AI Response  →  YouTube Recommendations  →  History  →  Profile
```

**Agent pipeline (per query)**

```
User Query  →  Symptom Agent  →  Lifestyle Agent  →  Diet Agent  →  Fitness Agent  →  Orchestrator  →  Final Response
```

---

## Future Improvements

- Persistent database (PostgreSQL) replacing JSON storage
- Voice-based health query input
- PDF export of consultation reports
- Appointment booking integration
- Multilingual support
- Mobile app
- Wearable data integration

---

## Contributing

Contributions are welcome. Please follow the steps below.

1. Fork the repository
2. Create a feature branch

```bash
git checkout -b feature/your-feature-name
```

3. Commit your changes

```bash
git commit -m "Add: brief description of the change"
```

4. Push your branch

```bash
git push origin feature/your-feature-name
```

5. Open a Pull Request on GitHub with a clear description of what was changed and why.

---

## Developer

**Rankela Venkata Arjun** — Full Stack Developer

| | |
|---|---|
| GitHub | https://github.com/venkata-arjun |
| Repository | https://github.com/venkata-arjun/arogya-wellness-assistant |
| Live App | https://arogya-wellness.vercel.app |
| Backend API | https://arogya-care-zuzs.onrender.com |

---

<p align="center">Built with React, Flask, LangChain, and Groq — multi-agent AI orchestration for personalized wellness guidance.</p>
