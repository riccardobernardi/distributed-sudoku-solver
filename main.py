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
from util import solve, squeze_all, RANK, split, to_int, Sudodata, parse_sudoku
from time import sleep
from antiplagiarism import antiplagiarism

# download_sudokus()
# load_qqwing_sudokus()

# plagiarism = antiplagiarism("./sudokus",type=".txt", grams=2,threshold=0.9)
# print("number of sudokus that are very similar:",len(plagiarism))

DISTRIBUTE = True


def main():
	count = 0
	solved = 0
	dataset = list(os.listdir("./sudokus")).filter(lambda x: ".txt" in x)
	alls = len(dataset)

	c = Redis(host='192.168.1.237')
	q = Queue(connection=c)
	jobs = []

	for i in dataset:
		# i is a txt file representing a sudoku in the correct format
		with open("./sudokus/" + i, mode="r") as f:
			curr_sudoku = parse_sudoku(f)

			if DISTRIBUTE:
				jobs.append(q.enqueue(solve, curr_sudoku))
			else:
				result = solve(curr_sudoku)

				if result != -1:
					result = Sudodata(result)
					print("--------------------------")
					print(result)
					solved += 1
			count += 1

			print("\r done", count, "out of", alls, end='')

	print()
	distributed_finished = 0
	excluded = set()
	if DISTRIBUTE:
		while any(not job.is_finished for job in jobs):
			for i in jobs:
				if i.is_finished and (i.get_id() not in excluded):
					excluded.add(i.get_id())
					distributed_finished += 1
				print("\r distributed_and_finished: ", distributed_finished, "out of", alls, end='')
			sleep(0.01)

		for jj in jobs:
			result = jj.return_value
			if (result != -1) and (result is not None) and (result != "None"):
				#return result
				solved+=1
		print()
	print("Tot of correct over all:", solved, "/", alls)
	print("Accuracy is: %.2f" % ((solved / alls) * 100), "%")


init = time.time()
main()
print("Elapsed:", (time.time() - init) / 60, "min")
