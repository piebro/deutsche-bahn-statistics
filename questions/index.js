function setupTable(containerId, files, columns, defaultSort = null) {
    let tableData = {};
    let currentSort = defaultSort || { column: null, direction: null };
    let keyCounter = 0;

    function generateKey() {
        return `table_${keyCounter++}`;
    }

    function loadData() {
        return Promise.all(files.map(file => {
            if (file.data) {
                // If data is already provided, use it directly
                const key = generateKey();
                file.key = key;
                return Promise.resolve({ key: key, data: file.data });
            } else {
                // Otherwise fetch from file
                return fetch(file.file)
                    .then(response => response.json())
                    .then(data => {
                        const key = generateKey();
                        file.key = key;
                        return { key: key, data: data };
                    });
            }
        }))
        .then(results => {
            results.forEach(result => {
                tableData[result.key] = result.data;
            });
        })
        .catch(error => console.error('Error:', error));
    }

    function createTableStructure() {
        const container = document.getElementById(containerId);
        container.innerHTML = ''; // Clear the container
    
        if (files.length > 1) {
            // Create tab buttons
            const tabButtons = document.createElement('div');
            tabButtons.className = 'tab-buttons';
            files.forEach((file, index) => {
                const button = document.createElement('button');
                button.className = `tab-button ${index === 0 ? 'active' : ''}`;
                button.setAttribute('data-tab', file.key);
                button.textContent = file.label;
                tabButtons.appendChild(button);
            });
            container.appendChild(tabButtons);
    
            // Create tab content
            const tabContent = document.createElement('div');
            tabContent.className = 'tab-content';
            files.forEach((file, index) => {
                const tab = document.createElement('div');
                tab.className = `tab ${index === 0 ? 'active' : ''}`;
                tab.id = file.key;
                tabContent.appendChild(tab);
            });
            container.appendChild(tabContent);
        }
    }

    function createTable(tabId) {
        const container = files.length > 1 
            ? document.querySelector(`#${containerId} #${tabId}`)
            : document.getElementById(containerId);
        
        const table = document.createElement('table');
        table.id = `${tabId}Table`;
        
        // Create table header
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        columns.forEach(column => {
            const th = document.createElement('th');
            th.className = 'sortable';
            th.setAttribute('data-sort', column.key);
            th.innerHTML = `${column.label || column.key} <span class="sort-icon">▼▲</span>`;
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);

        // Create table body
        const tbody = document.createElement('tbody');
        table.appendChild(tbody);

        container.appendChild(table);
    }

    function renderTable(tabId) {
        const tableBody = document.querySelector(`#${containerId} #${tabId}Table tbody`);
        tableBody.innerHTML = '';
        let data = tableData[tabId];
        
        // Apply filter if it exists
        const fileConfig = files.find(f => f.key === tabId);
        if (fileConfig && fileConfig.filter) {
            data = fileConfig.filter(data);
        }
        
        data.forEach(row => {
            const tr = document.createElement('tr');
            columns.forEach(column => {
                const td = document.createElement('td');
                let value = row[column.key];
                if (column.format) {
                    value = column.format(value);
                }
                td.textContent = value;
                tr.appendChild(td);
            });
            tableBody.appendChild(tr);
        });
    }

    function renderAllTables() {
        createTableStructure();
        if (files.length === 1) {
            createTable(files[0].key);
            if (currentSort.column) {
                sortTable(files[0].key + 'Table', currentSort.column, currentSort.direction);
                updateSortIcons(files[0].key + 'Table');
            }
            renderTable(files[0].key);
        } else {
            files.forEach(file => {
                createTable(file.key);
                if (currentSort.column) {
                    sortTable(file.key + 'Table', currentSort.column, currentSort.direction);
                    updateSortIcons(file.key + 'Table');
                }
                renderTable(file.key);
            });
        }
    }

    function setupSortListeners() {
        files.forEach(file => {
            const tableId = `${file.key}Table`;
            const headers = document.querySelectorAll(`#${containerId} #${tableId} th`);
            headers.forEach(header => {
                header.addEventListener('click', () => {
                    const column = header.dataset.sort;
                    if (currentSort.column === column) {
                        currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
                    } else {
                        currentSort.column = column;
                        currentSort.direction = 'asc';
                    }
                    sortTable(tableId, column, currentSort.direction);
                    updateSortIcons(tableId);
                });
            });
        });
    }

    function sortTable(tableId, column, direction) {
        const key = tableId.replace('Table', '');
        tableData[key].sort((a, b) => {
            if (a[column] < b[column]) return direction === 'asc' ? -1 : 1;
            if (a[column] > b[column]) return direction === 'asc' ? 1 : -1;
            return 0;
        });
        renderTable(key);
    }

    function updateSortIcons(tableId) {
        const headers = document.querySelectorAll(`#${containerId} #${tableId} th`);
        headers.forEach(header => {
            const icon = header.querySelector('.sort-icon');
            if (header.dataset.sort === currentSort.column) {
                icon.textContent = currentSort.direction === 'asc' ? '▲' : '▼';
            } else {
                icon.textContent = '▼▲';
            }
        });
    }

    // Update the handleFilterChange function
    function handleFilterChange(tabId) {
        console.log('handleFilterChange', tabId);
        const fileConfig = files.find(f => f.key === tabId);
        if (fileConfig && fileConfig.filterTriggerElementList && fileConfig.filter) {
            renderTable(tabId);
        }
    }

    // Modify setupTabListeners to include filter setup
    function setupTabListeners() {
        if (files.length > 1) {
            const tabButtons = document.querySelectorAll(`#${containerId} .tab-button`);
            const tabs = document.querySelectorAll(`#${containerId} .tab`);

            tabButtons.forEach(button => {
                button.addEventListener('click', () => {
                    const tabId = button.getAttribute('data-tab');
                    
                    tabButtons.forEach(btn => btn.classList.remove('active'));
                    tabs.forEach(tab => tab.classList.remove('active'));

                    button.classList.add('active');
                    document.getElementById(tabId).classList.add('active');
                });
            });
        }
    }

    loadData().then(() => {
        renderAllTables();
        setupSortListeners();
        if (files.length > 1) {
            setupTabListeners();
        }

        // Update filter trigger listeners to handle multiple elements
        files.forEach(file => {
            if (file.filterTriggerElementList && file.filter) {
                file.filterTriggerElementList.forEach(selector => {
                    const element = document.querySelector(selector);
                    if (element) {
                        // Handle both change and input events
                        ['change', 'input'].forEach(eventType => {
                            element.addEventListener(eventType, () => handleFilterChange(file.key));
                        });
                    }
                });
            }
        });
    });
}

function setupImages(containerId, tabData) {
    const container = document.getElementById(containerId);
    let keyCounter = 0;

    function generateKey() {
        return `tab_${keyCounter++}`;
    }

    // Generiere eindeutige Schlüssel für jeden Tab
    tabData.forEach(tab => {
        tab.key = generateKey();
    });

    // Create tab buttons
    const tabButtons = document.createElement('div');
    tabButtons.className = 'tab-buttons';
    tabData.forEach((tab, index) => {
        const button = document.createElement('button');
        button.className = 'tab-button' + (index === 0 ? ' active' : '');
        button.setAttribute('data-tab', tab.key);
        button.textContent = tab.label;
        tabButtons.appendChild(button);
    });
    container.appendChild(tabButtons);

    // Create tab content
    const tabContent = document.createElement('div');
    tabContent.className = 'tab-content';
    tabData.forEach((tab, index) => {
        const tabDiv = document.createElement('div');
        tabDiv.className = 'tab' + (index === 0 ? ' active' : '');
        tabDiv.id = tab.key;
        const img = document.createElement('img');
        img.src = tab.imageSrc;
        tabDiv.appendChild(img);
        tabContent.appendChild(tabDiv);
    });
    container.appendChild(tabContent);

    // Setup tab functionality
    const buttons = container.querySelectorAll('.tab-button');
    const tabs = container.querySelectorAll('.tab');
    buttons.forEach(button => {
        button.addEventListener('click', () => {
            const tabKey = button.getAttribute('data-tab');
            buttons.forEach(btn => btn.classList.remove('active'));
            tabs.forEach(tab => tab.classList.remove('active'));
            button.classList.add('active');
            container.querySelector(`#${tabKey}`).classList.add('active');
        });
    });
}