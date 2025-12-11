# How to Start the Bot Safely

## ⚠️ CRITICAL: Avoid Rate Limits

To prevent hitting Google's rate limits, **NEVER** run multiple bot instances at once.

## Quick Start

**Use the safe startup script:**

```powershell
.\start_bot.bat
```

This script will:
1. ✅ Kill any old bot instances automatically
2. ✅ Start a fresh, single bot instance
3. ✅ Prevent duplicate processes

## Accessing the Bot

Once started, open your browser to:
- **URL**: `http://localhost:8000`

## Stopping the Bot

Simply **close the terminal window** or press `Ctrl+C`.

## Important Notes

### Rate Limits (gemini-2.5-flash)

The bot uses `gemini-2.5-flash` which has strict limits:
- **Speed Limit**: ~2 messages per minute
- **Daily Limit**: 20 requests per day (new projects)

**If you see:** `⚠️ High Traffic: I am currently rate-limited...`
- **Wait 60 seconds** before sending the next message
- Chat **slowly** - one message at a time

### Fixing "Instant Block" Issues

If the bot blocks you immediately:
1. **Check for duplicates**: Only ONE terminal should be running
2. **Wait 1-2 hours**: Your IP might be temporarily blocked
3. **Try different network**: Use mobile hotspot if available
4. **New API key**: Create a fresh Google Cloud project

## Troubleshooting

### Port Already in Use
If you see `[Errno 10048]`:
1. Close ALL terminals
2. Run `taskkill /F /IM python.exe /T`
3. Start again with `start_bot.bat`

### Bot Not Responding to "Hi"
This is fixed! The system prompt now handles greetings properly.
