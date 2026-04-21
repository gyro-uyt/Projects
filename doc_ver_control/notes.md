# DocVCS: Document Version Control System

## Overview
DocVCS is a lightweight, web-based document version control and collaboration system. It behaves as a localized alternative to Google Docs or a simplified Git, heavily focused on tracking the immutable history of text files, supporting concurrent edits over a local network, detecting specific changes via algorithms, and keeping data protected under user accounts.

---

## 1. Technology Stack

### Backend
*   **Python:** The core scripting language used for all algorithmic calculations and routing.
*   **Flask:** The lightweight web framework that acts as the server, routing HTTP requests from the browser to Python functions.
*   **Flask-Login & Werkzeug:** Handles secure user authentication, password hashing (`PBKDF2-SHA256`), and securely tracking HTTP session cookies.

### Frontend
*   **HTML5, CSS3, Vanilla JavaScript:** The core browser trifecta handling DOM structure, custom interactions (like the countdown toast alerts), and dynamic searching APIs.
*   **Bootstrap 5:** Extensive use of CSS classes for responsive grid layouts, navigational bars, modal-like visual UI elements, and overall aesthetic consistency. 
*   **Bootstrap Icons:** For clean, scalable SVG vector iconography used throughout the interface.

### Database Architecture
*   **SQLite:** A Serverless SQL database stored locally as a single file (`vcs.db`). The schema operates on three primary tables:
    1.  **Users:** Tracks registered accounts (`id`, `username`, `password_hash`).
    2.  **Documents:** Holds high-level document metadata (`id`, `title`, `created_at`).
    3.  **Revisions:** The heart of the app. Every saved change creates an immutable row here, tracking its assigned document, version number, textual content, parent pointer (the version it was editing off of), and a commit message.

---

## 2. Core Functionality

*   **Network-Wide Collaboration:** Binds to `0.0.0.0`, transforming the host laptop into a server. Any device (like a smartphone) connected to the same local network or hotspot can access the web application simultaneously.
*   **Immutable Version History:** Rather than overwriting a file, hitting "Save" branches off into a new Revision block. You can browse completely mapped document histories.
*   **Visual Diffs:** A visual engine that parses any two document iterations and renders a side-by-side color-coded view outlining precisely what text lines were added (green) or deleted (red).
*   **File I/O:** Upload `.txt` files directly into the ecosystem to instantly version track them, and download specific historical snapshots of a document back as a standard file.
*   **Contextual Spotlight Search:** A `Ctrl + K` global hotkey combined with an asynchronous `fetch` JavaScript API that combs through the SQLite database rapidly to find matching document titles and revision commit history.
*   **User Security:** Application-wide authentication gating. All viewing, modifications, and downloads are completely sealed behind a login layer.
*   **Dynamic Theming:** Seamless Dark/Light modes saved automatically to browser `localStorage`.

---

## 3. Underlying Mechanisms & Algorithms

The system uses complex algorithmic logic to prevent concurrent users from accidentally permanently destroying each other's work while using the app simultaneously. 

### Longest Common Subsequence (LCS)
When visual Diffs are generated, the underlying architecture relies on a dynamic programming algorithm known as the Longest Common Subsequence. It builds a matrix simulating the character-by-character transformation needed to turn Version A of a document into Version B. This is how the engine flawlessly identifies insertions versus deletions.

### Three-Way Merging & Conflict Detection pipelines
When a user begins editing "Revision 1", the app remembers they started from Revision 1. If User B swoops in and saves "Revision 2" first, User A is now attempting to save an obsolete copy.
When User A inevitably attempts to save:
1.  **Detection:** The app's logic prevents the database commit. It realizes the document has advanced.
2.  **Auto-Merger:** The application runs a Three-Way Merge algorithm. It fetches the Base (Rev 1), Mine (User A's edits), and Theirs (User B's rev 2 edits). If the users edited completely different parts of the document, the app mathematically stitches both edits together without interruption.
3.  **Manual Intervention:** If both users appended conflicting text to the exact same line numbers, the algorithm raises a "Merge Conflict" event. It triggers a specific visual conflict-resolution UI layout allowing the user to pick which combination stays.

---

## 4. Who Can Use It & How

**Target Audience:** Writers, coders, small teams, or students connected via the same local Wi-Fi / Hotspot who need robust, highly tracked document collaboration capabilities but want to retain complete privacy (as no data ever leaves the local network or travels to third-party internet cloud providers). 

**How to Operate:**
1.  **Ignition:** The host boots the terminal, activates their virtual environment (`venv`), and executes `python .\app.py`.
2.  **Host Access:** The host opens their web browser to `http://localhost:5000`. 
3.  **Local Access:** The host checks their IPv4 Address on their current active network interface (via `ipconfig`). Remote devices (e.g., phones connected to the host's hotspot) open their browsers to `http://[IP_ADDRESS]:5000` (for example: `http://10.228.193.21:5000`).
4.  All actors register accounts and immediately possess the capability to collaborate and cross-edit documents synced perfectly to the host's `vcs.db` file.
