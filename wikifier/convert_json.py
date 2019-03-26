import json
import numpy as np

def to_xml(json_response):

    data = json.loads(json_response)
    info = data["ranges"]
    words_used = [x["wordsUsed"] for x in info]
    out = "<test>"
    words = data["words"]
    full_view = []
    for w in words:
        if w in words_used:
            full_view.append([x for x in info if x["wordsUsed"] == w])
        else:
            full_view.append(w)

    for word in full_view:

        if isinstance(word, str):
            out += "<w>"+word+"</w>"

        best_match = [[float(x["cosine"]),
                       float(x["pageRank"]),
                       x["title"],
                       x["url"]] for x in word["candidates"]][0]

        if best_match[1] > 0.01:
            out+="<w wiki_title=\'"+str(best_match[2])+"\' wiki_url=\'"+str(best_match[2])+"\'>"+str(word["wordsUsed"][0])+"</w>"
        else:
            out+="<w>"+str(word["wordsUsed"][0])+"</w>"
    out+="</test>"
    return out
