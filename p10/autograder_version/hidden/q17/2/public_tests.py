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
                     'q5': Star(spectral_type='G3I', stellar_effective_temperature=6386.984745065553, stellar_radius=22.491501873685223, stellar_mass=1.0006911926505753, stellar_luminosity=-0.04835308496366869, stellar_surface_gravity=4.57514306773777, stellar_age=3.329984867089608),
                     'q7': -0.10709539476122151,
                     'q8': 6.69671818829985,
                     'q9': 8239.893130909533,
                     'q10': 'DP 8403',
                     'q11': 7.352415066679387,
                     'Planet': Planet(planet_name='Jupiter', host_name='Sun', discovery_method='Imaging', discovery_year=1610, controversial_flag=False, orbital_period=4333.0, planet_radius=11.209, planet_mass=317.828, semi_major_radius=5.2038, eccentricity=0.0489, equilibrium_temperature=110, insolation_flux=0.0345),
                     'q12': Planet(planet_name='HD-6976 a', host_name='HD-6976', discovery_method='Imaging', discovery_year=2019, controversial_flag=False, orbital_period=643.2307512944187, planet_radius=4.747919071158592, planet_mass=5729.280291096461, semi_major_radius=150.2153240010658, eccentricity=0.0197948729605102, equilibrium_temperature=1646.4425568641252, insolation_flux=1782.5763614230204),
                     'q13': [Planet(planet_name='TOI-6630 1', host_name='TOI-6630', discovery_method='Imaging', discovery_year=2017, controversial_flag=True, orbital_period=527.2982209667373, planet_radius=8.584310716251078, planet_mass=7339.048109497814, semi_major_radius=91.44653905679228, eccentricity=0.008705868495172, equilibrium_temperature=2023.4520028626168, insolation_flux=402.5118413342436),
                             Planet(planet_name='BD 793 1', host_name='BD 793', discovery_method='Radial Velocity', discovery_year=2019, controversial_flag=False, orbital_period=575.3763020476019, planet_radius=13.597823248583154, planet_mass=3106.623557414694, semi_major_radius=49.751382247152485, eccentricity=0.0805731910132923, equilibrium_temperature=225.23885444945552, insolation_flux=1052.298722557853),
                             Planet(planet_name='bet-4518 1', host_name='bet-4518', discovery_method='Radial Velocity', discovery_year=2023, controversial_flag=True, orbital_period=524.6682991492393, planet_radius=5.988150814138186, planet_mass=6678.212611861669, semi_major_radius=26.15650565782704, eccentricity=0.0183450512617828, equilibrium_temperature=454.215990716335, insolation_flux=879.383354893467),
                             Planet(planet_name='rho 7288 1', host_name='rho 7288', discovery_method='Transit Timing Variations', discovery_year=2020, controversial_flag=False, orbital_period=278.3372068601471, planet_radius=26.27548849595618, planet_mass=2179.140113925101, semi_major_radius=50.99383987879933, eccentricity=0.0423379566401309, equilibrium_temperature=1291.2448001635353, insolation_flux=167.47978711797623),
                             Planet(planet_name='mu2-3722 a', host_name='mu2-3722', discovery_method='Transit Timing Variations', discovery_year=2023, controversial_flag=False, orbital_period=475.594250612273, planet_radius=9.592919695319647, planet_mass=2400.65888081721, semi_major_radius=200.9432072313553, eccentricity=0.0786030282750386, equilibrium_temperature=1446.451463315282, insolation_flux=459.8533686158404)],
                     'q14': [Planet(planet_name='kap 66252 2', host_name='kap 66252', discovery_method='Imaging', discovery_year=2020, controversial_flag=True, orbital_period=796.1398610377444, planet_radius=15.964931887062017, planet_mass=4025.107981381713, semi_major_radius=113.75836681372527, eccentricity=0.0703143469580246, equilibrium_temperature=1130.8925359743685, insolation_flux=970.2307011450308),
                             Planet(planet_name='WASP-184 1', host_name='WASP-184', discovery_method='Pulsar Timing', discovery_year=2019, controversial_flag=True, orbital_period=245.81073913561573, planet_radius=22.38164090038409, planet_mass=5293.732237201876, semi_major_radius=47.41998932288334, eccentricity=0.0439592432220092, equilibrium_temperature=984.07794784895, insolation_flux=927.2000953460944),
                             Planet(planet_name='2MASS-9398 b', host_name='2MASS-9398', discovery_method='Astrometry', discovery_year=2020, controversial_flag=True, orbital_period=189.39500414481532, planet_radius=8.989383108952168, planet_mass=5010.161862190723, semi_major_radius=133.18436244293608, eccentricity=0.1047434640662963, equilibrium_temperature=903.3695058763294, insolation_flux=646.4460398332712),
                             Planet(planet_name='omi 27967 a', host_name='omi 27967', discovery_method='Pulsation Timing Variations', discovery_year=2023, controversial_flag=True, orbital_period=638.1360026110958, planet_radius=1.789395867929482, planet_mass=2713.851705219241, semi_major_radius=256.6067557585519, eccentricity=0.1175715529236542, equilibrium_temperature=1798.6019007683176, insolation_flux=1869.9205489471155),
                             Planet(planet_name='eps-9247 2', host_name='eps-9247', discovery_method='Radial Velocity', discovery_year=2023, controversial_flag=True, orbital_period=340.25068128373823, planet_radius=2.4404069338885077, planet_mass=3820.130870909316, semi_major_radius=117.2746531270828, eccentricity=0.0667606091610569, equilibrium_temperature=661.2666664605756, insolation_flux=2216.64339817623),
                             Planet(planet_name='omi 84136 2', host_name='omi 84136', discovery_method='Pulsation Timing Variations', discovery_year=2014, controversial_flag=True, orbital_period=599.164408662037, planet_radius=4.148995036468841, planet_mass=3210.81069236809, semi_major_radius=211.40898077006477, eccentricity=0.0121922526350606, equilibrium_temperature=245.69272604739115, insolation_flux=1036.719615809394),
                             Planet(planet_name='rho 7990 a', host_name='rho 7990', discovery_method='Astrometry', discovery_year=2023, controversial_flag=True, orbital_period=114.03389198195372, planet_radius=7.710494284123472, planet_mass=9001.545547264514, semi_major_radius=118.13630941437906, eccentricity=0.0887680141568738, equilibrium_temperature=1501.8890721077955, insolation_flux=1430.4348822759791),
                             Planet(planet_name='kap 5758 a', host_name='kap 5758', discovery_method='Pulsation Timing Variations', discovery_year=2021, controversial_flag=True, orbital_period=219.23557706517045, planet_radius=8.922208045665728, planet_mass=5061.1584528497, semi_major_radius=76.38607321321243, eccentricity=0.0260530265364785, equilibrium_temperature=2266.0257919605165, insolation_flux=2367.2969080175244),
                             Planet(planet_name='EPIC-2459 2', host_name='EPIC-2459', discovery_method='Disk Kinematics', discovery_year=2020, controversial_flag=True, orbital_period=820.3285098351876, planet_radius=8.244277309978322, planet_mass=8194.66187199455, semi_major_radius=4.707596569209102, eccentricity=0.0794200349488084, equilibrium_temperature=1246.087495016753, insolation_flux=920.0211705370108),
                             Planet(planet_name='rho 1176 2', host_name='rho 1176', discovery_method='Microlensing', discovery_year=2023, controversial_flag=True, orbital_period=158.39668984016856, planet_radius=8.385058209606026, planet_mass=4164.693401878424, semi_major_radius=30.371041976101694, eccentricity=0.0142110424153791, equilibrium_temperature=666.4241225685444, insolation_flux=711.5451889397823),
                             Planet(planet_name='mu2 56297 2', host_name='mu2 56297', discovery_method='Radial Velocity', discovery_year=2023, controversial_flag=True, orbital_period=69.77341806924414, planet_radius=18.70106283734029, planet_mass=2938.624512527937, semi_major_radius=59.499350523340325, eccentricity=0.0560284695903979, equilibrium_temperature=1217.323769870189, insolation_flux=945.1364901676692),
                             Planet(planet_name='BD 8489 2', host_name='BD 8489', discovery_method='Astrometry', discovery_year=2023, controversial_flag=True, orbital_period=599.96388989548, planet_radius=13.740846004674436, planet_mass=4127.1504827814615, semi_major_radius=74.27906627390344, eccentricity=0.0414198554014124, equilibrium_temperature=1517.2999714950745, insolation_flux=790.835812329303),
                             Planet(planet_name='Kepler 2269 2', host_name='Kepler 2269', discovery_method='Transit', discovery_year=2018, controversial_flag=True, orbital_period=25.779869669316497, planet_radius=8.32716706125698, planet_mass=5394.946920435724, semi_major_radius=174.51375123382513, eccentricity=0.0691020924541329, equilibrium_temperature=570.845984378176, insolation_flux=1377.0536142829892),
                             Planet(planet_name='rho 7479 b', host_name='rho 7479', discovery_method='Disk Kinematics', discovery_year=2020, controversial_flag=True, orbital_period=352.2909128898226, planet_radius=5.842327104244854, planet_mass=3936.45069269364, semi_major_radius=171.79542528084414, eccentricity=0.0652883779887878, equilibrium_temperature=1348.9720119941908, insolation_flux=980.2511242130784),
                             Planet(planet_name='alf 9503 b', host_name='alf 9503', discovery_method='Orbital Brightness Modulation', discovery_year=2023, controversial_flag=True, orbital_period=65.91533264636502, planet_radius=18.89788544575358, planet_mass=3960.119925388, semi_major_radius=126.50379950279408, eccentricity=0.0487553686475379, equilibrium_temperature=916.500579663034, insolation_flux=2021.2216766630156),
                             Planet(planet_name='omi-2235 2', host_name='omi-2235', discovery_method='Imaging', discovery_year=2017, controversial_flag=True, orbital_period=534.2859134751952, planet_radius=13.130606542258828, planet_mass=1163.4699817624955, semi_major_radius=117.30163803399584, eccentricity=0.0456712410806104, equilibrium_temperature=1978.2647027700127, insolation_flux=1607.7151116551686),
                             Planet(planet_name='GJ 7371 b', host_name='GJ 7371', discovery_method='Imaging', discovery_year=2023, controversial_flag=True, orbital_period=130.6620482973673, planet_radius=9.656944739351902, planet_mass=5141.401536349808, semi_major_radius=75.19133692744528, eccentricity=0.0890263820167763, equilibrium_temperature=383.4612317076191, insolation_flux=684.7687190997387),
                             Planet(planet_name='xi-9840 a', host_name='xi-9840', discovery_method='Transit Timing Variations', discovery_year=2019, controversial_flag=True, orbital_period=702.574025459616, planet_radius=3.5068422756292588, planet_mass=3043.1683882103134, semi_major_radius=171.19286305904404, eccentricity=0.0613724265125764, equilibrium_temperature=637.3448278484648, insolation_flux=621.881577647385),
                             Planet(planet_name='tau-8123 2', host_name='tau-8123', discovery_method='Orbital Brightness Modulation', discovery_year=2023, controversial_flag=True, orbital_period=899.7399941955765, planet_radius=18.79938569825832, planet_mass=1669.0026623995425, semi_major_radius=116.73311145245864, eccentricity=0.0276739163523038, equilibrium_temperature=954.0916391584052, insolation_flux=1095.9487408767395),
                             Planet(planet_name='EPIC 1400 2', host_name='EPIC 1400', discovery_method='Imaging', discovery_year=2017, controversial_flag=True, orbital_period=430.38246805572624, planet_radius=13.93485207753687, planet_mass=6455.029682344361, semi_major_radius=202.7287750143928, eccentricity=0.0551853831685026, equilibrium_temperature=2356.878183909529, insolation_flux=1168.06180079948),
                             Planet(planet_name='EPIC-1492 1', host_name='EPIC-1492', discovery_method='Microlensing', discovery_year=2023, controversial_flag=True, orbital_period=574.3775106589467, planet_radius=3.1961106867385736, planet_mass=3165.384442748816, semi_major_radius=42.70229990162578, eccentricity=0.0868256527931799, equilibrium_temperature=611.7668850531954, insolation_flux=2884.8543159628525),
                             Planet(planet_name='EPIC-1492 2', host_name='EPIC-1492', discovery_method='Astrometry', discovery_year=2022, controversial_flag=True, orbital_period=436.06910599030994, planet_radius=12.135928106479998, planet_mass=6412.37272657702, semi_major_radius=134.77715791293252, eccentricity=0.0497383760733471, equilibrium_temperature=1399.218228586043, insolation_flux=449.6969630494452),
                             Planet(planet_name='2MASS-4092 1', host_name='2MASS-4092', discovery_method='Imaging', discovery_year=2021, controversial_flag=True, orbital_period=827.9709168018212, planet_radius=17.14351370525629, planet_mass=8626.005548483332, semi_major_radius=121.47007768064768, eccentricity=0.1117746449150517, equilibrium_temperature=2373.126137802392, insolation_flux=923.6499294424297),
                             Planet(planet_name='gam 470 1', host_name='gam 470', discovery_method='Orbital Brightness Modulation', discovery_year=2014, controversial_flag=True, orbital_period=513.2835861142115, planet_radius=8.997833909741527, planet_mass=7669.412114529723, semi_major_radius=202.67836669566805, eccentricity=0.0227977911973233, equilibrium_temperature=288.21155799018925, insolation_flux=1652.0637193676305),
                             Planet(planet_name='gam 470 2', host_name='gam 470', discovery_method='Imaging', discovery_year=2019, controversial_flag=True, orbital_period=669.5502846471886, planet_radius=23.77843477205859, planet_mass=2521.5496144759486, semi_major_radius=179.91956576211254, eccentricity=0.0725768105960096, equilibrium_temperature=296.274521936063, insolation_flux=406.1622710901736),
                             Planet(planet_name='CoRoT-1518 b', host_name='CoRoT-1518', discovery_method='Imaging', discovery_year=2023, controversial_flag=True, orbital_period=891.8665954525245, planet_radius=9.39946440569694, planet_mass=4894.455738348584, semi_major_radius=56.63062850904917, eccentricity=0.0541411681585838, equilibrium_temperature=1384.8136467858435, insolation_flux=1346.4445654777735),
                             Planet(planet_name='HD-1301 2', host_name='HD-1301', discovery_method='Pulsar Timing', discovery_year=2023, controversial_flag=True, orbital_period=399.5952326146996, planet_radius=11.791511843831517, planet_mass=11096.226402165918, semi_major_radius=81.74428150316102, eccentricity=0.0407843135993462, equilibrium_temperature=624.9102156414965, insolation_flux=581.0050312115264),
                             Planet(planet_name='ups-9395 a', host_name='ups-9395', discovery_method='Imaging', discovery_year=2022, controversial_flag=True, orbital_period=666.0203411908346, planet_radius=19.241272661048143, planet_mass=1694.9382565250153, semi_major_radius=54.50314712201075, eccentricity=0.0647921652609098, equilibrium_temperature=2187.255761440117, insolation_flux=1589.8553030684263),
                             Planet(planet_name='omi-6156 2', host_name='omi-6156', discovery_method='Radial Velocity', discovery_year=2019, controversial_flag=True, orbital_period=34.24990320986376, planet_radius=18.568974737528958, planet_mass=7859.329751273604, semi_major_radius=116.31365904559232, eccentricity=0.0622849304781058, equilibrium_temperature=1807.099080459527, insolation_flux=1484.8089902976776),
                             Planet(planet_name='GJ-19564 b', host_name='GJ-19564', discovery_method='Orbital Brightness Modulation', discovery_year=2023, controversial_flag=True, orbital_period=755.0609677580081, planet_radius=19.79005399256081, planet_mass=1152.7725663873507, semi_major_radius=138.18670873480875, eccentricity=0.02822882714661, equilibrium_temperature=1263.250201534728, insolation_flux=1045.2330586434018),
                             Planet(planet_name='gam1 94 b', host_name='gam1 94', discovery_method='Disk Kinematics', discovery_year=2023, controversial_flag=True, orbital_period=184.90099293093917, planet_radius=13.206168014844517, planet_mass=3593.307593518732, semi_major_radius=146.44769942384875, eccentricity=0.049954726494396, equilibrium_temperature=1228.3520572721686, insolation_flux=1784.5539521026255),
                             Planet(planet_name='Kepler-2661 2', host_name='Kepler-2661', discovery_method='Microlensing', discovery_year=2023, controversial_flag=True, orbital_period=139.9686186278028, planet_radius=14.274895995106544, planet_mass=6164.277153894473, semi_major_radius=180.17108619578045, eccentricity=0.0744708559691216, equilibrium_temperature=1620.6545937863452, insolation_flux=923.3287499849685),
                             Planet(planet_name='ups-6453 1', host_name='ups-6453', discovery_method='Radial Velocity', discovery_year=2017, controversial_flag=True, orbital_period=549.5687176850383, planet_radius=16.852270137075525, planet_mass=5864.238693505662, semi_major_radius=132.18980487628463, eccentricity=0.0612273712661934, equilibrium_temperature=2474.478881498596, insolation_flux=1196.4110410894637),
                             Planet(planet_name='Kepler-2082 a', host_name='Kepler-2082', discovery_method='Radial Velocity', discovery_year=2017, controversial_flag=True, orbital_period=299.4415731825612, planet_radius=13.49518900445613, planet_mass=1771.0114411590607, semi_major_radius=233.15827816053155, eccentricity=0.0107069048900536, equilibrium_temperature=1735.510321013543, insolation_flux=1579.930300095456),
                             Planet(planet_name='ups 2676 1', host_name='ups 2676', discovery_method='Transit Timing Variations', discovery_year=2017, controversial_flag=True, orbital_period=685.2853662957452, planet_radius=3.1583988877280493, planet_mass=5464.877695744167, semi_major_radius=174.197977011622, eccentricity=0.0698849158468202, equilibrium_temperature=716.6587296003786, insolation_flux=1320.6277868995037),
                             Planet(planet_name='gam1-7063 a', host_name='gam1-7063', discovery_method='Imaging', discovery_year=2023, controversial_flag=True, orbital_period=1103.7525757368649, planet_radius=2.4388619004818963, planet_mass=4429.804804942661, semi_major_radius=137.35131631640843, eccentricity=0.0327274060762395, equilibrium_temperature=1371.3097041920566, insolation_flux=1189.272135700512),
                             Planet(planet_name='xi 1613 1', host_name='xi 1613', discovery_method='Microlensing', discovery_year=2023, controversial_flag=True, orbital_period=590.6985164010448, planet_radius=17.696920686558606, planet_mass=416.3445832455464, semi_major_radius=172.59772588683495, eccentricity=0.0506550612840636, equilibrium_temperature=953.9398767180674, insolation_flux=1242.6866032320318),
                             Planet(planet_name='xi 1613 2', host_name='xi 1613', discovery_method='Pulsation Timing Variations', discovery_year=2021, controversial_flag=True, orbital_period=422.7898260703303, planet_radius=22.29945225287025, planet_mass=6897.675364585182, semi_major_radius=155.5648829270326, eccentricity=0.0793910694865878, equilibrium_temperature=855.0669532269586, insolation_flux=1601.7821661002424),
                             Planet(planet_name='Kepler 6620 a', host_name='Kepler 6620', discovery_method='Pulsar Timing', discovery_year=2019, controversial_flag=True, orbital_period=399.3808805545332, planet_radius=6.810644095192873, planet_mass=4656.976237787623, semi_major_radius=147.8673503945652, eccentricity=0.016694616384724, equilibrium_temperature=908.7546202806636, insolation_flux=1438.3000363746512),
                             Planet(planet_name='Kepler 6620 b', host_name='Kepler 6620', discovery_method='Pulsation Timing Variations', discovery_year=2023, controversial_flag=True, orbital_period=388.0885118823048, planet_radius=19.270033718965173, planet_mass=3157.792271410717, semi_major_radius=98.35699204436658, eccentricity=0.0478983759371212, equilibrium_temperature=229.70323167212743, insolation_flux=312.0623649393748),
                             Planet(planet_name='nu-1368 2', host_name='nu-1368', discovery_method='Radial Velocity', discovery_year=2023, controversial_flag=True, orbital_period=699.1831164557481, planet_radius=6.405198910727713, planet_mass=6723.353072772195, semi_major_radius=98.61229943706736, eccentricity=0.0799738416435704, equilibrium_temperature=648.8521841392363, insolation_flux=1978.14128277683),
                             Planet(planet_name='tau 9525 a', host_name='tau 9525', discovery_method='Eclipse Timing Variations', discovery_year=2021, controversial_flag=True, orbital_period=719.0826412493512, planet_radius=4.512859361192705, planet_mass=8988.976779537392, semi_major_radius=84.18458672157716, eccentricity=0.0262978847220934, equilibrium_temperature=699.0301197469837, insolation_flux=1143.0055099948345),
                             Planet(planet_name='tau 9525 b', host_name='tau 9525', discovery_method='Eclipse Timing Variations', discovery_year=2019, controversial_flag=True, orbital_period=285.958987915776, planet_radius=15.158418264577318, planet_mass=3309.9695263091603, semi_major_radius=11.497347345841575, eccentricity=0.0149444492016083, equilibrium_temperature=1254.115887109, insolation_flux=1617.96751388229),
                             Planet(planet_name='rho-8179 1', host_name='rho-8179', discovery_method='Radial Velocity', discovery_year=2017, controversial_flag=True, orbital_period=650.7843505545331, planet_radius=7.772912111593628, planet_mass=5267.488358025193, semi_major_radius=61.98934827905171, eccentricity=0.0566828960425779, equilibrium_temperature=1699.1697691651823, insolation_flux=311.7792522824212),
                             Planet(planet_name='GJ-8145 a', host_name='GJ-8145', discovery_method='Orbital Brightness Modulation', discovery_year=2018, controversial_flag=True, orbital_period=841.752705497012, planet_radius=7.410155331537192, planet_mass=1623.883917078878, semi_major_radius=114.62824412913714, eccentricity=0.0125406857124426, equilibrium_temperature=1467.7273941215574, insolation_flux=2306.3147373162965),
                             Planet(planet_name='psi1 93 2', host_name='psi1 93', discovery_method='Transit', discovery_year=2022, controversial_flag=True, orbital_period=810.934461351788, planet_radius=22.73269813001134, planet_mass=3401.8641331508734, semi_major_radius=86.14948533114948, eccentricity=0.0498959514186711, equilibrium_temperature=1874.0365866275797, insolation_flux=985.679941513162),
                             Planet(planet_name='GJ 9947 1', host_name='GJ 9947', discovery_method='Microlensing', discovery_year=2023, controversial_flag=True, orbital_period=460.5704129243125, planet_radius=6.199465982357312, planet_mass=5925.215569978876, semi_major_radius=18.43557394030728, eccentricity=0.0559156401464064, equilibrium_temperature=275.7792855968256, insolation_flux=1130.534829219297),
                             Planet(planet_name='GJ 9947 2', host_name='GJ 9947', discovery_method='Microlensing', discovery_year=2021, controversial_flag=True, orbital_period=639.3091590248063, planet_radius=12.760220650233595, planet_mass=646.9535688233882, semi_major_radius=160.91599107564622, eccentricity=0.0783054056705606, equilibrium_temperature=1411.0991201428506, insolation_flux=1031.901824103596),
                             Planet(planet_name='BD 649 1', host_name='BD 649', discovery_method='Imaging', discovery_year=2020, controversial_flag=True, orbital_period=292.8325544264078, planet_radius=13.17319562856703, planet_mass=4746.886354583631, semi_major_radius=118.64858426959456, eccentricity=0.0544390817822153, equilibrium_temperature=1990.4975095323248, insolation_flux=879.8837733376595),
                             Planet(planet_name='EPIC 1818 2', host_name='EPIC 1818', discovery_method='Radial Velocity', discovery_year=2018, controversial_flag=True, orbital_period=107.54374736455418, planet_radius=11.487377355093866, planet_mass=7093.391069290345, semi_major_radius=196.6085714138032, eccentricity=0.0508621773766059, equilibrium_temperature=1171.0878489405095, insolation_flux=855.2913457530749),
                             Planet(planet_name='omi 7141 2', host_name='omi 7141', discovery_method='Pulsar Timing', discovery_year=2017, controversial_flag=True, orbital_period=947.0995026040064, planet_radius=10.56710872595932, planet_mass=6537.324494888803, semi_major_radius=30.18827816775476, eccentricity=0.0405925987677795, equilibrium_temperature=2585.718434629672, insolation_flux=531.7943344472591),
                             Planet(planet_name='mu2 6219 1', host_name='mu2 6219', discovery_method='Imaging', discovery_year=2018, controversial_flag=True, orbital_period=621.1339950206986, planet_radius=8.984594612113822, planet_mass=1015.2615271305008, semi_major_radius=44.35665614781221, eccentricity=0.0454272172245757, equilibrium_temperature=899.0997730145419, insolation_flux=1536.6390163490578),
                             Planet(planet_name='mu2 6219 2', host_name='mu2 6219', discovery_method='Transit Timing Variations', discovery_year=2019, controversial_flag=True, orbital_period=1126.7761050162896, planet_radius=10.968413114573996, planet_mass=12485.615843444544, semi_major_radius=63.82647715838174, eccentricity=0.0745406121485786, equilibrium_temperature=758.6765850487257, insolation_flux=1485.434606661273),
                             Planet(planet_name='iot-4040 a', host_name='iot-4040', discovery_method='Radial Velocity', discovery_year=2020, controversial_flag=True, orbital_period=240.00574338527971, planet_radius=6.331825635883281, planet_mass=964.0637002662124, semi_major_radius=63.0588655194425, eccentricity=0.0874041627593733, equilibrium_temperature=1561.03735642358, insolation_flux=1077.658448250407),
                             Planet(planet_name='BD 9947 2', host_name='BD 9947', discovery_method='Eclipse Timing Variations', discovery_year=2021, controversial_flag=True, orbital_period=194.5375024928404, planet_radius=14.035385158557537, planet_mass=5069.607555504976, semi_major_radius=134.25416734361534, eccentricity=0.0005604734650266, equilibrium_temperature=543.2692014599041, insolation_flux=1150.1841111659069),
                             Planet(planet_name='eps 7990 2', host_name='eps 7990', discovery_method='Microlensing', discovery_year=2021, controversial_flag=True, orbital_period=383.72454131032, planet_radius=2.691369762484612, planet_mass=6493.626550734402, semi_major_radius=48.65091548603672, eccentricity=0.0402137367596144, equilibrium_temperature=1117.897300779709, insolation_flux=1151.758369076045),
                             Planet(planet_name='DP 855 a', host_name='DP 855', discovery_method='Radial Velocity', discovery_year=2023, controversial_flag=True, orbital_period=532.8816910969331, planet_radius=16.946764114730833, planet_mass=2411.429307535768, semi_major_radius=145.51148669666082, eccentricity=0.0299645491558766, equilibrium_temperature=1552.1238503307177, insolation_flux=954.0843931972332),
                             Planet(planet_name='iot 1700 b', host_name='iot 1700', discovery_method='Microlensing', discovery_year=2023, controversial_flag=True, orbital_period=440.2181109892039, planet_radius=22.881952953146367, planet_mass=3221.5481426968213, semi_major_radius=46.25755612481701, eccentricity=0.0582691098583152, equilibrium_temperature=2227.1141745329182, insolation_flux=854.081186918448),
                             Planet(planet_name='WASP-3410 1', host_name='WASP-3410', discovery_method='Disk Kinematics', discovery_year=2017, controversial_flag=True, orbital_period=877.6769127075083, planet_radius=14.776930180605106, planet_mass=1416.3561934842592, semi_major_radius=129.69810689995336, eccentricity=0.061711586233162, equilibrium_temperature=1445.436311551127, insolation_flux=1182.6740066083214),
                             Planet(planet_name='xi 5716 a', host_name='xi 5716', discovery_method='Astrometry', discovery_year=2023, controversial_flag=True, orbital_period=538.2278573827217, planet_radius=11.651842728368004, planet_mass=8219.722452331605, semi_major_radius=98.80329683515782, eccentricity=0.091478524300532, equilibrium_temperature=934.0413902335796, insolation_flux=1088.2467457466848),
                             Planet(planet_name='mu 9791 2', host_name='mu 9791', discovery_method='Transit Timing Variations', discovery_year=2023, controversial_flag=True, orbital_period=461.4553588528103, planet_radius=14.989457099587964, planet_mass=10219.738689538775, semi_major_radius=90.10759565286185, eccentricity=0.0086463474577964, equilibrium_temperature=948.5086498820884, insolation_flux=551.4393727750536),
                             Planet(planet_name='bet 9929 b', host_name='bet 9929', discovery_method='Radial Velocity', discovery_year=2023, controversial_flag=True, orbital_period=603.5138872466497, planet_radius=8.771044679445419, planet_mass=5202.408286180511, semi_major_radius=119.11707124030644, eccentricity=0.007295490597205, equilibrium_temperature=1820.4811575808333, insolation_flux=615.8395230928363),
                             Planet(planet_name='gam1-8132 2', host_name='gam1-8132', discovery_method='Microlensing', discovery_year=2023, controversial_flag=True, orbital_period=456.5764863316796, planet_radius=8.466389563385135, planet_mass=6370.961636340817, semi_major_radius=133.5115779554065, eccentricity=0.0695929572163784, equilibrium_temperature=783.6423863575387, insolation_flux=1390.490563934304),
                             Planet(planet_name='GJ-3275 1', host_name='GJ-3275', discovery_method='Pulsation Timing Variations', discovery_year=2019, controversial_flag=True, orbital_period=765.3444024783221, planet_radius=7.183080191272559, planet_mass=12230.351581125748, semi_major_radius=112.68065551091792, eccentricity=0.0431574885743038, equilibrium_temperature=405.293094185399, insolation_flux=2417.7357847558123),
                             Planet(planet_name='GJ-3275 2', host_name='GJ-3275', discovery_method='Orbital Brightness Modulation', discovery_year=2020, controversial_flag=True, orbital_period=619.2098689951782, planet_radius=20.65879995251212, planet_mass=6105.735665328119, semi_major_radius=17.830836430824363, eccentricity=0.040260785455785, equilibrium_temperature=1118.8501471171164, insolation_flux=524.7127258006997),
                             Planet(planet_name='xi 3805 b', host_name='xi 3805', discovery_method='Imaging', discovery_year=2017, controversial_flag=True, orbital_period=800.1278412227718, planet_radius=3.0996110826969776, planet_mass=7981.2993427730435, semi_major_radius=126.94061865105724, eccentricity=0.0915904904660213, equilibrium_temperature=214.5747406268689, insolation_flux=1869.7831908048397),
                             Planet(planet_name='bet 7572 2', host_name='bet 7572', discovery_method='Microlensing', discovery_year=2023, controversial_flag=True, orbital_period=524.3001205952747, planet_radius=12.31220433501127, planet_mass=10934.227821745071, semi_major_radius=77.1559190294339, eccentricity=0.0520932729952509, equilibrium_temperature=943.1042886094224, insolation_flux=528.8426718853747),
                             Planet(planet_name='DP-7990 a', host_name='DP-7990', discovery_method='Transit Timing Variations', discovery_year=2015, controversial_flag=True, orbital_period=683.3731353653084, planet_radius=7.88538547250203, planet_mass=7416.200460083237, semi_major_radius=103.46899798469424, eccentricity=0.0583730511117825, equilibrium_temperature=1232.307851779981, insolation_flux=1800.1972359479428),
                             Planet(planet_name='psi1-14574 a', host_name='psi1-14574', discovery_method='Disk Kinematics', discovery_year=2023, controversial_flag=True, orbital_period=572.3889157579239, planet_radius=5.603304791772561, planet_mass=9044.574763029896, semi_major_radius=173.31245807369285, eccentricity=0.0789335116062674, equilibrium_temperature=67.94452240491569, insolation_flux=1213.1261201488694),
                             Planet(planet_name='BD 53 2', host_name='BD 53', discovery_method='Pulsation Timing Variations', discovery_year=2023, controversial_flag=True, orbital_period=244.8543208947436, planet_radius=10.64485077776698, planet_mass=4197.210612756095, semi_major_radius=131.31541736861607, eccentricity=0.0351070243072743, equilibrium_temperature=1200.1037649636864, insolation_flux=1624.898817456673),
                             Planet(planet_name='nu 4829 2', host_name='nu 4829', discovery_method='Pulsar Timing', discovery_year=2016, controversial_flag=True, orbital_period=844.8288686583917, planet_radius=13.41051514687572, planet_mass=3591.538349944288, semi_major_radius=98.30368628350192, eccentricity=0.0611199175622525, equilibrium_temperature=727.4284651822998, insolation_flux=1752.8704552431725),
                             Planet(planet_name='mu 7510 1', host_name='mu 7510', discovery_method='Orbital Brightness Modulation', discovery_year=2023, controversial_flag=True, orbital_period=563.7313912537255, planet_radius=14.133921425948262, planet_mass=3491.349516434036, semi_major_radius=148.7707223693706, eccentricity=0.0257503100903949, equilibrium_temperature=1533.0829009350814, insolation_flux=1701.4836991658383),
                             Planet(planet_name='GJ-4081 b', host_name='GJ-4081', discovery_method='Orbital Brightness Modulation', discovery_year=2020, controversial_flag=True, orbital_period=467.3819535052282, planet_radius=15.77302575984614, planet_mass=2413.0569270916294, semi_major_radius=48.74976652911237, eccentricity=0.0546897067065043, equilibrium_temperature=1387.3055519747063, insolation_flux=1567.3337468511138),
                             Planet(planet_name='kap-4867 b', host_name='kap-4867', discovery_method='Transit', discovery_year=2017, controversial_flag=True, orbital_period=148.40825818146874, planet_radius=0.4363211116211758, planet_mass=6944.649066463478, semi_major_radius=29.37741790333065, eccentricity=0.0416726732019708, equilibrium_temperature=1095.8080312084578, insolation_flux=2235.0522479098654),
                             Planet(planet_name='xi 145 a', host_name='xi 145', discovery_method='Pulsar Timing', discovery_year=2016, controversial_flag=True, orbital_period=108.03067321408037, planet_radius=18.57818486768784, planet_mass=5761.866692031548, semi_major_radius=166.44473443767006, eccentricity=0.0579938573865091, equilibrium_temperature=1811.0101950102776, insolation_flux=2623.4376642026027),
                             Planet(planet_name='xi 145 b', host_name='xi 145', discovery_method='Pulsar Timing', discovery_year=2018, controversial_flag=True, orbital_period=500.6169651818873, planet_radius=12.009730251478794, planet_mass=6757.887490449615, semi_major_radius=42.18350146085439, eccentricity=0.0175322595430201, equilibrium_temperature=1341.3272812921275, insolation_flux=1238.64969263904),
                             Planet(planet_name='WASP-3090 2', host_name='WASP-3090', discovery_method='Imaging', discovery_year=2019, controversial_flag=True, orbital_period=430.8673819548943, planet_radius=13.921522760043596, planet_mass=8042.117291516957, semi_major_radius=110.76454970526248, eccentricity=0.0037686022019867, equilibrium_temperature=1430.2406686597787, insolation_flux=663.4083725538112),
                             Planet(planet_name='CoRoT 5213 2', host_name='CoRoT 5213', discovery_method='Eclipse Timing Variations', discovery_year=2018, controversial_flag=True, orbital_period=597.5303991202139, planet_radius=18.913657932871548, planet_mass=1966.4057720283745, semi_major_radius=52.33453384813964, eccentricity=0.0708988678634875, equilibrium_temperature=1971.9697043915592, insolation_flux=595.9777384636897),
                             Planet(planet_name='alf-5 2', host_name='alf-5', discovery_method='Transit Timing Variations', discovery_year=2017, controversial_flag=True, orbital_period=289.4215450732221, planet_radius=2.708072388341403, planet_mass=3305.299811664144, semi_major_radius=88.05852143998028, eccentricity=0.0399156370887728, equilibrium_temperature=1573.8951318723311, insolation_flux=1378.59949359174),
                             Planet(planet_name='ups-2665 a', host_name='ups-2665', discovery_method='Orbital Brightness Modulation', discovery_year=2017, controversial_flag=True, orbital_period=1042.94101735199, planet_radius=16.604206510724566, planet_mass=392.1518286543897, semi_major_radius=61.09996026902411, eccentricity=0.0263671925351825, equilibrium_temperature=1622.4952959696095, insolation_flux=2001.2374192713205),
                             Planet(planet_name='ups-2665 b', host_name='ups-2665', discovery_method='Eclipse Timing Variations', discovery_year=2015, controversial_flag=True, orbital_period=542.2297606597351, planet_radius=13.56361734231081, planet_mass=11413.890737641148, semi_major_radius=219.22263756082225, eccentricity=0.0522871115724791, equilibrium_temperature=1160.717469610115, insolation_flux=1377.5047619446866),
                             Planet(planet_name='DP-56169 b', host_name='DP-56169', discovery_method='Astrometry', discovery_year=2023, controversial_flag=True, orbital_period=574.4834350713364, planet_radius=7.399329403415587, planet_mass=8259.105793127084, semi_major_radius=78.92346347951568, eccentricity=0.0731683948682192, equilibrium_temperature=1053.8840283250272, insolation_flux=1857.0055717950377),
                             Planet(planet_name='TOI-7812 a', host_name='TOI-7812', discovery_method='Pulsar Timing', discovery_year=2019, controversial_flag=True, orbital_period=698.2560315747221, planet_radius=6.610615199979396, planet_mass=7653.982470938361, semi_major_radius=150.50513418384506, eccentricity=0.0364227005819452, equilibrium_temperature=918.1994364614244, insolation_flux=804.4781626933155),
                             Planet(planet_name='TOI-7812 b', host_name='TOI-7812', discovery_method='Astrometry', discovery_year=2017, controversial_flag=True, orbital_period=1015.7624979741222, planet_radius=20.013092944506845, planet_mass=4124.717412291877, semi_major_radius=55.879578535553655, eccentricity=0.0849120295023633, equilibrium_temperature=214.2012159691452, insolation_flux=2115.38275685506),
                             Planet(planet_name='mu-89 a', host_name='mu-89', discovery_method='Orbital Brightness Modulation', discovery_year=2016, controversial_flag=True, orbital_period=832.8230148737384, planet_radius=15.114390491860991, planet_mass=5230.756528196584, semi_major_radius=77.9036097967117, eccentricity=0.0323938432248858, equilibrium_temperature=241.69245014578428, insolation_flux=988.093681496312),
                             Planet(planet_name='mu2-3006 a', host_name='mu2-3006', discovery_method='Orbital Brightness Modulation', discovery_year=2016, controversial_flag=True, orbital_period=377.9470711531712, planet_radius=7.267507370040548, planet_mass=2500.862635026598, semi_major_radius=93.0989580383549, eccentricity=0.0488228052608263, equilibrium_temperature=2302.6077493763087, insolation_flux=614.847179331236),
                             Planet(planet_name='ups-3899 2', host_name='ups-3899', discovery_method='Transit', discovery_year=2017, controversial_flag=True, orbital_period=610.4815790307663, planet_radius=16.1633553005203, planet_mass=2406.16000098537, semi_major_radius=126.74984226573844, eccentricity=0.0690005877581027, equilibrium_temperature=1204.725514390575, insolation_flux=770.1116267457608),
                             Planet(planet_name='kap-4594 2', host_name='kap-4594', discovery_method='Transit', discovery_year=2018, controversial_flag=True, orbital_period=274.9271995321943, planet_radius=1.4004877633510198, planet_mass=2460.049458452169, semi_major_radius=83.12341274120503, eccentricity=0.0788626274902119, equilibrium_temperature=667.4137137603823, insolation_flux=2132.5771404145207)],
                     'q15': [Planet(planet_name='omi-4482 d', host_name='omi-4482', discovery_method='Eclipse Timing Variations', discovery_year=2023, controversial_flag=False, orbital_period=632.0123253179738, planet_radius=8.804081419698047, planet_mass=2414.490365078466, semi_major_radius=132.02985374562044, eccentricity=0.0533341440131968, equilibrium_temperature=754.1960850852975, insolation_flux=763.0501446843258),
                             Planet(planet_name='alf-8432 1', host_name='alf-8432', discovery_method='Pulsar Timing', discovery_year=2023, controversial_flag=False, orbital_period=30.118770264502302, planet_radius=17.77912680646989, planet_mass=4502.866171523835, semi_major_radius=112.25079136013773, eccentricity=0.1253763789148612, equilibrium_temperature=930.5876491564754, insolation_flux=1922.8395191281345),
                             Planet(planet_name='alf-8432 2', host_name='alf-8432', discovery_method='Disk Kinematics', discovery_year=2016, controversial_flag=False, orbital_period=541.460041515413, planet_radius=2.430586916762669, planet_mass=9537.235886258137, semi_major_radius=124.37692470295956, eccentricity=0.0307638050158221, equilibrium_temperature=984.6077079119312, insolation_flux=1782.6219563433674),
                             Planet(planet_name='alf-8432 3', host_name='alf-8432', discovery_method='Pulsar Timing', discovery_year=2021, controversial_flag=True, orbital_period=730.1423570455273, planet_radius=16.105537617506368, planet_mass=1849.2071817382807, semi_major_radius=96.29997261140409, eccentricity=0.0051288737815215, equilibrium_temperature=1098.2065334897695, insolation_flux=902.4309617147794),
                             Planet(planet_name='alf-8432 4', host_name='alf-8432', discovery_method='Microlensing', discovery_year=2023, controversial_flag=False, orbital_period=565.0920691556591, planet_radius=4.674670290055033, planet_mass=10641.932743505136, semi_major_radius=134.99608350590069, eccentricity=0.0233318487486392, equilibrium_temperature=1063.6340462818157, insolation_flux=1943.967268287064)],
                     'q16': [],
                     'q17': 665}
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
