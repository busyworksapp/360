/**
 * D365 Table Functions - Global filtering and sorting for all tables
 * Apply to all tables with class 'table-d365'
 */

// Initialize all table functions when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeTableFiltering();
    initializeTableSorting();
    initializeTableSearch();
});

/**
 * Column Filtering - Works on all filter icons
 */
function initializeTableFiltering() {
    document.querySelectorAll('.filter-icon').forEach(icon => {
        icon.addEventListener('click', function(e) {
            e.stopPropagation();
            const th = this.closest('th');
            const table = this.closest('table');
            const columnIndex = Array.from(th.parentElement.children).indexOf(th);
            
            // Remove any existing filter dropdowns
            document.querySelectorAll('.filter-dropdown').forEach(d => d.remove());
            
            // Get unique values from this column
            const values = new Set();
            table.querySelectorAll('tbody tr').forEach(row => {
                // Skip empty state rows
                if (row.querySelector('td[colspan]')) return;
                
                const cell = row.children[columnIndex];
                if (cell) {
                    let text = '';
                    
                    // Check for badge first (status columns)
                    const badge = cell.querySelector('.badge-d365, .status-badge');
                    if (badge) {
                        text = badge.textContent.trim();
                    } 
                    // Check for links (order numbers, invoice numbers)
                    else if (cell.querySelector('a')) {
                        text = cell.querySelector('a').textContent.trim();
                    }
                    // Otherwise get cell text
                    else {
                        text = cell.textContent.trim();
                    }
                    
                    if (text) values.add(text);
                }
            });
            
            // Create filter dropdown
            const dropdown = document.createElement('div');
            dropdown.className = 'filter-dropdown';
            
            // Set all styles individually for better control
            dropdown.style.position = 'fixed';
            dropdown.style.background = 'white';
            dropdown.style.border = '1px solid #8a8886';
            dropdown.style.borderRadius = '2px';
            dropdown.style.boxShadow = '0 6.4px 14.4px 0 rgba(0,0,0,.132), 0 1.2px 3.6px rgba(0,0,0,.108)';
            dropdown.style.minWidth = '200px';
            dropdown.style.maxHeight = '300px';
            dropdown.style.overflowY = 'auto';
            dropdown.style.zIndex = '10000';
            dropdown.style.padding = '8px 0';
            
            // Add "Select All" option
            const allOption = document.createElement('div');
            allOption.style.cssText = `
                padding: 8px 16px;
                cursor: pointer;
                font-size: 12px;
                color: #323130;
                font-weight: 600;
            `;
            allOption.textContent = '(Select All)';
            allOption.addEventListener('mouseenter', function() {
                this.style.background = '#f3f2f1';
            });
            allOption.addEventListener('mouseleave', function() {
                this.style.background = 'white';
            });
            allOption.addEventListener('click', function() {
                table.querySelectorAll('tbody tr').forEach(row => {
                    if (!row.querySelector('td[colspan]')) {
                        row.style.display = '';
                    }
                });
                dropdown.remove();
            });
            dropdown.appendChild(allOption);
            
            // Add divider
            const divider = document.createElement('div');
            divider.style.cssText = 'height: 1px; background: #edebe9; margin: 4px 0;';
            dropdown.appendChild(divider);
            
            // Add value options
            if (values.size === 0) {
                const noData = document.createElement('div');
                noData.style.cssText = 'padding: 8px 16px; font-size: 12px; color: #a19f9d; font-style: italic;';
                noData.textContent = 'No data to filter';
                dropdown.appendChild(noData);
            } else {
                Array.from(values).sort().forEach(value => {
                    const option = document.createElement('div');
                    option.style.cssText = `
                        padding: 8px 16px;
                        cursor: pointer;
                        font-size: 12px;
                        color: #323130;
                    `;
                    option.textContent = value;
                    option.addEventListener('mouseenter', function() {
                        this.style.background = '#f3f2f1';
                    });
                    option.addEventListener('mouseleave', function() {
                        this.style.background = 'white';
                    });
                    option.addEventListener('click', function() {
                        // Filter rows
                        table.querySelectorAll('tbody tr').forEach(row => {
                            if (row.querySelector('td[colspan]')) return;
                            
                            const cell = row.children[columnIndex];
                            if (cell) {
                                let cellText = '';
                                
                                // Check for badge first
                                const badge = cell.querySelector('.badge-d365, .status-badge');
                                if (badge) {
                                    cellText = badge.textContent.trim();
                                }
                                // Check for links
                                else if (cell.querySelector('a')) {
                                    cellText = cell.querySelector('a').textContent.trim();
                                }
                                // Otherwise get cell text
                                else {
                                    cellText = cell.textContent.trim();
                                }
                                
                                row.style.display = cellText === value ? '' : 'none';
                            }
                        });
                        dropdown.remove();
                    });
                    dropdown.appendChild(option);
                });
            }
            
            // Position dropdown using fixed positioning (relative to viewport)
            const rect = icon.getBoundingClientRect();
            
            // Calculate position (below the icon)
            let left = rect.left;
            let top = rect.bottom + 5;
            
            // Ensure dropdown doesn't go off left edge
            if (left < 10) {
                left = 10;
            }
            
            // Ensure dropdown doesn't go off right edge of screen
            const dropdownWidth = 200; // min-width from CSS
            if (left + dropdownWidth > window.innerWidth - 10) {
                left = rect.right - dropdownWidth; // Align to right edge of icon
            }
            
            // Ensure dropdown doesn't go below viewport
            const dropdownMaxHeight = 300; // max-height from CSS
            if (top + dropdownMaxHeight > window.innerHeight - 20) {
                // Show above the icon instead
                top = rect.top - dropdownMaxHeight - 5;
                if (top < 10) {
                    // Not enough room above either, just limit height
                    top = 10;
                    dropdown.style.maxHeight = (window.innerHeight - 30) + 'px';
                }
            }
            
            // Set position
            dropdown.style.left = left + 'px';
            dropdown.style.top = top + 'px';
            
            // Add to DOM
            document.body.appendChild(dropdown);
            
            // Close dropdown when clicking outside
            setTimeout(() => {
                document.addEventListener('click', function closeDropdown() {
                    dropdown.remove();
                    document.removeEventListener('click', closeDropdown);
                });
            }, 0);
        });
    });
}
/**
 * Column Sorting - Works on all sort icons
 */
function initializeTableSorting() {
    document.querySelectorAll('.sort-icon').forEach(icon => {
        icon.addEventListener('click', function(e) {
            e.stopPropagation();
            const th = this.closest('th');
            const table = this.closest('table');
            const columnIndex = Array.from(th.parentElement.children).indexOf(th);
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr')).filter(row => !row.querySelector('td[colspan]'));
            
            // Determine sort direction
            const currentDirection = th.dataset.sortDirection || 'asc';
            const newDirection = currentDirection === 'asc' ? 'desc' : 'asc';
            
            // Reset all other column sort indicators
            th.parentElement.querySelectorAll('th').forEach(header => {
                if (header !== th) {
                    delete header.dataset.sortDirection;
                    const sortIcon = header.querySelector('.sort-icon');
                    if (sortIcon) {
                        sortIcon.className = 'fas fa-sort sort-icon';
                    }
                }
            });
            
            th.dataset.sortDirection = newDirection;
            
            // Update icon
            this.className = newDirection === 'asc' ? 'fas fa-sort-up sort-icon' : 'fas fa-sort-down sort-icon';
            
            // Sort rows
            rows.sort((a, b) => {
                const aCell = a.children[columnIndex];
                const bCell = b.children[columnIndex];
                
                if (!aCell || !bCell) return 0;
                
                let aText = '';
                let bText = '';
                
                // Extract text from cell a
                const aBadge = aCell.querySelector('.badge-d365, .status-badge');
                if (aBadge) {
                    aText = aBadge.textContent.trim();
                } else if (aCell.querySelector('a')) {
                    aText = aCell.querySelector('a').textContent.trim();
                } else {
                    aText = aCell.textContent.trim();
                }
                
                // Extract text from cell b
                const bBadge = bCell.querySelector('.badge-d365, .status-badge');
                if (bBadge) {
                    bText = bBadge.textContent.trim();
                } else if (bCell.querySelector('a')) {
                    bText = bCell.querySelector('a').textContent.trim();
                } else {
                    bText = bCell.textContent.trim();
                }
                
                // Try numeric comparison (for amounts, dates, etc.)
                const aNum = parseFloat(aText.replace(/[^0-9.-]/g, ''));
                const bNum = parseFloat(bText.replace(/[^0-9.-]/g, ''));
                
                if (!isNaN(aNum) && !isNaN(bNum)) {
                    return newDirection === 'asc' ? aNum - bNum : bNum - aNum;
                }
                
                // Date comparison (if looks like a date)
                const aDate = new Date(aText);
                const bDate = new Date(bText);
                if (!isNaN(aDate) && !isNaN(bDate)) {
                    return newDirection === 'asc' ? aDate - bDate : bDate - aDate;
                }
                
                // String comparison
                return newDirection === 'asc' 
                    ? aText.localeCompare(bText)
                    : bText.localeCompare(aText);
            });
            
            // Reorder rows
            rows.forEach(row => tbody.appendChild(row));
        });
    });
}

/**
 * Global table search - Works with filter inputs
 */
function initializeTableSearch() {
    document.querySelectorAll('#filterInput, .table-filter-input').forEach(input => {
        input.addEventListener('input', function(e) {
            const filter = e.target.value.toLowerCase();
            const container = this.closest('.dashboard-container, .container-fluid, .container');
            const table = container ? container.querySelector('.table-d365') : document.querySelector('.table-d365');
            
            if (!table) return;
            
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                // Skip empty state rows
                if (row.querySelector('td[colspan]')) return;
                
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(filter) ? '' : 'none';
            });
        });
    });
}

/**
 * Row selection helper - for tables with checkboxes
 */
function selectRow(row, event) {
    // Don't interfere with checkbox clicks or link clicks
    if (event.target.type === 'checkbox' || event.target.tagName === 'A') return;
    
    // Check if clicked element is inside a link
    if (event.target.closest('a')) return;
    
    // Check if clicked on a button
    if (event.target.closest('button')) return;
    
    const checkbox = row.querySelector('.row-select');
    if (checkbox) {
        checkbox.checked = !checkbox.checked;
        checkbox.dispatchEvent(new Event('change', { bubbles: true }));
    }
}

/**
 * Select all checkbox handler
 */
function toggleSelectAll(checkbox) {
    const table = checkbox.closest('table');
    const checkboxes = table.querySelectorAll('.row-select');
    checkboxes.forEach(cb => cb.checked = checkbox.checked);
    
    // Trigger change event for command bar updates
    const event = new Event('change', { bubbles: true });
    checkboxes.forEach(cb => cb.dispatchEvent(event));
}

// Make functions globally available
window.selectRow = selectRow;
window.toggleSelectAll = toggleSelectAll;
