#!/usr/bin/env python3

import csv
import urllib.request

with open("repos.csv", encoding="utf-8") as csvfile:
    urls = set()
    for row in csv.DictReader(csvfile):
        if row["homepage_url"]:
            urls.add(row["homepage_url"])

for url in urls:
    req = urllib.request.Request(url, method="HEAD")
    try:
        resp = urllib.request.urlopen(req)
    except urllib.error.HTTPError:
        print(url)
