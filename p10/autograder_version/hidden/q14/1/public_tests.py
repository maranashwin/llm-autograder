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
                     'q5': Star(spectral_type='M2.25IV-III', stellar_effective_temperature=9510.331903821767, stellar_radius=5.017532834657899, stellar_mass=2.7797782574496717, stellar_luminosity=-1.2551591757547649, stellar_surface_gravity=1.8790661887200746, stellar_age=8.88658389574099),
                     'q6': Star(spectral_type='B9.5II-B4.25I', stellar_effective_temperature=2347.1398569809767, stellar_radius=31.017623859107957, stellar_mass=2.255887790282564, stellar_luminosity=1.247281123405663, stellar_surface_gravity=4.313328795799345, stellar_age=9.25177310771723),
                     'q7': 0.18129502585836688,
                     'q8': 5.621124356516617,
                     'q9': 5595.348997415605,
                     'q10': 'TOI-2661',
                     'q11': 5.037433703805385,
                     'Planet': Planet(planet_name='Jupiter', host_name='Sun', discovery_method='Imaging', discovery_year=1610, controversial_flag=False, orbital_period=4333.0, planet_radius=11.209, planet_mass=317.828, semi_major_radius=5.2038, eccentricity=0.0489, equilibrium_temperature=110, insolation_flux=0.0345),
                     'q12': Planet(planet_name='BD 8169 1', host_name='BD 8169', discovery_method='Transit', discovery_year=2020, controversial_flag=False, orbital_period=538.3999372323509, planet_radius=3.237253667017204, planet_mass=7605.54304363391, semi_major_radius=104.79045660926344, eccentricity=0.08127432408337948, equilibrium_temperature=1940.7915058753542, insolation_flux=255.83201415692542),
                     'q13': [Planet(planet_name='ome-6363 a', host_name='ome-6363', discovery_method='Imaging', discovery_year=2018, controversial_flag=False, orbital_period=310.2879284132909, planet_radius=8.768092597568929, planet_mass=6299.816189878531, semi_major_radius=144.05181836255338, eccentricity=0.04436290643426143, equilibrium_temperature=1351.8473778246632, insolation_flux=2090.7315325898253),
                             Planet(planet_name='alf-2012 a', host_name='alf-2012', discovery_method='Pulsation Timing Variations', discovery_year=2019, controversial_flag=False, orbital_period=559.4493726609447, planet_radius=5.648567703443033, planet_mass=9817.666663881777, semi_major_radius=137.7921120026726, eccentricity=0.029903201955391017, equilibrium_temperature=700.1349164128014, insolation_flux=1181.6434219441599),
                             Planet(planet_name='HD-76287 1', host_name='HD-76287', discovery_method='Disk Kinematics', discovery_year=2019, controversial_flag=False, orbital_period=462.30824679404856, planet_radius=11.871570987217689, planet_mass=3199.475825641574, semi_major_radius=52.457077360394635, eccentricity=0.07459262102982844, equilibrium_temperature=2366.851515853999, insolation_flux=478.65426213930596),
                             Planet(planet_name='ups-7624 a', host_name='ups-7624', discovery_method='Pulsation Timing Variations', discovery_year=2022, controversial_flag=False, orbital_period=1024.1863933543214, planet_radius=2.485288982356865, planet_mass=4136.232306357248, semi_major_radius=147.45693868996761, eccentricity=0.10453958673644939, equilibrium_temperature=1022.2223701109748, insolation_flux=613.1098078249859),
                             Planet(planet_name='Kepler-220 1', host_name='Kepler-220', discovery_method='Pulsar Timing', discovery_year=2016, controversial_flag=False, orbital_period=671.0310610469581, planet_radius=30.519112114452827, planet_mass=8221.300160904895, semi_major_radius=108.84048997981594, eccentricity=0.02920633092182688, equilibrium_temperature=861.1363694618811, insolation_flux=471.5383742186475)],
                     'q14': [Planet(planet_name='gam-4633 1', host_name='gam-4633', discovery_method='Orbital Brightness Modulation', discovery_year=2016, controversial_flag=True, orbital_period=626.7810920744714, planet_radius=9.31098136128421, planet_mass=9519.86915149814, semi_major_radius=125.14732315750277, eccentricity=0.03879498519183247, equilibrium_temperature=1718.3565265438347, insolation_flux=1438.4274036037134),
                             Planet(planet_name='eps 406 2', host_name='eps 406', discovery_method='Imaging', discovery_year=2019, controversial_flag=True, orbital_period=811.6347722382064, planet_radius=15.956367595971471, planet_mass=3143.8236703601187, semi_major_radius=179.96583564489111, eccentricity=0.05646225882896792, equilibrium_temperature=1964.0003989270278, insolation_flux=1511.1805061886623),
                             Planet(planet_name='mu2 19152 1', host_name='mu2 19152', discovery_method='Microlensing', discovery_year=2017, controversial_flag=True, orbital_period=377.41661088407363, planet_radius=14.52800095481832, planet_mass=991.1997320333176, semi_major_radius=82.68974791835811, eccentricity=0.014979298049229886, equilibrium_temperature=626.932512088233, insolation_flux=739.0396644385736),
                             Planet(planet_name='mu-47 2', host_name='mu-47', discovery_method='Eclipse Timing Variations', discovery_year=2018, controversial_flag=True, orbital_period=886.6124312613711, planet_radius=6.063200749242638, planet_mass=8449.172151121402, semi_major_radius=65.34698434493862, eccentricity=0.06028733494626286, equilibrium_temperature=829.4499104812546, insolation_flux=817.6627453652734),
                             Planet(planet_name='gam1-26999 1', host_name='gam1-26999', discovery_method='Imaging', discovery_year=2015, controversial_flag=True, orbital_period=573.2779237267875, planet_radius=7.2843240658020765, planet_mass=1498.2688288051636, semi_major_radius=46.55667331042699, eccentricity=0.0023031645643652177, equilibrium_temperature=1993.6198580512391, insolation_flux=542.3839428124503),
                             Planet(planet_name='Kepler-83 b', host_name='Kepler-83', discovery_method='Astrometry', discovery_year=2021, controversial_flag=True, orbital_period=461.55853877206147, planet_radius=6.545495860268999, planet_mass=7912.6557798850445, semi_major_radius=211.2125857627578, eccentricity=0.04904994024556369, equilibrium_temperature=1896.3291760166412, insolation_flux=667.7296832147142),
                             Planet(planet_name='xi 4996 1', host_name='xi 4996', discovery_method='Microlensing', discovery_year=2017, controversial_flag=True, orbital_period=680.1668279628997, planet_radius=12.8964132473876, planet_mass=11042.32705362474, semi_major_radius=26.899537070162125, eccentricity=0.028507804031886137, equilibrium_temperature=1146.8474828378821, insolation_flux=517.6906058057535),
                             Planet(planet_name='xi-3596 2', host_name='xi-3596', discovery_method='Orbital Brightness Modulation', discovery_year=2013, controversial_flag=True, orbital_period=240.2721140713246, planet_radius=9.073730514230252, planet_mass=2992.304728618623, semi_major_radius=116.83906380921718, eccentricity=0.05504538368958736, equilibrium_temperature=388.28569717885216, insolation_flux=1056.5285840751053),
                             Planet(planet_name='EPIC-12 a', host_name='EPIC-12', discovery_method='Microlensing', discovery_year=2014, controversial_flag=True, orbital_period=752.8285071083133, planet_radius=5.614132744925816, planet_mass=248.80214667980817, semi_major_radius=8.260033737521496, eccentricity=0.06574075702322273, equilibrium_temperature=1954.8875706373726, insolation_flux=919.7644559437684),
                             Planet(planet_name='DP-2484 b', host_name='DP-2484', discovery_method='Eclipse Timing Variations', discovery_year=2020, controversial_flag=True, orbital_period=853.7004647358306, planet_radius=4.331116308263138, planet_mass=4723.910485255379, semi_major_radius=83.77156542432084, eccentricity=0.04305951482728655, equilibrium_temperature=1704.482675378833, insolation_flux=1395.392700450478),
                             Planet(planet_name='TOI 1258 a', host_name='TOI 1258', discovery_method='Orbital Brightness Modulation', discovery_year=2019, controversial_flag=True, orbital_period=379.9136249842777, planet_radius=7.473287886018749, planet_mass=5926.071014817017, semi_major_radius=172.53495534515048, eccentricity=0.03140047205749921, equilibrium_temperature=179.35024959238672, insolation_flux=1876.7177540989896),
                             Planet(planet_name='omi 4823 b', host_name='omi 4823', discovery_method='Transit Timing Variations', discovery_year=2019, controversial_flag=True, orbital_period=440.66947824004626, planet_radius=13.49445846653541, planet_mass=6030.978156296277, semi_major_radius=136.07979233615254, eccentricity=0.04204674492444432, equilibrium_temperature=86.73576092750443, insolation_flux=1488.0390378598795),
                             Planet(planet_name='TOI 45958 a', host_name='TOI 45958', discovery_method='Disk Kinematics', discovery_year=2015, controversial_flag=True, orbital_period=313.48731750374566, planet_radius=8.36580779038779, planet_mass=6559.4398743634165, semi_major_radius=122.58320976027272, eccentricity=0.046388150865832437, equilibrium_temperature=747.6080103728018, insolation_flux=1259.9303426034971),
                             Planet(planet_name='BD 1186 2', host_name='BD 1186', discovery_method='Imaging', discovery_year=2015, controversial_flag=True, orbital_period=253.0705973585845, planet_radius=20.931414330777738, planet_mass=10122.333472721946, semi_major_radius=162.41881261815882, eccentricity=0.05250720561749582, equilibrium_temperature=1448.2942494518097, insolation_flux=1168.5997652571223),
                             Planet(planet_name='ome-6616 a', host_name='ome-6616', discovery_method='Orbital Brightness Modulation', discovery_year=2017, controversial_flag=True, orbital_period=53.444272940216024, planet_radius=11.769021023826518, planet_mass=4109.658278036035, semi_major_radius=83.73625356431246, eccentricity=0.036311519258748134, equilibrium_temperature=1651.4674279699218, insolation_flux=1218.2989405550725),
                             Planet(planet_name='EPIC 62 2', host_name='EPIC 62', discovery_method='Pulsation Timing Variations', discovery_year=2021, controversial_flag=True, orbital_period=197.44721151428251, planet_radius=5.453157640475325, planet_mass=4790.38495865878, semi_major_radius=150.35196563669507, eccentricity=0.049227254149243144, equilibrium_temperature=1317.2182587833659, insolation_flux=864.8443008358549),
                             Planet(planet_name='mu 8668 1', host_name='mu 8668', discovery_method='Pulsar Timing', discovery_year=2017, controversial_flag=True, orbital_period=254.1139231746351, planet_radius=22.491864766811872, planet_mass=6351.800243268871, semi_major_radius=57.170542113072166, eccentricity=0.008107955089539695, equilibrium_temperature=1495.0593748375181, insolation_flux=2011.9869364687504),
                             Planet(planet_name='Kepler 26710 b', host_name='Kepler 26710', discovery_method='Transit Timing Variations', discovery_year=2021, controversial_flag=True, orbital_period=215.26783920088673, planet_radius=6.875047913339203, planet_mass=4440.615557933731, semi_major_radius=70.17970773549163, eccentricity=0.059240899907695266, equilibrium_temperature=308.3036443022719, insolation_flux=1912.5823616316509),
                             Planet(planet_name='omi-604 1', host_name='omi-604', discovery_method='Transit Timing Variations', discovery_year=2020, controversial_flag=True, orbital_period=610.8024908813562, planet_radius=13.951824418887108, planet_mass=4878.153790848933, semi_major_radius=238.38717286685744, eccentricity=0.057867747677664304, equilibrium_temperature=643.8508450551774, insolation_flux=1469.7093380065926),
                             Planet(planet_name='nu 17250 b', host_name='nu 17250', discovery_method='Disk Kinematics', discovery_year=2019, controversial_flag=True, orbital_period=607.8618610428524, planet_radius=11.431737119917411, planet_mass=3092.9357404254806, semi_major_radius=174.29342268198457, eccentricity=0.12944034754370592, equilibrium_temperature=1862.4830001002103, insolation_flux=870.5705272563575),
                             Planet(planet_name='ups-5659 a', host_name='ups-5659', discovery_method='Eclipse Timing Variations', discovery_year=2016, controversial_flag=True, orbital_period=766.0645508895145, planet_radius=16.3870373142022, planet_mass=5883.467033629023, semi_major_radius=46.04246435605895, eccentricity=0.03899628833856407, equilibrium_temperature=427.4898314407683, insolation_flux=1104.7257128869776),
                             Planet(planet_name='WASP 1423 b', host_name='WASP 1423', discovery_method='Microlensing', discovery_year=2016, controversial_flag=True, orbital_period=285.6288610176606, planet_radius=14.834694021176551, planet_mass=6203.793953161823, semi_major_radius=126.74603291699408, eccentricity=0.08141553462491877, equilibrium_temperature=67.54137918927086, insolation_flux=1202.749057062412),
                             Planet(planet_name='GJ 2546 1', host_name='GJ 2546', discovery_method='Orbital Brightness Modulation', discovery_year=2020, controversial_flag=True, orbital_period=292.3136133707635, planet_radius=12.320687499442394, planet_mass=5280.765462597406, semi_major_radius=231.94175185502996, eccentricity=0.06390044972392021, equilibrium_temperature=742.4421198216844, insolation_flux=1340.7979934025882),
                             Planet(planet_name='gam 8689 b', host_name='gam 8689', discovery_method='Radial Velocity', discovery_year=2017, controversial_flag=True, orbital_period=334.2877147712591, planet_radius=15.414460448985068, planet_mass=4313.963870929705, semi_major_radius=3.7552477785555, eccentricity=0.03901033371466733, equilibrium_temperature=1896.6255511703173, insolation_flux=149.8904312946455),
                             Planet(planet_name='tau 4363 1', host_name='tau 4363', discovery_method='Orbital Brightness Modulation', discovery_year=2016, controversial_flag=True, orbital_period=556.8457169340062, planet_radius=9.194683013033771, planet_mass=6617.204420789609, semi_major_radius=112.92792585283534, eccentricity=0.02899621374648763, equilibrium_temperature=804.2652054224865, insolation_flux=958.5240506900302),
                             Planet(planet_name='bet-9881 b', host_name='bet-9881', discovery_method='Transit', discovery_year=2017, controversial_flag=True, orbital_period=363.34361841231555, planet_radius=6.840732150923594, planet_mass=4350.939876791245, semi_major_radius=46.79066538301896, eccentricity=0.04403876072708719, equilibrium_temperature=2039.3836278513954, insolation_flux=861.7801022577796),
                             Planet(planet_name='WASP 1352 1', host_name='WASP 1352', discovery_method='Imaging', discovery_year=2021, controversial_flag=True, orbital_period=449.48510478643686, planet_radius=8.081110450505175, planet_mass=7191.96357155391, semi_major_radius=158.13054355837954, eccentricity=0.0475539608752586, equilibrium_temperature=1522.0728884011708, insolation_flux=960.7671979679866),
                             Planet(planet_name='xi 5659 2', host_name='xi 5659', discovery_method='Transit', discovery_year=2019, controversial_flag=True, orbital_period=461.7021425817177, planet_radius=12.90970923627037, planet_mass=3025.9424180061665, semi_major_radius=123.07329971679798, eccentricity=0.06864386381016405, equilibrium_temperature=1615.6879113137693, insolation_flux=1270.6437259600016),
                             Planet(planet_name='gam 6024 1', host_name='gam 6024', discovery_method='Orbital Brightness Modulation', discovery_year=2021, controversial_flag=True, orbital_period=873.6221088859354, planet_radius=12.335611289170139, planet_mass=5050.635432781639, semi_major_radius=25.591042377218756, eccentricity=0.08854733803285304, equilibrium_temperature=2016.572992008441, insolation_flux=1499.688782145037),
                             Planet(planet_name='ome-2673 2', host_name='ome-2673', discovery_method='Transit Timing Variations', discovery_year=2020, controversial_flag=True, orbital_period=548.0188172007759, planet_radius=11.400136081609064, planet_mass=2001.7146662840187, semi_major_radius=136.50129775382862, eccentricity=0.0359775655253511, equilibrium_temperature=340.9362672191436, insolation_flux=1852.9505117111712),
                             Planet(planet_name='rho 2391 1', host_name='rho 2391', discovery_method='Pulsar Timing', discovery_year=2018, controversial_flag=True, orbital_period=755.2722323224828, planet_radius=13.574011038975826, planet_mass=3590.089288915695, semi_major_radius=28.20448315979597, eccentricity=0.07872049276257584, equilibrium_temperature=756.4456395946434, insolation_flux=571.406706033243),
                             Planet(planet_name='WASP-687 2', host_name='WASP-687', discovery_method='Disk Kinematics', discovery_year=2018, controversial_flag=True, orbital_period=1184.0796912023354, planet_radius=11.822274303456355, planet_mass=5657.557103781451, semi_major_radius=160.98320113308708, eccentricity=0.04142858704144505, equilibrium_temperature=380.3278599614663, insolation_flux=1686.342720444729),
                             Planet(planet_name='mu 3587 1', host_name='mu 3587', discovery_method='Transit Timing Variations', discovery_year=2020, controversial_flag=True, orbital_period=940.6838929166918, planet_radius=9.034087300951688, planet_mass=4468.6371155656525, semi_major_radius=65.30893661561745, eccentricity=0.04923704025599111, equilibrium_temperature=1796.9899576793962, insolation_flux=2233.9989044107942),
                             Planet(planet_name='eps 1083 2', host_name='eps 1083', discovery_method='Pulsar Timing', discovery_year=2019, controversial_flag=True, orbital_period=651.784566937674, planet_radius=3.6437234790465833, planet_mass=4143.917216804596, semi_major_radius=106.27816709792653, eccentricity=0.05171188466469892, equilibrium_temperature=907.9590344500873, insolation_flux=1005.6182660071938)]}
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
