# AgeGuard – AI-Powered OTT Age Verification

**B.Tech Final Year AI/ML Project**

---

## Phase 1 – OTT Platform Foundation

A Netflix-style OTT frontend built with React + Tailwind CSS, backed by a Flask REST API.

### Tech Stack
- **Frontend:** React 18, Tailwind CSS, React Router v6
- **Backend:** Flask, Flask-CORS
- **AI (Phase 2+):** PyTorch, OpenCV, MediaPipe

---

## Project Structure

```
AgeGuard/
├── backend/
│   ├── app.py              ← Flask API
│   └── requirements.txt    ← Python dependencies
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── HeroBanner.jsx
│   │   │   ├── MovieCard.jsx
│   │   │   └── RatingBadge.jsx
│   │   ├── pages/
│   │   │   ├── HomePage.jsx
│   │   │   ├── MovieDetailPage.jsx
│   │   │   └── VideoPlayerPage.jsx
│   │   ├── App.js
│   │   ├── index.js
│   │   └── index.css
│   ├── package.json
│   ├── tailwind.config.js
│   └── postcss.config.js
└── README.md
```

---

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | /movies | Returns all movies as JSON |
| GET | /movies/:id | Returns a single movie |
| GET | /health | Health check |
