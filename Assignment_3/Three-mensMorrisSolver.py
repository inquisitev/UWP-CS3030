import itertools, math
from operator import add, gt, lt

class BoardState:
  BLANK_SPACE = -1
  PLAYER_1_SPACE = 1
  PLAYER_2_SPACE = 2
  BOARD_SIZE = 3
  def __init__(self, board = None, move_msg = ""):
    self.move_msg = move_msg
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
            f"| {val_or_b(1, 0)}    {val_or_b(1, 1)}    {val_or_b(1, 2)}  | {self.move_msg}",
            f"| {val_or_b(2, 0)}    {val_or_b(2, 1)}    {val_or_b(2, 2)}  |",
            "+--------------+"
        ]

        return '\n'.join(out)

  def get_neighboring_spaces(self, space):

    deltas = [(0, 1), (1, 0), (0, -1), (-1, 0), (1,1),(-1,1),(1,-1),(-1,-1)]

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
    diags = [tuple((j,j) for j in range(self.BOARD_SIZE)) ] + [tuple((self.BOARD_SIZE - 1 - j,j) for j in range(self.BOARD_SIZE)) ]

    lines = rows + cols + diags

    for line in lines:
        vals = set(self._board[space[0]][space[1]] for space in line)
        val = next(iter(vals))

        # If the set has only one element and it is not a blank space then we have a line populated
        # by a single player mark indicating a win
        if len(vals) == 1 and val != self.BLANK_SPACE:
            return val
    
    return None

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
      if player == recorded_win[0]:
        val = 1
      else: 
        val = -1
      return val
    else:
      return 0
  
  def get_neighbors(self, player):
    neighbors = []
    player_spaces = self.board_state.get_player_spaces(player)
    if len(player_spaces) < 3:
      for space in self.board_state.get_blank_spaces():
        new_board = self.board_state.copy()
        new_board.move_msg = f"Place for {player} at {space}"
        new_board.set_value_at_space(space, player)
        neighbors.append(new_board)

    else:
      for player_space in player_spaces:
        for space in self.board_state.get_neighboring_spaces(player_space):
          space_val = self.board_state.get_value_at_space(space)
          if space_val == self.board_state.BLANK_SPACE:
            new_board = self.board_state.copy()

            new_board.move_msg = f"Move for {player} From {player_space} To {space}"
            new_board.set_value_at_space(space, player)
            new_board.set_value_at_space(player_space, self.board_state.BLANK_SPACE)
            neighbors.append(new_board)

    return neighbors
    

parents = {}
visited_states = set()
def minimax(node, depth, max_player_1):


  current_player = 1 if max_player_1 else 2
  evaluate = max if max_player_1 else min
  best = -math.inf if max_player_1 else math.inf
  comparator = gt if max_player_1 else lt

  winner = node.board_state.check_win()
  if winner == 1:
    return 1
  elif winner == 2:
    return -1
  elif depth == 0:
    return 0





  #make dict key -> heuristic, value -> neighbor
  neighbors = {}
  for neighbor in node.get_neighbors(current_player):
    value = minimax(SearchNode(neighbor), depth - 1, not max_player_1)
    visited_states.add(neighbor)
    neighbors[value] = neighbor
  

  best = evaluate(neighbors.keys())
  best_neighbor = neighbors[best]
  parents[node.board_state] = best_neighbor
  return best
  

bs = BoardState()
sn = SearchNode(bs)
bs.check_win()
print(minimax(sn,10, True))

node = parents[bs]
print(bs)
while node in parents.keys():
    node = parents[node]
    print(node)


