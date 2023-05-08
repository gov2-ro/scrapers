import json
from bs4 import BeautifulSoup
from lxml import etree

inputfile ='../../data/cdep/sample/Pl-x nr. 8_2010.html'
target ='../../data/cdep/sample/Pl-x nr. 8_2010.json'
ignore_keys = ['width', 'cellspacing', 'cellpadding', 'border', 'style', 'valign', 'height', 'colspan', 'align', 'nowrap', 'bgcolor']

def html_to_json_obj(html_string):
    # parse the HTML string using lxml
    root = etree.fromstring(html_string)

    # recursively convert the tree to a JSON object
    def element_to_dict(element):
        # create a dictionary for the current element
        result = {
            'tag': element.tag,
            'attrs': dict(element.attrib),
            'children': []
        }

        # add the children of the element
        for child in element.iterchildren():
            result['children'].append(element_to_dict(child))

        return result

    # convert the root element to a dictionary and return as JSON
    # return json.dumps(element_to_dict(root)) 
    return element_to_dict(root) 

def readfile(path):
    encodings = ['utf-8', 'ISO-8859-1', 'cp1252']

    for encoding in encodings:
        try:
            with open(path, 'r', encoding=encoding) as file:
                text = file.read()
                break
        except UnicodeDecodeError:
            continue
    return text

def writefile(path, content):
    with open(path, 'w') as f:
        f.write(content)

def remove_empty_keys(data):
    # load the JSON string into a dictionary
    # data = json.loads(json_string)

    # recursively remove empty keys from the dictionary
    def remove_empty_keys_recursive(obj):
        if isinstance(obj, dict):
            # iterate over a copy of the dictionary to avoid modifying it during iteration
            for key, value in list(obj.items()):
                # remove the key if the value is empty
                if not value:
                    del obj[key]
                # recursively remove empty keys from nested objects
                else:
                    remove_empty_keys_recursive(value)
        elif isinstance(obj, list):
            # recursively remove empty keys from all items in the list
            for item in obj:
                remove_empty_keys_recursive(item)

    # remove empty keys from the dictionary
    remove_empty_keys_recursive(data)

    # convert the dictionary back to a JSON string and return it
    return json.dumps(data)

def remove_empty(obj):
    if isinstance(obj, dict):
        return {
            k: remove_empty(v) for k, v in obj.items() if v and remove_empty(v)
        }
    elif isinstance(obj, list):
        return [remove_empty(elem) for elem in obj if elem and remove_empty(elem)]
    else:
        return obj
def remove_empty_iterative(obj):
    stack = [obj]
    while stack:
        item = stack.pop()
        if isinstance(item, dict):
            for k, v in list(item.items()):
                if not v or len(v)==0:
                    del item[k]
                elif isinstance(v, (dict, list)):
                    stack.append(v)
        elif isinstance(item, list):
            for i, elem in reversed(list(enumerate(item))):
                if not elem or len(v)==0:
                    del item[i]
                elif isinstance(elem, (dict, list)):
                    stack.append(elem)
    return obj

def remove_keysz(json_obj, keys_to_remove):
    # list of keys to remove
    # remove nodes with keys from the list
    for key in keys_to_remove:
        json_obj.pop(key, None)
    return json_obj


def remoove_mpty(data):
    def delete_emtpy_from_l(l):
        len0 = len(l)
        l[:] = [d for d in l if 'value' in d and d['value'] != 'None' or d['sections']]
        cnt = len0 - len(l)
        for d in l:
            cnt += delete_emtpy_from_l(d['sections'])
        # cnt is how many dict are deleted
        return cnt


    # loop until no new dict is deleted
    while delete_emtpy_from_l(data):
        pass
    return data

def remove_empty_elements(d):
    """recursively remove empty lists, empty dicts, or None elements from a dictionary"""

    def empty(x):
        return x is None or x == {} or x == []

    if not isinstance(d, (dict, list)):
        return d
    elif isinstance(d, list):
        return [v for v in (remove_empty_elements(v) for v in d) if not empty(v)]
    else:
        return {k: v for k, v in ((k, remove_empty_elements(v)) for k, v in d.items()) if not empty(v)}

def remove_keys(json_obj, keys_to_remove):
    """
    Recursively remove nodes with keys from a JSON object
    """
    if isinstance(json_obj, dict):
        # loop through all keys in the dictionary
        for key in list(json_obj.keys()):
            # if the key is in the list of keys to remove, delete it
            if key in keys_to_remove:
                del json_obj[key]
            # if the value associated with the key is itself a dictionary or a list, recursively call the function
            elif isinstance(json_obj[key], (dict, list)):
                remove_keys(json_obj[key], keys_to_remove)
    elif isinstance(json_obj, list):
        # loop through all elements in the list
        for item in json_obj:
            # if the element is a dictionary or a list, recursively call the function
            if isinstance(item, (dict, list)):
                remove_keys(item, keys_to_remove)
    return json_obj

soup = BeautifulSoup(readfile(inputfile), 'html.parser')
derulare_procedura = soup.find("div", {"id": "olddiv"}).find("table", recursive=False)
zijson = html_to_json_obj(str(derulare_procedura))
zijson = remove_keys(zijson, ignore_keys)
zijson = remove_empty_elements(zijson)

writefile(target, json.dumps(zijson))

