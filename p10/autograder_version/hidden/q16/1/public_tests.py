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
                     'q5': Star(spectral_type='W8.75II', stellar_effective_temperature=4738.405056230713, stellar_radius=36.80510886269413, stellar_mass=2.2856240030182904, stellar_luminosity=1.6968965886599523, stellar_surface_gravity=1.8665895666477996, stellar_age=5.918636258578849),
                     'q6': Star(spectral_type='W6.5', stellar_effective_temperature=8182.931996162951, stellar_radius=24.343571072575614, stellar_mass=1.8013347919043452, stellar_luminosity=-2.715214954138829, stellar_surface_gravity=0.5143326393719669, stellar_age=7.506981013803658),
                     'q7': -0.17419102135525286,
                     'q8': 7.073359859257457,
                     'q9': 6777.222342702533,
                     'q10': 'DP-9885',
                     'q11': 6.884772920642415,
                     'Planet': Planet(planet_name='Jupiter', host_name='Sun', discovery_method='Imaging', discovery_year=1610, controversial_flag=False, orbital_period=4333.0, planet_radius=11.209, planet_mass=317.828, semi_major_radius=5.2038, eccentricity=0.0489, equilibrium_temperature=110, insolation_flux=0.0345),
                     'q12': Planet(planet_name='xi-4952 1', host_name='xi-4952', discovery_method='Orbital Brightness Modulation', discovery_year=2019, controversial_flag=False, orbital_period=709.40106092566, planet_radius=16.09261328967142, planet_mass=3782.5793056890543, semi_major_radius=31.091083150189334, eccentricity=0.012431916901885547, equilibrium_temperature=682.8991255995288, insolation_flux=232.16971580858626),
                     'q13': [Planet(planet_name='gam 6247 1', host_name='gam 6247', discovery_method='Transit Timing Variations', discovery_year=2021, controversial_flag=False, orbital_period=741.2539401886825, planet_radius=16.637553464302005, planet_mass=1994.3943738534076, semi_major_radius=150.4334995131211, eccentricity=0.017272724799663797, equilibrium_temperature=1557.9265221259582, insolation_flux=1466.7545047605108),
                             Planet(planet_name='mu 8257 1', host_name='mu 8257', discovery_method='Eclipse Timing Variations', discovery_year=2018, controversial_flag=False, orbital_period=268.96042761849276, planet_radius=10.560631084926381, planet_mass=4770.5122221910715, semi_major_radius=70.42121432258419, eccentricity=0.06944021592223265, equilibrium_temperature=1293.3977661477795, insolation_flux=2840.983301457663),
                             Planet(planet_name='gam-8339 1', host_name='gam-8339', discovery_method='Disk Kinematics', discovery_year=2017, controversial_flag=False, orbital_period=582.3534541040667, planet_radius=10.283195789346497, planet_mass=1883.7401548011226, semi_major_radius=47.867507698473695, eccentricity=0.050649241243511646, equilibrium_temperature=601.0897476754388, insolation_flux=1640.0222259374634),
                             Planet(planet_name='xi 6129 1', host_name='xi 6129', discovery_method='Transit Timing Variations', discovery_year=2022, controversial_flag=False, orbital_period=145.52973465689126, planet_radius=13.792505155757212, planet_mass=5198.513143504171, semi_major_radius=173.28715620497104, eccentricity=0.08803410258768687, equilibrium_temperature=1014.0599528267796, insolation_flux=1928.4135270781862),
                             Planet(planet_name='CoRoT 4909 1', host_name='CoRoT 4909', discovery_method='Astrometry', discovery_year=2018, controversial_flag=False, orbital_period=963.7360771145195, planet_radius=1.0650291620952483, planet_mass=2907.185418571324, semi_major_radius=24.9177047775284, eccentricity=0.08646817639893686, equilibrium_temperature=2677.4593199897377, insolation_flux=483.13452560956966)],
                     'q14': [Planet(planet_name='iot 1777 b', host_name='iot 1777', discovery_method='Transit', discovery_year=2017, controversial_flag=True, orbital_period=468.3438921704569, planet_radius=9.133048072156873, planet_mass=3019.7472227911194, semi_major_radius=114.84943863301626, eccentricity=0.06693328802130656, equilibrium_temperature=1364.527054481448, insolation_flux=808.7942419907886),
                             Planet(planet_name='gam1-71460 a', host_name='gam1-71460', discovery_method='Transit', discovery_year=2016, controversial_flag=True, orbital_period=737.5704362545132, planet_radius=2.3026992907770776, planet_mass=1477.5781102855485, semi_major_radius=103.84791482567616, eccentricity=0.0023420942850137377, equilibrium_temperature=1713.229118589149, insolation_flux=884.0699362837679),
                             Planet(planet_name='CoRoT-60359 a', host_name='CoRoT-60359', discovery_method='Transit', discovery_year=2015, controversial_flag=True, orbital_period=181.46266131589, planet_radius=7.189611053047626, planet_mass=4851.318347735364, semi_major_radius=109.20049817026623, eccentricity=0.062142904042727654, equilibrium_temperature=803.7517425393597, insolation_flux=1270.8289063402426),
                             Planet(planet_name='omi 7909 1', host_name='omi 7909', discovery_method='Eclipse Timing Variations', discovery_year=2014, controversial_flag=True, orbital_period=387.3877801523437, planet_radius=12.509960765924289, planet_mass=6688.699844031283, semi_major_radius=105.48679590623095, eccentricity=0.07409543702985111, equilibrium_temperature=2625.585616282664, insolation_flux=1596.9860581359046),
                             Planet(planet_name='omi 7909 2', host_name='omi 7909', discovery_method='Orbital Brightness Modulation', discovery_year=2019, controversial_flag=True, orbital_period=223.4028073286192, planet_radius=18.8164034670573, planet_mass=38.06987464169106, semi_major_radius=40.615311142444234, eccentricity=0.07759475356657541, equilibrium_temperature=685.5987664130316, insolation_flux=1502.00569474722),
                             Planet(planet_name='TOI-1359 b', host_name='TOI-1359', discovery_method='Pulsar Timing', discovery_year=2019, controversial_flag=True, orbital_period=553.4034156427699, planet_radius=10.339917312731316, planet_mass=4018.110556727611, semi_major_radius=137.841434789444, eccentricity=0.058899333646995754, equilibrium_temperature=945.2020134862107, insolation_flux=258.27147476358266),
                             Planet(planet_name='Kepler-5454 2', host_name='Kepler-5454', discovery_method='Imaging', discovery_year=2018, controversial_flag=True, orbital_period=315.76969000073836, planet_radius=14.864619646516507, planet_mass=3392.6633428530204, semi_major_radius=178.6062453245847, eccentricity=0.0834855160914996, equilibrium_temperature=1374.6176771982912, insolation_flux=713.7373899864268),
                             Planet(planet_name='psi1 449 1', host_name='psi1 449', discovery_method='Astrometry', discovery_year=2016, controversial_flag=True, orbital_period=912.1505505151009, planet_radius=11.116743724055883, planet_mass=6807.628858356261, semi_major_radius=144.09458464604933, eccentricity=0.0266175657283605, equilibrium_temperature=1355.3850299521391, insolation_flux=881.3001757307343),
                             Planet(planet_name='kap 1174 1', host_name='kap 1174', discovery_method='Radial Velocity', discovery_year=2015, controversial_flag=True, orbital_period=311.6311789121577, planet_radius=6.675966720994634, planet_mass=5498.034246617799, semi_major_radius=155.74092319186548, eccentricity=0.05065872232668718, equilibrium_temperature=1362.4624314481866, insolation_flux=682.1799848238617),
                             Planet(planet_name='HD 4679 b', host_name='HD 4679', discovery_method='Imaging', discovery_year=2018, controversial_flag=True, orbital_period=623.1447084252951, planet_radius=8.802361662569613, planet_mass=5503.820640345894, semi_major_radius=65.59080199363936, eccentricity=0.06325318091519364, equilibrium_temperature=1266.0353041615958, insolation_flux=581.1596823008617),
                             Planet(planet_name='DP-4166 a', host_name='DP-4166', discovery_method='Pulsar Timing', discovery_year=2020, controversial_flag=True, orbital_period=574.1137756524289, planet_radius=11.694794656197812, planet_mass=5466.00179734124, semi_major_radius=17.670180768986654, eccentricity=0.07325541078022713, equilibrium_temperature=1298.9933476203137, insolation_flux=1577.3290820433156),
                             Planet(planet_name='gam-8271 2', host_name='gam-8271', discovery_method='Radial Velocity', discovery_year=2018, controversial_flag=True, orbital_period=470.0057516594495, planet_radius=5.9156291321616505, planet_mass=1961.4288306981284, semi_major_radius=63.363849618845784, eccentricity=0.08779045532149496, equilibrium_temperature=378.8245348819669, insolation_flux=384.66221263062687),
                             Planet(planet_name='mu2 9885 b', host_name='mu2 9885', discovery_method='Astrometry', discovery_year=2014, controversial_flag=True, orbital_period=743.5115160155736, planet_radius=13.545228905098039, planet_mass=5766.506634011057, semi_major_radius=167.19874603052477, eccentricity=0.09850042474408281, equilibrium_temperature=901.0829375232443, insolation_flux=1340.9835881352096),
                             Planet(planet_name='BD 13482 1', host_name='BD 13482', discovery_method='Radial Velocity', discovery_year=2020, controversial_flag=True, orbital_period=699.609505122432, planet_radius=12.499363542011883, planet_mass=9930.247858768033, semi_major_radius=78.83017048993432, eccentricity=0.0426606933311561, equilibrium_temperature=35.814654445510996, insolation_flux=1251.7241697403497),
                             Planet(planet_name='BD 13482 2', host_name='BD 13482', discovery_method='Microlensing', discovery_year=2018, controversial_flag=True, orbital_period=864.6479048474229, planet_radius=21.93307812602797, planet_mass=3307.8566085287457, semi_major_radius=57.95619059233231, eccentricity=0.05562128119211462, equilibrium_temperature=1061.7246616506063, insolation_flux=1157.9857669504856),
                             Planet(planet_name='TOI 5579 1', host_name='TOI 5579', discovery_method='Pulsar Timing', discovery_year=2018, controversial_flag=True, orbital_period=371.5479024620885, planet_radius=18.761821170306966, planet_mass=8623.566643815871, semi_major_radius=109.19277149201294, eccentricity=0.06878181937107403, equilibrium_temperature=2006.2445535610805, insolation_flux=1101.9680893373559),
                             Planet(planet_name='gam1-2640 a', host_name='gam1-2640', discovery_method='Radial Velocity', discovery_year=2020, controversial_flag=True, orbital_period=478.00501444740286, planet_radius=11.790241748904982, planet_mass=3809.202981653504, semi_major_radius=116.14599926721696, eccentricity=0.04944301548170443, equilibrium_temperature=1175.5083328255255, insolation_flux=2272.338070448862),
                             Planet(planet_name='xi-8427 a', host_name='xi-8427', discovery_method='Microlensing', discovery_year=2019, controversial_flag=True, orbital_period=499.2369334447282, planet_radius=9.442302949274792, planet_mass=5135.706353189335, semi_major_radius=122.34849804591607, eccentricity=0.05417626511332142, equilibrium_temperature=1135.833235334649, insolation_flux=1268.4590231360005),
                             Planet(planet_name='xi-8427 b', host_name='xi-8427', discovery_method='Transit', discovery_year=2019, controversial_flag=True, orbital_period=865.5667169043791, planet_radius=11.363079210446992, planet_mass=3423.227024125669, semi_major_radius=126.27628634253675, eccentricity=0.06518437683303215, equilibrium_temperature=653.2408459727313, insolation_flux=128.82207470296146),
                             Planet(planet_name='kap 8117 1', host_name='kap 8117', discovery_method='Orbital Brightness Modulation', discovery_year=2015, controversial_flag=True, orbital_period=631.7794500540716, planet_radius=13.963348292175112, planet_mass=7484.604742155529, semi_major_radius=121.56057389832073, eccentricity=0.03957841003858472, equilibrium_temperature=320.8406369636016, insolation_flux=500.5540904453085),
                             Planet(planet_name='xi-2449 a', host_name='xi-2449', discovery_method='Pulsation Timing Variations', discovery_year=2014, controversial_flag=True, orbital_period=578.9303767212143, planet_radius=0.8194547334347888, planet_mass=7614.045600422216, semi_major_radius=21.482695884280716, eccentricity=0.044373794965466055, equilibrium_temperature=2538.0980640775388, insolation_flux=991.4186188688709),
                             Planet(planet_name='xi-2449 b', host_name='xi-2449', discovery_method='Pulsar Timing', discovery_year=2018, controversial_flag=True, orbital_period=1.8184423198665627, planet_radius=5.7670744169459445, planet_mass=3953.4969725759656, semi_major_radius=20.21436444354262, eccentricity=0.029786950623638, equilibrium_temperature=1404.6259412354914, insolation_flux=1249.071529526432),
                             Planet(planet_name='2MASS 1180 2', host_name='2MASS 1180', discovery_method='Radial Velocity', discovery_year=2018, controversial_flag=True, orbital_period=556.2962255533296, planet_radius=6.834531046487637, planet_mass=9406.510890376896, semi_major_radius=90.18262348784177, eccentricity=0.015740589420353043, equilibrium_temperature=1382.599756217867, insolation_flux=865.1687144357979),
                             Planet(planet_name='omi-29 a', host_name='omi-29', discovery_method='Pulsation Timing Variations', discovery_year=2019, controversial_flag=True, orbital_period=275.4820715892241, planet_radius=12.64207191903223, planet_mass=4444.300729537826, semi_major_radius=132.11902222551467, eccentricity=0.004120179035294005, equilibrium_temperature=900.7702088862907, insolation_flux=1392.0870693878492)],
                     'q15': [Planet(planet_name='DP 4364 d', host_name='DP 4364', discovery_method='Astrometry', discovery_year=2019, controversial_flag=False, orbital_period=469.6727436637603, planet_radius=13.657584305234444, planet_mass=5543.319324871691, semi_major_radius=137.05813943512797, eccentricity=0.09914372116383643, equilibrium_temperature=1382.6343391970427, insolation_flux=114.39214257005472),
                             Planet(planet_name='tau-9676 1', host_name='tau-9676', discovery_method='Radial Velocity', discovery_year=2019, controversial_flag=False, orbital_period=194.94058310785056, planet_radius=11.144197464406579, planet_mass=4613.541470533974, semi_major_radius=48.0081099980795, eccentricity=0.06175196077255818, equilibrium_temperature=1110.9869772098994, insolation_flux=384.25492520330863),
                             Planet(planet_name='tau-9676 2', host_name='tau-9676', discovery_method='Pulsation Timing Variations', discovery_year=2017, controversial_flag=True, orbital_period=390.804237601967, planet_radius=8.411182456158262, planet_mass=6178.063174828207, semi_major_radius=115.48217854683713, eccentricity=0.05018841680104793, equilibrium_temperature=452.5422494128045, insolation_flux=1116.628693194629),
                             Planet(planet_name='tau-9676 3', host_name='tau-9676', discovery_method='Astrometry', discovery_year=2020, controversial_flag=False, orbital_period=671.6807501395112, planet_radius=1.5504425713647692, planet_mass=1342.2946931274914, semi_major_radius=10.408579848549522, eccentricity=0.07650657631500775, equilibrium_temperature=799.3318987043988, insolation_flux=736.1026141025429),
                             Planet(planet_name='tau-9676 4', host_name='tau-9676', discovery_method='Disk Kinematics', discovery_year=2019, controversial_flag=False, orbital_period=377.2344806886548, planet_radius=15.799312797466222, planet_mass=2422.8691377016603, semi_major_radius=149.88477768244445, eccentricity=0.007735752087186527, equilibrium_temperature=1224.4810815234177, insolation_flux=1543.9484922350944)],
                     'q16': [Planet(planet_name='gam1 4 a', host_name='nu 7840', discovery_method='Disk Kinematics', discovery_year=2019, controversial_flag=False, orbital_period=451.6997308386441, planet_radius=20.91219813658352, planet_mass=5890.986364517897, semi_major_radius=84.06088687192903, eccentricity=0.07325541078022713, equilibrium_temperature=1014.0599528267796, insolation_flux=1304.2033634356972),
                             Planet(planet_name='2MASS 3614 b', host_name='Kepler 7356', discovery_method='Transit Timing Variations', discovery_year=2021, controversial_flag=False, orbital_period=448.46269688635186, planet_radius=8.916592845476774, planet_mass=2090.749248116496, semi_major_radius=104.20901535899203, eccentricity=0.07426074843803412, equilibrium_temperature=1008.9221818558809, insolation_flux=621.9564134937539),
                             Planet(planet_name='alf 6672 2', host_name='gam 31', discovery_method='Radial Velocity', discovery_year=2017, controversial_flag=False, orbital_period=388.9722277615973, planet_radius=14.585828092800197, planet_mass=10984.39055209038, semi_major_radius=29.766872343206742, eccentricity=0.10983336986863995, equilibrium_temperature=742.5680095365574, insolation_flux=1228.824281150972),
                             Planet(planet_name='nu 9722 a', host_name='ups 1320', discovery_method='Orbital Brightness Modulation', discovery_year=2016, controversial_flag=False, orbital_period=420.7816161546713, planet_radius=13.1753094943326, planet_mass=6399.509786071709, semi_major_radius=167.19874603052477, eccentricity=0.04588747963980552, equilibrium_temperature=685.7510873929588, insolation_flux=20.338815323674453),
                             Planet(planet_name='mu2-1576 b', host_name='2MASS-87016', discovery_method='Transit Timing Variations', discovery_year=2017, controversial_flag=True, orbital_period=941.0606809701012, planet_radius=13.681615899333647, planet_mass=8703.948258219885, semi_major_radius=81.7637108212082, eccentricity=0.08899719228339827, equilibrium_temperature=1099.4772920268804, insolation_flux=229.65395069884028)]}
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
