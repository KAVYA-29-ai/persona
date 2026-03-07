# PERSONA v2 — Vercel Deployment Guide

## Project Structure

```
persona-vercel/
├── api/
│   └── index.py        ← FastAPI backend (Vercel Python runtime)
├── public/
│   └── index.html      ← Frontend (served as static by Vercel CDN)
├── vercel.json         ← Routing config
├── requirements.txt    ← Python deps (Vercel reads this automatically)
├── .env                ← Local only — DO NOT commit
└── .gitignore
```

---

## Deploy to Vercel (5 steps)

### Step 1 — Push to GitHub
```bash
cd persona-vercel
git init
git add .
git commit -m "PERSONA AI Marketing Engine"
# Create a new repo on github.com, then:
git remote add origin https://github.com/YOUR_USERNAME/persona-ai.git
git push -u origin main
```

### Step 2 — Import on Vercel
1. Go to **https://vercel.com/new**
2. Click **"Import Git Repository"**
3. Select your `persona-ai` repo
4. Click **Deploy** (no framework preset needed)

### Step 3 — Add Environment Variable
1. In Vercel dashboard → your project → **Settings → Environment Variables**
2. Add:
   - **Name:** `GEMINI_API_KEY`
   - **Value:** `AIza...your actual key...`
   - **Environment:** Production + Preview + Development
3. Click **Save**

### Step 4 — Redeploy
After adding the env var:
1. Go to **Deployments** tab
2. Click the 3-dot menu on latest deploy → **Redeploy**

### Step 5 — Done! 🎉
Your app is live at `https://persona-ai.vercel.app`

---

## Get Your Gemini API Key
1. Go to **https://aistudio.google.com/app/apikey**
2. Click **"Create API Key"**
3. Copy the key → paste into Vercel env vars

---

## Important Notes

> **In-memory storage limitation:**
> Vercel runs serverless functions — memory resets between cold starts.
> For a production app, replace the in-memory dicts with **Vercel KV** (Redis).
> For demo/MVP purposes, it works perfectly within a single session.

---

## Local Development

```bash
pip install -r requirements.txt
# Create a real .env with your key:
echo "GEMINI_API_KEY=AIza..." > .env
# Run locally:
uvicorn api.index:app --reload --port 8000
# Open: http://localhost:8000/public/index.html
```
