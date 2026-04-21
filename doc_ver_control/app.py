from flask import Flask, render_template, request, redirect, url_for, flash, Response, jsonify
from database import get_db, init_db
from algo import get_side_by_side_diff, basic_merge
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'super_secret_key'

login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id, username FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    if user:
        return User(id=user['id'], username=user['username'])
    return None

with app.app_context():
    init_db()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            flash('Username already exists.', 'danger')
            return redirect(url_for('register'))
            
        password_hash = generate_password_hash(password)
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
        db.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT id, username, password_hash FROM users WHERE username = ?', (username,))
        user_row = cursor.fetchone()
        
        if user_row and check_password_hash(user_row['password_hash'], password):
            user = User(id=user_row['id'], username=user_row['username'])
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT d.id, d.title, MAX(datetime(r.timestamp, "localtime")) as last_updated 
        FROM documents d 
        LEFT JOIN revisions r ON d.id = r.document_id 
        GROUP BY d.id 
        ORDER BY last_updated DESC
    ''')
    documents = cursor.fetchall()
    return render_template('index.html', documents=documents)

@app.route('/doc/new', methods=['GET', 'POST'])
@login_required
def new_doc():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        commit_message = request.form.get('commit_message', 'Initial save')
        
        if not title:
            flash('Title is required!', 'danger')
            return redirect(url_for('new_doc'))
            
        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO documents (title) VALUES (?)', (title,))
        doc_id = cursor.lastrowid
        
        cursor.execute('''
            INSERT INTO revisions (document_id, version_number, content, commit_message) 
            VALUES (?, ?, ?, ?)
        ''', (doc_id, 1, content, commit_message))
        db.commit()
        
        flash('Document created successfully!', 'success')
        return redirect(url_for('view_doc', id=doc_id))
    
    return render_template('new_doc.html')

@app.route('/upload', methods=['POST'])
@login_required
def upload_doc():
    file = request.files.get('file')
    if not file or file.filename == '':
        flash('No file selected', 'warning')
        return redirect(url_for('index'))
        
    custom_title = request.form.get('title', '').strip()
    title = custom_title if custom_title else file.filename
    
    try:
        content = file.read().decode('utf-8')
    except UnicodeDecodeError:
        flash('Could not read file. Only plain-text files are supported.', 'danger')
        return redirect(url_for('index'))
        
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO documents (title) VALUES (?)', (title,))
    doc_id = cursor.lastrowid
    
    cursor.execute('''
        INSERT INTO revisions (document_id, version_number, content, commit_message) 
        VALUES (?, ?, ?, ?)
    ''', (doc_id, 1, content, 'Initial file upload'))
    db.commit()
    
    flash('Document uploaded successfully!', 'success')
    return redirect(url_for('view_doc', id=doc_id))

@app.route('/doc/<int:id>', methods=['GET'])
@login_required
def view_doc(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id, title FROM documents WHERE id = ?', (id,))
    doc = cursor.fetchone()
    if not doc:
        return "Document not found", 404
        
    cursor.execute('''
        SELECT id, version_number, content, commit_message, datetime(timestamp, "localtime") as timestamp 
        FROM revisions 
        WHERE document_id = ? 
        ORDER BY version_number DESC LIMIT 1
    ''', (id,))
    latest_rev = cursor.fetchone()
    return render_template('view_doc.html', doc=doc, rev=latest_rev)

@app.route('/doc/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_doc(id):
    db = get_db()
    cursor = db.cursor()
    if request.method == 'POST':
        new_content = request.form['content']
        parent_id = request.form['parent_id']
        submitted_version_num = int(request.form['version_number'])
        version_number = submitted_version_num + 1
        commit_message = request.form.get('commit_message', 'Update document')
        
        # Check actual latest to prevent overwrite
        cursor.execute('''
            SELECT id, version_number, content 
            FROM revisions 
            WHERE document_id = ? 
            ORDER BY version_number DESC LIMIT 1
        ''', (id,))
        actual_latest = cursor.fetchone()
        
        if actual_latest and actual_latest['id'] != int(parent_id):
            cursor.execute('SELECT content FROM revisions WHERE id = ?', (parent_id,))
            base_content = cursor.fetchone()['content']
            
            merged_content, has_conflict = basic_merge(base_content, new_content, actual_latest['content'])
            
            if has_conflict:
                flash("Concurrent Edit Detected! Someone else updated the document while you were working. We tried to auto-merge but found overlapping changes. Please resolve them below.", "danger")
                # Route them to merge resolution UI
                cursor.execute('SELECT id, title FROM documents WHERE id = ?', (id,))
                return render_template('merge_result.html', doc=cursor.fetchone(), content=merged_content, has_conflict=True, base_id=actual_latest['id'])
            else:
                new_content = merged_content
                parent_id = actual_latest['id']
                version_number = actual_latest['version_number'] + 1
                commit_message = f"Auto-merged: {commit_message}"
                flash("Someone edited the document while you were working, but your changes were cleanly auto-merged!", "info")
        
        cursor.execute('''
            INSERT INTO revisions (document_id, version_number, content, parent_id, commit_message)
            VALUES (?, ?, ?, ?, ?)
        ''', (id, version_number, new_content, parent_id, commit_message))
        db.commit()
        
        flash('New revision saved!', 'success')
        return redirect(url_for('view_doc', id=id))
        
    cursor.execute('SELECT id, title FROM documents WHERE id = ?', (id,))
    doc = cursor.fetchone()
    cursor.execute('''
        SELECT id, version_number, content 
        FROM revisions 
        WHERE document_id = ? 
        ORDER BY version_number DESC LIMIT 1
    ''', (id,))
    rev = cursor.fetchone()
    return render_template('edit_doc.html', doc=doc, rev=rev)

@app.route('/doc/<int:id>/history')
@login_required
def history(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id, title FROM documents WHERE id = ?', (id,))
    doc = cursor.fetchone()
    cursor.execute('''
        SELECT id, version_number, datetime(timestamp, "localtime") as timestamp, commit_message, parent_id
        FROM revisions 
        WHERE document_id = ? 
        ORDER BY version_number DESC
    ''', (id,))
    revisions = cursor.fetchall()
    
    current_target = request.args.get('target', '')
    current_compare_to = request.args.get('compare_to', '')
    
    return render_template('history.html', doc=doc, revisions=revisions, current_target=current_target, current_compare_to=current_compare_to)

@app.route('/doc/<int:id>/diff')
@login_required
def diff_view(id):
    target_rev_id = request.args.get('target')
    compare_to_id = request.args.get('compare_to')
    
    db = get_db()
    cursor = db.cursor()
    
    if target_rev_id and compare_to_id:
        cursor.execute('SELECT version_number, content FROM revisions WHERE id = ?', (compare_to_id,))
        r1 = cursor.fetchone()
        cursor.execute('SELECT version_number, content FROM revisions WHERE id = ?', (target_rev_id,))
        r2 = cursor.fetchone()
        if not r1 or not r2:
            flash("One or both selected revisions do not exist.", "warning")
            return redirect(url_for('history', id=id))

    elif target_rev_id:
        cursor.execute('SELECT version_number, content, parent_id FROM revisions WHERE id = ?', (target_rev_id,))
        r2 = cursor.fetchone()
        if not r2:
            flash("Target revision does not exist.", "warning")
            return redirect(url_for('history', id=id))
            
        if r2['parent_id']:
            cursor.execute('SELECT version_number, content FROM revisions WHERE id = ?', (r2['parent_id'],))
            r1 = cursor.fetchone()
            if not r1:
                r1 = {'version_number': 0, 'content': ''}
        else:
            r1 = {'version_number': 0, 'content': ''} # Initial commit
    else:
        flash("Invalid diff request.", "warning")
        return redirect(url_for('history', id=id))
        
    if int(r1['version_number']) > int(r2['version_number']):
        r1, r2 = r2, r1
        
    old_lines = r1['content'].splitlines()
    new_lines = r2['content'].splitlines()
    
    sbs_diff = get_side_by_side_diff(old_lines, new_lines)
    
    r1_id = ''
    try:
        r1_id = r1['id']
    except Exception:
        pass
        
    r2_id = ''
    try:
        r2_id = r2['id']
    except Exception:
        pass
    
    return render_template('diff.html', diff_data=sbs_diff, r1=r1, r2=r2, doc_id=id, r1_id=r1_id, r2_id=r2_id)

@app.route('/doc/<int:id>/merge', methods=['GET', 'POST'])
@login_required
def merge_view(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id, title FROM documents WHERE id = ?', (id,))
    doc = cursor.fetchone()
    
    if request.method == 'POST':
        base_id = request.form['base_id']
        mine_id = request.form['mine_id']
        theirs_id = request.form['theirs_id']
        
        cursor.execute('SELECT content FROM revisions WHERE id = ?', (base_id,))
        base_content = cursor.fetchone()['content']
        cursor.execute('SELECT content FROM revisions WHERE id = ?', (mine_id,))
        mine_content = cursor.fetchone()['content']
        cursor.execute('SELECT content FROM revisions WHERE id = ?', (theirs_id,))
        theirs_content = cursor.fetchone()['content']
        
        merged_content, has_conflict = basic_merge(base_content, mine_content, theirs_content)
        return render_template('merge_result.html', doc=doc, content=merged_content, has_conflict=has_conflict, base_id=base_id)
        
    cursor.execute('''
        SELECT id, version_number, datetime(timestamp, "localtime") as timestamp, commit_message
        FROM revisions 
        WHERE document_id = ? 
        ORDER BY version_number DESC
    ''', (id,))
    revisions = cursor.fetchall()
    return render_template('merge.html', doc=doc, revisions=revisions)

@app.route('/doc/<int:id>/download')
@login_required
def download_doc(id):
    rev_id = request.args.get('rev_id')
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT title FROM documents WHERE id = ?', (id,))
    doc = cursor.fetchone()
    
    if rev_id:
        cursor.execute('SELECT version_number, content FROM revisions WHERE id = ?', (rev_id,))
    else:
        cursor.execute('SELECT version_number, content FROM revisions WHERE document_id = ? ORDER BY version_number DESC LIMIT 1', (id,))
        
    rev = cursor.fetchone()
    
    safe_title = "".join([c for c in doc['title'] if c.isalpha() or c.isdigit() or c==' ']).rstrip().replace(" ", "_")
    if not safe_title:
        safe_title = "document"
    filename = f"{safe_title}_v{rev['version_number']}.txt"
    
    return Response(
        rev['content'],
        mimetype="text/plain",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )

@app.route('/api/search')
@login_required
def api_search():
    query = request.args.get('q', '').strip()
    doc_id = request.args.get('doc_id')
    
    if not query:
        return jsonify([])
        
    db = get_db()
    cursor = db.cursor()
    
    if not doc_id:
        cursor.execute("SELECT id, title FROM documents WHERE title LIKE ? LIMIT 10", ('%' + query + '%',))
        docs = cursor.fetchall()
        return jsonify([{'type': 'doc', 'id': d['id'], 'text': d['title']} for d in docs])
    else:
        import re
        version_num = re.sub(r'^[vV]\s*', '', query)
        
        cursor.execute("""
            SELECT id, version_number, commit_message 
            FROM revisions 
            WHERE document_id = ? AND (commit_message LIKE ? OR CAST(version_number AS TEXT) LIKE ?)
            ORDER BY version_number DESC
            LIMIT 15
        """, (doc_id, '%' + query + '%', '%' + version_num + '%'))
        revs = cursor.fetchall()
        return jsonify([{'type': 'rev', 'id': r['id'], 'doc_id': doc_id, 'version': r['version_number'], 'text': r['commit_message']} for r in revs])

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
