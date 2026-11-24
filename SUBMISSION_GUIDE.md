# 📋 Devnovate Ideathon — Prototype Submission Guide
### Track 1: Make MCP Matter — Less Magic, More Utility
**Deadline**: November 24th at 11:59 PM | **Pitch Round**: November 26th & 27th

---

## 🚀 Overview of Submission Deliverables

According to the official **Ideathon Guidelines**, here are the exact deliverables required for your submission on the **Devnovate platform**:

| # | Deliverable | Description & Exact Format | Status |
|---|---|---|---|
| **1** | **Public GitHub Repository** | Public GitHub repo containing the working MVP codebase, architecture diagrams, and MCP implementation.<br>👉 **Repo Link**: `https://github.com/tejas448866/AI-Virtual-Assistant-MCP` | ✅ **Ready & Pushed** |
| **2** | **Mandatory PPT Template Link** | File named `TeamName_Track1` (e.g., `OmniMCP_Track1.pptx`), uploaded to Google Drive with access set to **"Anyone with the link can view"**. | 📝 **Template Content Provided Below** |
| **3** | **Video Pitch (3–5 mins)** | Recorded 3–5 min video explaining the core problem, solution, technical architecture, and a quick prototype walkthrough. Uploaded to **YouTube** (Unlisted or Public). | 🎬 **Timestamped Script Provided Below** |
| **4** | **Submission Platform** | Submit all 3 links exclusively via the **Devnovate platform** before 11:59 PM. | ⏳ **Awaiting Final Form Submission** |

---

## 📊 Slide-by-Slide Presentation Blueprint (Mandatory PPT)

*Follow this slide breakdown strictly within the official PPT template without adding extra slides:*

### Slide 1: Title & Team Details
- **Project Title**: OmniMCP — The Everyday AI Assistant Powered by Model Context Protocol
- **Track**: Track 1 — Make MCP Matter (Less Magic, More Utility)
- **Team Name**: *[Insert Your Team Name, e.g., Team OmniMCP]*
- **Team Members**: Tejas (*Lead Developer*) & Team Members
- **Sponsor Tech Used**: ElevenLabs (Audio/Voice AI) & AWS (Amazon Bedrock & S3)

### Slide 2: The Core Problem
- **The "Magic vs. Utility" Dilemma**: AI tools and integrations are everywhere, but everyday people still struggle to get them to solve daily problems.
- **The Black-Box Failure**: Existing voice assistants either act like rigid keyword chatbots or execute unverified, unpredictable actions ("magic") that users cannot trust.
- **Walled Gardens**: Assistants are locked into single proprietary ecosystems rather than standard interoperable protocols.

### Slide 3: The Proposed Solution
- **OmniMCP Principle**: *Less Magic, More Utility.*
- **Open Standards**: Built natively on Anthropic's **Model Context Protocol (MCP)**, connecting any app, desktop tool, or cloud service without custom glue code.
- **Three-Tier Human-in-the-Loop Safety Gate**:
  - *Tier 1 (Safe)*: Read-only inspection (calendar lookup, note search, weather) executes immediately.
  - *Tier 2 (Reversible)*: Local desktop tasks (notes, shopping lists, app launching) execute with instant receipts and undo support.
  - *Tier 3 (Critical)*: External or destructive actions (sending emails/messages, file deletions, system modifications) require explicit voice or HUD confirmation.

### Slide 4: Technical Architecture & Blueprint
- **Core Engine**: Gemini Live / Local Engine with Push-to-Talk and Wake Word.
- **MCP Subsystem**:
  - `MCPClient` & `StdIOTransport` for JSON-RPC 2.0 protocol execution.
  - `MCPServerManager` orchestrating built-in everyday servers + community MCP servers (`filesystem`, `fetch`, `sqlite`).
- **Sponsor Integrations**:
  - **ElevenLabs**: Multilingual, emotion-aware speech streaming (`eleven_flash_v2_5`).
  - **AWS Cloud**: Amazon Bedrock inference + Amazon S3 encrypted state vault.

### Slide 5: Prototype & Everyday Demos
- **Daily Organization**: Natural grocery list management, quick note-taking, and categorized budget logging.
- **Desktop Productivity**: Clipboard assistant, safe file finder, and verified application launching.
- **Safe Communication**: One-click WhatsApp and email draft preparation without accidental sending.

### Slide 6: Sponsor Technology Highlights (Bonus Tracks)
- **ElevenLabs (Best Use of ElevenLabs Prize)**:
  - Sub-300ms time-to-speech latency.
  - Dynamic language switching that follows the user's spoken language.
- **AWS (Best Use of AWS Prize)**:
  - Amazon Bedrock Converse API with native MCP tool calling.
  - Amazon S3 automated sync for backup of personal notes, groceries, and memories.

### Slide 7: 24-Hour Hack Day Roadmap
- **Phase 1 (Morning)**: Expand MCP server catalog (Google Calendar, Notion, Spotify, Home Assistant).
- **Phase 2 (Afternoon)**: AWS Lambda containerization for serverless remote MCP hubs.
- **Phase 3 (Evening)**: Multi-device mobile PWA pairing via QR code with real-time WebSocket sync.

---

## 🎬 3–5 Minute Video Pitch Script & Storyboard

### [0:00 – 0:45] Hook & Problem Statement
> *"Hello judges! AI assistants are everywhere today, but when regular people try using them for everyday tasks, they either hit a wall of proprietary restrictions or get unpredictable, uncontrolled 'magic' that they can't trust with their real data. For Track 1, we asked: How can we make the Model Context Protocol truly matter for everyday people? Our answer is **OmniMCP: Less Magic, More Utility**."*

### [0:45 – 1:45] The Solution & MCP Core
> *"OmniMCP is an everyday virtual assistant that uses the Model Context Protocol (MCP) as its foundational nervous system. Instead of hardcoded, brittle integrations, any tool—whether it's managing groceries, checking calendar conflicts, organizing downloads, or drafting emails—is exposed as a standardized MCP tool. Crucially, we enforce a Human-in-the-Loop Safety Gate: read-only actions run instantly, but critical actions like sending emails or modifying files pause for your clear confirmation."*

### [1:45 – 3:30] Live Prototype Walkthrough
> *(Screen Recording Walkthrough)*
> 1. **Groceries & Tasks**: *"Jarvis, add oat milk and bread to my grocery list."* -> Shows item added to persistent store.
> 2. **Budget Tracking**: *"Log 12 dollars on lunch at Subway."* -> Shows categorized expenditure update.
> 3. **Desktop & Clipboard**: *"Summarize the text currently on my clipboard."* -> Displays clean summary in the HUD.
> 4. **Safe Communication**: *"Draft an email to my team about tomorrow's demo."* -> Demonstrates safety gate preparing the draft without sending without confirmation.

### [3:30 – 4:15] Sponsor Tech Integration
> *"We also integrated our key sponsors:*
> *First, **ElevenLabs** powers our conversational voice pipeline with ultra-low latency, emotive speech synthesis that dynamically adapts to whatever language you speak.*
> *Second, **AWS** provides our enterprise foundation: Amazon Bedrock handles complex reasoning with native tool calling, and Amazon S3 provides an encrypted cloud vault for multi-device sync."*

### [4:15 – 5:00] Conclusion & Roadmap
> *"Our working MVP is live, tested, and public on GitHub. During the 24-hour hack day, we will deploy containerized MCP hubs on AWS Lambda and connect Google Workspace and Home Assistant. Thank you!"*

---

## 📌 Checklist Before Final Submission

1. **GitHub Link**: `https://github.com/tejas448866/AI-Virtual-Assistant-MCP`
2. **Drive PPT Link**: Ensure sharing is set to **"Anyone with the link can view"** (not Restricted). Name: `TeamName_Track1.pptx`.
3. **YouTube Link**: Ensure video privacy is set to **Unlisted** or **Public** (not Private).
4. **Devnovate Submission**: Submit on the Devnovate ideathon platform before **11:59 PM today**!

