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
import google.generativeai as genai
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

def gemini() -> genai:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise HTTPException(500, "GEMINI_API_KEY not set in environment variables.")
    genai.configure(api_key=key)
    return genai
def sb() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise HTTPException(500, "SUPABASE_URL / SUPABASE_KEY not set.")
    return create_client(url, key)


SUPABASE_READY = bool(os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_KEY"))

LOCAL_TABLES: dict[str, list[dict]] = {
    "user_events": [],
    "user_preferences": [],
    "offer_history": [],
    "wishlist": [],
}

LOCAL_NEXT_IDS: dict[str, int] = {name: 1 for name in LOCAL_TABLES}

GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
]


def call_gemini(prompt: str) -> str:
    api = gemini()
    last_error: Optional[Exception] = None
    for model_name in GEMINI_MODELS:
        try:
            print(f"DEBUG: Attempting Gemini call with model {model_name}...")
            model = api.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            text = getattr(response, "text", "")
            if text and text.strip():
                print(f"DEBUG: Successfully got response from {model_name}")
                return text.strip()

            print(f"DEBUG: Empty response from {model_name}")
            last_error = Exception(f"Empty response from {model_name}")
        except Exception as exc:
            last_error = exc
            err_text = str(exc).lower()
            print(f"DEBUG: Model {model_name} failed: {err_text}")

            if any(term in err_text for term in ["resource_exhausted", "quota", "429", "402"]):
                continue
            if "not found" in err_text or "invalid" in err_text:
                continue
            continue

    if last_error:
        err_msg = str(last_error)
        if "429" in err_msg or "quota" in err_msg.lower() or "402" in err_msg:
            raise HTTPException(
                status_code=429,
                detail="Gemini API quota exhausted. Please check your AI Studio billing or wait a minute."
            )
        raise HTTPException(status_code=502, detail=f"Gemini API Error: {err_msg}")

    raise HTTPException(status_code=503, detail="Gemini service unavailable.")


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _local_insert(table: str, row: dict) -> dict:
    record = dict(row)
    record.setdefault("id", LOCAL_NEXT_IDS[table])
    LOCAL_NEXT_IDS[table] += 1
    record.setdefault("created_at", _utc_now())
    LOCAL_TABLES[table].append(record)
    return record


def _local_rows(
    table: str,
    *,
    user_id: Optional[str] = None,
    order_desc: bool = False,
    limit: Optional[int] = None,
) -> list[dict]:
    rows = [dict(row) for row in LOCAL_TABLES[table]]
    if user_id is not None:
        rows = [row for row in rows if row.get("user_id") == user_id]
    if order_desc:
        rows = sorted(rows, key=lambda row: row.get("created_at", ""), reverse=True)
    if limit is not None:
        rows = rows[:limit]
    return rows


def _local_delete(table: str, **filters) -> int:
    kept: list[dict] = []
    removed = 0
    for row in LOCAL_TABLES[table]:
        if all(row.get(key) == value for key, value in filters.items()):
            removed += 1
            continue
        kept.append(row)
    LOCAL_TABLES[table] = kept
    return removed


def _local_upsert_pref(user_id: str, category: str) -> int:
    for row in LOCAL_TABLES["user_preferences"]:
        if row.get("user_id") == user_id and row.get("category") == category:
            row["clicks"] = int(row.get("clicks", 1)) + 1
            return row["clicks"]
    _local_insert("user_preferences", {"user_id": user_id, "category": category, "clicks": 1})
    return 1


def _local_prefs(user_id: str) -> dict[str, int]:
    prefs: dict[str, int] = {}
    for row in _local_rows("user_preferences", user_id=user_id):
        prefs[row["category"]] = int(row.get("clicks", 1))
    return prefs


def _persist_local_offer(user_id: str, segment: str, category: str) -> None:
    _local_insert("offer_history", {"user_id": user_id, "segment": segment, "category": category})


def _build_local_offer(
    *,
    user_id: str,
    segment: str,
    engage: str,
    div: float,
    top_cat: str,
    top_meta: dict,
    interest: str,
    brands: list[str],
    avg_price: int,
    ranked: list[tuple[str, int]],
) -> dict:
    brand = brands[0] if brands else "Top Brand"
    alt_brand = brands[1] if len(brands) > 1 else brand
    cat2 = ranked[1][0] if len(ranked) > 1 else top_cat
    cat3 = ranked[2][0] if len(ranked) > 2 else top_cat
    discount = 20 if engage in ("hot", "super-engaged") else 18
    savings_amount = int(round(avg_price * 70 * discount / 100))
    headline_root = interest.title()
    return {
        "promo": {
            "badge": "TODAY" if engage != "cold" else "NEW",
            "headline": f"🔥 Exclusive {headline_root} Deals!",
            "subtext": f"You've shown real interest in {interest} — grab {discount}% off top picks today only.",
            "discount": str(discount),
            "brand": brand,
            "cta": "Shop Now →",
            "savings_amount": f"{savings_amount:,}",
            "expiry": "Ends at midnight tonight" if engage != "cold" else "Limited time offer",
        },
        "ab_variant": {
            "badge": "FLASH",
            "headline": f"⚡ Last Chance — {headline_root} Sale",
            "subtext": f"Don't miss your window — {interest} prices are moving fast for the next few hours.",
            "cta": "Grab the Deal →",
            "discount": str(min(discount + 2, 35)),
        },
        "email": {
            "subject": f"{top_meta.get('emoji', '✨')} Your exclusive {headline_root} offer expires tonight",
            "preview": f"Don't let this deal slip away on {interest}.",
            "body": (
                f"Hi there! We noticed you've been exploring {interest} on our platform.\n\n"
                f"Based on your interests, we've curated an exclusive {discount}% discount on top {interest} picks from {brand}.\n\n"
                f"This offer is valid for today only — don't miss out. Click below to explore your personalized picks.\n\n"
                f"Happy Shopping! 🛍️\n— Team PERSONA"
            ),
        },
        "whatsapp": (
            f"Hey! 👋 Spotted you checking out {interest} 😍\n\n"
            f"We've got an *exclusive {discount}% OFF* on {brand} today only! ⚡\n\n"
            f"Grab it before it's gone 👉 [LINK] 🔥"
        ),
        "instagram": {
            "caption": (
                f"Your {interest} era is calling ✨\n\n"
                f"Exclusive {discount}% off – today only. Link in bio 🔗\n\n"
                f"#PERSONA #ShopNow #LimitedOffer #TodayOnly #{top_cat.title()} #{segment.replace(' ', '')} #Deals"
            ),
            "story_text": f"{discount}% OFF {top_cat.upper()} 🔥",
        },
        "products": [
            {
                "name": f"{brand} Premium {headline_root} Pro",
                "category": top_cat,
                "price": f"₹{avg_price * 70:,}",
                "discounted_price": f"₹{int(avg_price * 70 * (100 - discount) / 100):,}",
                "rating": "4.7",
                "reviews": 2340,
                "tag": "BESTSELLER",
                "reason": f"Perfect match for your {interest} interest with top ratings.",
            },
            {
                "name": f"{alt_brand} {headline_root} Edition",
                "category": cat2,
                "price": f"₹{int(avg_price * 55):,}",
                "discounted_price": f"₹{int(avg_price * 55 * (100 - discount) / 100):,}",
                "rating": "4.5",
                "reviews": 1200,
                "tag": "TRENDING",
                "reason": "A fan favourite that's been flying off shelves this week.",
            },
            {
                "name": f"{headline_root} Essentials Bundle",
                "category": cat3,
                "price": f"₹{int(avg_price * 80):,}",
                "discounted_price": f"₹{int(avg_price * 80 * (100 - discount) / 100):,}",
                "rating": "4.8",
                "reviews": 890,
                "tag": "NEW ARRIVAL",
                "reason": f"Our top recommendation for {interest} lovers like you.",
            },
        ],
        "insights": {
            "personalization_score": 82 if engage != "cold" else 68,
            "conversion_probability": 67 if engage != "cold" else 48,
            "best_send_time": "Tonight at 8 PM" if engage != "cold" else "Tomorrow afternoon",
            "primary_trigger": "FOMO" if engage != "cold" else "Curiosity",
            "segment_note": f"This {segment.lower()} profile responds to urgency-based triggers and tailored offers.",
            "upsell_hint": f"Suggest accessories or a bundle that complements {interest} for a larger basket size.",
        },
        "meta": {
            "user_id": user_id,
            "segment": segment,
            "segment_info": SEGMENTS.get(segment, {}),
            "engagement": engage,
            "top_category": top_cat,
            "top_interest": interest,
            "total_events": sum(count for _, count in ranked),
            "diversity_score": div,
            "generated_at": time.strftime("%H:%M, %d %b %Y"),
            "fallback": True,
        },
    }
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
    return {
        "status": "ok",
        "engine": "PERSONA v3 — Supabase + Gemini",
        "storage": "supabase" if SUPABASE_READY else "local-fallback",
        "ai": "gemini" if os.environ.get("GEMINI_API_KEY") else "local-fallback",
    }


@app.post("/api/track-event")
async def track_event(req: TrackReq):
    cat  = req.category.lower().strip()
    meta = CATEGORY_META.get(cat, {})
    brand = req.brand or (meta.get("brands", ["Unknown"])[0])

    # Persist to Supabase
    new_clicks = upsert_pref(req.user_id, cat)
    try:
        if SUPABASE_READY:
            sb().table("user_events").insert({
                "user_id":  req.user_id,
                "category": cat,
                "brand":    brand,
            }).execute()
        else:
            _local_insert("user_events", {
                "user_id": req.user_id,
                "category": cat,
                "brand": brand,
            })
    except Exception:
        _local_insert("user_events", {
            "user_id": req.user_id,
            "category": cat,
            "brand": brand,
        })

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

    try:
        # ── Gemini call (new SDK) ──────────────────────────────────────────────
        text = call_gemini(prompt)

        # Strip markdown fences if model wraps output anyway
        if "```" in text:
            text = "\n".join(
                line for line in text.split("\n")
                if not line.strip().startswith("```")
            )

        offer = json.loads(text.strip())
    except Exception:
        offer = _build_local_offer(
            user_id=user_id,
            segment=segment,
            engage=engage,
            div=div,
            top_cat=top_cat,
            top_meta=top_meta,
            interest=interest,
            brands=brands,
            avg_price=avg_price,
            ranked=ranked,
        )

    # ── Persist offer to history ───────────────────────────────────────────────
    try:
        if SUPABASE_READY:
            sb().table("offer_history").insert({
                "user_id":  user_id,
                "segment":  segment,
                "category": top_cat,
            }).execute()
        else:
            _persist_local_offer(user_id, segment, top_cat)
    except Exception:
        _persist_local_offer(user_id, segment, top_cat)

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
        "fallback":      offer.get("meta", {}).get("fallback", False),
        "ai_mode":       "local-fallback" if offer.get("meta", {}).get("fallback", False) else "gemini",
    }
    return offer


@app.get("/api/dashboard/{user_id}")
async def dashboard(user_id: str):
    prefs  = get_prefs(user_id)
    total  = sum(prefs.values())
    recent_brands: list[str] = []
    offer_count = 0
    if SUPABASE_READY:
        try:
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
                dict.fromkeys(e["brand"] for e in (events_res.data or []) if e.get("brand"))
            )[:5]

            offers_res = client.table("offer_history").select("id").eq("user_id", user_id).execute()
            offer_count = len(offers_res.data or [])
        except Exception:
            recent_brands = list(
                dict.fromkeys(row["brand"] for row in _local_rows("user_events", user_id=user_id, order_desc=True, limit=30) if row.get("brand"))
            )[:5]
            offer_count = len(_local_rows("offer_history", user_id=user_id))
    else:
        recent_brands = list(
            dict.fromkeys(row["brand"] for row in _local_rows("user_events", user_id=user_id, order_desc=True, limit=30) if row.get("brand"))
        )[:5]
        offer_count = len(_local_rows("offer_history", user_id=user_id))

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
        "offer_count":       offer_count,
        "generated_at":      time.strftime("%H:%M, %d %b %Y"),
    }


@app.get("/api/history/{user_id}")
async def history(user_id: str):
    if SUPABASE_READY:
        try:
            res = (
                sb().table("offer_history")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(10)
                .execute()
            )
            return {"history": res.data or []}
        except Exception:
            pass
    return {"history": _local_rows("offer_history", user_id=user_id, order_desc=True, limit=10)}


@app.post("/api/wishlist/add")
async def wishlist_add(req: WishlistAddReq):
    try:
        if SUPABASE_READY:
            sb().table("wishlist").insert({
                "user_id":          req.user_id,
                "name":             req.name,
                "category":         req.category,
                "price":            req.price,
                "discounted_price": req.discounted_price,
                "rating":           req.rating,
            }).execute()
        else:
            _local_insert("wishlist", {
                "user_id":          req.user_id,
                "name":             req.name,
                "category":         req.category,
                "price":            req.price,
                "discounted_price": req.discounted_price,
                "rating":           req.rating,
            })
    except Exception:
        _local_insert("wishlist", {
            "user_id":          req.user_id,
            "name":             req.name,
            "category":         req.category,
            "price":            req.price,
            "discounted_price": req.discounted_price,
            "rating":           req.rating,
        })
    return {"status": "added", "name": req.name}


@app.get("/api/wishlist/{user_id}")
async def wishlist_get(user_id: str):
    if SUPABASE_READY:
        try:
            res = sb().table("wishlist").select("*").eq("user_id", user_id).execute()
            return {"wishlist": res.data or []}
        except Exception:
            pass
    return {"wishlist": _local_rows("wishlist", user_id=user_id)}


@app.delete("/api/wishlist/{user_id}/{name}")
async def wishlist_remove(user_id: str, name: str):
    try:
        if SUPABASE_READY:
            sb().table("wishlist").delete().eq("user_id", user_id).eq("name", name).execute()
        else:
            _local_delete("wishlist", user_id=user_id, name=name)
    except Exception:
        _local_delete("wishlist", user_id=user_id, name=name)
    return {"status": "removed", "name": name}


@app.delete("/api/reset/{user_id}")
async def reset_user(user_id: str):
    try:
        if SUPABASE_READY:
            client = sb()
            for table in ("user_events", "user_preferences", "offer_history", "wishlist"):
                client.table(table).delete().eq("user_id", user_id).execute()
        else:
            for table in ("user_events", "user_preferences", "offer_history", "wishlist"):
                _local_delete(table, user_id=user_id)
    except Exception:
        for table in ("user_events", "user_preferences", "offer_history", "wishlist"):
            _local_delete(table, user_id=user_id)
    return {"status": "reset", "user_id": user_id}


# ── Vercel ASGI adapter ────────────────────────────────────────────────────────
handler = Mangum(app)
