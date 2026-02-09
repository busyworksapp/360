/**
 * Mobile Table to Card Converter
 * Automatically converts tables to card-based layouts on mobile devices
 */

(function() {
    'use strict';
    
    // Configuration
    const MOBILE_BREAKPOINT = 768;
    
    /**
     * Convert table to mobile cards
     */
    function convertTableToCards(table) {
        // Check if already converted
        if (table.parentElement.querySelector('.mobile-cards')) {
            return;
        }
        
        const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent.trim());
        const rows = Array.from(table.querySelectorAll('tbody tr'));
        
        // Create mobile cards container
        const cardsContainer = document.createElement('div');
        cardsContainer.className = 'mobile-cards';
        
        rows.forEach(row => {
            const cells = Array.from(row.querySelectorAll('td'));
            const card = createMobileCard(headers, cells, row);
            cardsContainer.appendChild(card);
        });
        
        // Insert cards after table
        table.parentElement.appendChild(cardsContainer);
        
        // Add responsive class to parent
        if (!table.parentElement.classList.contains('table-responsive-cards')) {
            table.parentElement.classList.add('table-responsive-cards');
        }
    }
    
    /**
     * Create a mobile card from table row
     */
    function createMobileCard(headers, cells, originalRow) {
        const card = document.createElement('div');
        card.className = 'mobile-card';
        
        // Copy data attributes from original row
        if (originalRow.dataset) {
            Object.keys(originalRow.dataset).forEach(key => {
                card.dataset[key] = originalRow.dataset[key];
            });
        }
        
        // Create card header (first cell usually contains primary info)
        if (cells.length > 0) {
            const header = document.createElement('div');
            header.className = 'mobile-card-header';
            
            const title = document.createElement('h3');
            title.className = 'mobile-card-title';
            title.innerHTML = cells[0].innerHTML;
            header.appendChild(title);
            
            // Check for badge/status in row
            const badge = cells[cells.length - 1].querySelector('.badge, .badge-d365');
            if (badge) {
                const cardBadge = badge.cloneNode(true);
                cardBadge.className += ' mobile-card-badge';
                header.appendChild(cardBadge);
            }
            
            card.appendChild(header);
        }
        
        // Create card body
        const body = document.createElement('div');
        body.className = 'mobile-card-body';
        
        // Add rows for each cell (skip first as it's in header)
        cells.slice(1).forEach((cell, index) => {
            const headerIndex = index + 1;
            if (headerIndex < headers.length) {
                const row = document.createElement('div');
                row.className = 'mobile-card-row';
                
                const label = document.createElement('div');
                label.className = 'mobile-card-label';
                label.textContent = headers[headerIndex];
                
                const value = document.createElement('div');
                value.className = 'mobile-card-value';
                value.innerHTML = cell.innerHTML;
                
                row.appendChild(label);
                row.appendChild(value);
                body.appendChild(row);
            }
        });
        
        card.appendChild(body);
        
        // Create card footer with action buttons
        const actions = originalRow.querySelectorAll('a.btn, button.btn');
        if (actions.length > 0) {
            const footer = document.createElement('div');
            footer.className = 'mobile-card-footer';
            
            actions.forEach(action => {
                const btn = action.cloneNode(true);
                btn.className = btn.className.replace('btn-sm', '');
                footer.appendChild(btn);
            });
            
            card.appendChild(footer);
        }
        
        // Make card clickable if row has data-href
        if (originalRow.dataset.href) {
            card.style.cursor = 'pointer';
            card.addEventListener('click', function(e) {
                // Don't navigate if clicking on a button or link
                if (!e.target.closest('a, button')) {
                    window.location.href = originalRow.dataset.href;
                }
            });
        }
        
        return card;
    }
    
    /**
     * Convert product/service lists to grid
     */
    function convertToGrid(container) {
        if (container.classList.contains('mobile-grid')) {
            return;
        }
        
        container.classList.add('mobile-grid');
        
        const items = Array.from(container.children);
        items.forEach(item => {
            if (!item.classList.contains('grid-item')) {
                item.classList.add('grid-item');
            }
        });
    }
    
    /**
     * Initialize mobile enhancements
     */
    function initMobileEnhancements() {
        if (window.innerWidth <= MOBILE_BREAKPOINT) {
            // Convert all tables to cards
            const tables = document.querySelectorAll('table.table, table.table-d365');
            tables.forEach(table => {
                // Skip tables that shouldn't be converted
                if (!table.closest('.no-mobile-cards')) {
                    convertTableToCards(table);
                }
            });
            
            // Convert product/service grids
            const productGrids = document.querySelectorAll('.products-grid, .services-grid');
            productGrids.forEach(grid => convertToGrid(grid));
            
            // Add bottom navigation if not exists
            addBottomNavigation();
            
            // Add pull to refresh
            addPullToRefresh();
        }
    }
    
    /**
     * Add bottom navigation for mobile
     */
    function addBottomNavigation() {
        // Only add if on mobile and doesn't exist
        if (window.innerWidth > MOBILE_BREAKPOINT) return;
        if (document.querySelector('.bottom-nav-mobile')) return;
        
        // Check if we're in admin or customer portal
        const isAdmin = document.querySelector('.sidebar');
        if (!isAdmin) return;
        
        const nav = document.createElement('nav');
        nav.className = 'bottom-nav-mobile';
        
        // Get current page
        const currentPath = window.location.pathname;
        
        // Define navigation items based on context
        let navItems = [];
        
        if (currentPath.includes('/admin')) {
            navItems = [
                { icon: 'fa-th-large', label: 'Dashboard', href: '/admin' },
                { icon: 'fa-box', label: 'Products', href: '/admin/products' },
                { icon: 'fa-shopping-cart', label: 'Orders', href: '/admin/orders' },
                { icon: 'fa-file-invoice-dollar', label: 'Invoices', href: '/admin/invoices' },
                { icon: 'fa-bars', label: 'More', href: '#', onclick: 'window.mobileMenu.toggle()' }
            ];
        } else if (currentPath.includes('/customer')) {
            navItems = [
                { icon: 'fa-home', label: 'Home', href: '/customer/dashboard' },
                { icon: 'fa-shopping-cart', label: 'Orders', href: '/customer/orders' },
                { icon: 'fa-file-invoice', label: 'Invoices', href: '/customer/invoices' },
                { icon: 'fa-store', label: 'Store', href: '/customer/products' },
                { icon: 'fa-user', label: 'Profile', href: '/customer/profile' }
            ];
        }
        
        navItems.forEach(item => {
            const link = document.createElement('a');
            link.className = 'bottom-nav-item';
            link.href = item.href;
            
            if (currentPath === item.href || currentPath.startsWith(item.href + '/')) {
                link.classList.add('active');
            }
            
            if (item.onclick) {
                link.onclick = function(e) {
                    e.preventDefault();
                    eval(item.onclick);
                };
            }
            
            link.innerHTML = `
                <i class="fas ${item.icon}"></i>
                <span>${item.label}</span>
            `;
            
            nav.appendChild(link);
        });
        
        document.body.appendChild(nav);
    }
    
    /**
     * Add pull to refresh functionality
     */
    function addPullToRefresh() {
        let startY = 0;
        let currentY = 0;
        let pulling = false;
        
        const indicator = document.createElement('div');
        indicator.className = 'pull-to-refresh';
        indicator.innerHTML = '<div class="pull-to-refresh-icon"></div>';
        document.body.insertBefore(indicator, document.body.firstChild);
        
        document.addEventListener('touchstart', function(e) {
            if (window.scrollY === 0) {
                startY = e.touches[0].pageY;
                pulling = true;
            }
        }, { passive: true });
        
        document.addEventListener('touchmove', function(e) {
            if (!pulling) return;
            
            currentY = e.touches[0].pageY;
            const diff = currentY - startY;
            
            if (diff > 0 && diff < 100) {
                indicator.style.transform = `translateY(${diff - 100}%)`;
            } else if (diff >= 100) {
                indicator.classList.add('active');
            }
        }, { passive: true });
        
        document.addEventListener('touchend', function() {
            if (pulling && indicator.classList.contains('active')) {
                // Reload page
                window.location.reload();
            }
            
            pulling = false;
            indicator.classList.remove('active');
            indicator.style.transform = 'translateY(-100%)';
        }, { passive: true });
    }
    
    /**
     * Show toast notification
     */
    function showToast(message, type = 'success', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast-mobile ${type}`;
        
        const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';
        const title = type === 'success' ? 'Success' : 'Error';
        
        toast.innerHTML = `
            <div class="toast-mobile-icon">
                <i class="fas ${icon}"></i>
            </div>
            <div class="toast-mobile-content">
                <div class="toast-mobile-title">${title}</div>
                <div class="toast-mobile-message">${message}</div>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideDown 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }
    
    /**
     * Create floating action button
     */
    function addFloatingActionButton(icon, action, tooltip) {
        const fab = document.createElement('button');
        fab.className = 'fab-mobile';
        fab.innerHTML = `<i class="fas ${icon}"></i>`;
        fab.title = tooltip;
        fab.onclick = action;
        
        document.body.appendChild(fab);
        
        return fab;
    }
    
    /**
     * Handle window resize
     */
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            // Re-initialize if crossing breakpoint
            const wasMobile = document.querySelector('.mobile-cards') !== null;
            const isMobile = window.innerWidth <= MOBILE_BREAKPOINT;
            
            if (wasMobile !== isMobile) {
                // Remove existing mobile elements
                document.querySelectorAll('.mobile-cards, .bottom-nav-mobile, .pull-to-refresh, .fab-mobile').forEach(el => el.remove());
                
                // Re-initialize
                if (isMobile) {
                    initMobileEnhancements();
                }
            }
        }, 250);
    });
    
    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initMobileEnhancements);
    } else {
        initMobileEnhancements();
    }
    
    // Export utilities
    window.mobileUtils = {
        convertTableToCards,
        convertToGrid,
        showToast,
        addFloatingActionButton,
        refresh: initMobileEnhancements
    };
    
})();
