// main.js - Client-side functionality for the notes application

// Function to toggle dark mode
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    
    // Save preference to localStorage
    if (document.body.classList.contains('dark-mode')) {
        localStorage.setItem('theme', 'dark');
    } else {
        localStorage.setItem('theme', 'light');
    }
    
    // Update SVG icons in toggle buttons
    updateThemeIcons();
    
    // Debug statement to confirm toggle was executed
    console.log('Dark mode toggled. Current state:', document.body.classList.contains('dark-mode'));
}

// Function to update theme toggle icons
function updateThemeIcons() {
    const isDarkMode = document.body.classList.contains('dark-mode');
    const themeToggles = document.querySelectorAll('.theme-toggle');
    
    themeToggles.forEach(toggle => {
        if (isDarkMode) {
            toggle.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="5"></circle>
                    <line x1="12" y1="1" x2="12" y2="3"></line>
                    <line x1="12" y1="21" x2="12" y2="23"></line>
                    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                    <line x1="1" y1="12" x2="3" y2="12"></line>
                    <line x1="21" y1="12" x2="23" y2="12"></line>
                    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
                </svg>
            `;
        } else {
            toggle.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
                </svg>
            `;
        }
    });
}

// Function to format dates (can be used throughout the application)
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

// Initialize the application when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM content loaded, initializing app...');
    
    // Load theme preference from localStorage
    const currentTheme = localStorage.getItem('theme') || 'light';
    console.log('Current theme from localStorage:', currentTheme);
    
    if (currentTheme === 'dark') {
        document.body.classList.add('dark-mode');
        updateThemeIcons();
        console.log('Dark mode applied from saved preference');
    }

    // Explicitly find theme toggle buttons
    const themeToggles = document.querySelectorAll('.theme-toggle');
    console.log('Found', themeToggles.length, 'theme toggle buttons');
    
    // Add click event listeners to all theme toggle buttons
    themeToggles.forEach((toggle, index) => {
        toggle.addEventListener('click', function(event) {
            event.preventDefault();
            console.log('Theme toggle button clicked, index:', index);
            toggleDarkMode();
        });
    });

    // Handle note deletion
    document.querySelectorAll('.delete-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            if (confirm('Are you sure you want to delete this note?')) {
                const noteId = this.getAttribute('data-id');
                fetch(`/delete/${noteId}`, {
                    method: 'POST'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        this.closest('.note-item').remove();
                    }
                })
                .catch(error => {
                    console.error('Error deleting note:', error);
                });
            }
        });
    });

    // Handle note item click for navigation
    document.querySelectorAll('.note-item a').forEach(noteLink => {
        noteLink.addEventListener('click', function(e) {
            // Default navigation behavior is preserved
            // This is where you could add additional functionality like
            // highlighting the selected note
        });
    });

    // Add search functionality if search input exists
    const searchInput = document.getElementById('search-notes');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            document.querySelectorAll('.note-item').forEach(item => {
                const title = item.querySelector('h3').textContent.toLowerCase();
                if (title.includes(searchTerm)) {
                    item.style.display = 'flex';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    }
});

// Fallback initialization if DOMContentLoaded already fired
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    console.log('Document already loaded, initializing immediately');
    
    setTimeout(() => {
        // Apply theme
        const currentTheme = localStorage.getItem('theme') || 'light';
        if (currentTheme === 'dark' && !document.body.classList.contains('dark-mode')) {
            document.body.classList.add('dark-mode');
            updateThemeIcons();
        }
        
        // Set up theme toggles
        const themeToggles = document.querySelectorAll('.theme-toggle');
        themeToggles.forEach((toggle, index) => {
            // Remove any existing listeners first to prevent duplicates
            const newToggle = toggle.cloneNode(true);
            toggle.parentNode.replaceChild(newToggle, toggle);
            
            newToggle.addEventListener('click', function(event) {
                event.preventDefault();
                console.log('Theme toggle button clicked (fallback), index:', index);
                toggleDarkMode();
            });
        });
    }, 100);
}