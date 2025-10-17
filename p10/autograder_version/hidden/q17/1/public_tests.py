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
                     'q5': Star(spectral_type='B4.75III', stellar_effective_temperature=5573.0564723062835, stellar_radius=6.869459941484642, stellar_mass=2.648158084649327, stellar_luminosity=-0.33769198107816406, stellar_surface_gravity=1.2116573932691481, stellar_age=3.0911513059941855),
                     'q6': Star(spectral_type='D4.5II-D8VI', stellar_effective_temperature=8367.398111282371, stellar_radius=39.7397929733625, stellar_mass=1.4303439337475852, stellar_luminosity=1.5539000360183788, stellar_surface_gravity=4.626680782604987, stellar_age=9.372781870039688),
                     'q7': -0.25837449525682404,
                     'q8': 6.728239665188022,
                     'q9': 8840.184766101349,
                     'q10': 'xi 7172',
                     'q11': 6.964819280541058,
                     'Planet': Planet(planet_name='Jupiter', host_name='Sun', discovery_method='Imaging', discovery_year=1610, controversial_flag=False, orbital_period=4333.0, planet_radius=11.209, planet_mass=317.828, semi_major_radius=5.2038, eccentricity=0.0489, equilibrium_temperature=110, insolation_flux=0.0345),
                     'q12': Planet(planet_name='mu2 99588 a', host_name='mu2 99588', discovery_method='Orbital Brightness Modulation', discovery_year=2024, controversial_flag=False, orbital_period=189.02747047455955, planet_radius=9.383031623049412, planet_mass=7969.091269936833, semi_major_radius=136.04719209490565, eccentricity=0.028919017964155, equilibrium_temperature=2395.184797742849, insolation_flux=2660.169811264297),
                     'q13': [Planet(planet_name='rho 7093 1', host_name='rho 7093', discovery_method='Disk Kinematics', discovery_year=2022, controversial_flag=True, orbital_period=643.6023929749956, planet_radius=1.0097923688757913, planet_mass=3813.60037478902, semi_major_radius=205.5973064509301, eccentricity=0.056505734928139, equilibrium_temperature=661.9755230683054, insolation_flux=1040.747323287845),
                             Planet(planet_name='rho 1062 a', host_name='rho 1062', discovery_method='Transit Timing Variations', discovery_year=2022, controversial_flag=False, orbital_period=477.0687167802556, planet_radius=10.658129826129649, planet_mass=4374.548735415185, semi_major_radius=166.66033542143134, eccentricity=0.0563170237295758, equilibrium_temperature=1162.8303886760148, insolation_flux=867.2259134887187),
                             Planet(planet_name='mu-7623 a', host_name='mu-7623', discovery_method='Eclipse Timing Variations', discovery_year=2022, controversial_flag=False, orbital_period=418.8528590038858, planet_radius=16.721009053375848, planet_mass=10826.91425342361, semi_major_radius=117.0169370984368, eccentricity=0.0740743008817877, equilibrium_temperature=844.5909405591299, insolation_flux=1297.94187494456),
                             Planet(planet_name='bet-7671 a', host_name='bet-7671', discovery_method='Disk Kinematics', discovery_year=2024, controversial_flag=False, orbital_period=328.56888684740653, planet_radius=19.86572591545845, planet_mass=2638.1530698296788, semi_major_radius=107.96202693698528, eccentricity=0.060055790486768, equilibrium_temperature=965.4922816436316, insolation_flux=1588.884735191411),
                             Planet(planet_name='Kepler-7792 a', host_name='Kepler-7792', discovery_method='Pulsation Timing Variations', discovery_year=2024, controversial_flag=False, orbital_period=525.1721859858791, planet_radius=3.005975702353973, planet_mass=5526.189037686757, semi_major_radius=63.45142086642012, eccentricity=0.0736378319079762, equilibrium_temperature=372.8710382411713, insolation_flux=1170.45093650927)],
                     'q14': [Planet(planet_name='BD-1945 2', host_name='BD-1945', discovery_method='Pulsar Timing', discovery_year=2022, controversial_flag=True, orbital_period=591.3362354162975, planet_radius=19.219473668564525, planet_mass=2871.076348299003, semi_major_radius=125.4477244045516, eccentricity=0.082282585476496, equilibrium_temperature=1340.8834047669138, insolation_flux=2060.096644143709),
                             Planet(planet_name='GJ 8142 1', host_name='GJ 8142', discovery_method='Eclipse Timing Variations', discovery_year=2022, controversial_flag=True, orbital_period=340.30822525977896, planet_radius=13.677995772048314, planet_mass=5167.246004721579, semi_major_radius=211.4434191928031, eccentricity=0.1068159091173459, equilibrium_temperature=717.2877323620276, insolation_flux=751.2699073918236),
                             Planet(planet_name='rho 3362 b', host_name='rho 3362', discovery_method='Imaging', discovery_year=2024, controversial_flag=True, orbital_period=372.7382652694229, planet_radius=6.367105078912099, planet_mass=10823.345165691078, semi_major_radius=98.0830815729592, eccentricity=0.0229084067249843, equilibrium_temperature=2302.4588525700456, insolation_flux=1054.050967688766),
                             Planet(planet_name='xi-38353 1', host_name='xi-38353', discovery_method='Transit Timing Variations', discovery_year=2022, controversial_flag=True, orbital_period=1031.0549552238567, planet_radius=12.674417032048186, planet_mass=5563.397017938018, semi_major_radius=184.62929315687117, eccentricity=0.0686906386445683, equilibrium_temperature=721.0562898407111, insolation_flux=473.8350603066259),
                             Planet(planet_name='GJ 396 1', host_name='GJ 396', discovery_method='Radial Velocity', discovery_year=2024, controversial_flag=True, orbital_period=361.1812024318431, planet_radius=13.961624259589255, planet_mass=8800.711693423671, semi_major_radius=9.810062501478823, eccentricity=0.0819006250333888, equilibrium_temperature=1048.076537932958, insolation_flux=1095.1995429262106),
                             Planet(planet_name='DP 2937 b', host_name='DP 2937', discovery_method='Radial Velocity', discovery_year=2022, controversial_flag=True, orbital_period=613.8187852340271, planet_radius=4.6701856066248, planet_mass=4538.429025921733, semi_major_radius=56.68153076794577, eccentricity=0.0756510382146368, equilibrium_temperature=140.62703304331524, insolation_flux=505.4837794719194),
                             Planet(planet_name='mu-3086 b', host_name='mu-3086', discovery_method='Disk Kinematics', discovery_year=2022, controversial_flag=True, orbital_period=415.349774200361, planet_radius=21.879568730520987, planet_mass=5678.116480927468, semi_major_radius=126.02515609643432, eccentricity=0.0654899184175594, equilibrium_temperature=1582.926217445306, insolation_flux=2100.542435763079),
                             Planet(planet_name='gam1-7844 2', host_name='gam1-7844', discovery_method='Microlensing', discovery_year=2023, controversial_flag=True, orbital_period=225.29188172594013, planet_radius=6.33692163501182, planet_mass=5282.12732849207, semi_major_radius=54.25275173290595, eccentricity=0.0757471895467183, equilibrium_temperature=994.3493672037956, insolation_flux=444.9756271019112),
                             Planet(planet_name='gam1 8981 2', host_name='gam1 8981', discovery_method='Imaging', discovery_year=2023, controversial_flag=True, orbital_period=363.890723184373, planet_radius=18.963295915839076, planet_mass=6576.76584302065, semi_major_radius=220.0462869414621, eccentricity=0.0658000144305365, equilibrium_temperature=1173.4228108786212, insolation_flux=1329.32226913515),
                             Planet(planet_name='mu2 8558 a', host_name='mu2 8558', discovery_method='Disk Kinematics', discovery_year=2024, controversial_flag=True, orbital_period=179.09059646914454, planet_radius=13.422835369129754, planet_mass=6602.7533579913215, semi_major_radius=83.98211586545048, eccentricity=0.0209510429204926, equilibrium_temperature=1542.8632677682294, insolation_flux=1493.4184820870996),
                             Planet(planet_name='mu2 8558 b', host_name='mu2 8558', discovery_method='Radial Velocity', discovery_year=2022, controversial_flag=True, orbital_period=523.9048121764789, planet_radius=18.02160373169743, planet_mass=8080.487166990964, semi_major_radius=152.32115691555651, eccentricity=0.0610636851905436, equilibrium_temperature=1094.8795746344638, insolation_flux=1277.4164890676475),
                             Planet(planet_name='WASP 5052 a', host_name='WASP 5052', discovery_method='Transit Timing Variations', discovery_year=2024, controversial_flag=True, orbital_period=249.09316913220457, planet_radius=11.593429774766747, planet_mass=3223.723668551018, semi_major_radius=98.80786951296508, eccentricity=0.0071119165399028, equilibrium_temperature=607.6622772928818, insolation_flux=104.17436258975728),
                             Planet(planet_name='kap-6503 a', host_name='kap-6503', discovery_method='Eclipse Timing Variations', discovery_year=2024, controversial_flag=True, orbital_period=571.988934610702, planet_radius=3.167160692378511, planet_mass=5953.07200914762, semi_major_radius=229.4980259379646, eccentricity=0.034116654277073, equilibrium_temperature=1524.3715064434346, insolation_flux=1271.5617194821662),
                             Planet(planet_name='Kepler-55358 1', host_name='Kepler-55358', discovery_method='Eclipse Timing Variations', discovery_year=2024, controversial_flag=True, orbital_period=648.9536826781598, planet_radius=9.0762954731026, planet_mass=6456.77534040339, semi_major_radius=91.12235766541136, eccentricity=0.0852005480341252, equilibrium_temperature=2409.6748346388717, insolation_flux=1535.2293494183186),
                             Planet(planet_name='omi-2707 a', host_name='omi-2707', discovery_method='Radial Velocity', discovery_year=2022, controversial_flag=True, orbital_period=715.2511924494444, planet_radius=12.10100376154452, planet_mass=5898.585032141561, semi_major_radius=36.83550277781032, eccentricity=0.110914450873598, equilibrium_temperature=980.604631747234, insolation_flux=494.8794486457922),
                             Planet(planet_name='bet 6178 1', host_name='bet 6178', discovery_method='Pulsation Timing Variations', discovery_year=2024, controversial_flag=True, orbital_period=44.62542364596908, planet_radius=13.866972327112912, planet_mass=2074.154128066275, semi_major_radius=229.2116093467967, eccentricity=0.0322562085385777, equilibrium_temperature=545.0243076255822, insolation_flux=1157.3711933637546),
                             Planet(planet_name='bet 6178 2', host_name='bet 6178', discovery_method='Astrometry', discovery_year=2024, controversial_flag=True, orbital_period=694.3546542633098, planet_radius=15.671962054058042, planet_mass=10787.857170280153, semi_major_radius=92.87937696003938, eccentricity=0.0436146181580988, equilibrium_temperature=1428.21065299779, insolation_flux=1056.211125319609),
                             Planet(planet_name='TOI 8427 1', host_name='TOI 8427', discovery_method='Pulsar Timing', discovery_year=2022, controversial_flag=True, orbital_period=993.2469664886712, planet_radius=13.204356050479817, planet_mass=7206.946952984437, semi_major_radius=88.50800978900631, eccentricity=0.0692298666388604, equilibrium_temperature=1430.0344077208572, insolation_flux=17.561725379176096),
                             Planet(planet_name='GJ-96285 a', host_name='GJ-96285', discovery_method='Orbital Brightness Modulation', discovery_year=2023, controversial_flag=True, orbital_period=798.5340751719195, planet_radius=11.649221242810563, planet_mass=9302.980834854292, semi_major_radius=192.0013692350003, eccentricity=0.0919487952019018, equilibrium_temperature=1294.4202099596223, insolation_flux=315.4730336729659),
                             Planet(planet_name='GJ-96285 b', host_name='GJ-96285', discovery_method='Orbital Brightness Modulation', discovery_year=2022, controversial_flag=True, orbital_period=287.25467957092667, planet_radius=12.085069533352286, planet_mass=4868.832008243242, semi_major_radius=96.15435703606082, eccentricity=0.0502634482898444, equilibrium_temperature=472.1296329555336, insolation_flux=879.0032786361677),
                             Planet(planet_name='Kepler-220 a', host_name='Kepler-220', discovery_method='Microlensing', discovery_year=2024, controversial_flag=True, orbital_period=629.4464424898476, planet_radius=8.350372458526472, planet_mass=3929.4868112722215, semi_major_radius=133.02618841246448, eccentricity=0.0292161629329092, equilibrium_temperature=506.8125285520996, insolation_flux=660.0787130688275),
                             Planet(planet_name='Kepler-220 b', host_name='Kepler-220', discovery_method='Imaging', discovery_year=2022, controversial_flag=True, orbital_period=733.2096206495551, planet_radius=10.576961405450708, planet_mass=5933.092586159653, semi_major_radius=19.210099792889068, eccentricity=0.030528597442598, equilibrium_temperature=1042.4687664121766, insolation_flux=751.1321972575564),
                             Planet(planet_name='ome 9985 b', host_name='ome 9985', discovery_method='Disk Kinematics', discovery_year=2024, controversial_flag=True, orbital_period=912.5757295541983, planet_radius=10.614429771951135, planet_mass=4066.3461376543983, semi_major_radius=133.1099193269831, eccentricity=0.0735818469214964, equilibrium_temperature=1203.6538717796332, insolation_flux=1716.034541959261),
                             Planet(planet_name='mu2 3978 b', host_name='mu2 3978', discovery_method='Radial Velocity', discovery_year=2024, controversial_flag=True, orbital_period=318.19779541528624, planet_radius=4.344742246709315, planet_mass=5919.57827074953, semi_major_radius=101.93440385143964, eccentricity=0.039629270668586, equilibrium_temperature=417.4740099225455, insolation_flux=244.18136678191365),
                             Planet(planet_name='mu-722 a', host_name='mu-722', discovery_method='Eclipse Timing Variations', discovery_year=2022, controversial_flag=True, orbital_period=505.4993729665417, planet_radius=23.314095782058654, planet_mass=2164.3592555890923, semi_major_radius=52.56812711911419, eccentricity=0.0576833155938852, equilibrium_temperature=1535.8938420247714, insolation_flux=1467.053536499311),
                             Planet(planet_name='omi-12289 b', host_name='omi-12289', discovery_method='Pulsar Timing', discovery_year=2024, controversial_flag=True, orbital_period=721.4594346810834, planet_radius=8.674601684124601, planet_mass=6096.746503076767, semi_major_radius=50.72867408584501, eccentricity=0.0443945773336142, equilibrium_temperature=523.7105720094861, insolation_flux=3060.717353914948),
                             Planet(planet_name='bet 2193 1', host_name='bet 2193', discovery_method='Disk Kinematics', discovery_year=2024, controversial_flag=True, orbital_period=455.5644907763271, planet_radius=13.780031474228265, planet_mass=3149.341700834676, semi_major_radius=119.21766784953068, eccentricity=0.0628148137589038, equilibrium_temperature=1676.6332048688664, insolation_flux=1191.9718494014992),
                             Planet(planet_name='omi-1464 b', host_name='omi-1464', discovery_method='Astrometry', discovery_year=2024, controversial_flag=True, orbital_period=182.9224932997028, planet_radius=13.438480121133832, planet_mass=6391.954198678523, semi_major_radius=147.59389239575142, eccentricity=0.0447529689260715, equilibrium_temperature=283.9728391484771, insolation_flux=162.60736600170674),
                             Planet(planet_name='nu 1292 2', host_name='nu 1292', discovery_method='Eclipse Timing Variations', discovery_year=2022, controversial_flag=True, orbital_period=417.5710909986804, planet_radius=8.648506586652234, planet_mass=6543.306909534215, semi_major_radius=8.72498652442087, eccentricity=0.023381991012748, equilibrium_temperature=1322.5119003203745, insolation_flux=216.48307477351352),
                             Planet(planet_name='alf 63014 a', host_name='alf 63014', discovery_method='Eclipse Timing Variations', discovery_year=2023, controversial_flag=True, orbital_period=234.8910847764871, planet_radius=15.032981350493737, planet_mass=3993.867067946383, semi_major_radius=140.69716022430035, eccentricity=0.024146379402457, equilibrium_temperature=1448.942590629063, insolation_flux=1442.993486262419),
                             Planet(planet_name='alf 63014 b', host_name='alf 63014', discovery_method='Transit Timing Variations', discovery_year=2022, controversial_flag=True, orbital_period=515.8312837108216, planet_radius=9.667635436602511, planet_mass=6200.446655512343, semi_major_radius=11.077275984421902, eccentricity=0.0795256408343235, equilibrium_temperature=1977.4621721585968, insolation_flux=667.6915695464179),
                             Planet(planet_name='omi 3656 b', host_name='omi 3656', discovery_method='Astrometry', discovery_year=2022, controversial_flag=True, orbital_period=320.4989506741109, planet_radius=14.50402174797394, planet_mass=6491.704966940906, semi_major_radius=146.20751724657836, eccentricity=0.0211284462956385, equilibrium_temperature=774.5723192830449, insolation_flux=293.92878599578194),
                             Planet(planet_name='nu-47 2', host_name='nu-47', discovery_method='Eclipse Timing Variations', discovery_year=2023, controversial_flag=True, orbital_period=726.4823637922001, planet_radius=13.500531201572947, planet_mass=2206.9936708064924, semi_major_radius=115.5140769244479, eccentricity=0.0182525857796027, equilibrium_temperature=406.5701236984288, insolation_flux=1232.8204979622633),
                             Planet(planet_name='iot-2789 a', host_name='iot-2789', discovery_method='Orbital Brightness Modulation', discovery_year=2023, controversial_flag=True, orbital_period=11.86491817279591, planet_radius=17.527368428707703, planet_mass=5489.118736920234, semi_major_radius=100.57250042858269, eccentricity=0.1027578078461252, equilibrium_temperature=1511.1457142161753, insolation_flux=1137.9653855205604),
                             Planet(planet_name='iot-2789 b', host_name='iot-2789', discovery_method='Transit Timing Variations', discovery_year=2024, controversial_flag=True, orbital_period=856.2801040057407, planet_radius=11.833005790220696, planet_mass=6690.412704268047, semi_major_radius=35.52549505953857, eccentricity=0.0405079338400091, equilibrium_temperature=830.942830079802, insolation_flux=1054.2327308338895),
                             Planet(planet_name='gam1 84 a', host_name='gam1 84', discovery_method='Astrometry', discovery_year=2024, controversial_flag=True, orbital_period=538.6723048608617, planet_radius=2.1017051635694752, planet_mass=5765.9732019864805, semi_major_radius=142.83609902247449, eccentricity=0.0519794734700597, equilibrium_temperature=1078.60904735165, insolation_flux=562.830046808304),
                             Planet(planet_name='psi1 3400 a', host_name='psi1 3400', discovery_method='Radial Velocity', discovery_year=2024, controversial_flag=True, orbital_period=11.373838672634122, planet_radius=11.122820059535664, planet_mass=2284.302487470898, semi_major_radius=179.78838420981316, eccentricity=0.0087554599325629, equilibrium_temperature=947.4298568975424, insolation_flux=970.9306032994564),
                             Planet(planet_name='omi-1073 a', host_name='omi-1073', discovery_method='Transit Timing Variations', discovery_year=2024, controversial_flag=True, orbital_period=508.1897758292295, planet_radius=11.20838275331167, planet_mass=2871.526297888316, semi_major_radius=65.00032855161584, eccentricity=0.0714821497103258, equilibrium_temperature=1246.000887839948, insolation_flux=692.0780970367456),
                             Planet(planet_name='tau 3732 a', host_name='tau 3732', discovery_method='Radial Velocity', discovery_year=2022, controversial_flag=True, orbital_period=353.392473583237, planet_radius=15.262581684302567, planet_mass=7773.2217621303935, semi_major_radius=45.09652697374965, eccentricity=0.022519845693433, equilibrium_temperature=2117.8017278376983, insolation_flux=490.69945184906135),
                             Planet(planet_name='tau 3732 b', host_name='tau 3732', discovery_method='Eclipse Timing Variations', discovery_year=2022, controversial_flag=True, orbital_period=873.3678443744708, planet_radius=18.74282943714634, planet_mass=4199.0711645996935, semi_major_radius=107.98290417918096, eccentricity=0.0300651194527371, equilibrium_temperature=1176.1991273753133, insolation_flux=2212.6983369708714),
                             Planet(planet_name='omi-5290 1', host_name='omi-5290', discovery_method='Orbital Brightness Modulation', discovery_year=2022, controversial_flag=True, orbital_period=328.79491953834736, planet_radius=15.342634804570162, planet_mass=6286.358689580693, semi_major_radius=57.41369624771248, eccentricity=0.0614264720666571, equilibrium_temperature=1835.0542598690504, insolation_flux=1650.2606856826635),
                             Planet(planet_name='tau 9900 a', host_name='tau 9900', discovery_method='Transit', discovery_year=2023, controversial_flag=True, orbital_period=853.3516498955686, planet_radius=1.6174414443782368, planet_mass=8479.056167019251, semi_major_radius=77.62401706725619, eccentricity=0.0219806701277363, equilibrium_temperature=1869.7170695571417, insolation_flux=1406.695406385393),
                             Planet(planet_name='2MASS-5718 2', host_name='2MASS-5718', discovery_method='Transit Timing Variations', discovery_year=2024, controversial_flag=True, orbital_period=529.6576290227249, planet_radius=13.30928038648589, planet_mass=6087.959258111973, semi_major_radius=98.89675180588772, eccentricity=0.0490578254347046, equilibrium_temperature=687.3508598017893, insolation_flux=828.5410200905633),
                             Planet(planet_name='rho 6934 b', host_name='rho 6934', discovery_method='Pulsation Timing Variations', discovery_year=2024, controversial_flag=True, orbital_period=727.8300953089956, planet_radius=8.54356116171674, planet_mass=9749.320936151806, semi_major_radius=201.05318270602172, eccentricity=0.0416614675641778, equilibrium_temperature=1012.208905475167, insolation_flux=2626.428136820512),
                             Planet(planet_name='CoRoT-2666 1', host_name='CoRoT-2666', discovery_method='Transit', discovery_year=2024, controversial_flag=True, orbital_period=554.610821610572, planet_radius=6.3139354165039885, planet_mass=6801.091069122134, semi_major_radius=157.1374765547626, eccentricity=0.055523128770519, equilibrium_temperature=1201.330790516139, insolation_flux=1315.407247223095),
                             Planet(planet_name='xi 1901 a', host_name='xi 1901', discovery_method='Astrometry', discovery_year=2024, controversial_flag=True, orbital_period=581.5494550442075, planet_radius=3.4608120735999077, planet_mass=226.7962916541073, semi_major_radius=39.36743156981466, eccentricity=0.0654979961064877, equilibrium_temperature=806.080196784914, insolation_flux=739.9010501232284),
                             Planet(planet_name='xi 1901 b', host_name='xi 1901', discovery_method='Transit Timing Variations', discovery_year=2022, controversial_flag=True, orbital_period=169.34954028248836, planet_radius=17.54840596431107, planet_mass=4304.433811644175, semi_major_radius=92.30685515261592, eccentricity=0.0209245130852541, equilibrium_temperature=1253.226893603937, insolation_flux=2518.4391746854253),
                             Planet(planet_name='xi 40 1', host_name='xi 40', discovery_method='Microlensing', discovery_year=2024, controversial_flag=True, orbital_period=2.6925167771959195, planet_radius=8.706072866513715, planet_mass=2566.057980177109, semi_major_radius=118.56479198774971, eccentricity=0.0453907980887878, equilibrium_temperature=1670.8253903421355, insolation_flux=1695.0246011303648),
                             Planet(planet_name='iot 8461 a', host_name='iot 8461', discovery_method='Imaging', discovery_year=2023, controversial_flag=True, orbital_period=407.23722121475305, planet_radius=12.3647261765485, planet_mass=5875.947252880107, semi_major_radius=109.2818907168701, eccentricity=0.0547480477372533, equilibrium_temperature=2223.858084035003, insolation_flux=2045.6089527650192),
                             Planet(planet_name='Kepler-592 a', host_name='Kepler-592', discovery_method='Disk Kinematics', discovery_year=2022, controversial_flag=True, orbital_period=35.09730763333164, planet_radius=3.906764677177789, planet_mass=3888.0813642778858, semi_major_radius=4.609609486960864, eccentricity=0.0193160716759211, equilibrium_temperature=1501.8755369833502, insolation_flux=913.4662656448434),
                             Planet(planet_name='GJ-722 b', host_name='GJ-722', discovery_method='Eclipse Timing Variations', discovery_year=2022, controversial_flag=True, orbital_period=477.6842330013533, planet_radius=17.134101619757818, planet_mass=4933.976319961334, semi_major_radius=59.44993505249085, eccentricity=0.0428705917040679, equilibrium_temperature=538.7550162250201, insolation_flux=2053.930580359288),
                             Planet(planet_name='mu 3862 2', host_name='mu 3862', discovery_method='Imaging', discovery_year=2022, controversial_flag=True, orbital_period=635.1794045225524, planet_radius=18.380161552218453, planet_mass=2463.374732974627, semi_major_radius=68.15007044744661, eccentricity=0.0668850737047948, equilibrium_temperature=1897.443691465075, insolation_flux=1175.5868702586013),
                             Planet(planet_name='gam1 3730 b', host_name='gam1 3730', discovery_method='Transit', discovery_year=2023, controversial_flag=True, orbital_period=543.8129724496858, planet_radius=10.994531443119618, planet_mass=4313.921192873367, semi_major_radius=76.82440144258553, eccentricity=0.0258452466985748, equilibrium_temperature=1127.855285374867, insolation_flux=1305.465229801218),
                             Planet(planet_name='rho 2332 2', host_name='rho 2332', discovery_method='Pulsation Timing Variations', discovery_year=2024, controversial_flag=True, orbital_period=48.492455453891694, planet_radius=11.997486751716565, planet_mass=5577.22043037185, semi_major_radius=94.04650218657096, eccentricity=0.090703767098134, equilibrium_temperature=1151.628444977322, insolation_flux=1249.0216247670849),
                             Planet(planet_name='tau-3151 2', host_name='tau-3151', discovery_method='Imaging', discovery_year=2022, controversial_flag=True, orbital_period=770.2507645203873, planet_radius=6.215606921270497, planet_mass=6803.040918443638, semi_major_radius=246.16276312973616, eccentricity=0.1102110012972056, equilibrium_temperature=796.9141583406908, insolation_flux=607.2964699087563),
                             Planet(planet_name='eps-9458 a', host_name='eps-9458', discovery_method='Imaging', discovery_year=2024, controversial_flag=True, orbital_period=358.839766305695, planet_radius=10.55796721167694, planet_mass=8146.874268499911, semi_major_radius=149.83772181588773, eccentricity=0.0528464481102794, equilibrium_temperature=722.3054287782805, insolation_flux=1554.7246642624098),
                             Planet(planet_name='eps-9458 b', host_name='eps-9458', discovery_method='Transit', discovery_year=2023, controversial_flag=True, orbital_period=452.4896500663749, planet_radius=2.647973175025136, planet_mass=2984.9414517976284, semi_major_radius=20.098496729449156, eccentricity=0.0713746114614992, equilibrium_temperature=598.8216060475793, insolation_flux=741.6943907200636),
                             Planet(planet_name='DP 7792 a', host_name='DP 7792', discovery_method='Imaging', discovery_year=2024, controversial_flag=True, orbital_period=981.0260317260272, planet_radius=15.978002031747607, planet_mass=491.28970758295054, semi_major_radius=183.5773004145397, eccentricity=0.0387516605615414, equilibrium_temperature=846.1021402001186, insolation_flux=1484.081766196541),
                             Planet(planet_name='gam1 83705 1', host_name='gam1 83705', discovery_method='Transit', discovery_year=2022, controversial_flag=True, orbital_period=669.8894982135977, planet_radius=13.611118698828207, planet_mass=3757.637063949644, semi_major_radius=159.44703505975798, eccentricity=0.0248519446348104, equilibrium_temperature=2078.002256765272, insolation_flux=1779.5673554181376),
                             Planet(planet_name='nu 7196 b', host_name='nu 7196', discovery_method='Radial Velocity', discovery_year=2022, controversial_flag=True, orbital_period=321.87282105457984, planet_radius=17.687360422980362, planet_mass=4214.534544065987, semi_major_radius=123.98962354441824, eccentricity=0.0679911347236363, equilibrium_temperature=1487.197245564177, insolation_flux=70.1094578271991),
                             Planet(planet_name='HD 1305 b', host_name='HD 1305', discovery_method='Microlensing', discovery_year=2022, controversial_flag=True, orbital_period=724.6157303623706, planet_radius=10.866806538725852, planet_mass=4767.358223441813, semi_major_radius=58.84201990116826, eccentricity=0.0638841104185394, equilibrium_temperature=646.3270871665031, insolation_flux=2274.403476639526),
                             Planet(planet_name='Kepler 9540 1', host_name='Kepler 9540', discovery_method='Microlensing', discovery_year=2022, controversial_flag=True, orbital_period=274.02341195780843, planet_radius=5.647410397110048, planet_mass=6808.892255189154, semi_major_radius=111.47527693680496, eccentricity=0.007035588525651, equilibrium_temperature=1419.14577333153, insolation_flux=2524.1714040746783),
                             Planet(planet_name='psi1-2104 a', host_name='psi1-2104', discovery_method='Transit Timing Variations', discovery_year=2022, controversial_flag=True, orbital_period=61.16326744663178, planet_radius=16.285609055666434, planet_mass=7488.534486567145, semi_major_radius=133.76152378989806, eccentricity=0.0482434119322112, equilibrium_temperature=2435.5739992444887, insolation_flux=1593.0245460986978),
                             Planet(planet_name='psi1-2104 b', host_name='psi1-2104', discovery_method='Imaging', discovery_year=2022, controversial_flag=True, orbital_period=714.9878343986564, planet_radius=18.33483436243596, planet_mass=5632.921327434509, semi_major_radius=121.49052542894648, eccentricity=0.0725307881621594, equilibrium_temperature=625.593838832518, insolation_flux=169.58451991455638),
                             Planet(planet_name='gam1 2287 a', host_name='gam1 2287', discovery_method='Disk Kinematics', discovery_year=2024, controversial_flag=True, orbital_period=281.3720488508386, planet_radius=12.219688805817832, planet_mass=5649.916172697111, semi_major_radius=30.78024686816255, eccentricity=0.0076528943790628, equilibrium_temperature=1196.6555884870818, insolation_flux=2038.464249110052),
                             Planet(planet_name='iot 3656 2', host_name='iot 3656', discovery_method='Microlensing', discovery_year=2022, controversial_flag=True, orbital_period=520.5621709531212, planet_radius=20.044929990643148, planet_mass=4155.404684999456, semi_major_radius=77.75254496592525, eccentricity=0.0461036668525971, equilibrium_temperature=2224.5368967088643, insolation_flux=1311.2796650888372),
                             Planet(planet_name='mu 2553 a', host_name='mu 2553', discovery_method='Disk Kinematics', discovery_year=2024, controversial_flag=True, orbital_period=1062.3234094043455, planet_radius=2.155060596653451, planet_mass=3246.2070234160856, semi_major_radius=17.45585491204814, eccentricity=0.0710421657340364, equilibrium_temperature=1146.425537228757, insolation_flux=1628.269936828075),
                             Planet(planet_name='mu2-59417 b', host_name='mu2-59417', discovery_method='Astrometry', discovery_year=2024, controversial_flag=True, orbital_period=875.1068728413908, planet_radius=14.07801026404313, planet_mass=3234.5158554256027, semi_major_radius=135.12516743857572, eccentricity=0.0863485243504635, equilibrium_temperature=537.4377722631313, insolation_flux=89.02861222379249),
                             Planet(planet_name='ome 1615 2', host_name='ome 1615', discovery_method='Orbital Brightness Modulation', discovery_year=2022, controversial_flag=True, orbital_period=237.0652731067658, planet_radius=2.191715368907511, planet_mass=1338.2611931355714, semi_major_radius=149.1962495952946, eccentricity=0.0694073448787205, equilibrium_temperature=1036.9916351942436, insolation_flux=900.6603043921318),
                             Planet(planet_name='2MASS 7333 2', host_name='2MASS 7333', discovery_method='Imaging', discovery_year=2022, controversial_flag=True, orbital_period=809.6657251254177, planet_radius=9.912311432323545, planet_mass=7002.209546881517, semi_major_radius=61.4692667589155, eccentricity=0.0558696717540313, equilibrium_temperature=2321.062891666518, insolation_flux=970.6523654837192),
                             Planet(planet_name='omi-6223 a', host_name='omi-6223', discovery_method='Astrometry', discovery_year=2022, controversial_flag=True, orbital_period=184.1022013713168, planet_radius=0.5832524163574622, planet_mass=2795.466308138385, semi_major_radius=144.79137140804693, eccentricity=0.0236177063295241, equilibrium_temperature=816.0486793348509, insolation_flux=1024.3242917907703),
                             Planet(planet_name='omi-6223 b', host_name='omi-6223', discovery_method='Eclipse Timing Variations', discovery_year=2024, controversial_flag=True, orbital_period=782.1190705466261, planet_radius=10.362953579024753, planet_mass=6126.7499006930175, semi_major_radius=114.73196306497162, eccentricity=0.0336610773847138, equilibrium_temperature=635.5201053619928, insolation_flux=1740.104575884952),
                             Planet(planet_name='alf 8575 1', host_name='alf 8575', discovery_method='Microlensing', discovery_year=2024, controversial_flag=True, orbital_period=316.9498027301633, planet_radius=25.185690768936315, planet_mass=3351.928648859476, semi_major_radius=87.33917854455295, eccentricity=0.0564502261305695, equilibrium_temperature=612.1869083789979, insolation_flux=1458.5961744732683),
                             Planet(planet_name='ome 822 b', host_name='ome 822', discovery_method='Pulsar Timing', discovery_year=2022, controversial_flag=True, orbital_period=746.1617957379866, planet_radius=2.75498661515247, planet_mass=4398.264580733701, semi_major_radius=86.00899911803364, eccentricity=0.0557470969290281, equilibrium_temperature=1323.8257582878546, insolation_flux=813.5714877624184),
                             Planet(planet_name='DP 6796 a', host_name='DP 6796', discovery_method='Eclipse Timing Variations', discovery_year=2024, controversial_flag=True, orbital_period=209.6767169252705, planet_radius=8.028686502742584, planet_mass=3860.441059279654, semi_major_radius=211.47321841256536, eccentricity=0.1019205830284185, equilibrium_temperature=1042.03401948827, insolation_flux=2863.979874343236),
                             Planet(planet_name='alf-5 2', host_name='alf-5', discovery_method='Pulsar Timing', discovery_year=2024, controversial_flag=True, orbital_period=517.7648787984482, planet_radius=7.176443115428334, planet_mass=3951.103823008655, semi_major_radius=139.57129118954288, eccentricity=0.0101520777579131, equilibrium_temperature=1567.27124833043, insolation_flux=914.5983236721866),
                             Planet(planet_name='ups-2665 a', host_name='ups-2665', discovery_method='Eclipse Timing Variations', discovery_year=2024, controversial_flag=True, orbital_period=699.4030706592586, planet_radius=14.38077387764454, planet_mass=1822.500397819595, semi_major_radius=74.7724370184232, eccentricity=0.0214778163716558, equilibrium_temperature=475.9339513595214, insolation_flux=597.9738366772717),
                             Planet(planet_name='psi1-6961 a', host_name='psi1-6961', discovery_method='Transit Timing Variations', discovery_year=2022, controversial_flag=True, orbital_period=177.74226161114052, planet_radius=18.26053465276789, planet_mass=208.3893570271757, semi_major_radius=129.0188768001563, eccentricity=0.0581311604202875, equilibrium_temperature=1560.5415641242755, insolation_flux=1271.306527942205),
                             Planet(planet_name='psi1-6961 b', host_name='psi1-6961', discovery_method='Astrometry', discovery_year=2024, controversial_flag=True, orbital_period=175.9907081606317, planet_radius=16.1604442512748, planet_mass=3720.316313793514, semi_major_radius=147.9766672255645, eccentricity=0.0496785335491688, equilibrium_temperature=346.007858797396, insolation_flux=1625.7430721444014),
                             Planet(planet_name='alf 9493 2', host_name='alf 9493', discovery_method='Transit', discovery_year=2022, controversial_flag=True, orbital_period=902.6177831873716, planet_radius=16.696445940721166, planet_mass=5634.679224375723, semi_major_radius=142.39684584636308, eccentricity=0.0386291385908055, equilibrium_temperature=1387.8653587388694, insolation_flux=975.4413811801423),
                             Planet(planet_name='ups-8323 b', host_name='ups-8323', discovery_method='Astrometry', discovery_year=2024, controversial_flag=True, orbital_period=398.77132261840336, planet_radius=9.921727299969689, planet_mass=4410.475583330842, semi_major_radius=149.539091934244, eccentricity=0.0820594450840446, equilibrium_temperature=964.7581565133784, insolation_flux=722.0258023388694),
                             Planet(planet_name='tau-55358 1', host_name='tau-55358', discovery_method='Pulsation Timing Variations', discovery_year=2024, controversial_flag=True, orbital_period=181.1691761221993, planet_radius=20.96988833289088, planet_mass=4628.077634069218, semi_major_radius=59.11416958481964, eccentricity=0.095839620838473, equilibrium_temperature=701.4185784153478, insolation_flux=1281.4901473166535),
                             Planet(planet_name='tau-55358 2', host_name='tau-55358', discovery_method='Eclipse Timing Variations', discovery_year=2024, controversial_flag=True, orbital_period=500.6103154476063, planet_radius=5.718532982016832, planet_mass=986.5887510231246, semi_major_radius=105.6530052818819, eccentricity=0.0031367058590998, equilibrium_temperature=1066.8652613052193, insolation_flux=1499.602822613664),
                             Planet(planet_name='mu 607 1', host_name='mu 607', discovery_method='Pulsar Timing', discovery_year=2023, controversial_flag=True, orbital_period=284.6590821944173, planet_radius=12.734242438353508, planet_mass=6297.226370387216, semi_major_radius=116.09802749291428, eccentricity=0.0663950385255672, equilibrium_temperature=1832.8111165983623, insolation_flux=1939.998836877789),
                             Planet(planet_name='CoRoT 55320 1', host_name='CoRoT 55320', discovery_method='Astrometry', discovery_year=2024, controversial_flag=True, orbital_period=732.9515612031855, planet_radius=14.820416695190035, planet_mass=3224.081157391249, semi_major_radius=81.68674275108377, eccentricity=0.0373420835230838, equilibrium_temperature=906.8168642594042, insolation_flux=424.308120880504),
                             Planet(planet_name='DP-994 a', host_name='DP-994', discovery_method='Radial Velocity', discovery_year=2024, controversial_flag=True, orbital_period=539.9789952238004, planet_radius=21.119412792856533, planet_mass=6747.47103762975, semi_major_radius=119.21584241663652, eccentricity=0.0739970521702429, equilibrium_temperature=670.0652448728315, insolation_flux=2025.13588282759),
                             Planet(planet_name='mu2-5781 a', host_name='mu2-5781', discovery_method='Transit Timing Variations', discovery_year=2024, controversial_flag=True, orbital_period=1044.2692535815218, planet_radius=18.506308054345205, planet_mass=7878.998604853363, semi_major_radius=79.33187880247382, eccentricity=0.0321816787343347, equilibrium_temperature=1916.052279937002, insolation_flux=1205.511200800495),
                             Planet(planet_name='rho 1089 2', host_name='rho 1089', discovery_method='Eclipse Timing Variations', discovery_year=2024, controversial_flag=True, orbital_period=502.5952106901921, planet_radius=14.19645132611285, planet_mass=4572.39292490733, semi_major_radius=96.89613501812389, eccentricity=0.07294527842842, equilibrium_temperature=1272.3856241815674, insolation_flux=906.8524593975624),
                             Planet(planet_name='eps-8038 a', host_name='eps-8038', discovery_method='Transit', discovery_year=2024, controversial_flag=True, orbital_period=333.88824170327644, planet_radius=7.721941242156957, planet_mass=1738.9511602654538, semi_major_radius=72.95851643082734, eccentricity=0.0628496900879421, equilibrium_temperature=561.4810858350638, insolation_flux=303.7339811380182),
                             Planet(planet_name='eps-8038 b', host_name='eps-8038', discovery_method='Transit Timing Variations', discovery_year=2024, controversial_flag=True, orbital_period=326.619725236667, planet_radius=10.275278893996171, planet_mass=6984.511804599265, semi_major_radius=130.24824361976096, eccentricity=0.0382160751902012, equilibrium_temperature=1308.287800628336, insolation_flux=1752.6405174908891),
                             Planet(planet_name='rho-3804 1', host_name='rho-3804', discovery_method='Transit Timing Variations', discovery_year=2024, controversial_flag=True, orbital_period=615.7351451460927, planet_radius=8.399180540529631, planet_mass=4047.348858939668, semi_major_radius=174.24378856151418, eccentricity=0.0483537999850253, equilibrium_temperature=746.0447710142862, insolation_flux=1613.3475177834775)],
                     'q15': [Planet(planet_name='Kepler 7133 4', host_name='Kepler 7133', discovery_method='Disk Kinematics', discovery_year=2022, controversial_flag=False, orbital_period=585.302000143658, planet_radius=20.695347193397936, planet_mass=7881.001464395264, semi_major_radius=107.88700670335967, eccentricity=0.0546296470021251, equilibrium_temperature=981.2005496501504, insolation_flux=1002.4945562938868),
                             Planet(planet_name='2MASS-8892 1', host_name='2MASS-8892', discovery_method='Transit Timing Variations', discovery_year=2022, controversial_flag=False, orbital_period=470.1480331850986, planet_radius=5.961740698323072, planet_mass=3521.087091856274, semi_major_radius=149.3496957305446, eccentricity=0.0993339022029745, equilibrium_temperature=1688.149034811718, insolation_flux=1086.9086774429504),
                             Planet(planet_name='2MASS-8892 2', host_name='2MASS-8892', discovery_method='Radial Velocity', discovery_year=2022, controversial_flag=False, orbital_period=278.5336976349641, planet_radius=1.0349658600541929, planet_mass=9116.867210475262, semi_major_radius=201.3170353954968, eccentricity=0.1105676174727275, equilibrium_temperature=2562.5737322738105, insolation_flux=903.5877694156202),
                             Planet(planet_name='2MASS-8892 3', host_name='2MASS-8892', discovery_method='Radial Velocity', discovery_year=2022, controversial_flag=False, orbital_period=200.12865175712776, planet_radius=5.461153345773251, planet_mass=3503.749916393496, semi_major_radius=147.89751656154095, eccentricity=0.0458402099700624, equilibrium_temperature=934.897767520892, insolation_flux=324.845044705953),
                             Planet(planet_name='2MASS-8892 4', host_name='2MASS-8892', discovery_method='Disk Kinematics', discovery_year=2024, controversial_flag=False, orbital_period=993.52343740241, planet_radius=15.882831314378148, planet_mass=3009.859076291467, semi_major_radius=149.22174688894145, eccentricity=3.3411922643888925e-06, equilibrium_temperature=1487.376669600509, insolation_flux=828.1454395707342)],
                     'q16': [],
                     'q17': 200}
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
