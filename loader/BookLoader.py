import sys
import csv
import roac_client
import codelists
import decimal

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
        self.publication_uuids = {}
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
            "Copyright holder 1": "copyrightHolder",
            "Short Blurb (less than 100 words)": "short_blurb"
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

        self.get_prices()

        self.get_imprints()

    def skip_row(self, data):
        return False

    def skip_row_no_dict(self, row):
        return False

    def get_doi(self, data, raw_data):
        return raw_data['DOI']

    def get_copyright_holders(self, data):
        assert False # unimplemented

    def get_imprint(self, data, raw_data):
        assert False # unimplemented

    def get_series_ids(self, data, raw_data):
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
            data['imprint'] = self.get_imprint(data, row)
            data['series_ids'] = self.get_series_ids(data, row)
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
        discard_header = r.__next__() # sic
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
                book_uuid = self.book_uuids[row_id]
                u = roac_client.save_publication(self.client,
                                                 book_uuid,
                                                 pub_format,
                                                 pub_isbn)
                assert (book_uuid, pub_format) not in self.publication_uuids
                self.publication_uuids[(book_uuid, pub_format)] = u

    def price_column_name(self, currency, fmt):
        if fmt == "pdf":
            fmt = "PDF"
        return currency + " price " + fmt

    def get_prices(self):
        def currencies_and_prices():
            for currency in sorted(codelists.get_currencies()):
                for fmt in sorted(codelists.get_formats()):
                    yield currency, fmt, self.price_column_name(currency, fmt)

        def get_book_prices():
            for data in self.get_books():
                for currency, fmt, col_name in currencies_and_prices():
                    if col_name in data["row"]:
                        price = data["row"][col_name]
                        if len(price) == 0:
                            continue
                        book_uuid = self.book_uuids[data["row_id"]]
                        yield (book_uuid, currency, fmt, decimal.Decimal(price),
                               data["doi"])

        for book_uuid, currency, fmt, price, doi in get_book_prices():
            key = (book_uuid, fmt)
            if key not in self.publication_uuids:
                print("Price found without ISBN?: {}".format(key),
                      file=sys.stderr)
                continue
            publication_uuid = self.publication_uuids[(book_uuid, fmt)]
            roac_client.save_price(self.client, publication_uuid,
                                   currency, price)

    def get_imprints(self):
        def has_imprint(imp):
            if imp is None:
                return False
            if imp == "":
                return False
            return True

        def imprint_names():
            for data in self.get_books():
                imprint = data["imprint"]
                if not has_imprint(imprint):
                    continue
                yield imprint
        imprints = frozenset([ i for i in imprint_names() ])

        for i in imprints:
            roac_client.save_imprint(self.client, i, self.publisher_name)

        for data in self.get_books():
            imp = data["imprint"]
            if not has_imprint(imp):
                continue
            row_id = data["row_id"]
            roac_client.save_imprint_volume(self.client,
                                            self.book_uuids[row_id],
                                            imp)
