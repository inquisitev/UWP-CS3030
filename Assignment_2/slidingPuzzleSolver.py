from typing import List, Tuple
import itertools


# Puzzle state represents a 3 by 3 board of spaces.
# 8 spaces are occupied by a tile. One space is blank.
# Each tile has a label.
class PuzzleState:
    BLANK = -1
    BOARD_SIZE = 3
    VALID_TILE_VALUE_RANGE = list(range(1, 9)) + [-1]

    # The state is represented by a list of lists.
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
    mfront = [start]
    parents = {}
    visited = set()
    pnode = None

    # inner recursive search function
    def bfs(front: PuzzleState, cgoal):
        node = front.pop()

        while node != goal:
            neighbors = [x for x in SearchNode(node).neighbors() if x not in visited]
            neighbors.sort(key=lambda x: x.get_heuristic_weight(goal), reverse=True)
            if neighbors:
                front = neighbors + front
                for c in neighbors:
                    visited.add(c)
                    if c not in parents:
                        parents[c] = node
            node = front.pop()

        return node

    res = bfs(mfront, goal)

    if res:
        path = []

        path.append(goal)
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
    visited = []
    MAX_DEPTH = 2 ** 12  # just a real big number...

    # depth limited search inner recursive function
    def dls(cstart: PuzzleState, cgoal: PuzzleState, climit: int):

        visited.append(cstart)
        if cstart == cgoal:
            return True

        if limit <= 0:
            return False

        neighbors = SearchNode(cstart).neighbors()
        neighbors.sort(key=lambda x: x.get_heuristic_weight(goal))
        for neighbor in neighbors:
            if neighbor not in parents:
                parents[neighbor] = cstart
            if neighbor not in visited:
                if dls(neighbor, cgoal, climit - 1):
                    return True

    found = False
    for limit in range(0, MAX_DEPTH):
        if dls(start, goal, limit):
            found = True
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


def a_star_search(start, goal):
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
        "start": PuzzleState([[1, 2, 3], [4, 5, 6], [-1, 7, 8]]),
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


def vertical_path_to_horizontal(iterator):
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


def time_n_print_solve():
    print(vertical_path_to_horizontal(breadth_first_search(*problem.values())))


if __name__ == '__main__':

    for problem in problems:
        print(vertical_path_to_horizontal(breadth_first_search(*problem.values())))
        vertical_path_to_horizontal(iterative_deepening_depth_first_search(*problem.values()))
        vertical_path_to_horizontal(a_star_search(*problem.values()))
