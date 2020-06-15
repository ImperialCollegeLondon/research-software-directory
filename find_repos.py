#!/usr/bin/env python3

import csv
import datetime
import os
import re
import time

from github import Github

with open("repos.csv", encoding="utf-8") as csvfile:
    owners = set()
    urls = set()
    for row in csv.DictReader(csvfile):
        urls.add(row["url"])
        m = re.search("github.com/(.+)/", row["url"])
        if m:
            owners.add(m.group(1))


EXCLUDED_OWNERS = (
    "brian-team",
    "DRMacIver",
    "JuliaArrays",
    "JuliaMatrices",
    "Kaixhin",
    "ropensci",
    "tensorlayer",
)
EXCLUDED_REPOS = (
    "https://github.com/DRMacIver/hecate",
    "https://github.com/ImperialCollegeLondon/csml-reading-group",
    "https://github.com/ImperialCollegeLondon/group-theory-game",
    "https://github.com/ImperialCollegeLondon/M40001_lean",
    "https://github.com/ImperialCollegeLondon/M4P33",
    "https://github.com/ImperialCollegeLondon/natural_number_game",
    "https://github.com/ImperialCollegeLondon/real-number-game",
    "https://github.com/ImperialCollegeLondon/xena-UROP-2018",
    "https://github.com/johnlees/seer",
    "https://github.com/klee/klee-uclibc",
    "https://github.com/klee/klee-web",
    "https://github.com/klee/klee.github.io",
    "https://github.com/mp3guy/Stopwatch",
    "https://github.com/mrc-ide/COVID19_CFR_submission",
    "https://github.com/pawni/gpuobserver",
    "https://github.com/su2code/su2code.github.io",
    "https://github.com/su2code/TestCases",
)
MAXIMUM_DAYS = 365
MINIMUM_STARS = 10

g = Github(os.environ["PUBLIC_GITHUB_TOKEN"])
for owner in owners - set(EXCLUDED_OWNERS):
    time.sleep(5)
    date = datetime.datetime.now() - datetime.timedelta(days=MAXIMUM_DAYS)
    for repo in g.search_repositories(
        f"user:{owner} stars:>{MINIMUM_STARS} pushed:>{date.isoformat().split('T')[0]}"
    ):
        if repo.html_url not in urls and repo.html_url not in EXCLUDED_REPOS:
            print(f"{owner} {repo.name} {repo.html_url}")
            time.sleep(5)
