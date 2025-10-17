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
                     'q5': Star(spectral_type='W4.75', stellar_effective_temperature=4871.497146309018, stellar_radius=52.38674546050555, stellar_mass=2.4787360858790186, stellar_luminosity=-1.8370843229267515, stellar_surface_gravity=5.396080912979088, stellar_age=3.2),
                     'q6': Star(spectral_type='K3.75II', stellar_effective_temperature=8326.502192916454, stellar_radius=18.50984892973001, stellar_mass=2.589644264779813, stellar_luminosity=-0.8437803961935932, stellar_surface_gravity=1.745276254118413, stellar_age=3.2),
                     'q7': -0.21105565658514247,
                     'q8': 13.800000000000022,
                     'q9': 5155.647965197843,
                     'q10': 'ups-4347',
                     'q11': 10.791572989838325,
                     'Planet': Planet(planet_name='Jupiter', host_name='Sun', discovery_method='Imaging', discovery_year=1610, controversial_flag=False, orbital_period=4333.0, planet_radius=11.209, planet_mass=317.828, semi_major_radius=5.2038, eccentricity=0.0489, equilibrium_temperature=110, insolation_flux=0.0345),
                     'q12': Planet(planet_name='mu-8507 a', host_name='mu-8507', discovery_method='Disk Kinematics', discovery_year=2019, controversial_flag=False, orbital_period=416.8034141791728, planet_radius=13.693014741742957, planet_mass=4253.954366383935, semi_major_radius=172.03206733868313, eccentricity=0.01896037562118447, equilibrium_temperature=1853.8927547233375, insolation_flux=397.8355410795634),
                     'q13': [Planet(planet_name='ups 6602 a', host_name='ups 6602', discovery_method='Disk Kinematics', discovery_year=2017, controversial_flag=False, orbital_period=449.25146879102147, planet_radius=12.859754255589872, planet_mass=5504.085337695487, semi_major_radius=52.245657950725835, eccentricity=0.04981535308968937, equilibrium_temperature=582.3423656153738, insolation_flux=1473.4524621095254),
                             Planet(planet_name='kap-3068 a', host_name='kap-3068', discovery_method='Imaging', discovery_year=2018, controversial_flag=False, orbital_period=208.9501405510204, planet_radius=12.088996219696948, planet_mass=9439.574566784264, semi_major_radius=24.226372005523473, eccentricity=0.07901701225718245, equilibrium_temperature=1187.3178878398517, insolation_flux=1204.1647606304036),
                             Planet(planet_name='ome-9098 1', host_name='ome-9098', discovery_method='Orbital Brightness Modulation', discovery_year=2016, controversial_flag=False, orbital_period=555.6324429227036, planet_radius=8.139615577022175, planet_mass=6748.7828065873055, semi_major_radius=125.69605801555663, eccentricity=0.041535107437934135, equilibrium_temperature=1203.9385701209321, insolation_flux=943.6926924637401),
                             Planet(planet_name='HD 4423 a', host_name='HD 4423', discovery_method='Microlensing', discovery_year=2019, controversial_flag=True, orbital_period=214.25546515344848, planet_radius=12.852237880031561, planet_mass=4174.2832116523605, semi_major_radius=123.3218338910946, eccentricity=0.09312362048687002, equilibrium_temperature=1916.5749726648544, insolation_flux=1630.9290559220376),
                             Planet(planet_name='gam 9169 a', host_name='gam 9169', discovery_method='Imaging', discovery_year=2018, controversial_flag=False, orbital_period=216.14038151179193, planet_radius=10.772631406333701, planet_mass=9269.880150734938, semi_major_radius=47.20394800706773, eccentricity=0.043407180028280694, equilibrium_temperature=447.83402328297234, insolation_flux=755.6203863647077)],
                     'q14': [Planet(planet_name='BD 7817 b', host_name='BD 7817', discovery_method='Disk Kinematics', discovery_year=2018, controversial_flag=True, orbital_period=481.0267347755233, planet_radius=6.143107364377893, planet_mass=5146.172551105796, semi_major_radius=121.38169525202233, eccentricity=0.028213090147972845, equilibrium_temperature=1689.6904334127291, insolation_flux=1198.418862938081),
                             Planet(planet_name='omi-8507 1', host_name='omi-8507', discovery_method='Imaging', discovery_year=2018, controversial_flag=True, orbital_period=138.0843903247162, planet_radius=11.739991664561083, planet_mass=6645.754803805837, semi_major_radius=39.11696555975797, eccentricity=0.04687968624550129, equilibrium_temperature=1004.6063353592251, insolation_flux=759.4586313422924),
                             Planet(planet_name='omi-8507 2', host_name='omi-8507', discovery_method='Orbital Brightness Modulation', discovery_year=2016, controversial_flag=True, orbital_period=206.0822358019089, planet_radius=20.213556668396713, planet_mass=8656.1566433129, semi_major_radius=193.2656192232684, eccentricity=0.034884236048112895, equilibrium_temperature=1033.001328326735, insolation_flux=1496.538391334258),
                             Planet(planet_name='rho-2705 1', host_name='rho-2705', discovery_method='Transit Timing Variations', discovery_year=2018, controversial_flag=True, orbital_period=1136.2421987823677, planet_radius=12.397799710010917, planet_mass=8304.855683829292, semi_major_radius=125.73607512920412, eccentricity=0.04935528715927526, equilibrium_temperature=1281.3333478474494, insolation_flux=1404.9421052860719),
                             Planet(planet_name='gam-487 1', host_name='gam-487', discovery_method='Microlensing', discovery_year=2018, controversial_flag=True, orbital_period=50.822904322943884, planet_radius=20.399741186967397, planet_mass=10110.697944634321, semi_major_radius=136.51688170246882, eccentricity=0.06773497788659483, equilibrium_temperature=1102.5462416649434, insolation_flux=1468.1222360356294),
                             Planet(planet_name='mu 2716 2', host_name='mu 2716', discovery_method='Eclipse Timing Variations', discovery_year=2022, controversial_flag=True, orbital_period=439.80409973380955, planet_radius=13.314957460098714, planet_mass=9451.92428836527, semi_major_radius=149.47629322377074, eccentricity=0.060374616238444874, equilibrium_temperature=2195.63522225006, insolation_flux=1409.9850701651217),
                             Planet(planet_name='GJ-9585 2', host_name='GJ-9585', discovery_method='Pulsation Timing Variations', discovery_year=2018, controversial_flag=True, orbital_period=358.89827817469677, planet_radius=8.595862271528066, planet_mass=9055.59674782677, semi_major_radius=111.95038594587785, eccentricity=0.03819780619123251, equilibrium_temperature=1858.8701350637414, insolation_flux=830.1266105106338),
                             Planet(planet_name='BD 3927 b', host_name='BD 3927', discovery_method='Transit Timing Variations', discovery_year=2017, controversial_flag=True, orbital_period=312.4528474224062, planet_radius=22.80873468723687, planet_mass=2947.1938085864836, semi_major_radius=150.87584197578764, eccentricity=0.004407081983410027, equilibrium_temperature=980.5550982733997, insolation_flux=72.67364349813306),
                             Planet(planet_name='gam-19 2', host_name='gam-19', discovery_method='Pulsation Timing Variations', discovery_year=2018, controversial_flag=True, orbital_period=1262.0478329828525, planet_radius=7.435313456420358, planet_mass=9632.337181282684, semi_major_radius=182.588435064484, eccentricity=0.06387183084260241, equilibrium_temperature=1908.885718025983, insolation_flux=1255.3177775785268),
                             Planet(planet_name='psi1 9408 a', host_name='psi1 9408', discovery_method='Orbital Brightness Modulation', discovery_year=2017, controversial_flag=True, orbital_period=75.06083282189843, planet_radius=6.205095390274182, planet_mass=5343.5793948077735, semi_major_radius=162.14540713002282, eccentricity=0.0439791311663178, equilibrium_temperature=1187.3765547855817, insolation_flux=2162.3365368558398),
                             Planet(planet_name='HD-5564 a', host_name='HD-5564', discovery_method='Astrometry', discovery_year=2020, controversial_flag=True, orbital_period=160.8056522786298, planet_radius=12.381785487599958, planet_mass=11149.698167683397, semi_major_radius=69.17319632270636, eccentricity=0.008068699511069768, equilibrium_temperature=146.76258543803226, insolation_flux=494.2537622564572),
                             Planet(planet_name='nu-5498 a', host_name='nu-5498', discovery_method='Disk Kinematics', discovery_year=2022, controversial_flag=True, orbital_period=330.33457420772015, planet_radius=14.795538658741204, planet_mass=1906.7443407106161, semi_major_radius=61.24222455888701, eccentricity=0.06750687144618418, equilibrium_temperature=1375.2370534532179, insolation_flux=1230.6860210183831),
                             Planet(planet_name='mu-6037 1', host_name='mu-6037', discovery_method='Microlensing', discovery_year=2021, controversial_flag=True, orbital_period=382.1107317146417, planet_radius=15.490568202412236, planet_mass=8758.626993334943, semi_major_radius=182.25911450694366, eccentricity=0.030235758437727252, equilibrium_temperature=1167.2744176255628, insolation_flux=1434.5317645678322),
                             Planet(planet_name='ups-5415 2', host_name='ups-5415', discovery_method='Disk Kinematics', discovery_year=2018, controversial_flag=True, orbital_period=95.46831030961982, planet_radius=0.3124466559106214, planet_mass=4763.653451598389, semi_major_radius=137.27187931694843, eccentricity=0.07712167549960962, equilibrium_temperature=1520.7956095878524, insolation_flux=871.4102272638288),
                             Planet(planet_name='2MASS-8589 1', host_name='2MASS-8589', discovery_method='Eclipse Timing Variations', discovery_year=2020, controversial_flag=True, orbital_period=547.1914101018269, planet_radius=2.2051156128754172, planet_mass=1405.1929013742356, semi_major_radius=63.91316446754351, eccentricity=0.05917633993847775, equilibrium_temperature=395.2769559460395, insolation_flux=1003.1398315793369),
                             Planet(planet_name='EPIC-4901 a', host_name='EPIC-4901', discovery_method='Pulsation Timing Variations', discovery_year=2018, controversial_flag=True, orbital_period=256.4706699171004, planet_radius=13.882942910539956, planet_mass=3485.8324881072554, semi_major_radius=109.2718389219759, eccentricity=0.015015999368151942, equilibrium_temperature=1001.7219352068548, insolation_flux=233.64096790553845),
                             Planet(planet_name='EPIC-4901 b', host_name='EPIC-4901', discovery_method='Transit Timing Variations', discovery_year=2015, controversial_flag=True, orbital_period=90.47536134080627, planet_radius=18.57579311197029, planet_mass=3744.043184221987, semi_major_radius=107.83654727642404, eccentricity=0.07731782320354785, equilibrium_temperature=1589.3416526048538, insolation_flux=548.2203521605815),
                             Planet(planet_name='Kepler-3697 1', host_name='Kepler-3697', discovery_method='Astrometry', discovery_year=2020, controversial_flag=True, orbital_period=509.84265073632884, planet_radius=24.59994065571836, planet_mass=6386.532714637334, semi_major_radius=161.3802985337157, eccentricity=0.019278649962693184, equilibrium_temperature=1022.0658105986087, insolation_flux=1754.8876002286188),
                             Planet(planet_name='TOI 8975 a', host_name='TOI 8975', discovery_method='Imaging', discovery_year=2019, controversial_flag=True, orbital_period=1221.8844017036636, planet_radius=1.1441054963925215, planet_mass=1406.5268276574725, semi_major_radius=36.647233650291646, eccentricity=0.08122462052199499, equilibrium_temperature=2469.6474490782957, insolation_flux=1969.704247348388),
                             Planet(planet_name='alf 1964 1', host_name='alf 1964', discovery_method='Astrometry', discovery_year=2019, controversial_flag=True, orbital_period=530.0650087078722, planet_radius=4.615218158938432, planet_mass=4003.2140944760927, semi_major_radius=78.66255660203704, eccentricity=0.07248760869474807, equilibrium_temperature=911.9455760631519, insolation_flux=1153.8177407482722),
                             Planet(planet_name='mu 451 2', host_name='mu 451', discovery_method='Transit', discovery_year=2020, controversial_flag=True, orbital_period=69.64497246295139, planet_radius=11.114462956427948, planet_mass=6298.720528845912, semi_major_radius=58.000081196401034, eccentricity=0.07815899360743075, equilibrium_temperature=725.0411225461029, insolation_flux=735.413935545388),
                             Planet(planet_name='TOI 5994 1', host_name='TOI 5994', discovery_method='Transit', discovery_year=2022, controversial_flag=True, orbital_period=400.7334684398493, planet_radius=2.0333671523568064, planet_mass=5138.308425965012, semi_major_radius=60.95833372181586, eccentricity=0.04616043176404069, equilibrium_temperature=706.5292493066813, insolation_flux=667.889049583865),
                             Planet(planet_name='alf-2725 b', host_name='alf-2725', discovery_method='Pulsation Timing Variations', discovery_year=2021, controversial_flag=True, orbital_period=802.2016735313688, planet_radius=3.2386666137875757, planet_mass=5549.657822987125, semi_major_radius=42.43656385655062, eccentricity=0.04208792545254237, equilibrium_temperature=1228.2342271187117, insolation_flux=1495.1915839563515),
                             Planet(planet_name='mu2-8057 b', host_name='mu2-8057', discovery_method='Radial Velocity', discovery_year=2016, controversial_flag=True, orbital_period=701.8406399444814, planet_radius=11.146285123571339, planet_mass=5860.959846946666, semi_major_radius=75.49989788618899, eccentricity=0.03978380916917872, equilibrium_temperature=1388.6708625909755, insolation_flux=1701.1611454588096),
                             Planet(planet_name='gam1 5928 b', host_name='gam1 5928', discovery_method='Pulsation Timing Variations', discovery_year=2019, controversial_flag=True, orbital_period=315.1490778316678, planet_radius=3.3327912315325348, planet_mass=3587.5000696856937, semi_major_radius=121.54265754279191, eccentricity=0.062454484275254574, equilibrium_temperature=980.5934183143526, insolation_flux=930.4879721868755),
                             Planet(planet_name='ups-9395 1', host_name='ups-9395', discovery_method='Disk Kinematics', discovery_year=2019, controversial_flag=True, orbital_period=695.1288846779669, planet_radius=14.980585077610257, planet_mass=4429.675689666606, semi_major_radius=17.35870576056307, eccentricity=0.07823155141430446, equilibrium_temperature=672.7183006711874, insolation_flux=1151.5703614128456),
                             Planet(planet_name='nu 2623 a', host_name='nu 2623', discovery_method='Transit', discovery_year=2020, controversial_flag=True, orbital_period=689.2921072031594, planet_radius=5.97608596628305, planet_mass=701.9823131513695, semi_major_radius=11.33985653880643, eccentricity=0.02610614972239633, equilibrium_temperature=41.36476726110709, insolation_flux=484.9909578443652),
                             Planet(planet_name='xi 5778 a', host_name='xi 5778', discovery_method='Pulsation Timing Variations', discovery_year=2017, controversial_flag=True, orbital_period=303.7324563790345, planet_radius=6.4563561705764245, planet_mass=5939.655465570652, semi_major_radius=139.90855994370523, eccentricity=0.06415961503475412, equilibrium_temperature=1500.4719120231427, insolation_flux=506.75880848384304),
                             Planet(planet_name='BD-7430 b', host_name='BD-7430', discovery_method='Pulsation Timing Variations', discovery_year=2016, controversial_flag=True, orbital_period=409.38357124086747, planet_radius=9.6371820313314, planet_mass=9048.695300690939, semi_major_radius=120.52930010977532, eccentricity=0.026919859854214096, equilibrium_temperature=932.5127482199231, insolation_flux=1233.6421966115577),
                             Planet(planet_name='2MASS 4742 a', host_name='2MASS 4742', discovery_method='Transit', discovery_year=2019, controversial_flag=True, orbital_period=376.88348543952463, planet_radius=10.231616864073686, planet_mass=2006.6471533834338, semi_major_radius=122.65288209202072, eccentricity=0.020871025519854397, equilibrium_temperature=1392.7679384272178, insolation_flux=2754.476127550481),
                             Planet(planet_name='omi-8468 1', host_name='omi-8468', discovery_method='Imaging', discovery_year=2020, controversial_flag=True, orbital_period=147.95582363093837, planet_radius=2.22028873582358, planet_mass=2162.9429580134033, semi_major_radius=128.90894756231762, eccentricity=0.025503047827884533, equilibrium_temperature=392.723462029915, insolation_flux=543.5481027732977),
                             Planet(planet_name='omi-8468 2', host_name='omi-8468', discovery_method='Microlensing', discovery_year=2016, controversial_flag=True, orbital_period=396.6743629581114, planet_radius=1.3040351808769834, planet_mass=5986.564582238488, semi_major_radius=169.62100509887927, eccentricity=0.07419111389235183, equilibrium_temperature=495.35609445255636, insolation_flux=689.1581842662704),
                             Planet(planet_name='rho 5763 a', host_name='rho 5763', discovery_method='Pulsar Timing', discovery_year=2015, controversial_flag=True, orbital_period=723.3796229235854, planet_radius=12.761385070590286, planet_mass=6853.961259387974, semi_major_radius=131.7095703269499, eccentricity=0.0339287802911316, equilibrium_temperature=2626.654705511194, insolation_flux=522.4614332894216),
                             Planet(planet_name='gam-3068 2', host_name='gam-3068', discovery_method='Pulsar Timing', discovery_year=2022, controversial_flag=True, orbital_period=741.6329127813883, planet_radius=25.577592162867155, planet_mass=7821.169121989388, semi_major_radius=138.78023670239773, eccentricity=0.0928847796744685, equilibrium_temperature=1110.6535684327353, insolation_flux=345.4244811436323),
                             Planet(planet_name='iot-7737 a', host_name='iot-7737', discovery_method='Astrometry', discovery_year=2021, controversial_flag=True, orbital_period=291.18207223656043, planet_radius=10.407311366377309, planet_mass=3147.965994492284, semi_major_radius=127.90621876190033, eccentricity=0.04870408174679297, equilibrium_temperature=595.6710238362608, insolation_flux=969.2453980609458),
                             Planet(planet_name='bet-5252 a', host_name='bet-5252', discovery_method='Pulsation Timing Variations', discovery_year=2020, controversial_flag=True, orbital_period=419.7011123247001, planet_radius=18.337479015264655, planet_mass=7352.260679307476, semi_major_radius=160.54323665650892, eccentricity=0.04808805554228841, equilibrium_temperature=1060.7748903856163, insolation_flux=2105.8485687915563),
                             Planet(planet_name='xi 6165 a', host_name='xi 6165', discovery_method='Pulsation Timing Variations', discovery_year=2022, controversial_flag=True, orbital_period=439.27354691100805, planet_radius=13.187476198914995, planet_mass=4612.223086238751, semi_major_radius=98.78643899958732, eccentricity=0.04312709598546951, equilibrium_temperature=1354.7124656091664, insolation_flux=349.01501495654963),
                             Planet(planet_name='ome 4473 1', host_name='ome 4473', discovery_method='Transit', discovery_year=2017, controversial_flag=True, orbital_period=632.8010792183501, planet_radius=9.085742910424809, planet_mass=1948.5574882900132, semi_major_radius=25.160796451055987, eccentricity=0.0512603269050121, equilibrium_temperature=1121.7118590399975, insolation_flux=356.1287652552537),
                             Planet(planet_name='ome 4473 2', host_name='ome 4473', discovery_method='Microlensing', discovery_year=2016, controversial_flag=True, orbital_period=468.6028544086217, planet_radius=9.558560414964118, planet_mass=5637.239728602032, semi_major_radius=99.54535464551837, eccentricity=0.04379353846460214, equilibrium_temperature=883.7602495806356, insolation_flux=321.7951636437431),
                             Planet(planet_name='nu 3737 b', host_name='nu 3737', discovery_method='Orbital Brightness Modulation', discovery_year=2022, controversial_flag=True, orbital_period=564.3502433894546, planet_radius=8.394688961296698, planet_mass=2444.54283159395, semi_major_radius=151.12998061047475, eccentricity=0.010669994463914548, equilibrium_temperature=946.0758899123803, insolation_flux=1538.6379935671728),
                             Planet(planet_name='mu 6625 2', host_name='mu 6625', discovery_method='Disk Kinematics', discovery_year=2018, controversial_flag=True, orbital_period=625.8328664773187, planet_radius=6.6382488431830975, planet_mass=3535.4599761912696, semi_major_radius=130.05704506997324, eccentricity=0.06278553848649139, equilibrium_temperature=752.1064448212547, insolation_flux=788.8252660908383),
                             Planet(planet_name='WASP-4359 2', host_name='WASP-4359', discovery_method='Imaging', discovery_year=2020, controversial_flag=True, orbital_period=94.31983910950822, planet_radius=5.99286692209085, planet_mass=4551.691571990067, semi_major_radius=184.21624191938653, eccentricity=0.0798178382262362, equilibrium_temperature=1142.139906229873, insolation_flux=1785.719961139956),
                             Planet(planet_name='nu 4296 2', host_name='nu 4296', discovery_method='Radial Velocity', discovery_year=2020, controversial_flag=True, orbital_period=297.61880397041955, planet_radius=5.214277076732361, planet_mass=3382.484170158288, semi_major_radius=50.2412223350384, eccentricity=0.0597322072304154, equilibrium_temperature=1257.610838761524, insolation_flux=1006.8648383876612),
                             Planet(planet_name='xi-4031 b', host_name='xi-4031', discovery_method='Transit', discovery_year=2019, controversial_flag=True, orbital_period=628.4201150647762, planet_radius=11.619817428378157, planet_mass=5362.811956536745, semi_major_radius=86.48664897922835, eccentricity=0.004481210787792449, equilibrium_temperature=1369.4977280195533, insolation_flux=383.81047403607795),
                             Planet(planet_name='mu2-2675 a', host_name='mu2-2675', discovery_method='Transit Timing Variations', discovery_year=2019, controversial_flag=True, orbital_period=826.4104307453583, planet_radius=18.994269938129374, planet_mass=4856.517071212584, semi_major_radius=109.47192456915906, eccentricity=0.03852152460524425, equilibrium_temperature=1380.8261548588698, insolation_flux=2485.640256988084),
                             Planet(planet_name='eps 7883 b', host_name='eps 7883', discovery_method='Orbital Brightness Modulation', discovery_year=2017, controversial_flag=True, orbital_period=778.3449697709243, planet_radius=6.920612768078187, planet_mass=8678.204675980298, semi_major_radius=163.59960859885382, eccentricity=0.03542378506194897, equilibrium_temperature=1454.9518535166944, insolation_flux=880.5506207744255),
                             Planet(planet_name='TOI-8655 b', host_name='TOI-8655', discovery_method='Disk Kinematics', discovery_year=2017, controversial_flag=True, orbital_period=551.3244166990996, planet_radius=9.056673291046554, planet_mass=9534.049857865479, semi_major_radius=252.76538591486764, eccentricity=0.06347629957791324, equilibrium_temperature=889.5042685307445, insolation_flux=867.885375171121),
                             Planet(planet_name='gam1 4825 1', host_name='gam1 4825', discovery_method='Transit', discovery_year=2017, controversial_flag=True, orbital_period=852.0876958344318, planet_radius=3.8954136438828098, planet_mass=5792.915851113452, semi_major_radius=181.23047806368322, eccentricity=0.03599384794837892, equilibrium_temperature=1551.509122022565, insolation_flux=2338.361787252398),
                             Planet(planet_name='gam1-9125 1', host_name='gam1-9125', discovery_method='Pulsar Timing', discovery_year=2021, controversial_flag=True, orbital_period=314.476115876073, planet_radius=20.558954057227027, planet_mass=3272.808758344525, semi_major_radius=168.27224988365435, eccentricity=0.035245748442930956, equilibrium_temperature=1220.9371685564988, insolation_flux=487.0632437884101),
                             Planet(planet_name='gam1-9125 2', host_name='gam1-9125', discovery_method='Radial Velocity', discovery_year=2013, controversial_flag=True, orbital_period=369.57692805722417, planet_radius=15.834689969202842, planet_mass=2418.653510622228, semi_major_radius=106.07382265304679, eccentricity=0.02666822386843125, equilibrium_temperature=253.83773053735501, insolation_flux=2377.2192977902587),
                             Planet(planet_name='tau-6969 a', host_name='tau-6969', discovery_method='Radial Velocity', discovery_year=2019, controversial_flag=True, orbital_period=432.1325710975007, planet_radius=27.529945410408153, planet_mass=223.83942024557655, semi_major_radius=267.96964662333244, eccentricity=0.05192015464109746, equilibrium_temperature=1730.2938819383753, insolation_flux=1439.3847031471976),
                             Planet(planet_name='alf-8384 2', host_name='alf-8384', discovery_method='Pulsar Timing', discovery_year=2018, controversial_flag=True, orbital_period=357.512270504835, planet_radius=16.197333751865607, planet_mass=1511.4496202671676, semi_major_radius=68.63867886615769, eccentricity=0.1349962854159653, equilibrium_temperature=1749.5289380848208, insolation_flux=157.5890273226952),
                             Planet(planet_name='psi1 1082 2', host_name='psi1 1082', discovery_method='Transit Timing Variations', discovery_year=2014, controversial_flag=True, orbital_period=393.45251862931417, planet_radius=5.940013079470225, planet_mass=4874.443365795206, semi_major_radius=148.0352816988945, eccentricity=0.08213512778332868, equilibrium_temperature=1195.6412750863904, insolation_flux=1933.3593740393817),
                             Planet(planet_name='alf-2124 a', host_name='alf-2124', discovery_method='Microlensing', discovery_year=2015, controversial_flag=True, orbital_period=558.7467096887466, planet_radius=10.747360257746884, planet_mass=6942.205091414019, semi_major_radius=87.97246321406762, eccentricity=0.008293093111257477, equilibrium_temperature=394.9065945661522, insolation_flux=2113.9861274723175),
                             Planet(planet_name='xi 6509 1', host_name='xi 6509', discovery_method='Imaging', discovery_year=2019, controversial_flag=True, orbital_period=389.24348138686673, planet_radius=11.090980608928062, planet_mass=4411.078892511686, semi_major_radius=63.80640872487511, eccentricity=0.04483857782630585, equilibrium_temperature=2081.862502729241, insolation_flux=1693.361507381796),
                             Planet(planet_name='xi 6509 2', host_name='xi 6509', discovery_method='Astrometry', discovery_year=2016, controversial_flag=True, orbital_period=633.3329258277879, planet_radius=10.622338938336604, planet_mass=6129.6514012571815, semi_major_radius=78.78626159290005, eccentricity=0.06162832240831275, equilibrium_temperature=1445.4765314011174, insolation_flux=957.0588193769437),
                             Planet(planet_name='omi 9386 b', host_name='omi 9386', discovery_method='Radial Velocity', discovery_year=2019, controversial_flag=True, orbital_period=481.2843694734493, planet_radius=8.696992917882625, planet_mass=6377.096284379448, semi_major_radius=120.57460086730914, eccentricity=0.01928175612173077, equilibrium_temperature=403.89329447688374, insolation_flux=1005.15597136561),
                             Planet(planet_name='gam-3927 1', host_name='gam-3927', discovery_method='Microlensing', discovery_year=2014, controversial_flag=True, orbital_period=829.5201277015358, planet_radius=14.156483738401151, planet_mass=4860.30110066203, semi_major_radius=160.6157332489376, eccentricity=0.0719165210667342, equilibrium_temperature=1043.415354890506, insolation_flux=409.8544045660285),
                             Planet(planet_name='Kepler 6827 a', host_name='Kepler 6827', discovery_method='Imaging', discovery_year=2022, controversial_flag=True, orbital_period=564.0195867740293, planet_radius=12.04226942992004, planet_mass=1291.3667551648764, semi_major_radius=142.2689063472069, eccentricity=0.07416358866562614, equilibrium_temperature=1390.2614474671404, insolation_flux=1752.5325674377464),
                             Planet(planet_name='ups-5391 b', host_name='ups-5391', discovery_method='Orbital Brightness Modulation', discovery_year=2017, controversial_flag=True, orbital_period=920.4407003772128, planet_radius=11.270651874103631, planet_mass=3767.2233927523075, semi_major_radius=18.297735447806318, eccentricity=0.032606426563581925, equilibrium_temperature=2085.2210003433347, insolation_flux=883.333007699792),
                             Planet(planet_name='omi-3968 a', host_name='omi-3968', discovery_method='Orbital Brightness Modulation', discovery_year=2017, controversial_flag=True, orbital_period=639.2276827600022, planet_radius=22.480839530448243, planet_mass=6840.086138581245, semi_major_radius=113.92592274139446, eccentricity=0.02339467653962917, equilibrium_temperature=1972.3331690714235, insolation_flux=1513.186117754051),
                             Planet(planet_name='WASP-90489 1', host_name='WASP-90489', discovery_method='Transit', discovery_year=2018, controversial_flag=True, orbital_period=469.0970743489353, planet_radius=13.398386290566629, planet_mass=3988.7335844223153, semi_major_radius=170.4046374956664, eccentricity=0.03248459803875563, equilibrium_temperature=1156.8884948349953, insolation_flux=347.36057272589755),
                             Planet(planet_name='mu2-5663 2', host_name='mu2-5663', discovery_method='Disk Kinematics', discovery_year=2019, controversial_flag=True, orbital_period=146.8400374167153, planet_radius=20.29762665142492, planet_mass=2497.110551411097, semi_major_radius=53.367139440975116, eccentricity=0.01477502712765371, equilibrium_temperature=1940.9056645105816, insolation_flux=1307.3679447622224),
                             Planet(planet_name='bet 7283 a', host_name='bet 7283', discovery_method='Transit Timing Variations', discovery_year=2017, controversial_flag=True, orbital_period=826.546377296482, planet_radius=15.213152201097701, planet_mass=3570.873465151813, semi_major_radius=89.24001385573366, eccentricity=0.10729649607883662, equilibrium_temperature=2519.665276861483, insolation_flux=1081.0937008818516),
                             Planet(planet_name='bet 7283 b', host_name='bet 7283', discovery_method='Transit', discovery_year=2017, controversial_flag=True, orbital_period=424.4841883134427, planet_radius=8.062954444963372, planet_mass=5698.991611919063, semi_major_radius=64.25504327464705, eccentricity=0.08367960932215601, equilibrium_temperature=1214.4112925957015, insolation_flux=1641.6596729125652),
                             Planet(planet_name='xi-5327 a', host_name='xi-5327', discovery_method='Pulsar Timing', discovery_year=2018, controversial_flag=True, orbital_period=1088.3927592308592, planet_radius=2.946561583023966, planet_mass=4293.481632666524, semi_major_radius=76.00901548467141, eccentricity=0.013273492789287612, equilibrium_temperature=1527.727441384132, insolation_flux=1079.421507711436),
                             Planet(planet_name='rho 36 2', host_name='rho 36', discovery_method='Orbital Brightness Modulation', discovery_year=2020, controversial_flag=True, orbital_period=385.71859606323613, planet_radius=10.972350490879307, planet_mass=6080.979783864223, semi_major_radius=19.70879635662655, eccentricity=0.0816254513281208, equilibrium_temperature=918.8137055833458, insolation_flux=299.8269187587988),
                             Planet(planet_name='BD-1979 1', host_name='BD-1979', discovery_method='Disk Kinematics', discovery_year=2014, controversial_flag=True, orbital_period=642.5857640099766, planet_radius=25.713400462548208, planet_mass=9137.329870481128, semi_major_radius=107.47648929041254, eccentricity=0.05435610629727505, equilibrium_temperature=1115.8065315129388, insolation_flux=603.7414601235062),
                             Planet(planet_name='GJ-7089 1', host_name='GJ-7089', discovery_method='Transit Timing Variations', discovery_year=2021, controversial_flag=True, orbital_period=939.8422895534401, planet_radius=19.799074634547743, planet_mass=5296.027931157823, semi_major_radius=8.381408876637977, eccentricity=0.0952523268505993, equilibrium_temperature=1731.3222967892461, insolation_flux=1463.7477175536394),
                             Planet(planet_name='bet-4359 1', host_name='bet-4359', discovery_method='Pulsation Timing Variations', discovery_year=2019, controversial_flag=True, orbital_period=517.1157895619966, planet_radius=10.045830824940143, planet_mass=5456.622749556979, semi_major_radius=35.921021233785794, eccentricity=0.07747512347475216, equilibrium_temperature=312.1455367150918, insolation_flux=1925.0157554133825),
                             Planet(planet_name='BD 1124 2', host_name='BD 1124', discovery_method='Pulsation Timing Variations', discovery_year=2022, controversial_flag=True, orbital_period=544.0430131493249, planet_radius=9.905122059741325, planet_mass=4224.042679331168, semi_major_radius=11.560389326162834, eccentricity=0.08801693139607712, equilibrium_temperature=1196.49495056493, insolation_flux=422.16200989870106),
                             Planet(planet_name='tau 9637 b', host_name='tau 9637', discovery_method='Microlensing', discovery_year=2019, controversial_flag=True, orbital_period=914.8557034127657, planet_radius=18.911106838480954, planet_mass=5785.953124874645, semi_major_radius=190.89113854716408, eccentricity=0.051113599768543655, equilibrium_temperature=138.13876012955916, insolation_flux=1102.7866509223225),
                             Planet(planet_name='eps-8988 b', host_name='eps-8988', discovery_method='Pulsar Timing', discovery_year=2021, controversial_flag=True, orbital_period=631.8505511049178, planet_radius=19.271366755342967, planet_mass=4562.735659835963, semi_major_radius=90.40673473414121, eccentricity=0.06419452682433288, equilibrium_temperature=779.5702748203707, insolation_flux=1375.8052107027197),
                             Planet(planet_name='mu 6237 b', host_name='mu 6237', discovery_method='Transit Timing Variations', discovery_year=2020, controversial_flag=True, orbital_period=293.8564484331166, planet_radius=4.20804403271823, planet_mass=5965.146654371223, semi_major_radius=45.167061971308556, eccentricity=0.06843147375273324, equilibrium_temperature=1317.418585898673, insolation_flux=1021.6034129753637),
                             Planet(planet_name='bet-90207 1', host_name='bet-90207', discovery_method='Eclipse Timing Variations', discovery_year=2018, controversial_flag=True, orbital_period=547.7732077995888, planet_radius=18.17038813878469, planet_mass=7151.98354468515, semi_major_radius=171.16072271843277, eccentricity=0.03500306923769417, equilibrium_temperature=818.0787751833421, insolation_flux=1375.1270343044157),
                             Planet(planet_name='Kepler 3387 1', host_name='Kepler 3387', discovery_method='Astrometry', discovery_year=2019, controversial_flag=True, orbital_period=825.366451403376, planet_radius=8.811015018608908, planet_mass=4931.890138129052, semi_major_radius=143.48466596856883, eccentricity=0.046443167080878124, equilibrium_temperature=1473.9025409117514, insolation_flux=2195.0610233912766),
                             Planet(planet_name='xi 8056 b', host_name='xi 8056', discovery_method='Disk Kinematics', discovery_year=2017, controversial_flag=True, orbital_period=726.7424563042871, planet_radius=11.459928192818387, planet_mass=3681.7808648703913, semi_major_radius=70.08574692399188, eccentricity=0.02801141427825538, equilibrium_temperature=667.3975437573868, insolation_flux=551.4980090435531),
                             Planet(planet_name='mu-89 1', host_name='mu-89', discovery_method='Pulsar Timing', discovery_year=2018, controversial_flag=True, orbital_period=773.6096128589156, planet_radius=9.51635650823819, planet_mass=342.36188341052, semi_major_radius=71.57293753420296, eccentricity=0.038566776022663445, equilibrium_temperature=1277.8131762793867, insolation_flux=802.3034614654184),
                             Planet(planet_name='mu2 6590 1', host_name='mu2 6590', discovery_method='Pulsar Timing', discovery_year=2016, controversial_flag=True, orbital_period=463.25216025297146, planet_radius=4.622115944571399, planet_mass=9340.702798858114, semi_major_radius=91.55903532463401, eccentricity=0.0723449170742071, equilibrium_temperature=2551.4813698148173, insolation_flux=1535.857934123758),
                             Planet(planet_name='mu2 6590 2', host_name='mu2 6590', discovery_method='Radial Velocity', discovery_year=2020, controversial_flag=True, orbital_period=126.66509878782517, planet_radius=17.54513981481744, planet_mass=7420.06435307516, semi_major_radius=39.77789463074325, eccentricity=0.0909895844538477, equilibrium_temperature=230.67767289285507, insolation_flux=717.9734250829631),
                             Planet(planet_name='eps-8057 2', host_name='eps-8057', discovery_method='Transit', discovery_year=2018, controversial_flag=True, orbital_period=352.27084717487855, planet_radius=10.057661357738175, planet_mass=4216.417281944854, semi_major_radius=148.11244523183996, eccentricity=0.065171843755198, equilibrium_temperature=2200.4984838664514, insolation_flux=250.62974129758004),
                             Planet(planet_name='iot-6116 1', host_name='iot-6116', discovery_method='Microlensing', discovery_year=2020, controversial_flag=True, orbital_period=326.58617291590303, planet_radius=12.09096407917402, planet_mass=5709.882418913738, semi_major_radius=127.99247478149081, eccentricity=0.035725976749213094, equilibrium_temperature=574.329760511425, insolation_flux=2256.357505355204),
                             Planet(planet_name='gam 1149 2', host_name='gam 1149', discovery_method='Orbital Brightness Modulation', discovery_year=2017, controversial_flag=True, orbital_period=701.8298083474384, planet_radius=21.11478342641123, planet_mass=4632.98130655566, semi_major_radius=176.47767285466244, eccentricity=0.0606535261717354, equilibrium_temperature=1189.238452818889, insolation_flux=625.9808461084484),
                             Planet(planet_name='gam1-8940 1', host_name='gam1-8940', discovery_method='Disk Kinematics', discovery_year=2019, controversial_flag=True, orbital_period=705.8287952479952, planet_radius=15.321943539474841, planet_mass=2769.51186051733, semi_major_radius=57.08992569105362, eccentricity=0.0722458747554071, equilibrium_temperature=2287.563043826197, insolation_flux=1312.7124747611078),
                             Planet(planet_name='gam1-8940 2', host_name='gam1-8940', discovery_method='Imaging', discovery_year=2018, controversial_flag=True, orbital_period=164.64506842920065, planet_radius=5.544886595895105, planet_mass=8481.447717653018, semi_major_radius=116.15507024442722, eccentricity=0.09099063449460604, equilibrium_temperature=807.2626680999867, insolation_flux=687.3780517848375),
                             Planet(planet_name='iot 8093 a', host_name='iot 8093', discovery_method='Radial Velocity', discovery_year=2017, controversial_flag=True, orbital_period=608.6694971983437, planet_radius=0.5787034147584915, planet_mass=2699.446074509584, semi_major_radius=147.13031535326132, eccentricity=0.03202500446534916, equilibrium_temperature=198.3000753630606, insolation_flux=780.8497920769846),
                             Planet(planet_name='psi1 189 1', host_name='psi1 189', discovery_method='Orbital Brightness Modulation', discovery_year=2020, controversial_flag=True, orbital_period=829.1114290047235, planet_radius=0.7466143136228283, planet_mass=7688.842676221635, semi_major_radius=137.82035723780933, eccentricity=0.052989434283729764, equilibrium_temperature=812.6552778418256, insolation_flux=982.4118425795835),
                             Planet(planet_name='psi1 189 2', host_name='psi1 189', discovery_method='Transit Timing Variations', discovery_year=2019, controversial_flag=True, orbital_period=685.9819143101322, planet_radius=19.935135325042403, planet_mass=815.4017419434658, semi_major_radius=138.71247946299536, eccentricity=0.043278006276673886, equilibrium_temperature=968.6403416785038, insolation_flux=639.6050400001584),
                             Planet(planet_name='Kepler 6482 1', host_name='Kepler 6482', discovery_method='Pulsar Timing', discovery_year=2021, controversial_flag=True, orbital_period=584.5082856488043, planet_radius=14.40612435706781, planet_mass=4969.866162449678, semi_major_radius=105.89982731534897, eccentricity=0.04883816238959033, equilibrium_temperature=531.8709208862725, insolation_flux=748.054133888533),
                             Planet(planet_name='GJ 6866 2', host_name='GJ 6866', discovery_method='Radial Velocity', discovery_year=2019, controversial_flag=True, orbital_period=825.6905162385665, planet_radius=15.442564961825374, planet_mass=267.24304084857795, semi_major_radius=160.50931040028198, eccentricity=0.06449082148775624, equilibrium_temperature=404.1139349247803, insolation_flux=1942.5833422422545),
                             Planet(planet_name='2MASS-8024 a', host_name='2MASS-8024', discovery_method='Radial Velocity', discovery_year=2016, controversial_flag=True, orbital_period=91.66466555034214, planet_radius=19.07120952591395, planet_mass=7024.820606106845, semi_major_radius=105.08834232249842, eccentricity=0.05466839336409442, equilibrium_temperature=769.5210415137478, insolation_flux=1276.3871407521206),
                             Planet(planet_name='2MASS-8024 b', host_name='2MASS-8024', discovery_method='Imaging', discovery_year=2018, controversial_flag=True, orbital_period=424.47067999168337, planet_radius=12.215678207547748, planet_mass=5839.831825502921, semi_major_radius=79.66438002251013, eccentricity=0.04157000311561557, equilibrium_temperature=962.1815993561985, insolation_flux=1420.9084668192502),
                             Planet(planet_name='psi1-5778 2', host_name='psi1-5778', discovery_method='Eclipse Timing Variations', discovery_year=2019, controversial_flag=True, orbital_period=813.099639766146, planet_radius=5.224183119538617, planet_mass=4587.080234251076, semi_major_radius=90.15489657274398, eccentricity=0.07953103008029708, equilibrium_temperature=1592.4084589030526, insolation_flux=487.2054455416388),
                             Planet(planet_name='BD 46946 1', host_name='BD 46946', discovery_method='Transit Timing Variations', discovery_year=2017, controversial_flag=True, orbital_period=489.6149983239187, planet_radius=15.020193073731383, planet_mass=2464.21049329481, semi_major_radius=117.41672874026669, eccentricity=0.0491939084658236, equilibrium_temperature=888.4405900882794, insolation_flux=717.2867440212669),
                             Planet(planet_name='mu 52078 b', host_name='mu 52078', discovery_method='Radial Velocity', discovery_year=2018, controversial_flag=True, orbital_period=437.53470227481273, planet_radius=13.857547157405666, planet_mass=2137.751949756737, semi_major_radius=47.44389770443783, eccentricity=0.07085112075438044, equilibrium_temperature=1149.4903270589523, insolation_flux=1367.1547098191095),
                             Planet(planet_name='WASP-9098 b', host_name='WASP-9098', discovery_method='Radial Velocity', discovery_year=2019, controversial_flag=True, orbital_period=124.67272791827742, planet_radius=14.262905974115345, planet_mass=1833.9836471222025, semi_major_radius=128.79775476630294, eccentricity=0.018142791734214465, equilibrium_temperature=769.8037388313251, insolation_flux=1467.2684141472587)],
                     'q15': [Planet(planet_name='ups 67186 4', host_name='ups 67186', discovery_method='Radial Velocity', discovery_year=2019, controversial_flag=False, orbital_period=1175.659606072101, planet_radius=15.718952305678418, planet_mass=6283.96252618428, semi_major_radius=41.431898960148125, eccentricity=0.048130411323069854, equilibrium_temperature=2184.5654614581563, insolation_flux=1117.6155213654094),
                             Planet(planet_name='tau-7729 1', host_name='tau-7729', discovery_method='Eclipse Timing Variations', discovery_year=2018, controversial_flag=False, orbital_period=396.82161218010924, planet_radius=24.960953797006542, planet_mass=4956.393596775083, semi_major_radius=28.19391148556757, eccentricity=0.05016647709514772, equilibrium_temperature=1373.1301020812093, insolation_flux=1334.6061311503076),
                             Planet(planet_name='tau-7729 2', host_name='tau-7729', discovery_method='Radial Velocity', discovery_year=2018, controversial_flag=True, orbital_period=732.685267588312, planet_radius=21.834488469544688, planet_mass=4070.630098428295, semi_major_radius=19.0572097152166, eccentricity=0.10572314783175354, equilibrium_temperature=1175.0368287067656, insolation_flux=1114.0808853809153),
                             Planet(planet_name='tau-7729 3', host_name='tau-7729', discovery_method='Eclipse Timing Variations', discovery_year=2017, controversial_flag=False, orbital_period=538.9930361439726, planet_radius=14.909279128981089, planet_mass=4344.515654214219, semi_major_radius=103.51026060739869, eccentricity=0.031125884862877717, equilibrium_temperature=1027.3106768470873, insolation_flux=413.50617227467296),
                             Planet(planet_name='tau-7729 4', host_name='tau-7729', discovery_method='Imaging', discovery_year=2020, controversial_flag=True, orbital_period=509.3743799549818, planet_radius=14.054332252663494, planet_mass=4562.396276518155, semi_major_radius=63.98982387505912, eccentricity=0.06993579896190433, equilibrium_temperature=606.1681466921086, insolation_flux=911.5765969342787)],
                     'q16': [],
                     'q17': 0,
                     'q18': Star(spectral_type='L4.75', stellar_effective_temperature=5434.940293198909, stellar_radius=62.58162764458916, stellar_mass=0.9087563163446042, stellar_luminosity=0.8459800361747618, stellar_surface_gravity=2.394386751231921, stellar_age=12.1),
                     'q19': 11.813478404314132,
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
