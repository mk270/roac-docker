# ScholarLed Metadata loader, by Martin Keegan
#
# Copyright (C) 2018-2019  Open Book Publishers
#
# This programme is free software; you may redistribute and/or modify
# it under the terms of the Apache License v2.0.

import sys
import re

from BookLoader import BookLoader

def comma_join(names):
    if len(names) == 1:
        return names[0]
    elif len(names) == 2:
        return names[0] + " & " + names[1]
    else:
        return ", ".join(names[0:-1]) + " & " + names[-1]

class OBPBookLoader(BookLoader):
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
            "Short Blurb (less than 100 words)": "short_blurb",
            "Full-text URL - PDF": "full_text_pdf_url",
            "Full-text URL - HTML": "full_text_html_url"
        }

    def extra_detail_fields(self):
        return [
            "full_text_html_url"
        ]

    def skip_row(self, data):
        return data['doiSuffix'] == ""

    def skip_row_no_dict(self, row):
        return row[3] == ""

    def get_doi(self, data, row_data):
        return data['doiPrefix'] + '/' + data['doiSuffix']

    def get_imprint(self, data, row_data):
        """Unimplemented - OBP effectively has no imprints."""
        return None

    def get_licence(self, data, row_data):
        lic_url = row_data["License URL (human-readable summary)"]
        lic_code = row_data["License"]
        lic_version = row_data["Version of the license"]
        return lic_url, lic_code, lic_version

    def get_keywords(self, data, row_data):
        kwds = row_data["keywords"]
        return [ kwd.strip() for kwd in kwds.split(";") ]

    def get_subjects(self, data, row_data):
        def all_subject_data():
            for scheme in ["BIC", "BISAC"]:
                for col in map(str, [i for i in range(1, 6)]):
                    col_name = "{} subject code {}".format(scheme, col)
                    val = row_data[col_name]
                    if len(val) > 0:
                        yield scheme, val
        return [ i for i in all_subject_data() ]

    def get_series_ids(self, data, row_data):
        def sanitise_issn(s):
            s2 = s[0:4] + s[5:9]
            assert s2[:7].isdigit()
            assert s2[-1:] == "X" or s2[-1:].isdigit()
            return s2

        print_issn   = row_data["ISSN Print with dashes"]
        digital_issn = row_data["ISSN Digital with dashes"]
        series_name  = row_data["Series Name"]
        if len(print_issn) < 8 or len(digital_issn) < 8:
            return None
        return (sanitise_issn(print_issn),
                sanitise_issn(digital_issn),
                series_name)

    def get_series_ordinal(self, data, row_data):
        num = row_data["No. in the Series"]
        if num.isdigit():
            return int(num)
        return None

    def get_copyright_holders(self, row):
        base = "Copyright holder "
        names = []
        for i in ["1", "2", "3"]:
            field_name = base + i
            val = row.get(field_name, "")
            if val != "":
                names.append(val)

        assert len(names) > 0
        return comma_join(names)

    def contributors_from_row(self, row):
        for contributor in range(0, 6):
            offset = contributor * 7 + 5
            first_name = row[offset]
            last_name  = row[offset + 1]
            role       = row[offset + 2]
            if first_name == "" or last_name == "" or role == "":
                continue
            yield (first_name, last_name, role)

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

