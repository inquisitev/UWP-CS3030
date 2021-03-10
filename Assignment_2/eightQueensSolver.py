import itertools, random
import math


class BoardState:
    BOARD_SIZE = 8

    def __init__(self,):
        self._board = [[False for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)]

        self._occupied_spaces = []

        while len(self._occupied_spaces) < self.BOARD_SIZE:
            new_space = random.randint(0,self.BOARD_SIZE - 1), random.randint(0,self.BOARD_SIZE - 1),
            if new_space not in self._occupied_spaces:
                self._occupied_spaces.append(new_space)

        for occupied_space in self._occupied_spaces:
            self.populate_space(*occupied_space)

    def copy(self):
        new_board = BoardState()
        for i, j in itertools.product(range(self.BOARD_SIZE), range(self.BOARD_SIZE)):
            if self.get_space(i, j):
                new_board.populate_space(i, j)
        return new_board

    def get_space(self, row, col):
        if not 0 <= row <= self.BOARD_SIZE:
            raise Exception("Bad Row")
        if not 0 <= col <= self.BOARD_SIZE:
            raise Exception("Bad Col")
        return self._board[row][col]

    def populate_space(self, row, col):
        if not 0 <= row <= self.BOARD_SIZE:
            raise Exception("Bad Row")
        if not 0 <= col <= self.BOARD_SIZE:
            raise Exception("Bad Col")

        self._board[row][col] = True

    def clear_space(self, row, col):
        if not 0 <= row <= self.BOARD_SIZE:
            raise Exception("Bad Row")
        if not 0 <= col <= self.BOARD_SIZE:
            raise Exception("Bad Col")

        self._board[row][col] = True

    def _same_row(self,new, existing):
        return new[0] == existing[0]

    def _same_col(self,new, existing):
        return new[1] == existing[1]

        # Check that the difference in the x,y is the same, implying square shift, implying same diagnol.
    def _same_diag(self, new, existing):
        return abs(new[0] - existing[0]) == abs(new[1] - existing[1])

    def get_threat_level(self):
        threat = 0
        for space in self._occupied_spaces:
            for other_space in self._occupied_spaces:
                spaces = [space, other_space]
                if space != other_space:
                    if self._same_diag(*spaces):
                        threat += 1
                    if self._same_col(*spaces):
                        threat += 1
                    if self._same_row(*spaces):
                        threat += 1
        return threat




    def __str__(self):
        rows = []
        for row in self._board:
            row_str = "".join(["[Q]" if x else "[ ]" for x in row])
            rows.append(row_str)
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
        rand_neighb = BoardState()
        new_h = rand_neighb.get_threat_level()
        old_h = prev_state.get_threat_level()

        dif_weight =  new_h - old_h
        sol_better = new_h < old_h
        accept_worse = random.uniform(0,1) > math.exp(-dif_weight/ trial)
        if sol_better or accept_worse:
            state = rand_neighb
            print(rand_neighb)
            print()



if __name__ == '__main__':
    bs = BoardState()
    simulated_annealing(bs)
