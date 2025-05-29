/**
 * Resume Match AI - Main JavaScript File
 * Provides interactive functionality for the web interface
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Resume Match AI initialized');
    
    // Initialize all components
    initializeFormValidation();
    initializeFileUpload();
    initializeTooltips();
    initializeAlerts();
    initializeScoreAnimations();
    initializeSearchAndFilter();
    initializeProgressTracking();
    initializeKeyboardNavigation();
});

/**
 * Form validation and enhancement
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        // Add Bootstrap validation classes
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
        
        // Real-time validation feedback
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    validateField(this);
                }
            });
        });
    });
}

/**
 * Validate individual form field
 */
function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let message = '';
    
    // Required field validation
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        message = 'This field is required.';
    }
    
    // Email validation
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            message = 'Please enter a valid email address.';
        }
    }
    
    // Job description validation
    if (field.name === 'job_description' && value && value.length < 50) {
        isValid = false;
        message = 'Job description should be at least 50 characters long.';
    }
    
    // File validation
    if (field.type === 'file' && field.files.length > 0) {
        const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
        const maxSize = 16 * 1024 * 1024; // 16MB
        
        for (let file of field.files) {
            if (!allowedTypes.includes(file.type) && !file.name.match(/\.(pdf|docx|txt)$/i)) {
                isValid = false;
                message = 'Only PDF, DOCX, and TXT files are allowed.';
                break;
            }
            
            if (file.size > maxSize) {
                isValid = false;
                message = 'File size must be less than 16MB.';
                break;
            }
        }
    }
    
    // Update field appearance
    field.classList.remove('is-valid', 'is-invalid');
    field.classList.add(isValid ? 'is-valid' : 'is-invalid');
    
    // Update feedback message
    let feedback = field.parentNode.querySelector('.invalid-feedback');
    if (!feedback) {
        feedback = document.createElement('div');
        feedback.classList.add('invalid-feedback');
        field.parentNode.appendChild(feedback);
    }
    feedback.textContent = message;
    
    return isValid;
}

/**
 * Enhanced file upload functionality
 */
function initializeFileUpload() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        // Drag and drop functionality
        const container = input.closest('.mb-3') || input.parentNode;
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            container.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        ['dragenter', 'dragover'].forEach(eventName => {
            container.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            container.addEventListener(eventName, unhighlight, false);
        });
        
        function highlight(e) {
            container.classList.add('border-primary', 'bg-light');
        }
        
        function unhighlight(e) {
            container.classList.remove('border-primary', 'bg-light');
        }
        
        container.addEventListener('drop', handleDrop, false);
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            input.files = files;
            
            // Trigger change event
            const event = new Event('change', { bubbles: true });
            input.dispatchEvent(event);
        }
        
        // File preview enhancement
        input.addEventListener('change', function() {
            updateFilePreview(this);
            validateField(this);
        });
    });
}

/**
 * Update file preview display
 */
function updateFilePreview(input) {
    const files = input.files;
    let preview = document.getElementById('filePreview');
    let fileList = document.getElementById('fileList');
    
    if (!preview || !fileList) return;
    
    if (files.length > 0) {
        preview.style.display = 'block';
        fileList.innerHTML = '';
        
        let totalSize = 0;
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            totalSize += file.size;
            
            const fileItem = document.createElement('div');
            fileItem.className = 'badge bg-secondary me-2 mb-1 d-inline-flex align-items-center';
            
            const fileIcon = getFileIcon(file.name);
            const fileSize = formatFileSize(file.size);
            
            fileItem.innerHTML = `
                <i class="bi ${fileIcon} me-1"></i>
                <span class="me-2">${file.name}</span>
                <small>(${fileSize})</small>
                <button type="button" class="btn-close btn-close-white ms-2" 
                        onclick="removeFile(${i})" aria-label="Remove file"></button>
            `;
            
            fileList.appendChild(fileItem);
        }
        
        // Show total size
        const totalElement = document.createElement('div');
        totalElement.className = 'text-muted small mt-2';
        totalElement.textContent = `Total: ${files.length} file(s), ${formatFileSize(totalSize)}`;
        fileList.appendChild(totalElement);
        
    } else {
        preview.style.display = 'none';
    }
}

/**
 * Get appropriate icon for file type
 */
function getFileIcon(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    const icons = {
        'pdf': 'bi-file-earmark-pdf-fill',
        'docx': 'bi-file-earmark-word-fill',
        'doc': 'bi-file-earmark-word-fill',
        'txt': 'bi-file-earmark-text-fill'
    };
    return icons[ext] || 'bi-file-earmark';
}

/**
 * Format file size for display
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Enhanced alert functionality
 */
function initializeAlerts() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Add slide-in animation to new alerts
    alerts.forEach(alert => {
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-20px)';
        
        setTimeout(() => {
            alert.style.transition = 'all 0.3s ease-in-out';
            alert.style.opacity = '1';
            alert.style.transform = 'translateY(0)';
        }, 100);
    });
}

/**
 * Show dynamic alert
 */
function showAlert(message, type = 'info', autoDismiss = true) {
    const alertContainer = document.querySelector('.container') || document.body;
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.insertBefore(alertDiv, alertContainer.firstChild);
    
    if (autoDismiss) {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        }, 5000);
    }
}

/**
 * Score animations and visual enhancements
 */
function initializeScoreAnimations() {
    const scoreElements = document.querySelectorAll('[data-score]');
    
    scoreElements.forEach(element => {
        const score = parseFloat(element.dataset.score);
        animateScore(element, score);
    });
    
    // Animate progress bars
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(bar => {
        const width = bar.style.width || bar.getAttribute('aria-valuenow') + '%';
        bar.style.width = '0%';
        
        setTimeout(() => {
            bar.style.transition = 'width 1s ease-in-out';
            bar.style.width = width;
        }, 200);
    });
}

/**
 * Animate score counter
 */
function animateScore(element, targetScore) {
    const duration = 1000; // 1 second
    const startTime = performance.now();
    const startScore = 0;
    
    function updateScore(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function
        const easeOut = 1 - Math.pow(1 - progress, 3);
        const currentScore = startScore + (targetScore - startScore) * easeOut;
        
        element.textContent = Math.round(currentScore) + '%';
        
        if (progress < 1) {
            requestAnimationFrame(updateScore);
        }
    }
    
    requestAnimationFrame(updateScore);
}

/**
 * Search and filter functionality
 */
function initializeSearchAndFilter() {
    const searchInputs = document.querySelectorAll('[data-search]');
    const filterSelects = document.querySelectorAll('[data-filter]');
    
    searchInputs.forEach(input => {
        input.addEventListener('input', debounce(function() {
            performSearch(this);
        }, 300));
    });
    
    filterSelects.forEach(select => {
        select.addEventListener('change', function() {
            performFilter(this);
        });
    });
}

/**
 * Perform search functionality
 */
function performSearch(input) {
    const searchTerm = input.value.toLowerCase();
    const targetSelector = input.dataset.search;
    const items = document.querySelectorAll(targetSelector);
    
    items.forEach(item => {
        const text = item.textContent.toLowerCase();
        const shouldShow = text.includes(searchTerm);
        
        item.style.display = shouldShow ? '' : 'none';
    });
}

/**
 * Perform filter functionality
 */
function performFilter(select) {
    const filterValue = select.value;
    const targetSelector = select.dataset.filter;
    const items = document.querySelectorAll(targetSelector);
    
    items.forEach(item => {
        const itemValue = item.dataset.filterValue || '';
        const shouldShow = !filterValue || itemValue === filterValue;
        
        item.style.display = shouldShow ? '' : 'none';
    });
}

/**
 * Progress tracking for long operations
 */
function initializeProgressTracking() {
    const forms = document.querySelectorAll('form[data-progress]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            showProgressIndicator();
        });
    });
}

/**
 * Show progress indicator
 */
function showProgressIndicator() {
    const progressHtml = `
        <div id="globalProgress" class="position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center" 
             style="background: rgba(0,0,0,0.7); z-index: 9999;">
            <div class="text-center text-white">
                <div class="spinner-border mb-3" role="status">
                    <span class="visually-hidden">Processing...</span>
                </div>
                <div>Processing your request...</div>
                <small class="text-muted">This may take a few moments</small>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', progressHtml);
}

/**
 * Hide progress indicator
 */
function hideProgressIndicator() {
    const progress = document.getElementById('globalProgress');
    if (progress) {
        progress.remove();
    }
}

/**
 * Keyboard navigation enhancements
 */
function initializeKeyboardNavigation() {
    // Global keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Enter to submit forms
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const activeForm = document.activeElement.closest('form');
            if (activeForm) {
                e.preventDefault();
                activeForm.requestSubmit();
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                const modal = bootstrap.Modal.getInstance(openModal);
                if (modal) modal.hide();
            }
        }
    });
    
    // Enhance focus management
    const focusableElements = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';
    const modals = document.querySelectorAll('.modal');
    
    modals.forEach(modal => {
        modal.addEventListener('shown.bs.modal', function() {
            const firstFocusable = modal.querySelector(focusableElements);
            if (firstFocusable) firstFocusable.focus();
        });
    });
}

/**
 * Utility function: Debounce
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Utility function: Throttle
 */
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        return navigator.clipboard.writeText(text);
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        return new Promise((resolve, reject) => {
            document.execCommand('copy') ? resolve() : reject();
            textArea.remove();
        });
    }
}

/**
 * Format numbers for display
 */
function formatNumber(num, decimals = 1) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(decimals) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(decimals) + 'K';
    } else {
        return num.toString();
    }
}

/**
 * Smooth scroll to element
 */
function scrollToElement(elementId, offset = 0) {
    const element = document.getElementById(elementId);
    if (element) {
        const elementPosition = element.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - offset;
        
        window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
        });
    }
}

/**
 * Local storage helpers
 */
const Storage = {
    set: function(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.warn('LocalStorage not available:', e);
        }
    },
    
    get: function(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            console.warn('LocalStorage not available:', e);
            return defaultValue;
        }
    },
    
    remove: function(key) {
        try {
            localStorage.removeItem(key);
        } catch (e) {
            console.warn('LocalStorage not available:', e);
        }
    }
};

/**
 * Initialize auto-save for forms
 */
function initializeAutoSave() {
    const autoSaveForms = document.querySelectorAll('[data-autosave]');
    
    autoSaveForms.forEach(form => {
        const formId = form.id || 'form_' + Date.now();
        
        // Load saved data
        const savedData = Storage.get('autosave_' + formId);
        if (savedData) {
            Object.keys(savedData).forEach(key => {
                const field = form.querySelector(`[name="${key}"]`);
                if (field && field.type !== 'file') {
                    field.value = savedData[key];
                }
            });
        }
        
        // Save data on input
        form.addEventListener('input', debounce(function(e) {
            if (e.target.type !== 'file') {
                const formData = new FormData(form);
                const data = {};
                for (let [key, value] of formData.entries()) {
                    data[key] = value;
                }
                Storage.set('autosave_' + formId, data);
            }
        }, 1000));
        
        // Clear saved data on successful submit
        form.addEventListener('submit', function() {
            Storage.remove('autosave_' + formId);
        });
    });
}

// Global error handler
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    hideProgressIndicator();
});

// Global unhandled promise rejection handler
window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    hideProgressIndicator();
});

// Export functions for global use
window.ResumeMatchAI = {
    showAlert,
    copyToClipboard,
    formatNumber,
    scrollToElement,
    Storage,
    showProgressIndicator,
    hideProgressIndicator
};
