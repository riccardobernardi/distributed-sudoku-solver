# Distributed Sudoku Solver

Author: Riccardo Bernardi

E-mail: 864018@stud.unive.it

The code and the report were entirely developed only by Riccardo Bernardi.

## Table of Contents

- 1 Background
- 2 Web Scraping
- 3 Data Model
- 4 Constraint Propagation
- 5 BackTracking
- 6 Distributed Computation
- 7 Results
- 8 Conclusions
- 9 Bibliography

## 1 Background

The sudoku is a challenging game about finding the proper numbers that can stay in a certain cell of a 9x9 square. A number is correct when it respects the constraints of:

- 1 only one number with same value on the same row, column and 3x3 box
- 2 on the same row, column and 3x3 box have to be every number from 1 to 9 in only one copy

Some numbers at the start of the game are already provided on the sudoku and cannot be modified, you can only insert new numbers.

Another important notice about sudokus is that a sudoku that is correct should have exactly one solution, this is very important because asserting this fact will allow us to search for a solution with the certainty of converging.

Constraint Propagation is about taking the rule as written before and building a method that checks that fact but my implementation works in a different way, it prunes wrong solutions from possible ones. In particular at the very start every 0 cell(void cells to be calculated) are substituted by an array [1...9] and the **propagate_constraints** function will prune wrong ones.

Both **most-constrained** and **least-constrained** are implemented because of completeness but it is obvious and it is also proven by the empirical results that **most-constrained** is the best strategy(also used in the real game when done using pencil) because in the recursion you will find with more cells completed. This is because the only case in which you use backtracking is when the constraints become **cyclic** so no solution can be found with only the **propagation**, in this case solving one little constraint means that at least another one or more cells will be easily completed by the propagation in the recursion. Instead if you use the least constrained strategy probably you will complete only one cell with probably the wrong answer and you will need to have many and many recursions before knowing that your initial choice was wrong and so you need to close the stack and retry the same non-efficient strategy.

The easiest puzzles will be solved by just doing the steps before but for the hardest ones you will need to apply **backtracking** that is about searching for all possible solutions in the puzzle until the only one solution is found. If a wrong one is found it is ignored.

The author is a passionate sudoku solver and a passionate python programmer so you will find additions with respect to the basic assignment's requests.

Some libraries that were used in the assignment are previous projects of the author published on PYPI, in these cases will be put references.



## 2 Web Scraping



- checking the repetitions - antilagiarism
- some functional constructs - pygraham



## 3 Data Model



## 4 Constraint Propagation



## 5 BackTracking



## 6 Distributed Computation



## 7 Results



| Num. Sudoku | Time in mins | Description of improvement                                   | Constants                | Sudoku/s   |
| ----------- | ------------ | ------------------------------------------------------------ | ------------------------ | ---------- |
| 1899        | 26mins       |                                                              | MOST_CONSTR              | 0.89secs   |
| 1899        | 12mins       | pruning tree, adding more returns if data.void or data.duplicates | MOST_CONSTR              | 0.38secs   |
| 1899        | 7.9mins      | pruning tree, adding more propagation just before the recursion begins | MOST_CONSTR              | 0.25secs   |
| 1899        | 5mins        | distributing on the raspberry pi cluster                     | MOST_CONSTR, DISTRIBUTED | 0.0026secs |
| 1899        | a lot        |                                                              | LEAST_CONSTR             | a lot      |



## 8 Conclusions

I think that in this case the knowledge of the domain was crucial and I was able to devise a good solution since first try because I'm passionate.



## 9 Bibliography

- 





## Features

- webscraping from many sources
- constraint propagation
- distributed computation on a cluster
- check of similarity between sudokus
- ~2000 sudokus to evaluate performances