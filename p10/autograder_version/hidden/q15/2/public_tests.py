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
                     'q2': ['data&stars_5.csv',
                            'data&stars_4.csv',
                            'data&stars_3.csv',
                            'data&stars_2.csv',
                            'data&stars_1.csv',
                            'data&planets_5.csv',
                            'data&planets_4.csv',
                            'data&planets_3.csv',
                            'data&planets_2.csv',
                            'data&planets_1.csv',
                            'data&mapping_5.json',
                            'data&mapping_4.json',
                            'data&mapping_3.json',
                            'data&mapping_2.json',
                            'data&mapping_1.json'],
                     'q3': ['data&stars_5.csv',
                            'data&stars_4.csv',
                            'data&stars_3.csv',
                            'data&stars_2.csv',
                            'data&stars_1.csv',
                            'data&planets_5.csv',
                            'data&planets_4.csv',
                            'data&planets_3.csv',
                            'data&planets_2.csv',
                            'data&planets_1.csv'],
                     'q4': ['data&stars_5.csv',
                            'data&stars_4.csv',
                            'data&stars_3.csv',
                            'data&stars_2.csv',
                            'data&stars_1.csv'],
                     'Star': Star(spectral_type='G2 V', stellar_effective_temperature=5780.0, stellar_radius=1.0, stellar_mass=1.0, stellar_luminosity=0.0, stellar_surface_gravity=4.44, stellar_age=4.6),
                     'q5': Star(spectral_type='B6.5V', stellar_effective_temperature=5177.933552036308, stellar_radius=33.9769946762661, stellar_mass=2.606875693679697, stellar_luminosity=-0.09961453055124267, stellar_surface_gravity=3.920932367802404, stellar_age=1.6051099782542986),
                     'q6': Star(spectral_type='B6.5V', stellar_effective_temperature=5142.939264937733, stellar_radius=59.607454682897924, stellar_mass=2.9582809859623485, stellar_luminosity=-0.28193751578314147, stellar_surface_gravity=3.3208119745285436, stellar_age=0.5252062456093896),
                     'q7': -0.2911403869742767,
                     'q8': 6.8603218586593995,
                     'q9': 5627.084640271472,
                     'q10': 'Kepler 8997',
                     'q11': 7.398892559199113,
                     'Planet': Planet(planet_name='Jupiter', host_name='Sun', discovery_method='Imaging', discovery_year=1610, controversial_flag=False, orbital_period=4333.0, planet_radius=11.209, planet_mass=317.828, semi_major_radius=5.2038, eccentricity=0.0489, equilibrium_temperature=110, insolation_flux=0.0345),
                     'q12': Planet(planet_name='gam1 7643 1', host_name='gam1 7643', discovery_method='Astrometry', discovery_year=2017, controversial_flag=False, orbital_period=637.5230601555123, planet_radius=21.98290175190458, planet_mass=7788.0267736335645, semi_major_radius=79.1722410273114, eccentricity=0.0038592838436078136, equilibrium_temperature=1306.6091792998402, insolation_flux=1494.6221674244657),
                     'q13': [Planet(planet_name='tau-6411 a', host_name='tau-6411', discovery_method='Imaging', discovery_year=2020, controversial_flag=False, orbital_period=522.5247590631704, planet_radius=12.622429521297084, planet_mass=2053.0969215255423, semi_major_radius=76.1591016269951, eccentricity=0.06707374606425247, equilibrium_temperature=794.0956108979553, insolation_flux=1289.0509570761428),
                             Planet(planet_name='kap-5699 1', host_name='kap-5699', discovery_method='Transit Timing Variations', discovery_year=2019, controversial_flag=False, orbital_period=765.7700418428537, planet_radius=16.011340480805853, planet_mass=3979.6109340217145, semi_major_radius=118.27862386810875, eccentricity=0.02645801127943509, equilibrium_temperature=1128.3865426317097, insolation_flux=434.32498752652805),
                             Planet(planet_name='bet-2135 a', host_name='bet-2135', discovery_method='Transit', discovery_year=2020, controversial_flag=False, orbital_period=897.5618116896653, planet_radius=13.05980849831869, planet_mass=4280.069888474506, semi_major_radius=140.58640187790184, eccentricity=0.0613205814458513, equilibrium_temperature=1191.6851844096002, insolation_flux=1499.7002576554783),
                             Planet(planet_name='tau-8155 a', host_name='tau-8155', discovery_method='Disk Kinematics', discovery_year=2018, controversial_flag=False, orbital_period=343.3870626779136, planet_radius=14.586545465602603, planet_mass=6215.418449956172, semi_major_radius=31.538257923678188, eccentricity=0.09249293527941328, equilibrium_temperature=1348.1333490886245, insolation_flux=2701.4201539587903),
                             Planet(planet_name='kap 3348 1', host_name='kap 3348', discovery_method='Eclipse Timing Variations', discovery_year=2020, controversial_flag=True, orbital_period=1019.0259878282397, planet_radius=14.628818943978615, planet_mass=2948.691865489613, semi_major_radius=87.93903231458634, eccentricity=0.08625033469103173, equilibrium_temperature=820.9585608688747, insolation_flux=635.9822293669238)],
                     'q14': [Planet(planet_name='nu-9353 2', host_name='nu-9353', discovery_method='Radial Velocity', discovery_year=2014, controversial_flag=True, orbital_period=1154.0184505601355, planet_radius=17.585753514953055, planet_mass=7470.727314589036, semi_major_radius=118.85536226297418, eccentricity=0.030842209686730362, equilibrium_temperature=1540.0301447326779, insolation_flux=1814.7153975609135),
                             Planet(planet_name='ups 438 1', host_name='ups 438', discovery_method='Imaging', discovery_year=2019, controversial_flag=True, orbital_period=434.0947617092072, planet_radius=11.038046340848801, planet_mass=8291.980528647826, semi_major_radius=150.74309833473663, eccentricity=0.09343211028188676, equilibrium_temperature=1159.960988292518, insolation_flux=814.6463372152341),
                             Planet(planet_name='kap 6232 b', host_name='kap 6232', discovery_method='Eclipse Timing Variations', discovery_year=2020, controversial_flag=True, orbital_period=395.56120487104806, planet_radius=12.928724957853149, planet_mass=4332.077570811563, semi_major_radius=66.06338026269616, eccentricity=0.05249197374512221, equilibrium_temperature=848.2185727956006, insolation_flux=1055.0456413568568),
                             Planet(planet_name='HD-8785 2', host_name='HD-8785', discovery_method='Transit Timing Variations', discovery_year=2020, controversial_flag=True, orbital_period=187.89594327951596, planet_radius=12.969456747157249, planet_mass=152.89760905856656, semi_major_radius=90.62542536289988, eccentricity=0.008015992592872175, equilibrium_temperature=1316.6887802469887, insolation_flux=222.6201411059585),
                             Planet(planet_name='gam1 9561 2', host_name='gam1 9561', discovery_method='Astrometry', discovery_year=2022, controversial_flag=True, orbital_period=477.44068212041446, planet_radius=13.383003037288935, planet_mass=8813.419359005771, semi_major_radius=150.46745953085278, eccentricity=0.06144391404153464, equilibrium_temperature=1118.2937315405004, insolation_flux=487.0911015842804),
                             Planet(planet_name='HD-5150 1', host_name='HD-5150', discovery_method='Imaging', discovery_year=2019, controversial_flag=True, orbital_period=681.7391382409146, planet_radius=8.810627740500617, planet_mass=6128.339296430837, semi_major_radius=147.832580215898, eccentricity=0.036653038286902334, equilibrium_temperature=627.3023467922892, insolation_flux=1155.4113500572007),
                             Planet(planet_name='HD-5150 2', host_name='HD-5150', discovery_method='Astrometry', discovery_year=2020, controversial_flag=True, orbital_period=1048.47262283084, planet_radius=12.446610343104473, planet_mass=6997.517290225048, semi_major_radius=134.12106246553876, eccentricity=0.07961726547177131, equilibrium_temperature=686.8771026819184, insolation_flux=28.70978673503032),
                             Planet(planet_name='psi1 6134 a', host_name='psi1 6134', discovery_method='Radial Velocity', discovery_year=2018, controversial_flag=True, orbital_period=570.6219806953558, planet_radius=11.370188106486316, planet_mass=12487.260107057627, semi_major_radius=112.77553887342208, eccentricity=0.09463433572179164, equilibrium_temperature=1454.1817219302468, insolation_flux=820.2871138938676),
                             Planet(planet_name='EPIC 5652 a', host_name='EPIC 5652', discovery_method='Pulsation Timing Variations', discovery_year=2017, controversial_flag=True, orbital_period=286.0582084000198, planet_radius=8.96134916497787, planet_mass=8193.354594415096, semi_major_radius=113.58984115815753, eccentricity=0.02402379036355201, equilibrium_temperature=1120.332174726753, insolation_flux=784.6024450782941),
                             Planet(planet_name='tau 9144 2', host_name='tau 9144', discovery_method='Orbital Brightness Modulation', discovery_year=2020, controversial_flag=True, orbital_period=231.92963088983169, planet_radius=18.463054944088984, planet_mass=5907.915105764074, semi_major_radius=26.50160351431488, eccentricity=0.0532339633242477, equilibrium_temperature=1685.5608530649079, insolation_flux=1601.8964082192977),
                             Planet(planet_name='GJ 14568 1', host_name='GJ 14568', discovery_method='Transit', discovery_year=2015, controversial_flag=True, orbital_period=617.986609422465, planet_radius=6.4160878187237165, planet_mass=4948.1879877286165, semi_major_radius=52.29848321162291, eccentricity=0.08457596455486513, equilibrium_temperature=1630.9407254201174, insolation_flux=305.0880203621673),
                             Planet(planet_name='Kepler 43524 1', host_name='Kepler 43524', discovery_method='Transit Timing Variations', discovery_year=2018, controversial_flag=True, orbital_period=555.2112675490473, planet_radius=4.654700936638809, planet_mass=5262.020290206262, semi_major_radius=29.526615513892352, eccentricity=0.06975368580092256, equilibrium_temperature=329.6134731283104, insolation_flux=2207.276369255679),
                             Planet(planet_name='bet 4454 b', host_name='bet 4454', discovery_method='Imaging', discovery_year=2018, controversial_flag=True, orbital_period=692.0211386501494, planet_radius=16.69810328062983, planet_mass=1769.8800993932678, semi_major_radius=80.74474518166585, eccentricity=0.055879314800735484, equilibrium_temperature=1093.2656489251042, insolation_flux=1067.0171853155725),
                             Planet(planet_name='xi 94942 a', host_name='xi 94942', discovery_method='Imaging', discovery_year=2014, controversial_flag=True, orbital_period=540.4615915330655, planet_radius=11.00191057171632, planet_mass=5674.66717679811, semi_major_radius=2.221952202772769, eccentricity=0.03977080375843052, equilibrium_temperature=658.2393202265702, insolation_flux=1380.8127908546314),
                             Planet(planet_name='rho 81 a', host_name='rho 81', discovery_method='Imaging', discovery_year=2014, controversial_flag=True, orbital_period=646.7240669606535, planet_radius=15.002429730445645, planet_mass=5239.99284271469, semi_major_radius=95.66175671962436, eccentricity=0.050560920601898436, equilibrium_temperature=1178.9951503520138, insolation_flux=431.8088596737007),
                             Planet(planet_name='EPIC 8074 1', host_name='EPIC 8074', discovery_method='Transit', discovery_year=2019, controversial_flag=True, orbital_period=265.7272549904334, planet_radius=13.092384855921901, planet_mass=10541.909809687178, semi_major_radius=190.1817063132052, eccentricity=0.07111309323343307, equilibrium_temperature=1808.358750883097, insolation_flux=1529.7430991462022),
                             Planet(planet_name='WASP 6315 a', host_name='WASP 6315', discovery_method='Pulsar Timing', discovery_year=2017, controversial_flag=True, orbital_period=11.587640992198828, planet_radius=13.339253758234946, planet_mass=4206.722258869095, semi_major_radius=188.33586735012472, eccentricity=0.07358282639009037, equilibrium_temperature=310.14367627240847, insolation_flux=538.0472760948561),
                             Planet(planet_name='psi1-8539 a', host_name='psi1-8539', discovery_method='Microlensing', discovery_year=2015, controversial_flag=True, orbital_period=337.9850518999644, planet_radius=24.266143367067727, planet_mass=9017.683673074724, semi_major_radius=50.76619390003104, eccentricity=0.03624328461216583, equilibrium_temperature=2134.8106931750963, insolation_flux=2373.6847069222877),
                             Planet(planet_name='kap 6595 a', host_name='kap 6595', discovery_method='Radial Velocity', discovery_year=2021, controversial_flag=True, orbital_period=5.530272616363561, planet_radius=0.37162696702594644, planet_mass=1842.8496504868367, semi_major_radius=113.40719333693119, eccentricity=0.13032175915410152, equilibrium_temperature=1684.0450357734785, insolation_flux=68.75700670165565),
                             Planet(planet_name='mu2 7535 1', host_name='mu2 7535', discovery_method='Disk Kinematics', discovery_year=2018, controversial_flag=True, orbital_period=1053.3831441798557, planet_radius=20.642133621993064, planet_mass=7317.258232654316, semi_major_radius=139.9606141509512, eccentricity=0.07070983083838368, equilibrium_temperature=1614.230764286302, insolation_flux=1023.3363820380802),
                             Planet(planet_name='mu2-1865 1', host_name='mu2-1865', discovery_method='Microlensing', discovery_year=2019, controversial_flag=True, orbital_period=326.23150785259463, planet_radius=4.629711090790144, planet_mass=6568.026772077561, semi_major_radius=52.465882126780876, eccentricity=0.03602676791294501, equilibrium_temperature=1650.1448753177363, insolation_flux=854.5831884000136),
                             Planet(planet_name='mu2-1865 2', host_name='mu2-1865', discovery_method='Imaging', discovery_year=2016, controversial_flag=True, orbital_period=723.2776771812456, planet_radius=0.4136606723283851, planet_mass=5107.199759939204, semi_major_radius=83.09978293851559, eccentricity=0.09318547663883428, equilibrium_temperature=418.70687113350834, insolation_flux=1113.4553532442214)],
                     'q15': [Planet(planet_name='bet 9154 d', host_name='bet 9154', discovery_method='Imaging', discovery_year=2020, controversial_flag=False, orbital_period=220.7320504258593, planet_radius=16.003316732217108, planet_mass=8709.105421821685, semi_major_radius=52.38462741933718, eccentricity=0.08501892727318094, equilibrium_temperature=827.9730462731166, insolation_flux=1855.096725428571),
                             Planet(planet_name='tau 51471 1', host_name='tau 51471', discovery_method='Transit Timing Variations', discovery_year=2021, controversial_flag=False, orbital_period=346.392071080628, planet_radius=19.314594669143535, planet_mass=6168.791481317639, semi_major_radius=125.48913117920432, eccentricity=0.05909410010996857, equilibrium_temperature=732.0362478768698, insolation_flux=35.069046091494556),
                             Planet(planet_name='tau 51471 2', host_name='tau 51471', discovery_method='Astrometry', discovery_year=2015, controversial_flag=False, orbital_period=518.136711519407, planet_radius=7.219478555824221, planet_mass=8198.640332532226, semi_major_radius=83.58047392056729, eccentricity=0.016591714789134238, equilibrium_temperature=1251.330983902857, insolation_flux=1493.9721651266875),
                             Planet(planet_name='tau 51471 3', host_name='tau 51471', discovery_method='Pulsation Timing Variations', discovery_year=2018, controversial_flag=False, orbital_period=842.2902871745811, planet_radius=5.211616245760073, planet_mass=3062.6482554887416, semi_major_radius=73.63325086905164, eccentricity=0.0038573415529993688, equilibrium_temperature=1409.9783597025255, insolation_flux=382.22560843612337),
                             Planet(planet_name='tau 51471 4', host_name='tau 51471', discovery_method='Microlensing', discovery_year=2017, controversial_flag=False, orbital_period=468.0313409122722, planet_radius=14.166152753908024, planet_mass=5737.064551758894, semi_major_radius=111.7149133612071, eccentricity=0.0287724675389923, equilibrium_temperature=847.3375200072978, insolation_flux=1195.7536943505602)]}
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
