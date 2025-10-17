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
                     'q5': Star(spectral_type='M7.25VI', stellar_effective_temperature=5652.897566841999, stellar_radius=8.558471992664309, stellar_mass=2.1313815891493206, stellar_luminosity=-3.6588337626881193, stellar_surface_gravity=5.416610264543044, stellar_age=3.713810234114803),
                     'q6': Star(spectral_type='A2.5I', stellar_effective_temperature=6507.368419346395, stellar_radius=None, stellar_mass=5.575546762032203, stellar_luminosity=-2.3836618308982374, stellar_surface_gravity=1.4574467580534074, stellar_age=3.651541914567465),
                     'q7': -0.29340115240558395,
                     'q8': 7.123292448383828,
                     'q9': 7157.9704930872085,
                     'q10': 'kap-4191',
                     'q11': 8.554803946392418,
                     'Planet': Planet(planet_name='Jupiter', host_name='Sun', discovery_method='Imaging', discovery_year=1610, controversial_flag=False, orbital_period=4333.0, planet_radius=11.209, planet_mass=317.828, semi_major_radius=5.2038, eccentricity=0.0489, equilibrium_temperature=110, insolation_flux=0.0345),
                     'q12': Planet(planet_name='HD-3993 a', host_name='HD-3993', discovery_method='Pulsar Timing', discovery_year=2017, controversial_flag=False, orbital_period=211.81519142424708, planet_radius=0.0, planet_mass=4752.79644679978, semi_major_radius=157.09925316377422, eccentricity=0.0839174703289532, equilibrium_temperature=1321.8429788829608, insolation_flux=653.1345425181989),
                     'q13': [Planet(planet_name='ups 5959 a', host_name='ups 5959', discovery_method='Astrometry', discovery_year=2022, controversial_flag=False, orbital_period=494.2815366612187, planet_radius=None, planet_mass=2745.613658018625, semi_major_radius=15.276907254423534, eccentricity=0.0617688654799801, equilibrium_temperature=745.4618481801443, insolation_flux=1712.0002045566805),
                             Planet(planet_name='tau-2526 a', host_name='tau-2526', discovery_method='Transit Timing Variations', discovery_year=2022, controversial_flag=False, orbital_period=420.7490397677651, planet_radius=5.5795636832515365, planet_mass=7313.519855673096, semi_major_radius=147.08579049419703, eccentricity=0.0492616412316732, equilibrium_temperature=1660.0964940669476, insolation_flux=1424.8321244211693),
                             Planet(planet_name='ome-5385 1', host_name='ome-5385', discovery_method='Pulsar Timing', discovery_year=2018, controversial_flag=True, orbital_period=804.8975081394241, planet_radius=13.13933256548847, planet_mass=4376.561098103744, semi_major_radius=114.05412131913856, eccentricity=0.0590394196634442, equilibrium_temperature=2130.7340204861, insolation_flux=140.98392287555305),
                             Planet(planet_name='2MASS-2024 a', host_name='2MASS-2024', discovery_method='Radial Velocity', discovery_year=2020, controversial_flag=True, orbital_period=626.0327218416234, planet_radius=11.714786621115094, planet_mass=6504.5963774217325, semi_major_radius=21.361351881339036, eccentricity=0.1013291805563381, equilibrium_temperature=1850.9607184346887, insolation_flux=1215.871044424705),
                             Planet(planet_name='gam 4096 1', host_name='gam 4096', discovery_method='Transit Timing Variations', discovery_year=2017, controversial_flag=False, orbital_period=522.9561367474333, planet_radius=25.45061174780887, planet_mass=4567.588956628823, semi_major_radius=107.29689621329364, eccentricity=0.0376482669268554, equilibrium_temperature=1219.1082420098774, insolation_flux=900.593097800293)],
                     'q14': [Planet(planet_name='ome-9098 a', host_name='ome-9098', discovery_method='Orbital Brightness Modulation', discovery_year=2021, controversial_flag=True, orbital_period=791.0815122738614, planet_radius=10.049234498983648, planet_mass=6337.409527741413, semi_major_radius=230.93476364197005, eccentricity=0.0489767638753115, equilibrium_temperature=748.4746381699961, insolation_flux=1345.3177434855866),
                             Planet(planet_name='WASP 3321 2', host_name='WASP 3321', discovery_method='Pulsation Timing Variations', discovery_year=2017, controversial_flag=True, orbital_period=185.76784578443835, planet_radius=12.930868262370062, planet_mass=5136.588087283751, semi_major_radius=19.3135179732987, eccentricity=0.0371366462575753, equilibrium_temperature=1562.201991992862, insolation_flux=1140.405806637016),
                             Planet(planet_name='iot 4763 1', host_name='iot 4763', discovery_method='Microlensing', discovery_year=2021, controversial_flag=True, orbital_period=225.7700788844184, planet_radius=8.342746695903628, planet_mass=7060.658259005961, semi_major_radius=165.89431169699054, eccentricity=0.0190401744986942, equilibrium_temperature=1212.1309959439775, insolation_flux=843.7063571180175),
                             Planet(planet_name='iot 4763 2', host_name='iot 4763', discovery_method='Pulsar Timing', discovery_year=2021, controversial_flag=True, orbital_period=408.09481030347735, planet_radius=8.125408019918567, planet_mass=3017.2300626948886, semi_major_radius=125.75011847197436, eccentricity=0.0757346491206547, equilibrium_temperature=2039.2773788364875, insolation_flux=2024.6782228850348),
                             Planet(planet_name='GJ 396 b', host_name='GJ 396', discovery_method='Pulsation Timing Variations', discovery_year=2017, controversial_flag=True, orbital_period=527.5669567192829, planet_radius=9.061606747849904, planet_mass=10834.308058781407, semi_major_radius=149.8410017300201, eccentricity=0.0765531436517463, equilibrium_temperature=1303.656111016253, insolation_flux=2663.861135231144),
                             Planet(planet_name='2MASS-934 1', host_name='2MASS-934', discovery_method='Transit', discovery_year=2019, controversial_flag=True, orbital_period=766.893943173377, planet_radius=None, planet_mass=1654.6106275538, semi_major_radius=85.50237857410151, eccentricity=0.0461966880007649, equilibrium_temperature=1532.5489692149913, insolation_flux=623.5999896130327),
                             Planet(planet_name='rho 4894 a', host_name='rho 4894', discovery_method='Pulsation Timing Variations', discovery_year=2014, controversial_flag=True, orbital_period=355.6068576472478, planet_radius=None, planet_mass=1758.5853452231895, semi_major_radius=14.766636542038285, eccentricity=0.0583984449218787, equilibrium_temperature=1217.295078550805, insolation_flux=1880.343345420304),
                             Planet(planet_name='gam-487 a', host_name='gam-487', discovery_method='Imaging', discovery_year=2018, controversial_flag=True, orbital_period=1091.5705349391271, planet_radius=4.884333457728517, planet_mass=2435.793004918776, semi_major_radius=46.8377713703833, eccentricity=0.0736170145223398, equilibrium_temperature=1781.1604440687738, insolation_flux=1543.2037293689723),
                             Planet(planet_name='gam-487 b', host_name='gam-487', discovery_method='Radial Velocity', discovery_year=2016, controversial_flag=True, orbital_period=1104.5264530025509, planet_radius=12.317080489032469, planet_mass=3153.256724812476, semi_major_radius=206.90341840468164, eccentricity=0.0421210056871965, equilibrium_temperature=1627.504315106468, insolation_flux=832.9216900187075),
                             Planet(planet_name='BD 1319 a', host_name='BD 1319', discovery_method='Transit Timing Variations', discovery_year=2021, controversial_flag=True, orbital_period=1042.9773402769565, planet_radius=18.240890766463792, planet_mass=3193.6518115731383, semi_major_radius=206.05587774934924, eccentricity=0.0087393770271695, equilibrium_temperature=1496.3456784409834, insolation_flux=795.0136037791644),
                             Planet(planet_name='HD 6192 1', host_name='HD 6192', discovery_method='Radial Velocity', discovery_year=2017, controversial_flag=True, orbital_period=434.9592081273916, planet_radius=4.461413605179172, planet_mass=4008.4107550476665, semi_major_radius=12.198070798187686, eccentricity=0.0617459914262111, equilibrium_temperature=1836.610371117276, insolation_flux=606.7245556352798),
                             Planet(planet_name='HD 6192 2', host_name='HD 6192', discovery_method='Transit', discovery_year=2015, controversial_flag=True, orbital_period=321.72487269650406, planet_radius=15.524396725633451, planet_mass=2233.1356650019025, semi_major_radius=143.41540616363997, eccentricity=0.0566501391744352, equilibrium_temperature=1125.8555107856946, insolation_flux=1409.7183551860417),
                             Planet(planet_name='mu-3086 b', host_name='mu-3086', discovery_method='Microlensing', discovery_year=2019, controversial_flag=True, orbital_period=306.1715413643114, planet_radius=24.841123314706515, planet_mass=2083.276552921431, semi_major_radius=149.59316886762463, eccentricity=0.0464189551930351, equilibrium_temperature=1189.3491439186485, insolation_flux=668.1837514722031),
                             Planet(planet_name='TOI 8261 1', host_name='TOI 8261', discovery_method='Eclipse Timing Variations', discovery_year=2017, controversial_flag=True, orbital_period=253.06693152482316, planet_radius=16.628400997903604, planet_mass=2992.125144930975, semi_major_radius=66.88765976367344, eccentricity=0.038108066387227, equilibrium_temperature=245.27468293787933, insolation_flux=1084.5982356141133),
                             Planet(planet_name='tau-5013 2', host_name='tau-5013', discovery_method='Radial Velocity', discovery_year=2016, controversial_flag=True, orbital_period=128.2303072118466, planet_radius=14.191013781966806, planet_mass=233.1720116900424, semi_major_radius=115.05246398471658, eccentricity=0.1046566655179189, equilibrium_temperature=1263.848662099983, insolation_flux=1555.8059955859749),
                             Planet(planet_name='gam-4532 1', host_name='gam-4532', discovery_method='Disk Kinematics', discovery_year=2018, controversial_flag=True, orbital_period=614.0192653444767, planet_radius=7.739574983420136, planet_mass=3056.447513705236, semi_major_radius=108.83186713276444, eccentricity=0.0989055930085229, equilibrium_temperature=1793.3113456386145, insolation_flux=1254.4844069050005),
                             Planet(planet_name='mu2 4253 2', host_name='mu2 4253', discovery_method='Transit', discovery_year=2022, controversial_flag=True, orbital_period=344.127937343632, planet_radius=0.0, planet_mass=5078.054637737499, semi_major_radius=107.74078385590752, eccentricity=0.0022331930703064, equilibrium_temperature=456.11034070407607, insolation_flux=1724.279696310116),
                             Planet(planet_name='ups 6220 1', host_name='ups 6220', discovery_method='Microlensing', discovery_year=2019, controversial_flag=True, orbital_period=347.89906145452414, planet_radius=0.0, planet_mass=4724.961075118637, semi_major_radius=40.19840285371156, eccentricity=0.0445808621650528, equilibrium_temperature=1367.8147744492137, insolation_flux=1398.61588142062),
                             Planet(planet_name='2MASS 6325 2', host_name='2MASS 6325', discovery_method='Pulsation Timing Variations', discovery_year=2022, controversial_flag=True, orbital_period=427.6908270707016, planet_radius=17.6089274755671, planet_mass=4762.258440650847, semi_major_radius=60.553227985817855, eccentricity=0.0547872611459511, equilibrium_temperature=739.7543557826549, insolation_flux=1884.754822343082),
                             Planet(planet_name='rho 9165 b', host_name='rho 9165', discovery_method='Pulsation Timing Variations', discovery_year=2019, controversial_flag=True, orbital_period=1019.8219425498936, planet_radius=15.918906208530668, planet_mass=3409.28625216652, semi_major_radius=136.70574193042427, eccentricity=0.0475065181517402, equilibrium_temperature=1202.1534595892442, insolation_flux=706.4880796310813),
                             Planet(planet_name='ups 7652 a', host_name='ups 7652', discovery_method='Pulsar Timing', discovery_year=2017, controversial_flag=True, orbital_period=1069.9104252076029, planet_radius=8.604501881422063, planet_mass=10032.12509331258, semi_major_radius=149.68457201413594, eccentricity=0.054276926060742, equilibrium_temperature=1728.3515346969284, insolation_flux=486.0189160152738),
                             Planet(planet_name='kap 4641 1', host_name='kap 4641', discovery_method='Pulsation Timing Variations', discovery_year=2019, controversial_flag=True, orbital_period=342.24846451412793, planet_radius=None, planet_mass=7485.093841952862, semi_major_radius=157.88807886397467, eccentricity=0.0251100858692387, equilibrium_temperature=973.194181937348, insolation_flux=1330.2993510513402),
                             Planet(planet_name='EPIC 2325 1', host_name='EPIC 2325', discovery_method='Radial Velocity', discovery_year=2013, controversial_flag=True, orbital_period=193.02908394897557, planet_radius=9.988715224958902, planet_mass=10911.49023840921, semi_major_radius=68.70107454245746, eccentricity=0.018526863954221, equilibrium_temperature=1339.1533225632852, insolation_flux=455.5897324487007),
                             Planet(planet_name='gam1-5875 2', host_name='gam1-5875', discovery_method='Disk Kinematics', discovery_year=2015, controversial_flag=True, orbital_period=173.80041005612048, planet_radius=7.724225443331199, planet_mass=2650.0859117107148, semi_major_radius=95.89964080814072, eccentricity=0.0777967660162042, equilibrium_temperature=2337.7368717001023, insolation_flux=464.0025187819415),
                             Planet(planet_name='nu-883 a', host_name='nu-883', discovery_method='Pulsar Timing', discovery_year=2021, controversial_flag=True, orbital_period=192.7256310015473, planet_radius=100000.0, planet_mass=1608.0507413915748, semi_major_radius=156.34928412112333, eccentricity=0.0333297799225188, equilibrium_temperature=958.4697013442636, insolation_flux=1432.0001016269723),
                             Planet(planet_name='ome-7977 a', host_name='ome-7977', discovery_method='Orbital Brightness Modulation', discovery_year=2019, controversial_flag=True, orbital_period=407.46988906874026, planet_radius=4.334493380320946, planet_mass=4947.6012223587495, semi_major_radius=55.8742370129282, eccentricity=0.0156273977413536, equilibrium_temperature=1189.6770139608998, insolation_flux=1693.413228557584),
                             Planet(planet_name='ome-7977 b', host_name='ome-7977', discovery_method='Eclipse Timing Variations', discovery_year=2017, controversial_flag=True, orbital_period=650.8304564835988, planet_radius=16.251441327518986, planet_mass=3546.348541838208, semi_major_radius=140.4235057935013, eccentricity=0.0415485941330818, equilibrium_temperature=1087.6980936372868, insolation_flux=887.1523425306141),
                             Planet(planet_name='ome-2000 1', host_name='ome-2000', discovery_method='Imaging', discovery_year=2019, controversial_flag=True, orbital_period=703.5744451058393, planet_radius=None, planet_mass=3960.0193903648583, semi_major_radius=84.51069815215389, eccentricity=0.0897299776089072, equilibrium_temperature=519.5640685847027, insolation_flux=3.039959087125908),
                             Planet(planet_name='xi-5334 1', host_name='xi-5334', discovery_method='Disk Kinematics', discovery_year=2020, controversial_flag=True, orbital_period=357.7719023063747, planet_radius=14.902569704169858, planet_mass=10337.40607180528, semi_major_radius=151.92178757873384, eccentricity=0.0502235843148197, equilibrium_temperature=944.7586755170978, insolation_flux=1353.7426783334372),
                             Planet(planet_name='xi-5334 2', host_name='xi-5334', discovery_method='Imaging', discovery_year=2020, controversial_flag=True, orbital_period=625.096860937221, planet_radius=16.583038806667858, planet_mass=10890.32584597802, semi_major_radius=98.71128030325048, eccentricity=0.0315336668119585, equilibrium_temperature=1144.2108031912146, insolation_flux=1658.7523736008338),
                             Planet(planet_name='DP-2325 1', host_name='DP-2325', discovery_method='Radial Velocity', discovery_year=2019, controversial_flag=True, orbital_period=324.07140387029807, planet_radius=2.410846812094631, planet_mass=9132.31378721513, semi_major_radius=145.28914125508268, eccentricity=0.064986725494826, equilibrium_temperature=1663.8914620600694, insolation_flux=1191.5312662184035),
                             Planet(planet_name='EPIC-3586 b', host_name='EPIC-3586', discovery_method='Transit', discovery_year=2020, controversial_flag=True, orbital_period=816.3432964221679, planet_radius=9.37060649385807, planet_mass=9096.102190992548, semi_major_radius=140.64257250484548, eccentricity=0.006459000265585, equilibrium_temperature=216.4644522375729, insolation_flux=1140.2265473382806),
                             Planet(planet_name='omi-3321 a', host_name='omi-3321', discovery_method='Disk Kinematics', discovery_year=2022, controversial_flag=True, orbital_period=979.7361199861108, planet_radius=13.950675713007817, planet_mass=7649.422037001765, semi_major_radius=52.31775274076621, eccentricity=0.0178270526659545, equilibrium_temperature=766.2439425820655, insolation_flux=2244.125241296737),
                             Planet(planet_name='omi-7951 a', host_name='omi-7951', discovery_method='Microlensing', discovery_year=2018, controversial_flag=True, orbital_period=799.0515923798597, planet_radius=0.8178767185035856, planet_mass=5099.728391061194, semi_major_radius=115.31949680902774, eccentricity=0.0505380466016092, equilibrium_temperature=1647.0953195229542, insolation_flux=1127.9108436411557),
                             Planet(planet_name='omi-7951 b', host_name='omi-7951', discovery_method='Imaging', discovery_year=2018, controversial_flag=True, orbital_period=533.0601472774435, planet_radius=15.513380925135271, planet_mass=5462.676042146031, semi_major_radius=116.21498419637098, eccentricity=0.0874938051452531, equilibrium_temperature=2031.4974860960624, insolation_flux=912.458299313486),
                             Planet(planet_name='HD-3824 a', host_name='HD-3824', discovery_method='Microlensing', discovery_year=2017, controversial_flag=True, orbital_period=568.9969853885227, planet_radius=14.176909652754354, planet_mass=10156.455857445948, semi_major_radius=152.0409817236825, eccentricity=0.0203936989901151, equilibrium_temperature=1158.670430795236, insolation_flux=1242.8492015625047),
                             Planet(planet_name='bet 288 a', host_name='bet 288', discovery_method='Pulsation Timing Variations', discovery_year=2016, controversial_flag=True, orbital_period=474.91605878956295, planet_radius=None, planet_mass=10078.93207478508, semi_major_radius=57.39174015430847, eccentricity=0.0626643411023747, equilibrium_temperature=1345.893421043363, insolation_flux=918.5533425449122),
                             Planet(planet_name='alf 7895 b', host_name='alf 7895', discovery_method='Orbital Brightness Modulation', discovery_year=2019, controversial_flag=True, orbital_period=350.8158641831208, planet_radius=17.75106699416418, planet_mass=3723.9728805308496, semi_major_radius=216.74404606669637, eccentricity=0.0905321277388718, equilibrium_temperature=1459.5819612583914, insolation_flux=2771.02580581216),
                             Planet(planet_name='kap 809 a', host_name='kap 809', discovery_method='Eclipse Timing Variations', discovery_year=2017, controversial_flag=True, orbital_period=487.02886390206834, planet_radius=8.740827263341489, planet_mass=6379.311532887105, semi_major_radius=14.737138022994683, eccentricity=0.0230249248469658, equilibrium_temperature=755.803459895852, insolation_flux=1828.104611503938),
                             Planet(planet_name='kap 809 b', host_name='kap 809', discovery_method='Disk Kinematics', discovery_year=2015, controversial_flag=True, orbital_period=646.262306679915, planet_radius=16.51969577667385, planet_mass=4577.84925995593, semi_major_radius=122.58749209302148, eccentricity=0.0867900603901346, equilibrium_temperature=811.7987614173553, insolation_flux=1254.763943612397),
                             Planet(planet_name='iot 26228 b', host_name='iot 26228', discovery_method='Disk Kinematics', discovery_year=2015, controversial_flag=True, orbital_period=782.6045104580651, planet_radius=10.79958668334361, planet_mass=3087.5461495362656, semi_major_radius=150.8111305422375, eccentricity=0.051206651539363, equilibrium_temperature=1664.8088390217142, insolation_flux=335.29977157886594),
                             Planet(planet_name='alf 7323 a', host_name='alf 7323', discovery_method='Transit Timing Variations', discovery_year=2020, controversial_flag=True, orbital_period=947.7230775848544, planet_radius=7.580772882503948, planet_mass=10068.62125634697, semi_major_radius=63.59479033450397, eccentricity=0.0482110175307515, equilibrium_temperature=1333.985123416281, insolation_flux=642.7317591510091),
                             Planet(planet_name='alf 7323 b', host_name='alf 7323', discovery_method='Disk Kinematics', discovery_year=2015, controversial_flag=True, orbital_period=839.5095086761473, planet_radius=12.391759834412074, planet_mass=3783.809422237413, semi_major_radius=213.03440072398783, eccentricity=0.0349235783071535, equilibrium_temperature=845.7877287735932, insolation_flux=1674.3096665162195),
                             Planet(planet_name='nu-6887 1', host_name='nu-6887', discovery_method='Pulsation Timing Variations', discovery_year=2017, controversial_flag=True, orbital_period=553.3383842013545, planet_radius=19.45952886922558, planet_mass=4103.024930260588, semi_major_radius=95.86654728163418, eccentricity=0.0374423750102944, equilibrium_temperature=2288.736963131045, insolation_flux=1497.6834751535257),
                             Planet(planet_name='ups-8713 a', host_name='ups-8713', discovery_method='Pulsar Timing', discovery_year=2016, controversial_flag=True, orbital_period=266.821561514626, planet_radius=7.808576467456492, planet_mass=7308.158499263886, semi_major_radius=132.31430823056442, eccentricity=0.0803073338346528, equilibrium_temperature=2189.2337018106177, insolation_flux=478.12032905640206),
                             Planet(planet_name='ups-8713 b', host_name='ups-8713', discovery_method='Orbital Brightness Modulation', discovery_year=2018, controversial_flag=True, orbital_period=379.94427023284607, planet_radius=18.737731038275705, planet_mass=8094.909628030325, semi_major_radius=144.8935542480637, eccentricity=0.0561615341909343, equilibrium_temperature=1447.4237324327116, insolation_flux=1844.7471049045132),
                             Planet(planet_name='psi1-61397 a', host_name='psi1-61397', discovery_method='Pulsar Timing', discovery_year=2015, controversial_flag=True, orbital_period=836.3093862989808, planet_radius=20.06179098577096, planet_mass=1832.810108205857, semi_major_radius=92.84846160553998, eccentricity=0.06664241362953, equilibrium_temperature=1907.7014247312527, insolation_flux=978.2272206468248),
                             Planet(planet_name='mu2-3993 2', host_name='mu2-3993', discovery_method='Pulsar Timing', discovery_year=2019, controversial_flag=True, orbital_period=1163.2549346161954, planet_radius=9.21434902901423, planet_mass=2091.489282161729, semi_major_radius=58.78755065788952, eccentricity=0.0335980537173143, equilibrium_temperature=1055.186143519297, insolation_flux=200.4230403555315),
                             Planet(planet_name='ups 3455 2', host_name='ups 3455', discovery_method='Disk Kinematics', discovery_year=2017, controversial_flag=True, orbital_period=571.7328499902649, planet_radius=22.162302240148744, planet_mass=3856.6711755137753, semi_major_radius=123.03874148660526, eccentricity=0.1100142868740945, equilibrium_temperature=708.5248143496367, insolation_flux=2041.3093685264123),
                             Planet(planet_name='tau 3181 a', host_name='tau 3181', discovery_method='Pulsar Timing', discovery_year=2020, controversial_flag=True, orbital_period=160.23697954079506, planet_radius=21.056072169451756, planet_mass=5703.054005242775, semi_major_radius=163.29088762719027, eccentricity=0.0960444683154269, equilibrium_temperature=892.7780307778687, insolation_flux=5.934616935401436),
                             Planet(planet_name='gam 9707 b', host_name='gam 9707', discovery_method='Pulsation Timing Variations', discovery_year=2021, controversial_flag=True, orbital_period=280.93425865162243, planet_radius=None, planet_mass=3933.918018555544, semi_major_radius=70.11432279508824, eccentricity=0.0378912847324694, equilibrium_temperature=1090.247547599953, insolation_flux=159.67527004677763),
                             Planet(planet_name='ups-2218 2', host_name='ups-2218', discovery_method='Transit', discovery_year=2017, controversial_flag=True, orbital_period=746.7785629530401, planet_radius=12.463488477607852, planet_mass=7803.347748383338, semi_major_radius=86.18738038680875, eccentricity=0.0105842278790525, equilibrium_temperature=1103.5792795832149, insolation_flux=1316.6927670944904),
                             Planet(planet_name='CoRoT-8533 a', host_name='CoRoT-8533', discovery_method='Disk Kinematics', discovery_year=2020, controversial_flag=True, orbital_period=256.26173648641566, planet_radius=11.671249883780987, planet_mass=1893.3569933823733, semi_major_radius=138.6688175132836, eccentricity=0.0394310883409023, equilibrium_temperature=1100.6475619946875, insolation_flux=1030.5669666742306),
                             Planet(planet_name='rho-2950 b', host_name='rho-2950', discovery_method='Pulsar Timing', discovery_year=2021, controversial_flag=True, orbital_period=347.1496288573468, planet_radius=20.93207595602986, planet_mass=4978.00703948275, semi_major_radius=89.83371290192946, eccentricity=0.1070804825064205, equilibrium_temperature=448.6007537971772, insolation_flux=923.079526652794),
                             Planet(planet_name='HD 5530 1', host_name='HD 5530', discovery_method='Pulsation Timing Variations', discovery_year=2017, controversial_flag=True, orbital_period=631.1528382064791, planet_radius=100000.0, planet_mass=3421.080578900364, semi_major_radius=75.64883559718203, eccentricity=0.0483707071601817, equilibrium_temperature=563.9328182556874, insolation_flux=515.9946809865714),
                             Planet(planet_name='nu 3737 b', host_name='nu 3737', discovery_method='Transit Timing Variations', discovery_year=2017, controversial_flag=True, orbital_period=199.7913733641521, planet_radius=1.9446064070969824, planet_mass=4351.668921169707, semi_major_radius=159.68331400378852, eccentricity=0.0239893075377322, equilibrium_temperature=789.7211829128462, insolation_flux=1303.291589064765),
                             Planet(planet_name='mu 9988 a', host_name='mu 9988', discovery_method='Eclipse Timing Variations', discovery_year=2018, controversial_flag=True, orbital_period=304.4671177371642, planet_radius=9.392922727783336, planet_mass=6864.238716267047, semi_major_radius=66.70323131637352, eccentricity=0.0409744398193605, equilibrium_temperature=1533.8939111622688, insolation_flux=1826.6076281511623),
                             Planet(planet_name='bet 3892 b', host_name='bet 3892', discovery_method='Radial Velocity', discovery_year=2020, controversial_flag=True, orbital_period=498.39795023805294, planet_radius=13.935776604674476, planet_mass=8030.658581388688, semi_major_radius=115.3639645995403, eccentricity=0.0409979981497408, equilibrium_temperature=104.82301104034208, insolation_flux=1765.9483568689122),
                             Planet(planet_name='WASP 6436 2', host_name='WASP 6436', discovery_method='Imaging', discovery_year=2014, controversial_flag=True, orbital_period=400.60131634054494, planet_radius=12.690922329499912, planet_mass=7843.4993048426495, semi_major_radius=7.545535464165624, eccentricity=0.0155034581886159, equilibrium_temperature=462.35647386319135, insolation_flux=846.6097673771865),
                             Planet(planet_name='ups 4325 a', host_name='ups 4325', discovery_method='Radial Velocity', discovery_year=2016, controversial_flag=True, orbital_period=505.7869792987861, planet_radius=7.294854441848637, planet_mass=3111.066930140701, semi_major_radius=88.60773088942449, eccentricity=0.0141071132653316, equilibrium_temperature=1491.586123303185, insolation_flux=1401.1085888183163),
                             Planet(planet_name='HD 51128 b', host_name='HD 51128', discovery_method='Microlensing', discovery_year=2016, controversial_flag=True, orbital_period=344.98292123837075, planet_radius=13.470209291262409, planet_mass=10312.78864453005, semi_major_radius=87.40787445425117, eccentricity=0.1005502937515687, equilibrium_temperature=1636.8546098702318, insolation_flux=1161.6763374494424),
                             Planet(planet_name='BD-2946 b', host_name='BD-2946', discovery_method='Disk Kinematics', discovery_year=2012, controversial_flag=True, orbital_period=41.267814153313054, planet_radius=17.10599336754365, planet_mass=4838.524130765908, semi_major_radius=65.49329644927207, eccentricity=0.0328884936321664, equilibrium_temperature=1101.5480425751898, insolation_flux=124.0095924690918),
                             Planet(planet_name='kap-6585 1', host_name='kap-6585', discovery_method='Radial Velocity', discovery_year=2017, controversial_flag=True, orbital_period=35.09917286152745, planet_radius=3.189970538999823, planet_mass=5841.795528174734, semi_major_radius=143.88199065166677, eccentricity=0.065083977218871, equilibrium_temperature=1211.4781943570977, insolation_flux=1915.268479278237),
                             Planet(planet_name='ome-6220 b', host_name='ome-6220', discovery_method='Radial Velocity', discovery_year=2021, controversial_flag=True, orbital_period=850.7876238297375, planet_radius=None, planet_mass=2730.093013981429, semi_major_radius=88.89885677436048, eccentricity=0.0064787541598321, equilibrium_temperature=1489.5081903143032, insolation_flux=2328.8773341645683),
                             Planet(planet_name='EPIC-4390 a', host_name='EPIC-4390', discovery_method='Microlensing', discovery_year=2021, controversial_flag=True, orbital_period=434.5561832042965, planet_radius=10.213199633554424, planet_mass=7587.520103653166, semi_major_radius=227.18856710686924, eccentricity=0.0917062598496526, equilibrium_temperature=865.961090058662, insolation_flux=515.6101621113854),
                             Planet(planet_name='rho 2332 1', host_name='rho 2332', discovery_method='Imaging', discovery_year=2017, controversial_flag=True, orbital_period=480.0425860834009, planet_radius=11.004155191092082, planet_mass=5818.765749197625, semi_major_radius=155.2671284337917, eccentricity=0.0542679942501093, equilibrium_temperature=2043.189748642781, insolation_flux=1255.7804485453637),
                             Planet(planet_name='kap-3514 b', host_name='kap-3514', discovery_method='Disk Kinematics', discovery_year=2020, controversial_flag=True, orbital_period=563.0078725934397, planet_radius=9.65564679398583, planet_mass=1201.4463641047969, semi_major_radius=67.82046893456838, eccentricity=0.0244650447945935, equilibrium_temperature=2197.2659226356345, insolation_flux=1404.84267390086),
                             Planet(planet_name='GJ-8133 a', host_name='GJ-8133', discovery_method='Microlensing', discovery_year=2021, controversial_flag=True, orbital_period=648.5659504975649, planet_radius=3.3872423680054924, planet_mass=8857.785909374481, semi_major_radius=123.94922874068092, eccentricity=0.0788724347295539, equilibrium_temperature=956.5055868890386, insolation_flux=948.8151104742864),
                             Planet(planet_name='BD-2444 2', host_name='BD-2444', discovery_method='Pulsar Timing', discovery_year=2021, controversial_flag=True, orbital_period=506.5997086702829, planet_radius=14.408140678682429, planet_mass=2212.835787191471, semi_major_radius=183.09191727957804, eccentricity=0.023440451290149, equilibrium_temperature=1058.4202570212535, insolation_flux=1183.529509345125),
                             Planet(planet_name='2MASS-4939 1', host_name='2MASS-4939', discovery_method='Astrometry', discovery_year=2020, controversial_flag=True, orbital_period=587.251545151359, planet_radius=100000.0, planet_mass=5780.367104910988, semi_major_radius=109.80376982697712, eccentricity=0.0978055541062757, equilibrium_temperature=1380.6762626601344, insolation_flux=1541.2897150933773),
                             Planet(planet_name='omi 4253 1', host_name='omi 4253', discovery_method='Disk Kinematics', discovery_year=2020, controversial_flag=True, orbital_period=979.5263621301988, planet_radius=20.272128212693858, planet_mass=8478.973546408848, semi_major_radius=151.79386463269233, eccentricity=0.1073329551670702, equilibrium_temperature=1377.4969380956863, insolation_flux=1229.815850580267),
                             Planet(planet_name='psi1 1082 b', host_name='psi1 1082', discovery_method='Transit', discovery_year=2017, controversial_flag=True, orbital_period=441.8136655482512, planet_radius=12.788474440632925, planet_mass=4958.071866787322, semi_major_radius=108.22292646086922, eccentricity=0.0258177968187536, equilibrium_temperature=1038.0054519876262, insolation_flux=1225.520053029697),
                             Planet(planet_name='mu2 8895 b', host_name='mu2 8895', discovery_method='Pulsar Timing', discovery_year=2020, controversial_flag=True, orbital_period=1003.600172095208, planet_radius=17.5199396972973, planet_mass=6368.060672087366, semi_major_radius=171.53503055748115, eccentricity=0.0417384075272572, equilibrium_temperature=800.3979450015207, insolation_flux=1917.7325104047068),
                             Planet(planet_name='DP 8470 1', host_name='DP 8470', discovery_method='Eclipse Timing Variations', discovery_year=2019, controversial_flag=True, orbital_period=1192.938289133583, planet_radius=15.97587762087991, planet_mass=4091.333746992787, semi_major_radius=155.22054800052044, eccentricity=0.0469565393153228, equilibrium_temperature=494.4477424694441, insolation_flux=670.4205977419596),
                             Planet(planet_name='GJ 3743 b', host_name='GJ 3743', discovery_method='Pulsar Timing', discovery_year=2017, controversial_flag=True, orbital_period=868.7678699495857, planet_radius=100000.0, planet_mass=7095.276469516943, semi_major_radius=216.5079789428405, eccentricity=0.0525688219346841, equilibrium_temperature=1435.1756657772846, insolation_flux=1079.0783692464863),
                             Planet(planet_name='kap-3040 2', host_name='kap-3040', discovery_method='Astrometry', discovery_year=2018, controversial_flag=True, orbital_period=239.6033119469506, planet_radius=100000.0, planet_mass=4911.768909001715, semi_major_radius=111.80583999954511, eccentricity=0.0407602072165268, equilibrium_temperature=1313.464139377024, insolation_flux=1200.213929888471),
                             Planet(planet_name='psi1-2104 1', host_name='psi1-2104', discovery_method='Microlensing', discovery_year=2019, controversial_flag=True, orbital_period=360.3674206370048, planet_radius=15.678833108821586, planet_mass=5677.957787587599, semi_major_radius=92.2155705816452, eccentricity=0.0633424982182296, equilibrium_temperature=2101.7837826952555, insolation_flux=954.5027075964676),
                             Planet(planet_name='psi1-2104 2', host_name='psi1-2104', discovery_method='Orbital Brightness Modulation', discovery_year=2022, controversial_flag=True, orbital_period=629.9553038584636, planet_radius=8.703713190254929, planet_mass=2334.306943775694, semi_major_radius=87.14185760403846, eccentricity=0.034600419241137, equilibrium_temperature=1915.6166839852056, insolation_flux=1536.8907560921298),
                             Planet(planet_name='eps 7991 a', host_name='eps 7991', discovery_method='Orbital Brightness Modulation', discovery_year=2021, controversial_flag=True, orbital_period=139.85643675695803, planet_radius=5.586544237221013, planet_mass=2844.8086628233405, semi_major_radius=60.36887416666228, eccentricity=0.0402472140916864, equilibrium_temperature=401.0074135203978, insolation_flux=110.21623761260209),
                             Planet(planet_name='eps 7991 b', host_name='eps 7991', discovery_method='Eclipse Timing Variations', discovery_year=2019, controversial_flag=True, orbital_period=628.5081730690189, planet_radius=0.4178213515278806, planet_mass=3079.5145914866007, semi_major_radius=93.08267278629518, eccentricity=0.089309850662736, equilibrium_temperature=854.1788614136226, insolation_flux=1043.3604033195131),
                             Planet(planet_name='ups 8768 a', host_name='ups 8768', discovery_method='Radial Velocity', discovery_year=2021, controversial_flag=True, orbital_period=999.539698332813, planet_radius=17.735477122289744, planet_mass=3515.555417760627, semi_major_radius=178.7411213123577, eccentricity=0.0079048961963139, equilibrium_temperature=721.2365459816826, insolation_flux=826.5208248070144),
                             Planet(planet_name='iot 4910 2', host_name='iot 4910', discovery_method='Transit Timing Variations', discovery_year=2015, controversial_flag=True, orbital_period=391.60450698781545, planet_radius=100000.0, planet_mass=5697.205880068108, semi_major_radius=130.36052229431354, eccentricity=0.0142001317102873, equilibrium_temperature=2382.1537522976323, insolation_flux=1193.3418790752482),
                             Planet(planet_name='bet 6224 2', host_name='bet 6224', discovery_method='Radial Velocity', discovery_year=2020, controversial_flag=True, orbital_period=714.592854790682, planet_radius=None, planet_mass=11965.976633239836, semi_major_radius=92.78436979368388, eccentricity=0.0814462836193271, equilibrium_temperature=1659.6566841100807, insolation_flux=1673.5417199794067),
                             Planet(planet_name='EPIC-2774 1', host_name='EPIC-2774', discovery_method='Astrometry', discovery_year=2018, controversial_flag=True, orbital_period=335.33469124360454, planet_radius=100000.0, planet_mass=1682.6759401492332, semi_major_radius=68.53299600774197, eccentricity=0.0827647006871686, equilibrium_temperature=236.22469855790905, insolation_flux=2340.142190952947),
                             Planet(planet_name='alf 4720 a', host_name='alf 4720', discovery_method='Astrometry', discovery_year=2015, controversial_flag=True, orbital_period=688.9687370639264, planet_radius=1.3019791317878973, planet_mass=4259.684986562451, semi_major_radius=122.07994246486729, eccentricity=0.102034328288659, equilibrium_temperature=1141.5629570049189, insolation_flux=574.6077953923492),
                             Planet(planet_name='gam 1470 b', host_name='gam 1470', discovery_method='Orbital Brightness Modulation', discovery_year=2019, controversial_flag=True, orbital_period=868.6324644226673, planet_radius=11.37767031815013, planet_mass=9847.436163307744, semi_major_radius=24.88488247233528, eccentricity=0.0522796999936241, equilibrium_temperature=1251.3760373970772, insolation_flux=915.970369424122),
                             Planet(planet_name='nu-7949 2', host_name='nu-7949', discovery_method='Microlensing', discovery_year=2021, controversial_flag=True, orbital_period=498.5171112846302, planet_radius=3.858166567428426, planet_mass=6768.384220023517, semi_major_radius=79.60031347587869, eccentricity=0.0585535114146973, equilibrium_temperature=1461.936626415646, insolation_flux=1403.8744573848064),
                             Planet(planet_name='ups-8189 2', host_name='ups-8189', discovery_method='Astrometry', discovery_year=2015, controversial_flag=True, orbital_period=593.214380262846, planet_radius=9.181616345815778, planet_mass=4457.036973240378, semi_major_radius=81.76701163438844, eccentricity=0.0664018455599909, equilibrium_temperature=1095.2551467818712, insolation_flux=908.8987418520272),
                             Planet(planet_name='EPIC 425 2', host_name='EPIC 425', discovery_method='Orbital Brightness Modulation', discovery_year=2019, controversial_flag=True, orbital_period=628.7019173552561, planet_radius=6.020888564907532, planet_mass=884.8089642472696, semi_major_radius=114.8675639009022, eccentricity=0.0312030352706902, equilibrium_temperature=652.6779577837303, insolation_flux=667.4243360715352),
                             Planet(planet_name='gam 23084 a', host_name='gam 23084', discovery_method='Imaging', discovery_year=2021, controversial_flag=True, orbital_period=265.199534685192, planet_radius=11.328311589837664, planet_mass=5270.532430408292, semi_major_radius=14.035146457513676, eccentricity=0.071307274140565, equilibrium_temperature=1369.45012662752, insolation_flux=1521.983825334564),
                             Planet(planet_name='gam 23084 b', host_name='gam 23084', discovery_method='Transit', discovery_year=2020, controversial_flag=True, orbital_period=239.34714840147268, planet_radius=13.04380261777954, planet_mass=8999.279400865673, semi_major_radius=12.707822427816012, eccentricity=0.0359479358438455, equilibrium_temperature=617.2175836856023, insolation_flux=1349.925355307789),
                             Planet(planet_name='iot 6357 a', host_name='iot 6357', discovery_method='Pulsation Timing Variations', discovery_year=2019, controversial_flag=True, orbital_period=432.2943151807574, planet_radius=25.221105011870755, planet_mass=12641.211787973896, semi_major_radius=110.30156928183416, eccentricity=0.0041101556762951, equilibrium_temperature=1541.7292356900912, insolation_flux=709.3557002908308),
                             Planet(planet_name='iot 6357 b', host_name='iot 6357', discovery_method='Pulsation Timing Variations', discovery_year=2013, controversial_flag=True, orbital_period=648.2378272990427, planet_radius=10.117360470423398, planet_mass=4229.35497910768, semi_major_radius=253.727534580944, eccentricity=0.0734378947539688, equilibrium_temperature=1091.0555895962257, insolation_flux=611.5132337010886),
                             Planet(planet_name='2MASS 3463 1', host_name='2MASS 3463', discovery_method='Pulsation Timing Variations', discovery_year=2017, controversial_flag=True, orbital_period=572.573290132257, planet_radius=9.261415649236367, planet_mass=7339.586319490549, semi_major_radius=190.4466294191164, eccentricity=0.0918105411284931, equilibrium_temperature=1988.9886865027695, insolation_flux=1343.0887376503808),
                             Planet(planet_name='2MASS 3463 2', host_name='2MASS 3463', discovery_method='Pulsation Timing Variations', discovery_year=2017, controversial_flag=True, orbital_period=187.78947050767152, planet_radius=10.406480074744293, planet_mass=6024.229005857435, semi_major_radius=102.50149772564204, eccentricity=0.0523961347534522, equilibrium_temperature=251.54360345717623, insolation_flux=1352.091118146509),
                             Planet(planet_name='ome 7949 b', host_name='ome 7949', discovery_method='Microlensing', discovery_year=2015, controversial_flag=True, orbital_period=732.2843339230474, planet_radius=None, planet_mass=12284.065531849665, semi_major_radius=110.76269950929512, eccentricity=0.1009597962559341, equilibrium_temperature=1340.4781250669175, insolation_flux=2022.915676537136),
                             Planet(planet_name='tau 8444 2', host_name='tau 8444', discovery_method='Transit Timing Variations', discovery_year=2020, controversial_flag=True, orbital_period=562.3653345445783, planet_radius=9.621424015029126, planet_mass=4408.764184049206, semi_major_radius=170.330133961485, eccentricity=0.0281934202843579, equilibrium_temperature=864.2519180475043, insolation_flux=1699.2373820832297),
                             Planet(planet_name='tau 1578 b', host_name='tau 1578', discovery_method='Disk Kinematics', discovery_year=2018, controversial_flag=True, orbital_period=457.56638559414193, planet_radius=6.251351857138964, planet_mass=5128.625739245602, semi_major_radius=90.57047000700754, eccentricity=0.0612027674882309, equilibrium_temperature=585.3527616377336, insolation_flux=1017.6706862630635),
                             Planet(planet_name='CoRoT-1931 1', host_name='CoRoT-1931', discovery_method='Microlensing', discovery_year=2019, controversial_flag=True, orbital_period=335.1463464916978, planet_radius=18.757830509230555, planet_mass=2349.5375797401853, semi_major_radius=183.2904827731722, eccentricity=0.0327814383788618, equilibrium_temperature=127.30888762401604, insolation_flux=610.746403167378),
                             Planet(planet_name='CoRoT-1931 2', host_name='CoRoT-1931', discovery_method='Astrometry', discovery_year=2020, controversial_flag=True, orbital_period=720.0990808406513, planet_radius=21.107083354351666, planet_mass=9105.62887605008, semi_major_radius=37.07688702742531, eccentricity=0.0909602313144416, equilibrium_temperature=531.0762931486394, insolation_flux=1987.22898317084),
                             Planet(planet_name='alf-5 b', host_name='alf-5', discovery_method='Transit Timing Variations', discovery_year=2018, controversial_flag=True, orbital_period=807.2269768968856, planet_radius=12.683348235621612, planet_mass=4537.199883588255, semi_major_radius=127.1230899954721, eccentricity=0.056740404165002, equilibrium_temperature=1086.1469535407632, insolation_flux=1021.3809808360176),
                             Planet(planet_name='psi1 8108 2', host_name='psi1 8108', discovery_method='Disk Kinematics', discovery_year=2018, controversial_flag=True, orbital_period=291.86037998066, planet_radius=14.30423226767172, planet_mass=7332.174545289016, semi_major_radius=146.03071809945902, eccentricity=0.0543950648077299, equilibrium_temperature=945.3499730889424, insolation_flux=396.6768096837841)],
                     'q15': [Planet(planet_name='rho 586 4', host_name='rho 586', discovery_method='Orbital Brightness Modulation', discovery_year=2020, controversial_flag=False, orbital_period=705.9997479399611, planet_radius=100000.0, planet_mass=9444.003867727071, semi_major_radius=92.08901594759212, eccentricity=0.0629126341023307, equilibrium_temperature=1240.5341936481668, insolation_flux=1466.454013650518),
                             Planet(planet_name='eps-6746 1', host_name='eps-6746', discovery_method='Transit', discovery_year=2021, controversial_flag=False, orbital_period=456.4975853187316, planet_radius=0.0, planet_mass=4984.557863156679, semi_major_radius=99.8687506016568, eccentricity=0.0518009355184869, equilibrium_temperature=595.3499236099403, insolation_flux=1095.7969469229636),
                             Planet(planet_name='eps-6746 2', host_name='eps-6746', discovery_method='Astrometry', discovery_year=2016, controversial_flag=False, orbital_period=1065.1556003876535, planet_radius=0.0, planet_mass=886.9689232430073, semi_major_radius=171.53575899053033, eccentricity=0.0690159585699204, equilibrium_temperature=1230.7687682703167, insolation_flux=383.3790141300053),
                             Planet(planet_name='eps-6746 3', host_name='eps-6746', discovery_method='Orbital Brightness Modulation', discovery_year=2018, controversial_flag=True, orbital_period=119.23041972739856, planet_radius=100000.0, planet_mass=4232.300239648934, semi_major_radius=69.44859304664752, eccentricity=0.00697800079908, equilibrium_temperature=1143.3854205173168, insolation_flux=1346.2226937291623),
                             Planet(planet_name='eps-6746 4', host_name='eps-6746', discovery_method='Orbital Brightness Modulation', discovery_year=2020, controversial_flag=False, orbital_period=748.6795838106757, planet_radius=0.0, planet_mass=7983.865721560628, semi_major_radius=203.66613826237085, eccentricity=0.0588587175104004, equilibrium_temperature=1556.476274695813, insolation_flux=572.2308877152037)],
                     'q16': [],
                     'q17': 0,
                     'q18': Star(spectral_type='F2.25', stellar_effective_temperature=6999.227539802438, stellar_radius=None, stellar_mass=1.9159963816656924, stellar_luminosity=-1.440154814821628, stellar_surface_gravity=2.090610805036065, stellar_age=10.729047061210512),
                     'q19': 19586.3367180518}
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
