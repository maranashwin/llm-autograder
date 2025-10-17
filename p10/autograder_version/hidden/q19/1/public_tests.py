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
                     'q5': Star(spectral_type='L3VI', stellar_effective_temperature=4460.587052778466, stellar_radius=10.01, stellar_mass=4.878144562249236, stellar_luminosity=-1.4618566005250409, stellar_surface_gravity=2.7647967176611776, stellar_age=8.827165496273425),
                     'q6': Star(spectral_type='A0.5', stellar_effective_temperature=4702.958767836078, stellar_radius=42.594992808507165, stellar_mass=3.16234021399535, stellar_luminosity=-1.1313397833789274, stellar_surface_gravity=2.1096076410310305, stellar_age=1.8142509703521796),
                     'q7': -0.22152502538695046,
                     'q8': 7.309081656460567,
                     'q9': 5106.700368162256,
                     'q10': 'nu-3403',
                     'q11': 7.42846161824086,
                     'Planet': Planet(planet_name='Jupiter', host_name='Sun', discovery_method='Imaging', discovery_year=1610, controversial_flag=False, orbital_period=4333.0, planet_radius=11.209, planet_mass=317.828, semi_major_radius=5.2038, eccentricity=0.0489, equilibrium_temperature=110, insolation_flux=0.0345),
                     'q12': Planet(planet_name='alf 5259 a', host_name='alf 5259', discovery_method='Pulsation Timing Variations', discovery_year=2015, controversial_flag=False, orbital_period=677.4746434120955, planet_radius=11.441783963425635, planet_mass=9168.781293777733, semi_major_radius=107.58367400861007, eccentricity=0.0485877925302147, equilibrium_temperature=1086.7639924865082, insolation_flux=1457.967881866727),
                     'q13': [Planet(planet_name='alf-5592 a', host_name='alf-5592', discovery_method='Eclipse Timing Variations', discovery_year=2017, controversial_flag=False, orbital_period=498.4048825336154, planet_radius=3.156737277562639, planet_mass=2874.428966366696, semi_major_radius=94.568292639399, eccentricity=0.0677773272576702, equilibrium_temperature=895.2382886379908, insolation_flux=548.6471346434136),
                             Planet(planet_name='DP 7443 a', host_name='DP 7443', discovery_method='Orbital Brightness Modulation', discovery_year=2021, controversial_flag=False, orbital_period=481.19429660819713, planet_radius=6.978231227862279, planet_mass=5053.417346211012, semi_major_radius=138.28420141023273, eccentricity=0.1160756880075092, equilibrium_temperature=1964.0954962292064, insolation_flux=560.3918365827138),
                             Planet(planet_name='gam-487 a', host_name='gam-487', discovery_method='Transit', discovery_year=2017, controversial_flag=False, orbital_period=623.2591330593734, planet_radius=100000.0, planet_mass=5091.0406031317725, semi_major_radius=57.12287164193447, eccentricity=0.020059841268165, equilibrium_temperature=1444.323467267234, insolation_flux=414.07495927203183),
                             Planet(planet_name='Kepler 359 1', host_name='Kepler 359', discovery_method='Microlensing', discovery_year=2015, controversial_flag=False, orbital_period=324.37499558245406, planet_radius=100000.0, planet_mass=4586.929712215415, semi_major_radius=120.86219599771628, eccentricity=0.008868784073478, equilibrium_temperature=1637.983460898768, insolation_flux=1611.4344219794823),
                             Planet(planet_name='2MASS-5173 1', host_name='2MASS-5173', discovery_method='Orbital Brightness Modulation', discovery_year=2014, controversial_flag=False, orbital_period=670.269605785736, planet_radius=9.925666393998688, planet_mass=6127.980197711554, semi_major_radius=54.20429049985852, eccentricity=0.0496083677808065, equilibrium_temperature=241.44606719131968, insolation_flux=1214.2241071430287)],
                     'q14': [Planet(planet_name='alf 1235 1', host_name='alf 1235', discovery_method='Microlensing', discovery_year=2019, controversial_flag=True, orbital_period=107.49631700281634, planet_radius=15.232539842265728, planet_mass=3532.381417427041, semi_major_radius=34.339558400456994, eccentricity=0.0550623779546851, equilibrium_temperature=821.3684875739925, insolation_flux=799.622731375886),
                             Planet(planet_name='gam-19 b', host_name='gam-19', discovery_method='Eclipse Timing Variations', discovery_year=2020, controversial_flag=True, orbital_period=597.8513268255659, planet_radius=10.54229820026904, planet_mass=9446.387421359632, semi_major_radius=99.34442627279084, eccentricity=0.0397702200673998, equilibrium_temperature=1086.4480437274792, insolation_flux=1617.8094734663189),
                             Planet(planet_name='ups-45062 a', host_name='ups-45062', discovery_method='Eclipse Timing Variations', discovery_year=2015, controversial_flag=True, orbital_period=309.48027498009344, planet_radius=100000.0, planet_mass=1638.739941127681, semi_major_radius=75.56703333403469, eccentricity=0.0103284422843668, equilibrium_temperature=1355.048287584283, insolation_flux=1225.296782720405),
                             Planet(planet_name='CoRoT-1560 b', host_name='CoRoT-1560', discovery_method='Pulsar Timing', discovery_year=2021, controversial_flag=True, orbital_period=302.61871773220923, planet_radius=100000.0, planet_mass=3826.199575906592, semi_major_radius=135.31334906086826, eccentricity=0.0062384945049828, equilibrium_temperature=837.5775935770897, insolation_flux=2021.26579054316),
                             Planet(planet_name='TOI-459 a', host_name='TOI-459', discovery_method='Pulsation Timing Variations', discovery_year=2021, controversial_flag=True, orbital_period=889.3776359420868, planet_radius=100000.0, planet_mass=8119.173697624903, semi_major_radius=136.9637044668101, eccentricity=0.0907743216482106, equilibrium_temperature=1248.750632806787, insolation_flux=1848.260391214054),
                             Planet(planet_name='HD-5564 b', host_name='HD-5564', discovery_method='Orbital Brightness Modulation', discovery_year=2015, controversial_flag=True, orbital_period=739.4696509031461, planet_radius=6.614691539060774, planet_mass=657.9401150406011, semi_major_radius=19.917183943312352, eccentricity=0.0215268865284297, equilibrium_temperature=324.4749917697053, insolation_flux=857.3592731172247),
                             Planet(planet_name='BD-9135 1', host_name='BD-9135', discovery_method='Pulsar Timing', discovery_year=2022, controversial_flag=True, orbital_period=375.65862364245226, planet_radius=18.521172831802573, planet_mass=1983.3605562763223, semi_major_radius=63.46849053815099, eccentricity=0.022802897494455, equilibrium_temperature=1270.3587816284075, insolation_flux=1951.7570321924327),
                             Planet(planet_name='BD-9135 2', host_name='BD-9135', discovery_method='Microlensing', discovery_year=2017, controversial_flag=True, orbital_period=574.6420458752012, planet_radius=9.639471847403684, planet_mass=4961.694681342752, semi_major_radius=52.185077177710106, eccentricity=0.0090001289898809, equilibrium_temperature=715.0245647943693, insolation_flux=1136.3806791060113),
                             Planet(planet_name='DP 5464 1', host_name='DP 5464', discovery_method='Transit Timing Variations', discovery_year=2017, controversial_flag=True, orbital_period=316.27554990148747, planet_radius=12.912541539942968, planet_mass=6244.706878651453, semi_major_radius=65.84447620612471, eccentricity=0.0654670799792741, equilibrium_temperature=863.1817704842697, insolation_flux=1451.8353894040963),
                             Planet(planet_name='mu2 523 a', host_name='mu2 523', discovery_method='Radial Velocity', discovery_year=2018, controversial_flag=True, orbital_period=333.7371676588997, planet_radius=7.64237215240451, planet_mass=4942.74275416105, semi_major_radius=99.22024595626092, eccentricity=0.0784679019074525, equilibrium_temperature=1442.5334749737774, insolation_flux=236.59738662873255),
                             Planet(planet_name='EPIC-8929 2', host_name='EPIC-8929', discovery_method='Eclipse Timing Variations', discovery_year=2018, controversial_flag=True, orbital_period=673.4938194430256, planet_radius=14.44731248882444, planet_mass=5541.173119171413, semi_major_radius=114.14842801010478, eccentricity=0.050521330606937, equilibrium_temperature=2339.5101827157014, insolation_flux=1551.9706730821397),
                             Planet(planet_name='psi1 1193 a', host_name='psi1 1193', discovery_method='Orbital Brightness Modulation', discovery_year=2018, controversial_flag=True, orbital_period=573.5200149667711, planet_radius=100000.0, planet_mass=9149.15231287617, semi_major_radius=70.88212539228945, eccentricity=0.0753846107892924, equilibrium_temperature=1020.4072283542804, insolation_flux=1244.6473604965397),
                             Planet(planet_name='EPIC-6650 b', host_name='EPIC-6650', discovery_method='Transit', discovery_year=2018, controversial_flag=True, orbital_period=338.2821400441572, planet_radius=12.949453355277546, planet_mass=5187.604353402954, semi_major_radius=146.3156340371953, eccentricity=0.0680135263026532, equilibrium_temperature=1731.9152442580648, insolation_flux=576.6230192172926),
                             Planet(planet_name='Kepler-3697 1', host_name='Kepler-3697', discovery_method='Pulsar Timing', discovery_year=2017, controversial_flag=True, orbital_period=532.9243626716932, planet_radius=9.28669890583937, planet_mass=1493.0779286562706, semi_major_radius=131.17620180105774, eccentricity=0.0483153164692716, equilibrium_temperature=1066.3818441043545, insolation_flux=1318.6888334686448),
                             Planet(planet_name='ome-8079 2', host_name='ome-8079', discovery_method='Orbital Brightness Modulation', discovery_year=2018, controversial_flag=True, orbital_period=374.9923737383749, planet_radius=7.385743708205783, planet_mass=8196.267320928464, semi_major_radius=203.7756066259456, eccentricity=0.0738419912659578, equilibrium_temperature=874.6578303383461, insolation_flux=1125.4164052688434),
                             Planet(planet_name='psi1 6342 1', host_name='psi1 6342', discovery_method='Imaging', discovery_year=2018, controversial_flag=True, orbital_period=770.2702040785423, planet_radius=3.63113368826134, planet_mass=4126.641691052049, semi_major_radius=87.75754905820779, eccentricity=0.0939833047387783, equilibrium_temperature=532.5200324523643, insolation_flux=14.742419053328376),
                             Planet(planet_name='xi-3364 1', host_name='xi-3364', discovery_method='Disk Kinematics', discovery_year=2012, controversial_flag=True, orbital_period=408.8530085311304, planet_radius=14.88993259229499, planet_mass=5895.951889830085, semi_major_radius=2.602343922757697, eccentricity=0.0623120376781385, equilibrium_temperature=2433.521762937285, insolation_flux=416.5026752646769),
                             Planet(planet_name='xi-7639 b', host_name='xi-7639', discovery_method='Pulsation Timing Variations', discovery_year=2013, controversial_flag=True, orbital_period=565.1474787178762, planet_radius=11.601566047695528, planet_mass=7827.861001175406, semi_major_radius=13.242582347474112, eccentricity=0.0703000933402372, equilibrium_temperature=776.6361735118676, insolation_flux=1460.3882804527111),
                             Planet(planet_name='HD 7031 b', host_name='HD 7031', discovery_method='Radial Velocity', discovery_year=2018, controversial_flag=True, orbital_period=475.6612544354094, planet_radius=17.85631184584752, planet_mass=7992.761361069464, semi_major_radius=83.0228508421182, eccentricity=0.0392317573815312, equilibrium_temperature=1245.0344069908488, insolation_flux=989.8869195766048),
                             Planet(planet_name='2MASS 8792 1', host_name='2MASS 8792', discovery_method='Pulsation Timing Variations', discovery_year=2018, controversial_flag=True, orbital_period=218.97062717936865, planet_radius=10.302413398342392, planet_mass=8874.837129397256, semi_major_radius=54.24005587704745, eccentricity=0.0491213364234196, equilibrium_temperature=2422.628260491885, insolation_flux=881.7926853235149),
                             Planet(planet_name='2MASS 8792 2', host_name='2MASS 8792', discovery_method='Eclipse Timing Variations', discovery_year=2018, controversial_flag=True, orbital_period=407.7300036732181, planet_radius=15.01033221306766, planet_mass=7602.060979866143, semi_major_radius=147.97667065636898, eccentricity=0.0954456719883571, equilibrium_temperature=1486.820039667457, insolation_flux=1137.932661522692),
                             Planet(planet_name='gam1 7321 a', host_name='gam1 7321', discovery_method='Microlensing', discovery_year=2016, controversial_flag=True, orbital_period=532.8236681992207, planet_radius=21.03251491746387, planet_mass=2914.5909467840484, semi_major_radius=116.85815965361432, eccentricity=0.0186645522765532, equilibrium_temperature=1181.95637860784, insolation_flux=807.1059143807911),
                             Planet(planet_name='rho-8365 b', host_name='rho-8365', discovery_method='Transit', discovery_year=2019, controversial_flag=True, orbital_period=247.92499938715167, planet_radius=15.285484950441983, planet_mass=7340.882643706313, semi_major_radius=52.15238285324721, eccentricity=0.0322741579924952, equilibrium_temperature=1844.517540488744, insolation_flux=1097.392723332007),
                             Planet(planet_name='ups-8878 b', host_name='ups-8878', discovery_method='Imaging', discovery_year=2019, controversial_flag=True, orbital_period=263.3850495125484, planet_radius=2.8509216493832845, planet_mass=4215.5441214418925, semi_major_radius=42.81123435137994, eccentricity=0.0380271057332342, equilibrium_temperature=356.41805278054994, insolation_flux=1127.4969586321083),
                             Planet(planet_name='ome 5757 a', host_name='ome 5757', discovery_method='Orbital Brightness Modulation', discovery_year=2022, controversial_flag=True, orbital_period=133.09607612698608, planet_radius=10.336834299797593, planet_mass=6135.526972099412, semi_major_radius=68.36678329751524, eccentricity=0.0545169919706798, equilibrium_temperature=1519.6874448434487, insolation_flux=1172.4760837284502),
                             Planet(planet_name='nu-47 2', host_name='nu-47', discovery_method='Disk Kinematics', discovery_year=2019, controversial_flag=True, orbital_period=639.5643562858296, planet_radius=1.8250422413843503, planet_mass=8561.867113831928, semi_major_radius=120.81437344951892, eccentricity=0.0625583169887777, equilibrium_temperature=1395.46577822496, insolation_flux=1366.4907665066792),
                             Planet(planet_name='omi-3224 b', host_name='omi-3224', discovery_method='Radial Velocity', discovery_year=2021, controversial_flag=True, orbital_period=675.1037617876203, planet_radius=11.821799142483767, planet_mass=8357.953408106327, semi_major_radius=70.45550824548178, eccentricity=0.0305226854030478, equilibrium_temperature=1758.9586738563926, insolation_flux=1032.124991396061),
                             Planet(planet_name='CoRoT 325 a', host_name='CoRoT 325', discovery_method='Eclipse Timing Variations', discovery_year=2021, controversial_flag=True, orbital_period=944.7142911424314, planet_radius=29.062802832493915, planet_mass=6037.370999926334, semi_major_radius=159.71854517668865, eccentricity=0.0519845674010226, equilibrium_temperature=2731.9287860996974, insolation_flux=1231.425453101955),
                             Planet(planet_name='HD-7391 b', host_name='HD-7391', discovery_method='Imaging', discovery_year=2020, controversial_flag=True, orbital_period=385.7516271649597, planet_radius=6.782230633500975, planet_mass=5314.845442592018, semi_major_radius=125.40172508586431, eccentricity=0.0329056629623535, equilibrium_temperature=552.6092206304764, insolation_flux=1507.4897416714157),
                             Planet(planet_name='EPIC 6346 2', host_name='EPIC 6346', discovery_method='Orbital Brightness Modulation', discovery_year=2018, controversial_flag=True, orbital_period=277.3891428825946, planet_radius=10.431355771722751, planet_mass=4114.701089318738, semi_major_radius=60.9084604930372, eccentricity=0.0338197401304949, equilibrium_temperature=1631.376201316394, insolation_flux=116.6970416668944),
                             Planet(planet_name='WASP-4834 a', host_name='WASP-4834', discovery_method='Transit Timing Variations', discovery_year=2015, controversial_flag=True, orbital_period=453.3545990571553, planet_radius=100000.0, planet_mass=9096.127894978985, semi_major_radius=107.61797184286664, eccentricity=0.0824754486830318, equilibrium_temperature=1341.179485940515, insolation_flux=953.3850678925612),
                             Planet(planet_name='mu-4348 1', host_name='mu-4348', discovery_method='Microlensing', discovery_year=2017, controversial_flag=True, orbital_period=625.5650194005926, planet_radius=4.724588789379294, planet_mass=1687.1717455669932, semi_major_radius=107.3539025891756, eccentricity=0.0804496592967119, equilibrium_temperature=711.5830709666498, insolation_flux=1438.7118614955514),
                             Planet(planet_name='mu-4348 2', host_name='mu-4348', discovery_method='Eclipse Timing Variations', discovery_year=2022, controversial_flag=True, orbital_period=682.3966383019379, planet_radius=10.079384903221614, planet_mass=740.5654992346099, semi_major_radius=67.39928859160901, eccentricity=0.0560235717120879, equilibrium_temperature=1398.27603399874, insolation_flux=1163.3454060764273),
                             Planet(planet_name='rho 4902 a', host_name='rho 4902', discovery_method='Microlensing', discovery_year=2016, controversial_flag=True, orbital_period=578.3058649244387, planet_radius=16.335091246842318, planet_mass=5624.811679892532, semi_major_radius=100.69966232979644, eccentricity=0.0622661543350482, equilibrium_temperature=1818.8277726881904, insolation_flux=1314.641480593605),
                             Planet(planet_name='gam1-7063 b', host_name='gam1-7063', discovery_method='Transit Timing Variations', discovery_year=2021, controversial_flag=True, orbital_period=588.7583949205448, planet_radius=15.943127663816226, planet_mass=9943.622205591451, semi_major_radius=56.96146046887635, eccentricity=0.104793954265681, equilibrium_temperature=401.2889206577244, insolation_flux=1681.553219233503),
                             Planet(planet_name='rho 4046 b', host_name='rho 4046', discovery_method='Eclipse Timing Variations', discovery_year=2015, controversial_flag=True, orbital_period=1111.793026405948, planet_radius=4.495448591207892, planet_mass=1734.3176912205872, semi_major_radius=160.07180974701276, eccentricity=0.059473970790358, equilibrium_temperature=1379.2602493394013, insolation_flux=1839.0226391117471),
                             Planet(planet_name='TOI 6066 a', host_name='TOI 6066', discovery_method='Orbital Brightness Modulation', discovery_year=2019, controversial_flag=True, orbital_period=1025.3247420692646, planet_radius=13.339539115318994, planet_mass=3411.1822976893523, semi_major_radius=174.8777301493282, eccentricity=0.074201883309892, equilibrium_temperature=987.707863497814, insolation_flux=774.2531237196627),
                             Planet(planet_name='kap 3387 a', host_name='kap 3387', discovery_method='Disk Kinematics', discovery_year=2018, controversial_flag=True, orbital_period=430.0531771572245, planet_radius=9.58041896980246, planet_mass=10266.65111183085, semi_major_radius=144.05228670901764, eccentricity=0.0185151914777087, equilibrium_temperature=854.0710362544446, insolation_flux=1625.4349480388153),
                             Planet(planet_name='gam-2589 1', host_name='gam-2589', discovery_method='Orbital Brightness Modulation', discovery_year=2018, controversial_flag=True, orbital_period=928.6983987684998, planet_radius=12.057578711420629, planet_mass=1011.1433393667608, semi_major_radius=51.36723089541974, eccentricity=0.0597411143840252, equilibrium_temperature=62.47608676403252, insolation_flux=2184.2094485838134),
                             Planet(planet_name='DP 7450 a', host_name='DP 7450', discovery_method='Transit', discovery_year=2014, controversial_flag=True, orbital_period=133.0197190325618, planet_radius=100000.0, planet_mass=7034.295251136723, semi_major_radius=77.16867100136135, eccentricity=0.047550879769864, equilibrium_temperature=1486.0874000254355, insolation_flux=1097.911846729031),
                             Planet(planet_name='GJ-4327 b', host_name='GJ-4327', discovery_method='Pulsation Timing Variations', discovery_year=2016, controversial_flag=True, orbital_period=569.4299485569627, planet_radius=6.808293267924464, planet_mass=7718.979016406867, semi_major_radius=33.217220410376726, eccentricity=0.0566786039920638, equilibrium_temperature=1958.809770238539, insolation_flux=1549.1033171531597),
                             Planet(planet_name='GJ-8441 1', host_name='GJ-8441', discovery_method='Transit Timing Variations', discovery_year=2016, controversial_flag=True, orbital_period=958.4891983610668, planet_radius=8.585089685948523, planet_mass=8560.90977550197, semi_major_radius=97.83150847319544, eccentricity=0.1146019689239353, equilibrium_temperature=851.7016623327229, insolation_flux=1516.926887864091),
                             Planet(planet_name='nu 8443 1', host_name='nu 8443', discovery_method='Transit', discovery_year=2022, controversial_flag=True, orbital_period=719.936940298257, planet_radius=3.0066753829392496, planet_mass=3033.886950110159, semi_major_radius=121.25515235645015, eccentricity=0.1084026819622727, equilibrium_temperature=1291.9371223630296, insolation_flux=1086.3967797742632),
                             Planet(planet_name='HD-35325 a', host_name='HD-35325', discovery_method='Radial Velocity', discovery_year=2017, controversial_flag=True, orbital_period=825.7062494742349, planet_radius=6.677421711928475, planet_mass=3924.987360099385, semi_major_radius=83.89013991110795, eccentricity=0.0310882650768871, equilibrium_temperature=1435.576386266111, insolation_flux=934.8279224063087),
                             Planet(planet_name='HD-8474 b', host_name='HD-8474', discovery_method='Pulsar Timing', discovery_year=2021, controversial_flag=True, orbital_period=516.7530531385602, planet_radius=21.097222057537177, planet_mass=5853.608117826699, semi_major_radius=171.09813024604443, eccentricity=0.0652179846290131, equilibrium_temperature=838.210604225699, insolation_flux=72.85271022793381),
                             Planet(planet_name='HD 6180 2', host_name='HD 6180', discovery_method='Radial Velocity', discovery_year=2016, controversial_flag=True, orbital_period=638.4496075217718, planet_radius=100000.0, planet_mass=2069.359522507583, semi_major_radius=10.91646035241486, eccentricity=0.0457207786479543, equilibrium_temperature=654.5153874229864, insolation_flux=1162.935605619426),
                             Planet(planet_name='kap-2781 1', host_name='kap-2781', discovery_method='Pulsation Timing Variations', discovery_year=2019, controversial_flag=True, orbital_period=141.20691479656512, planet_radius=100000.0, planet_mass=7163.197696596852, semi_major_radius=167.39967016522195, eccentricity=0.081028383590763, equilibrium_temperature=262.4117287952279, insolation_flux=1163.943243804442),
                             Planet(planet_name='BD-327 a', host_name='BD-327', discovery_method='Pulsar Timing', discovery_year=2017, controversial_flag=True, orbital_period=167.6579970193784, planet_radius=18.2520944857154, planet_mass=4638.946003246625, semi_major_radius=137.89038365334483, eccentricity=0.0736488603124322, equilibrium_temperature=489.0782310472418, insolation_flux=100.12008661205904),
                             Planet(planet_name='WASP-88 1', host_name='WASP-88', discovery_method='Radial Velocity', discovery_year=2017, controversial_flag=True, orbital_period=184.0792438314278, planet_radius=10.565756430047587, planet_mass=5565.012530576933, semi_major_radius=59.10678743894895, eccentricity=0.0832103986176513, equilibrium_temperature=1892.030249223222, insolation_flux=1332.8716644656076),
                             Planet(planet_name='kap 9427 b', host_name='kap 9427', discovery_method='Transit', discovery_year=2019, controversial_flag=True, orbital_period=681.7784957195862, planet_radius=15.249197549460067, planet_mass=7551.109690825348, semi_major_radius=101.3793893325484, eccentricity=0.0424128188539086, equilibrium_temperature=1653.530194234027, insolation_flux=194.83521007644185),
                             Planet(planet_name='iot-4790 a', host_name='iot-4790', discovery_method='Microlensing', discovery_year=2020, controversial_flag=True, orbital_period=666.5453952703393, planet_radius=5.719763732401935, planet_mass=10044.209279689414, semi_major_radius=144.01310772806684, eccentricity=0.0490341238187977, equilibrium_temperature=1978.5364747768492, insolation_flux=1702.1137811741771),
                             Planet(planet_name='iot-4790 b', host_name='iot-4790', discovery_method='Transit', discovery_year=2019, controversial_flag=True, orbital_period=1036.076091810797, planet_radius=24.92172843549643, planet_mass=10937.696132864286, semi_major_radius=86.8827202810187, eccentricity=0.0475553774317843, equilibrium_temperature=1540.2055329367113, insolation_flux=1392.4122792508556),
                             Planet(planet_name='iot-4040 b', host_name='iot-4040', discovery_method='Radial Velocity', discovery_year=2018, controversial_flag=True, orbital_period=412.1637048948276, planet_radius=100000.0, planet_mass=5778.091045777841, semi_major_radius=152.27327213409555, eccentricity=0.0412464040914767, equilibrium_temperature=1097.2793245964726, insolation_flux=508.0001312605468),
                             Planet(planet_name='EPIC-4390 1', host_name='EPIC-4390', discovery_method='Transit', discovery_year=2017, controversial_flag=True, orbital_period=649.3063411213564, planet_radius=23.34230174881093, planet_mass=8261.464359059963, semi_major_radius=173.2248176480395, eccentricity=0.0592779893895435, equilibrium_temperature=1950.5192338576455, insolation_flux=1067.3042784004035),
                             Planet(planet_name='EPIC-4390 2', host_name='EPIC-4390', discovery_method='Transit', discovery_year=2019, controversial_flag=True, orbital_period=757.3276928811006, planet_radius=10.59702174577856, planet_mass=3956.729766712837, semi_major_radius=132.61820344954918, eccentricity=0.0370468790614808, equilibrium_temperature=1630.188293736801, insolation_flux=1333.4819561659397),
                             Planet(planet_name='Kepler 4050 2', host_name='Kepler 4050', discovery_method='Eclipse Timing Variations', discovery_year=2013, controversial_flag=True, orbital_period=105.2701721284218, planet_radius=100000.0, planet_mass=9157.81340916703, semi_major_radius=58.053252645296375, eccentricity=0.0660143475447197, equilibrium_temperature=1088.8425645365137, insolation_flux=1522.6725289359292),
                             Planet(planet_name='GJ-8116 1', host_name='GJ-8116', discovery_method='Astrometry', discovery_year=2015, controversial_flag=True, orbital_period=636.4405427219526, planet_radius=100000.0, planet_mass=1936.8988053286344, semi_major_radius=47.46972528431341, eccentricity=0.028163465656965, equilibrium_temperature=2146.001163836294, insolation_flux=755.1886188557178),
                             Planet(planet_name='tau 658 2', host_name='tau 658', discovery_method='Imaging', discovery_year=2018, controversial_flag=True, orbital_period=222.7722062688443, planet_radius=9.356316049621851, planet_mass=5946.311975095338, semi_major_radius=85.06751353332885, eccentricity=0.0578255980853389, equilibrium_temperature=1592.621724450606, insolation_flux=1663.2124660741092),
                             Planet(planet_name='omi 8387 2', host_name='omi 8387', discovery_method='Pulsar Timing', discovery_year=2017, controversial_flag=True, orbital_period=362.1576078262134, planet_radius=8.651068178949686, planet_mass=6200.210297617688, semi_major_radius=95.06745468270648, eccentricity=0.0408908616925881, equilibrium_temperature=2000.006274767972, insolation_flux=1404.144589616883),
                             Planet(planet_name='ups 9504 a', host_name='ups 9504', discovery_method='Transit Timing Variations', discovery_year=2017, controversial_flag=True, orbital_period=152.21084437575496, planet_radius=11.572389718960368, planet_mass=277.99549493241284, semi_major_radius=75.96344454569285, eccentricity=0.0177834820015716, equilibrium_temperature=381.0713833354921, insolation_flux=943.2788747782124),
                             Planet(planet_name='xi 5716 2', host_name='xi 5716', discovery_method='Imaging', discovery_year=2022, controversial_flag=True, orbital_period=675.1177876147931, planet_radius=19.182631524247824, planet_mass=3394.469987368321, semi_major_radius=199.25237957596332, eccentricity=0.0197252299880566, equilibrium_temperature=1795.9691226289317, insolation_flux=744.795343372701),
                             Planet(planet_name='gam-7970 2', host_name='gam-7970', discovery_method='Astrometry', discovery_year=2020, controversial_flag=True, orbital_period=379.82850904228906, planet_radius=1.2475717305157712, planet_mass=9201.379155141962, semi_major_radius=73.82085547369267, eccentricity=0.008481096153952, equilibrium_temperature=596.8909011020712, insolation_flux=1271.5055468075086),
                             Planet(planet_name='nu-7327 b', host_name='nu-7327', discovery_method='Microlensing', discovery_year=2019, controversial_flag=True, orbital_period=479.8249700957312, planet_radius=4.830534340053705, planet_mass=10840.851143027972, semi_major_radius=43.77596884406901, eccentricity=0.0777356006522241, equilibrium_temperature=1799.1104943698328, insolation_flux=1586.10187670473),
                             Planet(planet_name='ome 5893 1', host_name='ome 5893', discovery_method='Transit', discovery_year=2018, controversial_flag=True, orbital_period=646.4361174808985, planet_radius=100000.0, planet_mass=6366.772008906482, semi_major_radius=56.440837982382845, eccentricity=0.0787357924249305, equilibrium_temperature=1754.226720684142, insolation_flux=1542.032610535152),
                             Planet(planet_name='omi-4274 2', host_name='omi-4274', discovery_method='Transit Timing Variations', discovery_year=2018, controversial_flag=True, orbital_period=643.1159345129688, planet_radius=100000.0, planet_mass=4258.978475656949, semi_major_radius=148.48634963940498, eccentricity=0.0472385548394637, equilibrium_temperature=216.37958672603952, insolation_flux=1226.939125738057),
                             Planet(planet_name='kap 2698 1', host_name='kap 2698', discovery_method='Transit Timing Variations', discovery_year=2019, controversial_flag=True, orbital_period=850.3286055924416, planet_radius=5.480077836169533, planet_mass=5163.036625515761, semi_major_radius=86.7641138812192, eccentricity=0.1023827431767051, equilibrium_temperature=1759.112973269909, insolation_flux=602.0179204535649),
                             Planet(planet_name='kap 2698 2', host_name='kap 2698', discovery_method='Eclipse Timing Variations', discovery_year=2018, controversial_flag=True, orbital_period=646.1681107004526, planet_radius=6.504125565797831, planet_mass=4834.148010949664, semi_major_radius=91.73232570817, eccentricity=0.0840012563658705, equilibrium_temperature=517.7170431662213, insolation_flux=1221.9086512587223),
                             Planet(planet_name='xi-117 1', host_name='xi-117', discovery_method='Astrometry', discovery_year=2015, controversial_flag=True, orbital_period=912.0585450283684, planet_radius=18.777774201492512, planet_mass=4458.247920914466, semi_major_radius=51.45772520707793, eccentricity=0.0606236395602185, equilibrium_temperature=788.493355590664, insolation_flux=1058.8986181621965),
                             Planet(planet_name='eps-5081 1', host_name='eps-5081', discovery_method='Transit Timing Variations', discovery_year=2017, controversial_flag=True, orbital_period=863.6629578605655, planet_radius=10.0051685585896, planet_mass=1659.8141633681405, semi_major_radius=204.0296110984561, eccentricity=0.1112361321526045, equilibrium_temperature=517.8765885712708, insolation_flux=1440.0222361245185),
                             Planet(planet_name='ome-14654 a', host_name='ome-14654', discovery_method='Radial Velocity', discovery_year=2019, controversial_flag=True, orbital_period=712.7137744785225, planet_radius=100000.0, planet_mass=8160.017888457885, semi_major_radius=182.41702570756408, eccentricity=0.1084749591689399, equilibrium_temperature=1804.967131290616, insolation_flux=753.8067169138008),
                             Planet(planet_name='ome-14654 b', host_name='ome-14654', discovery_method='Pulsation Timing Variations', discovery_year=2016, controversial_flag=True, orbital_period=1005.9389967635092, planet_radius=100000.0, planet_mass=8175.473361672259, semi_major_radius=134.17349934175644, eccentricity=0.0519502505459126, equilibrium_temperature=1094.966283961313, insolation_flux=1272.6263332967587),
                             Planet(planet_name='psi1-4886 a', host_name='psi1-4886', discovery_method='Radial Velocity', discovery_year=2022, controversial_flag=True, orbital_period=528.3904820733509, planet_radius=24.641734425810785, planet_mass=5426.686691794237, semi_major_radius=106.50617529281035, eccentricity=0.0715845974299112, equilibrium_temperature=1278.5843009157254, insolation_flux=1048.4653680093952),
                             Planet(planet_name='psi1-4492 b', host_name='psi1-4492', discovery_method='Pulsation Timing Variations', discovery_year=2021, controversial_flag=True, orbital_period=473.3724739081972, planet_radius=11.917417287709531, planet_mass=5156.289411598849, semi_major_radius=87.90917815605036, eccentricity=0.050334615553184, equilibrium_temperature=694.2019241619729, insolation_flux=2263.4009821208674),
                             Planet(planet_name='GJ 8971 a', host_name='GJ 8971', discovery_method='Disk Kinematics', discovery_year=2019, controversial_flag=True, orbital_period=866.784300971517, planet_radius=19.877066863497117, planet_mass=2618.4782516272817, semi_major_radius=71.92902929660113, eccentricity=0.0487421927533157, equilibrium_temperature=1058.1561589073335, insolation_flux=1718.515301852699),
                             Planet(planet_name='eps 7991 2', host_name='eps 7991', discovery_method='Disk Kinematics', discovery_year=2016, controversial_flag=True, orbital_period=506.3225818667709, planet_radius=100000.0, planet_mass=6160.491201147499, semi_major_radius=159.56078525702603, eccentricity=0.0357366351539084, equilibrium_temperature=2261.199701568933, insolation_flux=621.4381120884996),
                             Planet(planet_name='ome 6113 a', host_name='ome 6113', discovery_method='Pulsar Timing', discovery_year=2020, controversial_flag=True, orbital_period=503.7093838079888, planet_radius=13.432113410293862, planet_mass=4907.165860431947, semi_major_radius=96.09312429011445, eccentricity=0.0315225002804153, equilibrium_temperature=228.1200559749991, insolation_flux=1266.5785531626132),
                             Planet(planet_name='bet-3561 a', host_name='bet-3561', discovery_method='Pulsation Timing Variations', discovery_year=2021, controversial_flag=True, orbital_period=808.0284165790233, planet_radius=7.921413705967491, planet_mass=4140.942198041259, semi_major_radius=144.27623686194048, eccentricity=0.0380526933686738, equilibrium_temperature=1015.0337324398438, insolation_flux=2932.2865946604006),
                             Planet(planet_name='rho 9149 2', host_name='rho 9149', discovery_method='Eclipse Timing Variations', discovery_year=2019, controversial_flag=True, orbital_period=189.7165990880661, planet_radius=9.63455819621104, planet_mass=10013.645141471176, semi_major_radius=105.80125476662828, eccentricity=0.0641532212563344, equilibrium_temperature=1805.972511484058, insolation_flux=1011.288692487801),
                             Planet(planet_name='EPIC-2692 b', host_name='EPIC-2692', discovery_method='Disk Kinematics', discovery_year=2019, controversial_flag=True, orbital_period=131.30623752807742, planet_radius=100000.0, planet_mass=5869.1783784814525, semi_major_radius=29.69205677376661, eccentricity=0.0403925851183185, equilibrium_temperature=1086.4709989208147, insolation_flux=1143.990737960272),
                             Planet(planet_name='mu2 6972 a', host_name='mu2 6972', discovery_method='Radial Velocity', discovery_year=2017, controversial_flag=True, orbital_period=761.6390165180227, planet_radius=12.492475999283007, planet_mass=2644.9542336479853, semi_major_radius=105.4544362552296, eccentricity=0.0332457421387275, equilibrium_temperature=1460.5387199686131, insolation_flux=72.47199372210548),
                             Planet(planet_name='BD 53 a', host_name='BD 53', discovery_method='Pulsar Timing', discovery_year=2022, controversial_flag=True, orbital_period=630.8968574099363, planet_radius=100000.0, planet_mass=6224.558124155811, semi_major_radius=101.53186861341372, eccentricity=0.0471271669735323, equilibrium_temperature=2827.6905246568776, insolation_flux=280.92452087228537),
                             Planet(planet_name='ome 1615 a', host_name='ome 1615', discovery_method='Transit Timing Variations', discovery_year=2017, controversial_flag=True, orbital_period=277.7158612801429, planet_radius=100000.0, planet_mass=5999.14760707899, semi_major_radius=94.44847305006247, eccentricity=0.0200080608147064, equilibrium_temperature=1511.2894179017894, insolation_flux=1163.964284744575),
                             Planet(planet_name='ome 1615 b', host_name='ome 1615', discovery_method='Orbital Brightness Modulation', discovery_year=2020, controversial_flag=True, orbital_period=579.7666635424757, planet_radius=100000.0, planet_mass=6776.633334193886, semi_major_radius=171.57641815541814, eccentricity=0.0441839769272934, equilibrium_temperature=487.513707365076, insolation_flux=2551.927011216121),
                             Planet(planet_name='mu-3818 a', host_name='mu-3818', discovery_method='Transit Timing Variations', discovery_year=2017, controversial_flag=True, orbital_period=651.7714790422754, planet_radius=12.835891754922905, planet_mass=7877.8240149320445, semi_major_radius=36.021768934390195, eccentricity=0.0423113608369359, equilibrium_temperature=121.80207171565291, insolation_flux=61.66645717533993),
                             Planet(planet_name='mu 7510 b', host_name='mu 7510', discovery_method='Transit', discovery_year=2018, controversial_flag=True, orbital_period=772.0738632940004, planet_radius=10.91829928742542, planet_mass=10375.24834403525, semi_major_radius=90.503169551751, eccentricity=0.0504948290407837, equilibrium_temperature=1025.8805812660528, insolation_flux=1639.3608566300825),
                             Planet(planet_name='bet 879 2', host_name='bet 879', discovery_method='Astrometry', discovery_year=2016, controversial_flag=True, orbital_period=738.1451134925089, planet_radius=3.129449310609669, planet_mass=4874.6348529577, semi_major_radius=72.78322292780594, eccentricity=0.0138765101736364, equilibrium_temperature=912.378538231445, insolation_flux=1588.9008953012326),
                             Planet(planet_name='nu 5173 b', host_name='nu 5173', discovery_method='Astrometry', discovery_year=2016, controversial_flag=True, orbital_period=700.3256532592104, planet_radius=100000.0, planet_mass=7219.810732444034, semi_major_radius=137.8264578886174, eccentricity=0.0621858299313943, equilibrium_temperature=1608.4804862651292, insolation_flux=133.04919912959122),
                             Planet(planet_name='ome 7130 a', host_name='ome 7130', discovery_method='Pulsar Timing', discovery_year=2020, controversial_flag=True, orbital_period=275.10180260630983, planet_radius=100000.0, planet_mass=2977.7578876788248, semi_major_radius=192.1014929460937, eccentricity=0.0295989226950882, equilibrium_temperature=706.538579574599, insolation_flux=2095.0594697563747),
                             Planet(planet_name='ups-1040 a', host_name='ups-1040', discovery_method='Pulsation Timing Variations', discovery_year=2018, controversial_flag=True, orbital_period=679.7046221645213, planet_radius=11.441789441294995, planet_mass=4261.21058029733, semi_major_radius=106.37876501853654, eccentricity=0.043784232347177, equilibrium_temperature=1094.3047400362586, insolation_flux=1339.544638842469),
                             Planet(planet_name='rho 36 2', host_name='rho 36', discovery_method='Microlensing', discovery_year=2018, controversial_flag=True, orbital_period=243.43721229468173, planet_radius=11.509245775834788, planet_mass=494.3771339762216, semi_major_radius=174.06845214021854, eccentricity=0.0401593560468982, equilibrium_temperature=1093.0898157975362, insolation_flux=1525.0464101893413),
                             Planet(planet_name='psi1-5386 1', host_name='psi1-5386', discovery_method='Astrometry', discovery_year=2019, controversial_flag=True, orbital_period=1248.0732059847517, planet_radius=6.087660126397834, planet_mass=681.8064105785024, semi_major_radius=103.80578312324758, eccentricity=0.0072696611676694, equilibrium_temperature=707.4757330282184, insolation_flux=1282.7913515781925),
                             Planet(planet_name='psi1-5386 2', host_name='psi1-5386', discovery_method='Orbital Brightness Modulation', discovery_year=2022, controversial_flag=True, orbital_period=943.2560144819358, planet_radius=7.589878758181966, planet_mass=13898.082444494854, semi_major_radius=43.94988542624611, eccentricity=0.0890026070417055, equilibrium_temperature=1812.3583889975555, insolation_flux=1246.2115923591907),
                             Planet(planet_name='2MASS 4268 1', host_name='2MASS 4268', discovery_method='Microlensing', discovery_year=2013, controversial_flag=True, orbital_period=881.1287709709959, planet_radius=7.680135888844545, planet_mass=3098.809170684862, semi_major_radius=92.51663204345364, eccentricity=0.0705971690275846, equilibrium_temperature=1817.8845686164584, insolation_flux=1019.5778951286776),
                             Planet(planet_name='mu-4366 a', host_name='mu-4366', discovery_method='Transit', discovery_year=2019, controversial_flag=True, orbital_period=580.794076732246, planet_radius=12.043584935819784, planet_mass=3680.975926124213, semi_major_radius=76.75162485615975, eccentricity=0.0496173964603909, equilibrium_temperature=1600.5500910800451, insolation_flux=1188.5126978219398),
                             Planet(planet_name='mu-4366 b', host_name='mu-4366', discovery_method='Transit', discovery_year=2020, controversial_flag=True, orbital_period=1025.4166771976595, planet_radius=16.433160070282952, planet_mass=7069.997046289255, semi_major_radius=185.57558014098856, eccentricity=0.0821595603301544, equilibrium_temperature=1796.399680177591, insolation_flux=877.0609768628192),
                             Planet(planet_name='WASP 6198 1', host_name='WASP 6198', discovery_method='Transit Timing Variations', discovery_year=2018, controversial_flag=True, orbital_period=713.3702159824359, planet_radius=25.118248825010458, planet_mass=2242.0090190186165, semi_major_radius=120.4879359438416, eccentricity=0.0652483230577292, equilibrium_temperature=291.1699055468937, insolation_flux=2031.1411658044128),
                             Planet(planet_name='mu 1561 a', host_name='mu 1561', discovery_method='Pulsar Timing', discovery_year=2019, controversial_flag=True, orbital_period=550.5114854811321, planet_radius=100000.0, planet_mass=5922.484267046741, semi_major_radius=41.11997968140539, eccentricity=0.1099627898726985, equilibrium_temperature=2163.37108599896, insolation_flux=765.586110647453),
                             Planet(planet_name='mu 1561 b', host_name='mu 1561', discovery_method='Microlensing', discovery_year=2016, controversial_flag=True, orbital_period=599.5708561385712, planet_radius=100000.0, planet_mass=11864.848022447848, semi_major_radius=95.18932656262558, eccentricity=0.0425410535642827, equilibrium_temperature=985.1303618507412, insolation_flux=1247.3426107370683),
                             Planet(planet_name='alf 1688 2', host_name='alf 1688', discovery_method='Orbital Brightness Modulation', discovery_year=2020, controversial_flag=True, orbital_period=340.4292437623501, planet_radius=12.82156355317338, planet_mass=5062.731785823375, semi_major_radius=94.24045364304526, eccentricity=0.0162026805447433, equilibrium_temperature=1783.3062163591098, insolation_flux=2225.456088048149),
                             Planet(planet_name='alf-5 1', host_name='alf-5', discovery_method='Microlensing', discovery_year=2016, controversial_flag=True, orbital_period=767.6974029262708, planet_radius=100000.0, planet_mass=6106.254575695222, semi_major_radius=76.89343040945724, eccentricity=0.0130776256717253, equilibrium_temperature=1666.525739902146, insolation_flux=1848.2730528107115),
                             Planet(planet_name='tau 5471 a', host_name='tau 5471', discovery_method='Transit Timing Variations', discovery_year=2016, controversial_flag=True, orbital_period=591.3332592701136, planet_radius=15.043613408825212, planet_mass=9745.904301749231, semi_major_radius=137.1803780030917, eccentricity=0.0623942653679209, equilibrium_temperature=1735.386784243202, insolation_flux=1073.5713229668995),
                             Planet(planet_name='xi 7984 2', host_name='xi 7984', discovery_method='Imaging', discovery_year=2022, controversial_flag=True, orbital_period=159.5869011663292, planet_radius=3.766548004515962, planet_mass=5909.496967789892, semi_major_radius=54.38138330682965, eccentricity=0.0666125883745894, equilibrium_temperature=2556.160096947642, insolation_flux=328.00451407420405),
                             Planet(planet_name='TOI 1596 a', host_name='TOI 1596', discovery_method='Disk Kinematics', discovery_year=2022, controversial_flag=True, orbital_period=527.0096438206555, planet_radius=16.17545775300354, planet_mass=1567.50912257253, semi_major_radius=130.25916447949194, eccentricity=0.0304620741445396, equilibrium_temperature=1540.3812014314128, insolation_flux=2524.123616408521),
                             Planet(planet_name='WASP-4961 1', host_name='WASP-4961', discovery_method='Radial Velocity', discovery_year=2018, controversial_flag=True, orbital_period=392.1794748426417, planet_radius=17.736146562081085, planet_mass=1990.6558600167243, semi_major_radius=21.625984916726026, eccentricity=0.041858746035834, equilibrium_temperature=372.6732053395409, insolation_flux=1298.57847195684),
                             Planet(planet_name='WASP-4961 2', host_name='WASP-4961', discovery_method='Transit Timing Variations', discovery_year=2018, controversial_flag=True, orbital_period=586.2785065086804, planet_radius=4.380499839675768, planet_mass=2374.025102006756, semi_major_radius=139.98248980215402, eccentricity=0.1142465889524809, equilibrium_temperature=1690.979993074038, insolation_flux=2057.114125486619),
                             Planet(planet_name='DP 1045 b', host_name='DP 1045', discovery_method='Radial Velocity', discovery_year=2022, controversial_flag=True, orbital_period=260.4793207242669, planet_radius=8.563356032285787, planet_mass=1209.0367993602513, semi_major_radius=3.8690376881154265, eccentricity=0.0622059957614222, equilibrium_temperature=1769.0715296687008, insolation_flux=1249.564733014624),
                             Planet(planet_name='mu2 1465 2', host_name='mu2 1465', discovery_method='Radial Velocity', discovery_year=2018, controversial_flag=True, orbital_period=424.3982095419722, planet_radius=100000.0, planet_mass=5738.773691808511, semi_major_radius=72.75763653838091, eccentricity=0.0320118571565423, equilibrium_temperature=1003.998376306314, insolation_flux=555.8668673935539)],
                     'q15': [Planet(planet_name='2MASS 3387 4', host_name='2MASS 3387', discovery_method='Transit Timing Variations', discovery_year=2020, controversial_flag=False, orbital_period=554.5241248496626, planet_radius=7.770625431800216, planet_mass=6223.589493384062, semi_major_radius=71.80600304626736, eccentricity=0.0364519599110245, equilibrium_temperature=1256.3657093670795, insolation_flux=1098.3126800318812),
                             Planet(planet_name='gam1 1596 a', host_name='gam1 1596', discovery_method='Orbital Brightness Modulation', discovery_year=2022, controversial_flag=False, orbital_period=644.9745969231304, planet_radius=100000.0, planet_mass=6805.407389343258, semi_major_radius=109.2996658513811, eccentricity=0.0332368338312035, equilibrium_temperature=1702.6422254022075, insolation_flux=1095.355723782338),
                             Planet(planet_name='gam1 1596 b', host_name='gam1 1596', discovery_method='Orbital Brightness Modulation', discovery_year=2020, controversial_flag=False, orbital_period=488.6100718032155, planet_radius=100000.0, planet_mass=3505.548258710004, semi_major_radius=130.180314820048, eccentricity=0.0400342077199568, equilibrium_temperature=1682.925819297625, insolation_flux=172.59672597991812),
                             Planet(planet_name='gam1 1596 c', host_name='gam1 1596', discovery_method='Microlensing', discovery_year=2020, controversial_flag=False, orbital_period=431.06329152065206, planet_radius=100000.0, planet_mass=1229.6589270663903, semi_major_radius=16.981769987625555, eccentricity=0.0221156352185, equilibrium_temperature=1385.542912751809, insolation_flux=1773.35608138235),
                             Planet(planet_name='gam1 1596 d', host_name='gam1 1596', discovery_method='Eclipse Timing Variations', discovery_year=2019, controversial_flag=True, orbital_period=129.25542192871308, planet_radius=100000.0, planet_mass=7586.319677670051, semi_major_radius=149.9232398294629, eccentricity=0.0890842646299611, equilibrium_temperature=1284.0372521568352, insolation_flux=1365.2570619626845)],
                     'q16': [],
                     'q17': 0,
                     'q18': Star(spectral_type='W1.25', stellar_effective_temperature=4178.0958883651865, stellar_radius=23.506755788319683, stellar_mass=1.659316514553687, stellar_luminosity=-1.3282779386248031, stellar_surface_gravity=3.411616618459385, stellar_age=3.1899461613905045),
                     'q19': 12.020802511402517}
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
