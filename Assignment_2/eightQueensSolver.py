import itertools, random
import math


class BoardState:
    BOARD_SIZE = 8

    def __init__(self, occupied_spaces=[]):

        self._occupied_spaces = occupied_spaces


    # Simplify this problem by acknowleging that every column will have a queen
    def init_fill(self):

        for i in range(0, self.BOARD_SIZE):
            self._occupied_spaces.append((i, i))

    def best_neighbor(self):

        neighbors = {}

        def swap_row(dict, space_1, space_2):
            sp1_row = space_1[1]
            dict[space_1[0]] = space_2[1]
            dict[space_2[0]] = sp1_row

        for i in range(0, self.BOARD_SIZE):
            for j in range(0, self.BOARD_SIZE):
                if i != j:
                    oc_dict = {x: y for x, y in self._occupied_spaces}
                    start = self._occupied_spaces[i]
                    stop = self._occupied_spaces[j]
                    swap_row(oc_dict, start, stop)
                    board = BoardState(list(oc_dict.items()))
                    neighbors[board.get_threat_level()] = board

        lowest_threat = min(neighbors.keys())
        return neighbors[lowest_threat]

    def copy(self):
        new_board = BoardState()
        new_board._occupied_spaces = [x for x in self._occupied_spaces]
        return new_board

    def get_threat_level(self):
        def same_row(new, existing):
            return new[0] == existing[0]

        def same_col(new, existing):
            return new[1] == existing[1]

        # Check that the difference in the x,y is the same, implying square shift, implying same diagnal.
        def same_diag(new, existing):
            return abs(new[0] - existing[0]) == abs(new[1] - existing[1])

        threat = 0
        for space in self._occupied_spaces:
            for other_space in self._occupied_spaces:
                spaces = [space, other_space]
                if space != other_space:
                    if same_diag(*spaces):
                        threat += 1
                    if same_col(*spaces):
                        threat += 1
                    if same_row(*spaces):
                        threat += 1
        return threat

    def __str__(self):
        rows = []
        for row in range(0, self.BOARD_SIZE):
            row_str = "".join(
                ["[Q]" if (row, col) in self._occupied_spaces else "[ ]" for col in range(0, self.BOARD_SIZE)])
            rows.append(row_str)
        rows.append(f"Threat Level: {self.get_threat_level()}")

        return '\n'.join(rows)


# dont generate new random each time. Modify current state then select the best one or a possible worst one
# add a move_queen, get open rows, get open cols, get queens that share row/col, generate neighbors

def simulated_annealing(start):
    state = start
    prev_state = start
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
