---
name: tts
description: Toggle text-to-speech for Claude responses. Use when the user wants to hear responses spoken aloud, enable/disable TTS, or says "speak to me", "read aloud", "voice", "tts".
argument-hint: [on|off]
allowed-tools: Bash
---

# TTS - Text to Speech for Claude Code

Toggle text-to-speech so Claude's responses are spoken aloud using Windows SAPI (free, no API keys).

## How it works

- A **Stop hook** runs after every Claude response
- It reads the last assistant message from the transcript
- Cleans up markdown/code blocks for natural speech
- Speaks using Windows built-in SAPI voice
- Long responses are truncated to ~500 chars (~30 sec of speech)

## Commands

When the user says `$ARGUMENTS`, interpret as follows:

- **`/tts`** or **`/tts on`**: Enable TTS
- **`/tts off`**: Disable TTS

### Enable TTS
```bash
powershell -ExecutionPolicy Bypass -Command "& 'C:\Users\shiva\.claude\hooks\tts-toggle.ps1' -Action on"
```

### Disable TTS
```bash
powershell -ExecutionPolicy Bypass -Command "& 'C:\Users\shiva\.claude\hooks\tts-toggle.ps1' -Action off"
```

### Toggle TTS
```bash
powershell -ExecutionPolicy Bypass -Command "& 'C:\Users\shiva\.claude\hooks\tts-toggle.ps1'"
```

After running the command, tell the user the current TTS state and remind them that:
- TTS speaks after each response via the Stop hook
- Code blocks are skipped (only descriptions are read)
- Long responses are truncated to keep speech under ~30 seconds
- Rate is set to slightly fast (2/10) for comfortable listening
