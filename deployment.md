<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>PERSONA — Deployment Guide</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@300;400;500&display=swap" rel="stylesheet"/>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#05050a;
  --s1:#0c0c14;
  --s2:#13131e;
  --border:#1c1c2e;
  --border2:#252538;
  --a1:#6c63ff;
  --a2:#ff4d8b;
  --a3:#00f5c8;
  --a4:#ffd166;
  --text:#eeeaf8;
  --muted:#5a5878;
  --muted2:#8882aa;
  --fd:'Syne',sans-serif;
  --fm:'JetBrains Mono',monospace;
  --r:8px;
}
body{
  background:var(--bg);color:var(--text);
  font-family:var(--fd);min-height:100vh;
  line-height:1.6;
}
body::before{
  content:'';position:fixed;inset:0;z-index:0;pointer-events:none;
  background-image:
    linear-gradient(rgba(108,99,255,.025) 1px,transparent 1px),
    linear-gradient(90deg,rgba(108,99,255,.025) 1px,transparent 1px);
  background-size:52px 52px;
}
body::after{
  content:'';position:fixed;inset:0;z-index:0;pointer-events:none;
  background:radial-gradient(ellipse 70% 50% at 50% 0%,rgba(108,99,255,.07),transparent);
}

/* ── Layout ── */
.page{max-width:900px;margin:0 auto;padding:60px 32px 100px;position:relative;z-index:1;}

/* ── Header ── */
.guide-header{margin-bottom:60px;border-bottom:1px solid var(--border);padding-bottom:40px;}
.guide-tag{font-family:var(--fm);font-size:.62rem;letter-spacing:.25em;color:var(--a1);
  text-transform:uppercase;margin-bottom:16px;display:flex;align-items:center;gap:8px;}
.guide-tag::before{content:'//';color:var(--muted);}
h1{font-size:clamp(2.4rem,5vw,3.8rem);font-weight:800;letter-spacing:-.015em;
  line-height:1.05;margin-bottom:18px;}
h1 .grad{background:linear-gradient(90deg,var(--a1),var(--a2));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.guide-desc{font-size:.95rem;color:var(--muted2);max-width:560px;line-height:1.8;}

/* ── TOC ── */
.toc{background:var(--s1);border:1px solid var(--border2);border-radius:var(--r);
  padding:28px 32px;margin-bottom:60px;display:grid;
  grid-template-columns:1fr 1fr;gap:6px 40px;}
.toc-head{grid-column:1/-1;font-family:var(--fm);font-size:.6rem;letter-spacing:.2em;
  color:var(--muted);text-transform:uppercase;margin-bottom:14px;}
.toc a{display:flex;align-items:center;gap:10px;color:var(--muted2);text-decoration:none;
  font-family:var(--fm);font-size:.72rem;padding:5px 0;border-bottom:1px solid transparent;
  transition:color .2s;}
.toc a:hover{color:var(--a1);}
.toc-num{color:var(--a1);font-size:.58rem;min-width:24px;}

/* ── Section ── */
.section{margin-bottom:60px;}
.section-head{display:flex;align-items:center;gap:16px;margin-bottom:28px;
  padding-bottom:16px;border-bottom:1px solid var(--border);}
.section-num{font-family:var(--fm);font-size:.58rem;letter-spacing:.18em;
  color:var(--a1);background:rgba(108,99,255,.1);border:1px solid rgba(108,99,255,.2);
  padding:4px 10px;border-radius:999px;white-space:nowrap;}
.section-head h2{font-size:1.35rem;font-weight:700;letter-spacing:.02em;}
.section-head::after{content:'';flex:1;height:1px;
  background:linear-gradient(90deg,var(--border2),transparent);}

/* ── Step card ── */
.step{background:var(--s1);border:1px solid var(--border2);border-radius:var(--r);
  margin-bottom:12px;overflow:hidden;transition:border-color .2s;}
.step:hover{border-color:var(--border);}
.step-header{display:flex;align-items:flex-start;gap:16px;padding:20px 24px;}
.step-badge{width:32px;height:32px;border-radius:50%;flex-shrink:0;
  background:rgba(108,99,255,.12);border:1px solid rgba(108,99,255,.25);
  display:flex;align-items:center;justify-content:center;
  font-family:var(--fm);font-size:.7rem;color:var(--a1);font-weight:500;}
.step-content{flex:1;}
.step-title{font-weight:700;font-size:1rem;margin-bottom:6px;}
.step-body{font-size:.85rem;color:var(--muted2);line-height:1.75;}
.step-body a{color:var(--a1);text-decoration:none;}
.step-body a:hover{text-decoration:underline;}

/* ── Code block ── */
.code-block{background:#070710;border:1px solid var(--border);border-radius:6px;
  margin:14px 0;overflow:hidden;}
.code-head{background:var(--s2);padding:8px 16px;display:flex;align-items:center;
  justify-content:space-between;border-bottom:1px solid var(--border);}
.code-lang{font-family:var(--fm);font-size:.58rem;letter-spacing:.15em;
  color:var(--muted);text-transform:uppercase;}
.code-copy{font-family:var(--fm);font-size:.6rem;color:var(--muted2);
  background:transparent;border:1px solid var(--border2);padding:3px 10px;
  border-radius:4px;cursor:pointer;transition:all .2s;}
.code-copy:hover{border-color:var(--a3);color:var(--a3);}
pre{padding:18px 20px;overflow-x:auto;font-family:var(--fm);font-size:.78rem;
  line-height:1.8;color:#c9c4e8;}
pre .cm{color:var(--muted);}
pre .ck{color:var(--a1);}
pre .cs{color:var(--a3);}
pre .cv{color:var(--a4);}
pre .ca{color:var(--a2);}

/* ── Alert / note ── */
.alert{display:flex;gap:14px;padding:16px 20px;border-radius:var(--r);margin:16px 0;}
.alert.info{background:rgba(108,99,255,.07);border:1px solid rgba(108,99,255,.2);}
.alert.warn{background:rgba(255,209,102,.06);border:1px solid rgba(255,209,102,.2);}
.alert.ok  {background:rgba(0,245,200,.05);border:1px solid rgba(0,245,200,.2);}
.alert-icon{font-size:1rem;flex-shrink:0;margin-top:2px;}
.alert-body{font-size:.82rem;color:var(--muted2);line-height:1.7;}
.alert-body strong{font-weight:700;}
.alert.info .alert-body strong{color:var(--a1);}
.alert.warn .alert-body strong{color:var(--a4);}
.alert.ok  .alert-body strong{color:var(--a3);}

/* ── Env table ── */
.env-table{width:100%;border-collapse:collapse;margin:16px 0;}
.env-table th{font-family:var(--fm);font-size:.58rem;letter-spacing:.15em;
  color:var(--muted);text-transform:uppercase;padding:8px 16px;
  border-bottom:1px solid var(--border);text-align:left;background:var(--s2);}
.env-table td{padding:12px 16px;font-family:var(--fm);font-size:.75rem;
  border-bottom:1px solid var(--border);vertical-align:top;}
.env-table tr:last-child td{border-bottom:none;}
.env-table .key{color:var(--a1);}
.env-table .where{color:var(--muted2);}
.env-table .desc{color:var(--muted2);}
.env-table tr{background:var(--s1);}
.env-table tr:hover td{background:rgba(108,99,255,.04);}

/* ── Vercel env screenshot guide ── */
.env-steps{display:flex;flex-direction:column;gap:6px;margin:16px 0;}
.env-row{display:flex;align-items:center;gap:12px;background:var(--s2);
  border:1px solid var(--border2);border-radius:6px;padding:12px 16px;}
.env-arrow{color:var(--muted);font-size:.75rem;font-family:var(--fm);}
.env-path{font-family:var(--fm);font-size:.72rem;color:var(--text);}
.env-path span{color:var(--a1);}

/* ── Checklist ── */
.checklist{list-style:none;display:flex;flex-direction:column;gap:8px;margin:16px 0;}
.checklist li{display:flex;align-items:flex-start;gap:12px;font-size:.85rem;
  color:var(--muted2);line-height:1.6;}
.check-box{width:18px;height:18px;border:1px solid var(--border2);border-radius:4px;
  flex-shrink:0;margin-top:2px;display:flex;align-items:center;justify-content:center;
  font-size:.7rem;color:var(--a3);}

/* ── Pill badges ── */
.pill-row{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0;}
.pill{font-family:var(--fm);font-size:.65rem;padding:5px 14px;border-radius:999px;
  letter-spacing:.08em;}
.pill.purple{background:rgba(108,99,255,.12);border:1px solid rgba(108,99,255,.25);color:var(--a1);}
.pill.pink  {background:rgba(255,77,139,.1);border:1px solid rgba(255,77,139,.25);color:var(--a2);}
.pill.teal  {background:rgba(0,245,200,.08);border:1px solid rgba(0,245,200,.2);color:var(--a3);}
.pill.gold  {background:rgba(255,209,102,.08);border:1px solid rgba(255,209,102,.2);color:var(--a4);}

/* ── Success banner ── */
.success-banner{background:linear-gradient(135deg,rgba(108,99,255,.12),rgba(0,245,200,.06));
  border:1px solid rgba(108,99,255,.25);border-radius:var(--r);padding:32px;
  text-align:center;margin-top:60px;}
.success-banner h3{font-size:1.6rem;font-weight:800;margin-bottom:10px;}
.success-banner p{font-size:.88rem;color:var(--muted2);}
.success-banner .url{font-family:var(--fm);font-size:.82rem;color:var(--a3);
  background:rgba(0,245,200,.07);border:1px solid rgba(0,245,200,.2);
  padding:8px 20px;border-radius:4px;display:inline-block;margin-top:14px;}

/* ── Footer ── */
footer{text-align:center;margin-top:60px;padding-top:30px;
  border-top:1px solid var(--border);font-family:var(--fm);
  font-size:.65rem;color:var(--muted);letter-spacing:.1em;}

@media(max-width:640px){
  .page{padding:40px 20px 80px;}
  .toc{grid-template-columns:1fr;}
}
@keyframes fadein{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
.page>*{animation:fadein .5s ease both;}
</style>
</head>
<body>
<div class="page">

<!-- ── Header ── -->
<div class="guide-header">
  <div class="guide-tag">PERSONA v3 — Deployment Guide</div>
  <h1>Deploy to <span class="grad">Vercel</span><br>in 15 Minutes</h1>
  <p class="guide-desc">Step-by-step guide: GitHub → Supabase → Vercel. Gemini + Supabase fully wired up with environment variables.</p>
  <div class="pill-row">
    <span class="pill purple">FastAPI + Mangum</span>
    <span class="pill pink">Google Gemini 2.0 Flash</span>
    <span class="pill teal">Supabase</span>
    <span class="pill gold">Vercel Serverless</span>
  </div>
</div>

<!-- ── TOC ── -->
<div class="toc">
  <div class="toc-head">// Table of Contents</div>
  <a href="#s1"><span class="toc-num">01</span> Prerequisites</a>
  <a href="#s5"><span class="toc-num">05</span> Supabase Setup</a>
  <a href="#s2"><span class="toc-num">02</span> Project Structure</a>
  <a href="#s6"><span class="toc-num">06</span> Vercel Deploy</a>
  <a href="#s3"><span class="toc-num">03</span> Get API Keys</a>
  <a href="#s7"><span class="toc-num">07</span> Env Variables</a>
  <a href="#s4"><span class="toc-num">04</span> Push to GitHub</a>
  <a href="#s8"><span class="toc-num">08</span> Test &amp; Verify</a>
</div>

<!-- ══ SECTION 1 ══════════════════════════════════════════════ -->
<div class="section" id="s1">
  <div class="section-head">
    <span class="section-num">01 / PREREQUISITES</span>
    <h2>What You Need</h2>
  </div>

  <ul class="checklist">
    <li><div class="check-box">✓</div><span><strong style="color:var(--text)">GitHub account</strong> — free at github.com (for hosting your code)</span></li>
    <li><div class="check-box">✓</div><span><strong style="color:var(--text)">Vercel account</strong> — free at vercel.com (for deployment + serverless Python)</span></li>
    <li><div class="check-box">✓</div><span><strong style="color:var(--text)">Supabase account</strong> — free at supabase.com (for persistent storage)</span></li>
    <li><div class="check-box">✓</div><span><strong style="color:var(--text)">Gemini API Key</strong> — free at aistudio.google.com/app/apikey</span></li>
    <li><div class="check-box">✓</div><span><strong style="color:var(--text)">Git + Python 3.10+</strong> — installed locally</span></li>
  </ul>
</div>

<!-- ══ SECTION 2 ══════════════════════════════════════════════ -->
<div class="section" id="s2">
  <div class="section-head">
    <span class="section-num">02 / STRUCTURE</span>
    <h2>Project File Structure</h2>
  </div>

  <div class="code-block">
    <div class="code-head"><span class="code-lang">folder layout</span></div>
    <pre><span class="cm">persona-v3/</span>
<span class="cm">│</span>
<span class="ck">├── api/</span>
<span class="cm">│   └── </span><span class="cs">index.py</span>          <span class="cm">← FastAPI backend (replace with the new version)</span>
<span class="cm">│</span>
<span class="ck">├── public/</span>
<span class="cm">│   └── </span><span class="cs">index.html</span>        <span class="cm">← Frontend (no changes needed)</span>
<span class="cm">│</span>
<span class="cs">├── vercel.json</span>           <span class="cm">← Routing config (see below)</span>
<span class="cs">├── requirements.txt</span>      <span class="cm">← Replace with new version</span>
<span class="cs">├── .env</span>                  <span class="cm">← Local only — NEVER commit this</span>
<span class="cs">└── .gitignore</span>            <span class="cm">← Must include .env</span></pre>
  </div>

  <div class="alert warn">
    <div class="alert-icon">⚠</div>
    <div class="alert-body"><strong>Important:</strong> Make sure <code>.gitignore</code> includes <code>.env</code> so your API keys never get pushed to GitHub.</div>
  </div>

  <p style="font-size:.85rem;color:var(--muted2);margin-top:16px;">Your <code style="color:var(--a3)">vercel.json</code> should look like this:</p>
  <div class="code-block">
    <div class="code-head"><span class="code-lang">vercel.json</span><button class="code-copy" onclick="copyCode(this)">Copy</button></div>
    <pre><span class="cv">{</span>
  <span class="ck">"rewrites"</span><span class="cv">:</span> <span class="cv">[</span>
    <span class="cv">{</span> <span class="ck">"source"</span><span class="cv">:</span> <span class="cs">"/api/(.*)"</span><span class="cv">,</span> <span class="ck">"destination"</span><span class="cv">:</span> <span class="cs">"/api/index.py"</span> <span class="cv">}</span><span class="cv">,</span>
    <span class="cv">{</span> <span class="ck">"source"</span><span class="cv">:</span> <span class="cs">"/(.*)"</span><span class="cv">,</span>      <span class="ck">"destination"</span><span class="cv">:</span> <span class="cs">"/public/index.html"</span> <span class="cv">}</span>
  <span class="cv">]</span>
<span class="cv">}</span></pre>
  </div>
</div>

<!-- ══ SECTION 3 ══════════════════════════════════════════════ -->
<div class="section" id="s3">
  <div class="section-head">
    <span class="section-num">03 / API KEYS</span>
    <h2>Get Your API Keys</h2>
  </div>

  <div class="step">
    <div class="step-header">
      <div class="step-badge">A</div>
      <div class="step-content">
        <div class="step-title">Gemini API Key</div>
        <div class="step-body">
          Go to <a href="https://aistudio.google.com/app/apikey" target="_blank">aistudio.google.com/app/apikey</a>
          → Sign in with Google → Click <strong>"Create API Key"</strong> → Copy the key (starts with <code>AIzaSy...</code>).
          Free tier is enough for this project.
        </div>
      </div>
    </div>
  </div>

  <div class="step">
    <div class="step-header">
      <div class="step-badge">B</div>
      <div class="step-content">
        <div class="step-title">Supabase URL + Key</div>
        <div class="step-body">
          Go to <a href="https://supabase.com/dashboard" target="_blank">supabase.com/dashboard</a>
          → Open your project → <strong>Settings → API</strong><br><br>
          You need two things:<br>
          • <strong>Project URL</strong> — looks like <code>https://xxxx.supabase.co</code><br>
          • <strong>anon / public key</strong> — the long JWT token under "Project API Keys"
        </div>
      </div>
    </div>
  </div>

  <div class="alert info">
    <div class="alert-icon">ℹ</div>
    <div class="alert-body"><strong>Which Supabase key to use?</strong> Use the <code>anon</code> (public) key for the backend. If you enable Row Level Security (RLS) on your tables, also set up service-role key. For this demo project, anon key is fine.</div>
  </div>
</div>

<!-- ══ SECTION 4 ══════════════════════════════════════════════ -->
<div class="section" id="s4">
  <div class="section-head">
    <span class="section-num">04 / GITHUB</span>
    <h2>Push to GitHub</h2>
  </div>

  <div class="step">
    <div class="step-header">
      <div class="step-badge">1</div>
      <div class="step-content">
        <div class="step-title">Create .gitignore and .env</div>
        <div class="step-body">Before anything, make sure sensitive files are excluded:</div>
      </div>
    </div>
    <div class="code-block" style="margin:0 24px 20px;">
      <div class="code-head"><span class="code-lang">.gitignore</span></div>
      <pre><span class="cs">.env</span>
<span class="cm">__pycache__/</span>
<span class="cm">*.pyc</span>
<span class="cm">.vercel/</span></pre>
    </div>
    <div class="code-block" style="margin:0 24px 20px;">
      <div class="code-head"><span class="code-lang">.env &nbsp;(local only)</span></div>
      <pre><span class="ck">GEMINI_API_KEY</span>=<span class="cs">AIzaSy...your-key...</span>
<span class="ck">SUPABASE_URL</span>=<span class="cs">https://xxxx.supabase.co</span>
<span class="ck">SUPABASE_KEY</span>=<span class="cs">eyJh...your-anon-key...</span></pre>
    </div>
  </div>

  <div class="step">
    <div class="step-header">
      <div class="step-badge">2</div>
      <div class="step-content">
        <div class="step-title">Init git and push</div>
      </div>
    </div>
    <div class="code-block" style="margin:0 24px 20px;">
      <div class="code-head"><span class="code-lang">bash</span><button class="code-copy" onclick="copyCode(this)">Copy</button></div>
      <pre><span class="cm"># Inside your project folder</span>
git init
git add .
git commit -m <span class="cs">"PERSONA v3 — Gemini + Supabase"</span>

<span class="cm"># Create a new repo on github.com first, then:</span>
git remote add origin https://github.com/<span class="cv">YOUR_USERNAME</span>/persona-v3.git
git branch -M main
git push -u origin main</pre>
    </div>
  </div>

  <div class="alert ok">
    <div class="alert-icon">✓</div>
    <div class="alert-body"><strong>Tip:</strong> Create the GitHub repo with <em>no README</em> so the push doesn't conflict with existing files.</div>
  </div>
</div>

<!-- ══ SECTION 5 ══════════════════════════════════════════════ -->
<div class="section" id="s5">
  <div class="section-head">
    <span class="section-num">05 / SUPABASE</span>
    <h2>Create Tables in Supabase</h2>
  </div>

  <p style="font-size:.85rem;color:var(--muted2);margin-bottom:16px;">
    Go to your Supabase project → <strong>SQL Editor</strong> → New Query → paste and run:
  </p>

  <div class="code-block">
    <div class="code-head"><span class="code-lang">SQL — run in Supabase SQL Editor</span><button class="code-copy" onclick="copyCode(this)">Copy</button></div>
    <pre><span class="cm">-- Tracks every category click</span>
<span class="ck">create table if not exists</span> <span class="cs">user_events</span> (
  id         bigint generated always as identity primary key,
  user_id    text not null,
  category   text not null,
  brand      text,
  created_at timestamptz default now()
);

<span class="cm">-- Stores click counts per user per category</span>
<span class="ck">create table if not exists</span> <span class="cs">user_preferences</span> (
  id         bigint generated always as identity primary key,
  user_id    text not null,
  category   text not null,
  clicks     int default 1,
  unique (user_id, category)
);

<span class="cm">-- Stores each offer generation event</span>
<span class="ck">create table if not exists</span> <span class="cs">offer_history</span> (
  id         bigint generated always as identity primary key,
  user_id    text not null,
  segment    text,
  category   text,
  created_at timestamptz default now()
);

<span class="cm">-- Wishlist items</span>
<span class="ck">create table if not exists</span> <span class="cs">wishlist</span> (
  id                bigint generated always as identity primary key,
  user_id           text not null,
  name              text not null,
  category          text,
  price             text,
  discounted_price  text,
  rating            text,
  created_at        timestamptz default now()
);</pre>
  </div>

  <div class="alert info">
    <div class="alert-icon">ℹ</div>
    <div class="alert-body"><strong>Already have tables?</strong> The SQL uses <code>IF NOT EXISTS</code> — existing tables are safely skipped. Only missing ones will be created.</div>
  </div>
</div>

<!-- ══ SECTION 6 ══════════════════════════════════════════════ -->
<div class="section" id="s6">
  <div class="section-head">
    <span class="section-num">06 / VERCEL</span>
    <h2>Deploy on Vercel</h2>
  </div>

  <div class="step">
    <div class="step-header">
      <div class="step-badge">1</div>
      <div class="step-content">
        <div class="step-title">Import your GitHub repo</div>
        <div class="step-body">
          Go to <a href="https://vercel.com/new" target="_blank">vercel.com/new</a>
          → Click <strong>"Import Git Repository"</strong>
          → Select <code>persona-v3</code>
          → Leave all settings as default
          → Click <strong>"Deploy"</strong>
        </div>
      </div>
    </div>
  </div>

  <div class="alert warn">
    <div class="alert-icon">⚠</div>
    <div class="alert-body"><strong>First deploy will work but AI won't.</strong> That's expected — the environment variables (API keys) haven't been added yet. Do this next.</div>
  </div>

  <div class="step">
    <div class="step-header">
      <div class="step-badge">2</div>
      <div class="step-content">
        <div class="step-title">Add Environment Variables</div>
        <div class="step-body">In Vercel dashboard → your project → <strong>Settings → Environment Variables</strong></div>
      </div>
    </div>
  </div>

  <div class="step">
    <div class="step-header">
      <div class="step-badge">3</div>
      <div class="step-content">
        <div class="step-title">Redeploy after adding keys</div>
        <div class="step-body">Vercel dashboard → <strong>Deployments tab</strong> → Click <strong>⋯</strong> on the latest → <strong>Redeploy</strong></div>
      </div>
    </div>
  </div>
</div>

<!-- ══ SECTION 7 ══════════════════════════════════════════════ -->
<div class="section" id="s7">
  <div class="section-head">
    <span class="section-num">07 / ENV VARS</span>
    <h2>Environment Variables Reference</h2>
  </div>

  <p style="font-size:.85rem;color:var(--muted2);margin-bottom:16px;">
    Add all three in Vercel → Settings → Environment Variables. Check <strong>Production ✓ Preview ✓ Development ✓</strong> for each.
  </p>

  <table class="env-table">
    <thead>
      <tr>
        <th>Variable Name</th>
        <th>Value / Where to get it</th>
        <th>Example</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="key">GEMINI_API_KEY</td>
        <td class="where">aistudio.google.com → API Keys</td>
        <td class="desc"><code>AIzaSy...32chars...</code></td>
      </tr>
      <tr>
        <td class="key">SUPABASE_URL</td>
        <td class="where">Supabase → Settings → API → Project URL</td>
        <td class="desc"><code>https://xxxx.supabase.co</code></td>
      </tr>
      <tr>
        <td class="key">SUPABASE_KEY</td>
        <td class="where">Supabase → Settings → API → anon public key</td>
        <td class="desc"><code>eyJhbGci...long JWT...</code></td>
      </tr>
    </tbody>
  </table>

  <div class="alert warn">
    <div class="alert-icon">⚠</div>
    <div class="alert-body"><strong>Redeploy required!</strong> After adding or changing environment variables, always Redeploy — Vercel does not automatically restart with new env vars.</div>
  </div>

  <p style="font-size:.85rem;color:var(--muted2);margin:20px 0 10px;">For local development, create a <code>.env</code> file in the root:</p>
  <div class="code-block">
    <div class="code-head"><span class="code-lang">bash — local dev</span><button class="code-copy" onclick="copyCode(this)">Copy</button></div>
    <pre><span class="cm"># Install dependencies</span>
pip install -r requirements.txt

<span class="cm"># Start local server</span>
uvicorn api.index:app --reload --port 8000

<span class="cm"># Open browser at</span>
<span class="cs">http://localhost:8000</span></pre>
  </div>
</div>

<!-- ══ SECTION 8 ══════════════════════════════════════════════ -->
<div class="section" id="s8">
  <div class="section-head">
    <span class="section-num">08 / VERIFY</span>
    <h2>Test &amp; Verify</h2>
  </div>

  <div class="step">
    <div class="step-header">
      <div class="step-badge">1</div>
      <div class="step-content">
        <div class="step-title">Health check</div>
        <div class="step-body">Visit this URL in browser — should return JSON:</div>
      </div>
    </div>
    <div class="code-block" style="margin:0 24px 20px;">
      <div class="code-head"><span class="code-lang">browser / curl</span><button class="code-copy" onclick="copyCode(this)">Copy</button></div>
      <pre>https://<span class="cv">your-project</span>.vercel.app/api/health

<span class="cm">Expected response:</span>
<span class="cv">{ "status": "ok", "engine": "PERSONA v3 — Supabase + Gemini" }</span></pre>
    </div>
  </div>

  <div class="step">
    <div class="step-header">
      <div class="step-badge">2</div>
      <div class="step-content">
        <div class="step-title">Test the full flow</div>
        <div class="step-body">Open your deployed site → click 3–4 category tiles → click "Generate All Outputs" → should produce 8 AI outputs.</div>
      </div>
    </div>
  </div>

  <div class="step">
    <div class="step-header">
      <div class="step-badge">3</div>
      <div class="step-content">
        <div class="step-title">Verify Supabase data</div>
        <div class="step-body">Go to Supabase → <strong>Table Editor</strong> → check <code>user_events</code> and <code>user_preferences</code> tables — rows should appear after each click.</div>
      </div>
    </div>
  </div>

  <div class="alert ok">
    <div class="alert-icon">✓</div>
    <div class="alert-body">
      <strong>Common issues &amp; fixes:</strong><br><br>
      <strong style="color:var(--text)">500 error on /api/generate-offer</strong> → GEMINI_API_KEY not set or wrong. Check Vercel env vars and Redeploy.<br><br>
      <strong style="color:var(--text)">Data not persisting after refresh</strong> → SUPABASE_URL or SUPABASE_KEY missing. Check env vars.<br><br>
      <strong style="color:var(--text)">404 on /api/* routes</strong> → vercel.json missing or wrong. Make sure the rewrites block is present.<br><br>
      <strong style="color:var(--text)">Module not found: google.genai</strong> → requirements.txt not updated. Replace with the new version and Redeploy.
    </div>
  </div>
</div>

<!-- ── Success Banner ── -->
<div class="success-banner">
  <h3>🎉 You're Live!</h3>
  <p>Your PERSONA AI Marketing Engine is deployed and fully operational.</p>
  <div class="url">https://your-project.vercel.app</div>
</div>

<footer>PERSONA v3 · FastAPI · Google Gemini 2.0 Flash · Supabase · Vercel</footer>

</div>

<script>
function copyCode(btn) {
  const pre = btn.closest('.code-block').querySelector('pre');
  const text = pre.innerText;
  navigator.clipboard.writeText(text).then(() => {
    btn.textContent = 'Copied!';
    setTimeout(() => btn.textContent = 'Copy', 2000);
  });
}
</script>
</body>
</html>
