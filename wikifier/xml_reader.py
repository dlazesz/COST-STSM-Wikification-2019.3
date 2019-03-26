from lxml import etree
from lxml.etree import tostring
from itertools import chain


# from https://stackoverflow.com/questions/4624062/
# get-all-text-inside-a-tag-in-lxml
def stringify_children(node):
    try:
        parts = ([node.text] +
                list(chain(*([c.text, tostring(c), c.tail] for c in node.getchildren()))) +
                [node.tail])
        # filter removes possible Nones in texts and tails
        return ''.join(filter(None, parts))
    except TypeError:
        return ""


def parse_tei(path_to_file, namespaces):

    xml_tree = etree.parse(path_to_file)
    root = xml_tree.getroot()
    paragraphs = root.xpath("//tei:text//tei:p|tei:pb", namespaces=namespaces)



    return paragraphs, root
