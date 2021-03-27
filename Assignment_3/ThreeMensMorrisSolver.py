import itertools, math
from anytree import Node, RenderTree
from anytree.dotexport import DotExporter
from anytree.render import ContStyle
from anytree.dotexport import RenderTreeGraph
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

def print_board(board, indent = 0):

    def val_or_b(row: int, col: int) -> str:
        val = board[row][col]
        if val == BLANK:
          return "B"
        else:
          return str(val)


    out = [
        '\t' * indent + "+--------------+",
        '\t' * indent + f"| {val_or_b(0, 0)}    {val_or_b(0, 1)}    {val_or_b(0, 2)}  |",
        '\t' * indent + f"| {val_or_b(1, 0)}    {val_or_b(1, 1)}    {val_or_b(1, 2)}  |",
        '\t' * indent + f"| {val_or_b(2, 0)}    {val_or_b(2, 1)}    {val_or_b(2, 2)}  |",
        '\t' * indent + "+--------------+"
    ]

    joiner = '\n' 
    print(joiner.join(out))

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
    if check_wins(board):
        return [board]
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


def get_player_on_line(board, player, line):
    count = 0
    for x,y in line:
        if board[x][y] == player:
            count += 1

    return count



def rate_board(board):
    res = check_wins(board)
    if res == PLAYER_1:
        return 1000000000
    if res == PLAYER_2:
        return -1000000000
    return 0

parents = {}
visited = set()
def minimax(board, maxing_player, depth = 0):
    wins = check_wins(board)
    if wins != None or str(board) in visited :

        return rate_board(board)

    visited.add(str(board))
    #visited must be board at depth
    if maxing_player:
        best = -1000
        bestNeighbor = None
        neighbors = make_neighbors(board, PLAYER_1)

        if len(neighbors) == 0: #If no adjacent positions are empty, the player loses its turn and the other player makes their move

            return minimax(board, not maxing_player, depth +1 )
        for neighbor in neighbors:
            value = minimax(neighbor, not maxing_player, depth + 1) if str(neighbor) not in visited else 0

            if value >= best:
                best = value
                bestNeighbor = neighbor
                
        parents[str(board)] = bestNeighbor
        return best
    else:
        best = 1000
        bestNeighbor = None
        neighbors = make_neighbors(board, PLAYER_2)
        if len(neighbors) == 0: #If no adjacent positions are empty, the player loses its turn and the other player makes their move
            return minimax(board, not maxing_player, depth + 1)
        
        for neighbor in neighbors:


            value = minimax(neighbor, not maxing_player, depth + 1) if str(neighbor) not in visited else 0

            if value >= best:
                best = value
                bestNeighbor = neighbor
        
        parents[str(board)] = bestNeighbor
        return best


board = make_board()
#board[0][2] = PLAYER_1
#board[1][1] = PLAYER_1
#board[2][2] = PLAYER_1
#
#
#board[2][0] = PLAYER_2
#board[2][1] = PLAYER_2
#board[0][0] = PLAYER_2

cboard = copy_board(make_board())
node = Node(str(board))
val = minimax(board,  False)

print_board(board)
node = str(board)
while node in parents:
    board = parents[node]
    node = str(board)
    print_board(board)