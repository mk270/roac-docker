#!/usr/bin/env python3

# ScholarLed Metadata loader, by Martin Keegan
#
# Copyright (C) 2018-2019  Open Book Publishers
#
# This programme is free software; you may redistribute and/or modify
# it under the terms of the Apache License v2.0.

"""
   TODO: ENFORCE RESULT CHECKS

how do we enforce other checks?
"""

import argparse
from graphqlclient import GraphQLClient

import roac_client

from OBPBookLoader import OBPBookLoader
from PunctumBookLoader import PunctumBookLoader

publishers = {
    "OBP": (OBPBookLoader, "Open Book Publishers"),
    "Punctum": (PunctumBookLoader, "Punctum Books")
}

def run(client, data_file, mode, max_books, create_subjects):
    loader_class, publisher_name = publishers[mode]
    roac_client.save_publishers(client, publisher_name)
    book_loader = loader_class(client, data_file, publisher_name, max_books,
                               create_subjects)
    book_loader.load()

def unwrap_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="metadata CSV input file path",
                        default="all-book-metadata.csv")
    parser.add_argument("--base-url", help="GraphQL endpoint URL",
                        default="http://localhost:41962/graphql")
    parser.add_argument("--mode", help="Publisher mode (e.g., OBP, Punctum)",
                        default="OBP")
    parser.add_argument("--max-books", type=int, help="Maximum books to import",
                        default=None)
    parser.add_argument("--create-subjects", action="store_true",
                        default=False,
                        help="Auto-create BIC/BISAC codes where necessary")
    args = parser.parse_args()
    client = GraphQLClient(args.base_url)
    run(client, args.file, args.mode, args.max_books, args.create_subjects)

if __name__ == '__main__':
    unwrap_args()
