---
name: notebooklm-research
description: |
  Deep research pipeline: takes URLs (articles, papers, YouTube videos) and/or a
  search topic, finds relevant YouTube videos via yt-dlp, feeds everything into
  NotebookLM for analysis, and delivers a structured research output — summary first,
  then a full blog-style writeup, with optional infographic/slides/podcast/mindmap on
  request. Use this skill whenever the user wants to research a topic deeply, ingest
  multiple sources, "understand everything about X", "make a NotebookLM notebook on",
  "research and summarize", or provides a mix of links and asks for a coherent output.
  Also integrates with quant-writer: outputs a research-bundle.md that quant-writer
  can consume directly as a draft path.
argument-hint: "[topic or URLs] [--yt-search <query>] [--deliverable summary|blog|infographic|slides|podcast|mindmap|all]"
---

# NotebookLM Research Pipeline

You are orchestrating a deep research pipeline. The goal: take a topic + sources, push them into NotebookLM, and return coherent, structured knowledge — not just a dump of what was found.

---

## What this skill does

1. **Collect sources** — URLs the user provides + YouTube videos found via search
2. **Build a NotebookLM notebook** — add all sources, wait for processing
3. **Generate research output** — summary first, always. Full writeup. Optional artifacts on request.
4. **Save a research bundle** — structured markdown that quant-writer can consume directly

The user gets actionable knowledge, not raw transcripts.

---

## Step 0: Setup Check

Before anything else, run the setup check script:

```bash
python "C:/Users/shiva/ai-skills/notebooklm-research/scripts/setup_check.py"
```

This verifies notebooklm-py and yt-dlp are installed and NotebookLM auth is valid.

**If it fails:**
- Missing packages: `pip install notebooklm-py yt-dlp`
- Auth expired: run `notebooklm login` and have the user complete browser auth, then re-run the check
- Do NOT proceed until setup check passes

---

## Step 1: Parse Input

The user will provide some combination of:
- **A topic string** — "Bitcoin futures trading strategies", "quantitative momentum in Indian markets"
- **Direct URLs** — articles, papers, YouTube links, blog posts, PDFs
- **A YouTube search query** — explicit or implied from the topic

**Notebook name:** Use the topic/query as the name, cleaned up. Add a short timestamp suffix to avoid collisions. Example: `bitcoin-futures-2026-03`.

**Deliverable:** Default is `summary + blog`. User can request additional artifacts after seeing the summary.

---

## Step 2: YouTube Search (if topic provided)

Use yt-dlp to find relevant YouTube videos:

```bash
python "C:/Users/shiva/ai-skills/notebooklm-research/scripts/yt_search.py" "<search query>" --count 5
```

This returns a JSON list of `{url, title, duration_seconds, view_count, age_days}`.

**Filter before adding to NotebookLM:**
- Drop videos under 72 hours old (NotebookLM requirement)
- Drop videos without captions (yt-dlp flags this: `automatic_captions` empty AND `subtitles` empty)
- Prefer videos > 5 minutes (more substance)
- Cap at 5 YouTube sources — quality over quantity

Tell the user which videos were found and which were filtered, before proceeding.

---

## Step 3: Build the Notebook

```bash
# Create notebook
notebooklm create "<notebook-name>"
notebooklm use "<notebook-name>"

# Add all sources (user-provided URLs + filtered YouTube URLs)
# Add them one at a time with a short delay between each
notebooklm source add "<url>" --wait
```

Add sources sequentially with a 2-second pause between each to avoid rate limits. The `--wait` flag ensures each source is processed before moving on.

After all sources are added, confirm with:
```bash
notebooklm source list
```

Tell the user: "Notebook created with N sources. Processing..."

---

## Step 4: Generate Core Output (Always)

### 4a. Ask for summary

```bash
notebooklm ask "Give me a comprehensive summary of all sources. Cover: (1) the main thesis or finding of each source, (2) key concepts that appear across multiple sources, (3) disagreements or tensions between sources, (4) the most actionable or interesting insight overall."
```

Save the response. This is **Output 1: Summary** — present it to the user immediately.

### 4b. Ask for structured insights

```bash
notebooklm ask "Based on all sources, give me: (1) 5-7 key insights a practitioner would care about, (2) any data, statistics, or numbers mentioned, (3) what questions these sources leave unanswered."
```

Save the response. This feeds the writeup.

### 4c. Generate writeup

Using the summary + insights you just collected, write a coherent blog-style explanation of the topic. This is NOT NotebookLM generating the writeup — **you write this** using the research as input.

Structure:
```
## [Topic]: What You Actually Need to Know

[Opening: the most interesting tension or insight from the research — 2-3 sentences]

### What the sources agree on
[3-5 bullet points of consensus findings]

### The most interesting insight
[1-2 paragraphs on the sharpest finding]

### Key data and numbers
[bullet list of any concrete figures, stats, percentages]

### What's still unclear / open questions
[2-3 bullets on what the sources don't answer]

### Sources used
[list of titles + URLs]
```

This is **Output 2: Writeup** — present after the summary.

---

## Step 5: Optional Artifacts (On Request Only)

After presenting the summary and writeup, tell the user:

> "Summary and writeup are ready. I can also generate: **infographic**, **slides**, **podcast**, **mind map**, or **data table**. Just ask for any of these."

Only generate artifacts the user explicitly requests. Each one:

### Infographic
```bash
notebooklm generate infographic --orientation portrait --wait
notebooklm download infographic ./<notebook-name>-infographic.png
```

### Slides
```bash
notebooklm generate slide-deck --wait
notebooklm download slide-deck ./<notebook-name>-slides.pdf
```

### Podcast
```bash
notebooklm generate audio "Create a deep-dive podcast episode covering the key insights from these sources" --wait
notebooklm download audio ./<notebook-name>-podcast.mp3
```

### Mind Map
```bash
notebooklm generate mind-map --wait
notebooklm download mind-map ./<notebook-name>-mindmap.json
```

Tell the user where each file was saved. For artifacts with visual output (infographic, mindmap), also describe what it contains.

---

## Step 6: Save Research Bundle

Save a `research-bundle.md` file in the current working directory. This is the quant-writer integration point.

```markdown
---
research-topic: <topic>
notebook: <notebook-name>
sources: <count>
date: <YYYY-MM-DD>
---

# Research Bundle: <topic>

## Summary
<paste the NotebookLM summary from Step 4a>

## Key Insights
<paste the structured insights from Step 4b>

## Source List
<list of all URLs added, with titles>

## Raw Notes
<any additional context the user provided>
```

Tell the user: "Research bundle saved to `research-bundle.md`. You can pass this to `/quant-writer blog research-bundle.md` to turn it into a post."

---

## Error Handling

**"Transcript not available" for a YouTube video:**
Skip it. Tell the user which video was skipped and why. Do not retry — the 72-hour rule is firm.

**Rate limit / RPCError:**
Wait 30 seconds, retry once with `--retry 3`. If it still fails, skip that generation step and tell the user.

**Auth expired mid-session:**
Stop, tell the user to run `notebooklm login`, confirm re-auth, then resume from where you stopped. Do not re-add sources — the notebook already exists.

**notebooklm-py API breakage (RPCError: No result found for RPC ID):**
This means Google updated their internal API. Tell the user: "notebooklm-py has a known fragility with Google API updates. Check https://github.com/teng-lin/notebooklm-py/issues for a fix — these are usually patched within hours."

---

## quant-writer Integration

When the user wants to turn the research into a blog post:
1. The `research-bundle.md` from Step 6 is the input
2. Invoke quant-writer: `/quant-writer blog research-bundle.md`
3. quant-writer will read the bundle as a draft path and apply Shivam's voice + SEO structure

The research bundle is intentionally formatted to match what quant-writer expects: a topic, key claims, concrete data, and open questions. quant-writer handles the voice, structure, and Anti-AI pass.

---

## Output Order (Always Follow This)

1. **Setup check result** — pass/fail, fix if needed
2. **Sources found** — list of YouTube results + filtering decisions
3. **Notebook created** — confirmation with source count
4. **Summary** — present immediately after NotebookLM processes
5. **Writeup** — your synthesized blog-style explanation
6. **Offer optional artifacts** — one line, don't over-explain
7. **Research bundle saved** — path + quant-writer hint

Never skip the summary. Never generate all artifacts upfront. Never present the writeup before the summary.
