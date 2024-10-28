// CSV Parser function
function parseCsv(csv) {
    const lines = csv.split('\n');
    const headers = lines[0].split(',').map(header => header.trim());
    
    return lines.slice(1)
        .filter(line => line.trim()) // Skip empty lines
        .map(line => {
            // Handle quoted fields properly
            const values = [];
            let inQuotes = false;
            let currentValue = '';
            
            for (let char of line) {
                if (char === '"') {
                    inQuotes = !inQuotes;
                } else if (char === ',' && !inQuotes) {
                    values.push(currentValue);
                    currentValue = '';
                } else {
                    currentValue += char;
                }
            }
            values.push(currentValue); // Don't forget the last value
            
            // Create object from headers and values
            return headers.reduce((obj, header, index) => {
                const value = values[index] ? values[index].replace(/^["']|["']$/g, '').trim() : '';
                obj[header] = value;
                return obj;
            }, {});
        });
}

// Function to transform flat data into hierarchical structure
function buildHierarchy(categories) {
    const hierarchy = [];
    const lookup = {};
    
    // First pass: create lookup table and identify root nodes
    categories.forEach(category => {
        if (category.level === '0') return;
        
        lookup[category.code] = {
            ...category,
            children: [],
            datasets: []
        };
        
        if (!category.parentCode) {
            hierarchy.push(lookup[category.code]);
        }
    });
    
    // Second pass: build hierarchy
    categories.forEach(category => {
        if (category.level === '0' || !category.parentCode) return;
        
        const parent = lookup[category.parentCode];
        if (parent) {
            parent.children.push(lookup[category.code]);
        }
    });
    
    return { hierarchy, lookup };
}

// Function to add datasets to their respective categories
function addDatasetsToCategories(datasets, lookup) {
    datasets.forEach(dataset => {
        const parentCategory = lookup[dataset.directAncestor];
        if (parentCategory) {
            parentCategory.datasets.push(dataset);
        }
    });
}

// Function to generate HTML for the table of contents
function generateTocHtml(node) {
    let html = '';
    
    // Generate heading based on level
    if (node.level) {
        const levelClass = `level-${node.level}`;
        html += `<div class="${levelClass}">
            <h${node.level} id="x-${node.code}">
                <span class="code">${node.code}</span>
                ${node.name}
            </h${node.level}>
        </div>\n`;
    }
    
    // Add datasets if any
    if (node.datasets && node.datasets.length > 0) {
        // console.log(node.datasets)   
        html += '<ul class="datasets">\n';
        node.datasets.sort((a, b) => a.fileName.localeCompare(b.fileName));
        node.datasets.forEach(dataset => {
            
            html += `  <li>
                <span class="code"><a href="show.html#${dataset.fileName}">${dataset.fileName}</a></span>
                ${dataset.matrixName} <code>(${convertSize(dataset.filesize)})</code>
                
            </li>\n`;
        });
        html += '</ul>\n';
    }
    
    // Recursively process children
    if (node.children && node.children.length > 0) {
        // Sort children by code
        node.children.sort((a, b) => a.code.localeCompare(b.code));
        
        html += '<ul class="categories">\n';
        node.children.forEach(child => {
            html += '<li>\n';
            html += generateTocHtml(child);
            html += '</li>\n';
        });
        html += '</ul>\n';
    }
    
    return html;
}
 
function convertSize(human) {
    // const units = ['B', 'K', 'M', 'G', 'T'];
    // let size = parseFloat(human.replace(/[^0-9.]/g, ''));
    let size = parseFloat(human.replace(/[^0-9.]/g, ''));
 
    // Convert human-readable string to bytes
    // um = human.toLowerCase().slice(-1)
    um = human.slice(-1)
    switch (um) {
        case 'B':
            zz = size / 1000;
        case 'K':
            zz = size;
        case 'M':
            zz = size * 1000;
        case 'G':
            zz = size * 1000 * 1000;
        case 'T':
            zz = size * 1000 * 1000 * 1000;
        default:
            // throw new Error('Invalid unit');
            zz = size
    }
    ismuch = '  '
    if(um=='M' || um=='K') {
        ismuch = ' not-much '
    }
    if(um=='M' && size >= 5) {
        ismuch = ' is-much '
    }

    return '<span class="size-'+um+ ismuch +'">' + zz + um +'</span>'
}

// Main function to initialize the table of contents
async function initializeTableOfContents() {
    try {
        // Load CSV files
        const [categoriesResponse, datasetsResponse] = await Promise.all([
            fetch('data/x-categories.csv'),
            fetch('data/x-datasets-size.csv')
        ]);

        if (!categoriesResponse.ok || !datasetsResponse.ok) {
            throw new Error('Failed to load CSV files');
        }

        const [categoriesCsv, datasetsCsv] = await Promise.all([
            categoriesResponse.text(),
            datasetsResponse.text()
        ]);

        // Parse CSV data
        const categories = parseCsv(categoriesCsv);
        const datasets = parseCsv(datasetsCsv);

        // Build hierarchy and get lookup
        const { hierarchy, lookup } = buildHierarchy(categories);

        // Sort root level items by code
        hierarchy.sort((a, b) => a.code.localeCompare(b.code));

        // Add datasets to categories
        addDatasetsToCategories(datasets, lookup);

        // Generate HTML
        let tocHtml = '<div class="table-of-contents">\n';
        hierarchy.forEach(node => {
            tocHtml += generateTocHtml(node);
        });
        tocHtml += '</div>';

        // Insert into document
        document.getElementById('toc-container').innerHTML = tocHtml;

    } catch (error) {
        console.error('Error loading table of contents:', error);
        document.getElementById('toc-container').innerHTML = `
            <div class="error">
                Error loading table of contents: ${error.message}
                <br>Please check that the CSV files are available and properly formatted.
            </div>
        `;
    }
}

// Initialize when the document is ready
document.addEventListener('DOMContentLoaded', initializeTableOfContents);