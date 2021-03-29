import itertools, math, time
from operator import add
from typing import List, Tuple
BLANK = 0
PLAYER_1 = 1
PLAYER_2 = 2

MAX_DEPTH = 18

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
#Generate a blank boardd
def make_board() -> List[List[int]] :
    return [[BLANK,BLANK,BLANK],[BLANK,BLANK,BLANK],[BLANK,BLANK,BLANK]]

#duplicate a board and all its pieces
def copy_board(board: List[List[int]]):
    return [[board[j][i] for i in range(3)] for j in range(3)]

#pretty return a pretty board and print to console if console set to true
def print_board(board:List[List[int]] , indent: int = 0, console: bool = True) -> str:

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
    
    return joiner.join(out)

#check if a player occupies all of a single win line, returns a winning player ID
def check_wins(board: List[List[int]]) -> int:
    
    for line in WIN_LINES:
        vals = set()
        for x,y in line:
            vals.add(board[x][y])
        val = next(iter(vals))
        if len(vals) == 1 and val != BLANK:
            return val
    else:
        return None

#Calculate the difference in moves to win heuristic
def get_pieces(board: List[List[int]], player: int) -> List[Tuple[int,int]]:
    pieces = []
    for i,j in itertools.product(range(3), range(3)):
        if board[i][j] == player:
            pieces.append((i,j))
    return pieces

#get the location for all pieces on the board, return a list of possible next boards
def make_neighbors(board: List[List[int]], active_player: int) -> List[List[List[int]]]:
    if check_wins(board):
        return [board]
    neighbors = []
    occurances = get_pieces(board, active_player)
    if len(occurances) < 3: #TODO HERE
        for i,j in itertools.product(range(3), range(3)):
            if board[i][j] == BLANK:
                neighbor = copy_board(board)
                neighbor[i][j] = active_player
                neighbors.append(neighbor)
    else:
        deltas = {
            (0,0): [(1,0), (1, 1), (0, 1)], #Good
            (1,0): [(-1,0), (1, 0), (0,1)], #Good
            (2,0): [(-1,0), (-1, 1), (0,1)], #Good
            (0,1): [(0,-1), (1, 0), (0,1)], #Good
            (1,1):[(-1,1), (1,0), (1,1), (1, 0), (1,-1), (0,-1), (-1,-1), (-1, 0)],
            (2,1): [(0,-1), (-1, 0), (0,1)], #Good
            (0,2): [(1,-1), (1, 0), (0,-1)], 
            (1,2):[(-1,0), (1, 0), (0,-1)],
            (2,2): [(0,-1), (-1, 0),(-1,-1)], 
            }
        new_positions = set()
        for occurance in occurances:
            for delta in deltas[occurance]:
                new_pos = tuple(map(add, occurance, delta ))
                if 0 <= new_pos[0] < 3 and 0 <= new_pos[1] < 3 and board[new_pos[0]][new_pos[1]] == BLANK:
                    new_positions.add((occurance, new_pos))
        for start, end in iter(new_positions):
            new_board = copy_board(board)
            new_board[start[0]][start[1]] = BLANK
            new_board[end[0]][end[1]] = active_player
            neighbors.append(new_board)
        
    return neighbors

#pretty print a list of boards
def vertical_path_to_horizontal(iterator: List[str]) -> str:
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

# a node in the search space. Used to eliminate cycles
class Node:
    def __init__(self, board: List[List[int]], maxing:bool = True, depth: int = 0) -> 'Node':
        self.board = board
        self.parents = {}
        self.value = None
        self.children = []
        self.maxing = maxing
        self.depth = depth
        self.favorite_child = None

    # make a child for the current board with iterating depth, alternating maxing, 
    # and copied parents
    def make_child_with_board(self, board: List[List[int]]) -> 'Node':
        child = Node(board, maxing = not self.maxing, depth= self.depth + 1)
        child.parents= self.parents.copy()
        child.parents[str(self)] = self
        self.children.append(child)
        return child
    
    #two nodes are equal if they have the same board and same maxing player
    def __eq__(self, other: 'Node') -> bool:
        return self.board == other.board and self.maxing == other.maxing

    # pretty print a node
    def __str__(self) -> str:
        return f"Board:{self.board}, Max:{self.maxing}"
    
    #pretty printing in debugger
    def __repr__(self):
        return f"VAL: {self.value}, Board:{self.board}, Max:{self.maxing}"
    
    def get_favorite_path(self):
        path = []
        path.append(self)
        fav = self.favorite_child
        while fav is not None:
            path.append(fav)
            fav = fav.favorite_child
        #path.append(fav)
        return path


    # node is previous state if board and maxing pair have already happened
    def is_ancestor(self,board: List[List[int]], maxing: bool) -> bool:
        anc = str(Node(board, maxing)) in self.parents.keys()
        return anc

#Calculate the difference in moves to win heuristic
def compute_diff_possible_wins(board: List[List[int]]) -> int:
    possible_win_for_1 = 0
    possible_win_for_2 = 0
    for line in WIN_LINES:
        if all([board[x][y] != PLAYER_2 for x,y in line]):
            possible_win_for_1 += 1
        
        if all([board[x][y] != PLAYER_1 for x,y in line]):
            possible_win_for_2 += 1

    return possible_win_for_1 - possible_win_for_2

#rate board as win loss or draw
def rate_board(board: List[List[int]]) -> int:
    res = check_wins(board)
    if res == PLAYER_1:
        return 8
    if res == PLAYER_2:
        return -8
    return 0

nodes = []

#minimax algorithm
def minimax(current_node: Node) -> int:
    board = current_node.board
    player = 1 if current_node.maxing else 2
    neighbors = make_neighbors(board, player)

    if check_wins(board) is not None or current_node.depth == MAX_DEPTH :
        return rate_board(board)

    if current_node.maxing:
        best = -1000000
        value = -best
        for neighbor in neighbors:
            if current_node.is_ancestor(neighbor, not current_node.maxing):
                continue
                #possibly continue
            else:
                neighbor_node = current_node.make_child_with_board(neighbor)
                value = minimax(neighbor_node)
                if value >= best:
                    best = value
                    current_node.favorite_child = neighbor_node

        return best
            
    else:
        best = 1000000
        value = -best
        for neighbor in neighbors:
            if current_node.is_ancestor(neighbor, not current_node.maxing):
                continue
                #possibly continue
            else:
                neighbor_node = current_node.make_child_with_board(neighbor)
                value = minimax(neighbor_node)
                if value <= best:
                    best = value
                    current_node.favorite_child = neighbor_node
        return best
    

#minimax algorithm with alpha beta pruning
def alpha_beta_minimax(current_node: Node, max_is_first=True, alpha = -100000000, beta = 100000000) -> int:
    board = current_node.board
    if max_is_first:
        player = 1 if current_node.maxing else 2
    else:
        player = 2 if current_node.maxing else 1


    if check_wins(board) is not None or current_node.depth == MAX_DEPTH:
        value = rate_board(board)
        return value

    if current_node.maxing:
        best = -1000000
        nodevalue = best
        neighbors = make_neighbors(board, player)
        neighbors.sort(key= compute_diff_possible_wins, reverse=True)
        for neighbor in neighbors:
            if current_node.is_ancestor(neighbor, not current_node.maxing):
                continue
                #possibly continue
            else:
                neighbor_node = current_node.make_child_with_board(neighbor)
                ab = alpha_beta_minimax(neighbor_node, max_is_first=max_is_first, alpha = alpha, beta = beta, )
                nodevalue = max(nodevalue, ab)
                alpha = max(alpha, nodevalue)
                if ab >= best:
                    best = ab
                    current_node.favorite_child = neighbor_node
                    current_node.value = nodevalue
                if beta <= alpha:
                    break

        return best
            
    else:
        best = 1000000
        value = 1000000
        ab = best
        neighbors = make_neighbors(board, player)
        neighbors.sort(key= compute_diff_possible_wins, reverse=True)
        for neighbor in neighbors:
            if current_node.is_ancestor(neighbor, not current_node.maxing):
                continue
                #possibly continue
            else:
                neighbor_node = current_node.make_child_with_board(neighbor)
                ab = alpha_beta_minimax(neighbor_node,max_is_first=max_is_first, alpha = alpha, beta = beta, )
                value = min(value, ab)
                beta = min(beta, value)
                if ab <= best:
                    best = ab
                    current_node.favorite_child = neighbor_node
                    current_node.value = value
                if beta <= alpha:
                    break
        return best




    
def minimax_analysis(p1start):

    board = make_board()
    node = Node(board, maxing=p1start)
    minimax(node)
    return [n.board for n in node.get_favorite_path()]

def ab_analysis(p1start):

    board = make_board()
    node = Node(board)
    print(alpha_beta_minimax(node, max_is_first=p1start))
        
    return [n.board for n in node.get_favorite_path()]

def time_n_print_solve(label: str, func, args = []):
    tic = time.perf_counter()
    solution = vertical_path_to_horizontal(func(*args))
    toc = time.perf_counter()

    out = []
    out.append('-' * 180)
    out.append(f"{label} took {toc - tic:0.4f} seconds")
    out.append(solution)

    out.append('-' * 180)
    return toc - tic, '\n'.join(out)

def run_algos():

    algs = {"ABMinimax": ab_analysis}

    times = {label: [] for label in algs.keys()}
    results = {label: [] for label in algs.keys()}

    for label, algo in algs.items():
        for value in [False]:
            print(label + " Player " + ("1" if value else "2") + " First")
            result = time_n_print_solve(label + "Player " + ("1" if value else "2") + " First", algo, [value])
            times[label].append(result[0])
            results[label].append(result[1])

    for label in algs.keys():
        with open(f"{label}_results.txt", 'w+') as out_file:
            for result in results[label]:
                out_file.write(str(result))
                out_file.write("\n\n\n")

    with open("times.txt", 'w+') as out_file:
        for label, time_vals in times.items():
            avg_time = sum(time_vals) / len(time_vals)
            print(f"{label} -> {str(avg_time)}")
            out_file.write(f"{label} -> {str(avg_time)}\n")

run_algos()