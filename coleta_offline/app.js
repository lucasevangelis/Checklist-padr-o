document.addEventListener('DOMContentLoaded', () => {
    // Populate Modulo 1-36
    const moduloSelect = document.getElementById('modulo');
    for (let i = 1; i <= 36; i++) {
        const option = document.createElement('option');
        option.value = i;
        option.textContent = i;
        moduloSelect.appendChild(option);
    }

    // Set today's date as default
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('data').value = today;

    // Load data from LocalStorage
    let checklists = JSON.parse(localStorage.getItem('checklists_offline')) || [];
    renderTable();
    updateDatalists();

    // Form Submit
    document.getElementById('checklist-form').addEventListener('submit', (e) => {
        e.preventDefault();

        // Convert Date to DD/MM/YYYY format to match the Dashboard's expected format
        const dateRaw = document.getElementById('data').value;
        const [year, month, day] = dateRaw.split('-');
        const formattedDate = `${day}/${month}/${year}`;

        const entry = {
            Data: formattedDate,
            Piso: document.getElementById('piso').value,
            Posição: document.getElementById('posicao').value,
            Módulo: document.getElementById('modulo').value,
            Observação: document.getElementById('observacao').value,
            id: Date.now() // unique identifier
        };

        checklists.push(entry);
        localStorage.setItem('checklists_offline', JSON.stringify(checklists));
        
        // Reset free text fields
        document.getElementById('posicao').value = '';
        document.getElementById('modulo').value = '';
        document.getElementById('observacao').value = '';
        
        renderTable();
        updateDatalists();
    });

    // Render Table
    function renderTable() {
        const tbody = document.querySelector('#preview-table tbody');
        tbody.innerHTML = '';
        
        checklists.forEach(item => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${item.Data}</td>
                <td>${item.Piso}</td>
                <td>${item.Posição}</td>
                <td>${item.Módulo}</td>
                <td>${item.Observação}</td>
                <td><button class="btn-delete" onclick="deleteEntry(${item.id})">✖</button></td>
            `;
            tbody.appendChild(tr);
        });
    }

    // Delete entry
    window.deleteEntry = function(id) {
        checklists = checklists.filter(item => item.id !== id);
        localStorage.setItem('checklists_offline', JSON.stringify(checklists));
        renderTable();
    };

    // Update Datalists (Autocomplete based on history)
    function updateDatalists() {
        const posDatalist = document.getElementById('historico-posicoes');
        const obsDatalist = document.getElementById('historico-observacoes');
        
        // Get unique values from current offline history
        const posicoes = [...new Set(checklists.map(item => item.Posição))].filter(Boolean);
        const observacoes = [...new Set(checklists.map(item => item.Observação))].filter(Boolean);
        
        posDatalist.innerHTML = posicoes.map(p => `<option value="${p}">`).join('');
        obsDatalist.innerHTML = observacoes.map(o => `<option value="${o}">`).join('');
    }

    // Clear All
    document.getElementById('btn-clear').addEventListener('click', () => {
        if (confirm("Tem certeza que deseja apagar todos os registros desta sessão?")) {
            checklists = [];
            localStorage.removeItem('checklists_offline');
            renderTable();
        }
    });

    // Export Excel
    document.getElementById('btn-export').addEventListener('click', () => {
        if (checklists.length === 0) {
            alert("Não há dados para exportar.");
            return;
        }

        // Clean up internal ID for the export
        const exportData = checklists.map(({id, ...rest}) => rest);

        const ws = XLSX.utils.json_to_sheet(exportData);
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, "Checklist");
        
        // Generate file
        XLSX.writeFile(wb, `Checklist_Offline_${new Date().getTime()}.xlsx`);
    });

    // Network Status monitoring
    const statusIndicator = document.getElementById('status-indicator');
    function updateOnlineStatus() {
        if (navigator.onLine) {
            statusIndicator.textContent = 'Online';
            statusIndicator.className = 'status online';
        } else {
            statusIndicator.textContent = 'Offline';
            statusIndicator.className = 'status offline';
        }
    }

    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    updateOnlineStatus();
});
