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
                     'q5': Star(spectral_type='B2.75IV', stellar_effective_temperature=6878.059400549619, stellar_radius=17.895013409196093, stellar_mass=4.290970589401139, stellar_luminosity=-1.6947628930306733, stellar_surface_gravity=4.742878544773978, stellar_age=11.500992382198184),
                     'q6': Star(spectral_type='D8.5VI-V', stellar_effective_temperature=6824.694489891323, stellar_radius=2.9222540434216704, stellar_mass=4.498333539411475, stellar_luminosity=0.5326959698501146, stellar_surface_gravity=2.1503293818438225, stellar_age=8.016523041643135),
                     'q7': -0.11958093687238215,
                     'q8': 5.826081948559761,
                     'q9': 6420.011365321795,
                     'q10': 'psi1 8794',
                     'q11': 7.628571428571428,
                     'Planet': Planet(planet_name='Jupiter', host_name='Sun', discovery_method='Imaging', discovery_year=1610, controversial_flag=False, orbital_period=4333.0, planet_radius=11.209, planet_mass=317.828, semi_major_radius=5.2038, eccentricity=0.0489, equilibrium_temperature=110, insolation_flux=0.0345),
                     'q12': Planet(planet_name='mu2-5657 a', host_name='mu2-5657', discovery_method='Disk Kinematics', discovery_year=2015, controversial_flag=False, orbital_period=1027.3675304698068, planet_radius=8.88160690740167, planet_mass=9751.750411961919, semi_major_radius=109.63713763904049, eccentricity=0.04649598493010953, equilibrium_temperature=1001.2997360005292, insolation_flux=760.4740928953036),
                     'q13': [Planet(planet_name='BD-4509 1', host_name='BD-4509', discovery_method='Transit', discovery_year=2016, controversial_flag=False, orbital_period=409.47253028663886, planet_radius=2.8021954982282082, planet_mass=7949.383854445274, semi_major_radius=192.13472917822537, eccentricity=0.024103072040258775, equilibrium_temperature=1576.9938885147135, insolation_flux=929.4339486123549),
                             Planet(planet_name='kap 14468 a', host_name='kap 14468', discovery_method='Transit Timing Variations', discovery_year=2018, controversial_flag=False, orbital_period=403.6395087808586, planet_radius=8.888411086719772, planet_mass=204.71450637591533, semi_major_radius=162.8669041692744, eccentricity=0.06887994582601303, equilibrium_temperature=1560.6268033522404, insolation_flux=420.3970486790563),
                             Planet(planet_name='mu-47 1', host_name='mu-47', discovery_method='Imaging', discovery_year=2018, controversial_flag=False, orbital_period=360.53476862868644, planet_radius=14.964891615205632, planet_mass=8994.486054685636, semi_major_radius=143.69051019707354, eccentricity=0.06493462583255409, equilibrium_temperature=1510.8935577007617, insolation_flux=321.1286427624599),
                             Planet(planet_name='tau-984 a', host_name='tau-984', discovery_method='Pulsar Timing', discovery_year=2018, controversial_flag=False, orbital_period=292.0491673436899, planet_radius=9.449900167815738, planet_mass=3490.2390006193523, semi_major_radius=170.55199782153457, eccentricity=0.08575352317682067, equilibrium_temperature=1533.784863431652, insolation_flux=328.44128205404206),
                             Planet(planet_name='eps-3178 1', host_name='eps-3178', discovery_method='Imaging', discovery_year=2022, controversial_flag=False, orbital_period=216.04549757385593, planet_radius=16.821352722880988, planet_mass=9596.764510623923, semi_major_radius=24.935174626488006, eccentricity=0.04845197803666051, equilibrium_temperature=801.8918782009032, insolation_flux=822.2252639548954)],
                     'q14': [Planet(planet_name='HD 7594 b', host_name='HD 7594', discovery_method='Astrometry', discovery_year=2020, controversial_flag=True, orbital_period=657.3115981598453, planet_radius=14.99362970380065, planet_mass=2863.304367292206, semi_major_radius=11.853506319301943, eccentricity=0.06427878694519609, equilibrium_temperature=874.7376421795066, insolation_flux=1191.6796537519247),
                             Planet(planet_name='kap-9771 a', host_name='kap-9771', discovery_method='Pulsation Timing Variations', discovery_year=2017, controversial_flag=True, orbital_period=863.9405014319359, planet_radius=7.640308001129289, planet_mass=3056.5844536743666, semi_major_radius=219.68880733699197, eccentricity=0.0597214082073866, equilibrium_temperature=1196.5578584359414, insolation_flux=592.3041290952387),
                             Planet(planet_name='EPIC 9314 1', host_name='EPIC 9314', discovery_method='Transit Timing Variations', discovery_year=2015, controversial_flag=True, orbital_period=733.2126555066575, planet_radius=18.563148682014653, planet_mass=7501.127794433734, semi_major_radius=183.56518788967904, eccentricity=0.05530377241033817, equilibrium_temperature=1901.5313470809622, insolation_flux=1215.6969294500514),
                             Planet(planet_name='2MASS-692 a', host_name='2MASS-692', discovery_method='Orbital Brightness Modulation', discovery_year=2019, controversial_flag=True, orbital_period=482.6083785611577, planet_radius=12.610913138345657, planet_mass=6229.126806291673, semi_major_radius=25.056672284313905, eccentricity=0.09123792480868513, equilibrium_temperature=911.9166926720322, insolation_flux=1116.7261043500994),
                             Planet(planet_name='xi-3698 b', host_name='xi-3698', discovery_method='Transit', discovery_year=2017, controversial_flag=True, orbital_period=612.9330745673336, planet_radius=17.58154722031025, planet_mass=8291.315647770074, semi_major_radius=121.34392412748224, eccentricity=0.06004641018333458, equilibrium_temperature=1879.4571931291089, insolation_flux=2164.2104386368133),
                             Planet(planet_name='gam1 2658 b', host_name='gam1 2658', discovery_method='Microlensing', discovery_year=2022, controversial_flag=True, orbital_period=419.92022377153063, planet_radius=3.1959899386327573, planet_mass=6423.1547863829455, semi_major_radius=127.5096273123032, eccentricity=0.00223739732189579, equilibrium_temperature=612.7214121721361, insolation_flux=883.9332436190132),
                             Planet(planet_name='gam1 26117 a', host_name='gam1 26117', discovery_method='Microlensing', discovery_year=2017, controversial_flag=True, orbital_period=326.5958923889698, planet_radius=11.407732188712846, planet_mass=5472.369087752099, semi_major_radius=81.76784988130535, eccentricity=0.0018224631756621132, equilibrium_temperature=1052.6346621024766, insolation_flux=449.1383640062496),
                             Planet(planet_name='DP-87724 b', host_name='DP-87724', discovery_method='Transit Timing Variations', discovery_year=2019, controversial_flag=True, orbital_period=861.1238748939336, planet_radius=8.312367074295583, planet_mass=2177.0760208239753, semi_major_radius=153.50383924728263, eccentricity=0.10599307582608622, equilibrium_temperature=129.8589290391658, insolation_flux=733.3881313403169),
                             Planet(planet_name='BD-8794 1', host_name='BD-8794', discovery_method='Transit Timing Variations', discovery_year=2016, controversial_flag=True, orbital_period=648.9490091423847, planet_radius=1.5053474496261003, planet_mass=4449.74543499265, semi_major_radius=113.33391338379059, eccentricity=0.060951816692821584, equilibrium_temperature=991.0390080653774, insolation_flux=1351.2301933597523),
                             Planet(planet_name='tau 9701 2', host_name='tau 9701', discovery_method='Transit', discovery_year=2017, controversial_flag=True, orbital_period=633.0518933690516, planet_radius=14.909632863508179, planet_mass=2934.4556133149817, semi_major_radius=107.90309526530638, eccentricity=0.07927233381084084, equilibrium_temperature=1229.2847560363234, insolation_flux=2197.8025168259023),
                             Planet(planet_name='WASP 4347 1', host_name='WASP 4347', discovery_method='Pulsar Timing', discovery_year=2016, controversial_flag=True, orbital_period=773.9011246834484, planet_radius=6.843190590785839, planet_mass=3993.790820175467, semi_major_radius=182.77163260486088, eccentricity=0.0715153195316847, equilibrium_temperature=1125.1207180219187, insolation_flux=1173.1016291429364),
                             Planet(planet_name='CoRoT-18 a', host_name='CoRoT-18', discovery_method='Disk Kinematics', discovery_year=2014, controversial_flag=True, orbital_period=378.81305712953247, planet_radius=20.088157945422, planet_mass=7272.8149290716665, semi_major_radius=134.10368008025142, eccentricity=0.0691024555378024, equilibrium_temperature=1134.9847493277111, insolation_flux=1078.5154859740603),
                             Planet(planet_name='nu-5972 a', host_name='nu-5972', discovery_method='Pulsation Timing Variations', discovery_year=2020, controversial_flag=True, orbital_period=264.35234044944286, planet_radius=0.5340981815412036, planet_mass=4639.353045652045, semi_major_radius=208.6266444625325, eccentricity=0.04388872473835037, equilibrium_temperature=1623.5755670702906, insolation_flux=255.5450582547486),
                             Planet(planet_name='nu-5972 b', host_name='nu-5972', discovery_method='Imaging', discovery_year=2022, controversial_flag=True, orbital_period=760.4419261650079, planet_radius=6.226317471234936, planet_mass=4736.83875440881, semi_major_radius=108.64956845184096, eccentricity=0.05924084648985897, equilibrium_temperature=840.948679664554, insolation_flux=1466.6314077829097),
                             Planet(planet_name='rho 1101 2', host_name='rho 1101', discovery_method='Disk Kinematics', discovery_year=2022, controversial_flag=True, orbital_period=419.153110305323, planet_radius=18.869999005898435, planet_mass=6746.360937067202, semi_major_radius=59.16187055075317, eccentricity=0.02750774679125336, equilibrium_temperature=1308.2557110901344, insolation_flux=1636.106235621572),
                             Planet(planet_name='BD-6547 1', host_name='BD-6547', discovery_method='Pulsar Timing', discovery_year=2019, controversial_flag=True, orbital_period=450.78115798595763, planet_radius=13.6824951658546, planet_mass=7178.365507055161, semi_major_radius=104.57763628656376, eccentricity=0.04553349810614522, equilibrium_temperature=899.191023618046, insolation_flux=1705.6503744679567),
                             Planet(planet_name='mu2 8794 b', host_name='mu2 8794', discovery_method='Radial Velocity', discovery_year=2016, controversial_flag=True, orbital_period=342.79700979104166, planet_radius=7.742150939934908, planet_mass=1847.480200367444, semi_major_radius=65.41445896741999, eccentricity=0.06788457950020461, equilibrium_temperature=1395.7719348788974, insolation_flux=712.3213211642981),
                             Planet(planet_name='eps 7294 a', host_name='eps 7294', discovery_method='Radial Velocity', discovery_year=2019, controversial_flag=True, orbital_period=239.69352100360283, planet_radius=12.048295462320889, planet_mass=2346.192210869905, semi_major_radius=96.58884896505326, eccentricity=0.08824892913353449, equilibrium_temperature=1562.593179897919, insolation_flux=1501.3641592893014),
                             Planet(planet_name='eps 7294 b', host_name='eps 7294', discovery_method='Astrometry', discovery_year=2018, controversial_flag=True, orbital_period=130.65179034173207, planet_radius=3.614706224090323, planet_mass=1074.4899538817194, semi_major_radius=143.5121642336412, eccentricity=0.0011027261521474388, equilibrium_temperature=1989.422104340928, insolation_flux=347.03479282883984),
                             Planet(planet_name='alf 7685 b', host_name='alf 7685', discovery_method='Transit', discovery_year=2018, controversial_flag=True, orbital_period=460.62492349051763, planet_radius=23.272847834085503, planet_mass=5668.225824617045, semi_major_radius=173.82277106641982, eccentricity=0.04051990258653541, equilibrium_temperature=171.2201088761292, insolation_flux=610.2839385368368),
                             Planet(planet_name='bet-5832 a', host_name='bet-5832', discovery_method='Disk Kinematics', discovery_year=2017, controversial_flag=True, orbital_period=668.5517339702303, planet_radius=12.977958171267488, planet_mass=3619.5049503405708, semi_major_radius=157.59014108478183, eccentricity=0.06730251432089249, equilibrium_temperature=1031.9828506140375, insolation_flux=1081.9232478678593),
                             Planet(planet_name='psi1-2264 2', host_name='psi1-2264', discovery_method='Orbital Brightness Modulation', discovery_year=2017, controversial_flag=True, orbital_period=689.8637315344706, planet_radius=8.470693470240468, planet_mass=3336.7311983030127, semi_major_radius=109.60965708889574, eccentricity=0.049843885325130594, equilibrium_temperature=2063.2324726407464, insolation_flux=567.1856170383804),
                             Planet(planet_name='HD 6884 b', host_name='HD 6884', discovery_method='Radial Velocity', discovery_year=2019, controversial_flag=True, orbital_period=321.9999431794379, planet_radius=4.564063153458833, planet_mass=2352.1501837932838, semi_major_radius=221.402318730044, eccentricity=0.05646596690793595, equilibrium_temperature=669.2524317173176, insolation_flux=1674.43773927471),
                             Planet(planet_name='psi1-9305 a', host_name='psi1-9305', discovery_method='Orbital Brightness Modulation', discovery_year=2016, controversial_flag=True, orbital_period=541.6389484597001, planet_radius=6.541322948200641, planet_mass=2739.544661650737, semi_major_radius=52.053400571349236, eccentricity=0.04607994043240629, equilibrium_temperature=987.4039250611893, insolation_flux=387.95760785290304),
                             Planet(planet_name='gam1-352 b', host_name='gam1-352', discovery_method='Transit Timing Variations', discovery_year=2020, controversial_flag=True, orbital_period=519.7980527316379, planet_radius=14.157773230524455, planet_mass=6291.079903129178, semi_major_radius=161.89421196872345, eccentricity=0.06766447478267414, equilibrium_temperature=1214.675022750322, insolation_flux=1226.2806562206054),
                             Planet(planet_name='alf-3669 2', host_name='alf-3669', discovery_method='Transit Timing Variations', discovery_year=2015, controversial_flag=True, orbital_period=610.5613077731681, planet_radius=18.717884910799597, planet_mass=3508.7858308689833, semi_major_radius=63.9591167293692, eccentricity=0.05916936679617113, equilibrium_temperature=853.073493731126, insolation_flux=1717.439943517305),
                             Planet(planet_name='ups 23200 2', host_name='ups 23200', discovery_method='Transit Timing Variations', discovery_year=2022, controversial_flag=True, orbital_period=312.07687343214377, planet_radius=17.544037232833833, planet_mass=5567.932472762599, semi_major_radius=158.3351822800143, eccentricity=0.05568154873254389, equilibrium_temperature=667.0373211895834, insolation_flux=841.8164602502771)],
                     'q15': [Planet(planet_name='alf 6977 d', host_name='alf 6977', discovery_method='Orbital Brightness Modulation', discovery_year=2021, controversial_flag=False, orbital_period=454.25307484902356, planet_radius=19.092960114231257, planet_mass=5251.957737794978, semi_major_radius=177.9622409042675, eccentricity=0.030299673532040088, equilibrium_temperature=574.9277441449666, insolation_flux=1135.9117432542819),
                             Planet(planet_name='tau-4958 1', host_name='tau-4958', discovery_method='Transit', discovery_year=2018, controversial_flag=False, orbital_period=648.707202552739, planet_radius=17.793665148392385, planet_mass=5959.590508260599, semi_major_radius=82.23935430348547, eccentricity=0.08102974040475304, equilibrium_temperature=1726.9070512008375, insolation_flux=758.8552137779214),
                             Planet(planet_name='tau-4958 2', host_name='tau-4958', discovery_method='Astrometry', discovery_year=2021, controversial_flag=False, orbital_period=350.26548106329756, planet_radius=18.41224490677642, planet_mass=5085.627081040619, semi_major_radius=131.60399454996465, eccentricity=0.06496077464597842, equilibrium_temperature=271.0761744346379, insolation_flux=476.63228057831805),
                             Planet(planet_name='tau-4958 3', host_name='tau-4958', discovery_method='Disk Kinematics', discovery_year=2014, controversial_flag=False, orbital_period=1029.3162244620744, planet_radius=8.97349458162927, planet_mass=3764.817118383504, semi_major_radius=109.04171873782026, eccentricity=0.09468692210923746, equilibrium_temperature=403.7857894256781, insolation_flux=587.3051421981542),
                             Planet(planet_name='tau-4958 4', host_name='tau-4958', discovery_method='Microlensing', discovery_year=2016, controversial_flag=False, orbital_period=394.85272589323444, planet_radius=11.147239071902845, planet_mass=4863.751116841272, semi_major_radius=113.21303623644474, eccentricity=0.05323981547999862, equilibrium_temperature=1474.4687735999055, insolation_flux=1200.7898770911743)],
                     'q16': [],
                     'q17': 0,
                     'q18': Star(spectral_type='KI-', stellar_effective_temperature=7267.6703887608655, stellar_radius=37.942459390413745, stellar_mass=4.454865323338436, stellar_luminosity=1.0857738407772495, stellar_surface_gravity=0.9755212096588073, stellar_age=12.1),
                     'q19': 11.524797347603956,
                     'q20': []}
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
