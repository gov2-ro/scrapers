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
    // Filter out regional rows
    const filteredData = filterOutRegionalRows(data);
    const headers = filteredData[0];
    const rows = filteredData.slice(1);

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

        // Load CSV data
        const csvContent = await response.text();
        const data = parseCSV(csvContent);

        if (data.length === 0) {
            throw new Error('Dataset is empty');
        }

        // Initialize DataTable with filtered data
        initializeDataTable(data);

        // Convert filtered data to array of objects for chart
        const filteredData = filterOutRegionalRows(data);
        const headers = filteredData[0];
        const rows = filteredData.slice(1);
        const objectData = rows.map(row => {
            const obj = {};
            headers.forEach((header, index) => {
                obj[header] = row[index];
            });
            return obj;
        });

        // Initialize chart with filtered data
        await initializeChart(objectData);

        // Load JSON metadata
        const response2 = await fetch(`data/matrices/${datasetId}.json`);
        if (!response2.ok) {
            throw new Error(`Failed to load dataset metadata (${response2.status} ${response2.statusText})`);
        }

        // Process JSON metadata
        const jsonContent = await response2.json();
        
        // Update page elements with metadata
        document.getElementById('ziname').innerHTML = jsonContent['matrixName'];
        document.getElementById('ziobs').innerHTML = '<small class="lh1">obs: ' + jsonContent['observatii'] + '</small>';
        document.getElementById('zidef').innerHTML = '<small class="lh1">' + jsonContent['definitie'] + '</small>' + '| <small class="lh1"><b>Sursă</b> date: ' + jsonContent['surseDeDate'][0]['nume'] + '</small>';
        document.getElementById('ziultimaActualizare').innerHTML = 'ultima actualizare: ' + jsonContent['ultimaActualizare'];
        document.getElementById('download').innerHTML = '<a class="dl" href="data/csv/' + datasetId + '.csv" download="' + datasetId + '.csv">download csv</a>  &darr;';
        document.getElementById('ancestors1').innerHTML = '<small>' + jsonContent['ancestors'][1]['code'] + '</small> ' + jsonContent['ancestors'][1]['name'];
        
        const rr = jsonContent['ancestors'][2]['name'];
        document.getElementById('ancestors2').innerHTML = '<small>' + jsonContent['ancestors'][2]['code'] + '</small> ' + rr;
        document.getElementById('ancestors3').innerHTML = '<small>' + jsonContent['ancestors'][3]['code'] + '</small> ' + jsonContent['ancestors'][3]['name'];
        
        // Update page title
        document.title = datasetId + ' - ' + jsonContent['matrixName'] + ' &middot; ' + document.title;

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

// Add Chart.js to the page
function loadChartJS() {
    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js';
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
    });
}

// Create and update the chart
function createYearlySumChart(data) {
    // Check if Sexe column exists
    const hasGenderData = data.some(row => 'Sexe' in row);
    
    if (!hasGenderData) {
        // Use original single bar implementation
        const yearlyTotals = data.reduce((acc, row) => {
            let year = row.Perioade.startsWith('Anul ') ? 
                row.Perioade.split(' ')[1] : 
                row.Perioade.includes('Trimestrul') ? 
                    row.Perioade.split(' ').pop() : null;
            
            if (year) {
                acc[year] = (acc[year] || 0) + parseInt(row.Valoare, 10);
            }
            return acc;
        }, {});

        // Rest of original single bar implementation...
        return createSingleBarChart(yearlyTotals);
    }
    function createSingleBarChart(yearlyTotals) {
        const yearlyData = Object.entries(yearlyTotals)
            .map(([year, value]) => ({ year, value }))
            .sort((a, b) => a.year - b.year);
    
        const chartContainer = document.getElementById('zichart');
        chartContainer.innerHTML = '<canvas id="yearlyBarChart"></canvas>';
    
        const ctx = document.getElementById('yearlyBarChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: yearlyData.map(d => d.year),
                datasets: [{
                    label: 'Total',
                    data: yearlyData.map(d => d.value),
                    backgroundColor: '#4299E1',
                    borderColor: '#3182CE',
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.parsed.y.toLocaleString();
                            }
                        }
                    },
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }
    // Group data by year and gender
    const yearlyGenderTotals = data.reduce((acc, row) => {
        let year;
        if (row.Perioade.startsWith('Anul ')) {
            year = row.Perioade.split(' ')[1];
        } else if (row.Perioade.includes('Trimestrul')) {
            year = row.Perioade.split(' ').pop();
        }
        
        if (year) {
            if (!acc[year]) {
                acc[year] = { Masculin: 0, Feminin: 0 };
            }
            acc[year][row.Sexe] += parseInt(row.Valoare, 10);
        }
        return acc;
    }, {});

    // Convert to arrays and sort by year
    const years = Object.keys(yearlyGenderTotals).sort();
    const masculinData = years.map(year => yearlyGenderTotals[year].Masculin);
    const femininData = years.map(year => yearlyGenderTotals[year].Feminin);

    // Clear existing chart
    const chartContainer = document.getElementById('zichart');
    chartContainer.innerHTML = '<canvas id="yearlyBarChart"></canvas>';

    // Create stacked bar chart
    const ctx = document.getElementById('yearlyBarChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: years,
            datasets: [
                {
                    label: 'Masculin',
                    data: masculinData,
                    backgroundColor: '#4299E1',
                    borderColor: '#3182CE',
                    borderWidth: 1,
                    borderRadius: 4
                },
                {
                    label: 'Feminin',
                    data: femininData,
                    backgroundColor: '#F56565',
                    borderColor: '#E53E3E',
                    borderWidth: 1,
                    borderRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.parsed.y.toLocaleString()}`;
                        }
                    }
                },
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                x: {
                    stacked: true
                },
                y: {
                    stacked: true,
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

// Create and update the chart
function createYearlyChart(data) {
    // Filter for annual data and transform
    const yearlyData = data
        .filter(row => row.Perioade?.match(/^Anul \d{4}$/))
        .map(row => ({
            year: row.Perioade.split(' ')[1],
            value: parseInt(row.Valoare, 10)
        }))
        .sort((a, b) => a.year - b.year);

    // Clear existing chart if any
    const chartContainer = document.getElementById('zichart');
    chartContainer.innerHTML = '<canvas id="yearlyBarChart"></canvas>';

    // Create the chart
    const ctx = document.getElementById('yearlyBarChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: yearlyData.map(d => d.year),
            datasets: [{
                label: 'Annual Values',
                data: yearlyData.map(d => d.value),
                backgroundColor: '#4299E1',
                borderColor: '#3182CE',
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.parsed.y.toLocaleString();
                        }
                    }
                },
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

// Initialize chart when data is loaded
async function initializeChart(data) {
    try {
        await loadChartJS();
        createYearlySumChart(data);
    } catch (error) {
        console.error('Error initializing chart:', error);
        document.getElementById('zichart').innerHTML = 
            '<div class="error">Error loading chart: ' + error.message + '</div>';
    }
}

function filterOutRegionalRows(data) {
    // First find column that contains both region and judet
    const headers = data[0];
    const regionColumn = headers.findIndex(header => 
        header.toLowerCase().includes('regiun') && 
        header.toLowerCase().includes('judet')
    );

    if (regionColumn === -1) {
        // No mixed region/judet column found, return original data
        return data;
    }

    // Keep header row and filter other rows
    return [
        data[0],
        ...data.slice(1).filter(row => 
            !row[regionColumn].toLowerCase().includes('regiun')
        )
    ];
}