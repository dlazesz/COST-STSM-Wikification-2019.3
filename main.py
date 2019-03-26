#!/usr/bin/python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import csv
import sys
import pygtrie

import flair
import re
from scipy.spatial import distance
import requests
from functools import lru_cache

e = flair.embeddings.BertEmbeddings('bert-base-multilingual-cased')


def init_trie():
    trie = pygtrie.StringTrie(separator=' ')
    with open('result3_mod.csv', encoding='UTF-8') as fh:
        next(fh)  # Read the header
        csvreader = csv.reader(fh, delimiter=',', quotechar='"')
        for n, (wikidata_id, name, alias) in enumerate(csvreader):
            wikidata_id = wikidata_id.rsplit('/', maxsplit=1)[1]
            # modify_trie(trie, wikidata_id, name)
            # modify_trie(trie, wikidata_id, alias)
            # Also add partial names...
            add_parts(trie, wikidata_id, name)
            add_parts(trie, wikidata_id, alias)

    return trie


def modify_trie(trie, wikidata_id, name):
    if name in trie:
        trie[name].add(wikidata_id)
    else:
        trie[name] = {wikidata_id}


def add_parts(trie, wikidata_id, name):
    if ' ' in name:
        name_parts = name.split(' ')
        for i in range(len(name_parts) + 1):
            for j in range(i + 1, len(name_parts) + 1):
                name_part = name_parts[i:j]
                partial_name = ' '.join(name_part)
                if len(partial_name) == 0:
                    continue
                if partial_name not in {'el', 'a', 'az', 'A', 'I.', 'II.', 'Az'} and partial_name[0].isupper():  # TODO Stopword filtering
                    modify_trie(trie, wikidata_id, partial_name)


def bert_stuff(buff, inp_texts):
    keyword = ' '.join(buff)
    texts = [re.sub(keyword, "<key>", text[:500]) for text in inp_texts]

    flair_texts = [flair.data.Sentence(text) for text in texts]

    for text in flair_texts:
        e.embed(text)

    text_keys = [[x.embedding.cpu().detach().numpy() for x in text if x.text.startswith('<key>')]
                 for text in flair_texts]

    text_keys = [k[0] for k in text_keys if len(k) > 0]
    sample = text_keys[-1]
    winner, _ = min(((n, distance.euclidean(sample, cand)) for n, cand in enumerate(text_keys[:-1])),
                    key=lambda x: x[1])
    return winner


@lru_cache(maxsize=10000)
def get_texts_from_wikipedia_for_entities(cands):
    n = 45  # Maximum is 50
    ent_title_dict = {}
    for cands_chunk in (cands[i:i + n] for i in range(0, len(cands), n)):
        resp = requests.get('https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&props=sitelinks&'
                            'ids={0}&sitefilter=huwiki'.format('|'.join(cands_chunk)))
        json_resp = resp.json()
        if json_resp['success'] != 1:
            print('Problem!', json_resp)
            exit(1)

        for ent_name, ent_desc in json_resp['entities'].items():
            try:
                ent_title_dict[ent_name] = ent_desc['sitelinks']['huwiki']['title']
            except KeyError:
                pass

    ent_text_dict = {}
    for ent, title in ent_title_dict.items():
        resp = requests.get('https://hu.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&explaintext&'
                            'exlimit=max&titles={0}&redirects=true'.format(title))
        json_resp = resp.json()
        ent_text_dict[ent] = '\n'.join(json_resp["query"]["pages"][x]["extract"]
                                       for x in list(json_resp["query"]["pages"]))
    return ent_text_dict


def disambiguate(sent, buff, candidates):

    if len(candidates) > 0:
        texts = []
        ind_to_id = {}
        candidates_w_text = get_texts_from_wikipedia_for_entities(tuple(candidates))
        if len(list(candidates_w_text.keys())) > 1:
            for ind, (key, val) in enumerate(candidates_w_text.items()):
                texts.append(val)
                ind_to_id[ind] = key
            n = bert_stuff(buff, [*texts, sent])
            wid = ind_to_id[n]
            return wid
        else:
            print('WARNING: ONLY ONE CANDIDATE LEFT!', file=sys.stderr)
            return list(candidates_w_text.keys())[0]
    else:
        return candidates[0]


def find_ne_in_text(trie, test):
    buffer = []
    for i, word in enumerate(test.split()):
        buffer.append(word)
        joined = ' '.join(buffer)
        if trie.has_subtrie(joined):
            pass  # Wait for it!
        elif joined in trie:
            print('_'.join(buffer), disambiguate(test, buffer, trie[joined]), sep=' (', end=') ')
            buffer = []
        elif len(buffer) > 1:  # TODO backtracking more than one step!!!
            buffer2 = buffer[:-1]
            joined = ' '.join(buffer2)
            if joined in trie:  # Second chance!
                print('_'.join(buffer2), disambiguate(test, buffer2, trie[joined]), sep=' (', end=') ')
                print(buffer[-1], end=' ')
                buffer = []
            else:
                print(*buffer, end=' ')
                buffer = []  # False partial match!
        else:
            buffer = []  # Failed
            print(word, end=' ')


def main():
    trie = init_trie()

    # test = 'My favorite mad scientist is Johannes Wierd Koopmans who invented the XXX!'
    # test = 'Én kedvenc politikus író Földes László nagy!'  # I could not create better example... :)
    test = 'Barack Obama amerikai elnök még ebben a hónapban ellátogat Hirosimába, hogy lerója tiszteletét az' \
           ' atomtámadás áldozatai előtt - jelentette be kedden a Fehér Ház. Obama az első hivatalban lévő amerikai' \
           ' elnök, aki látogatást tesz az amerikai atomtámadás sújtotta japán városban, írta az MTI.' \
           ' A bejelentést a washingtoni Fehér Ház megerősítette egy nyilatkozatban, amely szerint Obama' \
           ' ebben a hónapban, Abe Sinzó japán kormányfő oldalán egy már betervezett út során látogat el a városba.' \
           ' A sajtóban a május 27-i dátumot emlegetik.'

    find_ne_in_text(trie, test)

    """
    with open('hun_POS_5000_e-magyar.csv', encoding='UTF-8') as fh:
        next(fh)  # Read header
        sent_buffer = []
        for line in fh:
            tid, form, lemma = line.split('\t')[3:6]
            if int(tid) == 1:
                find_ne_in_text(trie, ' '.join(sent_buffer))
                sent_buffer = []
                print()
            sent_buffer.append(lemma)
    """


if __name__ == '__main__':
    main()
