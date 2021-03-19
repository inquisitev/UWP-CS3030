from typing import List, Tuple, Callable
import itertools, time, sys, random

WANT_APROX_DEPTH = True
if WANT_APROX_DEPTH:
    depths = []

# Puzzle state represents a 3 by 3 board of spaces.
# 8 spaces are occupied by a tile. One space is blank.
# Each tile has a label.
class PuzzleState:
    BLANK = -1
    BOARD_SIZE = 3
    VALID_TILE_VALUE_RANGE = list(range(1, 9)) + [-1]

    # The state is represented by a list of lists. Must be 3 lists containing 3 integers between 1 and 8 and -1
    def __init__(self, rows: List[List[int]]):
        self._rows = rows

        existing_vals = []
        for row in rows:
            if len(row) != self.BOARD_SIZE:
                raise Exception("Bad game state.")
            for val in row:
                if type(val) != int or val not in self.VALID_TILE_VALUE_RANGE:
                    raise Exception(f"Bad tile value. {val}")
                elif val in existing_vals:
                    raise Exception("Val already in state.")
                else:
                    existing_vals.append(val)

    # Print the current board in a nice 3x3 grid with a border
    def __str__(self):

        def val_or_b(row: int, col: int) -> str:
            return self._rows[row][col] if self._rows[row][col] != self.BLANK else "B"

        out = [
            "+--------------+",
            f"| {val_or_b(0, 0)}    {val_or_b(0, 1)}    {val_or_b(0, 2)}  |",
            f"| {val_or_b(1, 0)}    {val_or_b(1, 1)}    {val_or_b(1, 2)}  |",
            f"| {val_or_b(2, 0)}    {val_or_b(2, 1)}    {val_or_b(2, 2)}  |",
            "+--------------+"
        ]

        return '\n'.join(out)

    # serialize the board to allow usage of 'in' keyword when interacting with lists
    def __hash__(self):
        return hash(str(self))

    @property
    # get the raw list of lists that describe the state of the board
    def rows(self):
        return self._rows

    # two boards are equal provided that for every row and every column, the value of the row, col combo match
    def __eq__(self, other: 'PuzzleState') -> bool:

        def tiles_are_equal(i: int, j: int) -> bool:
            return self.get_tile(i, j) == other.get_tile(i, j)

        b_range = range(self.BOARD_SIZE)

        equalities = [tiles_are_equal(i, j) for i, j in itertools.product(b_range, b_range)]
        return all(equalities)

    # get the coordinates of a board after compensation for overflow. row `BOARD_SIZE + 1` should be row `0`
    def in_board_coords(self, row: int, col: int) -> Tuple[int, int]:

        mrow = row % self.BOARD_SIZE
        mcol = col % self.BOARD_SIZE
        return mrow, mcol

    # get value of tile at row,col intersection
    def get_tile(self, row: int, col: int) -> int:
        mrow, mcol = self.in_board_coords(row, col)
        return self._rows[mrow][mcol]

    # set value of tile at row,col intersection
    def set_tile(self, row: int, col: int, val: int):
        mrow, mcol = self.in_board_coords(row, col)
        self._rows[mrow][mcol] = val

    # check if tile_pos is neighbor of current blank node, true implying that swap is legal
    def can_swap_with_blank(self, tile_pos: Tuple[int, int]) -> bool:
        tile_pos = self.in_board_coords(tile_pos[0], tile_pos[1])
        blank_x, blank_y = self.get_blank_node()

        allowed_moves = [
            self.in_board_coords(blank_x + 1, blank_y) == tile_pos,
            self.in_board_coords(blank_x, blank_y + 1) == tile_pos,
            self.in_board_coords(blank_x - 1, blank_y) == tile_pos,
            self.in_board_coords(blank_x, blank_y - 1) == tile_pos,
        ]

        return any(allowed_moves)

    # swap tile_pos with current blank position
    def swap_with_blank(self, tile_pos: Tuple[int, int]) -> None:
        blank = self.get_blank_node()
        val = self.get_tile(tile_pos[0], tile_pos[1])
        self.set_tile(blank[0], blank[1], val)
        self.set_tile(tile_pos[0], tile_pos[1], self.BLANK)

    # get the position of the blank node
    def get_blank_node(self) -> Tuple[int, int]:
        for i in range(self.BOARD_SIZE):
            for j in range(self.BOARD_SIZE):
                val = self._rows[i][j]
                if val == self.BLANK:
                    return i, j

    # create deep copy of the puzzel state
    def copy(self) -> 'PuzzleState':
        new_state = [[x for x in row] for row in self._rows]
        return PuzzleState(new_state)

    # Lower weight means better option
    def get_heuristic_weight(self, goal: 'PuzzleState') -> int:
        out_of_place_tiles = 0
        board_range = range(self.BOARD_SIZE)
        for i, j in itertools.product(board_range, board_range):
            if self.get_tile(i, j) != self.BLANK and self.get_tile(i, j) != goal.get_tile(i, j):
                out_of_place_tiles += 1

        return out_of_place_tiles


# A search node wraps the puzzle state to provide neighbor calculations.
class SearchNode:

    def __init__(self, state: PuzzleState):
        self._puzzle_state = state

    @property
    # the current puzzle state of the search node
    def state(self) -> PuzzleState:
        return self._puzzle_state

    # compute a list of neighbors, Should always provide a list of four boards with the
    # blank tile in a position up, down, left, or right, by one space only
    def neighbors(self) -> List[PuzzleState]:
        state = self._puzzle_state
        blank = state.get_blank_node()
        neighbors = []

        new_state = self._puzzle_state.copy()
        if new_state.can_swap_with_blank((blank[0] + 1, blank[1])):
            new_state.swap_with_blank((blank[0] + 1, blank[1]))
            neighbors.append(new_state)

        new_state = self._puzzle_state.copy()
        if new_state.can_swap_with_blank((blank[0], blank[1] + 1)):
            new_state.swap_with_blank((blank[0], blank[1] + 1))
            neighbors.append(new_state)

        new_state = self._puzzle_state.copy()
        if new_state.can_swap_with_blank((blank[0] - 1, blank[1])):
            new_state.swap_with_blank((blank[0] - 1, blank[1]))

            neighbors.append(new_state)

        new_state = self._puzzle_state.copy()
        if new_state.can_swap_with_blank((blank[0], blank[1] - 1)):
            new_state.swap_with_blank((blank[0], blank[1] - 1))
            neighbors.append(new_state)

        return neighbors


# Search for goal using breadth first search, return a list of PuzzleStates starting with start and ending with goal
def breadth_first_search(start: PuzzleState, goal: PuzzleState) -> List[PuzzleState]:
    front = [start]
    parents = {}
    visited = set()

    node = front.pop()

    while node != goal:
        neighbors = [x for x in SearchNode(node).neighbors() if x not in visited]

        # Adding this line to attempt to maintain fairness between bfs and dfs
        #neighbors.sort(key=lambda x: x.get_heuristic_weight(goal))
        if neighbors:
            front = neighbors + front
            for c in neighbors:
                visited.add(c)
                if c not in parents:
                    parents[c] = node
        node = front.pop()

    path = [goal]

    node = parents[goal]
    while node != start:
        path.append(node)
        node = parents[node]
    path.append(start)

    return list(reversed(path))


# using psuedo code from https://www.geeksforgeeks.org/iterative-deepening-searchids-iterative-deepening-depth-first-searchiddfs/

# Use iterative deepening depth first search to find a path from start state to goal state
# return the path taken to reach goal, or empty list if path does not exist.
def iterative_deepening_depth_first_search(start: PuzzleState, goal: PuzzleState) -> List[PuzzleState]:
    parents = {}
    visited = set()
    MAX_DEPTH = 100000 #Pythons max recusion size is 1000 anyways...

    # depth limited search inner recursive function
    def dls(cstart: PuzzleState, cgoal: PuzzleState, climit: int):

        visited.add(cstart)
        if cstart == cgoal:
            return True

        if climit <= 0:
            return False

        neighbors = SearchNode(cstart).neighbors()

        # --------------------------------------------------------------------------------------------------------------
        # Must add this line to avoid stack overflow.
        # have tried raising stack size, cant get that to happen. Am keeping track of neighbors that have been
        # visited, some solutions just require a larger stack than python will let me have. Well aware that this skews
        # search times and would prefer to not use this hack.
        #neighbors.sort(key=lambda x: x.get_heuristic_weight(goal))
        # --------------------------------------------------------------------------------------------------------------

        for neighbor in neighbors:
            if neighbor not in parents:
                parents[neighbor] = cstart
            if neighbor not in visited:
                if dls(neighbor, cgoal, climit - 1):
                    return True

    found = False
    for limit in range(0, MAX_DEPTH):
        visited = set()
        if dls(start, goal, limit):
            found = True
            if WANT_APROX_DEPTH:
                depths.append(limit)
            break

    if found:
        path = [goal]
        node = parents[goal]
        while node != start:
            path.append(node)
            node = parents[node]
        path.append(start)
        return list(reversed(path))
    else:
        return []


def a_star_search(start: PuzzleState, goal: PuzzleState) -> List[PuzzleState]:
    front = [start]
    visited = [start]
    parents = {}

    def a_star(front, visited, goal):
        if len(front) == 0:
            return False
        node = front.pop()
        if node != goal:
            visited.append(node),
            for neighbor in SearchNode(node).neighbors():
                if neighbor not in visited:
                    front.append(neighbor)
                    if neighbor not in parents:
                        parents[neighbor] = node

            front.sort(key=lambda x: x.get_heuristic_weight(goal), reverse=True)
            a_star(front, visited, goal)
        else:
            return True

    a_star(front, visited, goal)

    path = [goal]
    node = parents[goal]
    while node != start:
        path.append(node)
        node = parents[node]
    path.append(start)

    return reversed(path)


problems = [
    {
        "start": PuzzleState([[1, 7, 3], [4, 5, 6], [-1, 2, 8]]),
        "goal": PuzzleState([[1, 2, 3], [4, 5, 6], [7, 8, -1]])
    },

    {
        "start": PuzzleState([[1, 2, 6], [4, 5, 3], [-1, 7, 8]]),
        "goal": PuzzleState([[1, 2, 3], [4, 5, 6], [7, 8, -1]])
    },

    {
        "start": PuzzleState([[1, 2, 6], [-1, 7, 8], [4, 5, 3]]),
        "goal": PuzzleState([[1, 2, 3], [4, 5, 6], [7, 8, -1]])
    },
    #
    {
        "start": PuzzleState([[-1, 7, 8], [1, 2, 6], [4, 5, 3]]),
        "goal": PuzzleState([[1, 2, 3], [4, 5, 6], [7, 8, -1]])
    },

    {
        "start": PuzzleState([[1, 8, 2], [-1, 4, 3], [7, 6, 5]]),
        "goal": PuzzleState([[1, 2, 3], [4, 5, 6], [7, 8, -1]])
    },
]


# Take a list of board states that would be printed in sequence vertically in console and make them all printed
# on the same row with arrows in between to nicely display a path. Will return a string ready to print to console
def vertical_path_to_horizontal(iterator: List) -> str:
    rows = [[] for _ in range(5)]
    board_num = 0
    for board in iterator:
        row = str(board).split('\n')
        for i in range(len(row)):
            rows[i].append(row[i])
        board_num += 1

    printable_rows = []
    row_num = 0
    for row in rows:
        seperator = "  -> " if row_num == int(len(rows) / 2) else "     "
        printable_rows.append(seperator.join(row))
        row_num += 1
    return '\n'.join(printable_rows)


# solve the search problem, print out revelent data regaurding the search, Label is a name for the function,
# func is the sorting function {bfs, dldfs, a*} and args is a list containing start state and end state in that order
def time_n_print_solve(label: str, func: Callable, args: Tuple[PuzzleState, PuzzleState]):
    tic = time.perf_counter()
    solution = vertical_path_to_horizontal(func(*args))
    toc = time.perf_counter()

    out = []
    out.append('-' * 180)
    out.append(f"Searching via {label} took {toc - tic:0.4f} seconds")
    out.append(f"Start{' ' * 15} Goal")
    out.append(vertical_path_to_horizontal(args))
    out.append('')
    out.append("Solution")
    out.append(solution)

    out.append('-' * 180)
    return toc - tic, '\n'.join(out)

def make_random_puzzle():
    spaces = [1, 2, 3, 4, 5, 6, 7, 8, -1]

    random.shuffle(spaces)
    spaces = [spaces[0:3],spaces[3:6],spaces[6:9]]

    return PuzzleState(spaces)


def approximate_average_depth():
    # Generate random boards
    # run iterative deepening on all of them
    # record depth of solution
    # find average depth of all solutions

    goal = PuzzleState([[1, 2, 3], [4, 5, 6], [7, 8, -1]])
    
    for trial in range(100):    
        problem = make_random_puzzle()
        iterative_deepening_depth_first_search(problem, goal)
        print(depths[-1])
    print(sum(depths)/len(depths))

approximate_average_depth()

def run_algos():

    algs = {"BFS": breadth_first_search, "IDDFS": iterative_deepening_depth_first_search, "A*": a_star_search}

    times = {label: [] for label in algs.keys()}
    results = {label: [] for label in algs.keys()}

    for problem in problems:
        for label, algo in algs.items():
            result = time_n_print_solve(label, algo, problem.values())
            times[label].append(result[0])
            results[label].append(result[1])

    for label in algs.keys():
        with open(f"{label}_results.txt", 'w+') as out_file:
            for result in results[label]:
                out_file.write(str(result))
                out_file.write("\n\n\n")

    with open("times.txt", 'w+') as out_file:
        for label, time_vals in times.items():
            avg_time = sum(time_vals) / len(time_vals)
            print(f"{label} -> {str(avg_time)}")
            out_file.write(f"{label} -> {str(avg_time)}\n")
