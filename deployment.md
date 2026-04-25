# PERSONA v3 — Deployment Guide
> FastAPI · Google Gemini 2.0 Flash · Supabase · Vercel

---

## Prerequisites

- GitHub account — github.com
- Vercel account — vercel.com (free)
- Supabase account — supabase.com (free)
- Gemini API Key — aistudio.google.com/app/apikey (free)
- Git + Python 3.10+ installed locally

---

## Project Structure

```
persona-v3/
│
├── api/
│   └── index.py          ← FastAPI backend (use the updated version)
│
├── public/
│   └── index.html        ← Frontend (no changes needed)
│
├── vercel.json           ← Routing config
├── requirements.txt      ← Updated dependencies
├── .env                  ← Local only — NEVER commit this
└── .gitignore            ← Must include .env
```

Your `vercel.json` should look like this:

```json
{
  "rewrites": [
    { "source": "/api/(.*)", "destination": "/api/index.py" },
    { "source": "/(.*)",     "destination": "/public/index.html" }
  ]
}
```

---

## Step 1 — Get Your API Keys

**Gemini API Key**
1. Go to aistudio.google.com/app/apikey
2. Sign in with Google
3. Click **Create API Key**
4. Copy the key (starts with `AIzaSy...`)

**Supabase URL + Key**
1. Go to supabase.com/dashboard → open your project
2. Go to **Settings → API**
3. Copy the **Project URL** — looks like `https://xxxx.supabase.co`
4. Copy the **anon / public** key — the long JWT token

---

## Step 2 — Create Tables in Supabase

Go to your Supabase project → **SQL Editor** → New Query → paste and run:

```sql
-- Tracks every category click
create table if not exists user_events (
  id         bigint generated always as identity primary key,
  user_id    text not null,
  category   text not null,
  brand      text,
  created_at timestamptz default now()
);

-- Stores click counts per user per category
create table if not exists user_preferences (
  id         bigint generated always as identity primary key,
  user_id    text not null,
  category   text not null,
  clicks     int default 1,
  unique (user_id, category)
);

-- Stores each offer generation event
create table if not exists offer_history (
  id         bigint generated always as identity primary key,
  user_id    text not null,
  segment    text,
  category   text,
  created_at timestamptz default now()
);

-- Wishlist items
create table if not exists wishlist (
  id               bigint generated always as identity primary key,
  user_id          text not null,
  name             text not null,
  category         text,
  price            text,
  discounted_price text,
  rating           text,
  created_at       timestamptz default now()
);
```

> Uses `IF NOT EXISTS` — safe to run even if some tables already exist.

---

## Step 3 — Setup .gitignore and .env

**.gitignore**
```
.env
__pycache__/
*.pyc
.vercel/
```

**.env** (local only — never commit)
```
GEMINI_API_KEY=AIzaSy...your-key...
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=eyJh...your-anon-key...
```

---

## Step 4 — Push to GitHub

```bash
cd persona-v3

git init
git add .
git commit -m "PERSONA v3 — Gemini + Supabase"

# Create a new repo on github.com first, then:
git remote add origin https://github.com/YOUR_USERNAME/persona-v3.git
git branch -M main
git push -u origin main
```

> Create the GitHub repo with **no README** to avoid conflicts on push.

---

## Step 5 — Deploy on Vercel

1. Go to **vercel.com/new**
2. Click **Import Git Repository**
3. Select your `persona-v3` repo
4. Leave all settings as default
5. Click **Deploy**

> First deploy works but AI won't respond yet — API keys not added. Do Step 6 next.

---

## Step 6 — Add Environment Variables

Vercel dashboard → your project → **Settings → Environment Variables**

Add all three, checking **Production ✓ Preview ✓ Development ✓** for each:

| Variable Name    | Where to get it                            | Example value              |
|------------------|--------------------------------------------|----------------------------|
| `GEMINI_API_KEY` | aistudio.google.com → API Keys             | `AIzaSy...32chars...`      |
| `SUPABASE_URL`   | Supabase → Settings → API → Project URL   | `https://xxxx.supabase.co` |
| `SUPABASE_KEY`   | Supabase → Settings → API → anon key      | `eyJhbGci...long JWT...`   |

After saving → go to **Deployments tab** → click **⋯** on the latest → **Redeploy**

---

## Step 7 — Verify It Works

**Health check** — open in browser:
```
https://your-project.vercel.app/api/health
```

Expected response:
```json
{ "status": "ok", "engine": "PERSONA v3 — Supabase + Gemini" }
```

**Full flow test:**
1. Open your deployed site
2. Click 3–4 category tiles
3. Click **Generate All Outputs**
4. Should produce 8 AI-generated marketing outputs

**Verify Supabase data:**
Supabase → Table Editor → check `user_events` and `user_preferences` — rows should appear after clicking categories.

---

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start local server
uvicorn api.index:app --reload --port 8000

# Open browser
open http://localhost:8000
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| 500 error on `/api/generate-offer` | `GEMINI_API_KEY` missing or wrong — check env vars and Redeploy |
| Data not saving after refresh | `SUPABASE_URL` or `SUPABASE_KEY` missing — check env vars |
| 404 on `/api/*` routes | `vercel.json` missing or wrong rewrites block |
| `ModuleNotFoundError: google.genai` | `requirements.txt` not updated — replace and Redeploy |
| JSON parse error from Gemini | Temporary — retry. If persistent, check your Gemini API quota |

---

*PERSONA v3 · FastAPI · Google Gemini 2.0 Flash · Supabase · Vercel*
