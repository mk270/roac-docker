copy language_code (lang_code)
  from '/docker-entrypoint-initdb.d/language_codes.csv' with csv;

copy format (format_name)
  from '/docker-entrypoint-initdb.d/formats.csv' with csv;

copy contributor_role (role_name)
  from '/docker-entrypoint-initdb.d/contributor_roles.csv' with csv;

copy detail (detail_id, detail_name)
  from '/docker-entrypoint-initdb.d/details.csv' with csv;

copy subject_scheme (subject_scheme_name)
  from '/docker-entrypoint-initdb.d/subject_scheme.csv' with csv;

copy currency (currency_code)
  from '/docker-entrypoint-initdb.d/iso4217.csv' with csv;
