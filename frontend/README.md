# Clean City Dashboard

Frontend for the **Environmental Violation Detection System** — an operations console for reviewing AI-detected environmental violations (vehicle littering, exhaust smoke) captured from CCTV footage, enriched with ANPR license-plate data, and triaged by a human reviewer.

This is the web dashboard only. It consumes the project's FastAPI backend (`../backend`) over HTTP.

---


## Getting Started

```bash
# 1. From the repository root, enter the frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Start the development server (Vite, with hot-module reload)
npm run dev
```

The app is served at **http://localhost:5173** by default. Vite will print the exact URL and pick another port automatically if 5173 is taken.


## Configuration

The dashboard reads its API base URL from an environment variable. All Vite environment variables **must** be prefixed with `VITE_`.

| Variable        | Default                  | Description                                        |
| --------------- | ------------------------ | -------------------------------------------------- |
| `VITE_API_URL`  | `http://localhost:8000`  | Base URL of the FastAPI backend (no trailing `/`). |

### Response contract

The endpoint returns a **bare JSON array** of incident objects, there is no `{ data, total, page, page_size }` envelope in backend

## Project Structure

```
frontend/
├── public/                     
├── src/
│   ├── assets/                
│   ├── components/
│   │   ├── incidents/
│   │   │   └── IncidentCard    
│   │   └── layout/
│   │       ├── AppLayout       
│   │       └── TopBar          
│   ├── mock/
│   │   └── incidents.mock.json 
│   ├── pages/
│   │   ├── FullConsole        
│   │   ├── IncidentDetail     
│   │   └── ExpandedMap         
│   ├── theme/
│   │   └── tokens.css         
│   ├── App.jsx                 
│   ├── main.jsx               
│   └── index.css               
├── index.html                 
├── eslint.config.js
├── vite.config.js
└── package.json
```

---

## Building for Production

```bash
npm run build    
npm run preview  
