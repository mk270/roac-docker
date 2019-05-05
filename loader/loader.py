#!/usr/bin/env python3

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

def load_books(client, data_file, mode, publisher_name, max_books):
    assert mode in publishers
    book_loader = publishers[mode][0](client, data_file,
                                      publisher_name, max_books)
    book_loader.load()

def run(client, data_file, mode, max_books):
    roac_client.save_publishers(client, publishers[mode][1])
    load_books(client, data_file, mode, publishers[mode][1], max_books)

def unwrap_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="metadata CSV input file path",
                        default="all-book-metadata.csv")
    parser.add_argument("--base-url", help="GraphQL endpoint URL",
                        default="http://localhost:41962/graphql")
    parser.add_argument("--mode", help="Publisher mode (e.g., OBP, Punctum)",
                        default="OBP")
    parser.add_argument("--max-books", help="Maximum books to import",
                        default=None)
    args = parser.parse_args()
    client = GraphQLClient(args.base_url)
    run(client, args.file, args.mode, int(args.max_books))

if __name__ == '__main__':
    unwrap_args()
