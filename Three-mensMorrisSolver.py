import itertools
from operator import add

class BoardState:
  BLANK_SPACE = -1
  PLAYER_1_SPACE = 1
  PLAYER_2_SPACE = 2
  BOARD_SIZE = 3
  def __init__(self, board = None):
    if board:
      self._board = board
    else:
      self._board = [[self.BLANK_SPACE for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)]

  def copy(self) -> 'BoardState':
        new_state = [[x for x in row] for row in self._board]
        return BoardState(new_state)

  def __hash__(self):
        return hash(str(self))

  def __eq__(self, other: 'BoardState') -> bool:

        def tiles_are_equal(i: int, j: int) -> bool:
            return self._board[i][j] == other._board[i][j]

        b_range = range(self.BOARD_SIZE)

        equalities = [tiles_are_equal(i, j) for i, j in itertools.product(b_range, b_range)]
        return all(equalities)

  def __str__(self):

        def val_or_b(row: int, col: int) -> str:
            val = self._board[row][col]
            if val == self.BLANK_SPACE:
              return "B"
            elif val == self.PLAYER_1_SPACE:
              return "1"
            elif val == self.PLAYER_2_SPACE:
              return "2"


        out = [
            "+--------------+",
            f"| {val_or_b(0, 0)}    {val_or_b(0, 1)}    {val_or_b(0, 2)}  |",
            f"| {val_or_b(1, 0)}    {val_or_b(1, 1)}    {val_or_b(1, 2)}  |",
            f"| {val_or_b(2, 0)}    {val_or_b(2, 1)}    {val_or_b(2, 2)}  |",
            "+--------------+"
        ]

        return '\n'.join(out)

  def get_neighboring_spaces(self, space):

    deltas = [(0, 1), (1, 0), (0, -1), (-1, 0) ]

    def in_board(sp):
      return all([0 <= x < self.BOARD_SIZE for x in sp] )

    possible_spaces = [tuple(map(add, space, delta )) for delta in deltas]
    return [good_space for good_space in possible_spaces if in_board(good_space)]


  def get_value_at_space(self, space):
    return self._board[space[0]][space[1]]
  
  def set_value_at_space(self, space, val):
    self._board[space[0]][space[1]] = val

  def check_win(self):
    rows = [((i,0), (i,1), (i,2)) for i in range(self.BOARD_SIZE) ]
    cols = [((0,i), (1,i), (2,i)) for i in range(self.BOARD_SIZE)]
    diags = [tuple((j,j) for j in range(self.BOARD_SIZE)) ]

    lines = rows + cols + diags

    for line in lines:
        vals = set(self._board[space[0]][space[1]] for space in line)
        val = next(iter(vals)) 

        # If the set has only one element and it is not a blank space then we have a line populated
        # by a single player mark indicating a win
        if len(vals) == 1 and val != self.BLANK_SPACE:
            return ((val,line))
    
    return False

  def get_player_spaces(self, player):
    return self._get_spaces_by_value(player)

  def get_blank_spaces(self):
    return self._get_spaces_by_value(self.BLANK_SPACE)

  def _get_spaces_by_value(self, value):
    
    spaces_of_interest = []

    spaces = range(self.BOARD_SIZE)
    for space in itertools.product(spaces, spaces):
      if self.get_value_at_space(space) == value:
        spaces_of_interest.append(space)

    return spaces_of_interest


class SearchNode:
  def __init__(self, board_state):
    self.board_state = board_state

  def is_leaf(self, previous_states):
    leaf_conditions = [
      self.board_state in previous_states,
      self.board_state.check_win()
    ]

    return any(leaf_conditions)

  def get_heuristic_value(self, player, depth):
    recorded_win = self.board_state.check_win()
    if recorded_win:
      return 1 if player == recorded_win[0] else -1
    else:
      return 0
  
  def get_neighbors(self, player):
    neighbors = []
    player_spaces = self.board_state.get_player_spaces(player)
    if len(player_spaces) < 3:
      for space in self.board_state.get_blank_spaces():
        new_board = self.board_state.copy()
        new_board.set_value_at_space(space, player)
        neighbors.append(new_board)

    else:
      for player_space in player_spaces:
        for space in self.board_state.get_neighboring_spaces(player_space):
          space_val = self.board_state.get_value_at_space(space)
          if space_val == self.board_state.BLANK_SPACE:
            new_board = self.board_state.copy()
            new_board.set_value_at_space(space, player)
            new_board.set_value_at_space(player_space, self.board_state.BLANK_SPACE)
            neighbors.append(new_board)

    return neighbors
    


visited_states = []
def minimax(node, depth, max_player_1):
  if depth == 0 or node.is_leaf(visited_states):
    return node.get_heuristic_value(1 if max_player_1 else 2, depth)
  

bs = BoardState()
bs.set_value_at_space((0,0),1)
bs.set_value_at_space((0,1),2)
bs.set_value_at_space((0,2),1)

sn = SearchNode(bs)
print(minimax(sn, 1, True))


