import random
import math

# Repersent a set of 8 queens that must resided on an 8x8 space.
from typing import Tuple


class BoardState:
    BOARD_SIZE = 8

    def __init__(self, occupied_spaces=[]):

        self._occupied_spaces = occupied_spaces


    # Simplify this problem by acknowleging that every column will have a queen
    def init_fill(self):

        for i in range(0, self.BOARD_SIZE):
            self._occupied_spaces.append((i, i))

    # compute the best neighbor by swaping the row of every queen against every other and taking the best outcome
    def best_neighbor(self):

        neighbors = {}

        def swap_row(dict, space_1, space_2):
            sp1_row = space_1[1]
            dict[space_1[0]] = space_2[1]
            dict[space_2[0]] = sp1_row

        #--------------------------------------------------------
        # This section allows for different out comes
        base_list = list(range(0, self.BOARD_SIZE))
        board_rows = base_list.copy()
        random.shuffle(board_rows)
        board_cols = base_list.copy()
        random.shuffle(board_cols)
        #--------------------------------------------------------

        for i in board_rows:
            for j in board_cols:
                if i != j:
                    oc_dict = {x: y for x, y in self._occupied_spaces}
                    start = self._occupied_spaces[i]
                    stop = self._occupied_spaces[j]
                    swap_row(oc_dict, start, stop)
                    board = BoardState(list(oc_dict.items()))
                    neighbors[board.get_threat_level()] = board

        lowest_threat = min(neighbors.keys())
        return neighbors[lowest_threat]

    #deep copy the board state
    def copy(self):
        new_board = BoardState()
        new_board._occupied_spaces = [x for x in self._occupied_spaces]
        return new_board

    # Compute number of threats that a queen faces. Higher number implies worse board
    def get_threat_level(self) -> int:

        #check that two queens are on same row
        def same_row(new: Tuple[int,int], existing: Tuple[int,int]) -> bool:
            return new[0] == existing[0]

        # check that two queens are on same column
        def same_col(new: Tuple[int,int], existing: Tuple[int,int])-> bool:
            return new[1] == existing[1]

        # Check that the difference in the x,y is the same, implying square shift, implying same diagnal.
        def same_diag(new: Tuple[int,int], existing: Tuple[int,int]) -> bool:
            return abs(new[0] - existing[0]) == abs(new[1] - existing[1])

        threat = 0
        for space in self._occupied_spaces:
            for other_space in self._occupied_spaces:
                spaces = [space, other_space]
                if space != other_space: #ignore current queen to allow for result of zero
                    if same_diag(*spaces):
                        threat += 1
                    if same_col(*spaces):
                        threat += 1
                    if same_row(*spaces):
                        threat += 1
        return threat

    #pretty print board.
    def __str__(self):
        rows = []
        for row in range(0, self.BOARD_SIZE):
            row_str = "".join(
                ["[Q]" if (row, col) in self._occupied_spaces else "[ ]" for col in range(0, self.BOARD_SIZE)])
            rows.append(row_str)
        rows.append(f"Threat Level: {self.get_threat_level()}")

        return '\n'.join(rows)




# use simualted annealing to get the best solution
def simulated_annealing(start):
    state = start
    for trial in reversed(range(10000000)):
        prev_state = state
        if trial == 0 or state.get_threat_level() == 0:
            return state
        rand_neighb = state.best_neighbor()
        new_h = rand_neighb.get_threat_level()
        old_h = prev_state.get_threat_level()

        dif_weight = new_h - old_h
        sol_better = new_h <= old_h
        accept_worse = random.uniform(0, 1) > math.exp(-dif_weight / trial)
        if sol_better or accept_worse:
            state = rand_neighb
            print(rand_neighb)
            print()


if __name__ == '__main__':
    bs = BoardState()
    bs.init_fill()
    simulated_annealing(bs)
