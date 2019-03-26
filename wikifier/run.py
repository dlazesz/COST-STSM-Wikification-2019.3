from helpers import *
from xml_reader import *
from convert_json import *
import requests
import time


declared_namespaces = {"tei": "http://www.tei-c.org/ns/1.0"}

files_to_process = get_files_from_dir("in_folder")
responses = []
for file_path in files_to_process:

    paragraphs, root = parse_tei(file_path, declared_namespaces)
    i = 0
    for paragraph in paragraphs:
        i+=1

        pbs = paragraph.xpath("tei:pb", namespaces=declared_namespaces)

        pbs_texts = [x.tail for x in pbs]
        pbs_texts = " ".join(pbs_texts)
        query_text = paragraph.text +" "+ pbs_texts

        response = requests.get('http://www.wikifier.org/annotate-article?text='+query_text+'&lang=ger&userKey=kawbiukxqhytgbycxqjketxmsjlpli')

        for p in pbs:
            p.tail = None

        xml_resp = to_xml(response.text)
        paragraph.append(etree.fromstring(xml_resp))
        paragraph.text = None

        responses.append(xml_resp)
        time.sleep(2)

etree.ElementTree(root).write('test.xml', pretty_print=True)
with open("outfile", "w") as f:
    f.write("\n".join(responses))
