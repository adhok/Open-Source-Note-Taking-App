from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
import os
import sys
import json
import uuid
from datetime import datetime
import base64
import re
import tempfile

# Define the Flask app ONLY ONCE
if getattr(sys, 'frozen', False):
    # If the application is frozen (PyInstaller)
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    # Regular development environment
    app = Flask(__name__)

DATA_FOLDER = 'notes_data'
IMAGE_FOLDER = os.path.join('static', 'images')

# Ensure data and image folders exist
for folder in [DATA_FOLDER, IMAGE_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)


@app.route('/')
def index():
    return render_template('index.html', notes=get_all_notes())

@app.route('/note/<note_id>')
def view_note(note_id):
    try:
        with open(os.path.join(DATA_FOLDER, f"{note_id}.json"), 'r') as f:
            note = json.load(f)
        return render_template('note.html', note=note)
    except FileNotFoundError:
        return redirect(url_for('index'))

@app.route('/new_note')
def new_note():
    note_id = str(uuid.uuid4())
    note = {
        'id': note_id,
        'title': 'Untitled Note',
        'content': '',
        'created': datetime.now().isoformat(),
        'last_modified': datetime.now().isoformat()
    }
    return render_template('note.html', note=note)

@app.route('/save', methods=['POST'])
def save_note():
    data = request.get_json()
    note_id = data.get('id', str(uuid.uuid4()))
    content = data.get('content', '')
    title = data.get('title', 'Untitled')
    
    # Extract and save any embedded images
    content = process_embedded_images(content, note_id)
    
    note_data = {
        'id': note_id,
        'title': title,
        'content': content,
        'created': data.get('created', datetime.now().isoformat()),
        'last_modified': datetime.now().isoformat()
    }
    
    with open(os.path.join(DATA_FOLDER, f"{note_id}.json"), 'w') as f:
        json.dump(note_data, f)
    
    return jsonify({'success': True, 'id': note_id})

@app.route('/delete/<note_id>', methods=['POST'])
def delete_note(note_id):
    try:
        os.remove(os.path.join(DATA_FOLDER, f"{note_id}.json"))
        # Could also delete associated images here
        return jsonify({'success': True})
    except FileNotFoundError:
        return jsonify({'error': 'Note not found'}), 404

def process_embedded_images(content, note_id):
    # Look for base64 encoded images
    img_pattern = re.compile(r'data:image/(.*?);base64,(.*?)"')
    matches = img_pattern.findall(content)
    
    for i, match in enumerate(matches):
        img_type, img_data = match
        img_filename = f"{note_id}_{i}.{img_type}"
        img_path = os.path.join(IMAGE_FOLDER, img_filename)
        
        # Save the image
        with open(img_path, "wb") as img_file:
            img_file.write(base64.b64decode(img_data))
        
        # Replace the base64 data with a reference to the saved image
        img_url = f"/static/images/{img_filename}"
        content = content.replace(f"data:image/{img_type};base64,{img_data}", img_url)
    
    return content

def get_all_notes():
    notes = []
    for filename in os.listdir(DATA_FOLDER):
        if filename.endswith('.json'):
            with open(os.path.join(DATA_FOLDER, filename), 'r') as f:
                notes.append(json.load(f))
    return sorted(notes, key=lambda x: x['last_modified'], reverse=True)


import webbrowser
from threading import Timer

def open_browser():
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == '__main__':
    # Open the browser after a short delay
    Timer(1, open_browser).start()
    app.run(debug=False, use_reloader=False)