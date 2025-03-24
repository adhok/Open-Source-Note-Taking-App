# Open-Source Note-Taking App
A lightweight, web-based note-taking app built with Python and Flask. Jot down your thoughts in a simple interface, styled with CSS and powered by JavaScript, all bundled into a single executable for easy use on Windows or macOS.

## Features
- Add notes via a clean web interface.
- Notes saved locally (currently to memory or file—specify if you've got persistence like `notes.txt`).
- Responsive design with custom CSS and JS.
- Runs as a standalone `.exe` on Windows or `.dmg` on macOS—no Python install needed!

## Installation
### Run from Source
1. Clone the repo:
   ```bash
   git clone https://github.com/adhok/Open-Source-Note-Taking-App.git
   cd Open-Source-Note-Taking-App
   ```
2. Install dependencies:
   ```bash
   pip install flask
   ```
3. Launch the app:
   ```bash
   python app.py
   ```
4. Open your browser to `http://127.0.0.1:5000`.

### Run the Executable
- **Windows**: Find `app.exe` in the `dist` folder after building (see below). Double-click to run—it'll start the server and (if configured) open your default browser.
- **macOS**: Use `NoteTakingApp.dmg` located in the same folder as `app.py`. Double-click to install and run.

## Usage
- Navigate to the web interface.
- Type a note in the input field (adjust based on your app).
- Click "Add" (or your button name) to save it.
- Delete or edit notes as needed (add if implemented).

## Building the Executable
To create your own executable:
1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. For Windows:
   ```bash
   pyinstaller --add-data "static;static" --add-data "templates;templates" --onefile app.py
   ```
   - Output: `app.exe` in the `dist` folder.
3. For macOS: The `NoteTakingApp.dmg` is pre-built and available alongside `app.py`.

## Future Plans
- Adding AI capabilities to summarize highlighted text(ambitious)
- Add categories or tags for organization.
- Dark mode toggle in the UI.

## Contributing
Love to have your help! Fork the repo, make changes, and submit a pull request. Check the [Issues](https://github.com/adhok/Open-Source-Note-Taking-App/issues) tab for bugs or feature ideas.

