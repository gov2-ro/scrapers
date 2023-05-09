import json
from bs4 import BeautifulSoup
from lxml import etree

def html_to_json_obj(html_string):
    # parse the HTML string using lxml
    root = etree.fromstring(html_string)

    # recursively convert the tree to a JSON object
    def element_to_dict(element):
        # create a dictionary for the current element
        result = {
            'tag': element.tag,
            'attrs': dict(element.attrib),
            'kids': []
        }

        # add the children of the element
        for child in element.iterchildren():
            result['kids'].append(element_to_dict(child))

        return result

    # convert the root element to a dictionary and return as JSON
    # return json.dumps(element_to_dict(root)) 
    return element_to_dict(root) 
 
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

def node_to_dict(node):
    rr = {}
    if node.name is None:
        rr['tag'] = "_self"
        if node.strip():
            rr['text']= node.strip()
        return rr 
    else:
        node_dict = {"tag": node.name.lower()}
        if node.attrs:
            node_dict["attrs"] = node.attrs
        children = {}
        for i, child_node in enumerate(node.contents):
            if child_node.name or (child_node.strip() != ''):
                child_node_dict = node_to_dict(child_node)
                if child_node_dict:
                    children[str(i)] = child_node_dict
        if children:
            node_dict["children"] = children
        return node_dict


def html_to_json_obzx(html_str):
    soup = BeautifulSoup(html_str, 'html.parser')
    return {str(i): node_to_dict(node) for i, node in enumerate(soup.contents)}

def html2obj(inputsoup, ignore_keys):
    zijson = html_to_json_obzx(str(inputsoup))
    zijson = remove_keys(zijson, ignore_keys)
    zijson = remove_empty_elements(zijson)
    return zijson

""" 
# test 

htmlstr = '''
 xx <b>asa s</b> <ul><li>ss1</li><li>ss1 <em><b>rrs ss</b></em> lala  </li></ul> this <u>those</u> that  
'''
zz = html_to_json_obzx(htmlstr)
print(json.dumps(zz, ensure_ascii=False)) """