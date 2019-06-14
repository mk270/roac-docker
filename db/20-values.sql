copy language_code (lang_code) from '/docker-entrypoint-initdb.d/language_codes.csv' with csv;

copy format (format_name) from '/docker-entrypoint-initdb.d/formats.csv' with csv;

insert into contributor_role (role_name) values ('author');
insert into contributor_role (role_name) values ('editor');
insert into contributor_role (role_name) values ('illustrator');
insert into contributor_role (role_name) values ('introduction');
insert into contributor_role (role_name) values ('foreword');
insert into contributor_role (role_name) values ('preface');
insert into contributor_role (role_name) values ('translator');
insert into contributor_role (role_name) values ('music editor');

insert into detail (detail_id, detail_name) values ('cover_url', 'Cover URL');
insert into detail (detail_id, detail_name) values ('overview_url', 'Overview URL');
insert into detail (detail_id, detail_name) values ('doi', 'DOI');
insert into detail (detail_id, detail_name) values ('short_blurb', 'Short blurb');

copy currency (currency_code) from '/docker-entrypoint-initdb.d/iso4217.csv' with csv;
