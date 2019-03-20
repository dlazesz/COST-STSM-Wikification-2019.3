#!/usr/bin/python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import csv

from collections import defaultdict, Counter

d = defaultdict(set)
b = defaultdict(set)
with open('result3_mod.csv', encoding='UTF-8') as fh:
    next(fh)  # Read the header
    csvreader = csv.reader(fh, delimiter=',', quotechar='"')
    for rec in csvreader:
        try:
            wikidata_id, name, alias = rec
        except:
            print(rec)
            exit(1)
        wikidata_id = wikidata_id.rsplit('/', maxsplit=1)[1]
        if False and ' ' in name:  # DISABLE PARTIAL NAME MATCHING!
            name_parts = name.split(' ')
            for i in range(1, len(name_parts)+1):
                partial_name = ' '.join(name_parts[:i])
                d[partial_name].add(wikidata_id)
                b[wikidata_id].add(partial_name)
        else:
            d[name].add(wikidata_id)
            b[wikidata_id].add(name)

        if False and ' ' in alias:  # DISABLE PARTIAL NAME MATCHING!
            alias_parts = alias.split(' ')
            for i in range(1, len(alias_parts)+1):
                partial_alias = ' '.join(alias_parts[:i])
                d[partial_alias].add(wikidata_id)
                b[wikidata_id].add(partial_alias)
        else:
            d[alias].add(wikidata_id)
            b[wikidata_id].add(alias)

duplicate = 0
singlicate = 0
maximum = 0
for k, v in d.items():
    maximum = max(len(v), maximum)
    if len(v) > 1:
        duplicate += 1
        c = Counter()
        for wid in v:
            for e in b[wid]:
                c[e] += 1
        double = [(ke, va) for ke, va in c.items() if va > 1]
        # if len(v) > 20:
        print(len(v), k, v, double)
    else:
        singlicate += 1
        # print(len(v), k, v, None)
print(len(d), len(b), duplicate, singlicate, maximum)
