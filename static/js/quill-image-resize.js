// static/js/quill-image-resize-simple.js
class SimpleImageResize {
  constructor(quill) {
    this.quill = quill;
    this.quill.root.addEventListener('click', this.handleClick.bind(this));
    this.selectedImage = null;
    this.initResizePanel();
  }

  initResizePanel() {
    // Create a resize panel that appears when an image is selected
    this.resizePanel = document.createElement('div');
    this.resizePanel.className = 'image-resize-panel';
    this.resizePanel.style.display = 'none';
    this.resizePanel.style.position = 'absolute';
    this.resizePanel.style.padding = '5px';
    this.resizePanel.style.backgroundColor = 'white';
    this.resizePanel.style.border = '1px solid #ccc';
    this.resizePanel.style.borderRadius = '3px';
    this.resizePanel.style.boxShadow = '0 1px 5px rgba(0,0,0,0.1)';
    this.resizePanel.style.zIndex = '100';

    // Width input
    const widthLabel = document.createElement('label');
    widthLabel.innerText = 'Width: ';
    this.widthInput = document.createElement('input');
    this.widthInput.type = 'number';
    this.widthInput.style.width = '60px';
    this.widthInput.min = '1';

    // Height input
    const heightLabel = document.createElement('label');
    heightLabel.innerText = ' Height: ';
    this.heightInput = document.createElement('input');
    this.heightInput.type = 'number';
    this.heightInput.style.width = '60px';
    this.heightInput.min = '1';

    // Apply button
    this.applyButton = document.createElement('button');
    this.applyButton.innerText = 'Apply';
    this.applyButton.style.marginLeft = '5px';
    this.applyButton.style.backgroundColor = '#2563eb';
    this.applyButton.style.color = 'white';
    this.applyButton.style.border = 'none';
    this.applyButton.style.borderRadius = '3px';
    this.applyButton.style.padding = '2px 8px';
    this.applyButton.style.cursor = 'pointer';

    // Add all elements to the panel
    this.resizePanel.appendChild(widthLabel);
    this.resizePanel.appendChild(this.widthInput);
    this.resizePanel.appendChild(heightLabel);
    this.resizePanel.appendChild(this.heightInput);
    this.resizePanel.appendChild(this.applyButton);

    // Add the panel to the document body
    document.body.appendChild(this.resizePanel);

    // Add event listener for Apply button
    this.applyButton.addEventListener('click', this.resizeImage.bind(this));
    
    // Close panel when clicking outside
    document.addEventListener('click', (e) => {
      if (!this.resizePanel.contains(e.target) && 
          e.target !== this.selectedImage &&
          this.resizePanel.style.display === 'block') {
        this.hidePanel();
      }
    });
  }

  handleClick(event) {
    if (event.target.tagName === 'IMG') {
      // If an image is clicked, select it and show the resize panel
      this.selectedImage = event.target;
      
      // If this is a newly added image with no explicit dimensions set,
      // set the default width to 750px and maintain aspect ratio
      if (!this.selectedImage.getAttribute('width') && !this.selectedImage.style.width) {
        const aspectRatio = this.selectedImage.naturalHeight / this.selectedImage.naturalWidth;
        this.selectedImage.width = 750;
        this.selectedImage.height = Math.round(750 * aspectRatio);
      }
      
      this.showPanel();
      event.stopPropagation();
    }
  }

  showPanel() {
    if (!this.selectedImage) return;
    
    // Get image dimensions
    const width = this.selectedImage.width || this.selectedImage.naturalWidth;
    const height = this.selectedImage.height || this.selectedImage.naturalHeight;
    
    // Set values in inputs
    this.widthInput.value = width;
    this.heightInput.value = height;
    
    // Position the panel below the image
    const rect = this.selectedImage.getBoundingClientRect();
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    
    this.resizePanel.style.top = (rect.bottom + scrollTop + 5) + 'px';
    this.resizePanel.style.left = rect.left + 'px';
    this.resizePanel.style.display = 'block';
    
    // Add a highlight border to the selected image
    this.selectedImage.style.outline = '2px solid #2563eb';
  }

  hidePanel() {
    if (this.selectedImage) {
      this.selectedImage.style.outline = '';
      this.selectedImage = null;
    }
    this.resizePanel.style.display = 'none';
  }

  resizeImage() {
    if (!this.selectedImage) return;
    
    const newWidth = parseInt(this.widthInput.value) || this.selectedImage.width;
    const newHeight = parseInt(this.heightInput.value) || this.selectedImage.height;
    
    // Apply new dimensions to the image
    this.selectedImage.width = newWidth;
    this.selectedImage.height = newHeight;
    
    // Hide the panel after applying
    this.hidePanel();
  }
}

// Register module with Quill if available
if (typeof Quill !== 'undefined') {
  Quill.register('modules/simpleImageResize', SimpleImageResize);
}