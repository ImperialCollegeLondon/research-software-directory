# !/usr/bin/env python3

import csv
import datetime
import json
import operator
import os
import re
import sys
import urllib.request
from contextlib import suppress
from hashlib import md5

import emoji
import gitlab
from algoliasearch.search_client import SearchClient
from github import Github
from github.GithubException import UnknownObjectException


def get_license(repo):
    with suppress(UnknownObjectException):
        return repo.get_license().license.spdx_id


def get_doi(repo_url):
    # e.g. http://api.citeas.org/product/https://github.com/mwoodbri/MRIdb
    with urllib.request.urlopen(f"http://api.citeas.org/product/{repo_url}") as f:
        encoding = f.info().get_content_charset("utf-8")
        data = json.loads(f.read().decode(encoding))
        return data["metadata"].get("DOI", None)


# def get_commits(repo):
#     with suppress(GithubException):
#         return r.get_commits().totalCount
#     return 0

if len(sys.argv) > 1:
    REPOS = {
        sys.argv[1]: {
            "funders": [],
            "doi": None,
            "organisations": [],
            "contact": None,
            "licence": None,
            "homepage_url": None,
            "rsotm": None,
        }
    }
else:
    with open("repos.csv", encoding="utf-8") as csvfile:
        REPOS = {
            row["url"]: {
                **row,
                "funders": list(filter(None, row["funders"].split(";"))),
                "organisations": list(filter(None, row["organisations"].split(";"))),
            }
            for row in csv.DictReader(csvfile)
        }

repos = []

g = Github(os.environ["PUBLIC_GITHUB_TOKEN"])

for u, v in REPOS.items():
    m = re.match("(.*)/(.+/.+)", u)
    if "github.com" in m.group(1):
        r = g.get_repo(m.group(2))  # https://developer.github.com/v3/repos/#get
        repo = dict(
            name=r.name,
            owner_name=r.owner.name,
            owner_urn=f"github.com:{r.owner.login}",  # TODO
            # organisation=r.organization.name if r.organization else None,
            created_at=r.created_at,
            updated_at=r.pushed_at,
            language=r.language,
            topics=r.get_topics(),
            # is_fork=r.fork,
            # direct_collaborators_count=r.get_collaborators("direct").totalCount,
            stars_count=r.stargazers_count,
            license=v["licence"] or get_license(r),
            # outside_collaborators_count=r.get_collaborators("outside").totalCount,
            commits_count=r.get_commits().totalCount,
            contributors_count=r.get_contributors().totalCount,
            repo_url=r.html_url,
            description=emoji.emojize(r.description, use_aliases=True)
            if r.description
            else None,
            homepage_url=v["homepage_url"] or r.homepage,
            forks_count=r.forks_count,
            # watchers_count=r.subscribers_count,
            issues_count=r.open_issues_count,
            # downloads_count=r.get_downloads().totalCount,
            releases_count=r.get_releases().totalCount,
            # readme=r.get_readme().decoded_content,
            doi=v["doi"] or get_doi(r.html_url),
            urn=f"github.com:{r.id}",
        )
    else:
        with gitlab.Gitlab(m.group(1)) as gl:
            p = gl.projects.get(
                m.group(2)
            )  # https://gitlab.nektar.info/api/v4/projects/2/
            repo = dict(
                name=p.attributes["name"],
                owner_name=p.namespace["name"],
                owner_urn=f"gitlab.nektar.info:{p.namespace['path']}",
                created_at=datetime.datetime.fromisoformat(p.created_at[:-1]),
                updated_at=datetime.datetime.fromisoformat(p.last_activity_at[:-1]),
                language=max(p.languages().items(), key=operator.itemgetter(1))[0],
                topics=p.tag_list,
                # is_fork=False,  # TODO
                stars_count=p.star_count,
                license=v["licence"],
                commits_count=p.commits.list(as_list=False).total,
                contributors_count=len(p.repository_contributors()),
                repo_url=p.web_url,
                description=p.description,
                homepage_url=v["homepage_url"],
                forks_count=p.forks_count,
                # watchers_count=0,  # TODO NA?
                issues_count=p.issues.list(as_list=False).total,
                # downloads_count=0,  # TODO NA
                releases_count=p.releases.list(as_list=False).total,
                doi=v["doi"] or get_doi(p.web_url),
                urn=f"gitlab.nektar.info:{p.id}",
            )
    repo.update(
        objectID=md5(repo["urn"].encode()).hexdigest()[:8],
        inactive=datetime.datetime.now() - repo["updated_at"]
        > datetime.timedelta(days=365),
        # Imperial College London: https://www.grid.ac/institutes/grid.7445.2
        organisations=["grid.7445.2"] + v["organisations"],
        # EPSRC: https://search.crossref.org/funding?q=501100000266
        # MRC: https://search.crossref.org/funding?q=501100000265
        # Wellcome Trust: https://search.crossref.org/funding?q=100010269
        funders=v["funders"],
        contact=v["contact"],
        rsotm=v["rsotm"],
    )
    repos.append(repo)

if "ALGOLIA_APPLICATION_ID" in os.environ:
    client = SearchClient.create(
        os.environ["ALGOLIA_APPLICATION_ID"], os.environ["ALGOLIA_ADMIN_KEY"]
    )
    index = client.init_index("software_showcase")
    index.save_objects(repos)
else:
    json.dump(
        repos,
        sys.stdout,
        indent=4,
        default=lambda x: f"{x.isoformat()}Z"
        if isinstance(x, datetime.datetime)
        else None,
    )
