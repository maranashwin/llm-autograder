#!/usr/bin/python
# +
import os, json, math, copy
from collections import namedtuple
import pandas as pd
import bs4
from numpy import nan

HIDDEN_FILE = os.path.join("hidden", "hidden_tests.py")
if os.path.exists(HIDDEN_FILE):
    import hidden.hidden_tests as hidn
# -

REL_TOL = 6e-04  # relative tolerance for floats
TOTAL_SCORE = 100 # total score for the project

DF_FILE = 'expected_dfs.html'
PLOT_FILE = 'expected_plots.json'

PASS = "All test cases passed!"

TEXT_FORMAT = "TEXT_FORMAT"  # question type when expected answer is a type, str, int, float, or bool
TEXT_FORMAT_UNORDERED_LIST = "TEXT_FORMAT_UNORDERED_LIST"  # question type when the expected answer is a list or a set where the order does *not* matter
TEXT_FORMAT_ORDERED_LIST = "TEXT_FORMAT_ORDERED_LIST"  # question type when the expected answer is a list or tuple where the order does matter
TEXT_FORMAT_DICT = "TEXT_FORMAT_DICT"  # question type when the expected answer is a dictionary
TEXT_FORMAT_SPECIAL_ORDERED_LIST = "TEXT_FORMAT_SPECIAL_ORDERED_LIST"  # question type when the expected answer is a list where order does matter, but with possible ties. Elements are ordered according to values in special_ordered_json (with ties allowed)
TEXT_FORMAT_NAMEDTUPLE = "TEXT_FORMAT_NAMEDTUPLE"  # question type when expected answer is a namedtuple
PNG_FORMAT_SCATTER = "PNG_FORMAT_SCATTER" # question type when the expected answer is a scatter plot
HTML_FORMAT_ORDERED = "HTML_FORMAT_ORDERED" # question type when the expected answer is a DataFrame and the order of the indices matter
HTML_FORMAT_UNORDERED = "HTML_FORMAT_UNORDERED" # question type when the expected answer is a DataFrame and the order of the indices does not matter
FILE_JSON_FORMAT = "FILE_JSON_FORMAT" # question type when the expected answer is a JSON file
SLASHES = "SLASHES" # question SUFFIX when expected answer contains paths with slashes

def get_expected_format():
    """get_expected_format() returns a dict mapping each question to the format
    of the expected answer."""
    expected_format = {'q1': 'TEXT_FORMAT_UNORDERED_LIST',
                       'q2': 'TEXT_FORMAT',
                       'q3': 'TEXT_FORMAT',
                       'q4': 'PNG_FORMAT_SCATTER',
                       'q5': 'PNG_FORMAT_SCATTER',
                       'q6': 'TEXT_FORMAT_DICT',
                       'q7': 'PNG_FORMAT_SCATTER',
                       'q8': 'PNG_FORMAT_SCATTER',
                       'q9': 'PNG_FORMAT_SCATTER',
                       'q10': 'TEXT_FORMAT_ORDERED_LIST_SLASHES',
                       'q11': 'TEXT_FORMAT_ORDERED_LIST_SLASHES',
                       'q12': 'TEXT_FORMAT_ORDERED_LIST_SLASHES',
                       'q13': 'TEXT_FORMAT_ORDERED_LIST_SLASHES',
                       'q14': 'TEXT_FORMAT',
                       'q15': 'TEXT_FORMAT_ORDERED_LIST',
                       'q16': 'TEXT_FORMAT_ORDERED_LIST',
                       'q17': 'TEXT_FORMAT_UNORDERED_LIST',
                       'q18': 'TEXT_FORMAT_ORDERED_LIST',
                       'q19': 'TEXT_FORMAT_UNORDERED_LIST',
                       'q20': 'TEXT_FORMAT_UNORDERED_LIST'}
    return expected_format


def get_expected_json():
    """get_expected_json() returns a dict mapping each question to the expected
    answer (if the format permits it)."""
    expected_json = {'q1': [0.18751518245234763, 0.14495968322780176, 0.023351177301822967],
                     'q2': 0.7182887844043079,
                     'q3': 16939322.97315541,
                     'q6': {'Red Giant': -0.30455725305788545,
                            'White Dwarf': -0.35098783317952004,
                            'Neutron Star': -0.43743108035595923},
                     'q10': ['broken_data/toi/tois.json'],
                     'q11': ['broken_data/kepler/100/other/others.json',
                             'broken_data/kepler/100/200/others.json',
                             'broken_data/kepler/100/200/290/290s.json',
                             'broken_data/kepler/100/200/220s.json',
                             'broken_data/kepler/100/100/others.json',
                             'broken_data/kepler/100/100/100s.json'],
                     'q12': ['broken_data/kepler/100/other/others.json'],
                     'q13': ['broken_data/toi/tois.json',
                             'broken_data/others.json',
                             'broken_data/kepler/other/others.json',
                             'broken_data/kepler/100/other/others.json',
                             'broken_data/kepler/100/200/others.json',
                             'broken_data/kepler/100/200/290/290s.json',
                             'broken_data/kepler/100/200/220s.json',
                             'broken_data/kepler/100/100/others.json',
                             'broken_data/kepler/100/100/100s.json',
                             'broken_data/kepler/10/others.json',
                             'broken_data/kepler/10/80s.json',
                             'broken_data/kepler/10/30/30s.json',
                             'broken_data/kepler/10/20s.json',
                             'broken_data/k2s.json',
                             'broken_data/hd/other/others.json',
                             'broken_data/hd/10000/10000s.json',
                             'broken_data/gj/gjs.json'],
                     'q14': 243.58589886521645,
                     'q15': [210.79398932087835, 234.0919566866524],
                     'q16': [1.1322558761518515, 1.6678445441576182],
                     'q17': ['EPIC 4822 a', 'omi-1131 3', '2MASS-7122 d', 'eps 6219 a'],
                     'q18': [278.15, 314.15],
                     'q19': ['eps-9464 a',
                             'xi-3218 1',
                             'omi-377 1',
                             'xi 7600 a',
                             'kap 1644 a',
                             'TOI-6031 1',
                             'CoRoT-6127 a',
                             'gam1 6127 1',
                             'EPIC-6897 1',
                             'bet 7170 1',
                             'EPIC 4822 a',
                             'rho 5204 a',
                             '2MASS 4378 a',
                             'BD-2087 1',
                             'Kepler-6932 1',
                             'psi1 87 1',
                             '2MASS 2739 1',
                             'Kepler 565 a',
                             '2MASS 1718 1',
                             'GJ 3158 1',
                             'BD-5786 1',
                             'HD-73 a',
                             'CoRoT 5857 a',
                             'bet-9211 a',
                             'HD 1152 1',
                             'xi 4378 1',
                             'TOI 5170 a',
                             'ups 4924 1',
                             '2MASS 5857 1',
                             'GJ-3154 a',
                             'iot-9686 a',
                             'GJ 8124 a',
                             'WASP 2596 1',
                             'BD-6109 a',
                             'HD-4908 a',
                             'gam-8041 1',
                             'GJ-6358 a',
                             'iot-5165 1',
                             'BD 9049 1',
                             'kap 2402 a',
                             'psi1-4933 1',
                             'rho-9079 1',
                             'alf 2375 1',
                             'Kepler 9932 1',
                             '2MASS-7782 a',
                             'alf-2647 a',
                             'ome 2638 1',
                             'tau-80 a',
                             'BD-8290 1',
                             'mu2 4869 a',
                             'bet 8221 a',
                             '2MASS-8451 a',
                             'alf-237 1',
                             'xi-3842 1',
                             'GJ-1288 a',
                             'ups-6496 1',
                             'CoRoT-3226 a',
                             'gam1 6964 a',
                             'eps-7 a',
                             'psi1 1303 1',
                             'kap-7574 a',
                             'eps 4235 1',
                             'DP-953 a',
                             'Kepler-3031 1',
                             'psi1 6387 a',
                             'bet 28974 1',
                             'kap-8381 a',
                             'nu-1926 1',
                             'eps 1251 1',
                             'xi 40042 a',
                             'rho 797 1',
                             'Kepler-3535 1',
                             'WASP 5241 1',
                             'alf 1470 1',
                             'bet-2196 1',
                             'iot-4801 a',
                             'CoRoT-9952 a',
                             'ups 7129 1',
                             'TOI-5177 a',
                             'nu-1718 a',
                             'HD 6813 1',
                             '2MASS 5394 a',
                             'DP 2402 a',
                             'EPIC-90262 a',
                             'mu 7357 a',
                             'nu-697 1',
                             'tau 5177 1',
                             'alf-8097 a',
                             'kap 5212 a',
                             'bet 1552 a',
                             'ome 228 a',
                             'HD 5170 1',
                             'Kepler-9763 1',
                             'HD-7126 a',
                             'xi-6726 1',
                             'mu 8433 a',
                             'omi-7108 a',
                             'ups 3031 1',
                             'rho-8743 a',
                             'xi 1339 1',
                             'DP 8041 a',
                             'DP 8041 b',
                             'BD 9602 a',
                             'BD 9602 b',
                             'tau-7721 1',
                             'tau-7721 2',
                             'eps-3965 1',
                             'eps-3965 2',
                             'xi-57 a',
                             'xi-57 b',
                             'psi1-2336 a',
                             'psi1-2336 b',
                             'Kepler 8041 1',
                             'Kepler 8041 2',
                             'mu-3043 1',
                             'mu-3043 2',
                             'xi 2263 1',
                             'xi 2263 2',
                             'omi-2195 1',
                             'omi-2195 2',
                             'HD 6495 a',
                             'HD 6495 b',
                             'DP-8088 1',
                             'DP-8088 2',
                             'xi-5416 1',
                             'xi-5416 2',
                             '2MASS 3605 a',
                             '2MASS 3605 b',
                             'omi-726 1',
                             'omi-726 2',
                             'iot 9602 1',
                             'iot 9602 2',
                             'eps-4548 1',
                             'eps-4548 2',
                             'mu-1152 a',
                             'mu-1152 b',
                             'mu-2693 1',
                             'mu-2693 2',
                             'CoRoT 4653 1',
                             'CoRoT 4653 2',
                             'TOI 8743 a',
                             'TOI 8743 b',
                             'gam-9464 a',
                             'gam-9464 b',
                             'mu 75061 a',
                             'mu 75061 b',
                             'psi1-377 1',
                             'psi1-377 2',
                             'nu 9699 a',
                             'nu 9699 b',
                             'EPIC-8088 a',
                             'EPIC-8088 b',
                             'gam-8954 a',
                             'gam-8954 b',
                             'mu 6387 1',
                             'mu 6387 2',
                             'omi 697 1',
                             'omi 697 2',
                             'tau 6634 1',
                             'tau 6634 2',
                             'WASP-7412 1',
                             'WASP-7412 2',
                             'kap-4818 a',
                             'kap-4818 b',
                             'alf-7 a',
                             'alf-7 b',
                             'kap-46580 a',
                             'kap-46580 b',
                             'EPIC 1152 a',
                             'EPIC 1152 b',
                             'rho 3092 1',
                             'rho 3092 2',
                             'mu 1289 1',
                             'mu 1289 2',
                             'DP 5846 1',
                             'DP 5846 2',
                             '2MASS 2717 a',
                             '2MASS 2717 b',
                             'rho-8236 a',
                             'rho-8236 b',
                             'DP-726 a',
                             'DP-726 b',
                             'xi-5477 a',
                             'xi-5477 b',
                             '2MASS 3821 a',
                             '2MASS 3821 b',
                             'GJ-8739 1',
                             'GJ-8739 2',
                             'HD-5786 1',
                             'HD-5786 2',
                             'eps-4336 a',
                             'eps-4336 b',
                             'tau-237 1',
                             'tau-237 2',
                             'bet 7231 a',
                             'bet 7231 b',
                             'ome 90 a',
                             'ome 90 b',
                             'mu 47 1',
                             'mu 47 2',
                             'GJ 6031 a',
                             'GJ 6031 b',
                             'BD-9452 1',
                             'BD-9452 2',
                             'TOI-2865 1',
                             'TOI-2865 2',
                             'ome 23916 a',
                             'ome 23916 b',
                             'iot 5527 1',
                             'iot 5527 2',
                             '2MASS-8631 1',
                             '2MASS-8631 2',
                             'GJ 4036 a',
                             'GJ 4036 b',
                             'HD-2342 a',
                             'HD-2342 b',
                             'Kepler-7170 a',
                             'Kepler-7170 b',
                             'omi-6718 1',
                             'omi-6718 2',
                             'gam 1261 1',
                             'gam 1261 2',
                             'omi-2982 a',
                             'omi-2982 b',
                             'gam 4030 1',
                             'gam 4030 2',
                             'iot-6289 a',
                             'iot-6289 b',
                             'gam1 8433 1',
                             'gam1 8433 2',
                             'GJ-5554 1',
                             'GJ-5554 2',
                             'CoRoT 9620 1',
                             'CoRoT 9620 2',
                             'WASP-6219 1',
                             'WASP-6219 2',
                             'alf-5416 a',
                             'alf-5416 b',
                             'DP-4258 a',
                             'DP-4258 b',
                             'gam 6740 a',
                             'gam 6740 b',
                             'WASP 7721 1',
                             'WASP 7721 2',
                             'WASP 3535 a',
                             'WASP 3535 b',
                             'DP-2814 a',
                             'DP-2814 b',
                             'iot 57 1',
                             'iot 57 2',
                             'gam1-5989 a',
                             'gam1-5989 b',
                             'HD-1288 a',
                             'HD-1288 b',
                             'TOI 7360 a',
                             'TOI 7360 b',
                             'gam 8497 1',
                             'gam 8497 2',
                             'tau 1270 a',
                             'tau 1270 b',
                             'iot-1349 a',
                             'iot-1349 b',
                             'nu 2710 1',
                             'nu 2710 2',
                             'Kepler 8236 1',
                             'Kepler 8236 2',
                             'rho 4685 a',
                             'rho 4685 b',
                             'bet-439 a',
                             'bet-439 b',
                             'nu-2418 1',
                             'nu-2418 2',
                             'alf 6284 a',
                             'alf 6284 b',
                             'ome 4030 a',
                             'ome 4030 b',
                             'GJ-697 1',
                             'GJ-697 2',
                             'iot 93756 1',
                             'iot 93756 2',
                             'Kepler-2375 a',
                             'Kepler-2375 b',
                             'xi-4908 1',
                             'xi-4908 2',
                             'gam 3276 1',
                             'gam 3276 2',
                             'Kepler 89 a',
                             'Kepler 89 b',
                             'BD 4869 1',
                             'BD 4869 2',
                             'tau-32188 a',
                             'tau-32188 b',
                             'GJ 1149 a',
                             'GJ 1149 b',
                             'iot-85605 a',
                             'iot-85605 b',
                             'omi-2271 1',
                             'omi-2271 2',
                             'eps 37 1',
                             'eps 37 2',
                             'GJ-5534 a',
                             'GJ-5534 b',
                             'GJ-5534 c',
                             'kap-1339 a',
                             'kap-1339 b',
                             'kap-1339 c',
                             'xi 5748 a',
                             'xi 5748 b',
                             'xi 5748 c',
                             'GJ 8221 1',
                             'GJ 8221 2',
                             'GJ 8221 3',
                             'GJ-53 1',
                             'GJ-53 2',
                             'GJ-53 3',
                             'BD-5920 a',
                             'BD-5920 b',
                             'BD-5920 c',
                             'tau-40042 a',
                             'tau-40042 b',
                             'tau-40042 c',
                             'BD-2728 1',
                             'BD-2728 2',
                             'BD-2728 3',
                             'CoRoT 6932 a',
                             'CoRoT 6932 b',
                             'CoRoT 6932 c',
                             'EPIC 7224 a',
                             'EPIC 7224 b',
                             'EPIC 7224 c',
                             'ome-8739 a',
                             'ome-8739 b',
                             'ome-8739 c',
                             'kap-1568 1',
                             'kap-1568 2',
                             'kap-1568 3',
                             'TOI-28974 a',
                             'TOI-28974 b',
                             'TOI-28974 c',
                             'nu 7307 a',
                             'nu 7307 b',
                             'nu 7307 c',
                             'GJ 9827 1',
                             'GJ 9827 2',
                             'GJ 9827 3',
                             'omi 678 a',
                             'omi 678 b',
                             'omi 678 c',
                             'GJ-4358 a',
                             'GJ-4358 b',
                             'GJ-4358 c',
                             'gam-726 a',
                             'gam-726 b',
                             'gam-726 c',
                             'bet 4576 a',
                             'bet 4576 b',
                             'bet 4576 c',
                             'EPIC 9932 1',
                             'EPIC 9932 2',
                             'EPIC 9932 3',
                             'mu-3625 a',
                             'mu-3625 b',
                             'mu-3625 c',
                             'WASP-7842 1',
                             'WASP-7842 2',
                             'WASP-7842 3',
                             'eps-4989 a',
                             'eps-4989 b',
                             'eps-4989 c',
                             'DP-7574 1',
                             'DP-7574 2',
                             'DP-7574 3',
                             'CoRoT-7 1',
                             'CoRoT-7 2',
                             'CoRoT-7 3',
                             'nu-6905 1',
                             'nu-6905 2',
                             'nu-6905 3',
                             'alf 7129 1',
                             'alf 7129 2',
                             'alf 7129 3',
                             'mu 7224 1',
                             'mu 7224 2',
                             'mu 7224 3',
                             'omi 1149 1',
                             'omi 1149 2',
                             'omi 1149 3',
                             'kap 2087 1',
                             'kap 2087 2',
                             'kap 2087 3',
                             'rho-6726 1',
                             'rho-6726 2',
                             'rho-6726 3',
                             'bet 3769 1',
                             'bet 3769 2',
                             'bet 3769 3',
                             'rho-6934 1',
                             'rho-6934 2',
                             'rho-6934 3',
                             'EPIC 189 1',
                             'EPIC 189 2',
                             'EPIC 189 3',
                             'CoRoT 5184 1',
                             'CoRoT 5184 2',
                             'CoRoT 5184 3',
                             'tau 9763 1',
                             'tau 9763 2',
                             'tau 9763 3',
                             'TOI-228 1',
                             'TOI-228 2',
                             'TOI-228 3',
                             'WASP-3179 a',
                             'WASP-3179 b',
                             'WASP-3179 c',
                             'xi 8497 a',
                             'xi 8497 b',
                             'xi 8497 c',
                             'mu-996 a',
                             'mu-996 b',
                             'mu-996 c',
                             'omi-5149 1',
                             'omi-5149 2',
                             'omi-5149 3',
                             'eps 1411 a',
                             'eps 1411 b',
                             'eps 1411 c',
                             'gam-2814 1',
                             'gam-2814 2',
                             'gam-2814 3',
                             'mu-8497 1',
                             'mu-8497 2',
                             'mu-8497 3',
                             'mu-9201 1',
                             'mu-9201 2',
                             'mu-9201 3',
                             'rho-2865 a',
                             'rho-2865 b',
                             'rho-2865 c',
                             'bet-1664 1',
                             'bet-1664 2',
                             'bet-1664 3',
                             'BD-2739 a',
                             'BD-2739 b',
                             'BD-2739 c',
                             'WASP-5527 1',
                             'WASP-5527 2',
                             'WASP-5527 3',
                             'tau-7108 1',
                             'tau-7108 2',
                             'tau-7108 3',
                             '2MASS 88 1',
                             '2MASS 88 2',
                             '2MASS 88 3',
                             'b Cen AB a',
                             'b Cen AB b',
                             'b Cen AB c',
                             'Kepler-5402 a',
                             'Kepler-5402 b',
                             'Kepler-5402 c',
                             'omi 1743 a',
                             'omi 1743 b',
                             'omi 1743 c',
                             'ome-2087 a',
                             'ome-2087 b',
                             'ome-2087 c',
                             'mu 2631 a',
                             'mu 2631 b',
                             'mu 2631 c',
                             'eps-79144 1',
                             'eps-79144 2',
                             'eps-79144 3',
                             'kap 53225 a',
                             'kap 53225 b',
                             'kap 53225 c',
                             'alf 2418 1',
                             'alf 2418 2',
                             'alf 2418 3',
                             'tau 6387 1',
                             'tau 6387 2',
                             'tau 6387 3',
                             'EPIC 2316 1',
                             'EPIC 2316 2',
                             'EPIC 2316 3',
                             'bet 7574 a',
                             'bet 7574 b',
                             'bet 7574 c',
                             'omi 7639 1',
                             'omi 7639 2',
                             'omi 7639 3',
                             'HD 40042 1',
                             'HD 40042 2',
                             'HD 40042 3',
                             'TOI-2122 1',
                             'TOI-2122 2',
                             'TOI-2122 3',
                             'mu2-1612 a',
                             'mu2-1612 b',
                             'mu2-1612 c',
                             'kap 7721 1',
                             'kap 7721 2',
                             'kap 7721 3',
                             'DP-8041 1',
                             'DP-8041 2',
                             'DP-8041 3',
                             'mu 4803 a',
                             'mu 4803 b',
                             'mu 4803 c',
                             'ome-9049 1',
                             'ome-9049 2',
                             'ome-9049 3',
                             'eps-9225 a',
                             'eps-9225 b',
                             'eps-9225 c',
                             'gam 5149 a',
                             'gam 5149 b',
                             'gam 5149 c',
                             'psi1 4036 1',
                             'psi1 4036 2',
                             'psi1 4036 3',
                             'TOI-7200 a',
                             'TOI-7200 b',
                             'TOI-7200 c',
                             'gam 2418 a',
                             'gam 2418 b',
                             'gam 2418 c',
                             'BD 7167 1',
                             'BD 7167 2',
                             'BD 7167 3',
                             'HD-8 1',
                             'HD-8 2',
                             'HD-8 3',
                             'psi1-8547 a',
                             'psi1-8547 b',
                             'psi1-8547 c',
                             'CoRoT-8954 1',
                             'CoRoT-8954 2',
                             'CoRoT-8954 3',
                             'nu 1999 1',
                             'nu 1999 2',
                             'nu 1999 3',
                             'bet 8907 a',
                             'bet 8907 b',
                             'bet 8907 c',
                             'gam 5920 1',
                             'gam 5920 2',
                             'gam 5920 3',
                             'ups 2126 1',
                             'ups 2126 2',
                             'ups 2126 3',
                             'eps-6905 1',
                             'eps-6905 2',
                             'eps-6905 3',
                             'mu 40 a',
                             'mu 40 b',
                             'mu 40 c',
                             'TOI 1223 1',
                             'TOI 1223 2',
                             'TOI 1223 3',
                             'alf-3702 a',
                             'alf-3702 b',
                             'alf-3702 c',
                             'gam1 16 a',
                             'gam1 16 b',
                             'gam1 16 c',
                             'eps-6740 1',
                             'eps-6740 2',
                             'eps-6740 3',
                             'EPIC 565 a',
                             'EPIC 565 b',
                             'EPIC 565 c',
                             'EPIC 7108 a',
                             'EPIC 7108 b',
                             'EPIC 7108 c',
                             'omi-5554 a',
                             'omi-5554 b',
                             'omi-5554 c',
                             'gam-8 1',
                             'gam-8 2',
                             'gam-8 3',
                             'alf-3218 1',
                             'alf-3218 2',
                             'alf-3218 3',
                             'eps-2865 a',
                             'eps-2865 b',
                             'eps-2865 c',
                             'alf-9276 1',
                             'alf-9276 2',
                             'alf-9276 3',
                             'iot-87 a',
                             'iot-87 b',
                             'iot-87 c',
                             'Kepler 2196 1',
                             'Kepler 2196 2',
                             'Kepler 2196 3',
                             'WASP 6615 1',
                             'WASP 6615 2',
                             'WASP 6615 3',
                             'omi-1131 1',
                             'omi-1131 2',
                             'omi-1131 3',
                             'DP 2270 1',
                             'DP 2270 2',
                             'DP 2270 3',
                             'DP 2270 4',
                             'ups-6448 a',
                             'ups-6448 b',
                             'ups-6448 c',
                             'ups-6448 d',
                             'Kepler-4613 a',
                             'Kepler-4613 b',
                             'Kepler-4613 c',
                             'Kepler-4613 d',
                             'HD-5920 1',
                             'HD-5920 2',
                             'HD-5920 3',
                             'HD-5920 4',
                             'omi-1996 1',
                             'omi-1996 2',
                             'omi-1996 3',
                             'omi-1996 4',
                             'mu2-5206 1',
                             'mu2-5206 2',
                             'mu2-5206 3',
                             'mu2-5206 4',
                             'HD-5748 a',
                             'HD-5748 b',
                             'HD-5748 c',
                             'HD-5748 d',
                             'iot 79144 1',
                             'iot 79144 2',
                             'iot 79144 3',
                             'iot 79144 4',
                             'mu-697 1',
                             'mu-697 2',
                             'mu-697 3',
                             'mu-697 4',
                             'TOI-53225 1',
                             'TOI-53225 2',
                             'TOI-53225 3',
                             'TOI-53225 4',
                             'CoRoT 2140 1',
                             'CoRoT 2140 2',
                             'CoRoT 2140 3',
                             'CoRoT 2140 4',
                             'mu-1468 1',
                             'mu-1468 2',
                             'mu-1468 3',
                             'mu-1468 4',
                             '2MASS 8907 a',
                             '2MASS 8907 b',
                             '2MASS 8907 c',
                             '2MASS 8907 d',
                             'nu 7639 a',
                             'nu 7639 b',
                             'nu 7639 c',
                             'nu 7639 d',
                             'EPIC 8165 1',
                             'EPIC 8165 2',
                             'EPIC 8165 3',
                             'EPIC 8165 4',
                             'xi-73 a',
                             'xi-73 b',
                             'xi-73 c',
                             'xi-73 d',
                             'kap 4117 1',
                             'kap 4117 2',
                             'kap 4117 3',
                             'kap 4117 4',
                             'psi1 9782 a',
                             'psi1 9782 b',
                             'psi1 9782 c',
                             'psi1 9782 d',
                             'mu2-6498 1',
                             'mu2-6498 2',
                             'mu2-6498 3',
                             'mu2-6498 4',
                             'gam 89 1',
                             'gam 89 2',
                             'gam 89 3',
                             'gam 89 4',
                             'alf-1149 1',
                             'alf-1149 2',
                             'alf-1149 3',
                             'alf-1149 4',
                             'HD-1152 1',
                             'HD-1152 2',
                             'HD-1152 3',
                             'HD-1152 4',
                             'alf-8041 a',
                             'alf-8041 b',
                             'alf-8041 c',
                             'alf-8041 d',
                             'mu2 2693 1',
                             'mu2 2693 2',
                             'mu2 2693 3',
                             'mu2 2693 4',
                             'omi-4754 1',
                             'omi-4754 2',
                             'omi-4754 3',
                             'omi-4754 4',
                             'kap-237 a',
                             'kap-237 b',
                             'kap-237 c',
                             'kap-237 d',
                             'gam1 8088 1',
                             'gam1 8088 2',
                             'gam1 8088 3',
                             'gam1 8088 4',
                             'omi-57 1',
                             'omi-57 2',
                             'omi-57 3',
                             'omi-57 4',
                             'BD 6934 a',
                             'BD 6934 b',
                             'BD 6934 c',
                             'BD 6934 d',
                             'rho-4696 a',
                             'rho-4696 b',
                             'rho-4696 c',
                             'rho-4696 d',
                             'omi 805 1',
                             'omi 805 2',
                             'omi 805 3',
                             'omi 805 4',
                             'ome-6498 a',
                             'ome-6498 b',
                             'ome-6498 c',
                             'ome-6498 d',
                             'TOI-6397 1',
                             'TOI-6397 2',
                             'TOI-6397 3',
                             'TOI-6397 4',
                             'mu2-7812 1',
                             'mu2-7812 2',
                             'mu2-7812 3',
                             'mu2-7812 4',
                             'DP 5177 1',
                             'DP 5177 2',
                             'DP 5177 3',
                             'DP 5177 4',
                             'alf 40042 1',
                             'alf 40042 2',
                             'alf 40042 3',
                             'alf 40042 4',
                             'mu-2982 a',
                             'mu-2982 b',
                             'mu-2982 c',
                             'mu-2982 d',
                             'tau 6905 1',
                             'tau 6905 2',
                             'tau 6905 3',
                             'tau 6905 4',
                             'rho-7412 a',
                             'rho-7412 b',
                             'rho-7412 c',
                             'rho-7412 d',
                             'mu 86972 a',
                             'mu 86972 b',
                             'mu 86972 c',
                             'mu 86972 d',
                             'DP 67 1',
                             'DP 67 2',
                             'DP 67 3',
                             'DP 67 4',
                             'Kepler 2342 1',
                             'Kepler 2342 2',
                             'Kepler 2342 3',
                             'Kepler 2342 4',
                             'mu 9301 a',
                             'mu 9301 b',
                             'mu 9301 c',
                             'mu 9301 d',
                             'nu-8739 1',
                             'nu-8739 2',
                             'nu-8739 3',
                             'nu-8739 4',
                             'BD-3842 1',
                             'BD-3842 2',
                             'BD-3842 3',
                             'BD-3842 4',
                             'gam1-9079 1',
                             'gam1-9079 2',
                             'gam1-9079 3',
                             'gam1-9079 4',
                             'ups-8739 a',
                             'ups-8739 b',
                             'ups-8739 c',
                             'ups-8739 d',
                             'eps 7200 a',
                             'eps 7200 b',
                             'eps 7200 c',
                             'eps 7200 d',
                             'gam-2316 a',
                             'gam-2316 b',
                             'gam-2316 c',
                             'gam-2316 d',
                             'mu2-79144 a',
                             'mu2-79144 b',
                             'mu2-79144 c',
                             'mu2-79144 d',
                             'kap-5204 1',
                             'kap-5204 2',
                             'kap-5204 3',
                             'kap-5204 4',
                             'HD 4342 a',
                             'HD 4342 b',
                             'HD 4342 c',
                             'HD 4342 d',
                             'ome 189 1',
                             'ome 189 2',
                             'ome 189 3',
                             'ome 189 4',
                             'CoRoT 9000 1',
                             'CoRoT 9000 2',
                             'CoRoT 9000 3',
                             'CoRoT 9000 4',
                             'mu 1012 a',
                             'mu 1012 b',
                             'mu 1012 c',
                             'mu 1012 d',
                             '2MASS-5920 a',
                             '2MASS-5920 b',
                             '2MASS-5920 c',
                             '2MASS-5920 d',
                             'ome-954 a',
                             'ome-954 b',
                             'ome-954 c',
                             'ome-954 d',
                             'tau-1255 1',
                             'tau-1255 2',
                             'tau-1255 3',
                             'tau-1255 4',
                             'Kepler-2967 1',
                             'Kepler-2967 2',
                             'Kepler-2967 3',
                             'Kepler-2967 4',
                             'tau 1718 a',
                             'tau 1718 b',
                             'tau 1718 c',
                             'tau 1718 d',
                             'HD-7150 a',
                             'HD-7150 b',
                             'HD-7150 c',
                             'HD-7150 d',
                             'TOI-9615 a',
                             'TOI-9615 b',
                             'TOI-9615 c',
                             'TOI-9615 d',
                             'nu 72 1',
                             'nu 72 2',
                             'nu 72 3',
                             'nu 72 4',
                             'DP 46 a',
                             'DP 46 b',
                             'DP 46 c',
                             'DP 46 d',
                             'ome 5512 a',
                             'ome 5512 b',
                             'ome 5512 c',
                             'ome 5512 d',
                             'mu 6718 1',
                             'mu 6718 2',
                             'mu 6718 3',
                             'mu 6718 4',
                             'HD 20794 a',
                             'HD 20794 b',
                             'HD 20794 c',
                             'HD 20794 d',
                             'TOI-1086 a',
                             'TOI-1086 b',
                             'TOI-1086 c',
                             'TOI-1086 d',
                             'GJ-77934 1',
                             'GJ-77934 2',
                             'GJ-77934 3',
                             'GJ-77934 4',
                             'ups 8026 1',
                             'ups 8026 2',
                             'ups 8026 3',
                             'ups 8026 4',
                             '2MASS-237 1',
                             '2MASS-237 2',
                             '2MASS-237 3',
                             '2MASS-237 4',
                             'WASP-8547 1',
                             'WASP-8547 2',
                             'WASP-8547 3',
                             'WASP-8547 4',
                             'gam 805 a',
                             'gam 805 b',
                             'gam 805 c',
                             'gam 805 d',
                             'GJ-797 a',
                             'GJ-797 b',
                             'GJ-797 c',
                             'GJ-797 d',
                             'BD-5643 1',
                             'BD-5643 2',
                             'BD-5643 3',
                             'BD-5643 4',
                             'CoRoT-7639 1',
                             'CoRoT-7639 2',
                             'CoRoT-7639 3',
                             'CoRoT-7639 4',
                             'DP 93756 a',
                             'DP 93756 b',
                             'DP 93756 c',
                             'DP 93756 d',
                             'nu 3605 1',
                             'nu 3605 2',
                             'nu 3605 3',
                             'nu 3605 4',
                             'nu-8097 a',
                             'nu-8097 b',
                             'nu-8097 c',
                             'nu-8097 d',
                             'Kepler-2819 1',
                             'Kepler-2819 2',
                             'Kepler-2819 3',
                             'Kepler-2819 4',
                             'rho-8423 a',
                             'rho-8423 b',
                             'rho-8423 c',
                             'rho-8423 d',
                             'mu2 6359 a',
                             'mu2 6359 b',
                             'mu2 6359 c',
                             'mu2 6359 d',
                             'psi1-8 1',
                             'psi1-8 2',
                             'psi1-8 3',
                             'psi1-8 4',
                             'BD-6359 a',
                             'BD-6359 b',
                             'BD-6359 c',
                             'BD-6359 d',
                             'kap-3974 1',
                             'kap-3974 2',
                             'kap-3974 3',
                             'kap-3974 4',
                             'WASP-3229 1',
                             'WASP-3229 2',
                             'WASP-3229 3',
                             'WASP-3229 4',
                             '2MASS-7122 a',
                             '2MASS-7122 b',
                             '2MASS-7122 c',
                             '2MASS-7122 d',
                             'mu2-7937 1',
                             'mu2-7937 2',
                             'mu2-7937 3',
                             'mu2-7937 4',
                             'eps 6219 a',
                             'eps 6219 b',
                             'eps 6219 c',
                             'eps 6219 d',
                             'WASP 4 1',
                             'WASP 4 2',
                             'WASP 4 3',
                             'WASP 4 4',
                             'ups 7189 a',
                             'ups 7189 b',
                             'ups 7189 c',
                             'ups 7189 d',
                             'Kepler 5643 1',
                             'Kepler 5643 2',
                             'Kepler 5643 3',
                             'Kepler 5643 4',
                             'bet-699 a',
                             'bet-699 b',
                             'bet-699 c',
                             'bet-699 d',
                             'xi-65724 1',
                             'xi-65724 2',
                             'xi-65724 3',
                             'xi-65724 4',
                             'omi 4199 1',
                             'omi 4199 2',
                             'omi 4199 3',
                             'omi 4199 4',
                             'GJ-8221 1',
                             'GJ-8221 2',
                             'GJ-8221 3',
                             'GJ-8221 4',
                             'psi1 6219 1',
                             'psi1 6219 2',
                             'psi1 6219 3',
                             'psi1 6219 4',
                             'GJ-36956 a',
                             'GJ-36956 b',
                             'GJ-36956 c',
                             'GJ-36956 d',
                             'iot 7307 1',
                             'iot 7307 2',
                             'iot 7307 3',
                             'iot 7307 4',
                             'gam 569 a',
                             'gam 569 b',
                             'gam 569 c',
                             'gam 569 d',
                             'gam1 2122 a',
                             'alf-6127 3',
                             'psi1-60132 e',
                             'TOI-37 b',
                             'alf-439 4',
                             'xi-47 a',
                             '2MASS-2675 c',
                             'BD-4761 5',
                             'iot-7357 b',
                             'DP-7566 d',
                             'gam1-57 1',
                             'gam 4374 3',
                             'TOI-3030 e',
                             'xi 1664 b',
                             'Kepler-197 d',
                             'ome 6359 a',
                             'bet 9840 3',
                             'tau 4696 e',
                             'bet-7600 b',
                             'alf 79 d',
                             'bet-1373 1',
                             'DP-6903 c',
                             'tau-5534 5',
                             'psi1 5589 b',
                             'BD-6448 4',
                             'alf 9646 a',
                             'HD 6903 c',
                             'BD-9628 5',
                             'psi1-1288 2',
                             'iot-2596 2',
                             'gam1 2122 d',
                             'DP 6387 a',
                             'ome-1377 3',
                             'TOI-37 e',
                             'GJ-8142 2',
                             'xi-47 d',
                             'DP 6244 a',
                             'mu2 7566 3',
                             'iot-7357 e',
                             'gam1 8165 b',
                             'gam1-57 4',
                             'HD-7122 1',
                             'nu-79 3',
                             'xi 1664 e',
                             '2MASS 6897 2',
                             'ome 6359 d',
                             'HD-4431 1',
                             'CoRoT 5786 c',
                             'bet-7600 e',
                             'mu 5857 2',
                             'bet-1373 4',
                             'gam-4861 a',
                             'Kepler-228 3',
                             'psi1 5589 e',
                             'CoRoT-5241 b',
                             'alf 9646 d',
                             'BD-9225 a',
                             'gam-5177 3',
                             'psi1-1288 5',
                             'iot-2596 5',
                             'DP-2140 2',
                             'DP 6387 d',
                             'WASP-1086 a',
                             'ups 1743 3',
                             'GJ-8142 5',
                             'bet 212 b',
                             'DP 6244 d',
                             'xi-9 1',
                             'xi 5165 c',
                             'gam1 8165 e',
                             'BD-1339 2',
                             'HD-7122 4',
                             'CoRoT 1178 a',
                             'mu2 4801 3',
                             '2MASS 6897 5',
                             'Kepler-46580 2',
                             'HD-4431 4',
                             'GJ 9366 a',
                             'ome 3535 c',
                             'mu 5857 5',
                             'kap-7604 2',
                             'gam-4861 d',
                             'GJ-7604 1',
                             'HD-3760 c',
                             'CoRoT-5241 e',
                             '2MASS-2 2',
                             'BD-9225 d',
                             'bet 5965 1',
                             'bet-93 c',
                             'rho 1957 5',
                             'Kepler 4342 2',
                             'DP 4117 d',
                             'bet-569 1',
                             'ome-8083 3',
                             'Kepler 9301 e',
                             'WASP-40042 b',
                             '2MASS 1568 4',
                             'alf-6496 1',
                             'CoRoT-60132 3',
                             'psi1-2126 5',
                             'nu-7167 b',
                             'HD 6299 d',
                             'BD 2324 a',
                             'xi 2054 3',
                             'EPIC 1568 e',
                             'EPIC 5366 b',
                             'kap-9049 d',
                             'gam-2710 1',
                             'Kepler-9448 c',
                             'mu2-14040 e',
                             'GJ 554 2',
                             'eps 7307 4',
                             'kap 2316 1',
                             'Kepler-2638 c',
                             'TOI 4989 5',
                             'ups-6387 2',
                             'gam-3420 d',
                             'ups 4818 1',
                             'GJ 4685 d',
                             'alf-6127 1',
                             'psi1-60132 c',
                             'bet-569 5',
                             'alf-439 2',
                             'GJ 7478 d',
                             '2MASS-2675 a',
                             'BD-4761 3',
                             'alf-6496 5',
                             'DP-7566 b',
                             'ome 1468 d',
                             'gam 4374 1',
                             'TOI-3030 c',
                             'BD 2324 e',
                             'Kepler-197 b',
                             'CoRoT-2196 4',
                             'bet 9840 1',
                             'tau 4696 c',
                             'gam-2710 5',
                             'alf 79 b',
                             'Kepler-2195 d',
                             'DP-6903 a',
                             'tau-5534 3',
                             'kap 2316 5',
                             'BD-6448 2',
                             'mu2 2336 d',
                             'HD 6903 a',
                             'BD-9628 3',
                             'ups 4818 5',
                             'GJ 4685 e',
                             'alf-6127 2',
                             'psi1-60132 d',
                             'TOI-37 a',
                             'alf-439 3',
                             'GJ 7478 e',
                             '2MASS-2675 b',
                             'BD-4761 4',
                             'iot-7357 a',
                             'DP-7566 c',
                             'ome 1468 e',
                             'gam 4374 2',
                             'TOI-3030 d',
                             'xi 1664 a',
                             'Kepler-197 c',
                             'CoRoT-2196 5',
                             'bet 9840 2',
                             'tau 4696 d',
                             'bet-7600 a',
                             'alf 79 c',
                             'Kepler-2195 e',
                             'DP-6903 b',
                             'tau-5534 4',
                             'psi1 5589 a',
                             'BD-6448 3',
                             'mu2 2336 e',
                             'HD 6903 b',
                             'BD-9628 4',
                             'psi1-1288 1',
                             'GJ 4685 c',
                             'Kepler 4342 5',
                             'psi1-60132 b',
                             'bet-569 4',
                             'alf-439 1',
                             'GJ 7478 c',
                             'WASP-40042 e',
                             'BD-4761 2',
                             'alf-6496 4',
                             'DP-7566 a',
                             'ome 1468 c',
                             'nu-7167 e',
                             'TOI-3030 b',
                             'BD 2324 d',
                             'Kepler-197 a',
                             'CoRoT-2196 3',
                             'EPIC 5366 e',
                             'tau 4696 b',
                             'gam-2710 4',
                             'alf 79 a',
                             'Kepler-2195 c',
                             'GJ 554 5',
                             'tau-5534 2',
                             'kap 2316 4',
                             'BD-6448 1',
                             'mu2 2336 c',
                             'ups-6387 5',
                             'BD-9628 2',
                             'ups 4818 4',
                             'GJ 4685 b',
                             'Kepler 4342 4',
                             'psi1-60132 a',
                             'bet-569 3',
                             'ome-8083 5',
                             'GJ 7478 b',
                             'WASP-40042 d',
                             'BD-4761 1',
                             'alf-6496 3',
                             'CoRoT-60132 5',
                             'ome 1468 b',
                             'nu-7167 d',
                             'TOI-3030 a',
                             'BD 2324 c',
                             'xi 2054 5',
                             'CoRoT-2196 2',
                             'EPIC 5366 d',
                             'tau 4696 a',
                             'gam-2710 3',
                             'Kepler-9448 e',
                             'Kepler-2195 b',
                             'GJ 554 4',
                             'tau-5534 1',
                             'kap 2316 3',
                             'Kepler-2638 e',
                             'mu2 2336 b',
                             'ups-6387 4',
                             'BD-9628 1',
                             'ups 4818 3',
                             'GJ 4685 a',
                             'Kepler 4342 3',
                             'DP 4117 e',
                             'bet-569 2',
                             'ome-8083 4',
                             'GJ 7478 a',
                             'WASP-40042 c',
                             '2MASS 1568 5',
                             'alf-6496 2',
                             'CoRoT-60132 4',
                             'ome 1468 a',
                             'nu-7167 c',
                             'HD 6299 e',
                             'BD 2324 b',
                             'xi 2054 4',
                             'CoRoT-2196 1',
                             'EPIC 5366 c',
                             'kap-9049 e',
                             'gam-2710 2',
                             'Kepler-9448 d',
                             'Kepler-2195 a',
                             'GJ 554 3',
                             'eps 7307 5',
                             'kap 2316 2',
                             'Kepler-2638 d',
                             'mu2 2336 a',
                             'ups-6387 3',
                             'gam-3420 e',
                             'ups 4818 2',
                             'rho 1957 3',
                             'DP-2140 5',
                             'DP 4117 b',
                             'WASP-1086 d',
                             'ome-8083 1',
                             'Kepler 9301 c',
                             'bet 212 e',
                             '2MASS 1568 2',
                             'xi-9 4',
                             'CoRoT-60132 1',
                             'psi1-2126 3',
                             'BD-1339 5',
                             'HD 6299 b',
                             'CoRoT 1178 d',
                             'xi 2054 1',
                             'EPIC 1568 c',
                             'Kepler-46580 5',
                             'kap-9049 b',
                             'GJ 9366 d',
                             'Kepler-9448 a',
                             'mu2-14040 c',
                             'kap-7604 5',
                             'eps 7307 2',
                             'GJ-7604 4',
                             'Kepler-2638 a',
                             'TOI 4989 3',
                             '2MASS-2 5',
                             'gam-3420 b',
                             'bet 5965 4',
                             'rho 1957 1',
                             'DP-2140 3',
                             'DP 6387 e',
                             'WASP-1086 b',
                             'ups 1743 4',
                             'Kepler 9301 a',
                             'bet 212 c',
                             'DP 6244 e',
                             'xi-9 2',
                             'xi 5165 d',
                             'psi1-2126 1',
                             'BD-1339 3',
                             'HD-7122 5',
                             'CoRoT 1178 b',
                             'mu2 4801 4',
                             'EPIC 1568 a',
                             'Kepler-46580 3',
                             'HD-4431 5',
                             'GJ 9366 b',
                             'ome 3535 d',
                             'mu2-14040 a',
                             'kap-7604 3',
                             'gam-4861 e',
                             'GJ-7604 2',
                             'HD-3760 d',
                             'TOI 4989 1',
                             '2MASS-2 3',
                             'BD-9225 e',
                             'bet 5965 2',
                             'bet-93 d',
                             'rho 1957 4',
                             'Kepler 4342 1',
                             'DP 4117 c',
                             'WASP-1086 e',
                             'ome-8083 2',
                             'Kepler 9301 d',
                             'WASP-40042 a',
                             '2MASS 1568 3',
                             'xi-9 5',
                             'CoRoT-60132 2',
                             'psi1-2126 4',
                             'nu-7167 a',
                             'HD 6299 c',
                             'CoRoT 1178 e',
                             'xi 2054 2',
                             'EPIC 1568 d',
                             'EPIC 5366 a',
                             'kap-9049 c',
                             'GJ 9366 e',
                             'Kepler-9448 b',
                             'mu2-14040 d',
                             'GJ 554 1',
                             'eps 7307 3',
                             'GJ-7604 5',
                             'Kepler-2638 b',
                             'TOI 4989 4',
                             'ups-6387 1',
                             'gam-3420 c',
                             'bet 5965 5',
                             'rho 1957 2',
                             'DP-2140 4',
                             'DP 4117 a',
                             'WASP-1086 c',
                             'ups 1743 5',
                             'Kepler 9301 b',
                             'bet 212 d',
                             '2MASS 1568 1',
                             'xi-9 3',
                             'xi 5165 e',
                             'psi1-2126 2',
                             'BD-1339 4',
                             'HD 6299 a',
                             'CoRoT 1178 c',
                             'mu2 4801 5',
                             'EPIC 1568 b',
                             'Kepler-46580 4',
                             'kap-9049 a',
                             'GJ 9366 c',
                             'ome 3535 e',
                             'mu2-14040 b',
                             'kap-7604 4',
                             'eps 7307 1',
                             'GJ-7604 3',
                             'HD-3760 e',
                             'TOI 4989 2',
                             '2MASS-2 4',
                             'gam-3420 a',
                             'bet 5965 3',
                             'bet-93 e',
                             'iot-2596 1',
                             'gam1 2122 c',
                             'alf-6127 5',
                             'ome-1377 2',
                             'TOI-37 d',
                             'GJ-8142 1',
                             'xi-47 c',
                             '2MASS-2675 e',
                             'mu2 7566 2',
                             'iot-7357 d',
                             'gam1 8165 a',
                             'gam1-57 3',
                             'gam 4374 5',
                             'nu-79 2',
                             'xi 1664 d',
                             '2MASS 6897 1',
                             'ome 6359 c',
                             'bet 9840 5',
                             'CoRoT 5786 b',
                             'bet-7600 d',
                             'mu 5857 1',
                             'bet-1373 3',
                             'DP-6903 e',
                             'Kepler-228 2',
                             'psi1 5589 d',
                             'CoRoT-5241 a',
                             'alf 9646 c',
                             'HD 6903 e',
                             'gam-5177 2',
                             'psi1-1288 4',
                             'iot-2596 4',
                             'DP-2140 1',
                             'DP 6387 c',
                             'ome-1377 5',
                             'ups 1743 2',
                             'GJ-8142 4',
                             'bet 212 a',
                             'DP 6244 c',
                             'mu2 7566 5',
                             'xi 5165 b',
                             'gam1 8165 d',
                             'BD-1339 1',
                             'HD-7122 3',
                             'nu-79 5',
                             'mu2 4801 2',
                             '2MASS 6897 4',
                             'Kepler-46580 1',
                             'HD-4431 3',
                             'CoRoT 5786 e',
                             'ome 3535 b',
                             'mu 5857 4',
                             'kap-7604 1',
                             'gam-4861 c',
                             'Kepler-228 5',
                             'HD-3760 b',
                             'CoRoT-5241 d',
                             '2MASS-2 1',
                             'BD-9225 c',
                             'gam-5177 5',
                             'bet-93 b',
                             'iot-2596 3',
                             'gam1 2122 e',
                             'DP 6387 b',
                             'ome-1377 4',
                             'ups 1743 1',
                             'GJ-8142 3',
                             'xi-47 e',
                             'DP 6244 b',
                             'mu2 7566 4',
                             'xi 5165 a',
                             'gam1 8165 c',
                             'gam1-57 5',
                             'HD-7122 2',
                             'nu-79 4',
                             'mu2 4801 1',
                             '2MASS 6897 3',
                             'ome 6359 e',
                             'HD-4431 2',
                             'CoRoT 5786 d',
                             'ome 3535 a',
                             'mu 5857 3',
                             'bet-1373 5',
                             'gam-4861 b',
                             'Kepler-228 4',
                             'HD-3760 a',
                             'CoRoT-5241 c',
                             'alf 9646 e',
                             'BD-9225 b',
                             'gam-5177 4',
                             'bet-93 a',
                             'gam1 2122 b',
                             'alf-6127 4',
                             'ome-1377 1',
                             'TOI-37 c',
                             'alf-439 5',
                             'xi-47 b',
                             '2MASS-2675 d',
                             'mu2 7566 1',
                             'iot-7357 c',
                             'DP-7566 e',
                             'gam1-57 2',
                             'gam 4374 4',
                             'nu-79 1',
                             'xi 1664 c',
                             'Kepler-197 e',
                             'ome 6359 b',
                             'bet 9840 4',
                             'CoRoT 5786 a',
                             'bet-7600 c',
                             'alf 79 e',
                             'bet-1373 2',
                             'DP-6903 d',
                             'Kepler-228 1',
                             'psi1 5589 c',
                             'BD-6448 5',
                             'alf 9646 b',
                             'HD 6903 d',
                             'gam-5177 1',
                             'psi1-1288 3']}
    return expected_json


def get_special_json():
    """get_special_json() returns a dict mapping each question to the expected
    answer stored in a special format as a list of tuples. Each tuple contains
    the element expected in the list, and its corresponding value. Any two
    elements with the same value can appear in any order in the actual list,
    but if two elements have different values, then they must appear in the
    same order as in the expected list of tuples."""
    special_json = {}
    return special_json


def compare(expected, actual, q_format=TEXT_FORMAT):
    """compare(expected, actual) is used to compare when the format of
    the expected answer is known for certain."""
    try:
        if SLASHES in q_format:
            q_format = q_format.replace(SLASHES, "").strip("_ ")
            expected = clean_slashes(expected)
            actual = clean_slashes(actual)
            
        if q_format == TEXT_FORMAT:
            return simple_compare(expected, actual)
        elif q_format == TEXT_FORMAT_UNORDERED_LIST:
            return list_compare_unordered(expected, actual)
        elif q_format == TEXT_FORMAT_ORDERED_LIST:
            return list_compare_ordered(expected, actual)
        elif q_format == TEXT_FORMAT_DICT:
            return dict_compare(expected, actual)
        elif q_format == TEXT_FORMAT_SPECIAL_ORDERED_LIST:
            return list_compare_special(expected, actual)
        elif q_format == TEXT_FORMAT_NAMEDTUPLE:
            return namedtuple_compare(expected, actual)
        elif q_format == PNG_FORMAT_SCATTER:
            return compare_flip_dicts(expected, actual)
        elif q_format == HTML_FORMAT_ORDERED:
            return table_compare_ordered(expected, actual)
        elif q_format == HTML_FORMAT_UNORDERED:
            return table_compare_unordered(expected, actual)
        elif q_format == FILE_JSON_FORMAT:
            return compare_file_json(expected, actual)
        else:
            if expected != actual:
                return "expected %s but found %s " % (repr(expected), repr(actual))
    except:
        if expected != actual:
            return "expected %s but found %s " % (repr(expected), repr(actual))
    return PASS


def print_message(expected, actual, complete_msg=True):
    """print_message(expected, actual) displays a simple error message."""
    msg = "expected %s" % (repr(expected))
    if complete_msg:
        msg = msg + " but found %s" % (repr(actual))
    return msg


def simple_compare(expected, actual, complete_msg=True):
    """simple_compare(expected, actual) is used to compare when the expected answer
    is a type/Nones/str/int/float/bool. When the expected answer is a float,
    the actual answer is allowed to be within the tolerance limit. Otherwise,
    the values must match exactly, or a very simple error message is displayed."""
    msg = PASS
    if 'numpy' in repr(type((actual))):
        actual = actual.item()
    if isinstance(expected, type):
        if expected != actual:
            if isinstance(actual, type):
                msg = "expected %s but found %s" % (expected.__name__, actual.__name__)
            else:
                msg = "expected %s but found %s" % (expected.__name__, repr(actual))
            return msg
    elif not isinstance(actual, type(expected)):
        if not (isinstance(expected, (float, int)) and isinstance(actual, (float, int))) and not is_namedtuple(expected):
            return "expected to find type %s but found type %s" % (type(expected).__name__, type(actual).__name__)
    if isinstance(expected, float):
        if not math.isclose(actual, expected, rel_tol=REL_TOL):
            msg = print_message(expected, actual, complete_msg)
    elif isinstance(expected, (list, tuple)) or is_namedtuple(expected):
        new_msg = print_message(expected, actual, complete_msg)
        if len(expected) != len(actual):
            return new_msg
        for i in range(len(expected)):
            val = simple_compare(expected[i], actual[i])
            if val != PASS:
                return new_msg
    elif isinstance(expected, dict):
        new_msg = print_message(expected, actual, complete_msg)
        if len(expected) != len(actual):
            return new_msg
        val = simple_compare(sorted(list(expected.keys())), sorted(list(actual.keys())))
        if val != PASS:
            return new_msg
        for key in expected:
            val = simple_compare(expected[key], actual[key])
            if val != PASS:
                return new_msg
    else:
        if expected != actual:
            msg = print_message(expected, actual, complete_msg)
    return msg


def intelligent_compare(expected, actual, obj=None):
    """intelligent_compare(expected, actual) is used to compare when the
    data type of the expected answer is not known for certain, and default
    assumptions  need to be made."""
    if obj == None:
        obj = type(expected).__name__
    if is_namedtuple(expected):
        msg = namedtuple_compare(expected, actual)
    elif isinstance(expected, (list, tuple)):
        msg = list_compare_ordered(expected, actual, obj)
    elif isinstance(expected, set):
        msg = list_compare_unordered(expected, actual, obj)
    elif isinstance(expected, (dict)):
        msg = dict_compare(expected, actual)
    else:
        msg = simple_compare(expected, actual)
    msg = msg.replace("CompDict", "dict").replace("CompSet", "set").replace("NewNone", "None")
    return msg


def is_namedtuple(obj, init_check=True):
    """is_namedtuple(obj) returns True if `obj` is a namedtuple object
    defined in the test file."""
    bases = type(obj).__bases__
    if len(bases) != 1 or bases[0] != tuple:
        return False
    fields = getattr(type(obj), '_fields', None)
    if not isinstance(fields, tuple):
        return False
    if init_check and not type(obj).__name__ in [nt.__name__ for nt in _expected_namedtuples]:
        return False
    return True


def list_compare_ordered(expected, actual, obj=None):
    """list_compare_ordered(expected, actual) is used to compare when the
    expected answer is a list/tuple, where the order of the elements matters."""
    msg = PASS
    if not isinstance(actual, type(expected)):
        msg = "expected to find type %s but found type %s" % (type(expected).__name__, type(actual).__name__)
        return msg
    if obj == None:
        obj = type(expected).__name__
    for i in range(len(expected)):
        if i >= len(actual):
            msg = "at index %d of the %s, expected missing %s" % (i, obj, repr(expected[i]))
            break
        val = intelligent_compare(expected[i], actual[i], "sub" + obj)
        if val != PASS:
            msg = "at index %d of the %s, " % (i, obj) + val
            break
    if len(actual) > len(expected) and msg == PASS:
        msg = "at index %d of the %s, found unexpected %s" % (len(expected), obj, repr(actual[len(expected)]))
    if len(expected) != len(actual):
        msg = msg + " (found %d entries in %s, but expected %d)" % (len(actual), obj, len(expected))

    if len(expected) > 0:
        try:
            if msg != PASS and list_compare_unordered(expected, actual, obj) == PASS:
                msg = msg + " (%s may not be ordered as required)" % (obj)
        except:
            pass
    return msg


def list_compare_helper(larger, smaller):
    """list_compare_helper(larger, smaller) is a helper function which takes in
    two lists of possibly unequal sizes and finds the item that is not present
    in the smaller list, if there is such an element."""
    msg = PASS
    j = 0
    for i in range(len(larger)):
        if i == len(smaller):
            msg = "expected %s" % (repr(larger[i]))
            break
        found = False
        while not found:
            if j == len(smaller):
                val = simple_compare(larger[i], smaller[j - 1], complete_msg=False)
                break
            val = simple_compare(larger[i], smaller[j], complete_msg=False)
            j += 1
            if val == PASS:
                found = True
                break
        if not found:
            msg = val
            break
    return msg

class NewNone():
    """alternate class in place of None, which allows for comparison with
    all other data types."""
    def __str__(self):
        return 'None'
    def __repr__(self):
        return 'None'
    def __lt__(self, other):
        return True
    def __le__(self, other):
        return True
    def __gt__(self, other):
        return False
    def __ge__(self, other):
        return other == None
    def __eq__(self, other):
        return other == None
    def __ne__(self, other):
        return other != None

class CompDict(dict):
    """subclass of dict, which allows for comparison with other dicts."""
    def __init__(self, vals):
        super(self.__class__, self).__init__(vals)
        if type(vals) == CompDict:
            self.val = vals.val
        elif isinstance(vals, dict):
            self.val = self.get_equiv(vals)
        else:
            raise TypeError("'%s' object cannot be type casted to CompDict class" % type(vals).__name__)

    def get_equiv(self, vals):
        val = []
        for key in sorted(list(vals.keys())):
            val.append((key, vals[key]))
        return val

    def __str__(self):
        return str(dict(self.val))
    def __repr__(self):
        return repr(dict(self.val))
    def __lt__(self, other):
        return self.val < CompDict(other).val
    def __le__(self, other):
        return self.val <= CompDict(other).val
    def __gt__(self, other):
        return self.val > CompDict(other).val
    def __ge__(self, other):
        return self.val >= CompDict(other).val
    def __eq__(self, other):
        return self.val == CompDict(other).val
    def __ne__(self, other):
        return self.val != CompDict(other).val

class CompSet(set):
    """subclass of set, which allows for comparison with other sets."""
    def __init__(self, vals):
        super(self.__class__, self).__init__(vals)
        if type(vals) == CompSet:
            self.val = vals.val
        elif isinstance(vals, set):
            self.val = self.get_equiv(vals)
        else:
            raise TypeError("'%s' object cannot be type casted to CompSet class" % type(vals).__name__)

    def get_equiv(self, vals):
        return sorted(list(vals))

    def __str__(self):
        return str(set(self.val))
    def __repr__(self):
        return repr(set(self.val))
    def __getitem__(self, index):
        return self.val[index]
    def __lt__(self, other):
        return self.val < CompSet(other).val
    def __le__(self, other):
        return self.val <= CompSet(other).val
    def __gt__(self, other):
        return self.val > CompSet(other).val
    def __ge__(self, other):
        return self.val >= CompSet(other).val
    def __eq__(self, other):
        return self.val == CompSet(other).val
    def __ne__(self, other):
        return self.val != CompSet(other).val

def make_sortable(item):
    """make_sortable(item) replaces all Nones in `item` with an alternate
    class that allows for comparison with str/int/float/bool/list/set/tuple/dict.
    It also replaces all dicts (and sets) with a subclass that allows for
    comparison with other dicts (and sets)."""
    if item == None:
        return NewNone()
    elif isinstance(item, (type, str, int, float, bool)):
        return item
    elif isinstance(item, (list, set, tuple)):
        new_item = []
        for subitem in item:
            new_item.append(make_sortable(subitem))
        if is_namedtuple(item):
            return type(item)(*new_item)
        elif isinstance(item, set):
            return CompSet(new_item)
        else:
            return type(item)(new_item)
    elif isinstance(item, dict):
        new_item = {}
        for key in item:
            new_item[key] = make_sortable(item[key])
        return CompDict(new_item)
    return item

def list_compare_unordered(expected, actual, obj=None):
    """list_compare_unordered(expected, actual) is used to compare when the
    expected answer is a list/set where the order of the elements does not matter."""
    msg = PASS
    if not isinstance(actual, type(expected)):
        msg = "expected to find type %s but found type %s" % (type(expected).__name__, type(actual).__name__)
        return msg
    if obj == None:
        obj = type(expected).__name__

    try:
        sort_expected = sorted(make_sortable(expected))
        sort_actual = sorted(make_sortable(actual))
    except:
        return "unexpected datatype found in %s; expected entries of type %s" % (obj, obj, type(expected[0]).__name__)

    if len(actual) == 0 and len(expected) > 0:
        msg = "in the %s, missing " % (obj) + sort_expected[0]
    elif len(actual) > 0 and len(expected) > 0:
        val = intelligent_compare(sort_expected[0], sort_actual[0])
        if val.startswith("expected to find type"):
            msg = "in the %s, " % (obj) + simple_compare(sort_expected[0], sort_actual[0])
        else:
            if len(expected) > len(actual):
                msg = "in the %s, missing " % (obj) + list_compare_helper(sort_expected, sort_actual)
            elif len(expected) < len(actual):
                msg = "in the %s, found un" % (obj) + list_compare_helper(sort_actual, sort_expected)
            if len(expected) != len(actual):
                msg = msg + " (found %d entries in %s, but expected %d)" % (len(actual), obj, len(expected))
                return msg
            else:
                val = list_compare_helper(sort_expected, sort_actual)
                if val != PASS:
                    msg = "in the %s, missing " % (obj) + val + ", but found un" + list_compare_helper(sort_actual,
                                                                                               sort_expected)
    return msg


def namedtuple_compare(expected, actual):
    """namedtuple_compare(expected, actual) is used to compare when the
    expected answer is a namedtuple defined in the test file."""
    msg = PASS
    if not is_namedtuple(actual, False):
        return "expected to find type %s namedtuple but found type %s" % (type(expected).__name__, type(actual).__name__)
    if type(expected).__name__ != type(actual).__name__:
        return "expected to find type %s namedtuple but found type %s namedtuple" % (type(expected).__name__, type(actual).__name__)
    expected_fields = expected._fields
    actual_fields = actual._fields
    msg = list_compare_ordered(list(expected_fields), list(actual_fields), "namedtuple attributes")
    if msg != PASS:
        return msg
    for field in expected_fields:
        val = intelligent_compare(getattr(expected, field), getattr(actual, field))
        if val != PASS:
            msg = "at attribute %s of namedtuple %s, " % (field, type(expected).__name__) + val
            return msg
    return msg


def clean_slashes(item):
    """clean_slashes()"""
    if isinstance(item, str):
        return type(item)(str(item).replace("\\", os.path.sep).replace("/", os.path.sep))
    elif item == None or isinstance(item, (type, int, float, bool)):
        return item
    elif isinstance(item, (list, tuple, set)) or is_namedtuple(item):
        new_item = []
        for subitem in item:
            new_item.append(clean_slashes(subitem))
        if is_namedtuple(item):
            return type(item)(*new_item)
        else:
            return type(item)(new_item)
    elif isinstance(item, dict):
        new_item = {}
        for key in item:
            new_item[clean_slashes(key)] = clean_slashes(item[key])
        return item


def list_compare_special_initialize(special_expected):
    """list_compare_special_initialize(special_expected) takes in the special
    ordering stored as a sorted list of items, and returns a list of lists
    where the ordering among the inner lists does not matter."""
    latest_val = None
    clean_special = []
    for row in special_expected:
        if latest_val == None or row[1] != latest_val:
            clean_special.append([])
            latest_val = row[1]
        clean_special[-1].append(row[0])
    return clean_special


def list_compare_special(special_expected, actual):
    """list_compare_special(special_expected, actual) is used to compare when the
    expected answer is a list with special ordering defined in `special_expected`."""
    msg = PASS
    expected_list = []
    special_order = list_compare_special_initialize(special_expected)
    for expected_item in special_order:
        expected_list.extend(expected_item)
    val = list_compare_unordered(expected_list, actual)
    if val != PASS:
        return val
    i = 0
    for expected_item in special_order:
        j = len(expected_item)
        actual_item = actual[i: i + j]
        val = list_compare_unordered(expected_item, actual_item)
        if val != PASS:
            if j == 1:
                msg = "at index %d " % (i) + val
            else:
                msg = "between indices %d and %d " % (i, i + j - 1) + val
            msg = msg + " (list may not be ordered as required)"
            break
        i += j
    return msg


def dict_compare(expected, actual, obj=None):
    """dict_compare(expected, actual) is used to compare when the expected answer
    is a dict."""
    msg = PASS
    if not isinstance(actual, type(expected)):
        msg = "expected to find type %s but found type %s" % (type(expected).__name__, type(actual).__name__)
        return msg
    if obj == None:
        obj = type(expected).__name__

    expected_keys = list(expected.keys())
    actual_keys = list(actual.keys())
    val = list_compare_unordered(expected_keys, actual_keys, obj)

    if val != PASS:
        msg = "bad keys in %s: " % (obj) + val
    if msg == PASS:
        for key in expected:
            new_obj = None
            if isinstance(expected[key], (list, tuple, set)):
                new_obj = 'value'
            elif isinstance(expected[key], dict):
                new_obj = 'sub' + obj
            val = intelligent_compare(expected[key], actual[key], new_obj)
            if val != PASS:
                msg = "incorrect value for key %s in %s: " % (repr(key), obj) + val
    return msg


def is_flippable(item):
    """is_flippable(item) determines if the given dict of lists has lists of the
    same length and is therefore flippable."""
    item_lens = set(([str(len(item[key])) for key in item]))
    if len(item_lens) == 1:
        return PASS
    else:
        return "found lists of lengths %s" % (", ".join(list(item_lens)))

def flip_dict_of_lists(item):
    """flip_dict_of_lists(item) flips a dict of lists into a list of dicts if the
    lists are of same length."""
    new_item = []
    length = len(list(item.values())[0])
    for i in range(length):
        new_dict = {}
        for key in item:
            new_dict[key] = item[key][i]
        new_item.append(new_dict)
    return new_item

def compare_flip_dicts(expected, actual):
    """compare_flip_dicts(expected, actual) flips a dict of lists (or dicts) into
    a list of dicts (or dict of dicts) and then compares the list ignoring order."""
    msg = PASS
    example_item = list(expected.values())[0]
    if isinstance(example_item, (list, tuple)):
        val = is_flippable(actual)
        if val != PASS:
            msg = "expected to find lists of length %d, but " % (len(example_item)) + val
            return msg
        msg = list_compare_unordered(flip_dict_of_lists(expected), flip_dict_of_lists(actual), "lists")
    elif isinstance(example_item, dict):
        expected_keys = list(example_item.keys())
        for key in actual:
            val = list_compare_unordered(expected_keys, list(actual[key].keys()), "dictionary %s" % key)
            if val != PASS:
                return val
        for cat_key in expected_keys:
            expected_category = {}
            actual_category = {}
            for key in expected:
                expected_category[key] = expected[key][cat_key]
                actual_category[key] = actual[key][cat_key]
            val = list_compare_unordered(flip_dict_of_lists(expected_category), flip_dict_of_lists(actual_category), "category " + repr(cat_key))
            if val != PASS:
                return val
    return msg


def get_expected_tables():
    """get_expected_tables() reads the html file with the expected DataFrames
    and returns a dict mapping each question to a html table."""
    if not os.path.exists(DF_FILE):
        return None

    expected_tables = {}
    f = open(DF_FILE, encoding='utf-8')
    soup = bs4.BeautifulSoup(f.read(), 'html.parser')
    f.close()

    tables = soup.find_all('table')
    for table in tables:
        expected_tables[table.get("data-question")] = table

    return expected_tables

def parse_table(table):
    """parse_table(table) takes in a table as a html string and returns
    a dict mapping each row and column index to the value at that position."""
    rows = []
    for tr in table.find_all('tr'):
        rows.append([])
        for cell in tr.find_all(['td', 'th']):
            rows[-1].append(cell.get_text().strip("\n "))

    cells = {}
    for r in range(1, len(rows)):
        for c in range(1, len(rows[0])):
            rname = rows[r][0]
            cname = rows[0][c]
            cells[(rname,cname)] = rows[r][c]
    return cells


def get_expected_namedtuples():
    """get_expected_namedtuples() defines the required namedtuple objects
    globally. It also returns a tuple of the classes."""
    expected_namedtuples = []
    
    global Star
    try:
        star_attributes = ['spectral_type', 'stellar_effective_temperature', 'stellar_radius', 'stellar_mass', 'stellar_luminosity', 'stellar_surface_gravity', 'stellar_age']
        Star = namedtuple('Star', star_attributes)
    except:
        pass
    expected_namedtuples.append(Star)
    global Planet
    try:
        planets_attributes = ['planet_name', 'host_name', 'discovery_method', 'discovery_year', 'controversial_flag', 'orbital_period', 'planet_radius', 'planet_mass', 'semi_major_radius', 'eccentricity', 'equilibrium_temperature', 'insolation_flux']
        Planet = namedtuple('Planet', planets_attributes)
    except:
        pass
    expected_namedtuples.append(Planet)
    return tuple(expected_namedtuples)

_expected_namedtuples = get_expected_namedtuples()


def parse_df(item):
    """parse_df(item) takes in a DataFrame input in any format (i.e, a DataFrame, or as html string)
    and extracts the table in the DataFrame as a bs4.BeautifulSoup object"""
    if isinstance(item, (pd.Series)):
        item = pd.DataFrame(item)
    if isinstance(item, (pd.DataFrame)):
        item = item.to_html()
    if isinstance(item, (str)):
        item = bs4.BeautifulSoup(item, 'html.parser').find('table')
    if isinstance(item, (bs4.element.Tag)):
        return item
    return "item could not be parsed"


def parse_cells(cells):
    """parse_cells(cells) takes in DataFrame cells as input and returns a DataFrame object"""
    table = {}
    for idx in cells:
        if idx[1] not in table:
            table[idx[1]] = {}
        table[idx[1]][idx[0]] = cells[idx]
    return pd.DataFrame(table)


def compare_cell_html(expected_cells, actual_cells):
    """compare_cell_html(expected_cells, actual_cells) is used to compare all the cells
    of two DataFrames."""
    expected_cols = list(set(["column %s" % (loc[1]) for loc in expected_cells]))
    actual_cols = list(set(["column %s" % (loc[1]) for loc in actual_cells]))
    msg = list_compare_unordered(expected_cols, actual_cols, "DataFrame")
    if msg != PASS:
        return msg

    expected_rows = list(set(["row index %s" % (loc[0]) for loc in expected_cells]))
    actual_rows = list(set(["row index %s" % (loc[0]) for loc in actual_cells]))
    msg = list_compare_unordered(expected_rows, actual_rows, "DataFrame")
    if msg != PASS:
        return msg

    for location, expected in expected_cells.items():
        location_name = "column {} at index {}".format(location[1], location[0])
        actual = actual_cells.get(location, None)
        if actual == None:
            return "in %s, expected to find %s" % (location_name, repr(expected))
        try:
            actual_ans = float(actual)
            expected_ans = float(expected)
            if math.isnan(actual_ans) and math.isnan(expected_ans):
                continue
        except Exception as e:
            actual_ans, expected_ans = actual, expected
        msg = simple_compare(expected_ans, actual_ans)
        if msg != PASS:
            return "in %s, " % location_name + msg
    return PASS


def table_compare_ordered(expected, actual):
    """table_compare_ordered(expected, actual) is used to compare when the
    expected answer is a DataFrame where the order of the indices matter."""
    try:
        expected_table = parse_df(expected)
        actual_table = parse_df(actual)
    except Exception as e:
        return "expected to find type DataFrame but found type %s instead" % type(actual).__name__
    
    if not isinstance(expected_table, (bs4.element.Tag)) or not isinstance(actual_table, (bs4.element.Tag)):
        return "expected to find type DataFrames but found types %s and %s instead" % (type(expected).__name__, type(actual).__name__)
    expected_cells = parse_table(expected_table)
    actual_cells = parse_table(actual_table)
    return compare_cell_html(expected_cells, actual_cells)


def table_compare_unordered(expected, actual):
    """table_compare_unordered(expected, actual) is used to compare when the
    expected answer is a DataFrame where the order of the indices do not matter."""
    try:
        expected_table = parse_df(expected)
        actual_table = parse_df(actual)
    except Exception as e:
        return "expected to find type DataFrame but found type %s instead" % type(actual).__name__
    
    if not isinstance(expected_table, (bs4.element.Tag)) or not isinstance(actual_table, (bs4.element.Tag)):
        return "expected to find type DataFrames but found types %s and %s instead" % (type(expected).__name__, type(actual).__name__)
    expected_cells = parse_table(expected_table)
    actual_cells = parse_table(actual_table)
    
    new_expected = parse_cells(expected_cells)
    new_actual = parse_cells(actual_cells)
    
    new_expected = new_expected.sort_values(by=list(new_expected.columns)).reset_index(drop=True)
    new_actual = new_actual.sort_values(by=list(new_expected.columns)).reset_index(drop=True)[list(new_expected.columns)]
    
    return table_compare_ordered(new_expected, new_actual)


def get_expected_plots():
    """get_expected_plots() reads the json file with the expected plot data
    and returns a dict mapping each question to a dictionary with the plots data."""
    if not os.path.exists(PLOT_FILE):
        return None

    f = open(PLOT_FILE, encoding='utf-8')
    expected_plots = json.load(f)
    f.close()
    return expected_plots


def compare_file_json(expected, actual):
    """compare_file_json(expected, actual) is used to compare when the
    expected answer is a JSON file."""
    msg = PASS
    if not os.path.isfile(expected):
        return "file %s not found; make sure it is downloaded and stored in the correct directory" % (expected)
    elif not os.path.isfile(actual):
        return "file %s not found; make sure that you have created the file with the correct name" % (actual)
    try:
        e = open(expected, encoding='utf-8')
        expected_data = json.load(e)
        e.close()
    except json.JSONDecodeError:
        return "file %s is broken and cannot be parsed; please delete and redownload the file correctly" % (expected)
    try:
        a = open(actual, encoding='utf-8')
        actual_data = json.load(a)
        a.close()
    except json.JSONDecodeError:
        return "file %s is broken and cannot be parsed" % (actual)
    if isinstance(expected_data, list):
        msg = list_compare_ordered(expected_data, actual_data, 'file ' + actual)
    elif isinstance(expected_data, dict):
        msg = dict_compare(expected_data, actual_data)
    return msg


_expected_json = get_expected_json()
_special_json = get_special_json()
_expected_plots = get_expected_plots()
_expected_tables = get_expected_tables()
_expected_format = get_expected_format()

def check(qnum, actual):
    """check(qnum, actual) is used to check if the answer in the notebook is
    the correct answer, and provide useful feedback if the answer is incorrect."""
    msg = PASS
    error_msg = "<b style='color: red;'>ERROR:</b> "
    q_format = _expected_format[qnum]

    if q_format == TEXT_FORMAT_SPECIAL_ORDERED_LIST:
        expected = _special_json[qnum]
    elif q_format == PNG_FORMAT_SCATTER:
        if _expected_plots == None:
            msg = error_msg + "file %s not parsed; make sure it is downloaded and stored in the correct directory" % (PLOT_FILE)
        else:
            expected = _expected_plots[qnum]
    elif q_format in [HTML_FORMAT_ORDERED, HTML_FORMAT_UNORDERED]:
        if _expected_tables == None:
            msg = error_msg + "file %s not parsed; make sure it is downloaded and stored in the correct directory" % (DF_FILE)
        else:
            expected = _expected_tables[qnum]
    else:
        expected = _expected_json[qnum]

    if msg != PASS:
        print(msg)
    else:
        msg = compare(expected, actual, q_format)
        if msg != PASS:
            msg = error_msg + msg
        print(msg)


def reset_hidden_tests():
    """reset_hidden_tests() resets all hidden tests on the Gradescope autograder where the hidden test file exists"""
    if not os.path.exists(HIDDEN_FILE):
        return
    hidn.reset_hidden_tests()

def rubric_check(rubric_point):
    """rubric_check(rubric_point) uses the hidden test file on the Gradescope autograder to grade the `rubric_point`"""
    if not os.path.exists(HIDDEN_FILE):
        print(PASS)
        return
    error_msg_1 = "ERROR: "
    error_msg_2 = "TEST DETAILS: "
    try:
        msg = hidn.rubric_check(rubric_point)
    except:
        msg = "hidden tests crashed before execution"
    if msg != PASS:
        hidn.make_deductions(rubric_point)
        if msg == "hidden tests crashed before execution":
            comment = "This is most likely due to a bug in the autograder, or due to code in your notebook"
            comment += "\nthat does not meet our specifications. Please contact the TAs to get this resolved."
            link = "INSTRUCTIONS FOR COURSE STAFF: to debug, execute the following code in the test environment"
            link += "\nin a cell anywhere in this notebook:"
            link += "\n`public_tests.hidn.rubric_check('%s')`" % (rubric_point)
        else:
            comment = hidn.get_comment(rubric_point)
            link = "<a href=%s>TEST DIRECTORY LINK FOR COURSE STAFF</a>" % (hidn.get_directory_link(rubric_point))
        msg = error_msg_1 + msg
        if comment != "":
            msg = msg + "\n" + error_msg_2 + comment
        msg = msg + "\n" + link
    print(msg)

def get_summary():
    """get_summary() returns the summary of the notebook using the hidden test file on the Gradescope autograder"""
    try:
        if not os.path.exists(HIDDEN_FILE):
            print("Total Score: %d/%d" % (TOTAL_SCORE, TOTAL_SCORE))
            return
        print(hidn.get_deduction_string())
    except:
        print("hidden tests crashed before execution")

def display_late_days_used():
    """display_late_days_used() prints details about the number of late days used by the student"""
    if not os.path.exists(HIDDEN_FILE):
        print()
        return
    hidn.display_late_days_used()


def identify_nb():
    """identify_nb() identifies the name of the project `.ipynb` file that is tested by this file"""
    for file in os.listdir():
        if not file.endswith(".ipynb"):
            continue
        project_name = file.split(".")[0].lower().strip()
        if not (project_name.startswith("p") or project_name.startswith("lab-p")):
            continue
        project_num = project_name.replace("lab-p", "").replace("p", "")
        if not (project_num.isnumeric() and 1 <= int(project_num) <= 13):
            continue
        return file



import nbformat

def get_score_digit(digit):
    """get_score_digit(digit) returns the `digit` of the score using the hidden test file on the Gradescope autograder"""
    try:
        file = identify_nb()
        if file == None:
            return 0
        with open(file, encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=nbformat.NO_CONVERT)
        if nb['cells'][0]['cell_type'] == "raw" and nb['cells'][0]['source'].startswith("# ASSIGNMENT CONFIG"):
            return 1
        elif not os.path.exists(HIDDEN_FILE):
            return 0
        score = hidn.get_score()
        digits = bin(score)[2:]
        digits = "0"*(7 - len(digits)) + digits
        return int(digits[6 - digit])
    except:
        return 0


# -

def detect_public_tests():
    '''detect_public_tests() updates the `deductions` variable if there are any references to `public_tests` in `FILE`
    other than the `import public_tests`'''
    try:
        file = identify_nb()
        with open(file, encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=nbformat.NO_CONVERT)
        if nb['cells'][0]['cell_type'] == "raw" and nb['cells'][0]['source'].startswith("# ASSIGNMENT CONFIG"):
            return
        if hidn.detect_public_tests():
            hidn.deductions = {'unexpected references to `public_tests` in notebook': hidn.TOTAL_SCORE}
    except:
        pass
