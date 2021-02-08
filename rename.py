# -*- coding: utf-8 -*-

import requests
import PyPDF2
import os
import json

from refextract import extract_references_from_file


def get_doi_web(pdf):
    url = "https://ref.scholarcy.com/api/references/extract"
    files = {
        "file": open(pdf, "rb")
    }
    try:
        res = requests.post(url, files=files)
        doi = res.json()["metadata"]["doi"]
    except Exception as e:
        raise SystemExit(e)
    return doi


def get_doi_reader(pdf):
    reader = PyPDF2.PdfFileReader(open(pdf, "rb"))
    doi = None
    for k, v in reader.documentInfo.items():
        if "doi" in k:
            doi = v
            break

    if doi is None:
        raise ValueError("Bad pdf structure, no doi found.")
    return doi


def get_ref_doi(doi: str) -> dict:
    cross_ref = "http://api.crossref.org/works/"
    url = cross_ref + doi

    try:
        res = requests.get(url)
        item = res.json()
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    return item["message"]


def rename(pdf: str):
    dir_name = os.path.dirname(pdf)
    doi = get_doi_web(pdf)
    msg = get_ref_doi(doi)
    # print(item)
    with open("./out.json", 'w') as f:
        json.dump(msg, f, indent=4)

    year = msg["created"]["date-parts"][0][0] % 100
    auth = "None"
    for i in msg["author"]:
        if i["sequence"] == "first":
            auth = i["family"]
            break
    if msg["short-container-title"]:
        abbr = msg["short-container-title"][0]
    else:
        abbr = "".join([i[0] if i[0].isupper() else "" for i in msg["container-title"][0].split(" ")])
    title = ""
    if msg["title"]:
        title = "".join([i[:3] if i[0].isupper() else "" for i in msg["title"][0].split(" ")])

    name = "{}{}_{}_{}.pdf".format(auth, year, title, abbr)

    print(name)
    print(dir_name)
    # abbreviated_journal = item["message"]
    # year = item["message"]["created"]["date-parts"][0][0]
    # volume = item["message"]["volume"]
    # page = item["message"]["page"]

    # # format: abbreviated_journal year, volume, page.pdf
    # name = "{} {}, {}, {}".format(abbreviated_journal, year, volume, page)

    os.rename(pdf, os.path.join(dir_name, name))


if __name__ == "__main__":
    ff = "/Users/hackroid/Downloads/pp.pdf"

    # getting ref from a paper
    # references = extract_references_from_file(ff)

    # renaming a paper
    rename(ff)
