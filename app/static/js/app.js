/**
 * MediTrack — Client-side JavaScript
 *
 * Handles interactive UI behaviour: mobile navigation toggle, flash-message
 * auto-dismiss, AJAX medication toggles on the dashboard, and subtle
 * scroll-based animations.
 */

document.addEventListener('DOMContentLoaded', () => {
    initNavToggle();
    initFlashMessages();
    initMedicationToggles();
    initConfirmDelete();
    initScrollAnimations();
    initNavbarScroll();
});


// ---------------------------------------------------------------------------
//  Mobile Navigation Toggle
// ---------------------------------------------------------------------------

function initNavToggle() {
    const toggle = document.getElementById('nav-toggle');
    const links = document.getElementById('nav-links');

    if (!toggle || !links) return;

    toggle.addEventListener('click', () => {
        links.classList.toggle('nav-open');
        const icon = toggle.querySelector('i');
        icon.classList.toggle('fa-bars');
        icon.classList.toggle('fa-times');
    });

    // Close menu when a link is clicked (mobile)
    links.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            links.classList.remove('nav-open');
            const icon = toggle.querySelector('i');
            icon.classList.add('fa-bars');
            icon.classList.remove('fa-times');
        });
    });
}


// ---------------------------------------------------------------------------
//  Flash Messages — auto-dismiss after 5 seconds
// ---------------------------------------------------------------------------

function initFlashMessages() {
    const flashMessages = document.querySelectorAll('.flash-message');

    flashMessages.forEach((message, index) => {
        // Stagger the entrance animation
        message.style.animationDelay = `${index * 0.1}s`;

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            message.style.animation = 'slideOut 0.4s ease forwards';
            setTimeout(() => message.remove(), 400);
        }, 5000 + index * 200);
    });
}


// ---------------------------------------------------------------------------
//  Dashboard: AJAX Medication Toggle
// ---------------------------------------------------------------------------

function initMedicationToggles() {
    const checkboxes = document.querySelectorAll('.med-check-input');

    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', async (event) => {
            const medId = event.target.dataset.medId;
            const card = document.getElementById(`med-card-${medId}`);
            const csrfMeta = document.querySelector('meta[name="csrf-token"]');
            const csrfToken = csrfMeta ? csrfMeta.getAttribute('content') : '';

            try {
                const response = await fetch(`/medications/${medId}/toggle`, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': csrfToken,
                    },
                });

                if (!response.ok) throw new Error('Toggle failed');

                const data = await response.json();

                // Update the card's visual state
                if (data.taken) {
                    card.classList.add('med-taken');
                    updateBadge(card, true);
                } else {
                    card.classList.remove('med-taken');
                    updateBadge(card, false);
                }

                // Update dashboard stats
                updateDashboardStats(data);

                // Trigger a celebratory pulse animation
                card.classList.add('med-pulse');
                setTimeout(() => card.classList.remove('med-pulse'), 600);

            } catch (error) {
                console.error('Error toggling medication:', error);
                // Revert the checkbox on failure
                event.target.checked = !event.target.checked;
            }
        });
    });
}


// ---------------------------------------------------------------------------
//  Confirm Delete (modal) — intercept forms with class `confirm-delete`
// ---------------------------------------------------------------------------
function initConfirmDelete() {
    const modal = document.getElementById('confirm-modal');
    if (!modal) return;

    const messageEl = document.getElementById('confirm-modal-message');
    const btnCancel = document.getElementById('confirm-modal-cancel');
    const btnConfirm = document.getElementById('confirm-modal-confirm');

    let pendingForm = null;

    function showModal(text) {
        if (messageEl) messageEl.textContent = text || 'Are you sure?';
        modal.style.display = 'block';
        modal.setAttribute('aria-hidden', 'false');
    }

    function hideModal() {
        modal.style.display = 'none';
        modal.setAttribute('aria-hidden', 'true');
        pendingForm = null;
    }

    // Attach to forms with the confirm-delete class
    document.querySelectorAll('form.confirm-delete').forEach(form => {
        form.addEventListener('submit', (ev) => {
            ev.preventDefault();
            pendingForm = form;
            const medName = form.dataset.medName || '';
            const text = medName ? `Delete "${medName}"? This action cannot be undone.` : 'Delete this item? This action cannot be undone.';
            showModal(text);
        });
    });

    btnCancel && btnCancel.addEventListener('click', (e) => {
        e.preventDefault();
        hideModal();
    });

    btnConfirm && btnConfirm.addEventListener('click', (e) => {
        e.preventDefault();
        if (pendingForm) pendingForm.submit();
        hideModal();
    });

    // Close modal on backdrop click
    modal.addEventListener('click', (e) => {
        if (e.target.classList.contains('confirm-modal-backdrop')) hideModal();
    });
}

/**
 * Update the status badge inside a medication card.
 */
function updateBadge(card, taken) {
    const badge = card.querySelector('.med-status .badge');
    if (!badge) return;

    if (taken) {
        badge.className = 'badge badge-success';
        badge.innerHTML = '<i class="fas fa-check"></i> Taken';
    } else {
        badge.className = 'badge badge-pending';
        badge.innerHTML = '<i class="fas fa-hourglass-half"></i> Pending';
    }
}

/**
 * Update the dashboard stats cards with fresh data from the server.
 */
function updateDashboardStats(data) {
    const progressValue = document.getElementById('progress-value');
    const progressBar = document.getElementById('progress-bar');
    const takenCount = document.getElementById('taken-count');
    const streakValue = document.getElementById('streak-value');

    if (progressValue) progressValue.textContent = `${data.progress_percentage}%`;
    if (progressBar) progressBar.style.width = `${data.progress_percentage}%`;
    if (takenCount) takenCount.textContent = data.taken_count;
    if (streakValue) {
        streakValue.textContent = data.streak;
        // Add a fire animation if streak increased
        streakValue.classList.add('streak-bump');
        setTimeout(() => streakValue.classList.remove('streak-bump'), 500);
    }
}


// ---------------------------------------------------------------------------
//  Scroll Animations (Intersection Observer)
// ---------------------------------------------------------------------------

function initScrollAnimations() {
    const animatedElements = document.querySelectorAll(
        '.feature-card, .stat-card, .med-card, .auth-card, .form-card'
    );

    if (!animatedElements.length) return;

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry, index) => {
                if (entry.isIntersecting) {
                    // Stagger the animation for sibling cards
                    entry.target.style.transitionDelay = `${index * 0.05}s`;
                    entry.target.classList.add('animate-in');
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
    );

    animatedElements.forEach(el => observer.observe(el));
}


// ---------------------------------------------------------------------------
//  Navbar Scroll Effect
// ---------------------------------------------------------------------------

function initNavbarScroll() {
    const navbar = document.getElementById('main-navbar');
    if (!navbar) return;

    let lastScroll = 0;

    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;

        if (currentScroll > 60) {
            navbar.classList.add('navbar-scrolled');
        } else {
            navbar.classList.remove('navbar-scrolled');
        }

        lastScroll = currentScroll;
    });
}
