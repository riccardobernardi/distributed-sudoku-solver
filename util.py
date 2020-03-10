from pygraham import *

RANK = 3

def show(matrix):
	for i in matrix:
		for j in i:
			for k in j:
				print(k, end = '')

			print(" ",end='')
		print()

class Sudodata():
	def __init__(self, matrix):
		self.data = list(matrix)
		# self.cell_transform()

	def cell_rc(self,r,c):
		return self.data[r][c//RANK][c%RANK]

	def assign_cell_rc(self,r,c,v):
		#print(self.data[r][c//RANK][c%RANK],type(self.data[r][c//RANK][c%RANK]))
		for i,j in enumerate(self.row_iter()):
			

	def cell_rtc(self,r,t,c):
		return self.data[r][t][c]

	def column(self,c):
		return list([self.data[i][c//RANK][c%RANK] for i in range(RANK*RANK)])

	def row(self,r):
		return list([self.data[r][i//RANK][i%RANK] for i in range(RANK*RANK)])

	def triplet(self,r,t):
		return list(self.data[r][t])

	def cell_transform(self):
		for i in range(RANK*RANK):
			for j in range(RANK * RANK):
				self.assign_cell_rc(i,j,int(self.cell_rc(i,j)))

	def cell_iter(self):
		for i in range(RANK*RANK):
			for j in range(RANK * RANK):
				yield self.cell_rc(i,j)

	def row_iter(self):
		for i in range(RANK*RANK):
			yield self.row(i)

	def col_iter(self):
		for i in range(RANK*RANK):
			yield self.column(i)

	def box_iter(self):
		for v in range(RANK):
			for i in range(RANK):
				box = []
				for j in range(RANK):
					for k in range(RANK):
						box += self.cell_rc(v*RANK + j,i*RANK+k)

				yield box


def solve_bt(matrix):
	pass

def solve_cs(matrix):
	data = Sudodata(matrix)
	for i in data.box_iter():
		print(i)
