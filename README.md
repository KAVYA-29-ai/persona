<div align="center">

```
██████╗ ███████╗██████╗ ███████╗ ██████╗ ███╗   ██╗ █████╗
██╔══██╗██╔════╝██╔══██╗██╔════╝██╔═══██╗████╗  ██║██╔══██╗
██████╔╝█████╗  ██████╔╝███████╗██║   ██║██╔██╗ ██║███████║
██╔═══╝ ██╔══╝  ██╔══██╗╚════██║██║   ██║██║╚██╗██║██╔══██║
██║     ███████╗██║  ██║███████║╚██████╔╝██║ ╚████║██║  ██║
╚═╝     ╚══════╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝
```

### **AI-Powered Marketing Personalization Engine**
*Turn clicks into conversions — in real time.*

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python)](https://python.org)
[![Gemini](https://img.shields.io/badge/Gemini-2.0_Flash-4285F4?style=flat-square&logo=google)](https://aistudio.google.com)
[![Vercel](https://img.shields.io/badge/Deploy-Vercel-000000?style=flat-square&logo=vercel)](https://vercel.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

</div>

---

## What Is PERSONA?

**PERSONA** is a full-stack Generative AI marketing personalization engine. It watches what a user browses, builds a real-time behavioral profile, and uses **Google Gemini 2.0 Flash** to generate a complete, multi-channel marketing package — instantly.

**No database. No login. No setup headaches.** Just browse, click, and watch the AI work.

If Gemini or Supabase is unavailable, the app now falls back to a deterministic local mode so the site stays usable instead of returning repeated 500/502 errors.

### How It Works in 4 Steps

```
①  User clicks product categories  →  Interest signals are recorded
②  Preference model updates live   →  Segment & engagement inferred
③  Gemini AI analyzes the profile  →  Full marketing package generated
④  9 channel-specific outputs      →  Ready to copy, export, or deploy
```

---

## Features

### AI Output Channels (9 Total)

| # | Channel | What Gets Generated |
|---|---------|---------------------|
| 1 | 🎯 **Promo Card** | Headline, subtext, badge, expiry + live countdown timer |
| 2 | 🔀 **A/B Variant** | Alternate angle — same offer, different emotional hook |
| 3 | 📧 **Email** | Subject, preview text, full personalized body copy |
| 4 | 💬 **SMS** | 160-char punchy message with char counter |
| 5 | 🔔 **Push Notification** | Title, body, CTA — rendered as real phone notification |
| 6 | 📱 **WhatsApp** | Casual friend-tip message, rendered in WhatsApp UI |
| 7 | 📸 **Instagram** | Caption with hashtags, story overlay text, reel hook |
| 8 | 🔍 **Google Ads** | 3 headlines + 2 descriptions with character validation |
| 9 | 🛍️ **Product Picks** | 3 AI-curated products with price, rating, discount, reason |

### AI Insights Panel

- **Personalization Score** — how well-tailored the offer is (0–100%)
- **Conversion Probability** — estimated likelihood to convert
- **Best Send Time** — AI-recommended delivery window
- **Best Channel** — which platform to push hardest
- **Psychological Triggers** — primary + secondary (FOMO, Scarcity, Authority…)
- **Upsell Opportunity** — cross-sell suggestion
- **Risk Note** — what might reduce conversion for this segment

### Smart Preference Engine

10 buyer segments auto-inferred from browsing behavior:

| Segment | Trigger |
|---------|---------|
| ⚡ Impulse Buyer | Short session, varied clicks |
| 🔍 Research-First | High diversity score |
| 🔥 Trend Follower | Fashion / beauty focus |
| 🌟 Experience Buyer | Sports / shoes repeat clicks |
| 💎 Loyalty Seeker | Home category dominant |
| 🎯 Budget Hunter | Mixed with low repeat |
| 🎮 Power Gamer | Gaming category focus |
| ✈️ Explorer | Travel category dominant |
| 🍕 Foodie | Food category dominant |
| 📚 Knowledge Seeker | Books category dominant |

### Additional Features

- 📋 **Campaign History** — Last 10 generated campaigns saved to localStorage
- ❤️ **Wishlist** — Save products, persists across browser refresh
- 📊 **Analytics Dashboard** — Category breakdown bars, brand cloud, session summary
- ⬇️ **Export All** — Download full marketing package as `.txt` file
- ⏱ **Live Countdown Timer** — Real-time urgency on promo card
- 🌙 **Dark / Light Mode** — Toggles and saves preference
- 💾 **Session Persistence** — localStorage keeps data on refresh
- 🔄 **Session Reset** — One-click full clear

---

## Project Structure

```
persona-v3/
│
├── api/
│   └── index.py          ← FastAPI backend (Vercel Python serverless)
│                            8 endpoints · Gemini integration · preference engine
│
├── public/
│   └── index.html        ← Complete frontend (single file, no framework)
│                            4 views: Dashboard · History · Wishlist · Analytics
│
├── vercel.json           ← Routing: /api/* → Python, /* → static CDN
├── requirements.txt      ← fastapi · uvicorn · httpx · mangum
├── .env                  ← 🔒 Local only — your Gemini API key goes here
├── .gitignore            ← Excludes .env from git
└── README.md             ← You are here
```

---

## Deploy to Vercel

### Prerequisites

- [GitHub account](https://github.com)
- [Vercel account](https://vercel.com/signup) — free
- [Gemini API Key](https://aistudio.google.com/app/apikey) — free

---

### Step 1 — Push to GitHub

```bash
cd persona-v3

git init
git add .
git commit -m "PERSONA v3 — AI Marketing Engine"

# Create a new repo on github.com first, then:
git remote add origin https://github.com/YOUR_USERNAME/persona-v3.git
git push -u origin main
```

---

### Step 2 — Import on Vercel

1. Go to **[vercel.com/new](https://vercel.com/new)**
2. Click **"Import Git Repository"**
3. Select your `persona-v3` repo
4. Leave all settings as default
5. Click **Deploy**

> First deploy succeeds even if external services are not configured. For live AI and persistence, add the environment variables in the next step.

---

### Step 3 — Add Your Gemini API Key

1. Vercel dashboard → your project → **Settings → Environment Variables**
2. Click **"Add New"** and enter:

```
Name:   GEMINI_API_KEY
Value:  AIzaSy...your-actual-key...
```

3. Check all environments: **Production ✓  Preview ✓  Development ✓**
4. Click **Save**

If you also want browsing state, history, and wishlist persistence, add the Supabase variables from the deployment guide as well.

---

### Step 4 — Redeploy

1. Go to the **Deployments** tab
2. Click **⋯** on the latest deployment → **Redeploy**

---

### Done!

```
Your app is live at → https://persona-v3.vercel.app
```

---

## Local Development

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your API key
echo "GEMINI_API_KEY=AIzaSy...your-key..." > .env

# 3. Start the server
uvicorn api.index:app --reload --port 8000

# 4. Open browser
open http://localhost:8000
```

## CI

The repository includes a GitHub Actions workflow at [.github/workflows/ci.yml](.github/workflows/ci.yml) that installs dependencies, byte-compiles the backend, and runs a simple import smoke test on every push and pull request.

---

## API Reference

### `POST /api/track-event`
Records a category click and updates the user's preference profile.

```json
// Request
{
  "user_id": "usr-AB3XY",
  "category": "sports",
  "brand": "Nike"
}

// Response
{
  "status": "tracked",
  "category": "sports",
  "brand": "Nike",
  "click_count": 3,
  "total_events": 7,
  "segment": "Experience Buyer",
  "engagement": "hot"
}
```

---

### `GET /api/generate-offer/{user_id}`
Sends user profile to Gemini and returns the full 9-output marketing package.

```json
// Response (condensed)
{
  "promo":      { "headline": "🏃 Run Faster With Nike", "discount": "20", "cta": "Shop Now →", ... },
  "ab_variant": { "headline": "⚡ Last Chance — Nike Flash Sale", ... },
  "email":      { "subject": "...", "preview": "...", "body": "..." },
  "sms":        "🏃 20% OFF Nike shoes today! Code PERSONA20 → [LINK]",
  "push":       { "title": "Nike Deal Alert!", "body": "...", "cta": "View Offer" },
  "whatsapp":   "Hey! 👋 Spotted you checking out sports gear...",
  "instagram":  { "caption": "...", "story_text": "20% OFF 🔥", "reel_hook": "..." },
  "google_ad":  { "headline1": "...", "headline2": "...", "description1": "..." },
  "products":   [ { "name": "...", "price": "₹4,999", "discounted_price": "₹3,999", ... } ],
  "insights":   { "personalization_score": 87, "conversion_probability": 72, ... },
  "meta":       { "segment": "Experience Buyer", "engagement": "hot", ... }
}
```

---

### All Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/track-event` | Track a category click |
| `GET` | `/api/generate-offer/{user_id}` | Generate full AI marketing package |
| `GET` | `/api/dashboard/{user_id}` | Analytics + preference breakdown |
| `GET` | `/api/history/{user_id}` | Last 10 generated campaigns |
| `POST` | `/api/wishlist/add` | Add a product to wishlist |
| `GET` | `/api/wishlist/{user_id}` | Get wishlist items |
| `DELETE` | `/api/wishlist/{user_id}/{name}` | Remove item from wishlist |
| `DELETE` | `/api/reset/{user_id}` | Clear all user data |

---

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **AI** | Google Gemini 2.0 Flash | Fast, structured JSON output, free tier |
| **Backend** | FastAPI (Python) | Async, type-safe, minimal boilerplate |
| **ASGI Adapter** | Mangum | Wraps FastAPI for Vercel serverless |
| **HTTP Client** | HTTPX | Async requests to Gemini API |
| **Frontend** | Vanilla HTML + JS | Zero build step, instant load |
| **Hosting** | Vercel | Free tier, global CDN, serverless Python |
| **Storage** | In-memory + localStorage | No database needed for MVP |

---

## Known Limitations

### Serverless Memory Reset

Vercel runs **serverless functions** — the Python process restarts after ~5 min of inactivity. The in-memory Python dicts (`user_prefs`, `user_events`) reset on cold starts.

**For production**, swap them with **Vercel KV** (Redis):

```python
# Current (in-memory):
user_prefs[uid][cat] += 1

# Production (Vercel KV):
await kv.hincrby(f"prefs:{uid}", cat, 1)
```

> For demo, hackathon, or portfolio use — the current setup works perfectly. The frontend uses localStorage to keep your session alive across refreshes.

### No Authentication

Each browser tab generates a random `user_id`. This is intentional for a zero-friction demo. Add Clerk or Supabase Auth for a production setup.

---

## Roadmap

- [ ] Vercel KV (Redis) for persistent backend storage
- [ ] User authentication (email / Google)
- [ ] PDF export of full campaign package
- [ ] Scheduled email delivery via Resend
- [ ] Multi-language output (Hindi, Spanish, etc.)
- [ ] Admin dashboard with cross-user analytics
- [ ] Webhook integrations (WhatsApp via Twilio, email via SendGrid)

---

## License

MIT — free to use, modify, and deploy.

---

<div align="center">

Built with FastAPI · Gemini AI · Vercel

*If this helped you, drop a ⭐ on the repo!*

</div>
