import pickle
from time import sleep, time

pickle.HIGHEST_PROTOCOL = 2

import copy
from pygraham import *

RANK = 3
# STRATEGY = "MOST"
STRATEGY = "LEAST"
# STRATEGY = "DEFAULT"
HASH_COMPARISON = False
PROPAGATION_TRIES = 11
WRONG = "wrong"
CORRECT = "correct"
CONTINUE = "continue"


class StatisticsEval:
	def __init__(self):
		self.count_recursions = 0
		self.count_constraints = 0
		self.count_occupied_cells = 0

	def occupied_cell_present(self):
		self.count_occupied_cells += 1

	def get_num_occupied_cells(self):
		return self.count_occupied_cells

	def constraints_prop_call(self):
		self.count_constraints += 1

	def get_num_constraints_prop_calls(self):
		return self.count_constraints

	def recursive_call(self):
		self.count_recursions += 1

	def get_num_recursive_calls(self):
		return self.count_recursions

	def reset(self):
		self.count_recursions = 0
		self.count_constraints = 0
		self.count_occupied_cells = 0


cc = StatisticsEval()

precomputed_box_indexes = [
	[(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)],
	[(0, 3), (0, 4), (0, 5), (1, 3), (1, 4), (1, 5), (2, 3), (2, 4), (2, 5)],
	[(0, 6), (0, 7), (0, 8), (1, 6), (1, 7), (1, 8), (2, 6), (2, 7), (2, 8)],
	[(3, 0), (3, 1), (3, 2), (4, 0), (4, 1), (4, 2), (5, 0), (5, 1), (5, 2)],
	[(3, 3), (3, 4), (3, 5), (4, 3), (4, 4), (4, 5), (5, 3), (5, 4), (5, 5)],
	[(3, 6), (3, 7), (3, 8), (4, 6), (4, 7), (4, 8), (5, 6), (5, 7), (5, 8)],
	[(6, 0), (6, 1), (6, 2), (7, 0), (7, 1), (7, 2), (8, 0), (8, 1), (8, 2)],
	[(6, 3), (6, 4), (6, 5), (7, 3), (7, 4), (7, 5), (8, 3), (8, 4), (8, 5)],
	[(6, 6), (6, 7), (6, 8), (7, 6), (7, 7), (7, 8), (8, 6), (8, 7), (8, 8)]
]


def aux_precompute_box_indexes():
	for v in range(RANK):
		for i in range(RANK):
			box = []
			for j in range(RANK):
				for k in range(RANK):
					box += [(v * RANK + j, i * RANK + k)]

			yield box


def precompute_box_indexes():
	return [i for i in aux_precompute_box_indexes()]


def print_distributed_results(jobs, num_sudoku_avail, init):
	solved = 0
	print()
	distributed_finished = 0
	excluded = set()
	while any(not job.is_finished for job in jobs):
		for i in jobs:
			if i.is_finished and (i.get_id() not in excluded):
				excluded.add(i.get_id())
				distributed_finished += 1
			if distributed_finished != 0:
				print("\r [DISTRIBUTED] Finished sudokus:", distributed_finished, "out of", num_sudoku_avail,
					  "[Elapsed:", (time() - init) / 60, "mins]", "[Projection:",
					  num_sudoku_avail / distributed_finished * ((time() - init) / 60), "mins]", "[Avg:",
					  (time() - init) / distributed_finished, "secs]", end='')

		sleep(0.01)

	for jj in jobs:
		result = jj.return_value
		if (result != -1) and (result is not None) and (type(result) != str):
			solved += 1

	return solved


def parse_sudoku(f):
	curr_sudoku = list([])

	# linear
	if type(f) == str:
		f = [f[(i - 1) * 9:(9 * i)] for i in range(1, len(f) // 8)]

	for j in f:
		if j == "\n":
			continue
		if j == " \n":
			continue
		if j == " ":
			continue

		j = j.replace(" ", "")

		# no spaces
		if (j[1] != " ") and (j[3] != " "):
			curr_sudoku += [[list(split(k)).map(to_int) for k in [j.replace("\n", "")]][0]]

	curr_sudoku = squeeze_all(curr_sudoku)
	return curr_sudoku


def parse_sudoku_sol(f):
	curr_sudoku = list([])

	# linear
	if type(f) == str:
		f = [f[(i - 1) * 9:(9 * i)] for i in range(1, len(f) // 8)]

	for j in f:
		if j == "\n":
			continue
		if j == " \n":
			continue
		if j == " ":
			continue

		j = j.replace(" ", "")

		# no spaces
		if (j[1] != " ") and (j[3] != " "):
			curr_sudoku += [[list(split(k)).map(to_int_sol) for k in [j.replace("\n", "")]][0]]

	curr_sudoku = squeeze_all(curr_sudoku)
	return curr_sudoku


def split(word):
	return [char for char in word]


def to_int(x):
	if x == '0':
		return [1, 2, 3, 4, 5, 6, 7, 8, 9]
	if x == '.':
		return [1, 2, 3, 4, 5, 6, 7, 8, 9]
	else:
		cc.occupied_cell_present()
		return int(x)


def to_int_sol(x):
	if x == '0':
		return [1, 2, 3, 4, 5, 6, 7, 8, 9]
	if x == '.':
		return [1, 2, 3, 4, 5, 6, 7, 8, 9]
	else:
		return int(x)


def show(matrix):
	for i in matrix:
		for j in i:
			for k in j:
				print(k, end='')

			print(" ", end='')
		print()


def squeeze_all(matrix):
	for i in range(len(matrix)):
		if (type(matrix[i]) != int) and (len(matrix[i]) == 1):
			matrix[i] = matrix[i][0]
		for j in range(len(matrix[i])):
			if (type(matrix[i][j]) != int) and (len(matrix[i][j]) == 1):
				matrix[i][j] = matrix[i][j][0]
			if type(matrix[i][j]) != int:
				for k in range(len(matrix[i][j])):
					if (type(matrix[i][j][k]) != int) and (len(matrix[i][j][k]) == 1):
						matrix[i][j][k] = matrix[i][j][k][0]

	return matrix


class Sudodata():
	def __init__(self, matrix, sol=-1):
		self.data = matrix
		self.sol = sol

	def cell_rc(self, r, c):
		return self.data[r][c]

	def assign_cell_rc(self, r, c, v):
		self.data[r][c] = v

	def cell_rtc(self, r, t, c):
		return self.data[r][t]

	def column(self, c):
		return [self.cell_rc(i, c) for i in range(RANK * RANK)]

	def assign_column(self, c, v):
		for i in range(RANK * RANK):
			self.data[i][c] = v[i]

	def row(self, r):
		return self.data[r]

	def assign_row(self, r, v):
		for i in range(RANK * RANK):
			self.data[r][i] = v[i]

	def cell_iter(self):
		for i in range(RANK * RANK):
			for j in range(RANK * RANK):
				yield self.cell_rc(i, j)

	def row_iter(self):
		for i in range(RANK * RANK):
			yield self.row(i)

	def col_iter(self):
		for i in range(RANK * RANK):
			yield self.column(i)

	def box_iter(self):
		for box in precomputed_box_indexes:
			temp_box = []
			for cell in box:
				temp_box += [self.cell_rc(cell[0], cell[1])]
			yield temp_box

	def cell_transformer(self, l):
		for i in range(RANK * RANK):
			for j in range(RANK * RANK):
				self.assign_cell_rc(i, j, l(self.cell_rc(i, j)))

	def row_transformer(self, l):
		for i in range(RANK * RANK):
			self.assign_row(i, l(self.row(i)))

	def col_transformer(self, l):
		for i in range(RANK * RANK):
			self.assign_column(i, l(self.column(i)))

	def box_transformer(self, l):
		for box in precomputed_box_indexes:
			l(box)

	def __iter__(self):
		for i in range(RANK * RANK):
			for j in range(RANK * RANK):
				yield self.cell_rc(i, j)

	def __eq__(self, other):
		if other == -1:
			return False
		if HASH_COMPARISON:
			if self.hash() == other:
				return True
			return False
		else:
			for i in range(RANK * RANK):
				for j in range(RANK * RANK):
					if self.cell_rc(i, j) != other.cell_rc(i, j):
						return False
			return True

	def is_solved(self):
		for i in range(RANK * RANK):
			for j in range(RANK * RANK):
				if type(self.cell_rc(i, j)) != int:
					if len(self.cell_rc(i, j)) == 0:
						return WRONG

		for i in range(RANK * RANK):
			for j in range(RANK * RANK):
				if type(self.cell_rc(i, j)) != int:
					if len(self.cell_rc(i, j)) > 0:
						return CONTINUE

		for i in self.row_iter():
			if len(set([j for j in range(1, 10)]) & set(i)) != 9:
				return WRONG

		for i in self.col_iter():
			if len(set([j for j in range(1, 10)]) & set(i)) != 9:
				return WRONG

		for i in self.box_iter():
			if len(set([j for j in range(1, 10)]) & set(i)) != 9:
				return WRONG

		if self.sol != -1:
			assert self.sol == self.data
		return CORRECT

	def void_elems(self):
		for i in self.row_iter():
			if list(i).filter(lambda x: (type(x) != int) and (len(x) == 0)):
				return True
		return False

	def duplicates(self):
		for i in self.row_iter():
			for j in range(1, 10):
				if len(list(i).filter(lambda x: (type(x) == int) & (x == j))) > 1:
					return True

		for i in self.col_iter():
			for j in range(1, 10):
				if len(list(i).filter(lambda x: (type(x) == int) & (x == j))) > 1:
					return True

		for i in self.box_iter():
			for j in range(1, 10):
				if len(list(i).filter(lambda x: (type(x) == int) & (x == j))) > 1:
					return True

		return False

	def duplicates_and_voids(self):
		for i in self.row_iter():
			if list(i).filter(lambda x: (type(x) != int) and (len(x) == 0)):
				return True
			for j in range(1, 10):
				if len(list(i).filter(lambda x: (type(x) == int) & (x == j))) > 1:
					return True

		for i in self.col_iter():
			for j in range(1, 10):
				if len(list(i).filter(lambda x: (type(x) == int) & (x == j))) > 1:
					return True

		for i in self.box_iter():
			for j in range(1, 10):
				if len(list(i).filter(lambda x: (type(x) == int) & (x == j))) > 1:
					return True

		return False

	def hash(self):
		hashed = ''
		for i in range(RANK * RANK):
			for j in range(RANK * RANK):
				# hashing is not unique but it's okay
				if type(self.cell_rc(i, j)) == int:
					hashed += str(i) + str(j) + str(self.cell_rc(i, j)) + "-"
				else:
					hashed += str(i) + str(j) + str(sum(self.cell_rc(i, j))) + "-"

		return hashed[:len(hashed) - 1]

	def __repr__(self):
		s = ""
		for i in self.row_iter():
			s += str(i) + "\n"
		return s

	def __str__(self):
		s = ""
		for i in self.row_iter():
			s += str(i) + "\n"
		return s

	def set_matrix(self, matrix):
		self.data = matrix

	def get_possibles(self):
		possibles = []
		# we have to make a choice, use the smallest array of choices to cut out branches of the tree
		for j in range(RANK * RANK):
			for k in range(RANK * RANK):
				if type(self.cell_rc(j, k)) != int:
					possibles += [(j, k, self.cell_rc(j, k))]

		return possibles


def propagate_constraints(data):
	exclude = []

	def box_prop(box_indexes):
		for r, c in box_indexes:
			if type(data.cell_rc(r, c)) == int:
				exclude.append(data.cell_rc(r, c))

		for r, c in box_indexes:
			if type(data.cell_rc(r, c)) != int:
				data.assign_cell_rc(r, c, list(set(data.cell_rc(r, c)) - set(exclude)))

		exclude.clear()

	data.box_transformer(box_prop)

	def col_prop(col):
		exclude = []

		for elem in col:
			if type(elem) == int:
				exclude.append(elem)

		for i in range(len(col)):
			if type(col[i]) != int:
				col[i] = list(set(col[i]) - set(exclude))

		return col

	data.col_transformer(col_prop)

	def row_prop(row):
		exclude = []

		for elem in row:
			if type(elem) == int:
				exclude.append(elem)

		for i in range(len(row)):
			if type(row[i]) != int:
				row[i] = list(set(row[i]) - set(exclude))

		return row

	data.row_transformer(row_prop)

	def squeeze(row):
		for i in range(len(row)):
			if (type(row[i]) != int) and (len(row[i]) == 1):
				row[i] = row[i][0]

		return row

	data.row_transformer(squeeze)

	return data


def get_most_constrained_choice(possibles):
	min_len = 1000  # arbitrary, no more than 9 can be presented
	min_value = (0, 0, [])
	for k, value in enumerate(possibles):
		if len(value[2]) < min_len:
			min_len = len(value[2])
			min_value = value

	return min_value


def get_least_constrained_choice(possibles):
	max_len = -1  # arbitrary, no more than 9 can be presented
	max_value = (0, 0, [])
	for k, value in enumerate(possibles):
		if len(value[2]) > max_len:
			max_len = len(value[2])
			max_value = value

	return max_value


def get_default_ordering_choice(possibles):
	return possibles[0]


def solve(data):
	for i in range(PROPAGATION_TRIES):
		data = propagate_constraints(data)
		cc.constraints_prop_call()

	check = data.is_solved()
	if check == CORRECT:
		return data
	if check == WRONG:
		return -1

	possibles = data.get_possibles()

	# if no possibilities and not solved discard the recursion
	if len(possibles) == 0:
		return -1

	x, y, choices = get_default_ordering_choice(possibles)
	if STRATEGY == "MOST":
		x, y, choices = get_most_constrained_choice(possibles)
	if STRATEGY == "LEAST":
		x, y, choices = get_least_constrained_choice(possibles)

	for k in choices:
		to_pass = copy.deepcopy(data)
		to_pass.assign_cell_rc(x, y, k)

		cc.recursive_call()
		result = solve(to_pass)

		if result != -1:
			return result

	return -1
