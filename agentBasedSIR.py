from Farm import Farm
from SaleBarn import SaleBarn
from Stocker import Stocker
from Feedlot import Feedlot
import random
import subprocess
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
from limits import universe

# ================= Inital Constant ===================

cInitProb = 0.05
gridHeight = 126
gridWidth = 101
numberFarm = 6
dt = 0.25
currentTime = 0
infPeriod = 100
infProb = 0.2

numS = [0]
numI = [0]
numR = [0]
cumI = [0]
numC = [0]

# ================= Inital Constant ===================
ucl = []
gridList = [[[] for x in range(gridHeight)] for x in range(gridWidth)]
grid = np.random.choice([255], gridHeight*gridWidth, p=[1]).reshape(gridWidth, gridHeight)
grid[0, 0] = 0
#print grid
farmList = []

fin = open("output", "w")
print "Running Code"

for i in range(numberFarm):
	farmList.append(Farm(16 * i + i, 0, 16 * (i + 1) + i - 1, 94, cInitProb))
	farmList[i].initializeCattle(ucl, gridList)

ucl[1].state = ucl[1].state + 1
numS[0] = len(ucl) - 1
numI[0] = 1
numC[0] = len(ucl)
cumI[0] = 1

stocker = Stocker(0, 96, 49, 125)
saleBarn = SaleBarn(50, 96, 52, 125)
feedlot = Feedlot(53, 96, 72, 125)


def analyseGrid():
	for i in range(len(ucl)):
		if ucl[i].state == 0 and ucl[i].location != 8:
			for j in range(-1, 2):
				for k in range(-1, 2):
					if ucl[i].x + j >= ucl[i].x_min and ucl[i].x + j <= ucl[i].x_max and ucl[i].y + k >= ucl[i].y_min and ucl[i].y + k <= ucl[i].y_max:
						# print("["+str(ucl[i].x+j)+", "+str(ucl[i].y+k)+"]")
						# if len(gridList[ucl[i].x + j][ucl[i].y + k]) is not 0:
						for l in gridList[ucl[i].x + j][ucl[i].y + k]:
							# print ucl[l].state, ucl[i].location
							if ucl[l].state == 1:
								if random.random() <= infProb:
									ucl[i].state = ucl[i].state + 1
									numS[len(numS) - 1] = numS[len(numS) - 1] - 1
									numI[len(numI) - 1] = numI[len(numI) - 1] + 1
									cumI[len(cumI) - 1] = cumI[len(cumI) - 1] + 1
									break
					if ucl[i].state == 1:
						break
				if ucl[i].state == 1:
						break

def update(data):
	# while True:
	global grid, currentTime
	newGrid = grid.copy()
	currentTime = currentTime + dt

	numS.append(numS[len(numS) - 1])
	numI.append(numI[len(numI) - 1])
	numR.append(numR[len(numR) - 1])
	cumI.append(cumI[len(cumI) - 1])
	numC.append(len(ucl))

	analyseGrid()

	for i in range(len(ucl)):
		ucl[i].move(gridList)
		ucl[i].increase_weight(gridList)

		if (ucl[i].state == 1 and ucl[i].location != 1 and ucl[i].location !=2):
			ucl[i].daysSick = ucl[i].daysSick + dt
			if ucl[i].daysSick >= infPeriod:
				ucl[i].state = ucl[i].state + 1
				numI[len(numI) - 1] = numI[len(numI) - 1] - 1
				numR[len(numR) - 1] = numR[len(numR) - 1] + 1

		if ucl[i].location == 3:
			ucl[i].time1InSale = ucl[i].time1InSale - dt
			if ucl[i].time1InSale <= 0:
				gridList[ucl[i].x][ucl[i].y].remove(ucl[i].cattleId)
				ucl[i].location = ucl[i].location + 1
				ucl[i].x_min = 0
				ucl[i].x_max = 49
				ucl[i].y_min = 96
				ucl[i].y_max = 125
				ucl[i].x = int(random.random() * 49 + 1)
				ucl[i].y = int(96 + random.random() * 30)
				gridList[ucl[i].x][ucl[i].y].append(ucl[i].cattleId)

		if ucl[i].location == 6:
			ucl[i].time2InSale = ucl[i].time2InSale - dt
			if ucl[i].time2InSale <= 0:
				gridList[ucl[i].x][ucl[i].y].remove(ucl[i].cattleId)
				ucl[i].location = ucl[i].location + 1
				ucl[i].x_min = 53
				ucl[i].x_max = 72
				ucl[i].y_min = 96
				ucl[i].y_max = 125
				ucl[i].x = ucl[i].x_min
				gridList[ucl[i].x][ucl[i].y].append(ucl[i].cattleId)

		if ucl[i].location == 8:
			numC[len(numC) - 1] = numC[len(numC) - 1] - 1

	fin.write(str(currentTime) + " " + str(numS[len(numS) - 1]) + " " + str(numI[len(numI) - 1]) + " " + str(numR[len(numR) - 1]) + " " + str(cumI[len(numI) - 1]) + " " + str(numC[len(numC) - 1]) + "\n")

	# Map gridList to grid
	for i in range(gridWidth):
		for j in range(gridHeight):
			cell = gridList[i][j]
			if len(cell) is 0:  #Empty Cell
				newGrid[i, j] = 127
			elif len(cell) is 1 and ucl[cell[0]].state is 0:    #Susceptible
				newGrid[i, j] = 65
			elif len(cell) is 1 and ucl[cell[0]].state is 1:    #Infected
				newGrid[i, j] = 217
			elif len(cell) is 1 and ucl[cell[0]].state is 2:    #Recovered
                            newGrid[i, j] = 167
			elif len(cell) is not 1:
				newGrid[i, j] = 10  #Stacking cattle and No Infected
				for k in cell:
					if ucl[k].state is 1:   #Stacking cattle and at least one Infected
						newGrid[i, j] = 197
						break
	
	#for i in range(126):
	#	newGrid[0, i] = i
	#for i in range(127, 253):
	#	newGrid[1, i-127] = i
        for i in range(1,6):
            for j in range(0,95):
                newGrid[16*i +i-1,j] = 255;

	mat.set_data(newGrid)
	grid = newGrid
	return [mat]
	# if numC[len(numC) - 1] <= 0:
	# 	break

fig, ax = plt.subplots()
mat = ax.matshow(grid)
ax.text((universe['farm0']['minY']+universe['farm0']['maxY'])/2,(universe['farm0']['minX']+universe['farm0']['maxX'])/2,'Farm1')
ax.text((universe['farm1']['minY']+universe['farm1']['maxY'])/2,(universe['farm1']['minX']+universe['farm1']['maxX'])/2,'Farm2')
ax.text((universe['farm2']['minY']+universe['farm2']['maxY'])/2,(universe['farm2']['minX']+universe['farm2']['maxX'])/2,'Farm3')
ax.text((universe['farm3']['minY']+universe['farm3']['maxY'])/2,(universe['farm3']['minX']+universe['farm3']['maxX'])/2,'Farm4')
ax.text((universe['farm4']['minY']+universe['farm4']['maxY'])/2,(universe['farm4']['minX']+universe['farm4']['maxX'])/2,'Farm5')
ax.text((universe['farm5']['minY']+universe['farm5']['maxY'])/2,(universe['farm5']['minX']+universe['farm5']['maxX'])/2,'Farm6')
ax.text((universe['feedlot']['minY']+universe['feedlot']['maxY'])/2,(universe['feedlot']['minX']+universe['feedlot']['maxX'])/2,'feedlot')
ax.text((universe['salebarn']['minY']+universe['salebarn']['maxY'])/2,(universe['salebarn']['minX']+universe['salebarn']['maxX'])/2,'salebarn')
ax.text((universe['stocker']['minY']+universe['stocker']['maxY'])/2,(universe['stocker']['minX']+universe['stocker']['maxX'])/2,'stocker')
ax.text((universe['abbatoir']['minY']+universe['abbatoir']['maxY'])/2,(universe['abbatoir']['minX']+universe['abbatoir']['maxX'])/2,'abbatoir')
plt.legend((['Empty:green' ,'Susceptible:blue','Infected:red','Recovered:yellow','No Ill Stacked:dark blue','>1 Ill Stacked: dark red']),loc='lower right')

# ani = animation.FuncAnimation(fig, scheduler, interval=50, frames=20)
ani = animation.FuncAnimation(fig, update, interval=50, save_count=50)
plt.show()
plt.close(fig)

fin.close()

# plot = subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE)
# plot.stdin.write("""
# 	plot "output" using ($1):($2) title "Susceptible" with linespoints lc "blue" lw 2 pt 7 ps 4 smooth cspline, "output" using ($1):($3) title "Infected" with linespoints lc "red" lw 2 pt 7 ps 4 smooth cspline, "output" using ($1):($4) title "Recovered" with linespoints lc "black" lw 2 pt 7 ps 4 smooth cspline, "output" using ($1):($5) title "Cummulative Infected" with linespoints lc "cyan" lw 2 pt 7 ps 4 smooth cspline, "output" using ($1):($6) title "Cattle Remaining" with linespoints lc "gold" lw 2 pt 7 ps 4 smooth cspline	
# 	pause 50
# 	""")
