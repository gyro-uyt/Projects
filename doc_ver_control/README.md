# Document Version Control

A lightweight document version-control tool built with Flask, SQLite, and Bootstrap (Light Mode). 

## Features
- **Store Revisions**: Documents and their history are saved in a local SQLite database.
- **Diff Detection**: Implements the Dynamic Programming Longest Common Subsequence (LCS) algorithm to detect added, removed, or identical lines between versions.
- **Merge Utility**: Provides a basic 3-way merge operation by taking a base, incoming, and current version, producing either a merged text or inserting conflict markers.

## How to run
1. Ensure Python 3 is installed.
2. Install Flask: `pip install -r requirements.txt`
3. Run the app: `python app.py`
4. Visit `http://127.0.0.1:5000` in your web browser.

## File Structure
- `app.py`: Flask application logic and routing.
- `algo.py`: Dynamic programming algorithms for diff and merge.
- `database.py`: Contains database initialization and connection utilities.
- `templates/`: Bootstrap-based custom UI with no emoji, formatted in light mode.
