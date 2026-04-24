# AGENTS.md

## Project Overview
Flask web app for YouTube download (MP3/MP4) and audio conversion using edge-tts and yt-dlp.

## Run Commands

```bash
# Development
python app.py

# Or use startup script
start.bat
```

- Flask runs on port `5001` (start.bat line 6), not 5000 as in app.py default
- Template is at `template/xiazai.html`

## Architecture

- **Entry**: `app.py` → Flask app, registers `api/routes.py` blueprint
- **API**: `api/routes.py` handles download tasks via `yt-dlp`
- **Frontend**: `template/xiazai.html` - tabs for MP3, MP4, upgrade, convert, cookie settings

## Key Configuration

- **Proxy**: `http://127.0.0.1:7890` (hardcoded in `api/routes.py:18`)
- **Cookie path**: Stored in `config.json`, defaults to `C:\Users\Administrator\Downloads\www.youtube.com_cookies.txt`
- **yt-dlp**: Expected at `yt-dlp/yt-dlp.exe` (line 17)
- **Output dir**: `download/` (line 16)
- **Logs dir**: `logs/` (line 14)

## Testing
No test framework present. Manual testing via web UI.

## Quirks

- YouTube downloads require valid YouTube cookies (browser extension export)
- Proxy required for yt-dlp to work (Chinese network environment)
- Tasks stored in-memory in `TASKS` dict (lost on restart)