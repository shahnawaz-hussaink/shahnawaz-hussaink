"""Build every image the profile README uses, in a dark and a light theme.

    python3 scripts/build.py

Writes assets/dark/*.svg, assets/light/*.svg and assets/terminal.svg.
Live numbers (GitHub, LeetCode, recent activity) are fetched on each run; if a
source is unreachable, the last good values in scripts/cache.json are used.
Standard library only, so the GitHub Action needs no installs.

Text lives in the CONTENT section below. Edit it there, then run the script.
"""

import html
import json
import os
import sys
import textwrap
import urllib.request
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
CACHE = os.path.join(ROOT, "scripts", "cache.json")
FLOW_SRC = os.path.join(ROOT, "scripts", "request-flow.src.svg")
with open(os.path.join(ROOT, "scripts", "icons.json"), encoding="utf-8") as f:
    ICONS = json.load(f)  # from simple-icons (CC0): slug -> {title, hex, path}

GITHUB_USER = "shahnawaz-hussaink"
LEETCODE_USER = "shahnawazhussaink"
IST = timezone(timedelta(hours=5, minutes=30))

W = 840
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"
CW = 0.61  # monospace advance width per em, slightly generous so text never overflows

THEMES = {
    "dark": dict(
        page="#0d1117", surface="#161b22", surface2="#1c2128", border="#30363d",
        text="#e6edf3", muted="#8b949e", faint="#6e7681", accent="#3fb950", on_accent="#0d1117",
        link="#58a6ff", amber="#d29922", red="#f85149", purple="#a371f7", cyan="#79c0ff",
        glow=0.22, dots=0.55,
    ),
    "light": dict(
        page="#ffffff", surface="#f6f8fa", surface2="#ffffff", border="#d0d7de",
        text="#1f2328", muted="#59636e", faint="#818b98", accent="#1a7f37", on_accent="#ffffff",
        link="#0969da", amber="#9a6700", red="#cf222e", purple="#8250df", cyan="#0550ae",
        glow=0.12, dots=0.8,
    ),
}

# Colors swapped when deriving the light stack diagram from the dark source.
FLOW_LIGHT = {
    "#0d1117": "#f6f8fa", "#161b22": "#ffffff", "#30363d": "#d0d7de", "#e6edf3": "#1f2328",
    "#8b949e": "#59636e", "#3fb950": "#1a7f37", "#79c0ff": "#0969da", "#d29922": "#9a6700",
    "#f85149": "#cf222e", "#a371f7": "#8250df", "#f0883e": "#bc4c00",
}

# ---------------------------------------------------------------- CONTENT

HERO_TAGLINE = [
    "Backend developer. I build the parts of a product you never see:",
    "APIs, job queues, locks and caches, and what happens to them under load.",
]
HERO_NOW = [
    "real-time data-ingestion APIs @ CyPSi Lab, DU",
    "row-level locking in PostgreSQL",
    "BullMQ job queues and workers",
    "Redis caching and rate limiting",
    "Go concurrency patterns",
]
HERO_CHIPS = [
    ("open to opportunities", True),
    ("Developer @ SamarthX eGov", False),
    ("CS @ ARSD College, University of Delhi", False),
]

NAV = [("GET", "/whoami"), ("GET", "/stack"), ("GET", "/projects"),
       ("GET", "/experience"), ("GET", "/metrics"), ("POST", "/hire")]

SECTIONS = {
    "whoami": ("01", "About", "GET", "/v1/whoami", "Who's behind the API."),
    "stack": ("02", "Stack", "GET", "/v1/stack", "Follow a request through everything I build with."),
    "projects": ("03", "Projects", "GET", "/v1/projects?sort=hardest_problem", "Each one exists because of one hard problem."),
    "experience": ("04", "Experience", "GET", "/v1/experience", "Where I've shipped, and what I did there."),
    "metrics": ("05", "Metrics", "GET", "/v1/metrics", "Live. Refreshed every morning by a GitHub Action I wrote."),
    "hire": ("06", "Contact", "POST", "/v1/hire", "No SDK, no auth token. Just send it."),
}

# icon key: a simple-icons slug from icons.json, or a GLYPHS name
STACK = [
    ("languages", [("go", "Go"), ("typescript", "TypeScript"), ("javascript", "JavaScript"),
                   ("python", "Python"), ("cplusplus", "C++")]),
    ("backend", [("nodedotjs", "Node.js"), ("express", "Express"), ("fastapi", "FastAPI"),
                 ("graphql", "GraphQL"), ("jsonwebtokens", "JWT"), ("socket", "WebSockets")]),
    ("data", [("postgresql", "PostgreSQL"), ("mongodb", "MongoDB"), ("mysql", "MySQL"),
              ("redis", "Redis"), ("prisma", "Prisma"), ("queue", "BullMQ")]),
    ("cloud & tools", [("docker", "Docker"), ("cloud", "AWS"), ("git", "Git"),
                       ("vercel", "Vercel"), ("supabase", "Supabase"), ("firebase", "Firebase")]),
    ("frontend", [("react", "React"), ("nextdotjs", "Next.js"), ("angular", "Angular"),
                  ("tailwindcss", "Tailwind CSS")]),
]

PROJECTS = [
    dict(slug="irctc", repo="irctc-backend", kicker="railway booking engine", color="#4169E1",
         desc="Two users, one seat, same millisecond. SELECT\u00a0…\u00a0FOR\u00a0UPDATE row locks in ACID "
              "transactions, 10-min TTL seat holds, BullMQ waitlist workers.",
         stack=["postgresql", "prisma", "redis", "queue"]),
    dict(slug="debug-arena", repo="debug-arena", kicker="live DSA tournament platform", color="#3fb950",
         demo=True,
         desc="Hosted a live multi-college tournament for 35+ participants, crash-free. Strict "
              "timers, real-time monitoring, Judge0 code execution.",
         stack=["react", "express", "firebase"]),
    dict(slug="videotube", repo="Backend_Video_Tube", kicker="YouTube-style backend", color="#47A248",
         desc="The whole content lifecycle: Cloudinary uploads, JWT access/refresh rotation, "
              "subscriptions, comments, aggregation pipelines for watch history.",
         stack=["nodedotjs", "mongodb", "cloudinary"]),
    dict(slug="otp", repo="otp-verification-system", kicker="OTP over email and SMS", color="#FF4438",
         desc="OTPs that expire on their own (Redis TTL), resist brute force (rate limits), and "
              "come from crypto, not Math.random.",
         stack=["nodedotjs", "redis", "express"]),
    dict(slug="url-shortener", repo="URL-Shortener", kicker="link management backend", color="#58a6ff",
         desc="Collision-resistant NanoID short codes, custom slugs, link expiry, IP geolocation "
              "and per-link click analytics.",
         stack=["nodedotjs", "express", "jsonwebtokens"]),
    dict(slug="mosai", repo="MOSAI CMS", owner="u-b-001/main", kicker="contributor · mosai.org.in",
         color="#a371f7",
         desc="Contributed to a headless CMS running in production: dynamic content collections, "
              "role-based access control, REST + GraphQL APIs.",
         stack=["typescript", "nextdotjs", "graphql"]),
]
STACK_LABELS = {k: v for _, items in STACK for k, v in items} | {"cloudinary": "Cloudinary"}

EXPERIENCE = [
    dict(date="Jun 2026 – now", kind="WORK", now=True, role="Developer",
         org="SamarthX eGov · Cyber Physical Systems (CyPSi) Lab, University of Delhi",
         points=["Real-time backend architectures and data-ingestion APIs",
                 "Backend systems + admin dashboards for CMS tools, built for scale and correctness"]),
    dict(date="Sep 2025 – Jan 2026", kind="WORK", role="Organising Conference Member",
         org="India's International Movement to Unite Nations (IIMUN)",
         points=["Ran operational workflows and scheduling for large virtual conferences",
                 "Led communications across university and high-school delegates"]),
    dict(date="Oct 2025", kind="EVENT", role="Pitchcraft", org="Hackathon · team CAFFeINE-CORRUPT",
         points=["AI rental platform: AI matching, a \"rental DNA\" score, verified listings",
                 "Next.js · FastAPI · Supabase"]),
    dict(date="Mar 2025", kind="EVENT", role="AceHack, Jaipur", org="Hackathon",
         points=["Expense tracker built as a team; I owned the React + Tailwind frontend"]),
]

CONTACT = [
    ("email", "Email me", "mail", True),
    ("linkedin", "LinkedIn", "linkedin", False),
    ("portfolio", "Portfolio", "globe", False),
    ("resume", "Resume", "doc", False),
    ("leetcode", "LeetCode", "leetcode", False),
    ("x", "X", "x", False),
    ("instagram", "Instagram", "instagram", False),
]

# ---------------------------------------------------------------- SVG HELPERS

GLYPHS = {  # 24x24, stroked
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.6 3.8 5.6 3.8 9s-1.3 6.4-3.8 9c-2.5-2.6-3.8-5.6-3.8-9S9.5 5.6 12 3z"/>',
    "doc": '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h6"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
    "linkedin": '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M8 11v6M8 7.5v.01M12 17v-6M12 13.5a2.5 2.5 0 0 1 5 0V17"/>',
    "cloud": '<path d="M7 18a4.5 4.5 0 0 1-.6-8.96A6 6 0 0 1 18 9.5a4.25 4.25 0 0 1-.5 8.5z"/>',
    "queue": '<rect x="4" y="4" width="16" height="4" rx="1.5"/><rect x="4" y="10" width="16" height="4" rx="1.5"/><rect x="4" y="16" width="16" height="4" rx="1.5"/>',
    "socket": '<path d="M4 9h14l-3-3M20 15H6l3 3"/>',
    "repo": '<path d="M5 19V5a2 2 0 0 1 2-2h12v14H7a2 2 0 0 0-2 2zm0 0a2 2 0 0 0 2 2h12v-4"/>',
}
STAR = "M12 3.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8L12 16.9l-5.2 2.7 1-5.8-4.3-4.1 5.9-.9z"

BASE_CSS = (
    "text{font-family:SANS}.m{font-family:MONO}"
    ".up{animation:up .6s cubic-bezier(.2,.7,.2,1) both}"
    ".fade{animation:fade .35s ease-out both}"
    ".pulse{transform-box:fill-box;transform-origin:center;animation:pulse 2s ease-out infinite}"
    ".blink{animation:blink 1.1s step-end infinite}"
    "@keyframes up{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}"
    "@keyframes fade{from{opacity:0}to{opacity:1}}"
    "@keyframes pulse{0%{transform:scale(1);opacity:.6}100%{transform:scale(2.8);opacity:0}}"
    "@keyframes blink{0%{opacity:1}50%{opacity:0}}"
    "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
).replace("SANS", SANS).replace("MONO", MONO)


def esc(s):
    return html.escape(str(s), quote=True)


def mw(text, size):
    return len(text) * size * CW


def delay(s):
    return f' style="animation-delay:{s:.2f}s"'


def doc(w, h, title, body, css=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" '
            f'viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="{esc(title)}">'
            f'<title>{esc(title)}</title><style>{BASE_CSS}{css}</style>{body}</svg>\n')


def card(w, h, t, rx=14, fill=None):
    return (f'<rect x=".5" y=".5" width="{w - 1:.0f}" height="{h - 1:.0f}" rx="{rx}" '
            f'fill="{fill or t["surface"]}" stroke="{t["border"]}"/>')


def luminance(hex_color):
    def channel(c):
        c = int(c, 16) / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    h = hex_color.lstrip("#")
    return 0.2126 * channel(h[0:2]) + 0.7152 * channel(h[2:4]) + 0.0722 * channel(h[4:6])


def contrast(a, b):
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def brand(key, t, bg):
    """Brand color for an icon, or the theme's text color if the brand color would vanish on bg."""
    if key not in ICONS:
        return t["muted"]
    color = "#" + ICONS[key]["hex"]
    return color if contrast(color, bg) >= 2.2 else t["text"]


def icon(key, x, y, size, color):
    scale = f'translate({x:.1f},{y:.1f}) scale({size / 24:.4f})'
    if key in GLYPHS:
        return (f'<g transform="{scale}" fill="none" stroke="{color}" stroke-width="2" '
                f'stroke-linecap="round" stroke-linejoin="round">{GLYPHS[key]}</g>')
    return f'<g transform="{scale}"><path fill="{color}" d="{ICONS[key]["path"]}"/></g>'


def pill(x, y, w, h, color, opacity=0.12):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="{h / 2}" fill="{color}" '
            f'fill-opacity="{opacity}" stroke="{color}" stroke-opacity=".45"/>')


def live_dot(cx, cy, color, r=4):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}" class="pulse"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}"/>')


# ---------------------------------------------------------------- COMPONENTS

def hero(t):
    h = 300
    n, step = len(HERO_NOW), 3.2
    period = n * step
    css = ".ph{opacity:0}.ph0{opacity:1}"
    for k in range(n):
        a, b, e = 100 * k / n, 100 * (k + 1) / n, 2.5
        frames = [] if a == 0 else ["0%{opacity:0}"]
        frames += [f"{a:.2f}%{{opacity:0;transform:translateY(6px)}}",
                   f"{a + e:.2f}%{{opacity:1;transform:none}}",
                   f"{b - e:.2f}%{{opacity:1;transform:none}}",
                   f"{b:.2f}%{{opacity:0;transform:translateY(-6px)}}"]
        css += f"@keyframes ph{k}{{{''.join(frames)}}}.ph{k}{{animation:ph{k} {period}s linear infinite}}"
    css += (".scan{transform:translateX(-160px);animation:scan 7s ease-in-out 1s infinite}"
            "@keyframes scan{0%{transform:translateX(-160px)}60%,100%{transform:translateX(860px)}}")

    o = [f'<defs><clipPath id="c"><rect x=".5" y=".5" width="{W - 1}" height="{h - 1}" rx="16"/></clipPath>'
         f'<pattern id="d" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="{t["border"]}"/></pattern>'
         f'<radialGradient id="g1" cx="88%" cy="0%" r="65%"><stop offset="0" stop-color="{t["accent"]}" stop-opacity="{t["glow"]}"/><stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/></radialGradient>'
         f'<radialGradient id="g2" cx="0%" cy="100%" r="55%"><stop offset="0" stop-color="{t["link"]}" stop-opacity="{t["glow"] * .6:.3f}"/><stop offset="1" stop-color="{t["link"]}" stop-opacity="0"/></radialGradient>'
         f'<linearGradient id="s" x1="0" x2="1"><stop offset="0" stop-color="{t["accent"]}" stop-opacity="0"/><stop offset=".5" stop-color="{t["accent"]}"/><stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/></linearGradient></defs>',
         card(W, h, t, 16),
         f'<g clip-path="url(#c)"><rect width="{W}" height="{h}" fill="url(#d)" opacity="{t["dots"]}"/>'
         f'<rect width="{W}" height="{h}" fill="url(#g1)"/><rect width="{W}" height="{h}" fill="url(#g2)"/>'
         f'<rect class="scan" y="0" width="160" height="2" fill="url(#s)"/></g>']

    pw = mw("200 OK", 12) + 34
    o.append(f'<g class="up">{pill(40, 32, pw, 24, t["accent"])}{live_dot(53, 44, t["accent"])}'
             f'<text x="64" y="48.5" class="m" font-size="12" font-weight="700" fill="{t["accent"]}">200 OK</text>'
             f'<text x="{40 + pw + 12:.1f}" y="48.5" class="m" font-size="13" fill="{t["muted"]}">GET api.shahcodes.dev/v1/whoami</text>'
             f'<text x="{W - 40}" y="48.5" text-anchor="end" class="m" font-size="12.5" fill="{t["muted"]}">Delhi, India · UTC+5:30</text></g>')
    o.append(f'<text x="38" y="120" font-size="48" font-weight="800" letter-spacing="-1.2" fill="{t["text"]}" class="up"{delay(.1)}>Shahnawaz Hussain</text>')
    for i, line in enumerate(HERO_TAGLINE):
        o.append(f'<text x="40" y="{158 + i * 26}" font-size="18" fill="{t["muted"]}" class="up"{delay(.22 + i * .06)}>{esc(line)}</text>')

    prefix = "$ currently building: "
    px = 40 + mw(prefix, 14)
    o.append(f'<g class="up"{delay(.4)}><text x="40" y="232" class="m" font-size="14" fill="{t["muted"]}">'
             f'<tspan fill="{t["accent"]}">$</tspan> currently building:</text>')
    for k, phrase in enumerate(HERO_NOW):
        cx = px + mw(phrase, 14) + 3
        o.append(f'<g class="ph ph{k}"><text x="{px:.1f}" y="232" class="m" font-size="14" fill="{t["text"]}">{esc(phrase)}</text>'
                 f'<rect x="{cx:.1f}" y="219" width="8" height="17" fill="{t["accent"]}" class="blink"/></g>')
    o.append("</g>")

    x = 40
    for i, (label, status) in enumerate(HERO_CHIPS):
        w = mw(label, 12) + 28 + (14 if status else 0)
        color = t["accent"] if status else t["text"]
        chip = pill(x, 252, w, 30, t["accent"]) if status else (
            f'<rect x="{x:.1f}" y="252" width="{w:.1f}" height="30" rx="15" fill="{t["surface2"]}" stroke="{t["border"]}"/>')
        dot = live_dot(x + 16, 267, t["accent"]) if status else ""
        o.append(f'<g class="up"{delay(.55 + i * .08)}>{chip}{dot}<text x="{x + 14 + (14 if status else 0):.1f}" y="271.5" '
                 f'class="m" font-size="12" fill="{color}">{esc(label)}</text></g>')
        x += w + 10
    return doc(W, h, "Shahnawaz Hussain, backend developer in Delhi, open to opportunities", "".join(o), css)


def nav_button(t, method, path):
    mw_, pw = mw(method, 11.5), mw(path, 12.5)
    w, h = 16 + mw_ + 8 + pw + 16, 36
    color = t["accent"] if method == "GET" else t["amber"]
    body = (card(w, h, t, 18) +
            f'<text x="16" y="22.5" class="m" font-size="11.5" font-weight="700" fill="{color}">{method}</text>'
            f'<text x="{16 + mw_ + 8:.1f}" y="22.5" class="m" font-size="12.5" fill="{t["text"]}">{esc(path)}</text>')
    return doc(w, h, f"{method} {path}", body)


def section_header(t, num, title, method, endpoint, subtitle):
    h = 80
    ew = mw(endpoint, 12.5)
    color = t["accent"] if method == "GET" else t["amber"]
    body = (f'<g class="up"><text x="0" y="36" class="m" font-size="13" font-weight="700" fill="{t["accent"]}">{num}</text>'
            f'<text x="32" y="37" font-size="25" font-weight="700" letter-spacing="-.3" fill="{t["text"]}">{esc(title)}</text>'
            f'<text x="{W - ew - 8:.1f}" y="36" text-anchor="end" class="m" font-size="11.5" font-weight="700" fill="{color}">{method}</text>'
            f'<text x="{W}" y="36" text-anchor="end" class="m" font-size="12.5" fill="{t["muted"]}">{esc(endpoint)}</text>'
            f'<text x="32" y="61" font-size="14.5" fill="{t["muted"]}">{esc(subtitle)}</text></g>'
            f'<rect x="0" y="77" width="{W}" height="1" fill="{t["border"]}"/>'
            f'<rect x="0" y="76" width="64" height="2" rx="1" fill="{t["accent"]}"/>')
    return doc(W, h, f"{num} {title}: {method} {endpoint}. {subtitle}", body)


def terminal():
    """The whoami terminal. Dark in both themes: it's a terminal window."""
    bg, fg, muted, green, key, string = "#0d1117", "#e6edf3", "#8b949e", "#3fb950", "#79c0ff", "#a5d6ff"
    cmd = "curl -s api.shahcodes.dev/v1/whoami | jq"
    tl = len(cmd) * 8.4

    def kv(k, v, comma=True):
        if isinstance(v, list):
            val = "[" + ", ".join(f'<tspan fill="{string}">"{esc(x)}"</tspan>' for x in v) + "]"
        else:
            val = f'<tspan fill="{string}">"{esc(v)}"</tspan>'
        return f'  <tspan fill="{key}">"{k}"</tspan>: {val}' + ("," if comma else "")

    lines = [
        f'<tspan fill="{green}" font-weight="700">HTTP/1.1 200 OK</tspan><tspan fill="{muted}">  ·  12ms  ·  x-cache: HIT (redis)</tspan>',
        f'<tspan fill="{muted}">x-powered-by:</tspan> Node.js, Go, chai ☕',
        f'<tspan fill="{muted}">x-ratelimit-remaining:</tspan> ∞',
        "",
        "{",
        kv("name", "Shahnawaz Hussain"),
        kv("role", "Backend Developer"),
        kv("based_in", "Delhi, India"),
        kv("currently", "Developer @ SamarthX eGov · CyPSi Lab, DU"),
        kv("studying", "CS @ ARSD College, University of Delhi"),
        kv("speaks", ["Go", "JavaScript", "TypeScript", "C++", "Python"]),
        kv("stores_data_in", ["PostgreSQL", "MongoDB", "Redis"]),
        kv("obsessed_with", "race conditions, caching & what breaks under load"),
        kv("status", "open_to_opportunities", comma=False),
        "}",
    ]
    h = 95 + 23 * len(lines) + 37
    steps = len(cmd)
    css = (f".cover{{transform:translateX({tl + 10:.1f}px);animation:type 2s steps({steps}) .6s both}}"
           f".cur{{transform:translateX({tl:.1f}px);animation:type2 2s steps({steps}) .6s both,hide .9s step-end 2.6s 3 forwards}}"
           f"@keyframes type{{from{{transform:translateX(0)}}to{{transform:translateX({tl + 10:.1f}px)}}}}"
           f"@keyframes type2{{from{{transform:translateX(0)}}to{{transform:translateX({tl:.1f}px)}}}}"
           "@keyframes hide{0%{opacity:1}50%,100%{opacity:0}}")
    o = [f'<rect x=".5" y=".5" width="{W - 1}" height="{h - 1}" rx="12" fill="{bg}" stroke="#30363d"/>',
         f'<path d="M.5 36V12.5a12 12 0 0 1 12-12H{W - 12.5}a12 12 0 0 1 12 12V36z" fill="#161b22"/>',
         f'<line x1=".5" y1="36" x2="{W - .5}" y2="36" stroke="#30363d"/>',
         '<circle cx="22" cy="18" r="6" fill="#ff5f57"/><circle cx="42" cy="18" r="6" fill="#febc2e"/><circle cx="62" cy="18" r="6" fill="#28c840"/>',
         f'<text x="{W / 2}" y="22.5" text-anchor="middle" class="m" font-size="12" fill="{muted}">shahnawaz@backend — zsh</text>',
         f'<text x="24" y="72" class="m" font-size="14" xml:space="preserve"><tspan fill="{green}" font-weight="700">➜</tspan>  <tspan fill="{key}">~</tspan></text>',
         f'<text x="66" y="72" class="m" font-size="14" fill="{fg}" textLength="{tl:.1f}" lengthAdjust="spacing">{esc(cmd)}</text>',
         f'<rect class="cover" x="66" y="56" width="{tl + 12:.1f}" height="22" fill="{bg}"/>',
         f'<rect class="cur" x="66" y="59" width="8" height="16" fill="{fg}"/>']
    y, d = 95, 3.0
    for ln in lines:
        o.append(f'<text x="24" y="{y}" class="m fade" font-size="14" fill="{fg}" xml:space="preserve"{delay(d)}>{ln}</text>')
        y, d = y + 23, d + 0.11
    o.append(f'<g class="fade"{delay(d + .2)}><text x="24" y="{y}" class="m" font-size="14" xml:space="preserve">'
             f'<tspan fill="{green}" font-weight="700">➜</tspan>  <tspan fill="{key}">~</tspan></text>'
             f'<rect x="66" y="{y - 13}" width="8" height="16" fill="{fg}" class="blink"/></g>')
    return doc(W, h, "curl api.shahcodes.dev/v1/whoami: Shahnawaz Hussain, Backend Developer in Delhi. "
               "Developer at SamarthX eGov, CyPSi Lab, University of Delhi. CS at ARSD College. "
               "Speaks Go, JavaScript, TypeScript, C++, Python. Stores data in PostgreSQL, MongoDB, Redis.",
               "".join(o), css)


def flow(theme):
    with open(FLOW_SRC, encoding="utf-8") as f:
        svg = f.read()
    if theme == "light":
        for dark, light in FLOW_LIGHT.items():
            svg = svg.replace(dark, light)
    return svg


def stack(t):
    pad, x0, row_h = 24, 168, 44
    o, y = [], pad
    i = 0
    for gi, (label, items) in enumerate(STACK):
        if gi:
            o.append(f'<rect x="{pad}" y="{y - 7}" width="{W - 2 * pad}" height="1" fill="{t["border"]}" opacity=".6"/>')
        o.append(f'<text x="{pad}" y="{y + 20.5}" class="m" font-size="11" letter-spacing="1.4" fill="{t["muted"]}">{esc(label.upper())}</text>')
        x = x0
        for key, name in items:
            w = 36 + mw(name, 12.5) + 14
            if x + w > W - pad:
                x, y = x0, y + row_h - 4
            o.append(f'<g class="up"{delay(.05 + i * .03)}>'
                     f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="32" rx="8" fill="{t["surface2"]}" stroke="{t["border"]}"/>'
                     f'{icon(key, x + 11, y + 8, 16, brand(key, t, t["surface2"]))}'
                     f'<text x="{x + 36:.1f}" y="{y + 20.5}" class="m" font-size="12.5" fill="{t["text"]}">{esc(name)}</text></g>')
            x += w + 8
            i += 1
        y += row_h + 10
    h = y - 10 + pad - 10
    names = "; ".join(f"{label}: " + ", ".join(n for _, n in items) for label, items in STACK)
    return doc(W, h, f"Tech stack. {names}", card(W, h, t) + "".join(o))


def project_card(t, p, stars):
    w, h = 410, 204
    o = [f'<defs><clipPath id="c"><rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="12"/></clipPath></defs>',
         card(w, h, t, 12),
         f'<rect clip-path="url(#c)" width="{w}" height="3" fill="{p["color"]}"/>',
         icon("repo", 20, 21, 16, t["muted"]),
         f'<text x="44" y="34" class="m" font-size="15" font-weight="700" fill="{t["link"]}">{esc(p["repo"])}</text>']
    right = w - 20
    if stars:
        sw = mw(str(stars), 12)
        o.append(f'<text x="{right}" y="34" text-anchor="end" class="m" font-size="12" fill="{t["muted"]}">{stars}</text>'
                 f'<g transform="translate({right - sw - 19:.1f},21) scale(.6667)"><path d="{STAR}" fill="{t["amber"]}"/></g>')
        right -= sw + 30
    if p.get("demo"):
        lw = mw("live", 11) + 30
        o.append(pill(right - lw, 20, lw, 20, t["accent"]) + live_dot(right - lw + 11, 30, t["accent"], 3) +
                 f'<text x="{right - lw + 20:.1f}" y="34" class="m" font-size="11" fill="{t["accent"]}">live</text>')
    o.append(f'<text x="20" y="58" class="m" font-size="12" fill="{t["muted"]}">{esc(p["kicker"])}</text>')
    lines = textwrap.wrap(p["desc"], 52, break_on_hyphens=False)
    if len(lines) > 3:
        sys.exit(f"{p['repo']}: description wraps to {len(lines)} lines, keep it to 3")
    for i, line in enumerate(lines):
        o.append(f'<text x="20" y="{88 + i * 22}" font-size="14" fill="{t["text"]}">{esc(line)}</text>')
    x = 20
    for key in p["stack"]:
        label = STACK_LABELS.get(key, ICONS.get(key, {}).get("title", key))
        cw = 26 + mw(label, 11.5) + 10
        o.append(f'<rect x="{x:.1f}" y="164" width="{cw:.1f}" height="24" rx="12" fill="{t["surface2"]}" stroke="{t["border"]}"/>'
                 f'{icon(key, x + 8, 170, 12, brand(key, t, t["surface2"]))}'
                 f'<text x="{x + 26:.1f}" y="180" class="m" font-size="11.5" fill="{t["muted"]}">{esc(label)}</text>')
        x += cw + 6
    title = f'{p["repo"]}, {p["kicker"]}. {p["desc"]}' + (f" {stars} stars." if stars else "")
    return doc(w, h, title, "".join(o))


def timeline(t):
    date_x, rail_x, x = 150, 178, 206
    o, nodes, y = [], [], 8
    for i, e in enumerate(EXPERIENCE):
        color = t["link"] if e["kind"] == "WORK" else t["purple"]
        kw = mw(e["kind"], 10) + 18
        g = [f'<text x="{date_x}" y="{y + 19}" text-anchor="end" class="m" font-size="12" fill="{t["muted"]}">{esc(e["date"])}</text>',
             pill(date_x - kw, y + 30, kw, 20, color),
             f'<text x="{date_x - kw / 2:.1f}" y="{y + 44}" text-anchor="middle" class="m" font-size="10" '
             f'letter-spacing="1" font-weight="700" fill="{color}">{e["kind"]}</text>',
             f'<text x="{x}" y="{y + 20}" font-size="17" font-weight="700" fill="{t["text"]}">{esc(e["role"])}</text>',
             f'<text x="{x}" y="{y + 43}" font-size="13.5" fill="{t["muted"]}">{esc(e["org"])}</text>']
        for j, point in enumerate(e["points"]):
            py = y + 70 + j * 23
            g.append(f'<circle cx="{x + 4}" cy="{py - 4.5}" r="2.2" fill="{t["faint"]}"/>'
                     f'<text x="{x + 16}" y="{py}" font-size="14" fill="{t["text"]}">{esc(point)}</text>')
        o.append(f'<g class="up"{delay(.08 + i * .12)}>{"".join(g)}</g>')
        nodes.append((y + 14, e.get("now")))
        y += 54 + len(e["points"]) * 23 + 30
    h = y - 22
    rail = (f'<defs><linearGradient id="r" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t["accent"]}"/>'
            f'<stop offset=".35" stop-color="{t["border"]}"/></linearGradient></defs>'
            f'<rect x="{rail_x - 1}" y="{nodes[0][0]}" width="2" height="{nodes[-1][0] - nodes[0][0]}" fill="url(#r)"/>')
    dots = "".join(live_dot(rail_x, ny, t["accent"], 6) if now else
                   f'<circle cx="{rail_x}" cy="{ny}" r="5.5" fill="{t["page"]}" stroke="{t["faint"]}" stroke-width="2"/>'
                   for ny, now in nodes)
    title = "Experience. " + " ".join(f'{e["date"]}: {e["role"]}, {e["org"]}.' for e in EXPERIENCE)
    return doc(W, h, title, rail + dots + "".join(o))


def metrics(t, data):
    gh, lc = data.get("github") or {}, data.get("leetcode") or {}
    tiles = [("repositories", gh.get("public_repos"), "public on GitHub"),
             ("stars earned", gh.get("stars"), "across my own repos"),
             ("followers", gh.get("followers"), "on GitHub")]
    gap, sw, h = 12, 176, 150
    o = []
    for i, (label, value, note) in enumerate(tiles):
        x = i * (sw + gap)
        o.append(f'<g class="up"{delay(.05 + i * .08)}><g transform="translate({x},0)">{card(sw, h, t, 12)}'
                 f'<text x="20" y="34" class="m" font-size="11" letter-spacing="1.4" fill="{t["muted"]}">{label.upper()}</text>'
                 f'<text x="18" y="86" font-size="40" font-weight="700" letter-spacing="-1" fill="{t["text"]}">{value if value is not None else "–"}</text>'
                 f'<text x="20" y="126" class="m" font-size="11.5" fill="{t["faint"]}">{note}</text></g></g>')
    x = 3 * (sw + gap)
    lw = W - x
    solved = lc.get("solved")
    parts = [("easy", lc.get("easy") or 0, t["accent"]), ("medium", lc.get("medium") or 0, t["amber"]),
             ("hard", lc.get("hard") or 0, t["red"])]
    total = sum(n for _, n, _ in parts) or 1
    bar, bx, bw = [], 20.0, lw - 40
    for _, n, color in parts:
        seg = bw * n / total
        bar.append(f'<rect x="{bx:.1f}" y="100" width="{max(seg - 2, 0):.1f}" height="8" rx="4" fill="{color}"/>')
        bx += seg
    legend, lx = [], 20.0
    for name, n, color in parts:
        text = f"{n} {name}"
        legend.append(f'<circle cx="{lx + 4:.1f}" cy="127" r="4" fill="{color}"/>'
                      f'<text x="{lx + 13:.1f}" y="131" class="m" font-size="11.5" fill="{t["muted"]}">{text}</text>')
        lx += 13 + mw(text, 11.5) + 14
    o.append(f'<g class="up"{delay(.29)}><g transform="translate({x},0)">{card(lw, h, t, 12)}'
             f'<text x="20" y="34" class="m" font-size="11" letter-spacing="1.4" fill="{t["muted"]}">LEETCODE SOLVED</text>'
             f'{icon("leetcode", lw - 38, 20, 18, brand("leetcode", t, t["surface"]))}'
             f'<text x="18" y="80" font-size="40" font-weight="700" letter-spacing="-1" fill="{t["text"]}">{solved if solved is not None else "–"}</text>'
             f'{"".join(bar)}{"".join(legend)}</g></g>')
    title = (f'GitHub: {gh.get("public_repos")} public repositories, {gh.get("stars")} stars earned, '
             f'{gh.get("followers")} followers. LeetCode: {solved} solved '
             f'({parts[0][1]} easy, {parts[1][1]} medium, {parts[2][1]} hard).')
    return doc(W, h, title, "".join(o))


def activity(t, events, updated):
    rows = events or [["", "IDLE", "no public activity in the last 90 days"]]
    h = 66 + len(rows) * 30 + 14
    colors = {"PUSH": t["accent"], "MERGE": t["purple"], "PR": t["link"], "NEW": t["cyan"], "STAR": t["amber"],
              "FORK": t["muted"], "SHIP": t["accent"], "ISSUE": t["red"], "CLOSE": t["red"], "IDLE": t["muted"]}
    o = [card(W, h, t), live_dot(30, 31, t["accent"]),
         f'<text x="44" y="35.5" class="m" font-size="13" fill="{t["text"]}">tail -f ~/github.log</text>',
         f'<text x="{W - 24}" y="35.5" text-anchor="end" class="m" font-size="11.5" fill="{t["muted"]}">updated {esc(updated)}</text>',
         f'<rect x="0" y="54" width="{W}" height="1" fill="{t["border"]}"/>']
    for i, (when, label, text) in enumerate(rows):
        y = 86 + i * 30
        color = colors.get(label, t["muted"])
        if len(text) > 72:
            text = text[:71] + "…"
        o.append(f'<g class="fade"{delay(.15 + i * .12)}>'
                 f'<text x="24" y="{y}" class="m" font-size="12" fill="{t["faint"]}">{esc(when)}</text>'
                 f'{pill(150, y - 14.5, 62, 20, color)}'
                 f'<text x="181" y="{y - .5}" text-anchor="middle" class="m" font-size="10" font-weight="700" letter-spacing=".8" fill="{color}">{label}</text>'
                 f'<text x="228" y="{y}" class="m" font-size="13" fill="{t["text"]}">{esc(text)}</text></g>')
    title = "Recent public GitHub activity: " + "; ".join(f"{w} {l} {x}" for w, l, x in rows)
    return doc(W, h, title, "".join(o))


def cta(t):
    h = 168
    o = [f'<defs><clipPath id="c"><rect x=".5" y=".5" width="{W - 1}" height="{h - 1}" rx="16"/></clipPath>'
         f'<radialGradient id="g" cx="100%" cy="100%" r="70%"><stop offset="0" stop-color="{t["accent"]}" stop-opacity="{t["glow"]}"/>'
         f'<stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/></radialGradient></defs>',
         card(W, h, t, 16), f'<rect clip-path="url(#c)" width="{W}" height="{h}" fill="url(#g)"/>',
         f'<g class="up"><text x="36" y="46" class="m" font-size="12.5" fill="{t["muted"]}">'
         f'<tspan fill="{t["amber"]}" font-weight="700">POST</tspan> /v1/hire  →  <tspan fill="{t["accent"]}" font-weight="700">201 Created</tspan></text>'
         f'<text x="35" y="90" font-size="27" font-weight="700" letter-spacing="-.4" fill="{t["text"]}">Open to backend roles and collaborations.</text>'
         f'<text x="36" y="120" font-size="15" fill="{t["muted"]}">Especially where the hard problems are about scale and reliability.</text>'
         f'<text x="36" y="144" font-size="15" fill="{t["muted"]}">Email is fastest. My inbox has no rate limit.</text></g>']
    return doc(W, h, "Open to backend roles and collaborations. Email is fastest.", "".join(o))


def contact_button(t, label, glyph, primary):
    tw = mw(label, 12.5)
    w, h = 14 + 18 + 8 + tw + 14, 40
    fill = t["accent"] if primary else t["surface"]
    fg = t["on_accent"] if primary else t["text"]
    ic = t["on_accent"] if primary else (brand(glyph, t, t["surface"]) if glyph in ICONS else t["muted"])
    body = (f'<rect x=".5" y=".5" width="{w - 1:.1f}" height="{h - 1}" rx="10" fill="{fill}" '
            f'stroke="{t["accent"] if primary else t["border"]}"/>'
            f'{icon(glyph, 14, 11, 18, ic)}'
            f'<text x="{14 + 18 + 8}" y="25" class="m" font-size="12.5" font-weight="{700 if primary else 500}" fill="{fg}">{esc(label)}</text>')
    return doc(w, h, label, body)


def footer(t):
    h = 74
    css = (".pk{transform:translateX(-20px);animation:pk 5s cubic-bezier(.5,0,.5,1) infinite}"
           f"@keyframes pk{{0%{{transform:translateX(-20px)}}70%,100%{{transform:translateX({W + 20}px)}}}}")
    body = (f'<rect x="0" y="22" width="{W}" height="1" fill="{t["border"]}"/>'
            f'<g class="pk"><circle cx="0" cy="22.5" r="9" fill="{t["red"]}" opacity=".18"/><circle cx="0" cy="22.5" r="3.5" fill="{t["red"]}"/></g>'
            f'<text x="{W / 2}" y="54" text-anchor="middle" class="m" font-size="12" fill="{t["muted"]}">'
            f'<tspan fill="{t["red"]}" font-weight="700">429 Too Many Requests</tspan>  ·  you\'ve reached the end of this README</text>')
    return doc(W, h, "429 Too Many Requests: you've reached the end of this README", body, css)


# ---------------------------------------------------------------- LIVE DATA

def fetch(url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": GITHUB_USER, **(headers or {})})
    with urllib.request.urlopen(req, timeout=20) as res:
        return json.load(res)


def github(path):
    headers = {"Accept": "application/vnd.github+json"}
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    return fetch(f"https://api.github.com{path}", headers=headers)


def fetch_github():
    user = github(f"/users/{GITHUB_USER}")
    repos = github(f"/users/{GITHUB_USER}/repos?per_page=100&type=owner")
    own = [r for r in repos if not r["fork"]]
    return {"public_repos": user["public_repos"], "followers": user["followers"],
            "stars": sum(r["stargazers_count"] for r in own),
            "repo_stars": {r["name"]: r["stargazers_count"] for r in own}}


def fetch_leetcode():
    query = '{ matchedUser(username: "%s") { submitStats { acSubmissionNum { difficulty count } } } }' % LEETCODE_USER
    res = fetch("https://leetcode.com/graphql", json.dumps({"query": query}).encode(),
                {"Content-Type": "application/json", "Referer": "https://leetcode.com"})
    counts = {r["difficulty"]: r["count"] for r in res["data"]["matchedUser"]["submitStats"]["acSubmissionNum"]}
    return {"solved": counts["All"], "easy": counts["Easy"], "medium": counts["Medium"], "hard": counts["Hard"]}


def describe(event):
    repo = event["repo"]["name"]
    short = repo.split("/", 1)[1] if repo.startswith(f"{GITHUB_USER}/") else repo
    p, kind = event["payload"], event["type"]
    if kind == "PushEvent":
        return "PUSH", f"{short} → {p.get('ref', '').removeprefix('refs/heads/')}"
    if kind == "PullRequestEvent" and p.get("action") in ("opened", "merged", "closed"):
        merged = p["action"] == "merged" or p.get("pull_request", {}).get("merged")
        return ("MERGE" if merged else {"opened": "PR", "closed": "CLOSE"}[p["action"]]), f"{short}#{p['number']}"
    if kind == "CreateEvent":
        return "NEW", short if p.get("ref_type") == "repository" else f"{p.get('ref_type')} {p.get('ref')} in {short}"
    if kind == "ReleaseEvent":
        return "SHIP", f"{short} {p.get('release', {}).get('tag_name', '')}".strip()
    if kind == "IssuesEvent" and p.get("action") == "opened":
        return "ISSUE", f"{short}#{p['issue']['number']}"
    if kind == "WatchEvent":
        return "STAR", short
    if kind == "ForkEvent":
        return "FORK", short
    return None


def fetch_events(limit=6):
    rows, seen = [], set()
    events = github(f"/users/{GITHUB_USER}/events/public?per_page=100")
    for event in sorted(events, key=lambda e: e["created_at"], reverse=True):
        if event["repo"]["name"] == f"{GITHUB_USER}/{GITHUB_USER}":
            continue  # this profile repo, including the bot's daily commits
        described = describe(event)
        if not described or described in seen:
            continue
        seen.add(described)
        when = datetime.strptime(event["created_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        rows.append([when.astimezone(IST).strftime("%b %d, %H:%M"), *described])
        if len(rows) == limit:
            break
    return rows


def live_data():
    data = {}
    if os.path.exists(CACHE):
        with open(CACHE, encoding="utf-8") as f:
            data = json.load(f)
    fresh = False
    for key, source in (("github", fetch_github), ("leetcode", fetch_leetcode), ("events", fetch_events)):
        try:
            data[key] = source()
            fresh = True
        except Exception as err:  # keep the cached value for this source
            print(f"{key}: {err} (using cached value)", file=sys.stderr)
    if fresh:
        data["updated"] = datetime.now(IST).strftime("%b %d, %Y")
        with open(CACHE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
    return data


# ---------------------------------------------------------------- BUILD

def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    data = live_data()
    stars = (data.get("github") or {}).get("repo_stars", {})
    write(os.path.join(ASSETS, "terminal.svg"), terminal())
    for name, t in THEMES.items():
        out = os.path.join(ASSETS, name)
        files = {
            "hero": hero(t), "flow": flow(name), "stack": stack(t), "timeline": timeline(t),
            "metrics": metrics(t, data), "activity": activity(t, data.get("events"), data.get("updated", "")),
            "cta": cta(t), "footer": footer(t),
        }
        for method, path in NAV:
            files[f"nav-{path.strip('/')}"] = nav_button(t, method, path)
        for key, args in SECTIONS.items():
            files[f"h-{key}"] = section_header(t, *args)
        for p in PROJECTS:
            files[f"p-{p['slug']}"] = project_card(t, p, stars.get(p["repo"]))
        for key, label, glyph, primary in CONTACT:
            files[f"btn-{key}"] = contact_button(t, label, glyph, primary)
        for fname, svg in files.items():
            write(os.path.join(out, f"{fname}.svg"), svg)
    print(f"built {len(files) * 2 + 1} images")


if __name__ == "__main__":
    main()
