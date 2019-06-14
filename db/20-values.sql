copy language_code (lang_code) from '/docker-entrypoint-initdb.d/language_codes.csv' with csv;

insert into format (format_name) values ('paperback');
insert into format (format_name) values ('hardback');
insert into format (format_name) values ('pdf');
insert into format (format_name) values ('epub');
insert into format (format_name) values ('mobi');
insert into format (format_name) values ('html');
insert into format (format_name) values ('xml');

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
