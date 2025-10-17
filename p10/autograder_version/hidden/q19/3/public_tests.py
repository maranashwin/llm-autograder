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
    expected_format = {'q1': 'TEXT_FORMAT_ORDERED_LIST',
                       'q2': 'TEXT_FORMAT_ORDERED_LIST_SLASHES',
                       'q3': 'TEXT_FORMAT_ORDERED_LIST_SLASHES',
                       'q4': 'TEXT_FORMAT_ORDERED_LIST_SLASHES',
                       'Star': 'TEXT_FORMAT_NAMEDTUPLE',
                       'q5': 'TEXT_FORMAT_NAMEDTUPLE',
                       'q6': 'TEXT_FORMAT_NAMEDTUPLE',
                       'q7': 'TEXT_FORMAT',
                       'q8': 'TEXT_FORMAT',
                       'q9': 'TEXT_FORMAT',
                       'q10': 'TEXT_FORMAT',
                       'q11': 'TEXT_FORMAT',
                       'Planet': 'TEXT_FORMAT_NAMEDTUPLE',
                       'q12': 'TEXT_FORMAT_NAMEDTUPLE',
                       'q13': 'TEXT_FORMAT_ORDERED_LIST',
                       'q14': 'TEXT_FORMAT_ORDERED_LIST',
                       'q15': 'TEXT_FORMAT_ORDERED_LIST',
                       'q16': 'TEXT_FORMAT_ORDERED_LIST',
                       'q17': 'TEXT_FORMAT',
                       'q18': 'TEXT_FORMAT_NAMEDTUPLE',
                       'q19': 'TEXT_FORMAT',
                       'q20': 'TEXT_FORMAT_UNORDERED_LIST'}
    return expected_format


def get_expected_json():
    """get_expected_json() returns a dict mapping each question to the expected
    answer (if the format permits it)."""
    expected_json = {'q1': ['stars_5.csv',
                            'stars_4.csv',
                            'stars_3.csv',
                            'stars_2.csv',
                            'stars_1.csv',
                            'planets_5.csv',
                            'planets_4.csv',
                            'planets_3.csv',
                            'planets_2.csv',
                            'planets_1.csv',
                            'mapping_5.json',
                            'mapping_4.json',
                            'mapping_3.json',
                            'mapping_2.json',
                            'mapping_1.json'],
                     'q2': ['data/stars_5.csv',
                            'data/stars_4.csv',
                            'data/stars_3.csv',
                            'data/stars_2.csv',
                            'data/stars_1.csv',
                            'data/planets_5.csv',
                            'data/planets_4.csv',
                            'data/planets_3.csv',
                            'data/planets_2.csv',
                            'data/planets_1.csv',
                            'data/mapping_5.json',
                            'data/mapping_4.json',
                            'data/mapping_3.json',
                            'data/mapping_2.json',
                            'data/mapping_1.json'],
                     'q3': ['data/stars_5.csv',
                            'data/stars_4.csv',
                            'data/stars_3.csv',
                            'data/stars_2.csv',
                            'data/stars_1.csv',
                            'data/planets_5.csv',
                            'data/planets_4.csv',
                            'data/planets_3.csv',
                            'data/planets_2.csv',
                            'data/planets_1.csv'],
                     'q4': ['data/stars_5.csv',
                            'data/stars_4.csv',
                            'data/stars_3.csv',
                            'data/stars_2.csv',
                            'data/stars_1.csv'],
                     'Star': Star(spectral_type='G2 V', stellar_effective_temperature=5780.0, stellar_radius=1.0, stellar_mass=1.0, stellar_luminosity=0.0, stellar_surface_gravity=4.44, stellar_age=4.6),
                     'q5': Star(spectral_type='LI', stellar_effective_temperature=3865.8887187394666, stellar_radius=20.46233742769732, stellar_mass=0.2756746988900671, stellar_luminosity=1.3858207084942482, stellar_surface_gravity=0.7603437255820258, stellar_age=9.495359506438376),
                     'q6': Star(spectral_type='WIV-II', stellar_effective_temperature=2903.973644923211, stellar_radius=20.03802282578992, stellar_mass=1.4861013889418764, stellar_luminosity=0.3483975684121265, stellar_surface_gravity=7.344887225531718, stellar_age=7.621928624673455),
                     'q7': -0.31612426656449427,
                     'q8': 6.937863129795238,
                     'q9': 4922.761040631202,
                     'q10': 'TOI-5544',
                     'q11': 5.835083656539453,
                     'Planet': Planet(planet_name='Jupiter', host_name='Sun', discovery_method='Imaging', discovery_year=1610, controversial_flag=False, orbital_period=4333.0, planet_radius=11.209, planet_mass=317.828, semi_major_radius=5.2038, eccentricity=0.0489, equilibrium_temperature=110, insolation_flux=0.0345),
                     'q12': Planet(planet_name='EPIC-5553 a', host_name='EPIC-5553', discovery_method='Pulsar Timing', discovery_year=2021, controversial_flag=True, orbital_period=46.1593235262535, planet_radius=1.5848939317758095, planet_mass=4394.227723946089, semi_major_radius=179.91423766766638, eccentricity=0.08525697399338479, equilibrium_temperature=1364.234456127824, insolation_flux=1087.8727500497846),
                     'q13': [Planet(planet_name='tau 2365 a', host_name='tau 2365', discovery_method='Eclipse Timing Variations', discovery_year=2019, controversial_flag=False, orbital_period=1029.2656946889954, planet_radius=14.764563475524582, planet_mass=4840.974583382388, semi_major_radius=136.2470748927024, eccentricity=0.07577921305097338, equilibrium_temperature=962.4770263550236, insolation_flux=45.0414214315706),
                             Planet(planet_name='TOI 2641 1', host_name='TOI 2641', discovery_method='Orbital Brightness Modulation', discovery_year=2019, controversial_flag=True, orbital_period=822.0621526777919, planet_radius=6.476707634215975, planet_mass=6042.129912314014, semi_major_radius=149.63942181590068, eccentricity=0.024864921612507165, equilibrium_temperature=1493.6154370789368, insolation_flux=1335.4802360995955),
                             Planet(planet_name='TOI-4626 1', host_name='TOI-4626', discovery_method='Pulsation Timing Variations', discovery_year=2022, controversial_flag=True, orbital_period=621.8077261984363, planet_radius=20.45775333913057, planet_mass=6534.579929136208, semi_major_radius=167.6943117079723, eccentricity=0.027786674761922387, equilibrium_temperature=2442.3072091598324, insolation_flux=2105.9125735093244),
                             Planet(planet_name='EPIC 2547 1', host_name='EPIC 2547', discovery_method='Transit Timing Variations', discovery_year=2017, controversial_flag=True, orbital_period=281.1135110683415, planet_radius=3.852791931335571, planet_mass=8289.546431376022, semi_major_radius=177.39989796790658, eccentricity=0.08488965905756145, equilibrium_temperature=843.6440631203004, insolation_flux=1715.9489188830148),
                             Planet(planet_name='gam 1107 a', host_name='gam 1107', discovery_method='Transit', discovery_year=2019, controversial_flag=True, orbital_period=829.0030558544381, planet_radius=18.952204098293038, planet_mass=8724.41873633525, semi_major_radius=138.9026248265347, eccentricity=0.05646626008543592, equilibrium_temperature=634.3718616116103, insolation_flux=458.5975868075301)],
                     'q14': [Planet(planet_name='eps 6816 a', host_name='eps 6816', discovery_method='Pulsar Timing', discovery_year=2020, controversial_flag=True, orbital_period=458.26945546740285, planet_radius=19.04835366303986, planet_mass=1056.5871494506928, semi_major_radius=113.46587896702042, eccentricity=0.03477522354369716, equilibrium_temperature=1860.6876887427911, insolation_flux=1324.5280273896951),
                             Planet(planet_name='Kepler-1138 2', host_name='Kepler-1138', discovery_method='Pulsar Timing', discovery_year=2020, controversial_flag=True, orbital_period=414.84156525290734, planet_radius=13.740501559325871, planet_mass=11087.550513867925, semi_major_radius=224.57001941449278, eccentricity=0.04897684266713177, equilibrium_temperature=42.25718023708873, insolation_flux=828.5520313575139),
                             Planet(planet_name='TOI 9944 a', host_name='TOI 9944', discovery_method='Orbital Brightness Modulation', discovery_year=2021, controversial_flag=True, orbital_period=271.47908325723307, planet_radius=26.391127038937157, planet_mass=5740.109366669059, semi_major_radius=170.5356048077218, eccentricity=0.048514693521541655, equilibrium_temperature=1708.397957806646, insolation_flux=651.7255163074612),
                             Planet(planet_name='TOI 9944 b', host_name='TOI 9944', discovery_method='Astrometry', discovery_year=2020, controversial_flag=True, orbital_period=144.85955478070855, planet_radius=15.105621135553683, planet_mass=4854.406452921652, semi_major_radius=83.30663778340042, eccentricity=0.05156249859960048, equilibrium_temperature=1653.7007391552015, insolation_flux=950.0043255333753),
                             Planet(planet_name='omi 7204 1', host_name='omi 7204', discovery_method='Orbital Brightness Modulation', discovery_year=2021, controversial_flag=True, orbital_period=910.4051872547869, planet_radius=20.306328781198935, planet_mass=2536.3609133469927, semi_major_radius=158.79730438101723, eccentricity=0.0915874173966584, equilibrium_temperature=995.3943392652913, insolation_flux=1861.0961278204359),
                             Planet(planet_name='gam1-1792 1', host_name='gam1-1792', discovery_method='Transit Timing Variations', discovery_year=2016, controversial_flag=True, orbital_period=226.5213835240524, planet_radius=4.1914593334954535, planet_mass=5215.9689326959115, semi_major_radius=146.17436570003028, eccentricity=0.051058054823380786, equilibrium_temperature=1545.9120317705463, insolation_flux=702.8866662581787),
                             Planet(planet_name='omi-62443 b', host_name='omi-62443', discovery_method='Transit Timing Variations', discovery_year=2017, controversial_flag=True, orbital_period=647.916719065756, planet_radius=11.525043557438606, planet_mass=2185.0420020099473, semi_major_radius=47.86132302671231, eccentricity=0.07173804069818521, equilibrium_temperature=805.9716128213499, insolation_flux=1493.9111440203828),
                             Planet(planet_name='CoRoT-7058 2', host_name='CoRoT-7058', discovery_method='Imaging', discovery_year=2019, controversial_flag=True, orbital_period=398.0083766705231, planet_radius=16.480477133474906, planet_mass=11274.48016257236, semi_major_radius=25.9441818102096, eccentricity=0.03733704876244022, equilibrium_temperature=906.3636940904597, insolation_flux=547.1494006732722),
                             Planet(planet_name='iot 8598 1', host_name='iot 8598', discovery_method='Transit', discovery_year=2021, controversial_flag=True, orbital_period=335.96010464929054, planet_radius=1.2483831268812136, planet_mass=6553.213974369669, semi_major_radius=47.083444510046604, eccentricity=0.06588123234645994, equilibrium_temperature=712.3152239784421, insolation_flux=1329.2093643141998),
                             Planet(planet_name='EPIC-5812 a', host_name='EPIC-5812', discovery_method='Radial Velocity', discovery_year=2016, controversial_flag=True, orbital_period=843.3766675929496, planet_radius=11.00736597248639, planet_mass=7534.642847910425, semi_major_radius=94.40060617696591, eccentricity=0.07915064574641424, equilibrium_temperature=1946.5297709537163, insolation_flux=335.0674798259606),
                             Planet(planet_name='EPIC-5812 b', host_name='EPIC-5812', discovery_method='Radial Velocity', discovery_year=2014, controversial_flag=True, orbital_period=364.7085322180229, planet_radius=11.825285720887264, planet_mass=1219.8420999115947, semi_major_radius=45.752831927632, eccentricity=0.07242676971548326, equilibrium_temperature=1464.5202094632104, insolation_flux=224.80845661847798),
                             Planet(planet_name='alf 249 2', host_name='alf 249', discovery_method='Pulsar Timing', discovery_year=2020, controversial_flag=True, orbital_period=284.80165798081, planet_radius=11.062268794671565, planet_mass=4562.288719653147, semi_major_radius=69.44285354361926, eccentricity=0.08367527379550643, equilibrium_temperature=1184.4649997799174, insolation_flux=1834.141333286001),
                             Planet(planet_name='iot 70306 1', host_name='iot 70306', discovery_method='Pulsar Timing', discovery_year=2020, controversial_flag=True, orbital_period=120.8263799334195, planet_radius=8.05469147981793, planet_mass=5025.1066360327195, semi_major_radius=57.504509614242636, eccentricity=0.061614695347664686, equilibrium_temperature=501.6974549437067, insolation_flux=1752.7603279387845),
                             Planet(planet_name='iot 70306 2', host_name='iot 70306', discovery_method='Pulsation Timing Variations', discovery_year=2022, controversial_flag=True, orbital_period=68.45376116194512, planet_radius=9.2175699292826, planet_mass=4812.8478340020965, semi_major_radius=88.95522303154318, eccentricity=0.027533616706820755, equilibrium_temperature=1810.9174586030847, insolation_flux=573.1845661293646),
                             Planet(planet_name='xi 9329 1', host_name='xi 9329', discovery_method='Radial Velocity', discovery_year=2015, controversial_flag=True, orbital_period=392.0828913897344, planet_radius=4.596645740846388, planet_mass=8693.817718536182, semi_major_radius=140.424697605169, eccentricity=0.03528269554696145, equilibrium_temperature=990.7944526333074, insolation_flux=1227.7001853823476),
                             Planet(planet_name='eps 2231 2', host_name='eps 2231', discovery_method='Imaging', discovery_year=2021, controversial_flag=True, orbital_period=425.8407017066784, planet_radius=9.218327198001235, planet_mass=3111.7093764950223, semi_major_radius=107.28966462833232, eccentricity=0.03684314100577091, equilibrium_temperature=924.7034524988079, insolation_flux=1998.4401129778573),
                             Planet(planet_name='bet 6893 1', host_name='bet 6893', discovery_method='Imaging', discovery_year=2018, controversial_flag=True, orbital_period=224.41396693580168, planet_radius=7.6919342345288815, planet_mass=6402.864836313296, semi_major_radius=109.32799915208801, eccentricity=0.032274928702433536, equilibrium_temperature=1284.123663931738, insolation_flux=1163.5856584643193),
                             Planet(planet_name='eps 7294 a', host_name='eps 7294', discovery_method='Pulsar Timing', discovery_year=2019, controversial_flag=True, orbital_period=89.67046508039732, planet_radius=5.102777975158691, planet_mass=2293.2653884306887, semi_major_radius=133.54054889093237, eccentricity=0.06521257309290122, equilibrium_temperature=1219.3013586766235, insolation_flux=1362.0901169188999),
                             Planet(planet_name='tau 47172 1', host_name='tau 47172', discovery_method='Imaging', discovery_year=2019, controversial_flag=True, orbital_period=434.43058754940716, planet_radius=15.650287362307184, planet_mass=3736.002395444176, semi_major_radius=147.6228820759818, eccentricity=0.06695283541789467, equilibrium_temperature=1775.4289306567425, insolation_flux=1132.0187446117507),
                             Planet(planet_name='CoRoT-3395 b', host_name='CoRoT-3395', discovery_method='Radial Velocity', discovery_year=2018, controversial_flag=True, orbital_period=532.2147557818926, planet_radius=1.5404273158868431, planet_mass=4275.294032725654, semi_major_radius=93.35066724902805, eccentricity=0.058479048028834274, equilibrium_temperature=953.2387654698839, insolation_flux=1750.8063776884715),
                             Planet(planet_name='BD 162 1', host_name='BD 162', discovery_method='Pulsation Timing Variations', discovery_year=2016, controversial_flag=True, orbital_period=701.0254683396074, planet_radius=6.48349739137603, planet_mass=4280.003936120727, semi_major_radius=38.602083112048824, eccentricity=0.046025031467575445, equilibrium_temperature=1456.2777461575877, insolation_flux=964.6843155008105),
                             Planet(planet_name='tau-92080 a', host_name='tau-92080', discovery_method='Eclipse Timing Variations', discovery_year=2015, controversial_flag=True, orbital_period=773.6845965163922, planet_radius=3.1183174780714538, planet_mass=5865.770582885168, semi_major_radius=89.34594952583068, eccentricity=0.07835249744127198, equilibrium_temperature=1164.0846534042753, insolation_flux=1081.0371923102784),
                             Planet(planet_name='kap-7937 a', host_name='kap-7937', discovery_method='Eclipse Timing Variations', discovery_year=2020, controversial_flag=True, orbital_period=705.6130575855691, planet_radius=12.715427195898421, planet_mass=3476.76733623941, semi_major_radius=87.3798669807399, eccentricity=0.08248221736795663, equilibrium_temperature=822.3626904952424, insolation_flux=1481.820462808688),
                             Planet(planet_name='eps 1792 1', host_name='eps 1792', discovery_method='Eclipse Timing Variations', discovery_year=2016, controversial_flag=True, orbital_period=689.8716673954195, planet_radius=4.220431704178043, planet_mass=1458.7148619994673, semi_major_radius=129.52669943799881, eccentricity=0.023762328506936388, equilibrium_temperature=1533.8634536751179, insolation_flux=1200.606481749247),
                             Planet(planet_name='eps 1792 2', host_name='eps 1792', discovery_method='Transit', discovery_year=2015, controversial_flag=True, orbital_period=809.296856770369, planet_radius=11.523426778872478, planet_mass=81.651701684199, semi_major_radius=150.7414776260836, eccentricity=0.019859870881388558, equilibrium_temperature=954.9910498416227, insolation_flux=1704.8629128796806)],
                     'q15': [Planet(planet_name='WASP 2676 d', host_name='WASP 2676', discovery_method='Microlensing', discovery_year=2018, controversial_flag=False, orbital_period=437.22032845944926, planet_radius=18.638217814163195, planet_mass=8349.233642105813, semi_major_radius=101.22217713975783, eccentricity=0.08432217720606902, equilibrium_temperature=684.8598316781032, insolation_flux=421.34973639607676),
                             Planet(planet_name='xi 6367 1', host_name='xi 6367', discovery_method='Astrometry', discovery_year=2017, controversial_flag=True, orbital_period=119.3945343338217, planet_radius=4.837178118632626, planet_mass=6914.606779910675, semi_major_radius=56.24592937956605, eccentricity=0.06738607316577402, equilibrium_temperature=1187.0406977334126, insolation_flux=1195.775313132928),
                             Planet(planet_name='xi 6367 2', host_name='xi 6367', discovery_method='Microlensing', discovery_year=2021, controversial_flag=False, orbital_period=704.2941879621352, planet_radius=21.038118535122308, planet_mass=2848.4054981929025, semi_major_radius=137.4411266424632, eccentricity=0.052505789072644554, equilibrium_temperature=1375.4834245606567, insolation_flux=943.0708688868399),
                             Planet(planet_name='xi 6367 3', host_name='xi 6367', discovery_method='Pulsar Timing', discovery_year=2017, controversial_flag=True, orbital_period=304.3828951648426, planet_radius=17.81193548106439, planet_mass=5535.531839341543, semi_major_radius=95.36806361351503, eccentricity=0.03999931727122663, equilibrium_temperature=579.3203777230844, insolation_flux=1213.0564429221247),
                             Planet(planet_name='xi 6367 4', host_name='xi 6367', discovery_method='Transit', discovery_year=2019, controversial_flag=False, orbital_period=183.2346580147231, planet_radius=5.886013296819295, planet_mass=2177.5057794969975, semi_major_radius=123.96639068993322, eccentricity=0.14848438332800978, equilibrium_temperature=1468.797186259129, insolation_flux=1529.3565490468263)],
                     'q16': [],
                     'q17': 0,
                     'q18': Star(spectral_type='T5.5/V', stellar_effective_temperature=9002.032485397174, stellar_radius=12.358737006822722, stellar_mass=0.9358292753967201, stellar_luminosity=0.5360563139050141, stellar_surface_gravity=3.6738201826460672, stellar_age=9.332731055968093),
                     'q19': 100.0}
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
