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
                     'q5': Star(spectral_type='LIII', stellar_effective_temperature=2989.6594992005807, stellar_radius=30.049658236076, stellar_mass=5.711785046414573, stellar_luminosity=-2.5191687116307806, stellar_surface_gravity=3.0392197411981408, stellar_age=52.4),
                     'q6': Star(spectral_type='G3.25IV', stellar_effective_temperature=5429.990800104167, stellar_radius=12.876952166083775, stellar_mass=5.294795782299598, stellar_luminosity=-0.7835132952862314, stellar_surface_gravity=1.465833072562614, stellar_age=52.4),
                     'q7': -0.32033871482009874,
                     'q8': 21.30000000000008,
                     'q9': 3701.095767029823,
                     'q10': 'BD-4628',
                     'q11': 34.04787995421428,
                     'Planet': Planet(planet_name='Jupiter', host_name='Sun', discovery_method='Imaging', discovery_year=1610, controversial_flag=False, orbital_period=4333.0, planet_radius=11.209, planet_mass=317.828, semi_major_radius=5.2038, eccentricity=0.0489, equilibrium_temperature=110, insolation_flux=0.0345),
                     'q12': Planet(planet_name='eps 2872 a', host_name='eps 2872', discovery_method='Eclipse Timing Variations', discovery_year=2020, controversial_flag=True, orbital_period=540.0144977393053, planet_radius=19.8132863002161, planet_mass=6801.403539912954, semi_major_radius=128.85332465851602, eccentricity=0.05186634763968654, equilibrium_temperature=1273.2547295477873, insolation_flux=1200.1836001390172),
                     'q13': [Planet(planet_name='gam-1314 1', host_name='gam-1314', discovery_method='Pulsation Timing Variations', discovery_year=2018, controversial_flag=False, orbital_period=962.6341962938136, planet_radius=12.544189688751555, planet_mass=4442.758729536911, semi_major_radius=127.61751468408954, eccentricity=0.0657046976503287, equilibrium_temperature=1065.6244708597799, insolation_flux=1879.092138787965),
                             Planet(planet_name='kap 8118 a', host_name='kap 8118', discovery_method='Pulsar Timing', discovery_year=2020, controversial_flag=True, orbital_period=456.6131019413806, planet_radius=13.2897267642459, planet_mass=5484.415666062003, semi_major_radius=66.50281251040664, eccentricity=0.01871063083668429, equilibrium_temperature=1627.6961588839076, insolation_flux=1371.1355201075692),
                             Planet(planet_name='GJ-1415 1', host_name='GJ-1415', discovery_method='Orbital Brightness Modulation', discovery_year=2018, controversial_flag=True, orbital_period=419.33928446223683, planet_radius=9.835949476707675, planet_mass=3027.135856790339, semi_major_radius=171.19547757930596, eccentricity=0.008638053375328199, equilibrium_temperature=1545.344160237246, insolation_flux=1041.723823271858),
                             Planet(planet_name='xi-8694 a', host_name='xi-8694', discovery_method='Pulsar Timing', discovery_year=2017, controversial_flag=False, orbital_period=818.835137192558, planet_radius=14.576650366365593, planet_mass=4375.799246323016, semi_major_radius=207.90234062154138, eccentricity=0.003159350128446106, equilibrium_temperature=731.68613314547, insolation_flux=1059.1465277791285),
                             Planet(planet_name='GJ 9664 a', host_name='GJ 9664', discovery_method='Microlensing', discovery_year=2021, controversial_flag=False, orbital_period=634.4540361681736, planet_radius=12.990549629348406, planet_mass=1759.789291640705, semi_major_radius=139.74651224898315, eccentricity=0.0662052071610982, equilibrium_temperature=2134.777092568269, insolation_flux=715.7079453975691)],
                     'q14': [Planet(planet_name='rho 3120 a', host_name='rho 3120', discovery_method='Imaging', discovery_year=2020, controversial_flag=True, orbital_period=450.69496659391666, planet_radius=15.321789067533338, planet_mass=5889.727249486354, semi_major_radius=118.91693033778458, eccentricity=0.05608402060472857, equilibrium_temperature=2227.53297064257, insolation_flux=2002.6444838230193),
                             Planet(planet_name='nu 4731 a', host_name='nu 4731', discovery_method='Microlensing', discovery_year=2016, controversial_flag=True, orbital_period=331.78406970252735, planet_radius=0.6156786660378994, planet_mass=9627.245604194384, semi_major_radius=69.41955701502215, eccentricity=0.10408169656567819, equilibrium_temperature=1026.8918007659654, insolation_flux=1378.613567446687),
                             Planet(planet_name='2MASS-7594 1', host_name='2MASS-7594', discovery_method='Pulsation Timing Variations', discovery_year=2015, controversial_flag=True, orbital_period=392.74071306107203, planet_radius=12.07703907709028, planet_mass=5258.266601016641, semi_major_radius=12.230796393805349, eccentricity=0.02333038663319731, equilibrium_temperature=1526.8177315883374, insolation_flux=477.8340493746625),
                             Planet(planet_name='eps 9733 1', host_name='eps 9733', discovery_method='Pulsar Timing', discovery_year=2017, controversial_flag=True, orbital_period=578.1248943718226, planet_radius=4.790756517447783, planet_mass=9507.606863229707, semi_major_radius=137.33885878533442, eccentricity=0.03651893931840627, equilibrium_temperature=835.5647948196117, insolation_flux=2095.8941839468926),
                             Planet(planet_name='mu 242 2', host_name='mu 242', discovery_method='Eclipse Timing Variations', discovery_year=2020, controversial_flag=True, orbital_period=504.8739210217298, planet_radius=5.4852681328765955, planet_mass=11288.82708425359, semi_major_radius=114.61226883151906, eccentricity=0.060917532211653094, equilibrium_temperature=93.57155300676038, insolation_flux=781.905825375936),
                             Planet(planet_name='Kepler-8590 1', host_name='Kepler-8590', discovery_method='Microlensing', discovery_year=2016, controversial_flag=True, orbital_period=316.4076290992763, planet_radius=17.896335220932457, planet_mass=6574.715465509764, semi_major_radius=117.07940710994637, eccentricity=0.03170028141871939, equilibrium_temperature=1401.3395821917659, insolation_flux=1011.8960413608685),
                             Planet(planet_name='Kepler-8590 2', host_name='Kepler-8590', discovery_method='Pulsar Timing', discovery_year=2015, controversial_flag=True, orbital_period=320.532750181456, planet_radius=8.283909972016321, planet_mass=7892.407989267528, semi_major_radius=40.95247820910797, eccentricity=0.04635959400509108, equilibrium_temperature=1469.710151663793, insolation_flux=208.1075304381618),
                             Planet(planet_name='ome-5385 2', host_name='ome-5385', discovery_method='Pulsar Timing', discovery_year=2022, controversial_flag=True, orbital_period=594.0964898510423, planet_radius=18.554187267068688, planet_mass=444.4950532235225, semi_major_radius=26.37996999267689, eccentricity=0.09258934131706918, equilibrium_temperature=1244.9736242482882, insolation_flux=1112.0785610095002),
                             Planet(planet_name='alf 30 b', host_name='alf 30', discovery_method='Transit', discovery_year=2017, controversial_flag=True, orbital_period=476.9443434252354, planet_radius=10.293550566716897, planet_mass=2121.7717052963367, semi_major_radius=138.1137221100796, eccentricity=0.05027125818360072, equilibrium_temperature=1244.8515938128571, insolation_flux=901.0694976324556),
                             Planet(planet_name='alf-8699 a', host_name='alf-8699', discovery_method='Pulsation Timing Variations', discovery_year=2018, controversial_flag=True, orbital_period=834.9581467172342, planet_radius=9.201426750132367, planet_mass=158.61998591321026, semi_major_radius=164.45099859264639, eccentricity=0.09237403893479237, equilibrium_temperature=627.3317859549379, insolation_flux=976.2114899708253),
                             Planet(planet_name='xi-8834 b', host_name='xi-8834', discovery_method='Radial Velocity', discovery_year=2022, controversial_flag=True, orbital_period=1085.989835525677, planet_radius=7.944161831596691, planet_mass=3339.631836484772, semi_major_radius=89.95322710304083, eccentricity=0.08464446436490826, equilibrium_temperature=216.86944476702104, insolation_flux=1550.5320328584075),
                             Planet(planet_name='mu 4639 2', host_name='mu 4639', discovery_method='Microlensing', discovery_year=2017, controversial_flag=True, orbital_period=757.0523708186743, planet_radius=7.6632030965945805, planet_mass=5132.453544937658, semi_major_radius=56.04688351025779, eccentricity=0.06905734270324787, equilibrium_temperature=847.2748366539302, insolation_flux=1516.1392251539903),
                             Planet(planet_name='BD 7013 a', host_name='BD 7013', discovery_method='Transit', discovery_year=2021, controversial_flag=True, orbital_period=424.7547523702583, planet_radius=17.5409817838799, planet_mass=9385.686032937007, semi_major_radius=13.250091212708142, eccentricity=0.030577927365833955, equilibrium_temperature=1206.707503762986, insolation_flux=1349.6353402973161),
                             Planet(planet_name='BD 7013 b', host_name='BD 7013', discovery_method='Microlensing', discovery_year=2014, controversial_flag=True, orbital_period=426.4295556414495, planet_radius=13.54172690321581, planet_mass=4523.420132497507, semi_major_radius=113.4966619886453, eccentricity=0.07223313984461441, equilibrium_temperature=706.2173236897745, insolation_flux=1439.0480818720018),
                             Planet(planet_name='nu 9932 a', host_name='nu 9932', discovery_method='Microlensing', discovery_year=2019, controversial_flag=True, orbital_period=181.8914942130636, planet_radius=11.868361081210011, planet_mass=12930.444640054908, semi_major_radius=115.71484639237593, eccentricity=0.03347174562689263, equilibrium_temperature=1435.2612284906668, insolation_flux=637.0872241821945),
                             Planet(planet_name='TOI 8261 b', host_name='TOI 8261', discovery_method='Pulsar Timing', discovery_year=2016, controversial_flag=True, orbital_period=537.5673180825441, planet_radius=12.373072242756427, planet_mass=5081.701783143427, semi_major_radius=79.08530426407769, eccentricity=0.07365493514306742, equilibrium_temperature=1425.1515742409638, insolation_flux=2326.830603718624),
                             Planet(planet_name='alf-8644 2', host_name='alf-8644', discovery_method='Orbital Brightness Modulation', discovery_year=2018, controversial_flag=True, orbital_period=660.1542440060744, planet_radius=16.21476973510103, planet_mass=7006.636201681456, semi_major_radius=98.05984131580993, eccentricity=0.039362417248271796, equilibrium_temperature=2190.4304176106416, insolation_flux=1646.4471069841452),
                             Planet(planet_name='bet 8366 1', host_name='bet 8366', discovery_method='Transit', discovery_year=2014, controversial_flag=True, orbital_period=602.5034607813857, planet_radius=23.841532547453546, planet_mass=6071.897062716291, semi_major_radius=229.35720903373732, eccentricity=0.07971182423155627, equilibrium_temperature=1276.409224628963, insolation_flux=2251.3939040590426),
                             Planet(planet_name='2MASS-7524 1', host_name='2MASS-7524', discovery_method='Transit Timing Variations', discovery_year=2020, controversial_flag=True, orbital_period=612.7558692959528, planet_radius=17.463807123325566, planet_mass=1475.7394067298674, semi_major_radius=167.14216141852276, eccentricity=0.08564547001030226, equilibrium_temperature=1457.9330820755697, insolation_flux=1885.96305923716),
                             Planet(planet_name='Kepler 50694 b', host_name='Kepler 50694', discovery_method='Transit', discovery_year=2021, controversial_flag=True, orbital_period=915.4003493106172, planet_radius=1.5630973962006038, planet_mass=2357.066749084517, semi_major_radius=19.604654427395815, eccentricity=0.05679728744537294, equilibrium_temperature=989.1928413041636, insolation_flux=1200.2102452569977),
                             Planet(planet_name='BD-7551 2', host_name='BD-7551', discovery_method='Transit Timing Variations', discovery_year=2021, controversial_flag=True, orbital_period=681.4210760947271, planet_radius=12.107194360771047, planet_mass=4347.28154818891, semi_major_radius=54.47890378756679, eccentricity=0.06735267055311231, equilibrium_temperature=748.2557483110254, insolation_flux=413.2780909209223),
                             Planet(planet_name='alf 7726 1', host_name='alf 7726', discovery_method='Pulsation Timing Variations', discovery_year=2019, controversial_flag=True, orbital_period=70.97831851173538, planet_radius=7.631049672275422, planet_mass=6037.858003821976, semi_major_radius=144.97370095879893, eccentricity=0.07563177751926389, equilibrium_temperature=848.557879193911, insolation_flux=1903.8891025687426),
                             Planet(planet_name='alf 7726 2', host_name='alf 7726', discovery_method='Radial Velocity', discovery_year=2018, controversial_flag=True, orbital_period=640.7676970858665, planet_radius=8.253718059278842, planet_mass=5222.917877191838, semi_major_radius=87.0132979478727, eccentricity=0.07039715180606942, equilibrium_temperature=1098.5802362628513, insolation_flux=1925.680047735816),
                             Planet(planet_name='xi-8811 1', host_name='xi-8811', discovery_method='Orbital Brightness Modulation', discovery_year=2016, controversial_flag=True, orbital_period=94.99363043213305, planet_radius=15.116509837273174, planet_mass=2535.6676034429656, semi_major_radius=164.86961312530383, eccentricity=0.05765333425979468, equilibrium_temperature=874.0174856758749, insolation_flux=480.155963120317),
                             Planet(planet_name='xi-8811 2', host_name='xi-8811', discovery_method='Transit', discovery_year=2021, controversial_flag=True, orbital_period=875.0070592605613, planet_radius=5.532313609500985, planet_mass=509.0449877067049, semi_major_radius=206.40435639979194, eccentricity=0.08520029843379451, equilibrium_temperature=1621.0619669358862, insolation_flux=1645.0330018226737),
                             Planet(planet_name='EPIC-46 a', host_name='EPIC-46', discovery_method='Pulsar Timing', discovery_year=2016, controversial_flag=True, orbital_period=504.6040823422201, planet_radius=16.298427530753372, planet_mass=2180.978025625462, semi_major_radius=168.922172513956, eccentricity=0.06295441755826339, equilibrium_temperature=1449.4521814772945, insolation_flux=877.303623020423),
                             Planet(planet_name='EPIC-46 b', host_name='EPIC-46', discovery_method='Disk Kinematics', discovery_year=2020, controversial_flag=True, orbital_period=361.22162214287107, planet_radius=10.643758179443562, planet_mass=5929.052767566962, semi_major_radius=189.02211723392037, eccentricity=0.0029225170434565087, equilibrium_temperature=1704.834694721209, insolation_flux=1187.710110303241),
                             Planet(planet_name='psi1-8777 2', host_name='psi1-8777', discovery_method='Radial Velocity', discovery_year=2021, controversial_flag=True, orbital_period=660.2845226737255, planet_radius=16.97767178392749, planet_mass=8922.621051891503, semi_major_radius=113.26869798506812, eccentricity=0.07335048280094003, equilibrium_temperature=1465.8296243064372, insolation_flux=362.8936588536154),
                             Planet(planet_name='gam 5251 b', host_name='gam 5251', discovery_method='Astrometry', discovery_year=2019, controversial_flag=True, orbital_period=229.7710033569645, planet_radius=9.825543109564926, planet_mass=4725.596937246396, semi_major_radius=142.72816450772297, eccentricity=0.0598757498897799, equilibrium_temperature=1149.869901420968, insolation_flux=2415.2797717680905),
                             Planet(planet_name='TOI-2776 2', host_name='TOI-2776', discovery_method='Transit', discovery_year=2018, controversial_flag=True, orbital_period=805.778084041043, planet_radius=11.622350313920288, planet_mass=3478.5056152987136, semi_major_radius=137.36861878418497, eccentricity=0.04191667020313246, equilibrium_temperature=944.7272067075507, insolation_flux=1638.3538658334369),
                             Planet(planet_name='EPIC-4901 1', host_name='EPIC-4901', discovery_method='Radial Velocity', discovery_year=2017, controversial_flag=True, orbital_period=501.50423501904527, planet_radius=26.812435152057645, planet_mass=3310.3859267555235, semi_major_radius=56.57125059733435, eccentricity=0.05909625341329162, equilibrium_temperature=1112.0090362202764, insolation_flux=1548.5965411785849),
                             Planet(planet_name='EPIC-4901 2', host_name='EPIC-4901', discovery_method='Astrometry', discovery_year=2017, controversial_flag=True, orbital_period=276.60474783043713, planet_radius=4.768708585601997, planet_mass=2977.8009606207534, semi_major_radius=50.14388808424581, eccentricity=0.032914664194988605, equilibrium_temperature=526.5437393169046, insolation_flux=1307.1818269777843),
                             Planet(planet_name='gam1-9774 1', host_name='gam1-9774', discovery_method='Radial Velocity', discovery_year=2019, controversial_flag=True, orbital_period=462.94307949947824, planet_radius=5.458216782550721, planet_mass=4491.818091911185, semi_major_radius=202.1830931466281, eccentricity=0.039097640957153026, equilibrium_temperature=1821.1333319334794, insolation_flux=943.2673253733399),
                             Planet(planet_name='gam1-9774 2', host_name='gam1-9774', discovery_method='Orbital Brightness Modulation', discovery_year=2020, controversial_flag=True, orbital_period=761.2865845167387, planet_radius=19.0510055443502, planet_mass=6607.403454574129, semi_major_radius=59.17343457844256, eccentricity=0.022628776021349068, equilibrium_temperature=1090.0537953387347, insolation_flux=1452.8692566812522),
                             Planet(planet_name='gam 8776 1', host_name='gam 8776', discovery_method='Disk Kinematics', discovery_year=2020, controversial_flag=True, orbital_period=640.2943641160805, planet_radius=19.197842911224722, planet_mass=4344.80139257471, semi_major_radius=131.5809663510084, eccentricity=0.028330802977439576, equilibrium_temperature=335.4333882992405, insolation_flux=1911.9542232776832),
                             Planet(planet_name='ups-1880 a', host_name='ups-1880', discovery_method='Imaging', discovery_year=2017, controversial_flag=True, orbital_period=156.8854233940932, planet_radius=11.217035946101653, planet_mass=5716.804126764218, semi_major_radius=113.7346123265732, eccentricity=0.021934060125104966, equilibrium_temperature=1730.2908343335118, insolation_flux=1761.2852395522648),
                             Planet(planet_name='kap 809 b', host_name='kap 809', discovery_method='Disk Kinematics', discovery_year=2018, controversial_flag=True, orbital_period=270.8380178691302, planet_radius=12.08243704933702, planet_mass=5535.512162311416, semi_major_radius=147.5147701243473, eccentricity=0.03710783052873599, equilibrium_temperature=76.76657044185629, insolation_flux=2226.8191221229113),
                             Planet(planet_name='mu-5136 1', host_name='mu-5136', discovery_method='Pulsar Timing', discovery_year=2018, controversial_flag=True, orbital_period=377.83248927162424, planet_radius=18.33430634486765, planet_mass=4281.013114153808, semi_major_radius=59.518022107260116, eccentricity=0.06865218673757953, equilibrium_temperature=698.444359876269, insolation_flux=1108.6512676734903),
                             Planet(planet_name='TOI-5783 2', host_name='TOI-5783', discovery_method='Radial Velocity', discovery_year=2014, controversial_flag=True, orbital_period=812.7214230022835, planet_radius=9.448841358734564, planet_mass=2165.127696195864, semi_major_radius=122.98871036483759, eccentricity=0.06868848707599204, equilibrium_temperature=406.02892426594656, insolation_flux=2.0114781957058767),
                             Planet(planet_name='mu 6993 a', host_name='mu 6993', discovery_method='Astrometry', discovery_year=2016, controversial_flag=True, orbital_period=47.943531611563344, planet_radius=7.303030585726878, planet_mass=2620.107025675669, semi_major_radius=3.9311133989045857, eccentricity=0.005062133205239745, equilibrium_temperature=735.607738464475, insolation_flux=1149.3139879426944),
                             Planet(planet_name='kap 987 a', host_name='kap 987', discovery_method='Imaging', discovery_year=2019, controversial_flag=True, orbital_period=676.3030582977789, planet_radius=5.311181957307117, planet_mass=3156.2805319567537, semi_major_radius=153.6160082431419, eccentricity=0.0439739904636481, equilibrium_temperature=1090.1976585722111, insolation_flux=1086.5458682150297),
                             Planet(planet_name='kap 987 b', host_name='kap 987', discovery_method='Microlensing', discovery_year=2016, controversial_flag=True, orbital_period=731.5587490031776, planet_radius=9.048565617273763, planet_mass=10140.20934226323, semi_major_radius=89.75689854426503, eccentricity=0.07838698320812819, equilibrium_temperature=2025.5687581025804, insolation_flux=1229.3471340704825),
                             Planet(planet_name='TOI 8825 a', host_name='TOI 8825', discovery_method='Pulsar Timing', discovery_year=2017, controversial_flag=True, orbital_period=753.4038364191169, planet_radius=3.6892431093621703, planet_mass=9023.165729375973, semi_major_radius=79.22901343552806, eccentricity=0.06797238551511908, equilibrium_temperature=1179.1994610591116, insolation_flux=252.9737856677442),
                             Planet(planet_name='GJ 4468 b', host_name='GJ 4468', discovery_method='Pulsation Timing Variations', discovery_year=2014, controversial_flag=True, orbital_period=588.5521144155396, planet_radius=15.809975416642228, planet_mass=6786.536927759093, semi_major_radius=43.7386401553696, eccentricity=0.035132551917496445, equilibrium_temperature=540.5463412615505, insolation_flux=1606.3100890970006),
                             Planet(planet_name='gam1-8811 a', host_name='gam1-8811', discovery_method='Astrometry', discovery_year=2020, controversial_flag=True, orbital_period=328.855251863238, planet_radius=16.33806920211272, planet_mass=6206.6749985882325, semi_major_radius=105.25900188098652, eccentricity=0.05858245818484421, equilibrium_temperature=767.2784411875118, insolation_flux=784.3363086003192),
                             Planet(planet_name='iot 24 1', host_name='iot 24', discovery_method='Radial Velocity', discovery_year=2016, controversial_flag=True, orbital_period=169.1500141933697, planet_radius=6.5068407717167585, planet_mass=914.2954242565665, semi_major_radius=98.13630265652758, eccentricity=0.047916348099318364, equilibrium_temperature=2410.6189615046223, insolation_flux=425.92917314882277),
                             Planet(planet_name='DP 8451 1', host_name='DP 8451', discovery_method='Orbital Brightness Modulation', discovery_year=2020, controversial_flag=True, orbital_period=720.8763601815523, planet_radius=9.976444596964077, planet_mass=2305.6544050284033, semi_major_radius=37.88500181652362, eccentricity=0.03147363638819106, equilibrium_temperature=737.84839593365, insolation_flux=173.04293878992814),
                             Planet(planet_name='EPIC 78234 a', host_name='EPIC 78234', discovery_method='Astrometry', discovery_year=2018, controversial_flag=True, orbital_period=544.2156613617881, planet_radius=20.51190511334848, planet_mass=7856.281227833215, semi_major_radius=32.27355643015716, eccentricity=0.07129718620426426, equilibrium_temperature=951.6709174936781, insolation_flux=499.84880226878033),
                             Planet(planet_name='ups-8459 a', host_name='ups-8459', discovery_method='Radial Velocity', discovery_year=2020, controversial_flag=True, orbital_period=57.933258269154635, planet_radius=5.77316419996863, planet_mass=5663.651344507244, semi_major_radius=166.45697790627747, eccentricity=0.08329980079965756, equilibrium_temperature=807.1836913284562, insolation_flux=843.2862493774971),
                             Planet(planet_name='2MASS 7501 a', host_name='2MASS 7501', discovery_method='Astrometry', discovery_year=2020, controversial_flag=True, orbital_period=229.66651115345172, planet_radius=3.4444599497791284, planet_mass=3490.210892626313, semi_major_radius=91.47445157864962, eccentricity=0.06440309527463796, equilibrium_temperature=881.7682177503397, insolation_flux=2051.182846685738),
                             Planet(planet_name='mu2 3120 b', host_name='mu2 3120', discovery_method='Eclipse Timing Variations', discovery_year=2016, controversial_flag=True, orbital_period=951.7752241935146, planet_radius=14.764743119178675, planet_mass=6308.525772214238, semi_major_radius=27.85903363999431, eccentricity=0.08199806275415547, equilibrium_temperature=491.4286319101467, insolation_flux=289.4772490632147),
                             Planet(planet_name='bet-951 b', host_name='bet-951', discovery_method='Astrometry', discovery_year=2020, controversial_flag=True, orbital_period=684.5778722048467, planet_radius=10.91744474879481, planet_mass=4463.3046085395345, semi_major_radius=117.86398576408698, eccentricity=0.08615327452194713, equilibrium_temperature=1066.0872944484622, insolation_flux=1283.2482915726023),
                             Planet(planet_name='rho-7724 b', host_name='rho-7724', discovery_method='Disk Kinematics', discovery_year=2018, controversial_flag=True, orbital_period=557.8393172365687, planet_radius=10.677971049638797, planet_mass=6685.294052251794, semi_major_radius=120.14302083369799, eccentricity=0.02032922586177221, equilibrium_temperature=1952.891051550095, insolation_flux=1792.9872530684247),
                             Planet(planet_name='tau 6639 a', host_name='tau 6639', discovery_method='Orbital Brightness Modulation', discovery_year=2022, controversial_flag=True, orbital_period=94.29036259528522, planet_radius=9.844541680558017, planet_mass=6346.427427402418, semi_major_radius=62.518163908541815, eccentricity=0.03459298624475407, equilibrium_temperature=410.107680043016, insolation_flux=478.9155320116706),
                             Planet(planet_name='tau 6639 b', host_name='tau 6639', discovery_method='Radial Velocity', discovery_year=2016, controversial_flag=True, orbital_period=145.27426956621912, planet_radius=20.383746829219263, planet_mass=90.60729586133311, semi_major_radius=110.57802747619854, eccentricity=0.055938011368187004, equilibrium_temperature=1520.1011806478964, insolation_flux=985.8729602981982),
                             Planet(planet_name='omi-1073 b', host_name='omi-1073', discovery_method='Imaging', discovery_year=2018, controversial_flag=True, orbital_period=189.13524873120707, planet_radius=12.30269989985219, planet_mass=1477.1819057464404, semi_major_radius=28.051903514912638, eccentricity=0.062055354666681786, equilibrium_temperature=1155.3842486030164, insolation_flux=2150.6714319896028),
                             Planet(planet_name='Kepler-6188 b', host_name='Kepler-6188', discovery_method='Eclipse Timing Variations', discovery_year=2019, controversial_flag=True, orbital_period=833.5204050538406, planet_radius=7.003304538237686, planet_mass=4939.4175648559185, semi_major_radius=116.8227153963334, eccentricity=0.02017883750440316, equilibrium_temperature=889.5419381327399, insolation_flux=1611.343798234686),
                             Planet(planet_name='kap 5376 1', host_name='kap 5376', discovery_method='Transit', discovery_year=2021, controversial_flag=True, orbital_period=349.80471520595535, planet_radius=13.777139480621603, planet_mass=975.6113452681739, semi_major_radius=4.535286076431603, eccentricity=0.026829249720308423, equilibrium_temperature=1374.8456798229859, insolation_flux=2313.0867625301944),
                             Planet(planet_name='BD 2211 2', host_name='BD 2211', discovery_method='Eclipse Timing Variations', discovery_year=2016, controversial_flag=True, orbital_period=421.2417689408861, planet_radius=2.049686854854981, planet_mass=4819.2253293469175, semi_major_radius=105.60466972607173, eccentricity=0.05691284531568904, equilibrium_temperature=659.772549828509, insolation_flux=2060.9132815877538),
                             Planet(planet_name='2MASS-2925 2', host_name='2MASS-2925', discovery_method='Imaging', discovery_year=2017, controversial_flag=True, orbital_period=382.54203687416503, planet_radius=6.981523142346881, planet_mass=5330.619511567189, semi_major_radius=144.91163540581016, eccentricity=0.07889505835945682, equilibrium_temperature=489.8123936380654, insolation_flux=414.777561402478),
                             Planet(planet_name='ups-543 a', host_name='ups-543', discovery_method='Eclipse Timing Variations', discovery_year=2016, controversial_flag=True, orbital_period=235.80578572809674, planet_radius=2.577820014075, planet_mass=6312.384238978229, semi_major_radius=100.86185729785271, eccentricity=0.049198020266693454, equilibrium_temperature=877.0124461814022, insolation_flux=542.7544354509073),
                             Planet(planet_name='EPIC 4272 1', host_name='EPIC 4272', discovery_method='Pulsation Timing Variations', discovery_year=2014, controversial_flag=True, orbital_period=411.4423917112877, planet_radius=13.125712073222207, planet_mass=4682.464370832388, semi_major_radius=17.46907203901371, eccentricity=0.04871508833690803, equilibrium_temperature=1596.079959484105, insolation_flux=108.49472437447741),
                             Planet(planet_name='WASP 4062 a', host_name='WASP 4062', discovery_method='Pulsation Timing Variations', discovery_year=2020, controversial_flag=True, orbital_period=376.3233125056372, planet_radius=12.941925221914602, planet_mass=2269.6682291464026, semi_major_radius=172.15832115884626, eccentricity=0.0820267114563946, equilibrium_temperature=567.2013812901776, insolation_flux=1364.6348710967823),
                             Planet(planet_name='WASP 4062 b', host_name='WASP 4062', discovery_method='Pulsation Timing Variations', discovery_year=2014, controversial_flag=True, orbital_period=222.77983043759906, planet_radius=3.413673349438964, planet_mass=1927.2549941420234, semi_major_radius=122.74686331103939, eccentricity=0.018900519294363226, equilibrium_temperature=1326.095440639754, insolation_flux=1321.1724742913364),
                             Planet(planet_name='EPIC-1249 2', host_name='EPIC-1249', discovery_method='Imaging', discovery_year=2021, controversial_flag=True, orbital_period=523.4802708993348, planet_radius=27.675682141317402, planet_mass=4956.8233149663265, semi_major_radius=71.38636263753334, eccentricity=0.11454256965112655, equilibrium_temperature=1960.2017991883527, insolation_flux=634.9806275972802),
                             Planet(planet_name='bet 3892 2', host_name='bet 3892', discovery_method='Imaging', discovery_year=2018, controversial_flag=True, orbital_period=108.85420565888938, planet_radius=12.725975325083448, planet_mass=2740.620030884541, semi_major_radius=149.6837226723479, eccentricity=0.07774866461321778, equilibrium_temperature=405.36175820281096, insolation_flux=952.2398812526383),
                             Planet(planet_name='WASP-88 2', host_name='WASP-88', discovery_method='Radial Velocity', discovery_year=2021, controversial_flag=True, orbital_period=864.2208682717874, planet_radius=4.192456275167886, planet_mass=2892.856865102254, semi_major_radius=156.3323544494884, eccentricity=0.05762578358676659, equilibrium_temperature=1385.8812216950212, insolation_flux=118.34073673697822),
                             Planet(planet_name='TOI 4130 1', host_name='TOI 4130', discovery_method='Pulsation Timing Variations', discovery_year=2022, controversial_flag=True, orbital_period=241.40770284400747, planet_radius=9.28765659107975, planet_mass=7574.1522208293945, semi_major_radius=106.88675856963975, eccentricity=0.03449179136367473, equilibrium_temperature=1664.8738604769933, insolation_flux=1216.322171444936),
                             Planet(planet_name='rho-1324 a', host_name='rho-1324', discovery_method='Eclipse Timing Variations', discovery_year=2021, controversial_flag=True, orbital_period=445.06668624391665, planet_radius=22.701515117644163, planet_mass=6241.836442320786, semi_major_radius=121.56556894992977, eccentricity=0.038806778985600185, equilibrium_temperature=1747.686346511618, insolation_flux=335.58081580415535),
                             Planet(planet_name='rho-1324 b', host_name='rho-1324', discovery_method='Orbital Brightness Modulation', discovery_year=2018, controversial_flag=True, orbital_period=904.243068887736, planet_radius=10.259189238316434, planet_mass=9429.617204967179, semi_major_radius=40.72363588188241, eccentricity=0.05583202786662705, equilibrium_temperature=1093.5407442357973, insolation_flux=687.0675937156911),
                             Planet(planet_name='kap 9427 2', host_name='kap 9427', discovery_method='Transit', discovery_year=2019, controversial_flag=True, orbital_period=211.96292089891847, planet_radius=12.33425563916045, planet_mass=5065.987134267418, semi_major_radius=130.2153816745046, eccentricity=0.08451755520252585, equilibrium_temperature=713.5676136152745, insolation_flux=920.300065918693),
                             Planet(planet_name='CoRoT-5167 1', host_name='CoRoT-5167', discovery_method='Disk Kinematics', discovery_year=2018, controversial_flag=True, orbital_period=415.0111990655582, planet_radius=21.00998205381712, planet_mass=7428.850324251057, semi_major_radius=141.5432580432139, eccentricity=0.07953949032193669, equilibrium_temperature=417.9917772647242, insolation_flux=1391.1968690894555),
                             Planet(planet_name='iot-8287 1', host_name='iot-8287', discovery_method='Pulsation Timing Variations', discovery_year=2021, controversial_flag=True, orbital_period=558.0198975121356, planet_radius=20.664017960795146, planet_mass=6912.848966617898, semi_major_radius=89.62733587090432, eccentricity=0.05634177415446075, equilibrium_temperature=458.66267025903824, insolation_flux=1093.8441662181851),
                             Planet(planet_name='BD 9546 a', host_name='BD 9546', discovery_method='Disk Kinematics', discovery_year=2017, controversial_flag=True, orbital_period=768.080426639704, planet_radius=11.941312732971307, planet_mass=5330.140494100986, semi_major_radius=162.37991279555604, eccentricity=0.04985423017651025, equilibrium_temperature=512.6228553807089, insolation_flux=1812.819932737107),
                             Planet(planet_name='mu 3190 a', host_name='mu 3190', discovery_method='Pulsar Timing', discovery_year=2019, controversial_flag=True, orbital_period=219.4117236819676, planet_radius=5.823540960167899, planet_mass=8810.939175642656, semi_major_radius=120.5394261060936, eccentricity=0.024832776511679158, equilibrium_temperature=2219.046256814121, insolation_flux=1482.4324253666812),
                             Planet(planet_name='HD-3873 b', host_name='HD-3873', discovery_method='Astrometry', discovery_year=2015, controversial_flag=True, orbital_period=568.1241876285832, planet_radius=7.683343554455583, planet_mass=6674.648153520213, semi_major_radius=206.70498817306301, eccentricity=0.06416227724106294, equilibrium_temperature=2076.137821507021, insolation_flux=1193.4834428758786),
                             Planet(planet_name='CoRoT-6877 2', host_name='CoRoT-6877', discovery_method='Orbital Brightness Modulation', discovery_year=2016, controversial_flag=True, orbital_period=468.9144334401796, planet_radius=22.887019441116255, planet_mass=4883.38637786528, semi_major_radius=196.54514722939032, eccentricity=0.02439528254008245, equilibrium_temperature=992.6936203071889, insolation_flux=868.9818560127931),
                             Planet(planet_name='gam 1036 2', host_name='gam 1036', discovery_method='Eclipse Timing Variations', discovery_year=2015, controversial_flag=True, orbital_period=473.39019379384257, planet_radius=4.73450529009576, planet_mass=5883.3857261880985, semi_major_radius=26.481020621623102, eccentricity=0.012976552036785771, equilibrium_temperature=764.7268682017749, insolation_flux=341.38819227705574),
                             Planet(planet_name='bet 6224 1', host_name='bet 6224', discovery_method='Transit', discovery_year=2017, controversial_flag=True, orbital_period=220.67228753902634, planet_radius=6.303204740783587, planet_mass=4635.735987068731, semi_major_radius=105.92715659579545, eccentricity=0.0876107512928748, equilibrium_temperature=479.9421761399468, insolation_flux=1189.8306007574733),
                             Planet(planet_name='bet 1677 a', host_name='bet 1677', discovery_method='Imaging', discovery_year=2020, controversial_flag=True, orbital_period=925.9003393236126, planet_radius=3.2126670446506207, planet_mass=4156.138973145201, semi_major_radius=57.10455115692524, eccentricity=0.06732577815763748, equilibrium_temperature=804.796993133674, insolation_flux=886.2427020357001),
                             Planet(planet_name='EPIC 6933 1', host_name='EPIC 6933', discovery_method='Pulsation Timing Variations', discovery_year=2022, controversial_flag=True, orbital_period=702.9030644395948, planet_radius=16.26469735344537, planet_mass=9526.33890198421, semi_major_radius=204.19037214863022, eccentricity=0.09695020070892124, equilibrium_temperature=203.73446981514212, insolation_flux=989.9338167267724),
                             Planet(planet_name='ups 78234 1', host_name='ups 78234', discovery_method='Transit Timing Variations', discovery_year=2016, controversial_flag=True, orbital_period=286.5186617605516, planet_radius=8.094344795530386, planet_mass=6771.763654822986, semi_major_radius=70.04535793105076, eccentricity=0.03535831117727584, equilibrium_temperature=1520.9154619819722, insolation_flux=1578.1329372527273),
                             Planet(planet_name='2MASS 7335 b', host_name='2MASS 7335', discovery_method='Disk Kinematics', discovery_year=2020, controversial_flag=True, orbital_period=675.0245729874613, planet_radius=8.609744218362637, planet_mass=5937.3882277884395, semi_major_radius=92.09833858513112, eccentricity=0.0387732917550677, equilibrium_temperature=1010.3468071090423, insolation_flux=824.9192784437662),
                             Planet(planet_name='TOI 247 1', host_name='TOI 247', discovery_method='Transit Timing Variations', discovery_year=2019, controversial_flag=True, orbital_period=498.507496456924, planet_radius=6.831942368305831, planet_mass=3101.3285851295286, semi_major_radius=62.78930122207021, eccentricity=0.06795894299228161, equilibrium_temperature=1477.5889604284212, insolation_flux=1778.7997368672213),
                             Planet(planet_name='bet 1095 1', host_name='bet 1095', discovery_method='Eclipse Timing Variations', discovery_year=2019, controversial_flag=True, orbital_period=305.9715439790787, planet_radius=8.70887335827976, planet_mass=8672.571357768818, semi_major_radius=55.87183313489475, eccentricity=0.06577446882725858, equilibrium_temperature=1119.3415833015767, insolation_flux=2254.0951472242514),
                             Planet(planet_name='iot-5850 a', host_name='iot-5850', discovery_method='Eclipse Timing Variations', discovery_year=2018, controversial_flag=True, orbital_period=673.1262729746679, planet_radius=11.836381155942256, planet_mass=4454.3400880090485, semi_major_radius=176.74842066248303, eccentricity=0.029586470688984488, equilibrium_temperature=297.73713749371836, insolation_flux=2264.465414905977),
                             Planet(planet_name='tau 7155 1', host_name='tau 7155', discovery_method='Pulsar Timing', discovery_year=2019, controversial_flag=True, orbital_period=599.2348915162295, planet_radius=9.356211425532946, planet_mass=4987.631739804633, semi_major_radius=86.36003556415568, eccentricity=0.029732081601453162, equilibrium_temperature=1641.2440526521686, insolation_flux=1111.9472682436342),
                             Planet(planet_name='psi1-1283 1', host_name='psi1-1283', discovery_method='Imaging', discovery_year=2019, controversial_flag=True, orbital_period=380.0729309710997, planet_radius=10.128726667972954, planet_mass=5314.293303989357, semi_major_radius=49.792928958185165, eccentricity=0.04128292049132579, equilibrium_temperature=2185.271454855423, insolation_flux=869.2599563878713),
                             Planet(planet_name='Kepler 3387 a', host_name='Kepler 3387', discovery_method='Disk Kinematics', discovery_year=2018, controversial_flag=True, orbital_period=456.6918742987134, planet_radius=5.314663689529067, planet_mass=5409.4734708557635, semi_major_radius=150.45455138884952, eccentricity=0.08223375263881816, equilibrium_temperature=1948.8213225342674, insolation_flux=415.42426801351894),
                             Planet(planet_name='2MASS 5496 2', host_name='2MASS 5496', discovery_method='Transit Timing Variations', discovery_year=2017, controversial_flag=True, orbital_period=802.8237199213213, planet_radius=0.4651824029877609, planet_mass=5193.0187711864255, semi_major_radius=150.62032983942842, eccentricity=0.05082581764278138, equilibrium_temperature=1860.7380452298266, insolation_flux=2318.8131246110443),
                             Planet(planet_name='rho 2565 b', host_name='rho 2565', discovery_method='Astrometry', discovery_year=2017, controversial_flag=True, orbital_period=747.6182791157539, planet_radius=11.640310527812051, planet_mass=544.6514300920771, semi_major_radius=149.94307134385207, eccentricity=0.02613809638897717, equilibrium_temperature=916.4685478946134, insolation_flux=317.6339792000415),
                             Planet(planet_name='BD-4417 2', host_name='BD-4417', discovery_method='Eclipse Timing Variations', discovery_year=2017, controversial_flag=True, orbital_period=544.7310249448435, planet_radius=9.517043230040542, planet_mass=3561.2647356675116, semi_major_radius=69.03830110359388, eccentricity=0.04086273429920092, equilibrium_temperature=1054.02122959276, insolation_flux=2049.0528192601796),
                             Planet(planet_name='EPIC 9788 1', host_name='EPIC 9788', discovery_method='Astrometry', discovery_year=2014, controversial_flag=True, orbital_period=743.0258445875343, planet_radius=28.55356745335804, planet_mass=9132.459754379619, semi_major_radius=111.37350150566414, eccentricity=0.0782958024081785, equilibrium_temperature=1054.7753455109525, insolation_flux=399.71590029700883),
                             Planet(planet_name='WASP-9932 2', host_name='WASP-9932', discovery_method='Pulsar Timing', discovery_year=2020, controversial_flag=True, orbital_period=774.5431733595198, planet_radius=13.409187119034073, planet_mass=6539.224469919631, semi_major_radius=83.64684591326318, eccentricity=0.013317336320910284, equilibrium_temperature=938.6428111020809, insolation_flux=812.0640248539537),
                             Planet(planet_name='kap-2568 2', host_name='kap-2568', discovery_method='Transit Timing Variations', discovery_year=2019, controversial_flag=True, orbital_period=478.0958842371014, planet_radius=9.758136283546131, planet_mass=6680.418289986837, semi_major_radius=126.2352330630632, eccentricity=0.06570986476023272, equilibrium_temperature=1225.004381470806, insolation_flux=1613.1133852536218),
                             Planet(planet_name='bet-6229 1', host_name='bet-6229', discovery_method='Radial Velocity', discovery_year=2020, controversial_flag=True, orbital_period=507.52673014683353, planet_radius=8.952749578907646, planet_mass=7990.024062795348, semi_major_radius=167.95035610944524, eccentricity=0.02256462845928992, equilibrium_temperature=912.5640685127411, insolation_flux=1262.8748930315332),
                             Planet(planet_name='TOI 1596 1', host_name='TOI 1596', discovery_method='Pulsar Timing', discovery_year=2016, controversial_flag=True, orbital_period=659.9561047288468, planet_radius=7.997647992065991, planet_mass=4471.233908005521, semi_major_radius=152.68121077283823, eccentricity=0.05722724429178056, equilibrium_temperature=1817.5129861478683, insolation_flux=677.284751113594),
                             Planet(planet_name='iot 640 1', host_name='iot 640', discovery_method='Pulsar Timing', discovery_year=2017, controversial_flag=True, orbital_period=410.0822229225229, planet_radius=14.773030525463298, planet_mass=10907.977644907383, semi_major_radius=58.50950574922003, eccentricity=0.034821894068833965, equilibrium_temperature=1938.8640376038013, insolation_flux=1871.8763776145202),
                             Planet(planet_name='TOI 6733 2', host_name='TOI 6733', discovery_method='Microlensing', discovery_year=2019, controversial_flag=True, orbital_period=606.050392299604, planet_radius=4.061144353976646, planet_mass=6694.462986083521, semi_major_radius=95.10430906625423, eccentricity=0.06698280807302323, equilibrium_temperature=826.9711352067088, insolation_flux=2338.3057931258904),
                             Planet(planet_name='alf-7519 2', host_name='alf-7519', discovery_method='Imaging', discovery_year=2014, controversial_flag=True, orbital_period=701.5566392673566, planet_radius=11.640425172808346, planet_mass=2828.3456673266405, semi_major_radius=149.35946056945434, eccentricity=0.07156107881345741, equilibrium_temperature=1569.3043589878912, insolation_flux=1087.252135667285),
                             Planet(planet_name='gam-4664 1', host_name='gam-4664', discovery_method='Transit Timing Variations', discovery_year=2016, controversial_flag=True, orbital_period=386.4876714150311, planet_radius=13.255814542978666, planet_mass=4333.964900173164, semi_major_radius=108.13003401443521, eccentricity=0.05029507256593695, equilibrium_temperature=2121.442425240486, insolation_flux=1253.3108304766301),
                             Planet(planet_name='gam-4664 2', host_name='gam-4664', discovery_method='Pulsation Timing Variations', discovery_year=2019, controversial_flag=True, orbital_period=327.65937544553657, planet_radius=25.491547148748232, planet_mass=240.8729398246105, semi_major_radius=122.8544496611368, eccentricity=0.023873589744529997, equilibrium_temperature=1309.4242959458566, insolation_flux=956.4549627552219),
                             Planet(planet_name='WASP-9381 2', host_name='WASP-9381', discovery_method='Transit Timing Variations', discovery_year=2021, controversial_flag=True, orbital_period=392.366567912689, planet_radius=7.295177248236986, planet_mass=7681.743642493354, semi_major_radius=59.3757177894108, eccentricity=0.005473478686446827, equilibrium_temperature=529.63380616659, insolation_flux=1527.5231270961556),
                             Planet(planet_name='alf-5889 2', host_name='alf-5889', discovery_method='Transit Timing Variations', discovery_year=2016, controversial_flag=True, orbital_period=70.88358601214884, planet_radius=15.512133783313546, planet_mass=2814.266281644218, semi_major_radius=82.08076188625213, eccentricity=0.01989367859785502, equilibrium_temperature=1276.707743230407, insolation_flux=174.51016356797481),
                             Planet(planet_name='eps-9714 2', host_name='eps-9714', discovery_method='Orbital Brightness Modulation', discovery_year=2015, controversial_flag=True, orbital_period=392.6649140061448, planet_radius=15.839043553796536, planet_mass=6287.655008792294, semi_major_radius=49.960529240830894, eccentricity=0.04208861555895124, equilibrium_temperature=456.44077592475685, insolation_flux=1786.7261082096638),
                             Planet(planet_name='TOI 3335 2', host_name='TOI 3335', discovery_method='Radial Velocity', discovery_year=2019, controversial_flag=True, orbital_period=267.2921795428864, planet_radius=7.399019961228405, planet_mass=7882.99450678873, semi_major_radius=23.311946490166733, eccentricity=0.063027156352681, equilibrium_temperature=1654.5867595373982, insolation_flux=35.098204701949044),
                             Planet(planet_name='GJ 35829 2', host_name='GJ 35829', discovery_method='Transit', discovery_year=2019, controversial_flag=True, orbital_period=588.9367163292917, planet_radius=3.840879135082245, planet_mass=7613.262365166689, semi_major_radius=106.86439657502348, eccentricity=0.004393194873445576, equilibrium_temperature=1334.3726231919436, insolation_flux=1334.7074282643348)],
                     'q15': [Planet(planet_name='EPIC-2013 4', host_name='EPIC-2013', discovery_method='Imaging', discovery_year=2016, controversial_flag=True, orbital_period=294.40480618516006, planet_radius=15.653651979514894, planet_mass=4511.748564893384, semi_major_radius=256.739250973071, eccentricity=0.08271016440588383, equilibrium_temperature=1683.2309274346203, insolation_flux=634.0975256926524),
                             Planet(planet_name='GJ-72662 1', host_name='GJ-72662', discovery_method='Disk Kinematics', discovery_year=2018, controversial_flag=True, orbital_period=644.0360399474631, planet_radius=8.952277267217648, planet_mass=3986.8910114391715, semi_major_radius=150.01841870473035, eccentricity=0.02229105660877684, equilibrium_temperature=1138.807207101832, insolation_flux=1477.1699780181552),
                             Planet(planet_name='GJ-72662 2', host_name='GJ-72662', discovery_method='Orbital Brightness Modulation', discovery_year=2015, controversial_flag=False, orbital_period=155.00728770077046, planet_radius=11.76814859330932, planet_mass=4451.080581401704, semi_major_radius=134.1771586942319, eccentricity=0.06746650920282701, equilibrium_temperature=857.2390559605312, insolation_flux=1014.2239739465866),
                             Planet(planet_name='GJ-72662 3', host_name='GJ-72662', discovery_method='Disk Kinematics', discovery_year=2015, controversial_flag=True, orbital_period=856.5975064673971, planet_radius=8.010629409223158, planet_mass=1862.9261738216328, semi_major_radius=102.66913467484105, eccentricity=0.11423721965762434, equilibrium_temperature=1649.9491659478194, insolation_flux=1543.6174411147445),
                             Planet(planet_name='GJ-72662 4', host_name='GJ-72662', discovery_method='Astrometry', discovery_year=2018, controversial_flag=True, orbital_period=186.24591089807228, planet_radius=15.899190949595972, planet_mass=3004.4747992367115, semi_major_radius=14.75959296045366, eccentricity=0.0705938511601412, equilibrium_temperature=1469.925946123589, insolation_flux=2555.601978664983)],
                     'q16': [],
                     'q17': 0,
                     'q18': Star(spectral_type='G8.5/K5', stellar_effective_temperature=3536.240782471817, stellar_radius=40.27120509738957, stellar_mass=3.073465137878138, stellar_luminosity=1.5711877129587406, stellar_surface_gravity=4.2468135088214245, stellar_age=30.4),
                     'q19': 11.71929549067841,
                     'q20': [Planet(planet_name='GJ 5131 a', host_name='GJ 5131', discovery_method='Imaging', discovery_year=2020, controversial_flag=False, orbital_period=156.65399299139688, planet_radius=9.182332137443156, planet_mass=6571.512146326467, semi_major_radius=87.18350826245653, eccentricity=0.057447342716581154, equilibrium_temperature=1168.3042732042409, insolation_flux=1698.56809809976)]}
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
