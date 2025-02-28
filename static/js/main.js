// main.js - Client-side functionality for the notes application

document.addEventListener('DOMContentLoaded', function() {
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

// Function to format dates (can be used throughout the application)
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}