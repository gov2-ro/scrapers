import json

# Load the data from the context file
lang = "ro"
with open('data/1-indexes/' +lang +'/context.json') as f:
    data = json.load(f)

# Organize the data into a dictionary for easy lookup
items_by_code = {item['context']['code']: item for item in data}

# Function to build the hierarchy recursively
def build_hierarchy(item):
    children = [build_hierarchy(child) for child in data if child['parentCode'] == item['context']['code']]
    item['children'] = children
    return item

# Build the hierarchical structure starting from the root nodes (parentCode == "0")
hierarchical_data = [build_hierarchy(item) for item in data if item['parentCode'] == "0"]

# Output the hierarchical JSON
hierarchical_json = json.dumps(hierarchical_data, indent=2, ensure_ascii=False)
# print(hierarchical_json)

with open("data/1-indexes/"+ lang +"/context-hierachical.json", "w") as file:
    file.write(hierarchical_json)