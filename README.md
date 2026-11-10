# AI YouTube SEO Assistant

Hookline generates YouTube publishing material from a video topic or script.

**Purpose:** a creator enters a topic or pastes a script and gets title options, a description, keywords and tags, and short-form video ideas, all as drafts to edit before publishing.

## Main workflow

1. Enter a video topic or paste a script.
2. Generate title options and a description.
3. Get relevant keywords and tags.
4. Get a short-form video script or hook.

**Example:** a creator enters a gaming video topic, such as "Beginner's guide to Minecraft redstone", and receives:

| Output | What you get |
|---|---|
| Titles | 5 options, each with an angle (how-to, curiosity, list) and a length check against the 60-character search-friendly range |
| Description | An opening hook with the main keyword, a short summary, a call to action, and hashtags |
| Keywords and tags | 8 to 12 search phrases, 10 to 15 tags kept inside YouTube's 500-character tag limit, and hashtags |
| Shorts | 3 ideas, each with an opening hook, a spoken script, and on-screen text |

The wording comes from the AI model, so results vary. Titles and descriptions are based only on what you enter. The assistant is told not to invent facts, links, or timestamps, but always check the output before you publish.

**Tech stack:** Python, Flask, HTML/CSS/JavaScript (one file), OpenRouter API, Gunicorn.

## Project structure

```
ai-youtube-seo-assistant/
├── app.py               Flask app, REST API, OpenRouter integration
├── index.html           Whole frontend (HTML, CSS, JS in one file)
├── requirements.txt
├── setup.bat / setup.sh Creates venv and installs dependencies
├── render.yaml          Render blueprint (optional)
├── .python-version      3.11.9
├── .env.example         Copy to .env
├── .gitignore
└── tests/test_app.py    Workflow tests (OpenRouter is mocked)
```

## Run locally (VS Code)

Requires Python 3.10 or newer (3.11.9 recommended).

**Shortcut:** double-click `setup.bat` (Windows) or run `./setup.sh` (macOS / Linux). It creates the `venv` folder inside the project and installs the dependencies. The manual steps below do the same thing.

**1. Create and activate a virtual environment**

```powershell
# Windows (PowerShell)
python -m venv venv
venv\Scripts\Activate.ps1
```
```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once.

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Add your OpenRouter API key**

Create a key at https://openrouter.ai/keys, then open `.env` (or copy `.env.example` to `.env`) and set `OPENROUTER_API_KEY`. Choose a model with `OPENROUTER_MODEL` (any slug from https://openrouter.ai/models).

**4. Start the app**

```bash
python app.py
```

Open http://localhost:5000.

**5. Run the tests (optional)**

```bash
python tests/test_app.py
```

### Using VS Code Live Server instead

1. Start the backend: `python app.py`.
2. Right-click `index.html` in VS Code and choose **Open with Live Server**.
3. The page opens at http://127.0.0.1:5500 and calls the Flask API at http://localhost:5000.

The API key stays in `.env` on the backend, so the page never sees it. If Flask uses another port, change `BACKEND_URL` near the top of the script in `index.html`.

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `OPENROUTER_API_KEY` | Yes | Your OpenRouter key. Stays on the server. |
| `OPENROUTER_MODEL` | No | Model slug. Defaults to `openai/gpt-4o-mini`. |
| `OPENROUTER_TIMEOUT` | No | Seconds to wait for the AI service. Defaults to 60. |
| `PORT` | No | Port to listen on. Defaults to 5000; Render sets it for you. |
| `FLASK_DEBUG` | No | Set to `1` for debug mode while developing. |
| `ALLOWED_ORIGINS` | No | Comma-separated origins allowed to call `/api`. Unset allows any localhost port. |

## API

| Method | Route | Purpose |
|---|---|---|
| POST | `/api/generate` | Body `{"input": "...", "mode": "topic" or "script", "tone": "Friendly"}`. Returns titles, description, keywords, tags, hashtags, and Shorts. |
| GET | `/api/config` | Tones and input limits. |
| GET | `/health` | Health check. |

Limits: topics 3 to 500 characters, scripts 40 to 12,000 characters. The backend validates the AI's JSON and returns a clear error if it is invalid or incomplete.

## Push to GitHub

```bash
git init
git add .
git status          # confirm .env is NOT listed
git commit -m "Initial commit: AI YouTube SEO assistant"
git branch -M main
git remote add origin https://github.com/<your-username>/ai-youtube-seo-assistant.git
git push -u origin main
```

Create the empty repository on GitHub first. `.env` is in `.gitignore`, so your key is not committed. If you ever commit a key by accident, revoke it on OpenRouter right away.

## Deploy to Render

1. Push the project to GitHub.
2. In Render, choose **New > Web Service** and connect the repository (or **New > Blueprint** to use `render.yaml`).
3. Build command: `pip install -r requirements.txt`. Start command: `gunicorn app:app`.
4. Add `OPENROUTER_API_KEY` (and optionally `OPENROUTER_MODEL`) under **Environment**. Add `PYTHON_VERSION` = `3.11.9` if you aren't using the blueprint.
5. Deploy. Render supplies `PORT` automatically.

Nothing is stored on the server, so the free plan works fine.

## Notes

- Input is trimmed, stripped of control characters, and length-limited. It reaches the model as delimited data with instructions not to follow anything inside it.
- AI output is shown as plain text, never as HTML.
- There is no login. Anyone who can open the deployed app can use your OpenRouter credits, so put it behind authentication before sharing a public URL.
