import random


# This is an example bot written by the developers!
# Use this to help write your own code, or run it against your bot to see how well you can do!

board_size = 16
team = None
opp_team = None
robottype = None
backRow = 0
row, col = 0,0

#PAWN

sensor_radius = 2

#OVERLORD
pawn_bias_L1 =[-1.55488, -9.070385, -1.921395, 1.044084, -7.058015, 2.446507, -0.913281, -4.424844, -1.795319, 2.929282, 3.098898, 1.281449, -9.3419, 0.549151, -0.470901, 0.581322, 3.91486, 3.100342, 1.178062, 4.883814]
pawn_bias_L2 =[0.439866, 9.686166]
pawn_weights_L2 =[[-0.880082, 8.113153], [0.888752, 9.948926], [4.819789, 0.790384], [-6.099065, 0.23384], [-0.499315, -2.961414], [-0.820322, 3.383643], [-0.702689, 6.653137], [-0.441499, 7.504966], [-8.774063, 4.444711], [1.742804, 1.675386], [4.913956, -3.403208], [-0.363786, -0.204379], [9.703281, 12.088667], [0.729667, 0.374009], [-0.272519, 1.088618], [-0.47876, 0.735881], [0.617007, -8.908237], [6.294164, -6.64664], [9.359203, -8.62672], [-10.691625, -2.610057]]
overlord_weights_same_allied = [
[-64,-63,-62,-61,-60,-59,-58,-57,-56,-55,-54,-53,-52,-51,-50,-49], #on border
[-64,-63,-62,-61,-60,-59,-58,-57,-56,-55,-54,-53,-52,-51,-50,-49], #one away from boarder
[-64,-63,-62,-61,-60,-59,-58,-57,-56,-55,-54,-53,-52,-51,-50,-49]] #all other possibilities

overlord_weights_same_enemy = [
[0,1000,700,14,13,12,11,10,9,8,7,6,5,4,3,2],
[0,1000,700,14,13,12,11,10,9,8,7,6,5,4,3,2],
[0,1000,700,14,13,12,11,10,9,8,7,6,5,4,3,2]]

overlord_weights_adjacent_allied = [
[10,9.5,9,8.5,8,7.5,7,6.5,6,5.5,5,4.5,4,3.5,3,2.5],
[10,9.5,9,8.5,8,7.5,7,6.5,6,5.5,5,4.5,4,3.5,3,2.5],
[10,9.5,9,8.5,8,7.5,7,6.5,6,5.5,5,4.5,4,3.5,3,2.5]]

overlord_weights_adjacent_enemy = [
[0,-500,15,14,13,12,11,10,9,8,7,6,5,4,3,2],
[0,-500,15,14,13,12,11,10,9,8,7,6,5,4,3,2],
[0,-500,15,14,13,12,11,10,9,8,7,6,5,4,3,2]]


sameRowAlliedPawnWeight = -64
adjacentRowAlliedPawnWeight = 0

sameRowEnemyPawnWeight = 16
adjacentRowEnemyPawnWeight = 16

sameRowAlliedPawnDistanceMultiplier = 1
adjacentRowAlliedPawnDistanceMultiplier = 0

sameRowEnemyPawnDistanceMultiplier = -1
adjacentRowEnemyPawnDistanceMultiplier = -1

enemyOneTileAwayWeight = 1000
enemyTwoTilesAwayWeight = 700
enemyOneAdjacentTileAwayWeight = -500

DEBUG = 1
def dlog(str):
	if DEBUG > 0:
		log(str)



def check_space_wrapper(r, c):
	# check space, except doesn't hit you with game errors
	if r < 0 or c < 0 or c >= board_size or r >= board_size:
		return False
	try:
		return check_space(r, c)
	except:
		return None

def turn():

	if robottype is None:
		init()

	if robottype == RobotType.PAWN:
		pawn_turn()
	else:
		overlord_turn()

	bytecode = get_bytecode()
	dlog('Done! Bytecode left: ' + str(bytecode))

def init():
	global board_size, team, opp_team, robottype, backRow, forward

	board_size = get_board_size()

	team = get_team()

	robottype = get_type()

	if team == Team.WHITE:
		backRow = 0
		forward = 1
		opp_team = Team.BLACK
	else:
		backRow = board_size - 1
		forward = -1
		opp_team = Team.WHITE

	if robottype == RobotType.PAWN:
		pawn_init()
	else:
		overlord_init()

##############################################################
############################ PAWN ############################
##############################################################

def pawn_init():
	return

def dist_to_side(column):
	dist1 = column
	dist2 = board_size-1-column
	return dist1 if dist1 < dist2 else dist2

def check_right():
	return check_space_wrapper(row + forward, col + 1) == opp_team

def check_left():
	return check_space_wrapper(row + forward, col - 1) == opp_team

def check_right2():
	return check_space_wrapper(row + forward*2, col + 1) == opp_team

def check_left2():
	return check_space_wrapper(row + forward*2, col - 1) == opp_team

def check_right_adjacent_ally():
	return check_space_wrapper(row, col + 1) == team

def check_left_adjacent_ally():
	return check_space_wrapper(row, col - 1) == team

def capture_right():
	capture(row + forward, col + 1)

def capture_left():
	capture(row + forward, col - 1)

def can_move_forward():
	return row + forward != -1 and row + forward != board_size and not check_space_wrapper(row + forward, col)

def close_to_enemy_side():
	distance = abs(row-backRow)
	return distance >= board_size-3

def pawn_weights_L1_generator(i):
	pawn_weights_L1=[]
	if i == 0:
		pawn_weights_L1 = [-0.663459, -6.076977, -12.964345, 5.568164, -0.205287, -6.619921, -10.849402, -5.277583, 6.971651, 0.449585, -5.890716, -4.945722, -1.852586, 0.164263, 0.573121, -5.444384, -5.918033, 4.126374, 24.805051, 1.242718, 0.578608, 0.463992, -10.309168, -5.735557, -1.475967, 5.672515, -2.11907, -0.845694, 0.454198, -0.328345, 0.791318, 0.218439, 3.49358, 0.250497, -4.057744, 2.2799, -8.306117, -0.393475,
		-1.323643, 0.016052, -0.468809, -9.004918, -1.704542, 0.378988, -7.228064, -7.821859, -0.625108, 8.038314, -2.160396, 0.10103, -0.046312, -4.830034, -0.852112, -6.757444, -0.863494, 5.280013, 5.550562, -1.092596, 0.20853, 0.457118, 0.419888, 6.65033, 0.758446, -0.136775, 11.412931, 2.228013, 3.825776, -1.867908, -1.270747, 1.07769, -1.4196, -5.432985, -0.210082, 0.384095, -0.948773, -0.515745]
	elif i == 1:
		pawn_weights_L1 = [-3.103816, 3.33915, 7.720432, -4.848466, -0.808121, 0.945847, 2.893927, -12.952623, -1.886916, -0.4058, -0.003274, 0.508916, 0.080791, -0.301678, -0.857347, 0.307331, 5.263055, -8.656005, 0.554778, -3.659749, 0.066221, -1.606839, -1.117186, 8.894675, -2.129494, 6.990906, 0.26792, 6.418704, -0.685166, 3.009178, 7.731768, 6.658054, -5.566953, -6.294657, -3.21436, 0.120121, -0.41456, 4.620685,
		-4.502925, 3.040855, -3.601185, 2.627055, 1.55098, 0.159265, -0.846024, 3.912947, -1.850137, -8.375857, -5.715286, 2.218294, -5.253524, 16.89872, 2.98306, 0.084811, -0.430025, -6.493573, 0.084277, -0.244347, -0.771013, -1.803947, -0.378134, -0.198514, 7.65784, -7.417766, -2.492922, -1.73351, -11.15541, -0.410781, 2.742902, -6.017085, 0.635986, -0.176598, -0.288567, 0.25456, 1.287418, -1.84289]
	elif i == 2:
		pawn_weights_L1 = [0.559292, -4.59618, 5.472937, -8.544897, 0.440934, 0.49063, 5.439701, 3.43736, 1.819653, 7.274923, 5.85413, 2.123456, -12.343175, -1.863957, 2.597487, 4.610532, -0.523591, -1.002361, 2.847213, -0.00704, 4.671524, -0.489077, -3.201713, 0.323728, 4.487324, 1.057446, -2.799772, 5.525274, 0.514124, -9.925058, -2.116548, -4.10803, 0.008051, 0.827485, 0.930699, -3.241633, 6.047476, 0.341383,
		-0.244736, -1.181684, -3.251837, -3.361238, -0.538552, -10.076953, -0.921234, 2.016602, -12.594794, 0.466719, -0.30265, -4.938001, -0.155015, -7.97187, -12.389222, -6.311141, -0.586553, -0.290736, -0.03407, 9.483161, -0.952379, -3.280442, -0.281456, -9.302407, 6.531826, 6.328391, 6.233162, 0.296984, 9.749007, -0.122218, -1.65408, 12.487058, -8.428803, -9.196532, 7.038677, 6.628315, 2.644083, -3.958073]
	elif i == 3:
		pawn_weights_L1 = [-5.189302, 0.724242, -1.571503, -5.699804, -2.657959, -0.292888, -4.087089, -3.01554, -0.427963, -0.764039, 4.909984, 0.97732, -4.290206, -6.762742, -1.88463, -6.505987, -4.606279, -14.772099, 0.397593, 0.642627, 0.285928, -1.186188, -0.423484, -0.18834, -3.91143, -0.743598, 2.879165, -0.519512, -2.648203, 0.299543, -1.077998, 0.615968, -8.957533, -0.416527, -1.725925, 9.249296, -1.308696, 0.047818,
		-7.511618, -1.454541, -10.858444, 5.59333, -1.099467, 1.169568, -3.623411, -0.176058, -5.582968, 10.2385, -3.588656, -0.190363, 0.547087, 1.020902, 3.488015, -0.763035, -1.146044, 8.087647, 1.976363, 11.908113, 0.528475, -3.289577, 0.127134, 0.075363, 3.281282, -4.573378, 0.075562, -0.275565, -3.784511, 3.770192, -2.317256, 0.890647, -8.426121, 0.690111, -9.763665, -4.249992, -0.151394, -0.670645]
	elif i == 4:
		pawn_weights_L1 = [7.221538, 0.821546, -0.22979, 7.473349, -4.914648, -0.544854, 0.899931, 0.714963, -0.912578, 0.783268, -0.206364, -8.5779, 4.785157, -0.856013, -0.145642, 2.798294, 0.417882, -0.626085, -0.275784, 0.636862, -2.855362, 0.709929, -0.256791, -4.067787, -0.314288, -3.809763, -6.149055, 0.451111, -3.388962, 1.752243, -3.13608, 9.733898, -0.280555, -2.368599, -0.111481, 7.535859, 5.479383, 0.541989,
		0.426617, 0.066195, 1.625642, 8.859844, -0.29145, 2.979402, -0.604688, -8.523018, 5.75732, -7.189272, -3.295517, 4.978929, -9.448614, 6.640668, 0.240456, 0.497291, -0.167843, 0.144081, 8.383302, -0.23339, 4.929562, -0.563162, -4.4027, 1.273908, 3.868833, 5.607143, 3.649067, 4.037311, 0.332184, 0.086573, -3.681967, 1.712345, -6.753387, -0.486436, -0.731626, -0.129291, -7.581865, 1.068137]
	elif i == 5:
		pawn_weights_L1 = [-9.199352, -2.238861, -2.322556, 1.07588, 9.912115, 0.658604, -0.251131, 0.951824, -5.529744, 9.256663, 0.455599, 3.157777, 5.075047, -6.385322, 6.497841, -6.403046, 0.829926, -0.551855, -1.424515, -8.063989, 6.350282, -5.074993, -4.941319, -6.058692, -0.173292, 0.577851, 0.202608, 1.179648, 0.156436, -0.689304, -0.2261, 3.968933, 3.388215, 13.830309, -0.800366, 7.26889, -0.373804, 0.488749,
		9.128741, -0.710414, -2.016199, -2.375236, -6.185713, -0.459307, 5.495405, 0.872011, -1.201774, -5.526335, 0.289482, 0.948482, 0.206726, 3.715541, 1.578364, 2.230908, -1.636478, 4.357522, -11.62126, -3.522678, 8.935917, -8.606806, -0.047418, 2.218089, -3.862968, -4.41341, -8.254809, 4.008937, 0.056805, 2.034363, -0.061341, -14.435569, 0.043966, 5.426977, 0.840613, 11.442606, -12.525785, 0.111486]
	elif i == 6:
		pawn_weights_L1 = [-10.149135, -8.287332, -0.632248, 0.433966, 0.46551, 9.59758, -8.034715, -3.394505, -0.402234, 0.834749, -0.718134, 0.357113, 8.756929, -8.982639, -0.818945, -6.128385, -0.485059, 0.396268, -0.106404, -0.234853, 0.019701, -5.886216, 0.561892, 0.867404, 9.628691, -0.282443, -2.282065, -0.639267, -0.682974, -3.644592, -6.073593, 0.439636, 4.297783, -8.013176, 1.901203, 0.999482, 4.229091, -0.410253,
		0.982439, -0.630243, -6.908664, -1.263301, -0.387783, 3.413102, 2.182179, -5.446113, -6.579903, 0.236473, 0.503693, 0.352642, -0.887104, -0.794631, -1.56293, 0.604428, 0.171763, -2.283575, -10.146116, -0.037935, 1.128745, 2.616818, 5.401802, -9.330886, 0.552829, 2.505659, 7.54376, -0.560977, -8.006876, -0.439331, 6.040291, 3.624964, -3.973068, -0.072381, 4.119482, 1.004845, 0.33727, 0.455528]
	elif i == 7:
		pawn_weights_L1 = [9.82979, -7.941445, 11.82376, -0.631637, 1.001727, 0.313528, 0.56023, -0.787841, -0.664725, -0.006959, 3.378802, -0.496924, 0.394686, -0.184801, -9.629487, 9.710048, 3.188882, -4.443759, 0.506456, 0.787484, -5.476146, -6.834759, 0.431334, -3.006779, -0.015376, -0.749233, -1.222095, 8.592696, -0.122281, 0.062199, 7.164079, 7.1068, 0.687635, 0.728057, -4.380373, 0.733013, 3.575533, -8.237389,
		22.938031, 1.472112, -3.823178, -0.317792, 1.851184, -2.580206, -0.10387, -1.895636, -0.33385, 1.638783, -0.78171, 5.742581, 3.777962, 0.2653, -4.170024, -3.45724, -1.013111, -0.588534, 0.156052, -7.980509, 8.880792, 0.284473, -4.113581, -0.337719, 0.220888, 0.010274, 1.726842, -1.892253, -9.452772, 4.537977, 0.199484, 0.596182, -5.143998, -0.313431, -0.601325, 0.010885, 0.200632, -2.492951]
	elif i == 8:
		pawn_weights_L1 = [-0.437648, -8.156607, -2.062046, 0.146879, -1.211162, 0.91509, -0.886778, 1.191169, 2.171539, -5.669834, -3.641314, 7.153895, -7.147441, 3.685035, -8.860861, -1.882048, -9.874603, 1.160566, 0.853337, 9.860748, -4.700621, -4.99872, -0.337749, 0.207654, -10.319162, 1.911751, -5.951669, -7.745738, -9.140966, -1.873967, -1.471542, 0.612568, 2.316427, -7.852533, -10.85581, -0.533602, 1.026055, -0.3302,
		5.153258, 1.417772, -6.081575, 1.098989, -0.15933, -6.941164, 9.303939, 0.482899, 5.368113, 2.253618, 4.829524, 8.019086, 8.345658, -3.359954, -0.564888, -2.483106, 1.687032, 8.112932, 8.888244, -0.075465, -2.202596, -4.076553, -0.167716, -2.284634, -0.633543, 8.125736, -5.806266, -9.040685, 0.866789, 2.512937, 9.829638, -1.648276, 6.026893, -7.366391, 6.955085, -0.781187, 0.571851, 4.00545]
	elif i == 9:
		pawn_weights_L1 = [0.627197, 9.963641, 4.401136, -8.516678, -6.367272, -0.018823, 6.708833, 0.769632, -1.932364, 0.362372, -1.292426, -0.308709, 1.682256, 3.02876, -4.075164, -3.702462, 9.551413, -2.302155, -5.010478, -3.144256, -0.111584, -0.630592, -7.445575, 0.226075, 0.303788, -0.28095, 4.758494, -3.730547, 0.529742, -7.491452, 14.490625, -0.052657, -2.811236, -7.417635, -1.527952, -6.478653, -5.44834, 6.816375,
		-9.190948, -1.166449, 5.532557, 6.758504, 0.865987, 10.623447, -6.149684, 4.381585, -0.450156, 1.805649, -3.891215, 2.572912, 1.359325, -8.467287, 5.221002, 0.475359, 0.665626, -11.297334, -0.053721, 8.522666, -0.907647, -0.600764, -9.124353, -1.771458, -4.381602, -2.720331, 1.302679, -7.172481, 0.079695, 7.015466, 3.792581, 1.280866, -8.426444, 0.023045, 1.060218, 2.077788, -7.291034, 0.186474]
	elif i == 10:
		pawn_weights_L1 = [0.222694, 0.301283, 1.01973, 0.99984, 3.425466, -2.451086, -8.18649, 6.063912, 8.400944, 2.024814, -9.909802, 4.852966, 0.064189, 7.360716, -4.749324, -4.419464, 11.667449, 4.002169, -1.222845, -4.359857, 3.490378, -3.253975, -1.413942, -0.612622, 3.464346, -0.820781, -5.719077, -0.527724, 2.562146, 0.052778, 0.023055, 4.571897, -0.900814, 5.137826, -6.292971, 2.447444, 0.090402, -0.835646,
		0.570389, -7.596753, 0.603447, -2.178595, -0.51503, -0.72627, -0.526893, 0.935451, 4.874676, 2.821647, -2.040446, 0.001248, -2.887813, 2.247368, -5.48735, 0.17914, 0.72726, 7.540525, -0.209084, -6.94569, -5.995575, -0.113209, -1.343652, -0.968335, -0.430178, -6.602408, -1.391075, -0.890289, -5.77268, 4.322031, -6.317539, 4.818819, 1.1927, -1.020876, 0.039611, 1.593579, -0.897801, 7.548726]
	elif i == 11:
		pawn_weights_L1 = [1.280615, -2.694935, -5.47835, -2.798785, -7.368015, -0.243631, 0.18125, -6.964816, 0.464462, 5.264691, -0.146415, 0.877729, 3.646641, 2.836391, 3.488862, -7.881502, -2.557227, -7.691918, -3.736892, -0.52288, 4.786555, -6.172034, 6.330228, 5.958991, -1.070795, 9.509971, 0.619248, 0.799143, 0.913545, 8.909128, 7.447676, 3.232464, -9.016457, -5.167787, -0.295718, 5.399683, -1.179733, -5.993088,
		1.508674, -5.294057, 0.386457, -11.496035, -6.385282, -2.034689, -9.290114, 8.240456, -5.658696, 1.68724, 0.472221, -1.250716, -0.740766, -0.774395, 0.448419, 0.356119, -1.018301, -1.336417, 3.789939, -8.379407, -7.91649, 0.078878, 2.496643, -0.120366, 1.191311, 0.045374, 9.301216, -8.448768, 0.213924, -0.176017, 0.463966, -6.575076, 6.149846, 0.453706, 7.84744, 4.221375, -0.480713, -2.111243]
	elif i == 12:
		pawn_weights_L1 = [10.388921, 3.086245, -0.267, -0.878435, -5.136311, 0.157622, -0.214117, -8.50323, 9.13979, -0.250761, -2.213954, -0.694677, 0.69615, -9.145666, 1.528774, -6.725611, 8.873395, 3.231432, -7.008054, -2.069613, 11.264268, -0.711961, -0.946567, 6.841485, 0.29707, 5.289925, -0.392681, 1.998448, -3.803491, 6.561839, -0.673068, 0.715931, -0.092318, -7.959008, -0.704367, -0.329431, 0.876384, 0.973938,
		2.687499, -3.425382, -7.168278, -4.552897, 0.217366, -1.972192, 9.000037, -0.242169, 7.557077, 4.968008, -4.27056, -0.26465, -6.195624, -0.97691, 5.560747, 9.384778, -0.81659, -0.077167, 5.484689, 0.28168, -6.817956, 0.927015, -7.226313, 6.549488, 1.378998, -0.715783, -0.060689, -0.366154, 0.41758, -0.429958, -6.61711, -4.124215, 1.013701, -0.611186, 0.992649, 0.014727, 0.654959, -3.227496]
	elif i == 13:
		pawn_weights_L1 = [-0.910803, 2.223254, 0.336513, 11.618305, 5.486307, -0.659841, -0.373427, 0.395835, -3.183156, 2.014709, -6.708258, -0.416148, -4.217678, -6.903848, -4.821169, -1.804041, -0.711775, -6.064806, -0.248134, -4.198452, 0.925243, 0.57188, 0.357957, 8.782594, 0.170656, -6.605797, -0.538474, -0.87711, -0.929508, -0.850443, -0.491339, 0.879963, 0.391219, -0.18921, 0.329549, -8.477418, 3.433511, -0.00728,
		-0.020543, -0.008985, -2.211972, -0.577771, -4.717851, -0.903207, -0.116769, 8.723661, -9.344857, -0.50375, -1.526935, 0.950624, -0.474628, -0.112939, -5.807802, -4.993933, -0.046115, -7.854823, -1.674274, 10.248536, -2.873394, 0.729331, -0.391497, -0.38909, 0.780827, 8.774249, -2.132083, -0.064833, 2.172693, -1.057135, -3.235132, 3.014676, -1.075039, -0.461561, -1.621012, 4.520843, -0.374214, 2.133926]
	elif i == 14:
		pawn_weights_L1 = [-6.700734, 9.698296, 9.994433, -0.654866, -8.479207, 2.312615, 12.761055, 7.030317, 0.57204, -0.121816, 0.250336, 0.125339, 0.378497, -0.233204, 9.354991, 0.204352, -6.47083, 1.358406, 4.355543, -3.060524, 0.752404, 4.87831, 6.556864, 5.078945, -0.337478, 2.436513, -2.495922, -5.460103, -0.007962, 2.596842, 12.567882, 0.835661, 9.114089, -0.239691, -5.955504, -2.19695, -10.499913, -2.855033,
		0.193561, 0.060458, -0.580665, 1.709278, 0.927162, 5.944212, 1.339787, 5.064027, -0.55313, -0.967974, 0.124551, -0.156265, -0.063565, 8.34301, 0.784378, -0.730747, 9.377946, -4.730687, -3.088829, -8.818399, -7.443763, 4.289177, 0.118014, -5.725266, -3.087174, -6.353929, -8.002299, 5.535711, 9.365411, 2.806735, -0.559868, 0.405091, -1.931428, 0.136127, -3.340096, -0.259454, -0.154015, 7.295229]
	elif i == 15:
		pawn_weights_L1 = [6.110509, 0.262138, 2.511089, 6.114316, -8.341581, -0.286653, -0.486488, 0.30735, -0.651285, 2.791206, 3.911491, 0.462833, -0.793804, 0.737531, -0.810585, 0.462234, 0.567818, -2.87035, 0.635403, -6.274376, -1.58309, 5.856001, -4.240314, 0.659464, -0.034468, -1.098077, -0.673208, 2.883519, -0.324199, -9.117864, -2.272562, -3.983615, 0.452879, 1.924634, 7.474335, -0.307549, -2.13012, -1.365424,
		8.509485, 6.532629, 0.740993, -8.022775, 8.495182, 1.647402, -5.850733, -0.32051, 0.475161, -0.323184, -6.369016, 1.295104, -8.27898, -5.785326, -1.578441, 5.351721, 2.963924, 6.879505, 3.753711, -3.922946, 6.991171, 2.151267, 3.874347, -3.029612, -1.165833, -8.236022, 0.420188, -7.023304, 0.665903, 0.243611, 1.338632, -8.156411, -8.929137, -3.477902, -0.478385, 5.336645, -1.280566, 6.683551]
	elif i == 16:
		pawn_weights_L1 = [-1.960107, 10.618845, 9.402988, -0.024449, -0.246262, 6.870171, 14.770741, -1.027202, 6.74596, -3.865896, 7.008352, 0.757421, 9.684182, -0.683772, -5.131941, -9.681333, 9.551498, 0.120438, -8.845988, -9.333553, 5.320222, -1.234587, 0.324827, 3.804626, -3.885399, 4.189747, 0.813296, 0.417702, -7.935507, -0.096491, 8.539988, -0.702008, -1.151087, -0.521314, -0.812942, 1.21774, -0.066862, 0.007189,
		1.892381, 9.37245, 11.023045, 5.364734, 0.525215, -1.740031, -5.65985, -10.214913, 0.725294, -1.15231, -0.023985, -1.725623, -6.512843, 8.227183, 10.385173, -1.497866, 6.184605, 0.238663, -0.607429, -0.089909, 0.739197, -6.11455, -4.044768, -0.310841, -4.54261, -2.095611, -0.271957, 5.700615, -9.224751, -0.302751, 6.18645, 12.809045, 0.586472, 0.778299, 0.837298, -0.821797, 11.706052, 0.006822]
	elif i == 17:
		pawn_weights_L1 = [-0.111732, 7.392379, -0.675657, -0.485789, -0.033873, 0.516773, 8.982731, -0.262192, 2.06089, 0.592896, -2.520263, 0.245447, -7.122605, -0.02358, 0.083896, 9.674792, -3.353359, -6.406976, 0.423915, 6.703394, 0.054322, 0.67461, 0.228529, -0.627219, 0.129546, 0.037028, 13.226305, 0.796092, -0.708475, -7.182149, 2.804907, 12.626937, 4.651403, -4.418963, -1.891083, 1.035178, 2.919632, -0.654818,
		0.827219, -3.760684, 0.39845, -0.745803, -0.436643, 7.465923, -2.695033, 9.150836, 0.790114, -3.442515, -4.18965, -1.65041, 4.499979, 9.388987, -2.97242, -5.729731, 0.394891, -0.289261, 3.420373, 3.721246, -7.451353, -2.25183, 0.421903, 4.809125, 6.108881, -9.032555, -11.627732, 9.393895, -6.203784, -9.174893, -0.777334, -0.149311, 0.30751, 0.754094, -2.569866, 7.740742, -0.50007, 0.600352]
	elif i == 18:
		pawn_weights_L1 = [-0.829913, -0.408863, 5.820753, 7.535275, 0.337526, -4.189335, 5.033619, 0.399602, -0.347657, 0.739848, -2.416319, -0.607258, 6.03011, -0.320711, 6.579418, 3.096079, 0.79343, 0.109999, 6.736159, -9.002772, 0.085617, -6.557324, -1.386861, -1.591108, -0.06018, -0.299869, -0.696147, 1.993327, -4.811771, 8.70863, -0.679022, 0.840184, -0.161503, -0.120878, -2.509655, 4.966984, -5.206447, -5.295347,
		0.493009, 0.296876, -4.404127, 1.088691, -0.022735, -3.413124, 9.14666, 2.642334, 7.887569, -0.067232, -5.560439, 6.423099, -0.5638, -5.82366, -3.122401, 1.909553, 4.315752, -0.620347, -8.256459, 6.86542, 1.129807, 7.827382, 0.5711, -1.372563, -0.18153, 2.375234, -0.360358, -5.823846, 12.313075, 6.647149, -5.837319, -4.070232, -4.542162, -0.116777, 0.044991, 8.275619, 0.240277, -3.276251]
	elif i == 19:
		pawn_weights_L1 = [-1.477443, 0.054115, 0.223094, -0.385747, 5.514665, 2.900237, 0.348336, -7.628612, -6.728794, -5.500953, 5.172258, 1.066442, -4.868813, 0.03033, 0.80636, 0.46083, -9.789879, -0.186275, -2.018995, 6.462244, 9.125453, -3.948754, 9.298992, 0.173429, -0.10273, -3.72932, -4.237128, -6.502951, 0.02338, -5.612887, 0.648202, 3.748107, 3.931231, -0.57964, -2.489837, 7.537585, -3.280122, 5.175315,
		2.222974, -11.162103, -3.361047, 1.409655, 0.27915, 1.260783, -5.267728, 7.472281, 0.562522, 6.335312, -0.446177, 10.332954, -1.633438, 6.887719, 13.467638, 0.441233, 0.83758, 0.139943, -0.917911, 1.439261, -6.588635, -7.489732, -0.123203, 0.570855, -2.793804, -0.255267, -0.822515, 0.143365, 11.516794, 0.534435, 0.156653, 0.127792, 0.115416, -4.565545, -1.292128, -1.219508, -3.533131, 0.459672]
	return pawn_weights_L1

def pawn_turn():
	global row,col
	
	row, col = get_location()

	first_layer = []
	if team == Team.WHITE:
		for i in range(-sensor_radius, sensor_radius+1):
			to_print = ""
			for j in range(-sensor_radius, sensor_radius+1):
				if i == 0 and j == 0:
					continue
				pawn = check_space_wrapper(row+i, col+j)
				to_print=to_print+" "+str(pawn)
				if pawn == team:
					first_layer.append(1)
					first_layer.append(0)
					first_layer.append(0)
				elif pawn == opp_team:
					first_layer.append(0)
					first_layer.append(1)
					first_layer.append(0)
				else:
					first_layer.append(0)
					first_layer.append(0)
					first_layer.append(1)
	else:
		for i in range(sensor_radius, -sensor_radius-1, -1):
			to_print = ""
			for j in range(sensor_radius, -sensor_radius-1, -1):
				if i == 0 and j == 0:
					continue
				pawn = check_space_wrapper(row+i, col+j)
				to_print=to_print+" "+str(pawn)
				if pawn == team:
					first_layer.append(1)
					first_layer.append(0)
					first_layer.append(0)
				elif pawn == opp_team:
					first_layer.append(0)
					first_layer.append(1)
					first_layer.append(0)
				else:
					first_layer.append(0)
					first_layer.append(0)
					first_layer.append(1)

	first_layer.append(dist_to_side(col))
	first_layer.append(abs(row-backRow))
	if col == 0 or col == board_size-1:
		first_layer.append(1)
	else:
		first_layer.append(0)
	if col == 1 or col == board_size-2:
		first_layer.append(1)
	else:
		first_layer.append(0)

	second_layer = []
	second_layer_len = 20
	#test_weights = [[random.randint(0,10) for x in range(len(first_layer))] for y in range(second_layer_len)]

	for i in range(second_layer_len):
		value = pawn_bias_L1[i]
		pawn_weights_L1 = pawn_weights_L1_generator(i)

		
		for j in range(len(first_layer)):
			value += first_layer[j] * pawn_weights_L1[j]
		second_layer.append(value)
		#del pawn_weights_L1[:]
	#dlog('Second layer values: ' + str(second_layer))

	#third layer
	output_layer = []
	output_layer_len = 2

	for i in range(output_layer_len):
		tempValue = pawn_bias_L2[i]
		for j in range(second_layer_len):
			dlog(str(i)+" "+ str(j))
			try:
				tempValue += second_layer[j] * pawn_weights_L2[j][i]
			except:
				hello = "hello"
		output_layer.append(tempValue)
	#dlog('Output layer values: ' + str(output_layer))
	log(str(output_layer[0])+" "+str(output_layer[1]))
	if check_right(): # up and right
		capture_right()

	elif check_left(): # up and left
		capture_left()

	# otherwise try to move forward
	elif can_move_forward() and output_layer[0] > output_layer[1]:
		#if row < whiteHalfway:
		move_forward()

	confusion = "you need a line here to avoid segfault. we aren't sure why but are working on it"
	# ^ I think this is related to the potential ambiguity of what the following else is referring to?

##############################################################
########################## OVERLORD ##########################
##############################################################

def overlord_init():
	global backRow
	if team == Team.WHITE:
		backRow = 0
	else:
		backRow = board_size - 1

def spawn_weights_pro_plus_max_xyz(board):
	weights = []
	for tempCol in range(board_size):
		weights.append(0)

		weight_index = dist_to_side(tempCol) # different weights depending on how far away from the wall
		if weight_index > 2:
			weight_index = 2 #limit is 2 away

		#check same col
		for tempRow in range(board_size):
			pawn = board[tempRow][tempCol]
			if pawn != None: # there is a pawn
				distance = abs(tempRow-backRow) # distance to pawn from your back row
				if pawn == team: # your pawn
					weights[tempCol] = weights[tempCol] + overlord_weights_same_allied[weight_index][distance]
				else: # enemy pawn
					weights[tempCol] = weights[tempCol] + overlord_weights_adjacent_allied[weight_index][distance]

		#check left adjacent col
		if tempCol > 0:
			for tempRow in range(board_size):
				pawn = board[tempRow][tempCol-1]
				if pawn != None: # there is a pawn
					distance = abs(tempRow-backRow) # distance to pawn from your back row
					if pawn == team: # your pawn
						weights[tempCol] = weights[tempCol] + overlord_weights_same_enemy[weight_index][distance]
					else: # enemy pawn
						weights[tempCol] = weights[tempCol] + overlord_weights_adjacent_enemy[weight_index][distance]

		#check right adjacent col
		if tempCol < board_size-1:
			for tempRow in range(board_size):
				pawn = board[tempRow][tempCol+1]
				if pawn != None: # there is a pawn
					distance = abs(tempRow-backRow) # distance to pawn from your back row
					if pawn == team: # your pawn
						weights[tempCol] = weights[tempCol] + overlord_weights_same_enemy[weight_index][distance]
					else: # enemy pawn
						weights[tempCol] = weights[tempCol] + overlord_weights_adjacent_enemy[weight_index][distance]
	return weights

def spawn_weights(board):
	weights = []
	for tempCol in range(board_size):
		weights.append(0)

		#check same col
		for tempRow in range(board_size):
			pawn = board[tempRow][tempCol]
			if pawn != None: # there is a pawn
				distance = abs(tempRow-backRow) # distance to pawn from your back row
				if pawn == team: # your pawn
					weights[tempCol] = weights[tempCol] + sameRowAlliedPawnWeight + sameRowAlliedPawnDistanceMultiplier * distance
				else: # enemy pawn
					weights[tempCol] = weights[tempCol] + sameRowEnemyPawnWeight + sameRowEnemyPawnDistanceMultiplier * distance

		#check left adjacent col
		if tempCol > 0:
			for tempRow in range(board_size):
				pawn = board[tempRow][tempCol-1]
				if pawn != None: # there is a pawn
					distance = abs(tempRow-backRow) # distance to pawn from your back row
					if pawn == team: # your pawn
						weights[tempCol] = weights[tempCol] + adjacentRowAlliedPawnWeight + adjacentRowAlliedPawnDistanceMultiplier * distance
					else: # enemy pawn
						weights[tempCol] = weights[tempCol] + adjacentRowEnemyPawnWeight + adjacentRowEnemyPawnDistanceMultiplier * distance

		#check right adjacent col
		if tempCol < board_size-1:
			for tempRow in range(board_size):
				pawn = board[tempRow][tempCol+1]
				if pawn != None: # there is a pawn
					distance = abs(tempRow-backRow) # distance to pawn from your back row
					if pawn == team: # your pawn
						weights[tempCol] = weights[tempCol] + adjacentRowAlliedPawnWeight + adjacentRowAlliedPawnDistanceMultiplier * distance
					else: # enemy pawn
						weights[tempCol] = weights[tempCol] + adjacentRowEnemyPawnWeight + adjacentRowEnemyPawnDistanceMultiplier * distance
		
		if board[backRow+forward][tempCol] == opp_team: # if opponent pawn is one tile away from back row
			weights[tempCol] = weights[tempCol] + enemyOneTileAwayWeight 
		
		if board[backRow+forward*2][tempCol] == opp_team: # if opponent pawn is two tiles away from back row
			weights[tempCol] = weights[tempCol] + enemyTwoTilesAwayWeight 

		if tempCol > 0 and board[backRow+forward][tempCol-1] == opp_team: # if opponent pawn is one tile away from back row and one to the left:
			weights[tempCol] = weights[tempCol] + enemyOneAdjacentTileAwayWeight

		if tempCol < board_size-1 and board[backRow+forward][tempCol+1] == opp_team: # if opponent pawn is one tile away from back row and one to the right:
			weights[tempCol] = weights[tempCol] + enemyOneAdjacentTileAwayWeight

	return weights

def maxIndex(list):
	maxNum = list[0]
	maxIndex = 0
	for i in range(len(list)):
		if list[i] > maxNum:
			maxIndex = i
			maxNum = list[i]
	return maxIndex

def overlord_turn():
	board = get_board()
	weights = spawn_weights_pro_plus_max_xyz(board)
	
	debug = ''
	for i in range(board_size):
		debug = debug + str(weights[i]) + ' '
	dlog(debug)

	for i in range(board_size):
		maxWeightCol = maxIndex(weights)
		if not check_space(backRow, maxWeightCol):
			spawn(backRow, maxWeightCol)
			break
		else:
			weights[maxWeightCol] = -100000

	# for tempCol in range(board_size):
	# 	for tempRow in range(board_size):
	# 		temp = board[tempCol][tempRow]
	# 		if temp == opp_team:
	# 			allied_list.append(0)
	# 			enemy_list.append(1)
	# 		elif temp == team:
	# 			allied_list.append(1)
	# 			enemy_list.append(0)
	# 		else:
	# 			allied_list.append(0)
	# 			enemy_list.append(0)



	# for _ in range(board_size):
	# 	i = random.randint(0, board_size - 1)
	# 	if not check_space(backRow, i):
	# 		spawn(backRow, i)
	# 		break

# python -i run.py ml_test weights --raw-text
