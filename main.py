import os
from pygraham import *
from util import solve_cs, solve_bt, show

for i in os.listdir("./sudokus"):
	# i is a txt file representing a sudoku in the correct format
	with open("./sudokus/" + i,mode="r") as f:
		curr_sudoku = list([])
		for j in f:
			curr_sudoku += [ k for k in [j.replace("\n","").split(" ")] ]

		# show(curr_sudoku)
		solve_cs(curr_sudoku)
		#solve_bt(curr_sudoku)
