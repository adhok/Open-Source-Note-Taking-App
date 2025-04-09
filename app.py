from flask import (
    Flask, render_template, request, jsonify, redirect, url_for,
    send_from_directory, abort # Added send_from_directory and abort
)
import os
import sys
import json
import uuid
from datetime import datetime
import base64
import re
from pathlib import Path
import webbrowser
from threading import Timer

# Configure Flask for bundled resources when frozen
if getattr(sys, 'frozen', False):
    # When bundled by PyInstaller, load templates and static files from sys._MEIPASS
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    # Development mode, Flask finds templates/static relative to app.py
    app = Flask(__name__)

# Determine a base path for writable data
if getattr(sys, 'frozen', False):
    # Use the directory of the executable when frozen
    base_writable_path = os.path.dirname(sys.executable)
else:
    # Otherwise, use the current directory (development mode)
    base_writable_path = os.path.abspath(".")

# Define writable folders relative to the base_writable_path
DATA_FOLDER = os.path.join(base_writable_path, 'notes_data')
# Use a distinct name for user uploads, outside the potentially bundled 'static' folder
USER_IMAGE_FOLDER = os.path.join(base_writable_path, 'user_images') # <-- Changed name

# Ensure data and user image folders exist
# Use the new folder name here
for folder in [DATA_FOLDER, USER_IMAGE_FOLDER]: # <-- Use new name
    if not os.path.exists(folder):
        try:
            os.makedirs(folder)
        except OSError as e:
            print(f"Error creating directory {folder}: {e}")
            # Handle the error appropriately, maybe exit or log critical error
            sys.exit(f"Could not create necessary directory: {folder}")


# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html', notes=get_all_notes())

@app.route('/note/<note_id>')
def view_note(note_id):
    try:
        # Sanitize note_id? Basic check here:
        if not re.match(r'^[a-zA-Z0-9-]+$', note_id):
             print(f"Invalid note_id format attempt: {note_id}")
             return redirect(url_for('index')) # Or show an error page

        note_file = os.path.join(DATA_FOLDER, f"{note_id}.json")
        # Security check: ensure the path is within the DATA_FOLDER
        if not os.path.abspath(note_file).startswith(os.path.abspath(DATA_FOLDER)):
            print(f"Potential path traversal attempt: {note_id}")
            return redirect(url_for('index')) # Or 403 Forbidden

        with open(note_file, 'r', encoding='utf-8') as f: # Specify encoding
            note = json.load(f)
        return render_template('note.html', note=note)
    except FileNotFoundError:
        print(f"Note not found: {note_id}")
        return redirect(url_for('index'))
    except json.JSONDecodeError:
        print(f"Error decoding JSON for note: {note_id}")
        # Maybe delete the corrupted file or show an error
        return "Error loading note data.", 500
    except Exception as e:
        print(f"Error viewing note {note_id}: {e}")
        return "An unexpected error occurred.", 500


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
    # Pass note_id separately if note.html needs it explicitly for new notes
    return render_template('note.html', note=note, is_new=True)


@app.route('/save', methods=['POST'])
def save_note():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data received'}), 400

        note_id = data.get('id')
        # Validate or generate note_id
        if not note_id or not isinstance(note_id, str) or not re.match(r'^[a-zA-Z0-9-]+$', note_id):
             note_id = str(uuid.uuid4()) # Generate a new one if invalid/missing

        content = data.get('content', '')
        title = data.get('title', 'Untitled')
        # Basic sanitization/validation
        title = title[:255] # Limit title length

        # Process and save any embedded images, replacing base64 with URLs
        content = process_embedded_images(content, note_id)

        note_data = {
            'id': note_id,
            'title': title,
            'content': content, # Content now has URLs instead of base64
            'created': data.get('created', datetime.now().isoformat()), # Keep original creation date if exists
            'last_modified': datetime.now().isoformat()
        }

        note_file = os.path.join(DATA_FOLDER, f"{note_id}.json")
        # Security check: ensure the path is within the DATA_FOLDER
        if not os.path.abspath(note_file).startswith(os.path.abspath(DATA_FOLDER)):
            print(f"Potential path traversal attempt during save: {note_id}")
            return jsonify({'error': 'Invalid note ID path'}), 400

        with open(note_file, 'w', encoding='utf-8') as f: # Specify encoding
            json.dump(note_data, f, indent=4) # Use indent for readability

        return jsonify({'success': True, 'id': note_id})

    except Exception as e:
        print(f"Error saving note: {e}")
        # Log the exception details for debugging
        # import traceback
        # traceback.print_exc()
        return jsonify({'error': 'Failed to save note'}), 500


@app.route('/delete/<note_id>', methods=['POST'])
def delete_note(note_id):
    try:
        # Sanitize note_id
        if not re.match(r'^[a-zA-Z0-9-]+$', note_id):
             print(f"Invalid note_id format for delete: {note_id}")
             return jsonify({'error': 'Invalid note ID format'}), 400

        note_file = os.path.join(DATA_FOLDER, f"{note_id}.json")

        # Security check
        if not os.path.abspath(note_file).startswith(os.path.abspath(DATA_FOLDER)):
            print(f"Potential path traversal attempt during delete: {note_id}")
            return jsonify({'error': 'Invalid note ID path'}), 400

        os.remove(note_file)

        # --- Optional: Delete associated images ---
        # Be careful with this - ensure filenames are strictly controlled
        try:
            for filename in os.listdir(USER_IMAGE_FOLDER):
                # Construct filename pattern based on how images are named in process_embedded_images
                # Example: if named note_id_index.ext
                if filename.startswith(f"{note_id}_") and \
                   os.path.splitext(filename)[1].lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp']:
                     img_path = os.path.join(USER_IMAGE_FOLDER, filename)
                     # Final check for safety
                     if os.path.abspath(img_path).startswith(os.path.abspath(USER_IMAGE_FOLDER)):
                        os.remove(img_path)
                        print(f"Deleted associated image: {filename}")
        except OSError as e:
             print(f"Error deleting associated images for note {note_id}: {e}")
        # --- End optional image deletion ---

        return jsonify({'success': True})
    except FileNotFoundError:
        print(f"Note not found for deletion: {note_id}")
        return jsonify({'error': 'Note not found'}), 404
    except Exception as e:
        print(f"Error deleting note {note_id}: {e}")
        return jsonify({'error': 'Failed to delete note'}), 500


# --- Route to Serve User Uploaded Images ---
@app.route('/user_images/<path:filename>') # Route matches the url_for name
def serve_user_image(filename):
    """Serves images uploaded by the user."""
    # Security: Basic check for filename validity (avoids weird characters, path separators)
    # You might want stricter checks depending on allowed image types/names
    if ".." in filename or filename.startswith("/"):
         print(f"Invalid image filename request: {filename}")
         abort(400) # Bad request

    safe_path = os.path.abspath(os.path.join(USER_IMAGE_FOLDER, filename))
    # Double-check it's still within the intended folder afterabspath resolution
    if not safe_path.startswith(os.path.abspath(USER_IMAGE_FOLDER)):
        print(f"Attempt to access file outside USER_IMAGE_FOLDER: {filename}")
        abort(403) # Forbidden

    try:
        # send_from_directory handles range requests, ETags, etc.
        # and provides some protection against directory traversal upwards.
        print(f"Serving image: {filename}") # Debug log
        return send_from_directory(USER_IMAGE_FOLDER, filename)
    except FileNotFoundError:
        print(f"Image file not found: {filename}")
        abort(404) # Standard way to return 404
    except Exception as e:
        print(f"Error serving image {filename}: {e}")
        abort(500)

# --- Helper Functions ---

def process_embedded_images(content, note_id):
    """
    Finds base64 encoded images, saves them to USER_IMAGE_FOLDER,
    and replaces the base64 string with a URL pointing to the saved file.
    """
    if not content: # Handle empty content
        return ''

    # Regex to find data URLs like data:image/png;base64,ABC...XYZ" (including the quote)
    img_pattern = re.compile(r'data:image/(?P<type>.*?);base64,(?P<data>.*?)"')
    replacements = {} # Store replacements: { full_base64_str_with_quote : new_url_with_quote }

    current_pos = 0
    while True:
        match = img_pattern.search(content, current_pos)
        if not match:
            break # No more matches found

        full_match_str_with_quote = match.group(0) # e.g., data:image/png;base64,ABC...XYZ"
        img_type = match.group('type')
        img_data = match.group('data')
        match_start_index = match.start() # Use start position for a somewhat unique identifier

        # Basic validation of image type (allow common web formats)
        allowed_types = ['png', 'jpeg', 'jpg', 'gif', 'webp', 'bmp']
        if img_type.lower() not in allowed_types:
            print(f"Skipping unsupported image type: {img_type}")
            current_pos = match.end() # Move past this match
            continue

        # Create a unique filename using note_id and match position
        img_filename = f"{note_id}_{match_start_index}.{img_type}"

        # Use the dedicated user image folder
        img_path = os.path.join(USER_IMAGE_FOLDER, img_filename)

        # Security check: Ensure the path is within the USER_IMAGE_FOLDER
        if not os.path.abspath(img_path).startswith(os.path.abspath(USER_IMAGE_FOLDER)):
             print(f"Potential path traversal attempt during image save: {img_filename}")
             current_pos = match.end() # Skip this match
             continue

        try:
            # Decode and save the image file
            img_bytes = base64.b64decode(img_data)
            # Optional: Add checks for file size or basic magic number validation if needed
            with open(img_path, "wb") as img_file:
                img_file.write(img_bytes)

            # Generate URL using url_for pointing to the 'serve_user_image' route
            img_url = url_for('serve_user_image', filename=img_filename)

            # Store the replacement pair (original string -> new url string)
            # Add the quote back to the replacement URL string
            replacements[full_match_str_with_quote] = img_url + '"'
            print(f"Processed image, saving as {img_filename}, replacing with {img_url}") # Debug log

        except (base64.binascii.Error) as e:
             print(f"Error decoding base64 data at pos {match_start_index}: {e}")
             # Log error, potentially skip replacement or use a placeholder
        except (OSError, FileNotFoundError) as e:
             print(f"Error saving image file {img_filename}: {e}")
             # Log error, potentially skip replacement or use a placeholder
        except Exception as e:
             print(f"Unexpected error processing image at pos {match_start_index}: {e}")

        # Move search position past the current match to find the next one
        current_pos = match.end()

    # Perform replacements after finding all matches
    # Replace longer strings first to avoid issues where a shorter match might be part of a longer one
    if replacements:
        print(f"Performing {len(replacements)} image replacements...") # Debug log
        # Create a single regex for replacement for efficiency if many images
        # This requires careful escaping if keys contain regex special chars, simpler to loop for now
        # sorted_keys = sorted(replacements.keys(), key=len, reverse=True)
        # for data_url_str in sorted_keys:
        #     content = content.replace(data_url_str, replacements[data_url_str])

        # Simpler loop (might be slow for huge documents with many images)
        for data_url_str, file_url_str in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
             content = content.replace(data_url_str, file_url_str)

    return content


def get_all_notes():
    """Loads summary data for all notes from the DATA_FOLDER."""
    notes = []
    if not os.path.exists(DATA_FOLDER):
        print(f"Data folder {DATA_FOLDER} does not exist.")
        return [] # Return empty list if folder is missing

    try:
        for filename in os.listdir(DATA_FOLDER):
            if filename.endswith('.json'):
                filepath = os.path.join(DATA_FOLDER, filename)
                # Security check: Ensure we're not reading outside DATA_FOLDER
                if not os.path.abspath(filepath).startswith(os.path.abspath(DATA_FOLDER)):
                    print(f"Skipping file outside data folder: {filename}")
                    continue

                try:
                    with open(filepath, 'r', encoding='utf-8') as f: # Specify encoding
                        note_data = json.load(f)
                        # Only append necessary info for index list if performance is key
                        notes.append({
                            'id': note_data.get('id'),
                            'title': note_data.get('title', 'Untitled'),
                            'last_modified': note_data.get('last_modified')
                        })
                except json.JSONDecodeError:
                    print(f"Warning: Skipping corrupted JSON file: {filename}")
                except Exception as e:
                    print(f"Error reading note file {filename}: {e}")

        # Sort notes by last modified date, newest first
        return sorted(notes, key=lambda x: x.get('last_modified', ''), reverse=True)
    except OSError as e:
         print(f"Error listing files in {DATA_FOLDER}: {e}")
         return [] # Return empty on directory read error


def open_browser():
    """Opens the default web browser to the app's URL."""
    try:
        webbrowser.open("http://127.0.0.1:5000")
    except Exception as e:
        print(f"Could not open web browser: {e}")

# --- Main Execution ---

if __name__ == '__main__':
    # Optional: Delay opening browser slightly to allow server to start
    Timer(1.5, open_browser).start()

    # Run the Flask app
    # debug=True is helpful for development (auto-reloads), but should be False for deployment/frozen app.
    # use_reloader=False is often needed for frozen apps to prevent issues.
    # Consider specifying host='0.0.0.0' if you need to access it from other devices on your network.
    is_debug_mode = not getattr(sys, 'frozen', False) # Debug only if not frozen
    app.run(host='127.0.0.1', port=5000, debug=is_debug_mode, use_reloader=is_debug_mode)

    # Alternative for packaging with webview (like pywebview) instead of browser:
    # try:
    #     import webview
    #     window = webview.create_window("Note App", app, width=1400, height=850)
    #     webview.start(debug=is_debug_mode) # Pass Flask app object directly
    # except ImportError:
    #     print("webview library not found, running in browser mode.")
    #     app.run(host='127.0.0.1', port=5000, debug=is_debug_mode, use_reloader=is_debug_mode)