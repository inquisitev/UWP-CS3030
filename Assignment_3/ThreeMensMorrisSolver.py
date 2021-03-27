import itertools, math
from operator import add
BLANK = 0
PLAYER_1 = 1
PLAYER_2 = -1

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
    return [[BLANK,BLANK,BLANK],[BLANK,BLANK,BLANK],[BLANK,BLANK,BLANK]]

def copy_board(board):
    return [[board[j][i] for i in range(3)] for j in range(3)]

def print_board(board, indent = 0, console = True):

    def val_or_b(row: int, col: int) -> str:
        val = board[row][col]
        if val == BLANK:
          return "B"
        elif val == PLAYER_1:
            return "1"

        elif val == PLAYER_2:
            return "2"
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
    if console:
        print(joiner.join(out))
    else: 
        return joiner.join(out)

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
# Take a list of board states that would be printed in sequence vertically in console and make them all printed
# on the same row with arrows in between to nicely display a path. Will return a string ready to print to console
def vertical_path_to_horizontal(iterator) -> str:
    rows = [[] for _ in range(5)]
    board_num = 0
    for board in iterator:
        row = print_board(board, console=False).split('\n')
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

def get_player_on_line(board, player, line):
    count = 0
    for x,y in line:
        if board[x][y] == player:
            count += 1

    return count

def get_parents(board):
    game_states = []
    game_states.append(board)
    node = str(board)
    while node in parents:
        board = parents[node]
        node = str(board)
        game_states.append(board)
    return game_states

class Node:
    def __init__(self, board, parent, maxing = True, depth = 0):
        self.board = board
        self.parent = parent
        self.value = 0
        self.children = []
        self.maxing = maxing
        self.depth = depth
    
    def __str__(self):
        return f"VAL: {self.value}, MAX: {self.maxing}, DEPTH: {self.depth} BOARD: {self.board}"
    
    def __repr__(self):
        return self.__str__()

    def is_ancestor(self,board):

        if self.parent is None:
            return False
        
        current = self.parent
        while current is not None:
            if current.board == board:
                return True
            current = current.parent
        return False


def rate_board(board):
    res = check_wins(board)
    if res == PLAYER_1:
        return 1
    if res == PLAYER_2:
        return -1
    return 0

parents = {}
visited = set()
def minimax(node, maxing_player, depth = 0):
    board = node.board
    wins = check_wins(board)
    if wins != None:
        return rate_board(board)

    best, player, compare = (-1000000, PLAYER_1, lambda a,b : a >= b) if maxing_player else (1000000, PLAYER_2, lambda a,b : a <= b)
    
    neighbors = make_neighbors(board, player)

    for neighbor in neighbors:
        if node.is_ancestor(neighbor):
            continue
        else:
            neighbor_node = Node(neighbor, node, maxing_player, depth)
            node.children.append(neighbor_node)
            value = minimax(neighbor_node, not maxing_player, depth + 1) 
            neighbor_node.value = value

        if compare(value, best):
            best = value
            bestNeighbor = neighbor


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
node = Node(board, None, True, 0)
val = minimax(node,  True)

with open("file.txt", "w+") as f:
    def print_node(node, depth):
        f.write('\t' * depth + str(node) + "\n") 
        for child in node.children:
            print_node(child, depth + 1)
    print_node(node, 0)


visited = set()
parents = {}

board = make_board()
val = minimax(Node(board, None),  False)
