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
                     'q5': Star(spectral_type='G6.75III/I', stellar_effective_temperature=4806.073841782789, stellar_radius=19.12361725614394, stellar_mass=3.873313884301798, stellar_luminosity=3.070363545524019, stellar_surface_gravity=2.280499275670044, stellar_age=1.4249535681619028),
                     'q6': Star(spectral_type='D1V-G8.25III', stellar_effective_temperature=6580.45674449826, stellar_radius=28.793275933664734, stellar_mass=1.7108909096084335, stellar_luminosity=-0.6287156741996038, stellar_surface_gravity=5.583987444127004, stellar_age=11.135708302653681),
                     'q7': -0.04375686646712192,
                     'q8': 7.177178416382857,
                     'q9': 3314.200834975658,
                     'q10': 'ome 2368',
                     'q11': 6.685433675495716,
                     'Planet': Planet(planet_name='Jupiter', host_name='Sun', discovery_method='Imaging', discovery_year=1610, controversial_flag=False, orbital_period=4333.0, planet_radius=11.209, planet_mass=317.828, semi_major_radius=5.2038, eccentricity=0.0489, equilibrium_temperature=110, insolation_flux=0.0345),
                     'q12': Planet(planet_name='HD 9070 1', host_name='HD 9070', discovery_method='Pulsation Timing Variations', discovery_year=2017, controversial_flag=False, orbital_period=353.92318763995803, planet_radius=20.13388655684213, planet_mass=10786.635275108973, semi_major_radius=9.829285182139657, eccentricity=0.0376168740549478, equilibrium_temperature=1142.18918640707, insolation_flux=1030.48090221517),
                     'q13': [Planet(planet_name='alf-9810 1', host_name='alf-9810', discovery_method='Orbital Brightness Modulation', discovery_year=2018, controversial_flag=False, orbital_period=781.034695162671, planet_radius=21.284467444864298, planet_mass=6648.538090739557, semi_major_radius=102.88689147123324, eccentricity=0.0712497133371211, equilibrium_temperature=1681.8876397218307, insolation_flux=1051.4313015098528),
                             Planet(planet_name='bet-5510 1', host_name='bet-5510', discovery_method='Transit', discovery_year=2016, controversial_flag=False, orbital_period=321.66320591476165, planet_radius=5.278505937325793, planet_mass=9602.25955356692, semi_major_radius=51.801744833525, eccentricity=0.0383146748270257, equilibrium_temperature=108.92462824946745, insolation_flux=680.3851179674284),
                             Planet(planet_name='ups-5078 a', host_name='ups-5078', discovery_method='Imaging', discovery_year=2018, controversial_flag=False, orbital_period=335.37888904770494, planet_radius=17.46259253747195, planet_mass=1051.3432715432782, semi_major_radius=81.05696740182168, eccentricity=0.0215631483302318, equilibrium_temperature=1973.7973368952717, insolation_flux=2220.5315494031347),
                             Planet(planet_name='nu-5638 1', host_name='nu-5638', discovery_method='Microlensing', discovery_year=2019, controversial_flag=False, orbital_period=134.4922234208248, planet_radius=15.162149916163576, planet_mass=4867.207712582858, semi_major_radius=131.85062352933127, eccentricity=0.0722173781150215, equilibrium_temperature=884.8477898105652, insolation_flux=1489.6025178305542),
                             Planet(planet_name='BD-3099 a', host_name='BD-3099', discovery_method='Astrometry', discovery_year=2019, controversial_flag=False, orbital_period=275.4700398682963, planet_radius=5.190027891193489, planet_mass=14029.5585845204, semi_major_radius=74.94792148258702, eccentricity=0.0602479878196307, equilibrium_temperature=867.5851219837182, insolation_flux=1018.3960153651732)],
                     'q14': [Planet(planet_name='psi1 89 1', host_name='psi1 89', discovery_method='Microlensing', discovery_year=2015, controversial_flag=True, orbital_period=263.2487163329138, planet_radius=9.654493147625256, planet_mass=5852.826473069793, semi_major_radius=92.61339599163162, eccentricity=0.033622233128441, equilibrium_temperature=769.7454363896949, insolation_flux=2122.477860118487),
                             Planet(planet_name='rho 6350 2', host_name='rho 6350', discovery_method='Astrometry', discovery_year=2016, controversial_flag=True, orbital_period=268.0498350857994, planet_radius=12.89039576166856, planet_mass=6707.922225529284, semi_major_radius=196.5510122561655, eccentricity=0.0055446032367511, equilibrium_temperature=946.10614748734, insolation_flux=1382.9413767715696),
                             Planet(planet_name='ups 9511 a', host_name='ups 9511', discovery_method='Orbital Brightness Modulation', discovery_year=2022, controversial_flag=True, orbital_period=394.5195244758813, planet_radius=10.631455950372356, planet_mass=6885.851049822459, semi_major_radius=75.18085809697591, eccentricity=0.0105069214194711, equilibrium_temperature=788.6566353934647, insolation_flux=617.3100849601634),
                             Planet(planet_name='GJ 6548 1', host_name='GJ 6548', discovery_method='Disk Kinematics', discovery_year=2018, controversial_flag=True, orbital_period=421.0404895743942, planet_radius=21.339669949854475, planet_mass=2046.517692665336, semi_major_radius=93.37322760014207, eccentricity=0.0412604468106009, equilibrium_temperature=916.0471176266092, insolation_flux=1122.0954731649167),
                             Planet(planet_name='TOI-2202 c', host_name='alf 6628', discovery_method='Pulsar Timing', discovery_year=2016, controversial_flag=True, orbital_period=366.9629457410874, planet_radius=9.76427071115195, planet_mass=6567.427360085808, semi_major_radius=86.13991924201923, eccentricity=0.0048097458167733, equilibrium_temperature=1470.9952731596663, insolation_flux=156.4318347711403),
                             Planet(planet_name='rho 9266 b', host_name='rho 9266', discovery_method='Eclipse Timing Variations', discovery_year=2020, controversial_flag=True, orbital_period=259.65220026201143, planet_radius=7.764897010521441, planet_mass=2756.345189717624, semi_major_radius=60.83976693008117, eccentricity=0.001158896473433, equilibrium_temperature=2331.3588131141123, insolation_flux=2367.34418684085),
                             Planet(planet_name='gam1-9925 a', host_name='gam1-9925', discovery_method='Imaging', discovery_year=2021, controversial_flag=True, orbital_period=708.4889569450821, planet_radius=8.633000630068437, planet_mass=6970.405446219324, semi_major_radius=38.42565552572249, eccentricity=0.0692081192859957, equilibrium_temperature=767.2427047214742, insolation_flux=1209.767871812247),
                             Planet(planet_name='rho 3507 a', host_name='rho 3507', discovery_method='Pulsar Timing', discovery_year=2016, controversial_flag=True, orbital_period=636.8867917415213, planet_radius=12.85074268479914, planet_mass=1899.6348606221104, semi_major_radius=151.7048896832768, eccentricity=0.0161917438223121, equilibrium_temperature=457.1384619243584, insolation_flux=1609.9010913506131),
                             Planet(planet_name='Kepler-7792 a', host_name='Kepler-7792', discovery_method='Transit Timing Variations', discovery_year=2017, controversial_flag=True, orbital_period=363.7976376533061, planet_radius=9.529691345673744, planet_mass=5812.920313346488, semi_major_radius=126.5267051017934, eccentricity=0.0497496283775688, equilibrium_temperature=177.36996556598126, insolation_flux=597.7372336463284),
                             Planet(planet_name='psi1-3874 1', host_name='psi1-3874', discovery_method='Eclipse Timing Variations', discovery_year=2020, controversial_flag=True, orbital_period=491.7659438159441, planet_radius=15.19555675413008, planet_mass=6090.227928428773, semi_major_radius=1.3382693167585558, eccentricity=0.1362738499655617, equilibrium_temperature=2794.521576929553, insolation_flux=1460.5258978623046),
                             Planet(planet_name='xi-8834 a', host_name='xi-8834', discovery_method='Radial Velocity', discovery_year=2019, controversial_flag=True, orbital_period=138.4250590204776, planet_radius=13.097828657676896, planet_mass=3317.55931668632, semi_major_radius=235.9860055816932, eccentricity=0.021966887144172, equilibrium_temperature=135.40613193723436, insolation_flux=1392.0375391643545),
                             Planet(planet_name='Kepler 4568 1', host_name='Kepler 4568', discovery_method='Transit', discovery_year=2020, controversial_flag=True, orbital_period=562.059875003393, planet_radius=5.909932014545979, planet_mass=7852.383026642021, semi_major_radius=244.26259278577368, eccentricity=0.0866636335434401, equilibrium_temperature=1363.9544068903415, insolation_flux=966.5826993344112),
                             Planet(planet_name='Kepler 4568 2', host_name='Kepler 4568', discovery_method='Microlensing', discovery_year=2017, controversial_flag=True, orbital_period=721.6558137402396, planet_radius=9.818791433476848, planet_mass=2941.792509106195, semi_major_radius=146.1206708155574, eccentricity=0.0399048260809387, equilibrium_temperature=1116.4876139449548, insolation_flux=1040.911027462466),
                             Planet(planet_name='iot 8420 a', host_name='iot 8420', discovery_method='Imaging', discovery_year=2019, controversial_flag=True, orbital_period=460.0835914229656, planet_radius=6.472497109259563, planet_mass=14602.712774490245, semi_major_radius=129.17482788109388, eccentricity=0.0398858374251792, equilibrium_temperature=2718.603816818653, insolation_flux=1386.4184881935275),
                             Planet(planet_name='mu2 346 a', host_name='mu2 346', discovery_method='Microlensing', discovery_year=2022, controversial_flag=True, orbital_period=462.11649405122137, planet_radius=21.19658910585256, planet_mass=5999.492900697904, semi_major_radius=157.1344628541022, eccentricity=0.0935916223144223, equilibrium_temperature=2073.979039122853, insolation_flux=1596.51368377548),
                             Planet(planet_name='kap 5420 1', host_name='kap 5420', discovery_method='Astrometry', discovery_year=2017, controversial_flag=True, orbital_period=292.77186744663766, planet_radius=5.03398742547011, planet_mass=1011.4852637775044, semi_major_radius=68.61982461121077, eccentricity=0.0223171971074508, equilibrium_temperature=712.0297307210749, insolation_flux=52.6086191521149),
                             Planet(planet_name='GJ-1729 1', host_name='GJ-1729', discovery_method='Pulsation Timing Variations', discovery_year=2020, controversial_flag=True, orbital_period=372.8963466932428, planet_radius=23.10347676403204, planet_mass=7056.538105787207, semi_major_radius=88.12048424401308, eccentricity=0.0987421326017598, equilibrium_temperature=1129.1750536497796, insolation_flux=1097.5039504904628),
                             Planet(planet_name='GJ-1729 2', host_name='GJ-1729', discovery_method='Pulsar Timing', discovery_year=2018, controversial_flag=True, orbital_period=1239.4315308679795, planet_radius=20.483007340338972, planet_mass=7737.452326284323, semi_major_radius=133.815579111814, eccentricity=0.0516523645271102, equilibrium_temperature=736.4981615564135, insolation_flux=1136.8784712976228),
                             Planet(planet_name='nu-4335 b', host_name='nu-4335', discovery_method='Eclipse Timing Variations', discovery_year=2019, controversial_flag=True, orbital_period=565.2715370893663, planet_radius=10.952741012703768, planet_mass=4807.411625153405, semi_major_radius=124.18946256968312, eccentricity=0.0240763408135991, equilibrium_temperature=608.1648596247862, insolation_flux=379.84885444591646),
                             Planet(planet_name='Kepler 7164 a', host_name='Kepler 7164', discovery_method='Transit Timing Variations', discovery_year=2016, controversial_flag=True, orbital_period=440.93179625136304, planet_radius=10.972873567573188, planet_mass=1960.4278483766225, semi_major_radius=1.9496364673839397, eccentricity=0.0442893726011322, equilibrium_temperature=706.0484811784638, insolation_flux=1052.2420599498057),
                             Planet(planet_name='Kepler 7164 b', host_name='Kepler 7164', discovery_method='Radial Velocity', discovery_year=2018, controversial_flag=True, orbital_period=439.9334792580728, planet_radius=10.305378012313888, planet_mass=4039.573929483105, semi_major_radius=50.15139926522862, eccentricity=0.0368451443695037, equilibrium_temperature=710.9089023944412, insolation_flux=623.3388810000133),
                             Planet(planet_name='BD 7872 1', host_name='BD 7872', discovery_method='Radial Velocity', discovery_year=2019, controversial_flag=True, orbital_period=603.705241507797, planet_radius=9.632090792711008, planet_mass=8059.556704470779, semi_major_radius=95.92008191963748, eccentricity=0.0434679260746179, equilibrium_temperature=773.9941992459023, insolation_flux=739.5027275334297),
                             Planet(planet_name='mu 9036 2', host_name='mu 9036', discovery_method='Astrometry', discovery_year=2016, controversial_flag=True, orbital_period=891.649348086514, planet_radius=13.805288902066046, planet_mass=3366.593134923535, semi_major_radius=71.77200868226745, eccentricity=0.0748963189384822, equilibrium_temperature=1469.753546455439, insolation_flux=1306.0450937310025),
                             Planet(planet_name='nu 88775 2', host_name='nu 88775', discovery_method='Orbital Brightness Modulation', discovery_year=2019, controversial_flag=True, orbital_period=900.2382868404264, planet_radius=15.264783356742551, planet_mass=3600.515092089112, semi_major_radius=89.54490531922727, eccentricity=0.0275103219976443, equilibrium_temperature=2060.8411532336727, insolation_flux=558.1007524034225),
                             Planet(planet_name='mu 7220 1', host_name='mu 7220', discovery_method='Imaging', discovery_year=2017, controversial_flag=True, orbital_period=877.100268468555, planet_radius=10.941863042666744, planet_mass=4680.223463858876, semi_major_radius=161.40746460985332, eccentricity=0.0681309646194515, equilibrium_temperature=1978.0461138562089, insolation_flux=971.1273850090992),
                             Planet(planet_name='mu 7220 2', host_name='mu 7220', discovery_method='Orbital Brightness Modulation', discovery_year=2022, controversial_flag=True, orbital_period=137.35825747975156, planet_radius=12.95557451729928, planet_mass=9585.330362782282, semi_major_radius=85.29324739918584, eccentricity=0.0857117975778014, equilibrium_temperature=1142.2356590969491, insolation_flux=941.6109410613826),
                             Planet(planet_name='alf-8644 a', host_name='alf-8644', discovery_method='Pulsar Timing', discovery_year=2015, controversial_flag=True, orbital_period=303.9470976387522, planet_radius=13.581884614489358, planet_mass=4351.927263142945, semi_major_radius=129.27603847547917, eccentricity=0.0355229321577781, equilibrium_temperature=937.2139413487332, insolation_flux=2087.079298341052),
                             Planet(planet_name='alf-8644 b', host_name='alf-8644', discovery_method='Transit', discovery_year=2021, controversial_flag=True, orbital_period=544.6928410125677, planet_radius=4.710274142740665, planet_mass=4006.840082453676, semi_major_radius=124.7493062937646, eccentricity=0.0082235550757787, equilibrium_temperature=1387.4822814285192, insolation_flux=1181.8663358960382),
                             Planet(planet_name='EPIC-5568 a', host_name='EPIC-5568', discovery_method='Astrometry', discovery_year=2018, controversial_flag=True, orbital_period=434.70822779578464, planet_radius=18.829821906918617, planet_mass=6660.825293902225, semi_major_radius=85.61368869574389, eccentricity=0.0629522790133215, equilibrium_temperature=493.6744383848522, insolation_flux=573.9614150076267),
                             Planet(planet_name='rho 5073 a', host_name='rho 5073', discovery_method='Pulsar Timing', discovery_year=2016, controversial_flag=True, orbital_period=570.1324508196909, planet_radius=26.34897865306135, planet_mass=6965.455777598903, semi_major_radius=208.0319059356324, eccentricity=0.0114327006798986, equilibrium_temperature=1448.3041171812824, insolation_flux=17.980285071067556),
                             Planet(planet_name='2MASS-7524 a', host_name='2MASS-7524', discovery_method='Astrometry', discovery_year=2017, controversial_flag=True, orbital_period=150.1457457645966, planet_radius=15.64736211033733, planet_mass=7217.150482116653, semi_major_radius=42.6341869908726, eccentricity=0.020774711280382, equilibrium_temperature=469.8443107768314, insolation_flux=904.7707126721951),
                             Planet(planet_name='2MASS 8428 1', host_name='2MASS 8428', discovery_method='Transit Timing Variations', discovery_year=2021, controversial_flag=True, orbital_period=57.13871393274627, planet_radius=6.519911129453395, planet_mass=2763.132084223668, semi_major_radius=52.54795834508463, eccentricity=0.0721200776880685, equilibrium_temperature=1782.433240340816, insolation_flux=69.51050261470868),
                             Planet(planet_name='2MASS 8428 2', host_name='2MASS 8428', discovery_method='Imaging', discovery_year=2020, controversial_flag=True, orbital_period=509.0350609252199, planet_radius=10.011033738636582, planet_mass=2491.056434128092, semi_major_radius=96.57945105974795, eccentricity=0.0755250108587487, equilibrium_temperature=835.3844667718714, insolation_flux=1634.5283980332938),
                             Planet(planet_name='omi 2298 b', host_name='omi 2298', discovery_method='Disk Kinematics', discovery_year=2020, controversial_flag=True, orbital_period=963.9085527348872, planet_radius=13.305769604549546, planet_mass=5186.278116537495, semi_major_radius=151.5944335729398, eccentricity=0.0942946024002424, equilibrium_temperature=1026.6403284847604, insolation_flux=1438.046366898429),
                             Planet(planet_name='ome 9985 b', host_name='ome 9985', discovery_method='Pulsar Timing', discovery_year=2018, controversial_flag=True, orbital_period=983.9747135294464, planet_radius=8.223750696005483, planet_mass=7576.123906464712, semi_major_radius=39.61169765811547, eccentricity=0.0675912377497382, equilibrium_temperature=760.596720610728, insolation_flux=335.1715436863452),
                             Planet(planet_name='alf 7738 a', host_name='alf 7738', discovery_method='Pulsar Timing', discovery_year=2015, controversial_flag=True, orbital_period=467.62786174432864, planet_radius=14.123659153235868, planet_mass=3286.304481918406, semi_major_radius=18.20846585954156, eccentricity=0.0601324104843397, equilibrium_temperature=772.7536762618904, insolation_flux=1038.2424377657412),
                             Planet(planet_name='kap-9452 b', host_name='kap-9452', discovery_method='Pulsation Timing Variations', discovery_year=2020, controversial_flag=True, orbital_period=800.5690127458261, planet_radius=10.449887886875386, planet_mass=7356.524027219688, semi_major_radius=185.78956985145615, eccentricity=0.0507576672391896, equilibrium_temperature=498.8469385224083, insolation_flux=1930.53477835082),
                             Planet(planet_name='psi1 3413 a', host_name='psi1 3413', discovery_method='Transit Timing Variations', discovery_year=2016, controversial_flag=True, orbital_period=677.2095623519192, planet_radius=4.618501404573017, planet_mass=6264.902149517344, semi_major_radius=61.40114878839429, eccentricity=0.0907317529394948, equilibrium_temperature=88.66050147726003, insolation_flux=1142.3851207292068),
                             Planet(planet_name='2MASS 9186 b', host_name='2MASS 9186', discovery_method='Transit', discovery_year=2018, controversial_flag=True, orbital_period=246.08943512852244, planet_radius=4.822875233043634, planet_mass=3658.1168932527344, semi_major_radius=134.73311489430768, eccentricity=0.0850386655462401, equilibrium_temperature=1404.4223381317029, insolation_flux=654.3360887571247),
                             Planet(planet_name='TOI 5695 a', host_name='TOI 5695', discovery_method='Disk Kinematics', discovery_year=2022, controversial_flag=True, orbital_period=392.28029512844176, planet_radius=21.996486206122416, planet_mass=4805.1356079925545, semi_major_radius=63.85988107415062, eccentricity=0.0537182200609785, equilibrium_temperature=2255.406990017933, insolation_flux=673.49295143618),
                             Planet(planet_name='alf 3356 b', host_name='alf 3356', discovery_method='Microlensing', discovery_year=2020, controversial_flag=True, orbital_period=512.8358058975059, planet_radius=10.11097995011791, planet_mass=3533.2112085744675, semi_major_radius=10.347083206398196, eccentricity=0.0817432401586614, equilibrium_temperature=1094.1825053684902, insolation_flux=1425.508551005062),
                             Planet(planet_name='xi-3364 b', host_name='xi-3364', discovery_method='Eclipse Timing Variations', discovery_year=2015, controversial_flag=True, orbital_period=644.0444828833704, planet_radius=14.241885312212368, planet_mass=6453.320262202576, semi_major_radius=9.424475242118262, eccentricity=0.0486870010542453, equilibrium_temperature=1424.6983647271, insolation_flux=831.5918342144895),
                             Planet(planet_name='tau-8123 b', host_name='tau-8123', discovery_method='Microlensing', discovery_year=2019, controversial_flag=True, orbital_period=146.82487519931448, planet_radius=5.116530097204711, planet_mass=7664.322268654663, semi_major_radius=89.0756595057118, eccentricity=0.0534152073806411, equilibrium_temperature=65.5509049870675, insolation_flux=866.8267740962988),
                             Planet(planet_name='HD-8792 b', host_name='HD-8792', discovery_method='Pulsar Timing', discovery_year=2015, controversial_flag=True, orbital_period=1343.2883418219865, planet_radius=9.026689148464072, planet_mass=4388.826549213685, semi_major_radius=182.9883944558212, eccentricity=0.0366906141690273, equilibrium_temperature=992.8749878862496, insolation_flux=1845.4869969659503),
                             Planet(planet_name='gam 7865 a', host_name='gam 7865', discovery_method='Microlensing', discovery_year=2021, controversial_flag=True, orbital_period=140.8309210346061, planet_radius=9.93225522508593, planet_mass=1440.60649027831, semi_major_radius=11.08228694150482, eccentricity=0.0543792903550122, equilibrium_temperature=106.32050802330946, insolation_flux=1216.975822416854),
                             Planet(planet_name='gam 8743 a', host_name='gam 8743', discovery_method='Disk Kinematics', discovery_year=2016, controversial_flag=True, orbital_period=712.1335365754237, planet_radius=21.56597851725587, planet_mass=10079.677902210002, semi_major_radius=134.5620706482415, eccentricity=0.0364163139610588, equilibrium_temperature=1581.718825417435, insolation_flux=1604.7478416918689),
                             Planet(planet_name='gam 8743 b', host_name='gam 8743', discovery_method='Transit Timing Variations', discovery_year=2015, controversial_flag=True, orbital_period=586.2946937955295, planet_radius=11.665656816876416, planet_mass=2504.274781265722, semi_major_radius=4.6347755767888685, eccentricity=0.0540426043884678, equilibrium_temperature=975.8877555925424, insolation_flux=1416.6713293913872),
                             Planet(planet_name='2MASS 8792 1', host_name='2MASS 8792', discovery_method='Microlensing', discovery_year=2017, controversial_flag=True, orbital_period=815.7029551203109, planet_radius=18.32604865026894, planet_mass=5773.040721047353, semi_major_radius=87.58537972566037, eccentricity=0.0811631918062984, equilibrium_temperature=1951.2654840943333, insolation_flux=1490.6920565025046),
                             Planet(planet_name='2MASS 8792 2', host_name='2MASS 8792', discovery_method='Transit Timing Variations', discovery_year=2018, controversial_flag=True, orbital_period=833.8517111338571, planet_radius=11.220791944456575, planet_mass=5738.888058062554, semi_major_radius=132.0404987644856, eccentricity=0.0573618279890868, equilibrium_temperature=2365.444017704047, insolation_flux=1597.1068060981888),
                             Planet(planet_name='omi-9549 2', host_name='omi-9549', discovery_method='Disk Kinematics', discovery_year=2020, controversial_flag=True, orbital_period=859.3762845325359, planet_radius=16.596135149908438, planet_mass=6265.67844388618, semi_major_radius=113.73036159917898, eccentricity=0.0776813725563574, equilibrium_temperature=532.3602702878893, insolation_flux=1410.1723696088084),
                             Planet(planet_name='omi 7112 2', host_name='omi 7112', discovery_method='Microlensing', discovery_year=2022, controversial_flag=True, orbital_period=186.6126201931143, planet_radius=24.128632206184783, planet_mass=6742.824935296941, semi_major_radius=89.10813005374092, eccentricity=0.0563051359987863, equilibrium_temperature=712.9595398826197, insolation_flux=1902.912970412311),
                             Planet(planet_name='gam-444 2', host_name='gam-444', discovery_method='Astrometry', discovery_year=2019, controversial_flag=True, orbital_period=636.5717695063807, planet_radius=6.772419355147023, planet_mass=4389.084796930887, semi_major_radius=82.91195713592013, eccentricity=0.0443066447787657, equilibrium_temperature=2341.3324265687106, insolation_flux=1000.6314389538342),
                             Planet(planet_name='iot-7952 1', host_name='iot-7952', discovery_method='Eclipse Timing Variations', discovery_year=2014, controversial_flag=True, orbital_period=530.1526233007022, planet_radius=8.381579132363736, planet_mass=556.9264482693552, semi_major_radius=81.07603056939206, eccentricity=0.0661051503825004, equilibrium_temperature=996.65897050838, insolation_flux=1883.3603902177333),
                             Planet(planet_name='CoRoT 7998 1', host_name='CoRoT 7998', discovery_method='Transit', discovery_year=2019, controversial_flag=True, orbital_period=742.8133977841699, planet_radius=18.599965319942683, planet_mass=6802.120068798587, semi_major_radius=67.14598634289354, eccentricity=0.0644125843674104, equilibrium_temperature=1335.4349831939448, insolation_flux=673.7101773782758),
                             Planet(planet_name='CoRoT 7998 2', host_name='CoRoT 7998', discovery_method='Pulsation Timing Variations', discovery_year=2019, controversial_flag=True, orbital_period=343.28244721880765, planet_radius=9.68127373938493, planet_mass=2810.0676787381294, semi_major_radius=243.3874420370552, eccentricity=0.0731045351245287, equilibrium_temperature=1775.4275088357406, insolation_flux=667.7215965730552),
                             Planet(planet_name='tau-2333 b', host_name='tau-2333', discovery_method='Transit', discovery_year=2017, controversial_flag=True, orbital_period=321.76706990632164, planet_radius=10.86255036646981, planet_mass=2322.410502769033, semi_major_radius=93.2398837984522, eccentricity=0.0448193017704441, equilibrium_temperature=129.6959015205672, insolation_flux=796.0003758455682),
                             Planet(planet_name='nu 9705 2', host_name='nu 9705', discovery_method='Transit Timing Variations', discovery_year=2016, controversial_flag=True, orbital_period=656.9389841901922, planet_radius=17.10630306948789, planet_mass=3138.9649854317777, semi_major_radius=93.58002824090218, eccentricity=0.0406690729287195, equilibrium_temperature=826.1968923839843, insolation_flux=939.518586958874),
                             Planet(planet_name='xi 9043 1', host_name='xi 9043', discovery_method='Astrometry', discovery_year=2019, controversial_flag=True, orbital_period=276.4331290805021, planet_radius=13.516786175199204, planet_mass=6202.1662518540925, semi_major_radius=107.3756586431804, eccentricity=0.0176588289306225, equilibrium_temperature=1274.751578470915, insolation_flux=1807.2820911970323),
                             Planet(planet_name='GJ 62522 2', host_name='GJ 62522', discovery_method='Pulsation Timing Variations', discovery_year=2019, controversial_flag=True, orbital_period=591.6662837729032, planet_radius=2.5769358490328056, planet_mass=2652.452123852501, semi_major_radius=163.80938505398188, eccentricity=0.0620172487410043, equilibrium_temperature=1349.903744653087, insolation_flux=1086.7725895488993),
                             Planet(planet_name='EPIC 1331 2', host_name='EPIC 1331', discovery_method='Eclipse Timing Variations', discovery_year=2016, controversial_flag=True, orbital_period=403.0017669995712, planet_radius=3.1332856381900243, planet_mass=5861.349859676194, semi_major_radius=88.7881480092466, eccentricity=0.0057944814253035, equilibrium_temperature=976.3329398856496, insolation_flux=1714.956708887834),
                             Planet(planet_name='Kepler 8060 1', host_name='Kepler 8060', discovery_method='Imaging', discovery_year=2018, controversial_flag=True, orbital_period=284.7269334462812, planet_radius=5.161550257074002, planet_mass=3499.392482768998, semi_major_radius=204.2533089876109, eccentricity=0.0665528137125254, equilibrium_temperature=1180.3455287640631, insolation_flux=448.5784168747373),
                             Planet(planet_name='nu 8250 1', host_name='nu 8250', discovery_method='Astrometry', discovery_year=2017, controversial_flag=True, orbital_period=788.1423637236289, planet_radius=7.398925743772148, planet_mass=9422.057488169878, semi_major_radius=28.242433569709878, eccentricity=0.0631935809657332, equilibrium_temperature=1118.5155330645166, insolation_flux=432.35188124850345),
                             Planet(planet_name='mu2-6826 2', host_name='mu2-6826', discovery_method='Pulsar Timing', discovery_year=2017, controversial_flag=True, orbital_period=525.3984297966949, planet_radius=28.248612462943825, planet_mass=4028.0087691192407, semi_major_radius=136.21183948714506, eccentricity=0.0286789910491689, equilibrium_temperature=1525.3127600971054, insolation_flux=1120.3621994879663),
                             Planet(planet_name='bet-3249 1', host_name='bet-3249', discovery_method='Disk Kinematics', discovery_year=2016, controversial_flag=True, orbital_period=787.8341859702505, planet_radius=17.418110462770656, planet_mass=4797.051739771537, semi_major_radius=148.9358468568409, eccentricity=0.0151147543977422, equilibrium_temperature=1243.8921922604018, insolation_flux=495.8306739806019),
                             Planet(planet_name='gam1-7063 1', host_name='gam1-7063', discovery_method='Disk Kinematics', discovery_year=2015, controversial_flag=True, orbital_period=357.9554337884968, planet_radius=16.808976795333905, planet_mass=1695.727033384842, semi_major_radius=112.73241958678288, eccentricity=0.0251285424788092, equilibrium_temperature=1962.9163945636733, insolation_flux=114.58584743046517),
                             Planet(planet_name='GJ-8902 1', host_name='GJ-8902', discovery_method='Disk Kinematics', discovery_year=2019, controversial_flag=True, orbital_period=302.0312160936952, planet_radius=14.323857335245703, planet_mass=6718.059917539018, semi_major_radius=54.03732953588903, eccentricity=0.0462843283890902, equilibrium_temperature=1753.2055544661855, insolation_flux=254.49858816162416),
                             Planet(planet_name='iot-3440 b', host_name='iot-3440', discovery_method='Transit Timing Variations', discovery_year=2019, controversial_flag=True, orbital_period=191.82327818716624, planet_radius=9.36353498739548, planet_mass=1254.4636209226987, semi_major_radius=70.74790378149578, eccentricity=0.0710274903232883, equilibrium_temperature=2471.0475150558013, insolation_flux=1628.0717247100329),
                             Planet(planet_name='WASP-5020 1', host_name='WASP-5020', discovery_method='Microlensing', discovery_year=2019, controversial_flag=True, orbital_period=593.4968491007667, planet_radius=10.23761839676358, planet_mass=4694.177233274117, semi_major_radius=64.48029925854473, eccentricity=0.0589240750974881, equilibrium_temperature=423.795333659491, insolation_flux=1211.6416410626),
                             Planet(planet_name='WASP 2183 a', host_name='WASP 2183', discovery_method='Disk Kinematics', discovery_year=2020, controversial_flag=True, orbital_period=849.8872694708929, planet_radius=14.511326280186044, planet_mass=2726.4214825747918, semi_major_radius=137.06135075671716, eccentricity=0.0196266402747552, equilibrium_temperature=948.743274354488, insolation_flux=2712.4498505915863),
                             Planet(planet_name='xi-7929 b', host_name='xi-7929', discovery_method='Pulsar Timing', discovery_year=2019, controversial_flag=True, orbital_period=410.7881929611221, planet_radius=6.721629732231822, planet_mass=7036.914375081748, semi_major_radius=119.12026567095228, eccentricity=0.0271458281458849, equilibrium_temperature=908.5248730258578, insolation_flux=573.8843596515627),
                             Planet(planet_name='psi1 5125 2', host_name='psi1 5125', discovery_method='Astrometry', discovery_year=2020, controversial_flag=True, orbital_period=54.51873275591231, planet_radius=25.121240106273227, planet_mass=924.351956697496, semi_major_radius=137.28315764701486, eccentricity=0.0473150320626147, equilibrium_temperature=1343.517036210211, insolation_flux=1928.8791831695848),
                             Planet(planet_name='WASP-88 b', host_name='WASP-88', discovery_method='Radial Velocity', discovery_year=2018, controversial_flag=True, orbital_period=553.7613836208031, planet_radius=21.11845640486564, planet_mass=4991.617497713028, semi_major_radius=104.71515549312092, eccentricity=0.0574743530041614, equilibrium_temperature=2399.4478605729573, insolation_flux=386.1957157913437),
                             Planet(planet_name='BD-2946 b', host_name='BD-2946', discovery_method='Astrometry', discovery_year=2019, controversial_flag=True, orbital_period=178.08872490436664, planet_radius=10.558097091181544, planet_mass=5251.64111745434, semi_major_radius=2.83215206915429, eccentricity=0.0274297379103554, equilibrium_temperature=1249.131296851482, insolation_flux=1205.3777707370773),
                             Planet(planet_name='psi1-2236 2', host_name='psi1-2236', discovery_method='Eclipse Timing Variations', discovery_year=2020, controversial_flag=True, orbital_period=30.86820050728346, planet_radius=27.76569072808605, planet_mass=5866.952847548633, semi_major_radius=199.16595454315467, eccentricity=0.0362904248154441, equilibrium_temperature=1237.464955300887, insolation_flux=1286.7379713062544),
                             Planet(planet_name='nu 8621 b', host_name='nu 8621', discovery_method='Transit Timing Variations', discovery_year=2019, controversial_flag=True, orbital_period=357.2973151459813, planet_radius=9.928879429728434, planet_mass=3448.1735023788924, semi_major_radius=53.91423885666123, eccentricity=0.0280244660317614, equilibrium_temperature=758.1467943679718, insolation_flux=755.0970241140924),
                             Planet(planet_name='eps 728 1', host_name='eps 728', discovery_method='Imaging', discovery_year=2017, controversial_flag=True, orbital_period=838.2323365088814, planet_radius=17.564775507768502, planet_mass=412.1139794797464, semi_major_radius=67.470973067208, eccentricity=0.0745615740365659, equilibrium_temperature=763.1507619243832, insolation_flux=1480.5993783975507),
                             Planet(planet_name='eps 728 2', host_name='eps 728', discovery_method='Imaging', discovery_year=2018, controversial_flag=True, orbital_period=694.3489826633308, planet_radius=4.294598980437378, planet_mass=5306.188727476043, semi_major_radius=131.26402403268224, eccentricity=0.0549035185888598, equilibrium_temperature=1470.0712186044802, insolation_flux=302.8316000870228),
                             Planet(planet_name='ome 6577 a', host_name='ome 6577', discovery_method='Pulsation Timing Variations', discovery_year=2019, controversial_flag=True, orbital_period=652.7788772085446, planet_radius=16.639676004582125, planet_mass=3149.54586962393, semi_major_radius=79.72991890078191, eccentricity=0.0263414812077779, equilibrium_temperature=1445.4050143311642, insolation_flux=934.0870054339624),
                             Planet(planet_name='bet 5923 b', host_name='bet 5923', discovery_method='Radial Velocity', discovery_year=2018, controversial_flag=True, orbital_period=519.8765584679498, planet_radius=14.092056018457091, planet_mass=9626.699270446912, semi_major_radius=47.8497800135638, eccentricity=0.0305202161708651, equilibrium_temperature=1374.4186395615368, insolation_flux=918.0049426456555),
                             Planet(planet_name='CoRoT-8123 2', host_name='CoRoT-8123', discovery_method='Disk Kinematics', discovery_year=2019, controversial_flag=True, orbital_period=549.7443674568224, planet_radius=6.009150038510151, planet_mass=8415.685251700605, semi_major_radius=89.30567621336064, eccentricity=0.0611420412832389, equilibrium_temperature=1076.2051174116173, insolation_flux=999.4983327651622),
                             Planet(planet_name='tau-6969 b', host_name='tau-6969', discovery_method='Pulsar Timing', discovery_year=2021, controversial_flag=True, orbital_period=911.77381984989, planet_radius=10.026740983617492, planet_mass=1779.3687291136955, semi_major_radius=56.09486251028333, eccentricity=0.044150428397841, equilibrium_temperature=176.1062807060904, insolation_flux=991.9885119308144),
                             Planet(planet_name='ups-8501 2', host_name='ups-8501', discovery_method='Transit Timing Variations', discovery_year=2018, controversial_flag=True, orbital_period=704.2957793757869, planet_radius=4.986824632111169, planet_mass=5110.789736399246, semi_major_radius=117.12315942976169, eccentricity=0.0224985423920051, equilibrium_temperature=1259.4833573418302, insolation_flux=1057.5680506947606),
                             Planet(planet_name='psi1 1082 b', host_name='psi1 1082', discovery_method='Disk Kinematics', discovery_year=2017, controversial_flag=True, orbital_period=867.2916631412809, planet_radius=1.3233873758274228, planet_mass=4408.435562057717, semi_major_radius=168.52655306847785, eccentricity=0.0748349762808003, equilibrium_temperature=367.73867262481417, insolation_flux=80.80968207813976),
                             Planet(planet_name='GJ 3743 2', host_name='GJ 3743', discovery_method='Orbital Brightness Modulation', discovery_year=2018, controversial_flag=True, orbital_period=325.7510834335862, planet_radius=6.291779434577316, planet_mass=8087.772895848815, semi_major_radius=166.36811441329016, eccentricity=0.010859284118013, equilibrium_temperature=1634.932295469055, insolation_flux=746.0079833922314),
                             Planet(planet_name='EPIC 6953 1', host_name='EPIC 6953', discovery_method='Pulsation Timing Variations', discovery_year=2021, controversial_flag=True, orbital_period=782.7896507075162, planet_radius=3.165193327152542, planet_mass=7744.300886911292, semi_major_radius=152.7698506567319, eccentricity=0.0358360512905148, equilibrium_temperature=1140.793732877143, insolation_flux=925.9439067605006),
                             Planet(planet_name='GJ-3275 1', host_name='GJ-3275', discovery_method='Transit', discovery_year=2021, controversial_flag=True, orbital_period=596.3010292917895, planet_radius=20.95639054084832, planet_mass=5905.722963966452, semi_major_radius=105.52956428574922, eccentricity=0.0580540683588574, equilibrium_temperature=1392.1460661127162, insolation_flux=1293.3972204660192),
                             Planet(planet_name='GJ-3275 2', host_name='GJ-3275', discovery_method='Transit', discovery_year=2017, controversial_flag=True, orbital_period=191.66080022192224, planet_radius=1.0607396274567122, planet_mass=6223.34647595042, semi_major_radius=168.0980786179323, eccentricity=0.0624983313070595, equilibrium_temperature=687.4295834774684, insolation_flux=1395.2737755248972),
                             Planet(planet_name='Kepler 5927 2', host_name='Kepler 5927', discovery_method='Pulsar Timing', discovery_year=2016, controversial_flag=True, orbital_period=339.5614979040448, planet_radius=18.306527456193333, planet_mass=4710.539166506468, semi_major_radius=62.64236598610663, eccentricity=0.0494102216696081, equilibrium_temperature=1286.5084778706696, insolation_flux=1416.0333803740025),
                             Planet(planet_name='ups 3249 a', host_name='ups 3249', discovery_method='Transit', discovery_year=2022, controversial_flag=True, orbital_period=825.0984264649848, planet_radius=13.686633926556672, planet_mass=5351.239218146949, semi_major_radius=111.05684690404442, eccentricity=0.0300778271561352, equilibrium_temperature=1596.8342032351366, insolation_flux=310.4760341613555),
                             Planet(planet_name='alf 8449 b', host_name='alf 8449', discovery_method='Transit', discovery_year=2018, controversial_flag=True, orbital_period=512.5460458823453, planet_radius=8.469394497623455, planet_mass=5620.601261754834, semi_major_radius=181.9225188601164, eccentricity=0.0521931993565697, equilibrium_temperature=1194.0442163666175, insolation_flux=1189.1913388994578),
                             Planet(planet_name='TOI-9556 2', host_name='TOI-9556', discovery_method='Orbital Brightness Modulation', discovery_year=2016, controversial_flag=True, orbital_period=449.1069441559755, planet_radius=16.563589566779253, planet_mass=3306.344795996508, semi_major_radius=160.10202666699166, eccentricity=0.0080194794843188, equilibrium_temperature=1086.9244170388922, insolation_flux=494.387131393866),
                             Planet(planet_name='alf 3531 1', host_name='alf 3531', discovery_method='Disk Kinematics', discovery_year=2017, controversial_flag=True, orbital_period=215.02830877781685, planet_radius=9.06615374909347, planet_mass=9295.80244354142, semi_major_radius=56.01532381825014, eccentricity=0.049507544490314, equilibrium_temperature=1285.8741827073443, insolation_flux=977.9334311443916),
                             Planet(planet_name='BD 27652 1', host_name='BD 27652', discovery_method='Disk Kinematics', discovery_year=2020, controversial_flag=True, orbital_period=601.7748224929948, planet_radius=19.352903556513567, planet_mass=5313.303274034671, semi_major_radius=8.5262928421581, eccentricity=0.0830044549175929, equilibrium_temperature=1993.787800847445, insolation_flux=1587.6128065804537),
                             Planet(planet_name='HD-4335 2', host_name='HD-4335', discovery_method='Orbital Brightness Modulation', discovery_year=2017, controversial_flag=True, orbital_period=829.0771241898658, planet_radius=4.568968176739987, planet_mass=3626.88641764785, semi_major_radius=284.38152996290296, eccentricity=0.0248776997631765, equilibrium_temperature=1253.773995229588, insolation_flux=1181.6538676407276),
                             Planet(planet_name='nu 626 2', host_name='nu 626', discovery_method='Microlensing', discovery_year=2014, controversial_flag=True, orbital_period=851.6819821371778, planet_radius=11.84764183361473, planet_mass=8814.554787746989, semi_major_radius=47.98152269638538, eccentricity=0.0898206366870946, equilibrium_temperature=1186.475045614663, insolation_flux=744.9268530697199),
                             Planet(planet_name='BD-96147 a', host_name='BD-96147', discovery_method='Transit Timing Variations', discovery_year=2014, controversial_flag=True, orbital_period=564.5148726280993, planet_radius=10.45712479489675, planet_mass=2100.607559166328, semi_major_radius=112.3630354482609, eccentricity=0.069220459499787, equilibrium_temperature=1122.5747532413266, insolation_flux=2069.8844328857663),
                             Planet(planet_name='BD-96147 b', host_name='BD-96147', discovery_method='Eclipse Timing Variations', discovery_year=2016, controversial_flag=True, orbital_period=386.1887048223904, planet_radius=10.37954121410754, planet_mass=6803.527522291737, semi_major_radius=102.07348670997034, eccentricity=0.0309843396876475, equilibrium_temperature=950.858992159473, insolation_flux=1098.9003751624446),
                             Planet(planet_name='BD 6687 b', host_name='BD 6687', discovery_method='Disk Kinematics', discovery_year=2019, controversial_flag=True, orbital_period=495.19878879319054, planet_radius=21.69895807400356, planet_mass=6888.685533713617, semi_major_radius=61.49059762509387, eccentricity=0.0552300782257706, equilibrium_temperature=1328.5723961153024, insolation_flux=1153.835602585768),
                             Planet(planet_name='EPIC 8487 a', host_name='EPIC 8487', discovery_method='Imaging', discovery_year=2015, controversial_flag=True, orbital_period=662.0455507880326, planet_radius=19.00555689893632, planet_mass=7401.838658442676, semi_major_radius=133.12786059647294, eccentricity=0.0095046441638162, equilibrium_temperature=1318.0562240999957, insolation_flux=765.4742418410993),
                             Planet(planet_name='EPIC 8487 b', host_name='EPIC 8487', discovery_method='Eclipse Timing Variations', discovery_year=2019, controversial_flag=True, orbital_period=948.699036001909, planet_radius=12.18932102012034, planet_mass=6704.309287532648, semi_major_radius=12.973913393916432, eccentricity=0.0643093958732519, equilibrium_temperature=2141.5942230207584, insolation_flux=981.4759925075832),
                             Planet(planet_name='alf-5020 1', host_name='alf-5020', discovery_method='Eclipse Timing Variations', discovery_year=2018, controversial_flag=True, orbital_period=134.75696211419478, planet_radius=18.955097669762807, planet_mass=7047.643387815492, semi_major_radius=169.92758021670642, eccentricity=0.0392282576805462, equilibrium_temperature=234.51137724949285, insolation_flux=1116.064590034719),
                             Planet(planet_name='CoRoT-1931 1', host_name='CoRoT-1931', discovery_method='Transit', discovery_year=2021, controversial_flag=True, orbital_period=269.9514605854189, planet_radius=8.531941067706308, planet_mass=1911.483463196764, semi_major_radius=178.8199318407368, eccentricity=0.0814868695849914, equilibrium_temperature=512.6169524780044, insolation_flux=862.594975044429),
                             Planet(planet_name='alf-5 b', host_name='alf-5', discovery_method='Eclipse Timing Variations', discovery_year=2015, controversial_flag=True, orbital_period=522.6651964885341, planet_radius=25.27160967709036, planet_mass=5609.525261310315, semi_major_radius=86.9482866522371, eccentricity=0.0319705031380239, equilibrium_temperature=1536.8009190888251, insolation_flux=665.1578798160132),
                             Planet(planet_name='nu-6290 b', host_name='nu-6290', discovery_method='Orbital Brightness Modulation', discovery_year=2018, controversial_flag=True, orbital_period=390.27999513313046, planet_radius=18.489995284953896, planet_mass=4710.087569365871, semi_major_radius=127.37669748713552, eccentricity=0.121106948342815, equilibrium_temperature=1277.0392717752195, insolation_flux=758.2581537276496)],
                     'q15': [Planet(planet_name='alf-9043 4', host_name='alf-9043', discovery_method='Pulsar Timing', discovery_year=2014, controversial_flag=True, orbital_period=476.8835247686909, planet_radius=12.097940244957826, planet_mass=4133.146333216903, semi_major_radius=73.38151039360892, eccentricity=0.10511862715074291, equilibrium_temperature=889.0066625073698, insolation_flux=2333.5222209993344),
                             Planet(planet_name='mu2 7869 a', host_name='mu2 7869', discovery_method='Disk Kinematics', discovery_year=2016, controversial_flag=False, orbital_period=788.2847691094858, planet_radius=18.09053934104277, planet_mass=4260.560680374517, semi_major_radius=149.21945969135493, eccentricity=0.0605035533172124, equilibrium_temperature=1614.4163357801153, insolation_flux=1244.5543282059116),
                             Planet(planet_name='mu2 7869 b', host_name='mu2 7869', discovery_method='Astrometry', discovery_year=2019, controversial_flag=False, orbital_period=365.78501752387945, planet_radius=4.751093288421124, planet_mass=2351.878658865369, semi_major_radius=169.87734552891385, eccentricity=0.03776034252480265, equilibrium_temperature=303.8778407006555, insolation_flux=1641.0593938350278),
                             Planet(planet_name='mu2 7869 c', host_name='mu2 7869', discovery_method='Radial Velocity', discovery_year=2017, controversial_flag=False, orbital_period=812.8754347464487, planet_radius=16.75220715502253, planet_mass=5422.922984080339, semi_major_radius=21.9432121734732, eccentricity=0.13437716286536966, equilibrium_temperature=247.8823224359977, insolation_flux=1660.606842568487),
                             Planet(planet_name='mu2 7869 d', host_name='mu2 7869', discovery_method='Pulsar Timing', discovery_year=2022, controversial_flag=True, orbital_period=387.0816665771646, planet_radius=15.899041292942389, planet_mass=8635.517689993661, semi_major_radius=39.95903441584854, eccentricity=0.05273295047511027, equilibrium_temperature=773.1839369741388, insolation_flux=1390.288427705017)],
                     'q16': [],
                     'q17': 0,
                     'q18': Star(spectral_type='G', stellar_effective_temperature=4259.152657715636, stellar_radius=22.44876648040157, stellar_mass=4.067306660928754, stellar_luminosity=1.5868395608693022, stellar_surface_gravity=3.6737996609343466, stellar_age=9.335578685244542)}
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
