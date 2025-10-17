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
                     'q5': Star(spectral_type='D2.25V', stellar_effective_temperature=7027.143797366614, stellar_radius=19.822232773893482, stellar_mass=2.8947399066281876, stellar_luminosity=0.26008693404384464, stellar_surface_gravity=1.3749160281757256, stellar_age=7.142786619124782),
                     'q6': Star(spectral_type='F9.5', stellar_effective_temperature=8288.5747696411, stellar_radius=16.00066392318952, stellar_mass=1.295104708978181, stellar_luminosity=-0.8342383202591048, stellar_surface_gravity=3.8321957545082626, stellar_age=2.3713131649524755),
                     'q7': -0.513859760139098,
                     'q8': 6.977090035511985,
                     'q9': 4889.315832208161,
                     'q10': 'TOI 8651',
                     'q11': 7.356106185267596,
                     'Planet': Planet(planet_name='Jupiter', host_name='Sun', discovery_method='Imaging', discovery_year=1610, controversial_flag=False, orbital_period=4333.0, planet_radius=11.209, planet_mass=317.828, semi_major_radius=5.2038, eccentricity=0.0489, equilibrium_temperature=110, insolation_flux=0.0345),
                     'q12': Planet(planet_name='gam1-7117 1', host_name='gam1-7117', discovery_method='Astrometry', discovery_year=2021, controversial_flag=False, orbital_period=141.18435718623488, planet_radius=11.265877836393452, planet_mass=1411.4190612587486, semi_major_radius=179.99355014536715, eccentricity=0.05554451592198626, equilibrium_temperature=1051.68399841487, insolation_flux=1661.0134580687222),
                     'q13': [Planet(planet_name='TOI-8133 1', host_name='kap 33', discovery_method='Pulsar Timing', discovery_year=2018, controversial_flag=False, orbital_period=240.8372652061027, planet_radius=1.215842050452089, planet_mass=5798.536232534464, semi_major_radius=125.3034461721146, eccentricity=0.0033839880095773156, equilibrium_temperature=1989.9674464927677, insolation_flux=1328.2329393459574),
                             Planet(planet_name='mu2 5689 1', host_name='EPIC-814', discovery_method='Pulsation Timing Variations', discovery_year=2022, controversial_flag=False, orbital_period=461.9659168353273, planet_radius=11.466899895657578, planet_mass=2575.669291347394, semi_major_radius=142.47679743816076, eccentricity=0.0751867890196295, equilibrium_temperature=841.357758607865, insolation_flux=1661.0134580687222),
                             Planet(planet_name='HD 7758 a', host_name='GJ 5131', discovery_method='Pulsation Timing Variations', discovery_year=2015, controversial_flag=False, orbital_period=570.4324564692315, planet_radius=9.505009420498826, planet_mass=6197.898426416149, semi_major_radius=101.86710358158679, eccentricity=0.1009657656795458, equilibrium_temperature=1168.9928090183723, insolation_flux=865.4467743774646),
                             Planet(planet_name='mu2-6026 a', host_name='xi-5104', discovery_method='Pulsation Timing Variations', discovery_year=2021, controversial_flag=False, orbital_period=259.6547907381413, planet_radius=10.136936673010382, planet_mass=3124.4156542387946, semi_major_radius=21.725855888741165, eccentricity=0.053620343068769956, equilibrium_temperature=1305.107007706713, insolation_flux=211.09059147459607),
                             Planet(planet_name='gam1 66 a', host_name='gam 8946', discovery_method='Pulsation Timing Variations', discovery_year=2017, controversial_flag=False, orbital_period=392.0734647486645, planet_radius=13.868517214430858, planet_mass=5638.109669901162, semi_major_radius=124.03881570174673, eccentricity=0.03871518579731163, equilibrium_temperature=723.9364351709601, insolation_flux=1684.278820532016)],
                     'q14': [Planet(planet_name='2MASS 8946 2', host_name='iot-7740', discovery_method='Pulsation Timing Variations', discovery_year=2020, controversial_flag=True, orbital_period=530.643092489045, planet_radius=25.211053934536565, planet_mass=3455.997043179993, semi_major_radius=80.87080689764963, eccentricity=0.06534252278704508, equilibrium_temperature=2146.7460765607248, insolation_flux=1864.249083338058),
                             Planet(planet_name='ome 9482 a', host_name='Kepler 8017', discovery_method='Disk Kinematics', discovery_year=2022, controversial_flag=True, orbital_period=12.612817310935668, planet_radius=16.542146675005526, planet_mass=5019.46701493967, semi_major_radius=108.13148741626134, eccentricity=0.06833545116910625, equilibrium_temperature=1994.484644411677, insolation_flux=1607.338707411367),
                             Planet(planet_name='gam-354 b', host_name='BD-1268', discovery_method='Eclipse Timing Variations', discovery_year=2017, controversial_flag=True, orbital_period=570.5801009302954, planet_radius=12.108939030314476, planet_mass=5227.464539676512, semi_major_radius=76.96794558147019, eccentricity=0.026395530832626496, equilibrium_temperature=373.55967449717343, insolation_flux=835.7949562603794),
                             Planet(planet_name='Kepler 8017 2', host_name='mu2 5023', discovery_method='Imaging', discovery_year=2021, controversial_flag=True, orbital_period=467.81397239732036, planet_radius=13.771755107615716, planet_mass=4487.910281777744, semi_major_radius=40.49136381594099, eccentricity=0.049686880069211826, equilibrium_temperature=1075.3866883556973, insolation_flux=1532.72444956529),
                             Planet(planet_name='gam1-638 1', host_name='WASP 4050', discovery_method='Imaging', discovery_year=2021, controversial_flag=True, orbital_period=671.5622169443016, planet_radius=8.490577625100402, planet_mass=2279.588908452219, semi_major_radius=13.431750927928718, eccentricity=0.05859246428845031, equilibrium_temperature=1207.722944210428, insolation_flux=826.3596789075514),
                             Planet(planet_name='xi 5131 2', host_name='omi-4831', discovery_method='Disk Kinematics', discovery_year=2018, controversial_flag=True, orbital_period=487.85811664454576, planet_radius=10.894662341175431, planet_mass=7503.53090102555, semi_major_radius=77.98942725064977, eccentricity=0.04425141105708193, equilibrium_temperature=1491.7321707870015, insolation_flux=325.7789286816703),
                             Planet(planet_name='nu 354 1', host_name='bet 4614', discovery_method='Eclipse Timing Variations', discovery_year=2017, controversial_flag=True, orbital_period=727.0496273450644, planet_radius=19.124156293380665, planet_mass=7326.505838130435, semi_major_radius=234.0790914708782, eccentricity=0.022794532417570335, equilibrium_temperature=1859.4073158068404, insolation_flux=536.9689254925454),
                             Planet(planet_name='TOI 2429 b', host_name='nu 9614', discovery_method='Transit Timing Variations', discovery_year=2020, controversial_flag=True, orbital_period=413.12908261648215, planet_radius=9.05193287132038, planet_mass=4571.470600034426, semi_major_radius=61.962853892203505, eccentricity=0.04582468114128881, equilibrium_temperature=1927.5594536579006, insolation_flux=1653.7029641267713),
                             Planet(planet_name='CoRoT-3010 b', host_name='gam 8651', discovery_method='Orbital Brightness Modulation', discovery_year=2019, controversial_flag=True, orbital_period=435.5522533397906, planet_radius=13.744320846626472, planet_mass=6570.762029848367, semi_major_radius=16.223022716955597, eccentricity=0.08806314573809189, equilibrium_temperature=718.459145756085, insolation_flux=1418.6867616842887),
                             Planet(planet_name='WASP-89562 b', host_name='kap-4905', discovery_method='Pulsar Timing', discovery_year=2018, controversial_flag=True, orbital_period=704.5491084902726, planet_radius=3.7253797741817403, planet_mass=47.08635911038982, semi_major_radius=3.7066688490182145, eccentricity=0.038985580520995454, equilibrium_temperature=1530.509968156939, insolation_flux=1648.0874084166617),
                             Planet(planet_name='alf-9268 1', host_name='kap-1464', discovery_method='Astrometry', discovery_year=2018, controversial_flag=True, orbital_period=412.68274250833156, planet_radius=8.120064591455579, planet_mass=4490.834393826822, semi_major_radius=243.94737120938885, eccentricity=0.062058605388093185, equilibrium_temperature=260.0394458844994, insolation_flux=2135.9842223308574),
                             Planet(planet_name='nu 50914 2', host_name='alf-9268', discovery_method='Astrometry', discovery_year=2017, controversial_flag=True, orbital_period=541.6264112532662, planet_radius=17.932829484858253, planet_mass=13120.966303428004, semi_major_radius=161.72683852787173, eccentricity=0.023565429297381004, equilibrium_temperature=467.9013948157715, insolation_flux=1561.8965457946201),
                             Planet(planet_name='alf-58 2', host_name='mu2 5023', discovery_method='Imaging', discovery_year=2022, controversial_flag=True, orbital_period=620.5736385329803, planet_radius=10.089791332503447, planet_mass=4875.9453689029615, semi_major_radius=105.60711196740198, eccentricity=0.07444949117112538, equilibrium_temperature=855.2874326840099, insolation_flux=697.7432664944738),
                             Planet(planet_name='BD-1268 b', host_name='iot-6942', discovery_method='Microlensing', discovery_year=2016, controversial_flag=True, orbital_period=1268.790991408276, planet_radius=11.784815830614503, planet_mass=2568.3578251390395, semi_major_radius=241.71834572682116, eccentricity=0.06341329194053545, equilibrium_temperature=1442.734520770854, insolation_flux=171.97552381846253),
                             Planet(planet_name='bet 4614 a', host_name='alf 76681', discovery_method='Disk Kinematics', discovery_year=2017, controversial_flag=True, orbital_period=668.7067372200517, planet_radius=18.062981171318743, planet_mass=4077.8854947074815, semi_major_radius=196.16433932309275, eccentricity=0.07446931182880394, equilibrium_temperature=341.5801330613425, insolation_flux=986.750393473194),
                             Planet(planet_name='BD-1268 a', host_name='2MASS 8946', discovery_method='Pulsar Timing', discovery_year=2020, controversial_flag=True, orbital_period=938.9590280866901, planet_radius=19.13550203095504, planet_mass=5038.752254823725, semi_major_radius=147.81779117110153, eccentricity=0.058757809305690384, equilibrium_temperature=1110.877949415137, insolation_flux=998.496319375845),
                             Planet(planet_name='alf 76681 b', host_name='iot-6519', discovery_method='Microlensing', discovery_year=2017, controversial_flag=True, orbital_period=1158.6114793593292, planet_radius=19.374627221587296, planet_mass=8705.04201670809, semi_major_radius=83.68547196607626, eccentricity=0.0022486756098660868, equilibrium_temperature=556.074769889747, insolation_flux=197.07701112512348),
                             Planet(planet_name='DP-3566 b', host_name='alf 76681', discovery_method='Radial Velocity', discovery_year=2014, controversial_flag=True, orbital_period=771.5537086767564, planet_radius=23.080685345021255, planet_mass=6506.558786057685, semi_major_radius=36.67563106262151, eccentricity=0.06790464188615447, equilibrium_temperature=1860.9523154126455, insolation_flux=1106.381522827476),
                             Planet(planet_name='nu 45 b', host_name='ome 9482', discovery_method='Microlensing', discovery_year=2017, controversial_flag=True, orbital_period=193.67479629333258, planet_radius=15.502762478956928, planet_mass=1047.2580145744755, semi_major_radius=35.75921247081712, eccentricity=0.0412148986766144, equilibrium_temperature=761.8552219450105, insolation_flux=1236.596938567657),
                             Planet(planet_name='eps 7801 a', host_name='CoRoT-5745', discovery_method='Transit', discovery_year=2018, controversial_flag=True, orbital_period=538.0650898240293, planet_radius=16.65871322732476, planet_mass=3533.428160177108, semi_major_radius=106.42286390939958, eccentricity=0.05242542713564112, equilibrium_temperature=1695.3902494759247, insolation_flux=1359.0436879091583),
                             Planet(planet_name='WASP 43325 b', host_name='alf-58', discovery_method='Pulsar Timing', discovery_year=2018, controversial_flag=True, orbital_period=794.5469704295901, planet_radius=15.3726592270248, planet_mass=10563.316329846002, semi_major_radius=87.08400832579214, eccentricity=0.08165454844357659, equilibrium_temperature=550.3757096085462, insolation_flux=645.1416768479066),
                             Planet(planet_name='CoRoT-5745 1', host_name='DP-3566', discovery_method='Eclipse Timing Variations', discovery_year=2017, controversial_flag=True, orbital_period=182.07950690635977, planet_radius=15.510128028300073, planet_mass=7950.30852579867, semi_major_radius=13.454304419405346, eccentricity=0.006964043961088788, equilibrium_temperature=1321.1785387929629, insolation_flux=1652.2668320528257),
                             Planet(planet_name='CoRoT 4370 b', host_name='iot-6942', discovery_method='Eclipse Timing Variations', discovery_year=2022, controversial_flag=True, orbital_period=241.98028211455062, planet_radius=8.179337169181611, planet_mass=7247.175048060812, semi_major_radius=76.69946114085158, eccentricity=0.06777747503522885, equilibrium_temperature=292.26886153329167, insolation_flux=1046.3876316508613),
                             Planet(planet_name='gam1-87424 b', host_name='eps 4831', discovery_method='Microlensing', discovery_year=2021, controversial_flag=True, orbital_period=827.5997272179447, planet_radius=15.25227398127411, planet_mass=5393.925818117387, semi_major_radius=96.57133403412828, eccentricity=0.09902248149082951, equilibrium_temperature=700.2792145580721, insolation_flux=1223.555039181613),
                             Planet(planet_name='mu2 3010 b', host_name='nu 45', discovery_method='Transit Timing Variations', discovery_year=2015, controversial_flag=True, orbital_period=273.3590696060711, planet_radius=26.009172143878683, planet_mass=6930.939526478649, semi_major_radius=73.12280806512439, eccentricity=0.025993045842313017, equilibrium_temperature=167.15761049869513, insolation_flux=1625.1435798381356)],
                     'q15': [Planet(planet_name='gam 7740 3', host_name='iot-3573', discovery_method='Microlensing', discovery_year=2019, controversial_flag=True, orbital_period=564.8428149969102, planet_radius=0.8790584903528025, planet_mass=2902.143294525777, semi_major_radius=74.40788943905048, eccentricity=0.09242256422907394, equilibrium_temperature=1421.817028546399, insolation_flux=832.7507780780762),
                             Planet(planet_name='iot-8133 3', host_name='rho-293', discovery_method='Transit Timing Variations', discovery_year=2020, controversial_flag=False, orbital_period=794.8081593605161, planet_radius=7.7319504698460015, planet_mass=7430.205503889002, semi_major_radius=11.862492468746694, eccentricity=0.060340384843730506, equilibrium_temperature=615.8512605239428, insolation_flux=237.6844992097117),
                             Planet(planet_name='rho 43306 4', host_name='GJ 36', discovery_method='Pulsar Timing', discovery_year=2018, controversial_flag=True, orbital_period=389.962934021428, planet_radius=15.878050506797907, planet_mass=5109.900034011662, semi_major_radius=179.092731158987, eccentricity=0.051726783091242914, equilibrium_temperature=1207.5115487518306, insolation_flux=1790.5836977455647),
                             Planet(planet_name='nu 4831 3', host_name='eps 2353', discovery_method='Pulsar Timing', discovery_year=2018, controversial_flag=True, orbital_period=720.7261417267687, planet_radius=2.46275847026682, planet_mass=3476.4252570334183, semi_major_radius=191.98897364829784, eccentricity=0.05561309990046001, equilibrium_temperature=1164.544709501527, insolation_flux=904.8210722898714),
                             Planet(planet_name='gam1 8651 c', host_name='tau 3270', discovery_method='Eclipse Timing Variations', discovery_year=2022, controversial_flag=False, orbital_period=846.0880011736658, planet_radius=15.088071995449916, planet_mass=4345.732314033947, semi_major_radius=102.6537968735158, eccentricity=0.03791455152818805, equilibrium_temperature=732.6459436443495, insolation_flux=1461.617994614112)]}
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
