import os
import pickle

pickle.HIGHEST_PROTOCOL = 2

import rq
from pygraham import *
from redis import Redis
import pickle

pickle.HIGHEST_PROTOCOL = 2
from rq import Queue
import time
from scraper import download_sudokus, load_qqwing_sudokus
from util import solve, Sudodata, parse_sudoku, print_distributed_results
from antiplagiarism import antiplagiarism

DISTRIBUTE = False
VIEW_RESULTS = False
DOWNLOAD_DATA = False


if DOWNLOAD_DATA:
	try:
		download_sudokus()
		load_qqwing_sudokus()
	except:
		print("Some downloads went wrong...")

	plagiarism = antiplagiarism("./sudokus", type=".txt", grams=2, threshold=0.9)
	print("number of sudokus that are very similar:", len(plagiarism), "(over 90% of similarity)")


def main():
	count = 0
	solved = 0
	dataset = list(os.listdir("./sudokus")).filter(lambda x: ".txt" in x).filter(lambda x: "sudoku1.txt" in x)
	num_sudoku_avail = len(dataset)
	c = Redis(host='192.168.1.237')
	q = Queue(connection=c)
	jobs = []

	for i in dataset:
		# i is a txt file representing a sudoku in the correct format
		try:
			with open("./sudokus/" + i, mode="r") as f:
				curr_sudoku = parse_sudoku(f)

				if DISTRIBUTE:
					jobs.append(q.enqueue(solve, Sudodata(curr_sudoku)))
					count += 1
					print("\r [DISTRIBUTED] Distributed sudokus: ", count, "out of", num_sudoku_avail, end='')
				else:
					#print(Sudodata(curr_sudoku))
					result = solve(Sudodata(curr_sudoku))

					if result != -1:
						if VIEW_RESULTS:
							print("--------------------------")
							print(result)
						solved += 1
					count += 1
					print("\r [SEQUENTIAL] Solved sudokus:", count, "out of", num_sudoku_avail, end='')
		except:
			print("A sudoku was wrongly formatted, in particular:", i)

	if DISTRIBUTE:
		solved = print_distributed_results(jobs,num_sudoku_avail)

	print()
	print("Tot of correct over all:", solved, "/", num_sudoku_avail)
	print("Accuracy is: %.2f" % ((solved / num_sudoku_avail) * 100), "%")


init = time.time()
main()
print("Elapsed:", (time.time() - init) / 60, "min")
