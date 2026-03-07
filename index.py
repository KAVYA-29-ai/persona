from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import httpx, os, json, time
from collections import defaultdict

app = FastAPI(title="PERSONA — Advanced AI Marketing Engine")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

# ─── In-Memory Storage ────────────────────────────────────────────────────────

user_events:       dict[str, list[dict]]        = defaultdict(list)
user_preferences:  dict[str, dict[str, int]]    = defaultdict(lambda: defaultdict(int))
offer_history:     dict[str, list[dict]]         = defaultdict(list)

# ─── Static Data ──────────────────────────────────────────────────────────────

CATEGORY_META = {
    "sports":      {"interest": "sports & fitness",    "emoji": "🏃", "brands": ["Nike","Adidas","Under Armour","Puma"],       "avg_price": 85,  "segment_hint": "Active Athlete"},
    "electronics": {"interest": "gadgets & tech",      "emoji": "📱", "brands": ["Apple","Samsung","Sony","OnePlus"],          "avg_price": 320, "segment_hint": "Tech Enthusiast"},
    "fashion":     {"interest": "clothing & style",    "emoji": "👗", "brands": ["Zara","H&M","Levi's","Mango"],               "avg_price": 60,  "segment_hint": "Style Maven"},
    "shoes":       {"interest": "footwear & sneakers", "emoji": "👟", "brands": ["Nike","New Balance","Converse","Vans"],       "avg_price": 110, "segment_hint": "Sneakerhead"},
    "beauty":      {"interest": "beauty & wellness",   "emoji": "✨", "brands": ["L'Oréal","MAC","The Ordinary","Nykaa"],      "avg_price": 45,  "segment_hint": "Beauty Enthusiast"},
    "home":        {"interest": "home & lifestyle",    "emoji": "🏠", "brands": ["IKEA","Dyson","Philips","Prestige"],          "avg_price": 150, "segment_hint": "Home Curator"},
    "gaming":      {"interest": "gaming & esports",    "emoji": "🎮", "brands": ["PlayStation","Xbox","Razer","SteelSeries"],  "avg_price": 250, "segment_hint": "Power Gamer"},
    "travel":      {"interest": "travel & adventure",  "emoji": "✈️", "brands": ["Samsonite","GoPro","Lonely Planet","AirBnB"],"avg_price": 200, "segment_hint": "Explorer"},
}

SEGMENTS = {
    "Impulse Buyer":     {"icon": "⚡", "desc": "Responds to flash deals and FOMO triggers", "color": "#FF3D00"},
    "Research-First":    {"icon": "🔍", "desc": "Needs social proof and detailed comparisons", "color": "#00BCD4"},
    "Loyalty Seeker":    {"icon": "💎", "desc": "Values rewards, memberships, and exclusivity", "color": "#FFB800"},
    "Budget Hunter":     {"icon": "🎯", "desc": "Motivated by savings, discounts, best-value", "color": "#00E676"},
    "Trend Follower":    {"icon": "🔥", "desc": "Buys what's hot, values newness and clout",   "color": "#E040FB"},
    "Experience Buyer":  {"icon": "🌟", "desc": "Buys for lifestyle transformation, not items", "color": "#FF6E40"},
}


# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_top_n_preferences(user_id: str, n: int = 3) -> list[tuple[str, int]]:
    prefs = dict(user_preferences.get(user_id, {}))
    return sorted(prefs.items(), key=lambda x: x[1], reverse=True)[:n]

def get_engagement_level(total_clicks: int) -> str:
    if total_clicks == 0: return "cold"
    if total_clicks <= 2: return "warm"
    if total_clicks <= 6: return "hot"
    return "super-engaged"

def compute_diversity_score(prefs: dict) -> float:
    if not prefs: return 0.0
    values = list(prefs.values())
    total = sum(values)
    if total == 0: return 0.0
    import math
    entropy = -sum((v/total) * math.log2(v/total) for v in values if v > 0)
    max_entropy = math.log2(len(values)) if len(values) > 1 else 1
    return round(entropy / max_entropy, 2) if max_entropy else 0.0

def infer_segment(user_id: str) -> str:
    prefs = dict(user_preferences.get(user_id, {}))
    total = sum(prefs.values())
    top_cats = sorted(prefs.items(), key=lambda x: x[1], reverse=True)
    if not top_cats: return "Impulse Buyer"
    top_cat = top_cats[0][0]
    diversity = compute_diversity_score(prefs)
    if diversity > 0.8:          return "Research-First"
    if top_cat in ["electronics","gaming"]: return "Tech Enthusiast" if total > 4 else "Research-First"
    if top_cat in ["fashion","beauty"]:     return "Trend Follower"
    if top_cat in ["shoes","sports"]:       return "Experience Buyer"
    if top_cat in ["home","travel"]:        return "Loyalty Seeker"
    if total <= 2:                          return "Impulse Buyer"
    return "Budget Hunter"


# ─── Request Schemas ──────────────────────────────────────────────────────────

class TrackEventRequest(BaseModel):
    user_id: str
    category: str
    brand: Optional[str] = None


# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {"status": "ok", "engine": "PERSONA v2"}

@app.post("/track-event")
async def track_event(req: TrackEventRequest):
    cat = req.category.lower()
    meta = CATEGORY_META.get(cat, {})
    brand = req.brand or (meta.get("brands", [""])[0])

    user_events[req.user_id].append({
        "category": cat, "brand": brand, "ts": time.time()
    })
    user_preferences[req.user_id][cat] += 1

    top_prefs = get_top_n_preferences(req.user_id)
    total = sum(user_preferences[req.user_id].values())
    segment = infer_segment(req.user_id)

    return {
        "status": "tracked",
        "category": cat,
        "brand": brand,
        "click_count": user_preferences[req.user_id][cat],
        "total_events": total,
        "top_interest": top_prefs[0][1] if top_prefs else 0,
        "segment": segment,
        "engagement": get_engagement_level(total),
    }


@app.get("/generate-offer/{user_id}")
async def generate_offer(user_id: str):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not set.")

    prefs = dict(user_preferences.get(user_id, {}))
    top_prefs = get_top_n_preferences(user_id, 3)
    total_events = sum(prefs.values())
    segment = infer_segment(user_id)
    engagement = get_engagement_level(total_events)
    diversity = compute_diversity_score(prefs)

    if not top_prefs:
        raise HTTPException(status_code=400, detail="No browsing data. Click some categories first.")

    top_cat  = top_prefs[0][0]
    top_meta = CATEGORY_META.get(top_cat, {})
    interest = top_meta.get("interest", top_cat)
    brands   = top_meta.get("brands", [])[:3]
    avg_price = top_meta.get("avg_price", 100)

    # Secondary interests
    secondary = [CATEGORY_META.get(c, {}).get("interest", c) for c, _ in top_prefs[1:]]
    secondary_str = ", ".join(secondary) if secondary else "general shopping"

    prompt = f"""You are an elite AI marketing engine generating MULTI-CHANNEL personalization outputs.

USER PROFILE:
- Primary interest: {interest} (clicked {top_prefs[0][1]} times)
- Secondary interests: {secondary_str}
- Buyer segment: {segment}
- Engagement level: {engagement}
- Favorite brands: {', '.join(brands)}
- Average spend range: ₹{avg_price*70}–₹{avg_price*120}
- Browse diversity score: {diversity} (0=focused, 1=broad)

Generate a COMPREHENSIVE marketing package. Return ONLY valid JSON, no markdown:

{{
  "promo": {{
    "badge": "one urgency word (HOT/NEW/FLASH/LIMITED/EXCLUSIVE/TODAY)",
    "headline": "punchy headline with emoji, max 8 words",
    "subtext": "2 sentences personal and urgent, referencing {interest}",
    "discount": "specific % between 15-35",
    "brand": "{brands[0] if brands else 'Top Brand'}",
    "cta": "3-5 word action button text",
    "savings_amount": "estimated savings in ₹ (avg_price * discount%)",
    "expiry": "urgency timer text e.g. 'Ends in 4 hours' or 'Today only'"
  }},
  "ab_variant": {{
    "badge": "different urgency word",
    "headline": "completely different angle headline with emoji",
    "subtext": "different emotional hook — fear of missing out OR aspirational",
    "cta": "alternative CTA text",
    "discount": "slightly different % (within 5% of first)"
  }},
  "email": {{
    "subject": "email subject line, max 60 chars, includes emoji",
    "preview": "email preview text (30–50 chars)",
    "body": "3–4 sentence personalized email body. Warm, direct, mentions the brand and category. Include the discount offer and a clear CTA sentence."
  }},
  "whatsapp": "casual whatsapp message, 2–3 lines, uses emojis naturally, sounds like a friend tipping you off, includes discount and link placeholder [LINK]",
  "instagram": {{
    "caption": "instagram caption, 3–4 lines, trendy tone, relevant hashtags at end (6–8 hashtags)",
    "story_text": "very short story overlay text, punchy, max 6 words + emoji"
  }},
  "products": [
    {{
      "name": "specific product name from {brands[0] if brands else 'brand'}",
      "category": "{top_cat}",
      "price": "realistic ₹ price",
      "discounted_price": "price after discount",
      "rating": "4.1–4.9",
      "reviews": "number between 200–5000",
      "tag": "one tag: BESTSELLER or NEW ARRIVAL or TRENDING or STAFF PICK",
      "reason": "1 short sentence why this suits the user"
    }},
    {{
      "name": "second specific product name",
      "category": "{top_prefs[1][0] if len(top_prefs)>1 else top_cat}",
      "price": "realistic ₹ price",
      "discounted_price": "price after discount",
      "rating": "4.0–4.8",
      "reviews": "number between 100–3000",
      "tag": "one tag: BESTSELLER or NEW ARRIVAL or TRENDING or STAFF PICK",
      "reason": "1 short sentence why this suits the user"
    }},
    {{
      "name": "third specific product name",
      "category": "{top_prefs[2][0] if len(top_prefs)>2 else top_cat}",
      "price": "realistic ₹ price",
      "discounted_price": "price after discount",
      "rating": "4.2–4.9",
      "reviews": "number between 150–4000",
      "tag": "one tag: BESTSELLER or NEW ARRIVAL or TRENDING or STAFF PICK",
      "reason": "1 short sentence why this suits the user"
    }}
  ],
  "insights": {{
    "personalization_score": "integer 60–98",
    "conversion_probability": "integer 40–90",
    "best_send_time": "e.g. 'Tonight at 8 PM' or 'Tomorrow morning'",
    "primary_trigger": "psychological trigger used e.g. Scarcity / Social Proof / FOMO / Reciprocity / Authority",
    "segment_note": "1 sentence explaining why {segment} buyer responds to this offer type",
    "upsell_hint": "1 sentence about a logical upsell or cross-sell opportunity"
  }}
}}"""

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.0-flash:generateContent?key={api_key}"
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.85, "maxOutputTokens": 1800},
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, json=payload)

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Gemini error: {resp.text}")

    raw  = resp.json()
    text = raw["candidates"][0]["content"]["parts"][0]["text"].strip()

    # Strip markdown fences
    if "```" in text:
        lines = text.split("\n")
        text = "\n".join(l for l in lines if not l.strip().startswith("```"))

    try:
        offer = json.loads(text.strip())
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"JSON parse failed: {text[:300]}")

    # Enrich response
    offer["meta"] = {
        "user_id": user_id,
        "segment": segment,
        "segment_info": SEGMENTS.get(segment, {}),
        "engagement": engagement,
        "top_category": top_cat,
        "top_interest": interest,
        "total_events": total_events,
        "diversity_score": diversity,
        "generated_at": time.strftime("%H:%M, %d %b %Y"),
    }

    offer_history[user_id].append({"ts": time.time(), "segment": segment, "category": top_cat})
    return offer


@app.get("/dashboard/{user_id}")
async def get_dashboard(user_id: str):
    prefs = dict(user_preferences.get(user_id, {}))
    events = user_events.get(user_id, [])
    total = sum(prefs.values())
    segment = infer_segment(user_id)

    category_breakdown = []
    for cat, count in sorted(prefs.items(), key=lambda x: x[1], reverse=True):
        meta = CATEGORY_META.get(cat, {})
        category_breakdown.append({
            "category": cat,
            "emoji": meta.get("emoji", "📦"),
            "interest": meta.get("interest", cat),
            "clicks": count,
            "pct": round(count / total * 100) if total else 0,
            "top_brand": meta.get("brands", ["—"])[0],
        })

    recent_brands = list(dict.fromkeys(
        e["brand"] for e in reversed(events) if e.get("brand")
    ))[:5]

    return {
        "user_id": user_id,
        "segment": segment,
        "segment_info": SEGMENTS.get(segment, {}),
        "engagement": get_engagement_level(total),
        "total_events": total,
        "unique_categories": len(prefs),
        "diversity_score": compute_diversity_score(prefs),
        "category_breakdown": category_breakdown,
        "recent_brands": recent_brands,
        "offer_count": len(offer_history.get(user_id, [])),
        "generated_at": time.strftime("%H:%M, %d %b %Y"),
    }

# Vercel ASGI handler
from mangum import Mangum
handler = Mangum(app)
