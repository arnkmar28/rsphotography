import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from werkzeug.utils import secure_filename
from database import init_db, get_db, close_db
import config
import cloudinary
import cloudinary.uploader

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16MB max upload

# Initialize Cloudinary
cloudinary.config(
    cloud_name = config.CLOUDINARY_CLOUD_NAME,
    api_key = config.CLOUDINARY_API_KEY,
    api_secret = config.CLOUDINARY_API_SECRET
)

# Initialize DB (Note: In production with multiple workers, this might run multiple times, which is fine for IF NOT EXISTS)
# Ideally run this from a separate script or build step.
with app.app_context():
    init_db()

@app.teardown_appcontext
def teardown_db(exception):
    close_db(exception)

@app.route('/')
def index():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM images ORDER BY created_at DESC')
    images = cur.fetchall()
    cur.close()
    return render_template('index.html', images=images)

@app.route('/contact', methods=['POST'])
def contact():
    # In a real app, send email here
    flash('Thank you for your quote request! We will contact you shortly.', 'success')
    return redirect(url_for('index'))

# --- Admin Routes ---

def login_required(f):
    def wrapper(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.route('/admin', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == config.ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid password', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM images ORDER BY created_at DESC')
    images = cur.fetchall()
    cur.close()
    return render_template('dashboard.html', images=images)

@app.route('/dashboard/upload', methods=['POST'])
@login_required
def upload_image():
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('dashboard'))
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('dashboard'))
    
    if file:
        try:
            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(file)
            
            # Save to DB
            conn = get_db()
            cur = conn.cursor()
            cur.execute('INSERT INTO images (public_id, url, title) VALUES (%s, %s, %s)',
                       (upload_result['public_id'], upload_result['secure_url'], request.form.get('title', 'Untitled')))
            conn.commit()
            cur.close()
            flash('Image uploaded successfully', 'success')
        except Exception as e:
            flash(f'Error uploading image: {str(e)}', 'error')
        
    return redirect(url_for('dashboard'))

@app.route('/dashboard/delete/<int:id>', methods=['POST'])
@login_required
def delete_image(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT public_id FROM images WHERE id = %s', (id,))
    image = cur.fetchone()
    
    if image:
        try:
            # Delete from Cloudinary
            cloudinary.uploader.destroy(image['public_id'])
            
            # Delete from DB
            cur.execute('DELETE FROM images WHERE id = %s', (id,))
            conn.commit()
            flash('Image deleted', 'success')
        except Exception as e:
             flash(f'Error deleting image: {str(e)}', 'error')
             pass

    cur.close()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)

