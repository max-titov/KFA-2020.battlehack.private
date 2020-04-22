import numpy as np
import os

weights_dir = "saved_weights/"

input_count = 76
hidden_count = 20
output_count = 2

pawn_bias_L1 = np.zeros([hidden_count])
pawn_weights_L1 = np.zeros([input_count, hidden_count])
pawn_bias_L2 = np.zeros([output_count])
pawn_weights_L2 = np.zeros([hidden_count, output_count])

weight_zones = 3 # on border, one away from border, all other cases
board_size = 16

overlord_weights_same_allied = np.zeros([weight_zones, board_size])
overlord_weights_adjacent_allied = np.zeros([weight_zones, board_size])
overlord_weights_same_enemy = np.zeros([weight_zones, board_size])
overlord_weights_adjacent_enemy = np.zeros([weight_zones, board_size])

data_index = 0

def dir_name_generator(num):
	dirLen = 4
	newDir = ""
	while len(newDir)+len(str(num)) < dirLen:
		newDir=newDir+"0"
	return newDir+str(num)

def save_best_bot(best_bot):
	newDir = dir_name_generator(generation)
	
	os.mkdir(weights_dir+newDir)

	#best bot weights

	f=open(weights_dir+newDir+"/best_bot.txt", "w")

	#pawn weights
	for j in range(len(pawn_bias_L1[0])):
		f.write("%f\n"%pawn_bias_L1[best_bot][j])

	for j in range(len(pawn_weights_L1[0])):
		for k in range(len(pawn_weights_L1[0][0])):
			f.write("%f\n"%pawn_weights_L1[best_bot][j][k])

	for j in range(len(pawn_bias_L2[0])):
		f.write("%f\n"%pawn_bias_L2[best_bot][j])

	for j in range(len(pawn_weights_L2[0])):
		for k in range(len(pawn_weights_L2[0][0])):
			f.write("%f\n"%pawn_weights_L2[best_bot][j][k])

	#overlord weights
	for j in range(len(overlord_weights_same_allied[0])):
		for k in range(len(overlord_weights_same_allied[0][0])):
			f.write("%f\n"%overlord_weights_same_allied[best_bot][j][k])

	for j in range(len(overlord_weights_adjacent_allied[0])):
		for k in range(len(overlord_weights_adjacent_allied[0][0])):
			f.write("%f\n"%overlord_weights_adjacent_allied[best_bot][j][k])

	for j in range(len(overlord_weights_same_enemy[0])):
		for k in range(len(overlord_weights_same_enemy[0][0])):
			f.write("%f\n"%overlord_weights_same_enemy[best_bot][j][k])

	for j in range(len(overlord_weights_adjacent_enemy[0])):
		for k in range(len(overlord_weights_adjacent_enemy[0][0])):
			f.write("%f\n"%overlord_weights_adjacent_enemy[best_bot][j][k])

	f.close()

def read_line(data):
	global data_index
	num = float(data[data_index])
	data_index+=1
	return num

def load_best_bot(generation):
	newDir = dir_name_generator(generation)
	f = open(weights_dir+newDir+"/best_bot.txt", "r") 
	data = f.readlines() 

	for j in range(len(pawn_bias_L1)):
		pawn_bias_L1[j] = read_line(data)

	for j in range(len(pawn_weights_L1)):
		for k in range(len(pawn_weights_L1[0])):
			pawn_weights_L1[j][k] = read_line(data)

	for j in range(len(pawn_bias_L2)):
		pawn_bias_L2[j] = read_line(data)

	for j in range(len(pawn_weights_L2)):
		for k in range(len(pawn_weights_L2[0])):
			pawn_weights_L2[j][k] = read_line(data)

	for j in range(len(overlord_weights_same_allied)):
		for k in range(len(overlord_weights_same_allied[0])):
			overlord_weights_same_allied[j][k] = read_line(data)

	for j in range(len(overlord_weights_adjacent_allied)):
		for k in range(len(overlord_weights_adjacent_allied[0])):
			overlord_weights_adjacent_allied[j][k] = read_line(data)

	for j in range(len(overlord_weights_same_enemy)):
		for k in range(len(overlord_weights_same_enemy[0])):
			overlord_weights_same_enemy[j][k] = read_line(data)

	for j in range(len(overlord_weights_adjacent_enemy)):
		for k in range(len(overlord_weights_adjacent_enemy[0])):
			overlord_weights_adjacent_enemy[j][k] = read_line(data)

	f.close()
	print("pawn_bias_L1 = ")
	print(pawn_bias_L1.tolist())

	for i in range(len(pawn_weights_L1[0])):
		print("if i == "+str(i)+":")
		print("pawn_weights_L1 = "+str(pawn_weights_L1[:,i].tolist()[:len(pawn_weights_L1)//2]))
		print(pawn_weights_L1[:,i].tolist()[len(pawn_weights_L1)//2:])

	print("pawn_bias_L2 = ")
	print(pawn_bias_L2.tolist())

	print("pawn_weights_L2 = ")
	print(pawn_weights_L2.tolist())

	print("overlord_weights_same_allied = ")
	print(overlord_weights_same_allied.tolist())

	print("overlord_weights_adjacent_allied = ")
	print(overlord_weights_adjacent_allied.tolist())

	print("overlord_weights_same_enemy = ")
	print(overlord_weights_same_enemy.tolist())

	print("overlord_weights_adjacent_enemy = ")
	print(overlord_weights_adjacent_enemy.tolist())

np.set_printoptions(threshold=np.inf)
np.set_printoptions(suppress=True)
load_best_bot(400)
