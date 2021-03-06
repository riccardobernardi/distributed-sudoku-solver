import os
import pickle

import pandas as pd

pickle.HIGHEST_PROTOCOL = 2

import rq
from pygraham import *
from redis import Redis
import pickle

pickle.HIGHEST_PROTOCOL = 2
from rq import Queue
import time
from scraper import download_sudokus, load_qqwing_sudokus
from util import solve, Sudodata, parse_sudoku, print_distributed_results, cc, parse_sudoku_sol
from antiplagiarism import antiplagiarism

DISTRIBUTE = False
VIEW_RESULTS = False
DOWNLOAD_DATA = False
LOAD_KAGGLE = True
WEBSCRAPED = False


def main():
	if DOWNLOAD_DATA:
		try:
			download_sudokus()
			load_qqwing_sudokus()
		except:
			print("Some downloads went wrong...")

		plagiarism = antiplagiarism("./sudokus", type=".txt", grams=2, threshold=0.9)
		print("number of sudokus that are very similar:", len(plagiarism), "(over 90% of similarity)")

	if LOAD_KAGGLE:
		cc.reset()
		init = time.time()
		count = 0
		solved = 0
		nrows = 0 + 100000
		skip = 0
		c = Redis(host='192.168.1.237')
		q = Queue(connection=c)
		jobs = []
		dataset = list(os.listdir("./sudoku_csvs/")).filter(lambda x: "sudoku.csv" in x)#.filter(lambda x: "reduced_sudokus_kaggle.csv" in x)

		for i in dataset:
			print("loading sudokus from kaggle's csv:", i)
			ds = pd.read_csv("./sudoku_csvs/"+i,nrows=nrows)
			nrows = nrows - skip
			for en, j in enumerate(ds.iterrows()):
				if en < skip:
					continue
				curr_sudoku = parse_sudoku(j[1]["quizzes"])
				sol_sudoku = parse_sudoku_sol(j[1]["solutions"])

				if DISTRIBUTE:
					jobs.append(q.enqueue(solve, Sudodata(curr_sudoku,sol_sudoku)))
					count += 1
					print("\r [DISTRIBUTED] Distributed sudokus: ", count, "out of", nrows, end='')
				else:
					result = solve(Sudodata(curr_sudoku,sol_sudoku))

					if result != -1:
						if VIEW_RESULTS:
							print("--------------------------")
							print(result)
						solved += 1
					count += 1
					print("\r [SEQUENTIAL] Solved sudokus:", count, "out of", nrows, "[Elapsed:",(time.time() - init) / 60, "mins]", "[Projection:",nrows / count * ((time.time() - init) / 60), "mins]", "[Avg:",(time.time() - init) / count, "secs]", end='')

		if DISTRIBUTE:
			solved = print_distributed_results(jobs,nrows,init)

		print()
		print("Tot of correct over all:", solved, "/", nrows)
		print("Accuracy is: %.2f" % ((solved / nrows) * 100), "%")
		print("Elapsed:", (time.time() - init) / 60, "min")
		print("recursion count", cc.get_num_recursive_calls(), ", mean of recursions per sudoku:", cc.get_num_recursive_calls()/nrows,"recs/sudoku")
		print("constraint prop count", cc.get_num_constraints_prop_calls(), ", mean of constr. prop. per sudoku:", cc.get_num_constraints_prop_calls()/nrows,"const.props/sudoku")
		print("Coefficient of mean difficulty is:", cc.get_num_occupied_cells()/nrows,"(higher means easier sudokus)")
		print("----------------------------------------------------------")

	if WEBSCRAPED:
		cc.reset()
		init = time.time()
		count = 0
		solved = 0
		dataset = list(os.listdir("./sudokus")).filter(lambda x: ".txt" in x)[:10] # or ("norvig" in x))
		num_sudoku_avail = len(dataset)
		c = Redis(host='192.168.1.237')
		q = Queue(connection=c)
		jobs = []
		for i in dataset:
			# i is a txt file representing a sudoku in the correct format
			#try:
				with open("./sudokus/" + i, mode="r") as f:
					curr_sudoku = parse_sudoku(f)

					if DISTRIBUTE:
						jobs.append(q.enqueue(solve, Sudodata(curr_sudoku)))
						count += 1
						print("\r [DISTRIBUTED] Distributed sudokus: ", count, "out of", num_sudoku_avail, end='')
					else:
						result = solve(Sudodata(curr_sudoku))

						if result != -1:
							if VIEW_RESULTS:
								print("--------------------------")
								print(result)
							solved += 1
						count += 1
						print("\r [SEQUENTIAL] Solved sudokus:", count, "out of", num_sudoku_avail, "[Elapsed:", (time.time() - init) / 60, "mins]", "[Projection:", num_sudoku_avail/count*((time.time() - init) / 60), "mins]", "[Avg:", (time.time() - init)/count, "secs]", end='')
			# except:
			# 	print("A sudoku was wrongly formatted, in particular:", i)

		if DISTRIBUTE:
			solved = print_distributed_results(jobs,num_sudoku_avail,init)

		print()
		print("Tot of correct over all:", solved, "/", num_sudoku_avail)
		print("Accuracy is: %.2f" % ((solved / num_sudoku_avail) * 100), "%")
		print("Elapsed:", (time.time() - init) / 60, "min")
		print("recursion count", cc.get_num_recursive_calls(), ", mean of recursions per sudoku:",
			  cc.get_num_recursive_calls()/num_sudoku_avail,"recs/sudoku")
		print("constraint prop count", cc.get_num_constraints_prop_calls(), ", mean of constr. prop. per sudoku:",
			  cc.get_num_constraints_prop_calls()/num_sudoku_avail,"const.props/sudoku")
		print("Coefficient of mean difficulty is:", cc.get_num_occupied_cells()/num_sudoku_avail,"(higher means easier sudokus)")
		print("----------------------------------------------------------")

main()
