import itertools, math
from operator import add
BLANK = 0
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
    def __init__(self, board, maxing = True, depth = 0):
        self.board = board
        self.parents = {}
        self.value = None
        self.children = []
        self.maxing = maxing
        self.depth = depth
        self.favorite_child = None

    def make_child_with_board(self, board):
        child = Node(board, maxing = not self.maxing, depth= self.depth + 1)
        child.parents= self.parents.copy()
        child.parents[str(self)] = self
        return child
    
    def __eq__(self, other):
        return self.board == other.board and self.maxing == other.maxing

    def hash(self):
        return hash((self.board, self.maxing))

    def __str__(self):
        return f"Board:{self.board}, Max:{self.maxing}"
    
    def __repr__(self):
        return self.__str__()

    def is_ancestor(self,board, maxing):
        anc = str(Node(board, maxing)) in self.parents.keys()
        return anc


def compute_diff_possible_wins(board):
    possible_win_for_1 = 0
    possible_win_for_2 = 0
    for line in WIN_LINES:
        if all([board[x][y] != PLAYER_2 for x,y in line]):
            possible_win_for_1 += 1
        
        if all([board[x][y] != PLAYER_1 for x,y in line]):
            possible_win_for_2 += 1
    return possible_win_for_1 - possible_win_for_2

def rate_board(board):
    res = check_wins(board)
    if res == PLAYER_1:
        return 8
    if res == PLAYER_2:
        return -8
    return 0


def minimax(node):
    board = node.board
    player = 1 if node.maxing else 2
    neighbors = make_neighbors(board, player)

    if check_wins(board) is not None:
        return rate_board(board)

    if node.maxing:
        best = -1000000
        value = -best
        for neighbor in neighbors:
            if node.is_ancestor(neighbor, not node.maxing):
                continue
                #possibly continue
            else:
                neighbor_node = node.make_child_with_board(neighbor)
                value = minimax(neighbor_node)
                if value >= best:
                    best = value
                    node.favorite_child = neighbor_node

        return best
            
    else:
        best = 1000000
        value = -best
        for neighbor in neighbors:
            if node.is_ancestor(neighbor, not node.maxing):
                continue
                #possibly continue
            else:
                neighbor_node = node.make_child_with_board(neighbor)
                value = minimax(neighbor_node)
                if value <= best:
                    best = value
                    node.favorite_child = neighbor_node
        return best
    




    


board = make_board()
node = Node(board)
minimax(node)




quit()
#board[0][2] = PLAYER_1
#board[1][1] = PLAYER_1
#board[2][2] = PLAYER_1
#
#
#board[2][0] = PLAYER_2
#board[2][1] = PLAYER_2
#board[0][0] = PLAYER_2

cboard = copy_board(make_board())
node = visited[board]
#val = minimax(board,  True, depth = 0)
#val = minimax(board,  True, depth = 0)
val = ab_minimax(board,  True, -100000000,100000000, depth = 16)


current_node = node
while current_node is not None:
    print_board(current_node.board)
    winners = [child for child in current_node.children if child.value == 8]
    current_node = winners[0]
    if len(current_node.children) == 0:
        break


#with open("file.txt", "w+") as f:
#    def print_node(node, depth):
#        f.write('\t' * depth + str(node) + "\n") 
#        for child in node.children:
 #           print_node(child, depth + 1)
#    print_node(node, 0)


parents = {}

board = make_board()
#al = minimax(Node(board, None),  False)
