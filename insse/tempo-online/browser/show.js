// Parse CSV content handling quoted values and escapes
function parseCSV(csv) {
    const lines = csv.split(/\r\n|\n/);
    const result = [];
    let inQuotes = false;
    let currentField = '';
    let currentLine = [];

    function pushField() {
        currentLine.push(currentField.trim());
        currentField = '';
    }

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        
        if (!line.trim() && i > 0) continue; // Skip empty lines except header

        for (let char of line) {
            if (char === '"') {
                if (inQuotes && line[i + 1] === '"') {
                    // Handle escaped quotes
                    currentField += '"';
                    i++;
                } else {
                    // Toggle quotes mode
                    inQuotes = !inQuotes;
                }
            } else if (char === ',' && !inQuotes) {
                pushField();
            } else {
                currentField += char;
            }
        }
        
        pushField();
        result.push(currentLine);
        currentLine = [];
    }

    return result;
}

// Initialize DataTable with dynamic columns
function initializeDataTable(data) {
    const headers = data[0];
    const rows = data.slice(1);

    // Configure columns
    const columns = headers.map(header => ({
        title: header,
        data: header
    }));

    // Transform data into objects
    const tableData = rows.map(row => {
        const obj = {};
        headers.forEach((header, index) => {
            obj[header] = row[index];
        });
        return obj;
    });

    // Destroy existing DataTable if it exists
    if ($.fn.DataTable.isDataTable('#dataset-table')) {
        $('#dataset-table').DataTable().destroy();
    }

    // Create table element if it doesn't exist
    if (!$('#dataset-table').length) {
        $('#table-container').html('<table id="dataset-table" class="display" width="100%"></table>');
    }

    // Initialize DataTable
    $('#dataset-table').DataTable({
        data: tableData,
        columns: columns,
        pageLength: 25,
        lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
        order: [], // Disable initial sorting
        responsive: true,
        dom: '<"top"lf>rt<"bottom"ip>',
        language: {
            search: "Filter:",
            lengthMenu: "Show _MENU_ entries",
            info: "Showing _START_ to _END_ of _TOTAL_ entries",
            infoEmpty: "Showing 0 to 0 of 0 entries",
            infoFiltered: "(filtered from _MAX_ total entries)"
        },
        initComplete: function() {
            $('.dataTables_wrapper').addClass('full-width-table');
        }
    });
}

// Load and process CSV file
async function loadDataset() {
    try {
        // Get dataset ID from URL hash
        const datasetId = window.location.hash.slice(1);
        if (!datasetId) {
            throw new Error('No dataset ID specified in URL');
        }

        // Update page title
        document.getElementById('dataset-title').textContent = `Dataset: ${datasetId}`;
        document.title = `Dataset: ${datasetId}`;

        // Fetch CSV file
        const response = await fetch(`data/csv/${datasetId}.csv`);
        if (!response.ok) {
            throw new Error(`Failed to load dataset (${response.status} ${response.statusText})`);
        }

        const csvContent = await response.text();
        const data = parseCSV(csvContent);

        if (data.length === 0) {
            throw new Error('Dataset is empty');
        }

        // Initialize DataTable
        initializeDataTable(data);

    } catch (error) {
        console.error('Error loading dataset:', error);
        document.getElementById('table-container').innerHTML = `
            <div class="error">
                Error loading dataset: ${error.message}
                <br>Please check that the CSV file exists and is properly formatted.
            </div>
        `;
    }
}

// Handle hash changes to load different datasets
window.addEventListener('hashchange', loadDataset);

// Initial load
document.addEventListener('DOMContentLoaded', loadDataset);

// Export functionality
function exportToCSV() {
    const table = $('#dataset-table').DataTable();
    const csvContent = table
        .data()
        .toArray()
        .map(row => Object.values(row).join(','))
        .join('\n');
    
    const headers = table.columns().header().toArray()
        .map(header => header.textContent)
        .join(',');

    const blob = new Blob([headers + '\n' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `dataset_${window.location.hash.slice(1)}_export.csv`;
    link.click();
}