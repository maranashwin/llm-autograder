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
                     'q5': Star(spectral_type='M9.75III', stellar_effective_temperature=5580.407118135032, stellar_radius=22.44224104327183, stellar_mass=0.1581728853728781, stellar_luminosity=-0.7142375233000529, stellar_surface_gravity=5.086512360231565, stellar_age=0.8734360268126311),
                     'q6': Star(spectral_type='D', stellar_effective_temperature=2194.365166529972, stellar_radius=9.582495717380352, stellar_mass=2.7423376843765994, stellar_luminosity=-0.22688671352864873, stellar_surface_gravity=5.039022403692368, stellar_age=10.922828124972431),
                     'q7': -0.1256391725976027,
                     'q8': 7.487717581854391,
                     'q9': 2708.4386800521797,
                     'q10': 'bet 18',
                     'q11': 8.557911910785934,
                     'Planet': Planet(planet_name='Jupiter', host_name='Sun', discovery_method='Imaging', discovery_year=1610, controversial_flag=False, orbital_period=4333.0, planet_radius=11.209, planet_mass=317.828, semi_major_radius=5.2038, eccentricity=0.0489, equilibrium_temperature=110, insolation_flux=0.0345),
                     'q12': Planet(planet_name='TOI 6251 a', host_name='TOI 6251', discovery_method='Orbital Brightness Modulation', discovery_year=2020, controversial_flag=False, orbital_period=544.5551413571959, planet_radius=10.409699209095773, planet_mass=6570.13490362867, semi_major_radius=135.74636382055172, eccentricity=0.07794086578816792, equilibrium_temperature=1391.7730219727355, insolation_flux=412.0074466711641),
                     'q13': [Planet(planet_name='ups 4266 a', host_name='ups 4266', discovery_method='Transit', discovery_year=2018, controversial_flag=True, orbital_period=1063.5450032924668, planet_radius=11.52410693578382, planet_mass=4018.017761829423, semi_major_radius=95.70416238136896, eccentricity=0.058334522836014764, equilibrium_temperature=782.3824652534424, insolation_flux=1005.4286750372592),
                             Planet(planet_name='DP 6559 1', host_name='DP 6559', discovery_method='Transit Timing Variations', discovery_year=2018, controversial_flag=False, orbital_period=918.4198811026524, planet_radius=17.330028603957505, planet_mass=3710.2054666271683, semi_major_radius=17.75518474386257, eccentricity=0.040688619052904954, equilibrium_temperature=493.18196117763034, insolation_flux=1571.0207076878776),
                             Planet(planet_name='mu-2032 a', host_name='mu-2032', discovery_method='Microlensing', discovery_year=2015, controversial_flag=False, orbital_period=612.3444387439773, planet_radius=10.129973903242792, planet_mass=3671.746481784743, semi_major_radius=134.42418489472874, eccentricity=0.09103263756655414, equilibrium_temperature=1684.995744582573, insolation_flux=781.0789527147017),
                             Planet(planet_name='gam-2853 a', host_name='gam-2853', discovery_method='Transit Timing Variations', discovery_year=2017, controversial_flag=True, orbital_period=430.42205419556933, planet_radius=15.768447962448274, planet_mass=2123.202342352869, semi_major_radius=54.50608760673092, eccentricity=0.051017749918617905, equilibrium_temperature=785.898410561808, insolation_flux=294.8031277716128),
                             Planet(planet_name='nu-7601 a', host_name='nu-7601', discovery_method='Transit', discovery_year=2016, controversial_flag=False, orbital_period=631.2866212035308, planet_radius=12.924904624105249, planet_mass=7116.211634904444, semi_major_radius=112.31449629020489, eccentricity=0.06463079439331583, equilibrium_temperature=166.85023339644272, insolation_flux=808.6600244271625)],
                     'q14': [Planet(planet_name='ome-4097 2', host_name='ome-4097', discovery_method='Radial Velocity', discovery_year=2017, controversial_flag=True, orbital_period=193.29247014123297, planet_radius=18.60586706763383, planet_mass=2046.4872929712164, semi_major_radius=134.10774961723993, eccentricity=0.004890361744140072, equilibrium_temperature=1035.0780330139373, insolation_flux=239.60035786152832),
                             Planet(planet_name='xi-2648 b', host_name='xi-2648', discovery_method='Microlensing', discovery_year=2020, controversial_flag=True, orbital_period=968.1956566945041, planet_radius=16.99142106456443, planet_mass=8831.286504446212, semi_major_radius=69.25482497656212, eccentricity=0.07366953145270674, equilibrium_temperature=236.4170356294469, insolation_flux=1551.3238188956016),
                             Planet(planet_name='Kepler-220 2', host_name='Kepler-220', discovery_method='Orbital Brightness Modulation', discovery_year=2017, controversial_flag=True, orbital_period=857.9054365988536, planet_radius=11.599593064249177, planet_mass=31.79608271388588, semi_major_radius=139.10300323929988, eccentricity=0.030492859766024595, equilibrium_temperature=1354.8798377737166, insolation_flux=1528.7261119238187),
                             Planet(planet_name='psi1 4228 b', host_name='psi1 4228', discovery_method='Pulsation Timing Variations', discovery_year=2019, controversial_flag=True, orbital_period=203.97287438252522, planet_radius=18.284923498084545, planet_mass=4803.343997139182, semi_major_radius=64.65008258694431, eccentricity=0.03467943126346271, equilibrium_temperature=446.72424804109164, insolation_flux=70.14861687061125),
                             Planet(planet_name='Kepler-4362 2', host_name='Kepler-4362', discovery_method='Pulsation Timing Variations', discovery_year=2019, controversial_flag=True, orbital_period=343.54450279913067, planet_radius=17.313700410371673, planet_mass=2575.6122996930803, semi_major_radius=147.37132349408148, eccentricity=0.0867689132685286, equilibrium_temperature=1596.449805761853, insolation_flux=20.087437846023022),
                             Planet(planet_name='EPIC-9964 a', host_name='EPIC-9964', discovery_method='Pulsation Timing Variations', discovery_year=2016, controversial_flag=True, orbital_period=480.3232898548651, planet_radius=16.008400879612246, planet_mass=2238.8872491687994, semi_major_radius=84.95323949076656, eccentricity=0.022905061850852837, equilibrium_temperature=520.3197441684393, insolation_flux=1158.0377504630992),
                             Planet(planet_name='EPIC-9964 b', host_name='EPIC-9964', discovery_method='Orbital Brightness Modulation', discovery_year=2018, controversial_flag=True, orbital_period=390.6860020651984, planet_radius=4.778871247746572, planet_mass=2333.9311514088663, semi_major_radius=73.13601560912417, eccentricity=0.06787101565828825, equilibrium_temperature=1476.2933792343958, insolation_flux=1154.1199859542035),
                             Planet(planet_name='alf 5884 a', host_name='alf 5884', discovery_method='Eclipse Timing Variations', discovery_year=2019, controversial_flag=True, orbital_period=538.9881984447558, planet_radius=7.147897967099864, planet_mass=1499.9086234678475, semi_major_radius=124.41756473391902, eccentricity=0.08703768381592247, equilibrium_temperature=1452.2146428191854, insolation_flux=512.3592484009033),
                             Planet(planet_name='2MASS-5506 1', host_name='2MASS-5506', discovery_method='Microlensing', discovery_year=2015, controversial_flag=True, orbital_period=209.62122317091934, planet_radius=9.469070702636007, planet_mass=8504.967963892484, semi_major_radius=104.3585397620711, eccentricity=0.034254991945166874, equilibrium_temperature=711.5558711782669, insolation_flux=718.2528102623033),
                             Planet(planet_name='Kepler-7201 1', host_name='Kepler-7201', discovery_method='Transit', discovery_year=2018, controversial_flag=True, orbital_period=858.4854728174151, planet_radius=9.653255520299174, planet_mass=6573.184113365795, semi_major_radius=37.64929770968144, eccentricity=0.081072415107877, equilibrium_temperature=1784.779883054859, insolation_flux=576.1829481570478),
                             Planet(planet_name='Kepler 949 1', host_name='Kepler 949', discovery_method='Transit', discovery_year=2017, controversial_flag=True, orbital_period=294.71963195700187, planet_radius=19.102870132259085, planet_mass=5406.067660942281, semi_major_radius=36.782056729306696, eccentricity=0.06676089263393004, equilibrium_temperature=1068.1134847238077, insolation_flux=649.1277504312973),
                             Planet(planet_name='Kepler 949 2', host_name='Kepler 949', discovery_method='Orbital Brightness Modulation', discovery_year=2016, controversial_flag=True, orbital_period=122.38953969978729, planet_radius=21.470962953320722, planet_mass=6441.507038847922, semi_major_radius=202.7647798440463, eccentricity=0.0686133286220327, equilibrium_temperature=812.6192419640777, insolation_flux=2181.662681838852),
                             Planet(planet_name='CoRoT-18 a', host_name='CoRoT-18', discovery_method='Pulsar Timing', discovery_year=2017, controversial_flag=True, orbital_period=485.1414205888055, planet_radius=20.280286682895305, planet_mass=8874.070577248132, semi_major_radius=127.6927336264356, eccentricity=0.009641946978919388, equilibrium_temperature=590.6497916399605, insolation_flux=1450.5470929085318),
                             Planet(planet_name='kap 9645 1', host_name='kap 9645', discovery_method='Radial Velocity', discovery_year=2020, controversial_flag=True, orbital_period=678.4583828298588, planet_radius=15.266841949177916, planet_mass=4824.4892932230005, semi_major_radius=55.60146097230143, eccentricity=0.05561004143786451, equilibrium_temperature=1042.616995895111, insolation_flux=2294.7120042927836),
                             Planet(planet_name='iot-9075 2', host_name='iot-9075', discovery_method='Disk Kinematics', discovery_year=2019, controversial_flag=True, orbital_period=601.7056696806128, planet_radius=7.7135661451081505, planet_mass=3290.1512854674856, semi_major_radius=37.730092627775214, eccentricity=0.015175546550436021, equilibrium_temperature=940.722689107997, insolation_flux=1506.3495675179856),
                             Planet(planet_name='alf-9534 1', host_name='alf-9534', discovery_method='Orbital Brightness Modulation', discovery_year=2018, controversial_flag=True, orbital_period=173.36720940714957, planet_radius=18.258826617502415, planet_mass=3030.8398438734553, semi_major_radius=26.034498732225046, eccentricity=0.04881517488000807, equilibrium_temperature=295.1835953625265, insolation_flux=1289.520775389326),
                             Planet(planet_name='Kepler 4705 2', host_name='Kepler 4705', discovery_method='Disk Kinematics', discovery_year=2014, controversial_flag=True, orbital_period=481.0823212143236, planet_radius=8.355957733861606, planet_mass=7154.705484946133, semi_major_radius=131.5188759220129, eccentricity=0.04127010521088291, equilibrium_temperature=669.6985477471303, insolation_flux=1304.7117973369097),
                             Planet(planet_name='mu2-5822 1', host_name='mu2-5822', discovery_method='Radial Velocity', discovery_year=2022, controversial_flag=True, orbital_period=265.9451010722504, planet_radius=9.559813158073805, planet_mass=8003.769708216078, semi_major_radius=208.1773946416102, eccentricity=0.07021895456468483, equilibrium_temperature=919.2165836358773, insolation_flux=1209.5742880351363),
                             Planet(planet_name='mu2-5822 2', host_name='mu2-5822', discovery_method='Orbital Brightness Modulation', discovery_year=2017, controversial_flag=True, orbital_period=1142.5957515669993, planet_radius=21.000541917261344, planet_mass=6178.959873190663, semi_major_radius=75.50933686635763, eccentricity=0.08695018212495262, equilibrium_temperature=1557.6972429769266, insolation_flux=1572.4649550287254),
                             Planet(planet_name='gam1 7704 2', host_name='gam1 7704', discovery_method='Eclipse Timing Variations', discovery_year=2021, controversial_flag=True, orbital_period=283.49171451277175, planet_radius=11.011270768289751, planet_mass=3255.7160507903955, semi_major_radius=49.250108987367796, eccentricity=0.053407059083589045, equilibrium_temperature=495.61003787160007, insolation_flux=579.1543396338667),
                             Planet(planet_name='gam-8759 b', host_name='gam-8759', discovery_method='Astrometry', discovery_year=2015, controversial_flag=True, orbital_period=542.948473528271, planet_radius=7.156262456592138, planet_mass=1039.2491612886697, semi_major_radius=230.60583727417787, eccentricity=0.084967916657688, equilibrium_temperature=297.41078608406656, insolation_flux=2063.662067466078),
                             Planet(planet_name='eps-3919 2', host_name='eps-3919', discovery_method='Radial Velocity', discovery_year=2020, controversial_flag=True, orbital_period=1016.9088471926575, planet_radius=19.845150766752646, planet_mass=613.4940317922237, semi_major_radius=157.49564139638332, eccentricity=0.057049247822000576, equilibrium_temperature=709.3120039388766, insolation_flux=1615.5494107850805),
                             Planet(planet_name='tau-9723 a', host_name='tau-9723', discovery_method='Transit', discovery_year=2022, controversial_flag=True, orbital_period=123.06759724085776, planet_radius=8.209838062247716, planet_mass=4506.501501684517, semi_major_radius=210.93909979172753, eccentricity=0.08287806856866341, equilibrium_temperature=277.4414885595436, insolation_flux=1621.5484830135624)],
                     'q15': [Planet(planet_name='WASP 7242 d', host_name='WASP 7242', discovery_method='Astrometry', discovery_year=2017, controversial_flag=True, orbital_period=594.616357793655, planet_radius=19.251438136444037, planet_mass=4836.669616634205, semi_major_radius=117.66966456090684, eccentricity=0.02871882534501114, equilibrium_temperature=1376.6236475888797, insolation_flux=1549.1579381320091),
                             Planet(planet_name='bet 94180 a', host_name='bet 94180', discovery_method='Orbital Brightness Modulation', discovery_year=2018, controversial_flag=False, orbital_period=984.152928395144, planet_radius=13.517979648948058, planet_mass=3970.320837266614, semi_major_radius=77.97627847324318, eccentricity=0.05451406247151175, equilibrium_temperature=1838.8095213360436, insolation_flux=1571.9713572617284),
                             Planet(planet_name='bet 94180 b', host_name='bet 94180', discovery_method='Transit', discovery_year=2019, controversial_flag=False, orbital_period=705.9897765442665, planet_radius=16.910187065860647, planet_mass=4556.600151491278, semi_major_radius=149.1770360209677, eccentricity=0.0842766642199129, equilibrium_temperature=1202.444692746117, insolation_flux=795.9091467543701),
                             Planet(planet_name='bet 94180 c', host_name='bet 94180', discovery_method='Orbital Brightness Modulation', discovery_year=2016, controversial_flag=False, orbital_period=674.6634554881559, planet_radius=14.795222659380899, planet_mass=5392.406694628043, semi_major_radius=156.16719799411186, eccentricity=0.0663133606540486, equilibrium_temperature=1968.6605300013039, insolation_flux=1410.209257453551),
                             Planet(planet_name='bet 94180 d', host_name='bet 94180', discovery_method='Disk Kinematics', discovery_year=2022, controversial_flag=False, orbital_period=723.0496405588542, planet_radius=17.5857032278363, planet_mass=3566.9539321747734, semi_major_radius=147.91189006122724, eccentricity=0.06184090492529032, equilibrium_temperature=1229.5051278475034, insolation_flux=440.88706407965446)],
                     'q16': [],
                     'q17': 0,
                     'q18': Star(spectral_type='K', stellar_effective_temperature=5292.176978047133, stellar_radius=26.40046300414633, stellar_mass=0.98188893611458, stellar_luminosity=-1.3609103898823283, stellar_surface_gravity=3.8560411801647456, stellar_age=9.223515380521128)}
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
