import os
import uuid
import json
import sys

publishers_data = os.path.join(os.path.dirname(__file__), "publishers.json")

def nonce_uuid(): return str(uuid.uuid4())

def do_graphql(client, payload, data):
    def report_errors(result):
        jprint(json.loads(result))
        jprint(data)
        print(payload, file=sys.stderr)

    try:
        request = payload % data
        result = client.execute(request)
        if "errors" in result:
            report_errors(result)
            assert "errors" not in result
    except:
        print("ERROR", file=sys.stderr)
        report_errors({})
        raise

def quote(s):
    tmp = s.replace("\n", "\\n")
    return tmp.replace('"', '''\\"''')

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

def save_book(client, book_data, publisher, details):
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
              langCode: "%(languageCode)s"
              edition: %(edition)s
              copyrightHolder: "%(copyrightHolder)s"
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
    book_data['copyrightHolder'] = quote(book_data['copyrightHolder'])

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
    publication_uuid = nonce_uuid()
    data = {
        "bookUuid": book_uuid,
        "publicationUuid": publication_uuid,
        "format": pub_format,
        "isbn": pub_isbn
    }
    do_graphql(client, payload, data)
    return publication_uuid

def save_price(client, publication_uuid, currency, price):
    payload = """
    mutation {
        createPublicationPrice (
          input: {
            publicationPrice: {
              publicationUuid: "%(publicationUuid)s"
              currencyCode: "%(currency)s"
              listPrice: "%(listPrice)s"
            }
          }
        ) {
            clientMutationId
        }
      }
    """
    data = {
        "publicationUuid": publication_uuid,
        "currency": currency,
        "listPrice": str(price)
    }
    do_graphql(client, payload, data)

def save_imprint(client, imprint_name, publisher_name):
    payload = """
    mutation {
        createImprint (
          input: {
            imprint: {
              imprintName: "%(imprintName)s"
              publisherName: "%(publisherName)s"
            }
          }
        ) {
            clientMutationId
        }
      }
    """
    data = {
        "publisherName": publisher_name,
        "imprintName": imprint_name
    }
    do_graphql(client, payload, data)

def save_imprint_volume(client, book_uuid, imprint_name):
    payload = """
    mutation {
        createImprintVolume (
          input: {
            imprintVolume: {
              bookUuid: "%(bookUuid)s"
              imprintName: "%(imprintName)s"
            }
          }
        ) {
            clientMutationId
        }
      }
    """
    data = {
        "bookUuid": book_uuid,
        "imprintName": imprint_name
    }
    do_graphql(client, payload, data)

def save_series(client, issn1, issn2, series_name):
    payload = """
    mutation {
        createSeries (
          input: {
            series: {
              seriesUuid: "%(seriesUuid)s"
              seriesName: "%(seriesName)s"
              seriesIssnPrint: "%(seriesIssnPrint)s"
              seriesIssnDigital: "%(seriesIssnDigital)s"
            }
          }
        ) {
            clientMutationId
        }
      }
    """
    series_uuid = nonce_uuid()
    data = {
        "seriesUuid": series_uuid,
        "seriesName": series_name,
        "seriesIssnPrint": issn1,
        "seriesIssnDigital": issn2
    }
    do_graphql(client, payload, data)
    return series_uuid

def save_series_volume(client, book_uuid, series_uuid, volume_ordinal):
    payload = """
    mutation {
        createSeriesVolume (
          input: {
            seriesVolume: {
              seriesUuid: "%(seriesUuid)s"
              bookUuid: "%(bookUuid)s"
              volumeOrdinal: %(volumeOrdinal)s
            }
          }
        ) {
            clientMutationId
        }
      }
    """
    data = {
        "seriesUuid": series_uuid,
        "bookUuid": book_uuid,
        "volumeOrdinal": volume_ordinal
    }
    do_graphql(client, payload, data)

def save_keyword(client, book_uuid, keyword, idx):
    payload = """
    mutation {
        createBookKeyword (
          input: {
            bookKeyword: {
              bookUuid: "%(bookUuid)s"
              keywordText: "%(keywordText)s"
              keywordOrdinal: %(keywordOrdinal)s
            }
          }
        ) {
            clientMutationId
        }
      }
    """
    data = {
        "bookUuid": book_uuid,
        "keywordText": keyword,
        "keywordOrdinal": idx
    }
    do_graphql(client, payload, data)

def save_subject(client, subject_scheme, subject_name):
    payload = """
    mutation {
        createSubject (
          input: {
            subject: {
              subjectCode: "%(subjectCode)s"
              subjectSchemeName: "%(subjectScheme)s"
            }
          }
        ) {
            clientMutationId
        }
      }
    """
    data = {
        "subjectCode": subject_name,
        "subjectScheme": subject_scheme
    }
    do_graphql(client, payload, data)

def save_book_subject(client, book_uuid, subject_scheme, subject_name):
    payload = """
    mutation {
        createBookSubject (
          input: {
            bookSubject: {
              bookUuid: "%(bookUuid)s"
              subjectCode: "%(subjectCode)s"
              subjectSchemeName: "%(subjectScheme)s"
            }
          }
        ) {
            clientMutationId
        }
      }
    """
    data = {
        "bookUuid": book_uuid,
        "subjectCode": subject_name,
        "subjectScheme": subject_scheme
    }
    do_graphql(client, payload, data)
