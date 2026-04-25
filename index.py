"""
PERSONA — AI Marketing Engine  (Supabase + google-genai SDK)
─────────────────────────────────────────────────────────────
Env vars required (Vercel → Settings → Environment Variables):
  GEMINI_API_KEY   — from aistudio.google.com
  SUPABASE_URL     — https://xxxx.supabase.co
  SUPABASE_KEY     — anon/service-role key

Supabase tables expected:
  user_events      (user_id text, category text, brand text, created_at timestamptz default now())
  user_preferences (user_id text, category text, clicks int default 1)
  offer_history    (user_id text, segment text, category text, created_at timestamptz default now())
  wishlist         (user_id text, name text, category text, price text, discounted_price text, rating text)
"""

import os, json, time, math
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from supabase import create_client, Client
from mangum import Mangum

# ── App ────────────────────────────────────────────────────────────────────────

app = FastAPI(title="PERSONA — AI Marketing Engine v3")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Clients (initialised per-request — safe for serverless cold starts) ────────

def gemini() -> genai.Client:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise HTTPException(500, "GEMINI_API_KEY not set in environment variables.")
    return genai.Client(api_key=key)

def sb() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise HTTPException(500, "SUPABASE_URL / SUPABASE_KEY not set.")
    return create_client(url, key)

# ── Static Metadata ────────────────────────────────────────────────────────────

CATEGORY_META: dict[str, dict] = {
    "sports":      {"interest": "sports & fitness",    "emoji": "🏃", "brands": ["Nike","Adidas","Under Armour","Puma"],        "avg_price": 85},
    "electronics": {"interest": "gadgets & tech",      "emoji": "📱", "brands": ["Apple","Samsung","Sony","OnePlus"],           "avg_price": 320},
    "fashion":     {"interest": "clothing & style",    "emoji": "👗", "brands": ["Zara","H&M","Levi's","Mango"],                "avg_price": 60},
    "shoes":       {"interest": "footwear & sneakers", "emoji": "👟", "brands": ["Nike","New Balance","Converse","Vans"],        "avg_price": 110},
    "beauty":      {"interest": "beauty & wellness",   "emoji": "✨", "brands": ["L'Oréal","MAC","The Ordinary","Nykaa"],       "avg_price": 45},
    "home":        {"interest": "home & lifestyle",    "emoji": "🏠", "brands": ["IKEA","Dyson","Philips","Prestige"],           "avg_price": 150},
    "gaming":      {"interest": "gaming & esports",    "emoji": "🎮", "brands": ["PlayStation","Xbox","Razer","SteelSeries"],   "avg_price": 250},
    "travel":      {"interest": "travel & adventure",  "emoji": "✈️", "brands": ["Samsonite","GoPro","Lonely Planet","Airbnb"], "avg_price": 200},
}

SEGMENTS: dict[str, dict] = {
    "Impulse Buyer":    {"icon": "⚡", "desc": "Responds to flash deals and FOMO triggers"},
    "Research-First":   {"icon": "🔍", "desc": "Needs social proof and detailed comparisons"},
    "Loyalty Seeker":   {"icon": "💎", "desc": "Values rewards, memberships, and exclusivity"},
    "Budget Hunter":    {"icon": "🎯", "desc": "Motivated by savings, discounts, best-value"},
    "Trend Follower":   {"icon": "🔥", "desc": "Buys what's hot, values newness and clout"},
    "Experience Buyer": {"icon": "🌟", "desc": "Buys for lifestyle transformation, not items"},
}

# ── Preference Helpers ─────────────────────────────────────────────────────────

def get_prefs(user_id: str) -> dict[str, int]:
    """Fetch all category click-counts for a user from Supabase."""
    res = sb().table("user_preferences").select("category,clicks").eq("user_id", user_id).execute()
    return {r["category"]: r["clicks"] for r in res.data}


def upsert_pref(user_id: str, category: str) -> int:
    """Increment category click count; insert row if it doesn't exist yet."""
    client = sb()
    existing = (
        client.table("user_preferences")
        .select("id,clicks")
        .eq("user_id", user_id)
        .eq("category", category)
        .execute()
    )
    if existing.data:
        new_val = existing.data[0]["clicks"] + 1
        client.table("user_preferences").update({"clicks": new_val}).eq("id", existing.data[0]["id"]).execute()
    else:
        new_val = 1
        client.table("user_preferences").insert({"user_id": user_id, "category": category, "clicks": 1}).execute()
    return new_val


def top_prefs(prefs: dict[str, int], n: int = 3) -> list[tuple[str, int]]:
    return sorted(prefs.items(), key=lambda x: x[1], reverse=True)[:n]


def diversity_score(prefs: dict[str, int]) -> float:
    if not prefs:
        return 0.0
    vals = list(prefs.values())
    total = sum(vals)
    entropy = -sum((v / total) * math.log2(v / total) for v in vals if v > 0)
    max_e = math.log2(len(vals)) if len(vals) > 1 else 1
    return round(entropy / max_e, 2) if max_e else 0.0


def engagement_level(total: int) -> str:
    if total == 0:  return "cold"
    if total <= 2:  return "warm"
    if total <= 6:  return "hot"
    return "super-engaged"


def infer_segment(prefs: dict[str, int]) -> str:
    if not prefs:
        return "Impulse Buyer"
    ranked = sorted(prefs.items(), key=lambda x: x[1], reverse=True)
    top_cat = ranked[0][0]
    total = sum(prefs.values())
    div = diversity_score(prefs)
    num_cats = len(prefs)
    if div > 0.8 and num_cats >= 3:              return "Research-First"
    if top_cat in ("electronics", "gaming"):     return "Research-First"
    if top_cat in ("fashion", "beauty"):         return "Trend Follower"
    if top_cat in ("shoes", "sports"):           return "Experience Buyer"
    if top_cat in ("home", "travel"):            return "Loyalty Seeker"
    if total <= 2:                               return "Impulse Buyer"
    return "Budget Hunter"


# ── Request Schemas ────────────────────────────────────────────────────────────

class TrackReq(BaseModel):
    user_id: str
    category: str
    brand: Optional[str] = None

class WishlistAddReq(BaseModel):
    user_id: str
    name: str
    category: str
    price: str
    discounted_price: str
    rating: str

# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {"status": "ok", "engine": "PERSONA v3 — Supabase + Gemini"}


@app.post("/api/track-event")
async def track_event(req: TrackReq):
    cat  = req.category.lower().strip()
    meta = CATEGORY_META.get(cat, {})
    brand = req.brand or (meta.get("brands", ["Unknown"])[0])

    # Persist to Supabase
    new_clicks = upsert_pref(req.user_id, cat)
    sb().table("user_events").insert({
        "user_id":  req.user_id,
        "category": cat,
        "brand":    brand,
    }).execute()

    prefs = get_prefs(req.user_id)
    total = sum(prefs.values())

    return {
        "status":       "tracked",
        "category":     cat,
        "brand":        brand,
        "click_count":  new_clicks,
        "total_events": total,
        "segment":      infer_segment(prefs),
        "engagement":   engagement_level(total),
    }


@app.get("/api/generate-offer/{user_id}")
async def generate_offer(user_id: str):
    prefs = get_prefs(user_id)
    if not prefs:
        raise HTTPException(400, "No browsing data — click some categories first.")

    ranked   = top_prefs(prefs, 3)
    total    = sum(prefs.values())
    segment  = infer_segment(prefs)
    engage   = engagement_level(total)
    div      = diversity_score(prefs)

    top_cat   = ranked[0][0]
    top_meta  = CATEGORY_META.get(top_cat, {})
    interest  = top_meta.get("interest", top_cat)
    brands    = top_meta.get("brands", [])[:3]
    avg_price = top_meta.get("avg_price", 100)
    secondary = [CATEGORY_META.get(c, {}).get("interest", c) for c, _ in ranked[1:]]
    secondary_str = ", ".join(secondary) or "general shopping"

    cat2 = ranked[1][0] if len(ranked) > 1 else top_cat
    cat3 = ranked[2][0] if len(ranked) > 2 else top_cat

    prompt = f"""You are an elite AI marketing engine generating MULTI-CHANNEL personalization outputs.

USER PROFILE:
- Primary interest: {interest} (clicked {ranked[0][1]} times)
- Secondary interests: {secondary_str}
- Buyer segment: {segment}
- Engagement level: {engage}
- Favorite brands: {", ".join(brands)}
- Avg spend range: ₹{avg_price * 70}–₹{avg_price * 120}
- Diversity score: {div} (0 = focused, 1 = broad shopper)

Return ONLY valid JSON — no markdown, no extra text, no code fences:

{{
  "promo": {{
    "badge": "one urgency word: HOT / FLASH / LIMITED / TODAY / EXCLUSIVE / NEW",
    "headline": "punchy headline with 1 emoji, max 8 words",
    "subtext": "2 personalised, urgent sentences referencing {interest}",
    "discount": "integer 15–35",
    "brand": "{brands[0] if brands else 'Top Brand'}",
    "cta": "3–5 word CTA button text",
    "savings_amount": "estimated ₹ savings (avg_price × discount% × 70)",
    "expiry": "urgency e.g. Ends in 4 hours / Today only"
  }},
  "ab_variant": {{
    "badge": "different urgency word from promo.badge",
    "headline": "completely different angle with 1 emoji",
    "subtext": "FOMO or aspirational hook (different emotion from Variant A)",
    "cta": "alternative CTA text",
    "discount": "within 5% of promo.discount"
  }},
  "email": {{
    "subject": "max 60 chars with emoji",
    "preview": "preview text 30–50 chars",
    "body": "3–4 sentence warm personalised body. Mention brand, category, discount, clear CTA sentence."
  }},
  "whatsapp": "casual 2–3 line message, feels like a friend tip, uses 2–3 emojis, includes [LINK]",
  "instagram": {{
    "caption": "3–4 lines trendy tone with 6–8 hashtags at end",
    "story_text": "max 6 words + 1 emoji for story overlay"
  }},
  "products": [
    {{
      "name": "specific real product name from {brands[0] if brands else 'brand'}",
      "category": "{top_cat}",
      "price": "realistic ₹ price",
      "discounted_price": "price after discount",
      "rating": "4.1–4.9",
      "reviews": 200,
      "tag": "BESTSELLER",
      "reason": "1 sentence why this fits the user"
    }},
    {{
      "name": "specific product from a complementary brand",
      "category": "{cat2}",
      "price": "realistic ₹ price",
      "discounted_price": "price after discount",
      "rating": "4.0–4.8",
      "reviews": 150,
      "tag": "TRENDING",
      "reason": "1 sentence why this fits"
    }},
    {{
      "name": "third specific product",
      "category": "{cat3}",
      "price": "realistic ₹ price",
      "discounted_price": "price after discount",
      "rating": "4.2–4.9",
      "reviews": 100,
      "tag": "NEW ARRIVAL",
      "reason": "1 sentence why this fits"
    }}
  ],
  "insights": {{
    "personalization_score": 60,
    "conversion_probability": 40,
    "best_send_time": "e.g. Tonight at 8 PM",
    "primary_trigger": "Scarcity / FOMO / Social Proof / Reciprocity / Authority",
    "segment_note": "1 sentence why {segment} responds to this offer",
    "upsell_hint": "1 sentence cross-sell / upsell opportunity"
  }}
}}"""

    # ── Gemini call (new SDK) ──────────────────────────────────────────────────
    client = gemini()
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )
    text = response.text.strip()

    # Strip markdown fences if model wraps output anyway
    if "```" in text:
        text = "\n".join(
            line for line in text.split("\n")
            if not line.strip().startswith("```")
        )

    try:
        offer = json.loads(text.strip())
    except json.JSONDecodeError as exc:
        raise HTTPException(500, f"Gemini returned invalid JSON: {text[:400]}") from exc

    # ── Persist offer to history ───────────────────────────────────────────────
    sb().table("offer_history").insert({
        "user_id":  user_id,
        "segment":  segment,
        "category": top_cat,
    }).execute()

    offer["meta"] = {
        "user_id":       user_id,
        "segment":       segment,
        "segment_info":  SEGMENTS.get(segment, {}),
        "engagement":    engage,
        "top_category":  top_cat,
        "top_interest":  interest,
        "total_events":  total,
        "diversity_score": div,
        "generated_at":  time.strftime("%H:%M, %d %b %Y"),
    }
    return offer


@app.get("/api/dashboard/{user_id}")
async def dashboard(user_id: str):
    prefs  = get_prefs(user_id)
    total  = sum(prefs.values())
    client = sb()

    events_res = (
        client.table("user_events")
        .select("brand")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(30)
        .execute()
    )
    recent_brands = list(
        dict.fromkeys(e["brand"] for e in events_res.data if e.get("brand"))
    )[:5]

    offers_res = client.table("offer_history").select("id").eq("user_id", user_id).execute()

    segment = infer_segment(prefs)
    breakdown = [
        {
            "category": cat,
            "emoji":    CATEGORY_META.get(cat, {}).get("emoji", "📦"),
            "interest": CATEGORY_META.get(cat, {}).get("interest", cat),
            "clicks":   count,
            "pct":      round(count / total * 100) if total else 0,
        }
        for cat, count in sorted(prefs.items(), key=lambda x: x[1], reverse=True)
    ]

    return {
        "user_id":           user_id,
        "segment":           segment,
        "segment_info":      SEGMENTS.get(segment, {}),
        "engagement":        engagement_level(total),
        "total_events":      total,
        "unique_categories": len(prefs),
        "diversity_score":   diversity_score(prefs),
        "category_breakdown": breakdown,
        "recent_brands":     recent_brands,
        "offer_count":       len(offers_res.data),
        "generated_at":      time.strftime("%H:%M, %d %b %Y"),
    }


@app.get("/api/history/{user_id}")
async def history(user_id: str):
    res = (
        sb().table("offer_history")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(10)
        .execute()
    )
    return {"history": res.data}


@app.post("/api/wishlist/add")
async def wishlist_add(req: WishlistAddReq):
    sb().table("wishlist").insert({
        "user_id":          req.user_id,
        "name":             req.name,
        "category":         req.category,
        "price":            req.price,
        "discounted_price": req.discounted_price,
        "rating":           req.rating,
    }).execute()
    return {"status": "added", "name": req.name}


@app.get("/api/wishlist/{user_id}")
async def wishlist_get(user_id: str):
    res = sb().table("wishlist").select("*").eq("user_id", user_id).execute()
    return {"wishlist": res.data}


@app.delete("/api/wishlist/{user_id}/{name}")
async def wishlist_remove(user_id: str, name: str):
    sb().table("wishlist").delete().eq("user_id", user_id).eq("name", name).execute()
    return {"status": "removed", "name": name}


@app.delete("/api/reset/{user_id}")
async def reset_user(user_id: str):
    client = sb()
    for table in ("user_events", "user_preferences", "offer_history", "wishlist"):
        client.table(table).delete().eq("user_id", user_id).execute()
    return {"status": "reset", "user_id": user_id}


# ── Vercel ASGI adapter ────────────────────────────────────────────────────────
handler = Mangum(app)
