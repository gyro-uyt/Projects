# DocVCS — Project Report
### Localized Document Version Control & Collaboration System

---

## 1. Executive Summary

**DocVCS** is a fully self-contained, web-based document version control system engineered to deliver Google Docs-level real-time collaboration and Git-level versioning granularity — entirely within the boundaries of a local network. It runs as a lightweight Python server, stores all data in a single local SQLite file, and requires zero external cloud infrastructure. The system implements three custom-built algorithms from scratch — a Dynamic Programming LCS diffing engine, a Three-Way Block Merge conflict resolver, and an Extractive NLP Summarizer — to provide intelligent document tracking, concurrent-edit safety, and AI-powered content summarization without ever transmitting data to third-party services.

---

## 2. Problem Statement & Rationale

### The Problem
In educational institutions, small teams, and privacy-sensitive environments, multiple users frequently need to collaboratively edit text documents. The existing solutions present significant trade-offs:

| Solution | Limitation |
|---|---|
| **Google Docs / Microsoft 365** | Requires constant internet. Data stored on third-party cloud servers — unacceptable for sensitive IP, academic integrity, or air-gapped environments. |
| **Git / GitHub** | Extremely steep learning curve for non-technical users (writers, students, researchers). Command-line driven. Not designed for prose documents. |
| **Email / USB Sharing** | No version tracking. Overwrites are permanent. No conflict detection. Manual reconciliation of edits. |

### Why DocVCS Is Needed
DocVCS eliminates every limitation above. It provides:
*   **Complete Data Sovereignty:** Every byte stays on the host machine's `vcs.db` file. Zero network egress. Zero cloud dependency.
*   **Zero Learning Curve:** A polished web UI accessible from any browser — phones, tablets, laptops — on the same Wi-Fi / hotspot.
*   **Algorithmic Safety Net:** Custom-built Dynamic Programming algorithms ensure concurrent edits never silently destroy data.
*   **Instant Deployment:** A single `python app.py` command transforms any laptop into a collaboration server.

---

## 3. Complete Technology Stack

### 3.1 Backend — Python & Flask

| Component | Role | Details |
|---|---|---|
| **Python 3** | Core language | All algorithmic computation, routing logic, database interaction, and server orchestration. |
| **Flask** | WSGI micro-framework | Lightweight HTTP request routing. Maps URL endpoints to Python handler functions. Uses Jinja2 for server-side HTML templating. |
| **Flask-Login** | Session management | Manages user sessions via secure HTTP cookies. Provides the `@login_required` decorator to gate every route. Implements `UserMixin` for session serialization. |
| **Werkzeug** | Security utilities | Provides `generate_password_hash()` and `check_password_hash()` using the **PBKDF2-SHA256** algorithm with salting for password storage. |
| **Gunicorn** | Production WSGI server | Listed in `requirements.txt` as the production-grade server alternative to Flask's built-in development server. |

**Server Binding:** The application binds to `host='0.0.0.0'` on `port=5000` with `debug=True`, making it accessible to any device on the same local network interface.

### 3.2 Database — SQLite3

**Engine:** SQLite3 — a serverless, zero-configuration, transactional SQL database engine. The entire database is a single portable file: `vcs.db`.

**Connection Management:** `sqlite3.connect('vcs.db', check_same_thread=False)` with `conn.row_factory = sqlite3.Row` enabling dictionary-style column access on query results.

**Relational Schema (3 Tables):**

```
┌─────────────────────────────────────────────────────┐
│                      users                          │
├──────────────────┬──────────────────────────────────┤
│ id               │ INTEGER PRIMARY KEY AUTOINCREMENT│
│ username         │ TEXT UNIQUE NOT NULL              │
│ password_hash    │ TEXT NOT NULL                     │
└──────────────────┴──────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                    documents                        │
├──────────────────┬──────────────────────────────────┤
│ id               │ INTEGER PRIMARY KEY AUTOINCREMENT│
│ title            │ TEXT NOT NULL                     │
│ created_at       │ DATETIME DEFAULT CURRENT_TIMESTAMP│
└──────────────────┴──────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                    revisions                        │
├──────────────────┬──────────────────────────────────┤
│ id               │ INTEGER PRIMARY KEY AUTOINCREMENT│
│ document_id      │ INTEGER NOT NULL (FK → documents)│
│ version_number   │ INTEGER NOT NULL                 │
│ content          │ TEXT NOT NULL                     │
│ parent_id        │ INTEGER (self-referencing FK)     │
│ commit_message   │ TEXT DEFAULT 'No commit message'  │
│ timestamp        │ DATETIME DEFAULT CURRENT_TIMESTAMP│
└──────────────────┴──────────────────────────────────┘
```

**Key Design Decisions:**
*   `parent_id` in `revisions` is a self-referencing foreign key. It creates a linked-list (or tree) of version ancestry, enabling the system to trace which revision a user was editing when they submitted — this is the backbone of concurrent-edit detection.
*   All timestamps use `CURRENT_TIMESTAMP` (UTC) and are converted to local time in queries via `datetime(timestamp, "localtime")`.
*   `check_same_thread=False` is required because Flask serves multiple HTTP requests from different threads, while SQLite defaults to single-thread access.

**Schema Migration:** A dedicated `migrate.py` script handles backward-compatible `ALTER TABLE` operations (e.g., adding the `commit_message` column to existing databases) with graceful error handling via `sqlite3.OperationalError` catch.

### 3.3 Frontend — HTML5, CSS3, JavaScript (ES6)

| Component | Version | Role |
|---|---|---|
| **HTML5** | — | Semantic document structure via Jinja2 templates |
| **CSS3** | — | Custom styles for diff coloring, timeline visualization, toast animations, and navbar theming |
| **JavaScript ES6** | — | Asynchronous `fetch()` API for search, Bootstrap modal event listeners for summarization, theme persistence via `localStorage`, debounced input handlers |
| **Bootstrap** | 5.3.0 | Responsive flexbox grid, cards, modals, dropdowns, badges, alerts, list-groups, form controls |
| **Bootstrap Icons** | 1.11.1 | SVG icon library — `bi-file-earmark-text`, `bi-clock-history`, `bi-person-circle`, `bi-stars`, `bi-robot`, `bi-github`, `bi-sun-fill`, `bi-moon-stars-fill`, etc. |

**Template Inheritance Architecture (Jinja2):**
All 11 templates extend a single `layout.html` base template which provides:
*   The full navbar with logo, search bar, auth links, version badge, GitHub link, and theme toggle
*   Flash message rendering with animated SVG countdown timers
*   Bootstrap CSS/JS CDN includes
*   Theme persistence JavaScript
*   Global search JavaScript

```
layout.html (Base)
├── index.html        — Document listing + Upload modal
├── view_doc.html     — Document viewer + Summarize modal
├── new_doc.html      — New document form
├── edit_doc.html     — Edit form with parent_id tracking
├── history.html      — Timeline view + Custom Compare sidebar
├── diff.html         — Side-by-side diff table
├── merge.html        — 3-way merge selector
├── merge_result.html — Conflict viewer + Resolution editor
├── login.html        — Login form
└── register.html     — Registration form
```

### 3.4 Dependencies (`requirements.txt`)

```
Flask
Flask-Login
Werkzeug
gunicorn
```

All algorithmic modules (`algo.py`) use only Python standard library imports (`re`, `collections.defaultdict`). Zero external NLP or ML libraries are required.

---

## 4. Algorithms — Deep Technical Breakdown

### 4.1 Longest Common Subsequence (LCS) — Dynamic Programming

**Purpose:** Powers the diff engine. Given two sequences of lines (old document vs. new document), LCS identifies which lines are shared (unchanged), which exist only in the old (deleted), and which exist only in the new (inserted).

**Implementation (`algo.py → lcs()`):**

```
Algorithm: Bottom-Up Dynamic Programming
Time Complexity:  O(m × n)   where m = len(old_lines), n = len(new_lines)
Space Complexity: O(m × n)   (full 2D matrix stored)
```

**Step-by-step execution:**
1.  Construct a 2D matrix `L[m+1][n+1]` initialized to zeros.
2.  For each pair `(i, j)`:
    *   If `old_lines[i-1] == new_lines[j-1]` → `L[i][j] = L[i-1][j-1] + 1` (extend the matching subsequence)
    *   Otherwise → `L[i][j] = max(L[i-1][j], L[i][j-1])` (take the better of skipping one line from either sequence)
3.  Return the completed matrix `L`.

**Backtracking (`algo.py → get_diff()`):**
Starting from `L[m][n]`, the algorithm traces backward:
*   If lines match → emit `('equal', line)`, move diagonally `(i-1, j-1)`
*   If `L[i-1][j] > L[i][j-1]` → emit `('delete', old_line)`, move up `(i-1, j)`
*   Otherwise → emit `('insert', new_line)`, move left `(i, j-1)`
*   Remaining lines in either sequence are emitted as pure deletions or insertions.
*   The result is reversed to produce the diff in forward order.

### 4.2 Side-by-Side Diff Rendering

**Implementation (`algo.py → get_side_by_side_diff()`):**

Takes the raw diff output and transforms it into a structured list suitable for tabular HTML rendering:

| Diff Type | Left Column | Right Column | Visual Effect |
|---|---|---|---|
| `equal` | Old line + line number | Same line + line number | Neutral background |
| `delete` | Old line + line number | Empty | Red background (left) |
| `insert` | Empty | New line + line number | Green background (right) |
| `replace` | Old line + line number | New line + line number | Red left, Green right |

**Replace Detection:** When a `delete` operation is immediately followed by an `insert` in the diff stream, the algorithm combines them into a single `replace` row — visually showing the old and new text side-by-side on the same row for clearer readability.

**Frontend Rendering (`diff.html`):**
*   Uses a `<table>` with monospaced `Consolas` font
*   CSS classes `diff-type-insert`, `diff-type-delete`, `diff-type-replace`, `diff-type-equal` provide RGBA-based color backgrounds
*   Dark mode variants are handled via `[data-bs-theme="dark"]` CSS selectors with adjusted opacity

### 4.3 Chunk-Based Diff Extraction (for Merge)

**Implementation (`algo.py → get_chunks()`):**

Converts a raw diff into "chunks" — contiguous groups of changes anchored to base-document line indices. Each chunk records:
*   `base_start` / `base_end`: The range of base lines this change replaces
*   `lines[]`: The new lines being inserted in place of the base range
*   `source`: Tagged as `'mine'` or `'theirs'` during merge

This is the atomic unit the merge algorithm operates on.

### 4.4 Three-Way Block Merge with Conflict Detection

**Implementation (`algo.py → basic_merge()`):**

**The concurrency problem:** Two users (A and B) both begin editing the same base revision. User B saves first. When User A tries to save, their `parent_id` no longer matches the latest revision in the database — the system detects an outdated edit.

**Algorithm flow:**

```
Input:  base_content, mine_content (User A), theirs_content (User B)
Output: merged_content, has_conflict (boolean)
```

1.  **Fast-path shortcuts:**
    *   `mine == theirs` → return either (identical edits)
    *   `mine == base` → return `theirs` (only B changed)
    *   `theirs == base` → return `mine` (only A changed)

2.  **Chunk extraction:**
    *   `mine_chunks = get_chunks(base, mine)` — what User A changed
    *   `theirs_chunks = get_chunks(base, theirs)` — what User B changed
    *   Tag each chunk with `source = 'mine'` or `source = 'theirs'`

3.  **Merge all chunks sorted by `base_start`:**
    *   Iterate through chunks. For each chunk, build a "conflict group" by greedily absorbing any subsequent overlapping chunks (chunks whose `base_start..base_end` ranges intersect).

4.  **Overlap detection function:**
    ```python
    def overlap(a, b):
        if max(a['base_start'], b['base_start']) < min(a['base_end'], b['base_end']): return True
        if a['base_start'] == b['base_start'] == a['base_end'] == b['base_end']: return True  # pure insertions at same point
        return False
    ```

5.  **Resolution:**
    *   If a conflict group contains chunks from **both** sources with **different content** → **CONFLICT**. Wrap in Git-style markers: `<<<<<<< CURRENT VERSION ... ======= ... >>>>>>> INCOMING VERSION`
    *   If chunks from both sources have **identical content and positions** → deduplicate (both users made the same edit)
    *   If chunks are from a **single source** → apply cleanly
    *   Unchanged base lines between chunks are copied verbatim.

6.  **Output:** Either a cleanly merged string or a conflict-marked string with `has_conflict = True`.

**Concurrency Trigger in `app.py → edit_doc()`:**
```python
if actual_latest['id'] != int(parent_id):
    # Someone else saved while this user was editing
    merged_content, has_conflict = basic_merge(base, mine, theirs)
```
If clean → auto-save with "[Auto-merged]" commit prefix.
If conflict → redirect to `merge_result.html` with visual conflict resolution UI.

### 4.5 Extractive AI Summarization (NLP Pipeline)

**Implementation (`algo.py → summarize_text()`):**

A fully offline, privacy-preserving text summarization algorithm using extractive NLP techniques. No external AI APIs. No internet required.

**Pipeline stages:**

```
Raw Text → Sentence Splitting → Stop-Word Filtering → Term Frequency Scoring
→ Frequency Normalization → Sentence Scoring → Top-K Extraction → Summary
```

**Stage 1 — Sentence Tokenization:**
```python
sentences = re.split(r'(?<=[.!?])\s+', text.strip())
```
Uses a regex lookbehind to split on sentence-ending punctuation (`.`, `!`, `?`) followed by whitespace. Filters out fragments shorter than 5 characters.

**Stage 2 — Stop-Word Filtering:**
A curated set of 30 high-frequency English function words (`the`, `is`, `in`, `and`, `to`, `of`, `a`, `it`, `that`, `this`, `on`, `for`, `with`, `as`, `by`, `an`, `be`, `at`, `are`, `was`, `were`, `but`, `not`, `or`, `what`, `when`, `where`, `how`, `who`, `which`, `will`, `would`, `can`, `could`) are excluded from frequency analysis. These words carry minimal semantic weight.

**Stage 3 — Term Frequency (TF) Computation:**
```python
word_frequencies = defaultdict(int)
for sentence in sentences:
    words = re.findall(r'\b[A-Za-z]{2,}\b', sentence.lower())
    for word in words:
        if word not in stop_words:
            word_frequencies[word] += 1
```
Extracts alphabetic tokens of length ≥ 2, case-normalized, and increments their global frequency count.

**Stage 4 — Frequency Normalization:**
```python
max_frequency = max(word_frequencies.values())
word_frequencies[word] /= max_frequency  # Scale to [0.0, 1.0]
```
All word scores are normalized to a `[0, 1]` range relative to the most frequent meaningful term.

**Stage 5 — Sentence Scoring with Positional Bias:**
```python
sentence_scores[i] += word_frequencies[word] + (0.1 / (i + 1))
```
Each sentence receives a cumulative score based on its constituent word weights. A small positional bias `0.1 / (i + 1)` is added to slightly favor earlier sentences — reflecting the journalism/academic convention that opening sentences tend to be more topically important ("inverted pyramid" structure).

**Stage 6 — Top-K Extraction:**
The top `num_sentences` (default: 4) highest-scoring sentences are selected. Their original order in the document is preserved (sorted by index, not score) to maintain logical flow.

**Output:** A coherent, readable summary string that captures the document's most information-dense sentences.

---

## 5. Application Routes — Complete API Surface

### 5.1 Authentication Routes

| Method | Endpoint | Function | Description |
|---|---|---|---|
| GET/POST | `/register` | `register()` | Renders registration form. On POST: checks username uniqueness, hashes password via PBKDF2-SHA256, inserts into `users` table. |
| GET/POST | `/login` | `login()` | Renders login form. On POST: validates credentials via `check_password_hash()`, creates session via `login_user()`. |
| GET | `/logout` | `logout()` | Destroys session via `logout_user()`. Redirects to login. |

### 5.2 Document CRUD Routes

| Method | Endpoint | Function | Description |
|---|---|---|---|
| GET | `/` | `index()` | Dashboard. Queries all documents with their latest revision timestamp via `MAX(datetime(r.timestamp, "localtime"))` aggregate join. Sorted by most recently updated. |
| GET/POST | `/doc/new` | `new_doc()` | Create document form. On POST: inserts into `documents`, creates initial `revisions` row with `version_number=1`. |
| POST | `/upload` | `upload_doc()` | File upload handler. Accepts `.txt/.md/.csv/.json` files via `multipart/form-data`. Decodes UTF-8. Uses custom title or falls back to filename. Creates document + initial revision. |
| GET | `/doc/<id>` | `view_doc()` | Displays latest revision content. Provides action buttons: Edit, History, Merge Tools, Download, Summarize. |
| GET/POST | `/doc/<id>/edit` | `edit_doc()` | Edit form with hidden `parent_id` field. On POST: **checks if `parent_id` matches actual latest revision.** If mismatch → triggers 3-way merge. If clean → auto-merges. If conflict → routes to `merge_result.html`. |
| GET | `/doc/<id>/history` | `history()` | Displays all revisions in a CSS timeline layout with commit messages, timestamps, diff links, and per-version download buttons. Includes a "Custom Compare" sidebar for arbitrary version pair diffing. |
| GET | `/doc/<id>/diff` | `diff_view()` | Accepts `target` and optional `compare_to` revision IDs. Runs `get_side_by_side_diff()`. If only `target` provided, auto-diffs against its `parent_id`. Handles version ordering (swaps if older > newer). |
| GET/POST | `/doc/<id>/merge` | `merge_view()` | Manual merge tool. Lets users select Base/Mine/Theirs revisions from dropdowns. On POST: runs `basic_merge()` and renders result. |
| GET | `/doc/<id>/download` | `download_doc()` | Downloads revision content as a `.txt` file. Sanitizes filename from document title (alphanumeric + spaces only). Sets `Content-disposition: attachment` header. |

### 5.3 API Routes (JSON)

| Method | Endpoint | Function | Description |
|---|---|---|---|
| GET | `/api/search?q=&doc_id=` | `api_search()` | If `doc_id` is empty: searches `documents.title` via `LIKE`. If `doc_id` is set: searches `revisions.commit_message` and `version_number` within that document. Returns JSON array. Supports `v` prefix stripping for version searches. |
| GET | `/api/doc/<id>/summarize` | `api_summarize_doc()` | Fetches latest revision content, runs `summarize_text()`, returns `{"summary": "..."}`. |

---

## 6. Frontend Systems — Detailed Mechanics

### 6.1 Navbar & Branding
*   Custom teal (`#2a928c`) navbar background
*   Inline SVG document icon as logo
*   Centered search bar with translucent `rgba(255,255,255,0.15)` background
*   `Ctrl+K` badge rendered beside search input
*   GitHub source link, version badge (`v1.0`), vertical dividers, user display, and theme dropdown

### 6.2 Toast Notification System
Flash messages from Flask are rendered as Bootstrap alerts with a custom **SVG countdown timer animation**:
*   An SVG `<path>` draws a circle using `stroke-dasharray: 100, 100`
*   A CSS `@keyframes countdown` animation sweeps `stroke-dashoffset` from `0 → 100` over 5 seconds
*   A corresponding `setTimeout(5000)` JavaScript call triggers `bootstrap.Alert.close()` for synchronized auto-dismissal

### 6.3 Global Spotlight Search
*   **Trigger:** `Ctrl+K` keyboard shortcut or direct click
*   **Debounce:** 250ms `setTimeout` debounce on input events
*   **Context-Aware:** Extracts `doc_id` from the current URL via regex `/\/(doc|edit|history|diff|merge)\/(\d+)/`
    *   On dashboard → searches document titles globally
    *   Inside a document → searches revision commit messages and version numbers within that document
*   **Rendering:** Dynamically builds `<li>` elements with Bootstrap Icons (`bi-file-earmark-text` for docs, `bi-clock-history` + version badge for revisions)
*   **Dismissal:** Click-outside handler hides dropdown

### 6.4 Theme Persistence
*   Bootstrap 5.3 `data-bs-theme` attribute toggling between `"light"` and `"dark"`
*   User preference stored in `localStorage.setItem('theme', ...)`
*   On page load: reads `localStorage.getItem('theme') || 'light'` and applies immediately
*   Navbar icon swaps between `bi-sun-fill` and `bi-moon-stars-fill`
*   Diff colors have dedicated dark-mode CSS overrides using `[data-bs-theme="dark"]` selectors

### 6.5 AI Summarization Modal
*   Triggered by the "Summarize" button on `view_doc.html`
*   Uses Bootstrap 5 Modal with `show.bs.modal` event listener
*   Shows a spinner + "Reading and extracting key points..." loading state
*   Fires async `fetch()` to `/api/doc/<id>/summarize`
*   On success: renders summary in a styled blockquote with left border accent
*   On failure: renders error alert inside the modal

### 6.6 Version History Timeline
*   Pure CSS timeline using `::before` pseudo-elements
*   Vertical line via `position: absolute` 2px-wide element
*   Circular node markers with `border-radius: 50%`, blue fill, white border, and box-shadow
*   Each node shows version number, commit message, timestamp badge, diff link, and download button

### 6.7 Conflict Resolution Viewer
*   `merge_result.html` renders raw conflict content in a monospaced viewer
*   JavaScript regex replaces escape-encoded Git markers (`&lt;&lt;&lt;&lt;&lt;&lt;&lt;`, `=======`, `&gt;&gt;&gt;&gt;&gt;&gt;&gt;`) with color-coded Bootstrap-styled `<span>` and `<div>` blocks:
    *   `<<<<<<< CURRENT VERSION` → Red banner + red-tinted content block
    *   `=======` → Yellow separator banner
    *   `>>>>>>> INCOMING VERSION` → Green banner + green-tinted content block
*   Below the viewer: a `<textarea>` pre-filled with the conflict content for manual resolution

---

## 7. File Structure & Project Architecture

```
doc_ver_control/
├── app.py              — Flask application (419 lines). All 15 routes, auth, session management.
├── algo.py             — Algorithm module (254 lines). LCS, diff, merge, summarization.
├── database.py         — Database module (38 lines). Connection factory, schema initialization.
├── migrate.py          — Schema migration script (16 lines). ALTER TABLE operations.
├── requirements.txt    — Python dependencies (4 packages).
├── .gitignore          — Excludes venv/, __pycache__/, vcs.db, OS files.
├── readme.md           — Quick-start documentation.
├── notes.md            — Detailed project notes & writeup.
├── vcs.db              — SQLite database file (runtime-generated, gitignored).
├── venv/               — Python virtual environment (gitignored).
└── templates/
    ├── layout.html         — Base template (278 lines). Navbar, flash system, search, theme toggle.
    ├── index.html          — Document dashboard + upload modal.
    ├── view_doc.html       — Document reader + summarize modal.
    ├── new_doc.html        — New document creation form.
    ├── edit_doc.html       — Edit form with version tracking hidden fields.
    ├── history.html        — Timeline view + custom compare tool.
    ├── diff.html           — Side-by-side diff table with color coding.
    ├── merge.html          — 3-way merge revision selector.
    ├── merge_result.html   — Conflict visual viewer + manual editor.
    ├── login.html          — User login form.
    └── register.html       — User registration form.
```

---

## 8. Security Model

| Layer | Mechanism |
|---|---|
| **Password Storage** | PBKDF2-SHA256 with random salt via `werkzeug.security.generate_password_hash()`. Raw passwords are never stored. |
| **Session Management** | Flask-Login manages server-side sessions via signed cookies. `app.secret_key` signs session tokens. |
| **Route Protection** | Every document-related route is decorated with `@login_required`. Unauthenticated requests redirect to `/login`. |
| **Input Validation** | Username uniqueness enforced via SQL `UNIQUE` constraint + pre-insert check. File uploads restricted to UTF-8 decodable content. Filename sanitization on download strips non-alphanumeric characters. |
| **Data Isolation** | `vcs.db` is gitignored — credentials and documents are never committed to version control. |

---

## 9. Deployment & Network Access

| Mode | Address | Use Case |
|---|---|---|
| **Host-local** | `http://localhost:5000` | The machine running the server |
| **LAN / Hotspot** | `http://<HOST_IPv4>:5000` | Any device on the same network (phones, tablets, other laptops). Host IPv4 obtained via `ipconfig` on Windows. |

**Startup procedure:**
```
1. cd doc_ver_control
2. .\venv\Scripts\activate         # Activate virtual environment
3. python app.py                   # Starts Flask on 0.0.0.0:5000
```

---

## 10. Target Audience & Use Cases

*   **Students:** Collaborative essay writing or lab report editing over a shared hotspot; no institutional cloud required.
*   **Writers & Editors:** Track manuscript revisions with full diff history and commit messages. Revert to any past version.
*   **Small Teams:** Simultaneous editing with automatic merge — conflict markers only appear when edits overlap.
*   **Privacy-Sensitive Environments:** Air-gapped or restricted networks where data must never leave the local machine.
*   **Educational Projects:** The codebase itself serves as a teaching tool for Dynamic Programming, web architecture, database design, and NLP techniques.

---

## 11. Summary of Algorithmic Complexity

| Algorithm | Time Complexity | Space Complexity | Location |
|---|---|---|---|
| LCS Matrix Construction | O(m × n) | O(m × n) | `algo.py → lcs()` |
| Diff Backtracking | O(m + n) | O(m + n) | `algo.py → get_diff()` |
| Side-by-Side Transform | O(d) where d = diff length | O(d) | `algo.py → get_side_by_side_diff()` |
| Chunk Extraction | O(d) | O(c) where c = chunks | `algo.py → get_chunks()` |
| Three-Way Merge | O(c² ) worst case overlap check | O(c) | `algo.py → basic_merge()` |
| Extractive Summarization | O(s × w) where s = sentences, w = avg words | O(w + s) | `algo.py → summarize_text()` |
