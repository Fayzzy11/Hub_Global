#!/usr/bin/env python3
"""Test du garde-fou de nuit de scripts/update_market.py. Lancer : python3 scripts/test_update_market.py"""
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from update_market import PARIS, passage_de_nuit  # noqa: E402


def a(h, m=0):
    return dt.datetime(2026, 11, 27, h, m, tzinfo=PARIS)


assert passage_de_nuit(a(1), manuel=False), "1 h : programmé, ne fait rien"
assert passage_de_nuit(a(6, 59), manuel=False)
assert passage_de_nuit(a(23, 5), manuel=False)
assert not passage_de_nuit(a(7, 41), manuel=False), "7 h 41 : passe"
assert not passage_de_nuit(a(22, 59), manuel=False)
assert not passage_de_nuit(a(3), manuel=True), "lancement manuel ou par l'app : passe toujours"
utc = dt.datetime(2026, 11, 27, 6, 41, tzinfo=dt.timezone.utc)  # 7 h 41 à Paris en hiver
assert not passage_de_nuit(utc, manuel=False)
print("garde-fou de nuit : 7 tests OK")
