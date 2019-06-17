# ScholarLed Metadata loader, by Martin Keegan
#
# Copyright (C) 2018-2019  Open Book Publishers
#
# This programme is free software; you may redistribute and/or modify
# it under the terms of the Apache License v2.0.

# FIXME: should pull this out of the db dir

def get_currencies():
    return ["GBP", "USD", "AUD", "EUR", "CAD"]

def get_formats():
    return ["paperback", "hardback", "pdf", "epub", "mobi", "html", "xml"]
