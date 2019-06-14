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
    def skip_row(self, data):
        return data['doiSuffix'] == ""

    def skip_row_no_dict(self, row):
        return row[3] == ""

    def get_doi(self, data, raw_data):
        return data['doiPrefix'] + '/' + data['doiSuffix']

    def get_imprint(self, data, raw_data):
        """Unimplemented - OBP effectively has no imprints."""
        return None

    def get_series_ids(self, data, raw_data):
        def sanitise_issn(s):
            s2 = s[0:4] + s[5:9]
            assert s2[:7].isdigit()
            assert s2[-1:] == "X" or s2[-1:].isdigit()
            return s2

        print_issn   = raw_data["ISSN Print with dashes"]
        digital_issn = raw_data["ISSN Digital with dashes"]
        series_name  = raw_data["Series Name"]
        if len(print_issn) < 8 or len(digital_issn) < 8:
            return None
        return (sanitise_issn(print_issn),
                sanitise_issn(digital_issn),
                series_name)

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

