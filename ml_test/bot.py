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
pawn_bias_L1 =[-1.524522, 0.384594, 7.163271, -2.839412, -5.36444, -10.84269, -4.238211, -6.759446, -2.048246, -0.400748, 5.572956, 7.57119, 1.278863, -7.872531, 7.881619, 1.321183, -6.231871, -6.184106, 5.72193, 8.339716]
pawn_bias_L2 =[4.064319, 0.676518]
pawn_weights_L2 =[[3.677512, 0.720033], [-4.501768, -12.373649], [3.883611, -4.088675], [-7.09684, -6.903813], [2.274902, 14.976283], [7.487644, 6.652523], [0.761926, 9.086711], [-2.195426, -10.055632], [-1.53718, 1.905601], [1.449447, 7.723966], [-0.226429, 4.822939], [4.123273, -9.596199], [7.326063, 1.167754], [9.297785, 7.134038], [-4.052903, -1.250147], [4.402868, 3.055461], [-1.418938, 0.207038], [2.310362, 4.811312], [7.931236, 1.005522], [-9.064411, -4.062889]]

overlord_weights_same_allied = [
[-64,-63,-62,-61,-60,-59,-58,-57,-56,-55,-54,-53,-52,-51,-50,-49], #on border
[-64,-63,-62,-61,-60,-59,-58,-57,-56,-55,-54,-53,-52,-51,-50,-49], #one away from boarder
[-64,-63,-62,-61,-60,-59,-58,-57,-56,-55,-54,-53,-52,-51,-50,-49]] #all other possibilities

overlord_weights_adjacent_allied = [
[1000,700,14,13,12,11,10,9,8,7,6,5,4,3,2,1],
[1000,700,14,13,12,11,10,9,8,7,6,5,4,3,2,1],
[1000,700,14,13,12,11,10,9,8,7,6,5,4,3,2,1]]

overlord_weights_same_enemy = [
[5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5],
[5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5],
[5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5]]

overlord_weights_adjacent_enemy = [
[-500,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1],
[-500,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1],
[-500,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1]]


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
		pawn_weights_L1 = [4.591072, -24.091994, 9.038736, -2.245361, -1.090315, 4.471996, 2.955139, -0.421036, 8.480126, -4.858814, -0.917427, 2.847146, 0.961868, -1.942356, 3.839918, 3.02193, 5.591118, -10.473391, 5.365887, 6.614918, -9.245872, -6.305738, -6.693945, -9.00938, 10.118266, -11.128872, -8.596241, 3.634164, -4.565431, -10.597101, -0.214328, 6.840273, -7.156041, -11.589858, -2.874525, 1.207616, -0.605701, -0.898854,
		-5.178, 0.211035, -3.051706, 6.543506, -1.691559, -3.537125, 3.348264, -4.522857, 2.646244, -0.091581, 1.469325, 5.134217, -5.629812, 24.808838, 5.460018, -5.503715, 0.413884, -10.270935, 0.347776, -0.051658, 1.401893, 3.105884, 0.259124, 3.524336, -2.624967, -10.679805, 0.283422, 3.124168, -0.988648, 4.382883, -6.683553, 4.830552, -2.279654, 3.125579, -12.493113, -1.109344, 2.731731, -5.176135]
	elif i == 1:
		pawn_weights_L1 = [-5.653778, 3.976277, 0.926144, -1.191044, -3.266031, -1.598801, 6.28995, -0.134264, -4.188902, -0.411542, -3.856063, 3.369744, 6.568669, 4.668799, -5.765474, 7.812571, 0.257745, -20.879688, 0.602545, 4.123653, 4.68844, -3.932965, -7.603133, 1.908821, -6.585991, -3.77364, -9.952246, 5.044712, -10.674271, 10.522784, -2.099519, 3.211436, -6.19543, 3.651385, 4.605289, -4.876959, 4.582389, -3.287668,
		2.810081, 2.354526, -4.919789, 2.241258, -5.796023, -5.932862, -13.750938, -5.144767, -0.959595, 5.191526, 2.635383, -7.129571, 3.305681, -0.35094, -7.914406, -7.49994, 0.821363, -3.961266, 1.263532, -11.932005, -5.395881, -0.32636, 4.837319, -0.000679, 4.751952, -0.19261, 13.18395, 2.602712, -3.419934, 1.781382, -0.156478, 6.176914, 3.440002, -2.851285, -2.976316, 1.76659, 4.592979, 4.513707]
	elif i == 2:
		pawn_weights_L1 = [2.045376, -0.568341, -7.976338, -7.731391, -6.376883, 9.210106, 7.240958, -7.075559, -5.304721, 8.201594, -0.793519, -2.719258, -5.993352, 10.121553, -1.565298, 0.118263, -2.14244, -1.712812, -0.585007, 1.015925, 1.828507, -1.595719, 0.087167, -6.311983, -1.489642, 2.323838, -0.447195, -6.668228, 6.51619, -1.615996, 0.206508, -7.616426, 4.331262, -7.465131, -3.456834, -0.143904, 1.043885, 6.887109,
		-6.923894, -2.888765, -0.65105, -0.452426, 6.396307, -2.901318, -6.010715, -1.838883, -4.491684, -0.862218, 3.562376, 10.1958, 3.653874, -11.825922, 7.162923, 7.822699, 2.148032, -4.955108, -1.084981, -2.156206, -9.734336, -1.510833, 8.295422, -6.890747, -4.580002, -3.40402, -0.985656, 6.308653, -5.877226, -7.344827, 3.380965, 2.468506, 0.499696, -4.897977, 4.252808, 1.054336, 9.768917, 16.529459]
	elif i == 3:
		pawn_weights_L1 = [6.837921, 1.32715, 2.795789, 0.154435, 5.769249, -1.524524, -1.710862, -1.151028, 5.553951, 2.885582, 0.493384, -0.852286, -0.968072, 0.036555, 3.904972, 7.193578, -1.458701, -9.965012, -9.655983, 1.221304, -1.983863, 6.670486, -9.974565, 0.168905, -1.98678, 2.94175, 3.419662, 2.205064, -4.982892, 1.941727, 6.326195, -1.600066, 2.417706, -0.660653, 6.4796, -3.372731, 11.80692, 2.49341,
		-8.315199, -1.009003, 1.419417, 3.699277, -3.857749, 1.209287, -2.614019, 6.330159, -7.373918, 3.641574, 7.832038, 0.177631, -9.100297, -9.755094, -5.73829, 5.834499, -7.300499, -2.038491, -4.744403, -8.661196, 1.941232, -1.208081, 5.733355, -2.114723, 1.185092, -5.206807, 0.061561, -4.172707, -0.724166, 5.736735, -6.288182, -8.281048, 0.930437, 0.855033, -0.020389, -0.768039, -4.126023, 7.088603]
	elif i == 4:
		pawn_weights_L1 = [6.284393, -1.015048, -1.240087, 0.011678, -0.741765, 5.612206, -6.962603, 7.780052, -10.796101, 10.568176, 5.146236, 1.497669, -3.563458, -0.841662, 8.630196, 0.08303, 0.595173, 0.821852, -11.478166, 12.204732, -1.572607, -4.624713, -6.954499, 7.624611, 6.54467, -5.107863, 0.500769, -8.173891, 0.032502, 6.614996, -3.891701, 0.552977, -1.012806, 0.904063, -0.655072, -9.381558, -5.464017, -0.774892,
		12.84719, -9.440891, -2.61175, 2.469761, 7.677564, -3.153982, -8.150169, 1.142792, 1.180295, -2.511922, 8.094579, 0.309378, 11.430271, 7.488227, 3.568294, -4.885954, 12.65839, -13.395406, 5.300434, 1.641862, 4.920339, -5.021334, 4.958482, -0.275069, -3.881643, -1.731911, 7.928928, 5.340782, -3.943841, 0.36332, -0.052997, 9.898001, 12.662748, -1.023507, 2.347042, 4.561661, -5.66709, 10.017507]
	elif i == 5:
		pawn_weights_L1 = [-0.837176, 1.200089, -7.143244, -3.842106, -4.0079, 3.460088, 7.943753, 0.81961, -2.393089, -4.55652, 5.548169, 3.048038, 1.465612, -1.339987, 0.351598, 1.163717, 1.206647, 5.408734, 2.155021, 6.006244, 9.864299, -10.036084, -1.882605, -9.597727, 4.369086, 5.649758, -4.617197, -3.392734, -14.141546, -9.881836, 1.931441, -1.068017, -0.630721, 5.25154, -2.536992, 5.074166, 4.114488, -1.240238,
		-1.810976, 1.480554, -0.011423, 8.287229, -4.168166, 7.217353, 0.454531, 4.548995, -5.53952, 0.848, 1.470933, 2.995832, -4.187327, 4.440249, 0.078441, -0.66004, 3.33824, -8.73892, -7.701998, 2.677859, -5.699655, -0.466165, 5.580564, 5.010099, -3.518636, -0.578157, 3.888294, 8.432708, -2.387748, 1.559704, -4.372495, 0.264145, 2.703554, 4.341142, 2.225159, 5.14944, 8.449723, 10.770002]
	elif i == 6:
		pawn_weights_L1 = [7.204887, -8.085296, -1.164366, 7.033074, -11.592113, 3.790979, -7.781634, -0.606489, -4.95959, -0.534992, -1.01793, -6.503383, -3.114744, 6.989408, -0.728266, 0.151512, 3.08757, -4.662572, -1.732672, 7.384563, -7.463851, 3.384356, 1.373426, -6.348997, 3.198385, 1.710048, -10.550737, -7.109912, 5.791897, 4.505033, -0.229314, -6.527815, -13.466001, -0.855397, 9.256812, -2.086637, 1.49428, -8.191386,
		1.137077, -6.834668, 5.440013, -6.298781, 12.536205, -2.293907, -0.369791, 4.60301, 7.676935, 3.682682, -9.420701, 3.214309, 2.28563, -3.498116, -6.710361, -1.579859, -6.089988, -3.952823, 0.219111, -4.283354, 11.527278, 3.554735, -0.950795, 3.78034, -7.307755, -3.581597, 7.627439, 1.399643, 0.812446, 3.21194, 6.796205, -2.608787, 8.832314, -2.804009, 1.728739, -5.210439, -4.573681, 1.540721]
	elif i == 7:
		pawn_weights_L1 = [5.36935, 12.778289, 7.121812, 9.047487, -3.004384, -4.180106, -0.085993, 6.166703, -5.160527, 4.68826, 1.608718, 6.405414, 6.507537, -9.319541, 8.329947, 3.174197, -5.204438, 8.537223, 12.398911, 0.585179, 1.261222, 7.549145, -0.24116, 5.466399, -0.09228, -2.422496, -8.616102, 1.678049, 7.240173, -2.148631, 2.933957, -2.532128, -4.039695, -6.572084, 1.258495, -8.197799, -7.391624, -8.684155,
		9.140291, 7.098913, -6.214592, -1.869314, 1.789305, 3.095274, 1.47146, 8.685464, -5.485631, 3.613382, 3.900671, -8.734915, 3.578869, -4.659497, -2.03263, 1.48525, 0.959427, 6.928065, -2.926138, -8.166729, -2.394912, -7.856456, -1.950436, 1.559957, 6.189351, -3.472431, -3.827227, -20.08846, -5.486119, 6.300304, 3.587517, -1.48332, 2.451102, 9.629676, 0.882201, 2.967866, 6.489396, -8.866526]
	elif i == 8:
		pawn_weights_L1 = [-6.039805, -13.309762, 5.632929, -3.165648, -5.115635, 6.565305, 7.628289, -5.295619, 0.342614, -9.703509, -2.040922, 9.261898, 3.613368, -2.408925, -4.408419, 0.647703, 4.440467, -1.264019, 8.997535, 6.919278, -4.33798, -5.213344, -6.306013, -5.09321, -7.624522, 6.664608, -1.534565, 4.025749, -2.686092, 0.287914, 4.655386, 6.155088, 7.655001, -8.65641, -9.90149, 6.297037, 6.37123, 8.738441,
		1.276948, 0.77406, 6.245456, -0.187517, -1.124869, 4.927024, -4.916788, 18.537838, -3.28468, -2.13471, -2.189373, 6.528976, -5.469099, -0.558807, -4.458833, 0.424926, -3.113504, 1.741243, -2.637674, 1.15303, 2.058344, -7.587328, 3.601008, 7.813044, 6.014979, -1.018181, 6.99638, -2.006252, 2.025677, -2.99583, -21.59803, -8.193177, -10.405772, 5.023426, -5.693328, -6.362429, 3.752508, -5.600145]
	elif i == 9:
		pawn_weights_L1 = [-3.255469, -5.475349, 12.682268, 10.622055, 2.1976, -0.792483, -2.202611, 3.991865, 5.525629, -4.336189, 6.049169, -0.330008, -0.224026, 0.606768, 5.749129, 7.336227, -0.440938, -0.181202, 4.453835, 7.395949, 10.537599, 2.554825, -1.732347, -5.738244, 2.289604, -3.560054, -7.501151, 1.90671, 3.702919, 7.283305, -2.846365, 0.898242, 4.538106, 8.490017, 6.548929, -1.290999, -3.033831, -8.497597,
		0.262632, -7.731192, 7.207197, 6.059248, -12.080429, -5.006231, -1.950514, -3.527194, 7.148831, -5.344432, 7.29894, -4.888689, 1.521608, -7.249656, -7.472686, -6.788298, -4.940331, -0.809431, -7.142014, -8.946869, -0.396902, -2.737094, -5.789147, -5.745241, -6.042208, 3.062621, 0.372085, 8.233111, 6.261329, 5.582723, 2.298003, -6.410289, -6.418304, 2.96377, 7.58642, 0.852487, -0.608256, 1.249898]
	elif i == 10:
		pawn_weights_L1 = [-7.738263, -9.376382, -5.607916, 1.749652, 9.923015, 3.310012, 0.164262, -4.683883, -3.196723, -4.380368, 4.090035, 3.947502, 1.061786, -6.733228, -2.321233, -2.266062, -8.449725, -2.708463, -0.425146, -6.442632, 4.943524, 1.671507, -5.027709, -9.636053, -4.995663, -6.0938, 0.707295, -5.646519, 2.422096, 5.221186, -9.71056, -3.065272, -5.322053, 7.470494, -5.52104, -2.47495, -3.134683, -0.175397,
		-5.539439, 5.217285, 8.223985, 12.943942, -4.446057, -8.005632, 2.28456, 2.264399, 3.880596, -6.782664, 1.967398, 1.585182, -3.090351, 1.063038, 5.661308, 2.296241, 8.827303, -2.710031, -1.185168, -0.087817, 8.269738, 1.683927, -0.931573, 1.047992, 7.470864, 3.390262, -7.596087, 3.929097, -4.420941, -8.053428, 0.308118, 1.127442, -2.854076, -2.785097, 0.303077, 1.828308, 8.089508, -2.981313]
	elif i == 11:
		pawn_weights_L1 = [7.403102, -2.81877, -0.229069, -0.507204, 6.421072, -4.804269, -7.543355, 10.09743, -4.025077, 2.766235, -4.290868, -7.638283, -6.63173, 0.184011, 6.058888, 1.217998, -4.51582, 4.767841, 0.33616, -11.778663, 4.644852, -7.37173, -6.11842, 14.877299, -0.16805, -10.794834, 0.894284, -3.790862, 6.795754, -1.55013, -3.714568, 6.140469, 0.451687, -3.520067, -1.975536, -5.808689, -7.154286, 8.368085,
		-6.706018, -2.881327, 0.805974, 1.629228, -4.461523, 1.075145, 1.553949, 6.16869, 9.231751, 9.958154, 9.268806, -3.551039, 4.12983, 7.660765, -4.640252, -4.454647, 0.117241, 5.199097, 2.969124, -0.751497, 12.773326, -1.13692, -1.162698, 1.139277, -1.542857, -8.153649, 1.588038, 13.835247, 1.256493, 0.145558, 4.801979, 9.237322, 11.390696, -3.151798, -5.604925, -0.79382, 1.189558, 11.257524]
	elif i == 12:
		pawn_weights_L1 = [-2.957422, -1.152767, 10.330167, -6.849515, -8.809042, 8.669852, 10.482641, 2.673865, 5.958035, -0.169442, -5.834838, 2.582795, -7.369312, 5.921056, 7.029576, 4.72404, -4.08657, 5.045996, 9.903204, -1.746133, 4.920803, -10.718514, 2.910795, -7.692736, 4.562048, -0.176322, 5.761158, 8.895703, 1.084648, 0.625986, 1.635646, -0.231276, -1.253699, -4.22202, 6.23315, 15.291117, -3.917282, 7.919097,
		-3.959676, -5.209508, 5.235447, -21.92008, 30.587383, -4.583802, -6.045054, 7.002306, 8.6492, -3.170796, 7.119052, 6.534488, -0.79501, 3.755462, -1.709081, 0.930104, -5.008575, 1.038081, -8.626643, 4.845482, 0.446562, -9.918003, -11.00724, 5.675564, 1.038629, 6.307143, 2.930192, 0.186446, -6.781505, 1.48226, 0.213799, 3.907342, 6.627499, 2.546069, -2.747353, 5.167799, -4.670539, -1.826246]
	elif i == 13:
		pawn_weights_L1 = [7.853451, -9.59591, 0.957804, -8.741133, 5.211492, -0.952216, -2.888581, 0.83094, -4.01147, -5.908484, -7.854003, -6.87569, -5.402652, 0.651268, 1.951418, 6.684256, 4.96211, 0.304968, -1.662215, -8.257335, -0.846559, -5.697236, 9.405765, 1.702354, -4.718466, -2.052207, -5.02322, -4.205169, -8.695879, -4.596056, -10.657436, -5.728248, -5.528602, -9.424399, 1.146759, 0.965031, -5.394946, -7.757628,
		-2.586711, 4.360255, 0.365375, -3.949594, 10.976538, -9.492991, 3.521417, 5.518676, -1.68408, -4.08278, -6.556328, -16.856907, -4.199525, -2.953762, -3.03598, 0.857909, -0.019546, -0.078477, -9.799932, 10.193884, 7.040454, 3.746564, -9.768957, -9.386689, 10.498642, -8.90752, 7.807325, -1.062208, 5.389461, -2.330312, -0.257084, 15.43566, 0.806478, 1.758079, -18.121001, 6.513871, -8.857893, 9.426436]
	elif i == 14:
		pawn_weights_L1 = [-2.649639, -3.326884, -2.347901, 0.292543, -9.858919, 9.959648, -13.172459, 0.268815, -5.829743, 5.427778, 7.114502, -3.851137, 1.185076, -6.463447, 3.390873, -7.154865, 4.578945, -2.619479, -7.771136, 0.44817, 1.154643, -6.416932, 5.928823, -9.643612, 3.121926, 6.547075, 4.933031, 3.643709, -1.897827, 0.273817, -7.845152, -2.768759, 7.192971, 8.120229, 6.825158, 3.547854, -5.253818, -0.338332,
		-4.122837, -2.890885, 5.756006, -9.739557, 4.74527, 1.715623, 2.791086, -2.558506, 4.615501, -1.407782, 6.693455, 5.684037, -1.285565, 2.928999, 0.708699, 1.542309, 8.051332, -6.693332, 7.837179, -4.607803, -7.641749, -2.939381, -1.678227, 6.506371, 5.133949, -3.194684, -6.172877, 1.81068, -7.829134, -5.224895, -0.012048, -1.148476, -7.807027, -1.803234, -2.894274, 2.776886, 0.868542, 7.263465]
	elif i == 15:
		pawn_weights_L1 = [9.251219, -6.201716, -5.070308, -6.491983, -8.109017, -15.695005, 5.761056, 9.138502, 6.401788, -4.973162, -1.199053, 1.437447, -6.488427, 1.738379, -4.010387, -0.296699, -4.337531, -2.540925, 0.481377, -7.239203, -2.226246, 0.4586, 4.678929, 1.659455, -0.623129, -5.5165, 4.664681, -2.094781, -6.214326, 15.968613, -6.335882, -0.914829, -5.622885, -5.175293, -2.974304, 7.578421, -4.283974, -6.097158,
		5.684014, 5.064637, -5.71816, 0.368941, -4.119867, 0.031715, -5.159331, 3.365528, 6.783958, -1.30494, 1.681413, -4.489805, -9.075526, -5.250422, -4.598004, 2.815298, 5.11772, -7.927634, 0.119645, -6.478433, 7.591536, -1.034698, 5.948688, 6.166968, -3.348896, 3.49363, -9.112101, 0.715735, 0.938778, 20.624464, 8.089231, 6.323483, 9.846203, 0.217948, 3.491129, -8.255148, 6.605104, 7.75942]
	elif i == 16:
		pawn_weights_L1 = [-0.571593, -5.302272, 0.52307, -7.951396, 7.600542, -3.697308, 3.93604, 3.990101, 8.192329, 3.089835, -8.257991, 10.413866, -3.26949, -8.730609, 2.882893, 4.74483, 3.207364, 4.493327, 14.239485, -8.58515, 1.124752, 0.398609, -3.767923, -10.241501, -3.960219, 2.835162, 0.058023, 2.76458, 14.512625, 7.342278, 5.795983, 3.984423, -9.312776, 3.794003, -7.432632, -7.478168, -2.327404, 7.332094,
		-4.802075, -3.710784, 4.026892, -1.229722, -9.503222, 3.498504, -3.62553, 3.129434, 16.530339, -1.190691, 6.713904, -5.877431, -4.123196, -7.068974, 3.971146, -1.110274, 3.882555, 0.412303, -1.116835, 2.373618, -3.175148, 8.356394, 4.629611, -4.846562, -1.288132, 11.447755, -12.44225, 3.931642, -1.337091, 7.910315, -2.701781, -1.403872, 2.602987, 9.153266, 7.535057, 5.287612, 6.548231, -6.176743]
	elif i == 17:
		pawn_weights_L1 = [1.690586, 0.455851, -4.012303, -11.856282, 3.403591, -3.113432, -7.809214, 4.063174, -0.684127, 0.228704, -4.432317, 4.19053, 0.776332, -5.590624, 0.726135, -5.862867, -5.247426, 5.8867, 3.210759, -3.033486, 3.866519, 3.772372, 9.851635, 8.10425, -2.96727, -5.381895, -0.56134, -4.69949, -4.847182, -6.461335, -7.173525, 8.397018, 7.204574, 4.100407, 5.500397, -2.187383, -5.820109, 1.172054,
		2.366128, -0.024683, 0.359298, -6.870396, -5.988682, -6.223063, -2.021108, 2.387052, -8.984995, -8.087451, 4.618178, 3.002494, 1.838288, 4.461156, 5.167616, 11.575268, -0.460945, -6.732932, 6.772078, -1.695148, -6.369342, -7.062853, 10.798185, 1.290971, -5.473244, 1.479109, -1.00113, -2.973594, 1.568253, 3.632746, 9.323163, -2.932151, 3.849951, -0.444437, 7.149604, -2.000567, 1.192928, -1.622893]
	elif i == 18:
		pawn_weights_L1 = [4.425535, 3.613467, 0.68472, -1.062997, -4.358134, -3.825203, -4.545767, -2.135245, -8.521469, -1.41287, 0.167089, 3.392214, 3.764745, 1.211607, -6.521331, -1.197206, -0.532076, -14.548509, 2.821517, 4.851173, 2.902883, -4.387907, -8.983137, 9.295619, 5.64423, 8.80895, -4.894031, -6.457116, 5.454687, -1.016285, 4.101928, 1.797634, -2.982012, -3.165185, 2.130251, 4.276455, -7.146969, -1.229078,
		-5.388561, -4.101123, -6.999317, 2.252106, 1.596681, -4.134757, 5.01203, -0.97354, -2.481305, 0.812121, 6.529242, 9.739951, -1.55283, -3.579964, 0.89148, -0.792905, 6.393987, -6.96411, -5.506151, -2.291037, 4.142961, 0.066903, 2.054113, 0.800866, -3.154493, 4.350027, -4.273997, 3.185459, 5.28157, -6.823845, 0.329898, 0.46744, 11.670831, -3.705883, 1.453854, 3.47316, -3.523039, 11.712277]
	elif i == 19:
		pawn_weights_L1 = [14.138325, -0.036586, 3.349008, 3.397323, -4.426998, -9.264317, 0.845482, -8.748895, -5.400268, 6.231612, -8.834889, 2.492289, -2.512224, -5.362945, -0.723249, 2.956261, -2.219563, -8.736225, -2.745883, -6.487235, 1.848949, -7.281666, -5.554181, 1.055115, 3.824467, -4.293387, -1.663469, -4.641743, -2.711405, -0.946298, 3.278084, 7.724794, 7.964674, 4.379242, -6.154797, 3.291978, 0.550406, 5.772182,
		-8.50564, 1.033027, 0.66167, 0.807252, -0.884958, 9.374599, -7.658234, 4.036549, 0.61416, -0.574561, -5.58438, 6.732363, -7.140589, 9.201214, -10.37133, -2.949093, 4.47024, 5.528324, 6.957924, 1.60389, 5.647302, -2.929503, -0.415601, -0.491437, 1.979001, -4.903684, -0.608046, 3.055974, -2.318563, 2.672511, -13.874927, 3.366921, -8.322499, -2.015165, -8.828533, -1.073348, -4.874706, -8.169157]
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
