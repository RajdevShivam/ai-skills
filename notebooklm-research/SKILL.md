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

**IMPORTANT — Windows CLI:** All `notebooklm` commands must be run as `python -m notebooklm <subcommand>`. The bare `notebooklm` command is NOT reliably on PATH after pip install on Windows. Every code example in this skill uses the correct form.

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
- Auth expired: run `python -m notebooklm login` and have the user complete browser auth, then re-run the check
- Do NOT proceed until setup check passes

**After setup check passes, tell the user:**
> "Setup verified. This session will auto-save a `research-bundle.md` as we go. If the context window fills or the session is interrupted, that file contains the full output — nothing is lost. The NotebookLM notebook also persists on Google's servers under the name you'll see below."

---

## Step 1: Parse Input

The user will provide some combination of:
- **A topic string** — "Bitcoin futures trading strategies", "quantitative momentum in Indian markets"
- **Direct URLs** — articles, papers, YouTube links, blog posts, PDFs
- **A YouTube search query** — explicit or implied from the topic

**Notebook name:** Use the topic/query as the name, cleaned up. Add a short timestamp suffix to avoid collisions. Example: `bitcoin-futures-2026-03`.

**Deliverable:** Default is `summary + blog`. User can request additional artifacts after seeing the summary.

**Resume path:** Before creating a new notebook, check if one already exists for this topic:
```bash
python -m notebooklm notebook list
```
If a matching notebook exists, use it directly and skip source-add entirely — jump to Step 4. Do not recreate the notebook or re-add sources.

---

## Step 2: YouTube Search (if topic provided)

Tell the user: "Searching YouTube — this fetches full metadata per candidate video and typically takes 3-6 minutes for 15 candidates. I'll list results when done."

Use yt-dlp to find relevant YouTube videos. For niche topics (anything technical, strategy-focused, or practitioner-level), always use `--niche` — it appends practitioner/deep-dive terms to the query to steer YouTube's algorithm away from beginner explainers toward people who actually do the thing:

```bash
# For niche/technical topics (default for most research queries):
python "C:/Users/shiva/ai-skills/notebooklm-research/scripts/yt_search.py" "<search query>" --niche --count 15

# For broad/general topics where mainstream coverage is fine:
python "C:/Users/shiva/ai-skills/notebooklm-research/scripts/yt_search.py" "<search query>" --count 15
```

This returns a JSON list of `{url, title, duration_seconds, view_count, age_days, has_captions}`.

**Hard filters (applied in script — videos excluded entirely):**
- No captions available
- Under 5 minutes (too shallow to be useful)

**Cap at 5 YouTube sources** — quality over quantity.

Tell the user which videos were found and which were excluded.

---

## Step 3: Build the Notebook

```bash
# Create notebook
python -m notebooklm create "<notebook-name>"
```

Then add all sources one at a time. **The `--wait` flag does NOT exist for `source add`** — use a 3-second pause between each add instead:

```bash
# Add source 1
python -m notebooklm source add "<url1>" -n "<notebook-name>"
# (pause 3 seconds)
# Add source 2
python -m notebooklm source add "<url2>" -n "<notebook-name>"
# (pause 3 seconds)
# ...repeat for all sources
```

Tell the user before starting: "Adding N sources to NotebookLM — typically 2-4 minutes total. Adding them one at a time to avoid rate limits."

After all sources are added, confirm with:
```bash
python -m notebooklm source list -n "<notebook-name>"
```

Tell the user: "Notebook created with N sources. Processing..."

---

## Step 4: Generate Core Output (Always)

### 4a. Ask for summary

```bash
python -m notebooklm ask "Give me a comprehensive summary of all sources. Cover: (1) the main thesis or finding of each source, (2) key concepts that appear across multiple sources, (3) disagreements or tensions between sources, (4) the most actionable or interesting insight overall." -n "<notebook-name>"
```

Save the response. This is **Output 1: Summary** — present it to the user immediately.

### 4b. Ask for structured insights

```bash
python -m notebooklm ask "Based on all sources, give me: (1) 5-7 key insights a practitioner would care about, (2) any data, statistics, or numbers mentioned, (3) what questions these sources leave unanswered." -n "<notebook-name>"
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

### My provisional take
[1 paragraph: what this research suggests Shivam should believe or do differently.
Be explicit about confidence level. If the evidence is thin, say so.
This section is a starting point for quant-writer, not a final claim.]

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
python -m notebooklm generate infographic --orientation portrait --wait -n "<notebook-name>"
python -m notebooklm download infographic ./<notebook-name>-infographic.png -n "<notebook-name>"
```

### Slides
```bash
python -m notebooklm generate slide-deck --wait -n "<notebook-name>"
python -m notebooklm download slide-deck ./<notebook-name>-slides.pdf -n "<notebook-name>"
```

### Podcast
```bash
python -m notebooklm generate audio "Create a deep-dive podcast episode covering the key insights from these sources" --wait -n "<notebook-name>"
python -m notebooklm download audio ./<notebook-name>-podcast.mp3 -n "<notebook-name>"
```

### Mind Map
```bash
python -m notebooklm generate mind-map --wait -n "<notebook-name>"
python -m notebooklm download mind-map ./<notebook-name>-mindmap.json -n "<notebook-name>"
```

Tell the user where each file was saved. For artifacts with visual output (infographic, mindmap), also describe what it contains.

---

## Step 6: Save Research Bundle

Save a `research-bundle.md` file in the current working directory. Tell the user the **full absolute path** so they can reference it precisely. This is the quant-writer integration point.

```markdown
---
research-topic: <topic>
notebook: <notebook-name>
notebook-path: <full absolute path to this research-bundle.md file>
sources: <count>
date: <YYYY-MM-DD>
intended-audience: practitioner  # or: general, technical, investor
output-format: blog-post  # or: linkedin, newsletter, report
personal-angle: <what the user specifically wanted to understand — one sentence from their original query>
open-question: <the most important thing the sources left unanswered>
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

Tell the user: "Research bundle saved to `<absolute path>`. You can pass this to `/quant-writer blog <absolute path>` to turn it into a post."

---

## Error Handling

**"Transcript not available" for a YouTube video:**
Skip it. Tell the user which video was skipped and why. Do not retry.

**Rate limit / RPCError:**
Wait 30 seconds, retry once. If it still fails, skip that generation step and tell the user.

**Auth expired mid-session:**
Stop, tell the user to run `python -m notebooklm login`, confirm re-auth, then resume from where you stopped. Do not re-add sources — the notebook already exists.

**Context compaction / session interrupted mid-run:**
Check if a notebook matching this topic already exists: `python -m notebooklm notebook list`. If it does, use it directly and skip source-add entirely. Resume from Step 4. Do not recreate the notebook or re-add sources. The `research-bundle.md` on disk contains any output already generated.

**notebooklm-py API breakage (RPCError: No result found for RPC ID):**
This means Google updated their internal API. Tell the user: "notebooklm-py has a known fragility with Google API updates. Check https://github.com/teng-lin/notebooklm-py/issues for a fix — these are usually patched within hours."

---

## quant-writer Integration

When the user wants to turn the research into a blog post:
1. The `research-bundle.md` from Step 6 is the input
2. Invoke quant-writer: `/quant-writer blog <absolute path to research-bundle.md>`
3. quant-writer will read the bundle as a draft path and apply Shivam's voice + SEO structure

The research bundle frontmatter (intended-audience, output-format, personal-angle, open-question) gives quant-writer the context it needs to write without asking follow-up questions. The "My provisional take" section from the writeup is the thesis seed.

---

## Output Order (Always Follow This)

1. **Setup check result** — pass/fail, fix if needed. Then tell user about research-bundle persistence.
2. **Sources found** — list of YouTube results + filtering decisions
3. **Notebook created** — confirmation with source count
4. **Summary** — present immediately after NotebookLM processes
5. **Writeup** — your synthesized blog-style explanation
6. **Offer optional artifacts** — one line, don't over-explain
7. **Research bundle saved** — full absolute path + quant-writer hint

Never skip the summary. Never generate all artifacts upfront. Never present the writeup before the summary.
