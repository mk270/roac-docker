import csv
import roac_client

class BookLoader:
    # self.book_uuids starts off as an empty dict
    # it is supposed to map X to Y
    # where X and Y are
    # X: int, a row_id
    # Y: str, a uuid
    # the uuid is generated when the book is saved to graphql, and only
    # then cached in book_uuids


    def __init__(self, client, data_file, publisher_name, max_books):
        self.client = client
        self.data_file = data_file
        self.book_uuids = {}
        self.contributor_uuids = frozenset([])
        self.publisher_name = publisher_name
        self.max_books = max_books

    def setup_column_mapping(self):
        return {
            "Title": "title",
            "Subtitle": "subtitle",
            "DOI prefix": "doiPrefix",
            "DOI suffix": "doiSuffix",
            "no of pages": "pageCount",
            "Cover URL": "cover_url",
            "Book-page URL": "overview_url",
            "ONIX Language Code": "languageCode",
            "edition number (integers only)": "edition",
            "Copyright holder 1": "copyrightHolder"
        }

    def load(self):
        for data in self.get_books():
            book_uuid = roac_client.save_book(self.client, data,
                                              self.publisher_name)
            self.book_uuids[data["row_id"]] = book_uuid

        contributors = frozenset([ (c[0], c[1])
                                   for c in self.get_contributors() ])

        self.contributor_uuids = roac_client.save_contributors(self.client,
                                                               contributors)

        for contribution in self.get_contributions():
            roac_client.save_contribution(self.client, *contribution)

        self.get_publications()

    def skip_row(self, data):
        return False

    def skip_row_no_dict(self, row):
        return False

    def get_doi(self, data, raw_data):
        return raw_data['DOI']

    def get_copyright_holders(self, data):
        assert False # unimplemented

    # note duplicated fn below
    def get_books(self):
        columns = self.setup_column_mapping()
        r = csv.DictReader(open(self.data_file))
        row_id = 0
        for row in r:
            data = dict([ (v, row[k]) for k, v in columns.items() ])
            if self.skip_row(data):
                continue
            row_id += 1
            if self.max_books:
                if row_id > self.max_books:
                    break
            data['doi'] = self.get_doi(data, row)
            data['copyrightHolder'] = self.get_copyright_holders(row)
            data['languageCode'] = data['languageCode'][:3] ## FIXME
            data['row_id'] = row_id
            data['row'] = row
            yield data

    def contributors_from_row(self, row):
        assert False
        for contributor in range(0, 6):
            first_name = "Unimplemented"
            last_name  = "Unimplemented"
            role       = "Author"
            if first_name == "" or last_name == "" or role == "":
                continue
            yield (first_name, last_name, role)

    def get_contributors(self):
        r = csv.reader(open(self.data_file))
        row_id = 0
        for row in r:
            if self.skip_row_no_dict(row):
                continue
            row_id += 1
            if self.max_books:
                if row_id > self.max_books:
                    break
            for c in self.contributors_from_row(row):
                yield c

    def get_books_no_dict(self):
        r = csv.reader(open(self.data_file))
        discard_header = r.__next__() # sic
        row_id = 0
        for row in r:
            if self.skip_row_no_dict(row):
                continue
            row_id += 1
            if self.max_books:
                if row_id + 1 > self.max_books:
                    break
            yield row_id, row

    def get_contributions(self):
        for row_id, row in self.get_books_no_dict():
            for c in self.contributors_from_row(row):
                key = (c[0], c[1])
                c_uuid = self.contributor_uuids[key]
                b_uuid = self.book_uuids[row_id]
                role = c[2]
                yield (b_uuid, c_uuid, role)

    def publications_from_row(self, row):
        for pub in range(0, 5):
            offset = pub * 3 + 47
            pub_format = row[offset].lower().strip()
            pub_isbn   = row[offset + 1]
            if pub_format == "" or pub_isbn == "":
                continue
            if len(pub_isbn) > 13:
                continue
            yield (pub_format, pub_isbn)

    def get_publications(self):
        for row_id, row in self.get_books_no_dict():
            for pub_format, pub_isbn in self.publications_from_row(row):
                roac_client.save_publication(self.client,
                                             self.book_uuids[row_id],
                                             pub_format,
                                             pub_isbn)

