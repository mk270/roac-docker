
import os
import uuid
import json
import sys

publishers_data = os.path.join(os.path.dirname(__file__), "publishers.json")

def nonce_uuid(): return str(uuid.uuid4())

def do_graphql(client, payload, data):
    result = client.execute(payload % data)
    if "errors" in result:
        jprint(json.loads(result))
        jprint(data)
        assert "errors" not in result

def quote(s):
    return s.replace('"', '''\\"''')

def save_publishers(client, publisher_name):
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
        if publ["name"] == publisher_name:
            do_graphql(client, payload, publ)

def jprint(data):
    print(json.dumps(data, indent=2), file=sys.stderr)

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
    book_data['title'] = quote(book_data['title'])

    try:
        do_graphql(client, payload, book_data)
    except:
        jprint(book_data)
        jprint(payload)
        raise

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
            "detailValue": quote(book_data[detail])
        }
        try:
            do_graphql(client, payload, detail_data)
        except:
            jprint(detail_data)
            raise

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
            "contributorName": quote(c[0] + " " + c[1]),
            "contributorBio": "TBD"
        }
        try:
            do_graphql(client, payload, data)
        except:
            jprint(data)
            raise
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
