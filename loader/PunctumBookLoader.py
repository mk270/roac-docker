
from BookLoader import BookLoader

class PunctumBookLoader(BookLoader):
    def setup_column_mapping(self):
        return {
            "Book Title": "title",
            "Number of Pages": "pageCount",
            "Cover URL": "cover_url",
            "Website": "overview_url"
        }

    ## FIXME: this should be fixed upstream
    ## the code *here* ought to throw an error rather than correct this
    def get_doi(self, data, raw_data):
        return raw_data['DOI'].strip("\n")

    ## see comment for self.get_doi
    def skip_row(self, data):
        return data['pageCount'] == ""

    ## FIXME
    def skip_row_no_dict(self, row):
        return row[23] == "" # that is, column X in the spreadsheet

    def contributors_from_row(self, row):
        rows = {
            6: "Author",
            7: "Editor"
        }
        for offset, role in rows.items():
            cell = row[offset]
            if cell == "":
                continue
            contributors = [ c.strip() for c in cell.split(";") ]
            for contributor in contributors:
                if ", " not in contributor:
                    contributor += ", "
                last_name, first_name = contributor.split(", ")
                if last_name == "":
                    continue
                yield (first_name, last_name, role)

    def publications_from_row(self, row):
        for pub in (0,):
            offset = pub * 1 + 13
            pub_format = "paperback"
            pub_isbn   = row[offset + 1]
            if pub_format == "" or pub_isbn == "":
                continue
            if len(pub_isbn) > 13:
                continue
            yield (pub_format, pub_isbn)
