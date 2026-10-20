# COINVAULT — The Sovereign eFootball Coin Reserve Terminal

> **A premium, real-time eFootball coin tracking platform, high-frequency leaderboards, and algorithmic wealth intelligence.**

---

## 1. Architecture & Tech Stack

- **Backend**: Python 3.10+ / Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-Login, Flask-WTF (CSRF), Flask-Limiter, Flask-SocketIO (WebSocket real-time events), Pillow (secure image sanitization), Argon2-cffi (password security).
- **Database**: SQLite for development; native PostgreSQL configuration for production.
- **Frontend Craft**: Server-rendered Jinja2 shell, custom design tokens, Tailwind CSS build pipeline, self-hosted variable typography (`Syne`, `Inter`, `JetBrains Mono`).
- **Data Visualizations**: Apache ECharts (interactive sparklines, dual-timeline compare duels, wealth distribution histograms).
- **Motion & Kinetic UI**: GSAP, Lenis smooth scroll, 3D perspective mouse tilt, canvas confetti, Three.js WebGL hero coin token (graceful SVG fallback on reduced-motion).

---

## 2. Complete File Tree

```
coinvault/
├── app/
│   ├── __init__.py               # Flask app factory, security headers, template filters
│   ├── config.py                 # Dev / Prod / Test configurations, CSP settings
│   ├── extensions.py             # SQLAlchemy, Login, CSRF, Limiter, SocketIO instances
│   ├── models/
│   │   ├── __init__.py           # Model exports
│   │   ├── user.py               # User and ApiToken models (Argon2, Bearer tokens)
│   │   ├── coin.py               # CoinEntry (immutable ledger) and DailySnapshot
│   │   ├── social.py             # Follow, Badge, UserBadge, Report models
│   │   └── audit.py              # AuditLog compliance trail
│   ├── forms/
│   │   ├── __init__.py           # Form exports
│   │   ├── auth.py               # Login, Register, Password Reset forms
│   │   ├── coin.py               # LogCoinForm, EditCoinForm
│   │   └── profile.py            # ProfileForm (avatar upload), ApiTokenForm
│   ├── routes/
│   │   ├── __init__.py           # Blueprints registration
│   │   ├── main.py               # Landing, leaderboards hub, market analytics, compare
│   │   ├── auth.py               # Authentication flows
│   │   ├── user.py               # Personal dashboard, profile, settings, follow toggle
│   │   ├── api.py                # REST v1: Tampermonkey userscript sync, user search
│   │   └── admin.py              # Overseer console, anomaly queue, user ban, CSV export
│   ├── services/
│   │   ├── __init__.py           # Service exports
│   │   ├── anti_cheat.py         # Statistical Z-score outlier detection
│   │   ├── analytics.py          # Growth Score formula, volatility, projections
│   │   ├── badges.py             # Division honors and badge evaluation engine
│   │   └── audit.py              # Audit logger
│   ├── static/
│   │   ├── css/
│   │   │   ├── input.css         # Tailwind source + custom CSS design tokens
│   │   │   └── style.css         # Minified compiled stylesheet
│   │   ├── js/
│   │   │   ├── app.js            # Theme toggle, Cmd+K palette, Lenis, odometers
│   │   │   ├── charts.js         # Apache ECharts configuration
│   │   │   ├── motion.js         # GSAP entrances, 3D perspective tilt
│   │   │   ├── coin-hero.js      # Three.js 3D interactive gold coin token
│   │   │   └── socket.js         # Socket.IO live activity feed and toasts
│   │   ├── fonts/                # Self-hosted woff2 variable fonts
│   │   └── vendor/               # Bundled ECharts, GSAP, Lenis, Three.js, Confetti
│   └── templates/
│       ├── base.html             # Shell layout, navbar, Cmd+K, fast log modal
│       ├── index.html            # Landing hero, top-3 wealth podium, live stream
│       ├── dashboard/index.html  # User dashboard, balance curve, rivals watchlist
│       ├── leaderboards/index.html # Filterable rankings (richest, fastest, streaks)
│       ├── analytics/index.html  # Macro distribution histogram & Growth Score math
│       ├── compare/index.html    # Head-to-head stat duel mode
│       ├── achievements/index.html # Badges and milestones gallery
│       ├── user/
│       │   ├── profile.html      # Public dossier
│       │   ├── private_profile.html # Hidden vault notice
│       │   └── settings.html     # Avatar upload, API token generator
│       ├── auth/
│       │   ├── login.html
│       │   ├── register.html
│       │   └── reset_password.html
│       ├── admin/index.html      # Overseer queue, moderation, CSV export
│       └── errors/
│           ├── 404.html
│           └── 500.html
├── userscript/
│   ├── coinvault-verifier.user.js # Tampermonkey companion userscript
│   └── README.md                 # Detailed userscript installation manual
├── docs/
│   ├── design-system.md          # Complete design system specification
│   └── threat-model.md           # Security architecture and threat matrix
├── seeds/
│   └── seed_dev.py               # High-fidelity realistic development data seeder
├── tests/
│   └── test_app.py               # Automated unit and integration test suite
├── run.py                        # Application entrypoint
├── requirements.txt              # Python dependencies
├── package.json                  # Frontend build pipeline
├── tailwind.config.js            # Custom design tokens configuration
├── .env.example                  # Environment configuration template
└── README.md
```

---

## 3. Quickstart & Local Installation

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 1. Clone & Set Up Python Virtual Environment
```bash
# Navigate to directory
cd coinvault

# Create and activate virtual environment
python -m venv venv

# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Install Node Dependencies & Build CSS
```bash
npm install
npm run build:css
```

### 3. Initialize Environment & Seed Data
```bash
# Copy environment file
cp .env.example .env

# Populate database with realistic dev data
python seeds/seed_dev.py
```

### 4. Run the Development Server
```bash
python run.py
```
Open your browser to: **`http://127.0.0.1:5000`**

- **Admin Account**: `admin` / `AdminPass123!`
- **Demo Players**: `kane_striker`, `tokyo_tactics`, `ronaldinho_art` / `Player12345!`

---

## 4. Tampermonkey Userscript Companion

COINVAULT includes a companion script to verify balances from authorized web companions (e.g. Konami Point Store / My Page).

1. Install the [Tampermonkey Extension](https://www.tampermonkey.net/).
2. Log in to COINVAULT and visit **Settings > Tampermonkey Userscript & API Tokens**.
3. Generate a Personal API Bearer Token (`cv_...`).
4. Copy the script from `userscript/coinvault-verifier.user.js` into Tampermonkey.
5. In the on-page floating HUD pill, open Settings (⚙), paste your Bearer token, and click **Sync**.
6. Synced entries automatically receive the green **"Verified via script"** status on leaderboards.

---

## 5. Production Deployment Guide

### Architecture
- **Web / WebSocket Server**: Gunicorn with Eventlet or Gevent worker class.
- **Reverse Proxy**: Nginx with SSL termination (Let's Encrypt Certbot) and WebSocket upgrading.
- **Database**: PostgreSQL with connection pooling.

### Systemd Service Configuration (`/etc/systemd/system/coinvault.service`)
```ini
[Unit]
Description=COINVAULT Production Terminal Server
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/coinvault
Environment="PATH=/var/www/coinvault/venv/bin"
EnvironmentFile=/var/www/coinvault/.env
ExecStart=/var/www/coinvault/venv/bin/gunicorn --worker-class eventlet -w 1 --bind 127.0.0.1:5000 run:app

Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### Nginx Reverse Proxy (`/etc/nginx/sites-available/coinvault`)
```nginx
server {
    server_name vault.yourdomain.com;

    client_max_body_size 8M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/www/coinvault/app/static/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    listen 443 ssl http2;
    ssl_certificate /etc/letsencrypt/live/vault.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/vault.yourdomain.com/privkey.pem;
}
```

---

## 6. How to Extend Leaderboards & Indicators

- **Add New Leaderboard Metrics**:
  Edit `app/routes/main.py` in `leaderboards()`. Compute the metric on the candidate rows and add a matching sort branch (`elif metric == 'your_metric':`).
- **Add New Badges**:
  Add an entry in `INITIAL_BADGES` inside `app/services/badges.py` with unique slug, title, category, and tier. Then add the triggering criteria in `check_and_award_user_badges()`.
- **Adjust Anti-Cheat Sensitivity**:
  Tune the standard deviation threshold (`z_score > 4.0`) or time window rules in `app/services/anti_cheat.py`.
