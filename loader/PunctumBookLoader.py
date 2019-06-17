import sys

from BookLoader import BookLoader

class PunctumBookLoader(BookLoader):
    def setup_column_mapping(self):
        return {
            "Book Title": "title",
            "Number of Pages": "pageCount",
            "Cover URL": "cover_url",
            "Website": "overview_url",
            "Language": "languageCode",
            "Edition": "edition",
            "Abstract": "short_blurb",
            "Link to Download Title": "full_text_pdf_url"
        }

    ## FIXME: this should be fixed upstream
    ## the code *here* ought to throw an error rather than correct this
    def get_doi(self, data, row_data):
        return row_data['DOI'].strip("\n")

    def get_imprint(self, data, row_data):
        return row_data["Imprint"]

    def get_licence(self, data, row_data):
        lic_url = row_data["License"]
        if not lic_url.startswith("https://creativecommons.org/licenses/"):
            return (lic_url, None, None)
        parts = lic_url.split("/")
        version = parts[5]
        code = "CC " + parts[4].upper()
        return lic_url, code, version

    def get_keywords(self, data, row_data):
        kwds = row_data["Keywords"]
        return [ kwd.strip() for kwd in set(kwds.split(",")) ]

    def get_series_ids(self, data, row_data):
        return None ## FIXME - Punctum dataset currently lacks this info

    def get_series_ordinal(self, data, row_data):
        num = row_data["Series Number"]
        if num.isdigit():
            return int(num)
        return None

    def get_subjects(self, data, row_data):
        bics = row_data["BIC"].strip()
        if len(bics) == 0:
            return []
        return [ ("BIC", row_data["BIC"] ) ]

    ## see comment for self.get_doi
    def skip_row(self, data):
        return data['pageCount'] == ""

    ## FIXME
    def skip_row_no_dict(self, row):
        return row[23] == "" # that is, column X in the spreadsheet

    ## FIXME
    def get_copyright_holders(self, row):
        return row['Authors']

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
