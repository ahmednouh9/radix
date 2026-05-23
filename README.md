# SocialAutoReply

A full-stack Instagram + Facebook comment automation tool (ManyChat-style). Automatically replies to comments and sends DMs based on keyword-matched campaigns.

## Features

- **Auto-reply to comments** on Instagram and Facebook posts
- **Keyword-based campaigns** with exact, contains, and regex matching
- **Public replies + private DMs** — sends both or either per campaign
- **Real-time dashboard** with SSE-powered live notifications
- **Bilingual AR/EN** with RTL support
- **Dark mode** by default
- **PIN protection** for dashboard access
- **Analytics** with Chart.js visualizations

## Tech Stack

- **Backend:** Python + FastAPI + SQLAlchemy + SQLite
- **Frontend:** Jinja2 + vanilla HTML/CSS/JS + Chart.js
- **Real-time:** Server-Sent Events (SSE)
- **Rate limiting:** slowapi
- **Deployment:** Railway / Render ready

## Quick Start

```bash
# Clone the repo
git clone https://github.com/yourusername/SocialAutoReply.git
cd SocialAutoReply

# Install dependencies
pip install -r requirements.txt

# Copy env file and configure
cp .env.example .env
# Edit .env with your settings

# Run the app
uvicorn app.main:app --reload
```

Visit `http://localhost:8000` to access the dashboard.

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | SQLite path (default: `sqlite:///./app.db`) | No |
| `SECRET_KEY` | Session encryption key | Yes |
| `DASHBOARD_PIN` | PIN to protect dashboard access | No |
| `INSTAGRAM_APP_SECRET` | Instagram app secret (for webhook verification) | No |
| `FACEBOOK_APP_SECRET` | Facebook app secret (for webhook verification) | No |

## API Endpoints

### Webhooks
- `GET /webhook/instagram` — IG webhook verification
- `POST /webhook/instagram` — Receive IG comment events
- `GET /webhook/facebook` — FB webhook verification
- `POST /webhook/facebook` — Receive FB comment events

### Campaigns
- `GET /api/v1/campaigns` — List all campaigns
- `POST /api/v1/campaigns` — Create campaign
- `GET /api/v1/campaigns/{id}` — Get campaign
- `PUT /api/v1/campaigns/{id}` — Update campaign
- `DELETE /api/v1/campaigns/{id}` — Delete campaign
- `PATCH /api/v1/campaigns/{id}/toggle` — Toggle active status

### Platform Config
- `GET /api/v1/configs` — List configs
- `POST /api/v1/configs` — Create/update config
- `GET /api/v1/configs/{platform}` — Get platform config
- `POST /api/v1/configs/{platform}/test` — Test connection

### Analytics
- `GET /api/v1/analytics/overview` — Dashboard stats
- `GET /api/v1/analytics/timeline?days=7` — Daily activity
- `GET /api/v1/analytics/by-campaign` — Per-campaign stats

### Real-time
- `GET /api/sse` — SSE event stream

## Known Issues

- **Instagram public reply (April 2026):** The `POST /{ig-comment-id}/replies` endpoint is currently broken for comments by non-business users (error 100/subcode 33). The app automatically falls back to sending a private reply via DM as a workaround.
- **Meta App Review required** for production use: `instagram_manage_messages`, `instagram_manage_comments`, `pages_manage_engagement`, `pages_messaging` permissions need review approval.

## Deployment

### Railway

```bash
railway login
railway init
railway up
```

The app will be available at `https://socialaautoreply.up.railway.app`.

### Render

Create a new Web Service, set the start command to `uvicorn app.main:app --host 0.0.0.0 --port $PORT`, and configure environment variables.

## License

MIT
