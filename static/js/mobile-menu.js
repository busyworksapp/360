/**
 * Mobile Menu Functionality
 * Handles sidebar toggle and mobile navigation
 */

document.addEventListener('DOMContentLoaded', function() {
    // Don't create hamburger button - use bottom nav only
    if (window.innerWidth <= 991) {
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            // Create overlay for sidebar
            if (!document.querySelector('.sidebar-overlay')) {
                const overlay = document.createElement('div');
                overlay.className = 'sidebar-overlay';
                document.body.appendChild(overlay);
                
                // Close sidebar when clicking overlay
                overlay.addEventListener('click', function() {
                    sidebar.classList.remove('show');
                    overlay.classList.remove('show');
                });
            }
            
            // Close sidebar when clicking any sidebar link
            const sidebarLinks = sidebar.querySelectorAll('a');
            sidebarLinks.forEach(link => {
                link.addEventListener('click', function() {
                    const overlay = document.querySelector('.sidebar-overlay');
                    setTimeout(() => {
                        sidebar.classList.remove('show');
                        if (overlay) overlay.classList.remove('show');
                    }, 100);
                });
            });
        }
    }
    // Handle window resize
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            const overlay = document.querySelector('.sidebar-overlay');
            const sidebar = document.querySelector('.sidebar');
            
            if (window.innerWidth > 991) {
                // Desktop view
                if (overlay) overlay.classList.remove('show');
                if (sidebar) sidebar.classList.remove('show');
            }
        }, 250);
    });
    
    // Prevent body scroll when sidebar is open on mobile
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.attributeName === 'class') {
                const sidebar = document.querySelector('.sidebar');
                if (sidebar && sidebar.classList.contains('show') && window.innerWidth <= 991) {
                    document.body.style.overflow = 'hidden';
                } else {
                    document.body.style.overflow = '';
                }
            }
        });
    });
    
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        observer.observe(sidebar, { attributes: true });
    }
    
    // Touch swipe to close sidebar
    let touchStartX = 0;
    let touchEndX = 0;
    
    document.addEventListener('touchstart', function(e) {
        touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });
    
    document.addEventListener('touchend', function(e) {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    }, { passive: true });
    
    function handleSwipe() {
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.querySelector('.sidebar-overlay');
        
        if (sidebar && sidebar.classList.contains('show')) {
            // Swipe left to close
            if (touchEndX < touchStartX - 50) {
                sidebar.classList.remove('show');
                if (overlay) overlay.classList.remove('show');
            }
        }
    }
    
    // Make tables horizontally scrollable on mobile
    const tables = document.querySelectorAll('table:not(.table-responsive table)');
    tables.forEach(table => {
        if (!table.parentElement.classList.contains('table-responsive')) {
            const wrapper = document.createElement('div');
            wrapper.className = 'table-responsive';
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        }
    });
    
    // Improve form inputs on iOS
    if (/iPad|iPhone|iPod/.test(navigator.userAgent)) {
        const inputs = document.querySelectorAll('input[type="text"], input[type="email"], input[type="password"], input[type="number"], textarea, select');
        inputs.forEach(input => {
            // Prevent zoom on focus
            if (parseFloat(window.getComputedStyle(input).fontSize) < 16) {
                input.style.fontSize = '16px';
            }
        });
    }
    
    // Add touch feedback to buttons
    const buttons = document.querySelectorAll('.btn, button, a.nav-link');
    buttons.forEach(button => {
        button.addEventListener('touchstart', function() {
            this.style.opacity = '0.7';
        }, { passive: true });
        
        button.addEventListener('touchend', function() {
            this.style.opacity = '1';
        }, { passive: true });
    });
    
    // Optimize images for mobile
    if (window.innerWidth <= 768) {
        const images = document.querySelectorAll('img');
        images.forEach(img => {
            // Add loading="lazy" for better performance
            if (!img.hasAttribute('loading')) {
                img.setAttribute('loading', 'lazy');
            }
        });
    }
    
    // Handle orientation change
    window.addEventListener('orientationchange', function() {
        // Close sidebar on orientation change
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.querySelector('.sidebar-overlay');
        const toggleBtn = document.querySelector('.mobile-menu-toggle');
        
        if (sidebar && sidebar.classList.contains('show')) {
            sidebar.classList.remove('show');
            if (overlay) overlay.classList.remove('show');
            if (toggleBtn) toggleBtn.querySelector('i').className = 'fas fa-bars';
        }
        
        // Recalculate viewport height
        document.documentElement.style.setProperty('--vh', `${window.innerHeight * 0.01}px`);
    });
    
    // Set initial viewport height for mobile browsers
    document.documentElement.style.setProperty('--vh', `${window.innerHeight * 0.01}px`);
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#' && href !== '#!') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
});

// Export for use in other scripts
window.mobileMenu = {
    open: function() {
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.querySelector('.sidebar-overlay');
        if (sidebar) {
            sidebar.classList.add('show');
            if (overlay) overlay.classList.add('show');
        }
    },
    close: function() {
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.querySelector('.sidebar-overlay');
        if (sidebar) {
            sidebar.classList.remove('show');
            if (overlay) overlay.classList.remove('show');
        }
    },
    toggle: function() {
        const sidebar = document.querySelector('.sidebar');
        if (sidebar && sidebar.classList.contains('show')) {
            this.close();
        } else {
            this.open();
        }
    }
};
