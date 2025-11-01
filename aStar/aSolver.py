def load_game(path):
    game_board = []
    with open(path) as file:
        for line in file:
            if line.strip():
                orientation, lenght, row, col = line.strip().split(", ")
                game_board.append((orientation, lenght, row, col))
    return tuple(game_board)

def goal_reached(game_board):
    orientation, length, row, col = game_board[0]
    return int(col) + int(length) == 6

def heuristic(state):
    # Heuristic: distance of red car to exit + number of blocking cars
    red_car = state[0]
    orientation, length, row, col = red_car
    col = int(col)
    length = int(length)
    distance_to_exit = 6 - (col + length)
    blocking_cars = 0
    # Positions occupied by cars
    occupied = set()
    for car in state:
        o, l, r, c = car
        l = int(l)
        r = int(r)
        c = int(c)
        if o == 'h':
            for i in range(c, c + l):
                occupied.add((r, i))
        else:
            for i in range(r, r + l):
                occupied.add((i, c))
    # Count blocking cars in path of red car to exit
    for pos_col in range(col + length, 6):
        if (int(row), pos_col) in occupied:
            blocking_cars += 1
    return distance_to_exit + blocking_cars

def get_successors(state):
    successors = []
    occupied = set()
    # Build occupied set for quick lookup
    for car in state:
        o, l, r, c = car
        l = int(l)
        r = int(r)
        c = int(c)
        if o == 'h':
            for i in range(c, c + l):
                occupied.add((r, i))
        else:
            for i in range(r, r + l):
                occupied.add((i, c))
    # For each car, try to move forward and backward along orientation
    for idx, car in enumerate(state):
        o, l, r, c = car
        l = int(l)
        r = int(r)
        c = int(c)
        if o == 'h':
            # Move left
            new_c = c - 1
            if new_c >= 0 and (r, new_c) not in occupied:
                new_state = list(state)
                new_state[idx] = (o, str(l), str(r), str(new_c))
                successors.append(tuple(new_state))
            # Move right
            new_c = c + l
            if new_c < 6 and (r, new_c) not in occupied:
                new_state = list(state)
                new_state[idx] = (o, str(l), str(r), str(c + 1))
                successors.append(tuple(new_state))
        else:
            # Vertical car
            # Move up
            new_r = r - 1
            if new_r >= 0 and (new_r, c) not in occupied:
                new_state = list(state)
                new_state[idx] = (o, str(l), str(new_r), str(c))
                successors.append(tuple(new_state))
            # Move down
            new_r = r + l
            if new_r < 6 and (new_r, c) not in occupied:
                new_state = list(state)
                new_state[idx] = (o, str(l), str(r + 1), str(c))
                successors.append(tuple(new_state))
    return successors

import heapq

def performAStar(game_board):
    start = game_board
    open_set = [(heuristic(start), 0, start, [])]  # (f, g, state, path)
    visited = set()
    while open_set:
        f, g, state, path = heapq.heappop(open_set)
        if state in visited:
            continue
        visited.add(state)
        if goal_reached(state):
            return path + [state]
        for successor in get_successors(state):
            if successor not in visited:
                new_g = g + 1
                new_f = new_g + heuristic(successor)
                heapq.heappush(open_set, (new_f, new_g, successor, path + [state]))
    return None

if __name__ == "__main__":
    game = load_game("../games/game0.txt")
    solution_path = performAStar(game)
    if solution_path:
        print(f"Lösung gefunden in {len(solution_path)-1} Zügen.")
    else:
        print("Keine Lösung gefunden.")
