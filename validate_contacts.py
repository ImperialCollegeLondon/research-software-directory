#!/usr/bin/env python3

import csv
import re

import ldap
import ldap.filter

with open("repos.csv", encoding="utf-8") as csvfile:
    emails = set()
    for row in csv.DictReader(csvfile):
        m = re.search("<(.*)>", row["contact"])
        if m:
            emails.add(m.group(1))

EXCLUDED_EMAILS = ("iclocs@imperial.ac.uk",)

ldap_conn = ldap.initialize("ldaps://unixldap.cc.ic.ac.uk")
for email in emails:
    if email not in EXCLUDED_EMAILS and not ldap_conn.search_s(
        "ou=People,ou=shibboleth,dc=ic,dc=ac,dc=uk",
        ldap.SCOPE_SUBTREE,
        "mail=%s" % ldap.filter.escape_filter_chars(email, 1),
    ):
        print(email)
