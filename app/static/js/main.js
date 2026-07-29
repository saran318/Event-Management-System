/**
 * EventVerse - Primary JavaScript
 * 
 * Sections:
 * 1. DOM Ready Wrapper
 * 2. Flash Alert Auto-Dismiss
 * 3. Delete Confirmation
 * 4. Prevent Double Submission & Loading Indicators
 * 5. Form Validation & Date Limits
 * 6. Flatpickr Calendar & Time Picker Initialization
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // ==========================================================================
    // 2. Flash Alert Auto-Dismiss
    // ==========================================================================
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        // Only auto-dismiss success and info alerts, keep errors visible until dismissed
        if (alert.classList.contains('alert-success') || alert.classList.contains('alert-info')) {
            setTimeout(function() {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        }
    });

    // ==========================================================================
    // 3. Delete Confirmation
    // ==========================================================================
    const deleteForms = document.querySelectorAll('.form-delete');
    deleteForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!confirm('Are you sure you want to proceed? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // ==========================================================================
    // 4. Prevent Double Submission & Loading Indicators
    // ==========================================================================
    const loadingForms = document.querySelectorAll('.form-loading');
    loadingForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            // If the form is already submitting, prevent duplicate
            if (form.classList.contains('is-submitting')) {
                e.preventDefault();
                return;
            }
            
            // Check HTML5 validation first
            if (!form.checkValidity()) {
                return; // Let browser handle the validation UI
            }

            form.classList.add('is-submitting');
            
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                // Safely indicate loading state without breaking form submission
                // Modifying innerHTML or 'disabled' attribute during submit can cause the browser to abort the request
                submitBtn.style.opacity = '0.7';
                submitBtn.style.pointerEvents = 'none';
                
                // Change text if it has a span, or just append a small indicator
                if (!submitBtn.dataset.originalText) {
                    submitBtn.dataset.originalText = submitBtn.innerHTML;
                }
            }
        });
    });

    // ==========================================================================
    // 5. Form Validation & Date Limits
    // ==========================================================================
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // ==========================================================================
    // ==========================================================================
    // 6. Flatpickr Calendar & Time Picker Initialization with Current Date/Time Auto-Recognition
    // ==========================================================================
    function getTodayString() {
        const d = new Date();
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    function getNowTimeString() {
        const d = new Date();
        const hours = String(d.getHours()).padStart(2, '0');
        const minutes = String(d.getMinutes()).padStart(2, '0');
        return `${hours}:${minutes}`;
    }

    // Quick fill buttons
    const btnUseToday = document.getElementById('btn_use_today');
    const dateInputEl = document.getElementById('event_date');
    // Note: #event_time uses a custom modal picker (in create_event.html) — no flatpickr here

    if (btnUseToday && dateInputEl) {
        btnUseToday.addEventListener('click', function() {
            dateInputEl.value = getTodayString();
            if (dateInputEl._flatpickr) {
                dateInputEl._flatpickr.setDate(getTodayString());
            }
        });
    }

    // Auto-populate current date on focus if empty
    if (dateInputEl) {
        dateInputEl.addEventListener('focus', function() {
            if (!dateInputEl.value) {
                dateInputEl.value = getTodayString();
            }
        });
    }

    if (typeof flatpickr !== 'undefined') {
        // Date Picker with visual calendar popup
        if (dateInputEl) {
            flatpickr(dateInputEl, {
                dateFormat: "Y-m-d",
                minDate: "today",
                disableMobile: true,
                animate: true,
                monthSelectorType: "dropdown",
                onOpen: function(selectedDates, dateStr, instance) {
                    if (!instance.element.value) {
                        instance.setDate(getTodayString());
                    }
                }
            });
        }

        // Time picker is handled by the custom modal in create_event.html — flatpickr not used for time
    } else {
        // Fallback: set min date natively if flatpickr is unavailable
        if (dateInputEl) {
            dateInputEl.setAttribute('min', getTodayString());
        }
    }

});

