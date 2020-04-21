import os





dirLen = 4


for i in range(20):
	newDir = ""
	while len(newDir)+len(str(i)) < dirLen:
		newDir=newDir+"0"
	newDir=newDir+str(i)
	print(newDir)
	os.mkdir("test_folder/"+newDir)