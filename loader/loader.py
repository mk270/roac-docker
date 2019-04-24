#!/usr/bin/env python3

"""
   TODO: ENFORCE RESULT CHECKS

how do we enforce other checks?
"""

import csv
import json
import uuid
import argparse
from graphqlclient import GraphQLClient

import os

publishers_data = os.path.join(os.path.dirname(__file__), "publishers.json")

def nonce_uuid(): return str(uuid.uuid4())

def do_graphql(client, payload, data):
    result = client.execute(payload % data)
    if "errors" in result:
        jprint(json.loads(result))
        jprint(data)
        assert "errors" not in result

def load_publishers(client):
    payload = """
      mutation {
        createPublisher(
          input: {
            publisher: {
              publisherName: "%(name)s"
              publisherUrl: "%(url)s"
              publisherAbbrev: "%(abbrev)s"
            }
          }
        ) {
            clientMutationId
        }
      }
    """

    publishers = json.load(open(publishers_data))

    for publ in publishers:
        do_graphql(client, payload, publ)

def jprint(data):
    print(json.dumps(data, indent=2))

def save_book(client, book_data, publisher):
    #jprint(book_data)

    payload = """
      mutation {
        createBook (
          input: {
            book: {
              title: "%(title)s"
              bookUuid: "%(bookUuid)s"
              publisherName: "%(publisherName)s"
              pageCount: %(pageCount)s
            }
          }
        ) {
            clientMutationId
        }
      }
    """
    book_uuid = nonce_uuid()
    book_data['bookUuid'] = book_uuid
    book_data['publisherName'] = publisher

    do_graphql(client, payload, book_data)

    payload = """
      mutation {
        createBookDetail (
          input: {
            bookDetail: {
              bookUuid: "%(bookUuid)s"
              detailId: "%(detailId)s"
              detailValue: "%(detailValue)s"
            }
          }
        ) {
            clientMutationId
        }
      }
    """

    details = [
        "doi",
        "overview_url",
        "cover_url"
    ]
    
    for detail in details:
        detail_data = {
            "bookUuid": book_data["bookUuid"],
            "detailId": detail,
            "detailValue": book_data[detail]
        }
        do_graphql(client, payload, detail_data)

    return book_uuid

def save_contributors(client, contributors):
    payload = """
    mutation {
        createContributor (
          input: {
            contributor: {
              contributorUuid: "%(contributorUuid)s"
              contributorName: "%(contributorName)s"
              contributorBio: "%(contributorBio)s"
            }
          }
        ) {
            clientMutationId
        }
      }
    """
    uuids = {}
    for c in contributors:
        c_uuid = nonce_uuid()
        data = {
            "contributorUuid": c_uuid,
            "contributorName": c[0] + " " + c[1],
            "contributorBio": "TBD"
        }
        do_graphql(client, payload, data)
        uuids[c] = c_uuid

    return uuids

def save_contribution(client, book_uuid, contributor_uuid, role):
    payload = """
    mutation {
        createContribution (
          input: {
            contribution: {
              bookUuid: "%(bookUuid)s"
              contributorUuid: "%(contributorUuid)s"
              roleName: "%(role)s"
            }
          }
        ) {
            clientMutationId
        }
      }
    """
    data = {
        "contributorUuid": contributor_uuid,
        "bookUuid": book_uuid,
        "role": role.lower()
    }
    do_graphql(client, payload, data)

def save_publication(client, book_uuid, pub_format, pub_isbn):
    payload = """
    mutation {
        createPublication (
          input: {
            publication: {
              bookUuid: "%(bookUuid)s"
              publicationUuid: "%(publicationUuid)s"
              format: "%(format)s"
              isbn: "%(isbn)s"
            }
          }
        ) {
            clientMutationId
        }
      }
    """
    data = {
        "bookUuid": book_uuid,
        "publicationUuid": nonce_uuid(),
        "format": pub_format,
        "isbn": pub_isbn
    }
    do_graphql(client, payload, data)

def load_obp_books(client, data_file):
    book_uuids = {}

    columns = {
        "Title": "title",
        "Subtitle": "subtitle",
        "DOI prefix": "doiPrefix",
        "DOI suffix": "doiSuffix",
        "no of pages": "pageCount",
        "Cover URL": "cover_url",
        "Book-page URL": "overview_url"
    }

    # note duplicated fn below
    def get_books():
        r = csv.DictReader(open(data_file))
        row_id = 0
        for row in r:
            data = dict([ (v, row[k]) for k, v in columns.items() ])
            if data['doiSuffix'] == "":
                continue
            row_id += 1
            data['doi'] = data['doiPrefix'] + '/' + data['doiSuffix']
            data['row_id'] = row_id
            data['row'] = row
            yield data

    for data in get_books():
        book_uuid = save_book(client, data, "Open Book Publishers")
        book_uuids[data["row_id"]] = book_uuid

    def contributors_from_row(row):
        for contributor in range(0, 6):
            offset = contributor * 7 + 5
            first_name = row[offset]
            last_name  = row[offset + 1]
            role       = row[offset + 2]
            if first_name == "" or last_name == "" or role == "":
                continue
            yield (first_name, last_name, role)

    def get_contributors():
        r = csv.reader(open(data_file))
        for row in r:
            if row[0] in ["", "Title"]:
                continue
            for c in contributors_from_row(row):
                yield c

    contributors = frozenset([ (c[0], c[1]) for c in get_contributors() ])
    contributor_uuids = save_contributors(client, contributors)

    def get_books_no_dict():
        r = csv.reader(open(data_file))
        row_id = 0
        for row in r:
            if row[0] in ["", "Title"]:
                continue
            row_id += 1
            yield row_id, row

    def get_contributions():
        for row_id, row in get_books_no_dict():
            for c in contributors_from_row(row):
                key = (c[0], c[1])
                c_uuid = contributor_uuids[key]
                b_uuid = book_uuids[row_id]
                role = c[2]
                yield (b_uuid, c_uuid, role)

    for contribution in get_contributions():
        save_contribution(client, *contribution)

    def publications_from_row(row):
        for pub in range(0, 5):
            offset = pub * 3 + 47
            pub_format = row[offset].lower().strip()
            pub_isbn   = row[offset + 1]
            if pub_format == "" or pub_isbn == "":
                continue
            if len(pub_isbn) > 13:
                continue
            yield (pub_format, pub_isbn)

    def get_publications():
        for row_id, row in get_books_no_dict():
            for pub_format, pub_isbn in publications_from_row(row):
                save_publication(client, book_uuids[row_id],
                                 pub_format, pub_isbn)

    get_publications()

def run(client, data_file):
    load_publishers(client)
    load_obp_books(client, data_file)

def unwrap_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="metadata CSV input file path",
                        default="all-book-metadata.csv")
    parser.add_argument("--base-url", help="GraphQL endpoint URL",
                        default="http://localhost:41962/graphql")
    args = parser.parse_args()
    client = GraphQLClient(args.base_url)
    run(client, args.file)

if __name__ == '__main__':
    unwrap_args()
