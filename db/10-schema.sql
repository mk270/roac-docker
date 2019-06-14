begin transaction;

create table publisher (
       publisher_name text primary key,
       publisher_url text not null,
       publisher_abbrev text not null
);

create table language_code (
       lang_code char(3) primary key
);

insert into language_code (lang_code) values ('eng');
insert into language_code (lang_code) values ('fre');
insert into language_code (lang_code) values ('alb');
insert into language_code (lang_code) values ('por');
insert into language_code (lang_code) values ('ita');
insert into language_code (lang_code) values ('nor');


create table book (
       book_uuid char(36) primary key,
       title text not null,
       publisher_name text not null references publisher(publisher_name),
       lang_code char(3) not null references language_code(lang_code),
       edition integer not null,
       subtitle text,
       page_count integer not null,
       copyright_holder text not null
);

create table format (
       format_name varchar(30) primary key
);

insert into format (format_name) values ('paperback');
insert into format (format_name) values ('hardback');
insert into format (format_name) values ('pdf');
insert into format (format_name) values ('epub');
insert into format (format_name) values ('mobi');
insert into format (format_name) values ('html');
insert into format (format_name) values ('xml');

create table publication (
       publication_uuid char(36) primary key,
       book_uuid char(36) not null references book(book_uuid),
       format varchar(30) not null references format(format_name),
       isbn char(13) not null,
       unique(isbn)
);

create table publication_price (
       publication_uuid char(36) primary key
               references publication(publication_uuid),
       currency char(3) not null,
       price decimal(12,2) not null,
       unique (publication_uuid, currency)
);

create table chapter (
       chapter_uuid char(36) primary key,
       chapter_name varchar(200) not null,
       book_uuid char(36) not null references book(book_uuid),
       priority int not null,
       unique (book_uuid, chapter_name)
);

create table contributor (
       contributor_uuid char(36) primary key,
       contributor_name text not null,
       contributor_bio text not null,
       contributor_orcid text,
       contributor_website_url text
);

create table contributor_role (
       role_name varchar(20) unique not null
);

insert into contributor_role (role_name) values ('author');
insert into contributor_role (role_name) values ('editor');
insert into contributor_role (role_name) values ('illustrator');
insert into contributor_role (role_name) values ('introduction');
insert into contributor_role (role_name) values ('foreword');
insert into contributor_role (role_name) values ('preface');
insert into contributor_role (role_name) values ('translator');
insert into contributor_role (role_name) values ('music editor');

create table contribution (
       contributor_uuid char(36) not null
               references contributor(contributor_uuid),
       book_uuid char(36) not null references book(book_uuid),
       role_name varchar(20) not null references contributor_role(role_name),
       unique (contributor_uuid, book_uuid, role_name)
);

create table chapter_contribution (
       chapter_contributor_uuid char(36) not null
               references contributor(contributor_uuid),
       chapter_uuid char(36) not null references chapter(chapter_uuid),
       role_name varchar(20) not null references contributor_role(role_name),
       unique (chapter_contributor_uuid, chapter_uuid, role_name)
);

create table detail (
       detail_id varchar(30) unique not null,
       detail_name text not null
);

insert into detail (detail_id, detail_name) values ('cover_url', 'Cover URL');
insert into detail (detail_id, detail_name) values ('overview_url', 'Overview URL');
insert into detail (detail_id, detail_name) values ('doi', 'DOI');
insert into detail (detail_id, detail_name) values ('short_blurb', 'Short blurb');

create table book_detail (
       book_uuid char(36) not null references book(book_uuid),
       detail_id varchar(30) not null references detail(detail_id),
       detail_value text not null,
       unique (book_uuid, detail_id)
);

create table series (
       series_uuid char(36) unique not null,
       series_name text not null,
       series_issn_print char(8) unique not null,
       series_issn_digital char(8) unique not null,
       series_url text
);

create table series_volume (
       book_uuid char(36) not null references book(book_uuid),
       series_uuid char(36) not null references series(series_uuid),
       volume_ordinal integer not null,
       unique (book_uuid, series_uuid)
);

commit;
