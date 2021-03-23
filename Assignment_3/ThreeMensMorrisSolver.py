import itertools, math
from operator import add
BLANK = -1
PLAYER_1 = 1
PLAYER_2 = 2

WIN_LINES =  [
        [(0,0),(0,1),(0,2)],
        [(1,0),(1,1),(1,2)],
        [(2,0),(2,1),(2,2)],
        [(0,0),(1,0),(2,0)],
        [(0,1),(1,1),(2,1)],
        [(0,2),(1,2),(2,2)],
        [(0,0),(1,1),(2,2)],
        [(0,2),(1,1),(2,0)],
        ]

def make_board():
    return [[-1,-1,-1],[-1,-1,-1],[-1,-1,-1]]

def copy_board(board):
    return [[board[j][i] for i in range(3)] for j in range(3)]

def print_board(board):

    def val_or_b(row: int, col: int) -> str:
        val = board[row][col]
        if val == BLANK:
          return "B"
        elif val == PLAYER_1:
          return "1"
        elif val == PLAYER_2:
          return "2"


    out = [
        "+--------------+",
        f"| {val_or_b(0, 0)}    {val_or_b(0, 1)}    {val_or_b(0, 2)}  |",
        f"| {val_or_b(1, 0)}    {val_or_b(1, 1)}    {val_or_b(1, 2)}  |",
        f"| {val_or_b(2, 0)}    {val_or_b(2, 1)}    {val_or_b(2, 2)}  |",
        "+--------------+"
    ]

    print('\n'.join(out))

def check_wins(board):
    
    
    for line in WIN_LINES:
        vals = set()
        for x,y in line:
            vals.add(board[x][y])
        val = next(iter(vals))
        if len(vals) == 1 and val != BLANK:
            return val
    else:
        return None

def calculate_heuristic_value(board, player):
    
    value = 0
    for line in WIN_LINES:
        occs = 0
        for x,y in line:
            if board[x][y] == player:
                occs += 1
        value += 2 ** occs if occs > 0 else 0
    return value

def get_pieces(board, player):
    pieces = []
    for i,j in itertools.product(range(3), range(3)):
        if board[i][j] == player:
            pieces.append((i,j))
    return pieces

def make_neighbors(board, active_player):
    neighbors = []
    occurances = get_pieces(board, active_player)
    if len(occurances) < 3:
        for i,j in itertools.product(range(3), range(3)):
            if board[i][j] == BLANK:
                neighbor = copy_board(board)
                neighbor[i][j] = active_player
                neighbors.append(neighbor)
    else:
        deltas = [(-1,1), (1,0), (1,1), (1, 0), (1,-1), (0,-1), (-1,-1), (-1, 0)]
        new_positions = set()
        for occurance in occurances:
            for delta in deltas:
                new_pos = tuple(map(add, occurance, delta ))
                if 0 <= new_pos[0] < 3 and 0 <= new_pos[1] < 3 and board[new_pos[0]][new_pos[1]] == BLANK:
                    new_positions.add((occurance, new_pos))
        for start, end in iter(new_positions):
            new_board = copy_board(board)
            new_board[start[0]][start[1]] = BLANK
            new_board[end[0]][end[1]] = active_player
            neighbors.append(new_board)
        
    return neighbors


def rate_board(board):
    res = check_wins(board)
    if res == 1:
        return 1000
    elif res == 2:
        return -1000
    else:
        return calculate_heuristic_value(board, 1) - calculate_heuristic_value(board ,2)

visited = []
def minimax(board, max_turn):

    rating = rate_board(board)

    visited.append(board)
    if rating == 1000 or rating == -1000:
        return rating
    
    

    if max_turn:
        neighbors = make_neighbors(copy_board(board), 1)

        outcomes = {minimax(neighbor, False): neighbor for neighbor in neighbors if neighbor not in visited}

        keys = list(outcomes.keys() )
        best = max(keys + [0])
        if best in keys:
            print_board(outcomes[best])

        return best
    
    else:
        neighbors = make_neighbors(copy_board(board), 2)
        

        outcomes = {minimax(neighbor, True): neighbor for neighbor in neighbors  if neighbor not in visited}
        keys = list(outcomes.keys())
        best = min(keys + [0])
        if best in keys:
            print_board(outcomes[best])

        return best


print(minimax(make_board(), False))



