from contextlib import nullcontext


def load_game(path): # hier laden wir das spielfeld rein
    game_board = []
    with open(path) as file:
        for line in file:
            if line.strip():
                orientation, lenght, row, col = line.strip().split(", ")
                game_board.append((orientation, lenght, row, col))
    return tuple(game_board)

def goal_reached(game_board): # wenn rotes Auto rechts berührt - fertig
    orientation, length, row, col = game_board[0]
    return int(col) + int(length) == 6


def zero_heuristic(state):
    return 0


def find_car_at_pos(state, row, col):
    row = int(row)
    col = int(col)

    for i, (o, l, r, c) in enumerate(state):
        l = int(l)
        r = int(r)
        c = int(c)

        if o == "h":
            if row == r:
                if c <= col < c + l:
                    return i
        else:
            if row <= r + l:
                if col == c:
                    return i
    return None


def exit_strategie(state, blocking_id):
    o, l, r, c = state[blocking_id]
    l = int(l);
    r = int(r);
    c = int(c)
    occupied = build_occupied_map(state)

    strategies = []

    if o == "v":
        moves_up = blocking_cars_in_direction(occupied, r - 1, c, step=-1)
        if moves_up is not None:
            strategies.append(moves_up)


        moves_down = blocking_cars_in_direction(occupied, r + l, c, step=1)
        if moves_down is not None:
            strategies.append(moves_down)
    else:
        moves_left = blocking_cars_in_direction(occupied, r , c - 1, step=-1)
        if moves_left is not None:
            strategies.append(moves_left)

        moves_right = blocking_cars_in_direction(occupied, r, c + 1, step=1)
        if moves_right is not None:
            strategies.append(moves_right)

    return min(strategies) if strategies else 99

def blocking_cars_in_direction(occupied, start_r, c, step):
    cost = 0
    r = start_r

    while 0 <= r < 6:
        if (r, c) in occupied:
            cost += 1
        r += step
    return cost


def advanced_heuristic(state):
    red_car = state[0]
    orientation, length, row, col = red_car
    col = int(col)
    length = int(length)
    distance_to_exit = 6 - (col + length)
    # Positions occupied by cars
    occupied = build_occupied_map(state)
    heuristic_sum = 0
    for pos_col in range(col + length, 6):
        cost_to_move = 0
        if (int(row), pos_col) in occupied:
            blocking_id = find_car_at_pos(state, row, pos_col)
            cost_to_move = exit_strategie(state, blocking_id)
        heuristic_sum += cost_to_move
    return heuristic_sum


def distance_heuristic(state):
    # blockierende autos + abstand zum ziel ist unsere heuristik
    red_car = state[0]
    orientation, length, row, col = red_car
    col = int(col)
    length = int(length)
    distance_to_exit = 6 - (col + length)
    blocking_cars = 0
    # Positions occupied by cars
    occupied = build_occupied_map(state)

    for pos_col in range(col + length, 6):
        if (int(row), pos_col) in occupied:
            blocking_cars += 1
    return distance_to_exit + blocking_cars

def get_successors(state):
    successors = []
    occupied = build_occupied_map(state)

    for idx, car in enumerate(state):
        o, l, r, c = car
        l = int(l)
        r = int(r)
        c = int(c)
        if o == 'h':
            create_new_successor_h(successors,occupied, idx, o, l, r, c, state)

        else:
            create_new_successor_r(successors,occupied, idx, o, l, r, c, state)
            new_r = r - 1
            if new_r >= 0 and (new_r, c) not in occupied:
                new_state = list(state)
                new_state[idx] = (o, str(l), str(new_r), str(c))
                successors.append(tuple(new_state))
            new_r = r + l
            if new_r < 6 and (new_r, c) not in occupied:
                new_state = list(state)
                new_state[idx] = (o, str(l), str(r + 1), str(c))
                successors.append(tuple(new_state))
    return successors

import heapq

def create_new_successor_r(successors, occupied, idx, o, l, r, c, state):
    for target_r in range(r - 1, -1, -1):
        if (target_r, c) in occupied:
            break
        new_state = list(state)
        new_state[idx] = (o, str(l), str(target_r), str(c))
        successors.append(tuple(new_state))

    for target_r in range(r + 1, 6 - l + 1):
        if (target_r + l - 1, c) in occupied:
            break
        new_state = list(state)
        new_state[idx] = (o, str(l), str(target_r), str(c))
        successors.append(tuple(new_state))

def create_new_successor_h(successors, occupied, idx, o, l, r, c, state):
    for target_c in range(c - 1, -1, -1):
        if (r, target_c) in occupied:
            break
        new_state = list(state)
        new_state[idx] = (o, str(l), str(r), str(target_c))
        successors.append(tuple(new_state))

    for target_c in range(c + 1, 6 - l + 1):
        if (r, target_c + l - 1) in occupied:
            break
        new_state = list(state)
        new_state[idx] = (o, str(l), str(r), str(target_c))
        successors.append(tuple(new_state))


def build_occupied_map(state):
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
    return occupied


def perform_a_star(game_board):
    start = game_board
    # open_set = [(distance_heuristic(start), 0, start, [])]  # (f, g, state, path)
    # open_set = [(zero_heuristic(start), 0, start, [])]  # (f, g, state, path)

    open_set = [(advanced_heuristic(start), 0, start, [])]  # (f, g, state, path)
    visited = set()
    print(start)
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
                # new_f = new_g + distance_heuristic(successor)
                # new_f = new_g + zero_heuristic(successor)
                new_f = new_g + advanced_heuristic(successor)

                heapq.heappush(open_set, (new_f, new_g, successor, path + [state]))
    return None

if __name__ == "__main__":
    game = load_game("../games/hardest.txt")
    solution_path = perform_a_star(game)
    if solution_path:
        print(f"Lösung gefunden in {len(solution_path)-1} Zügen.")
    else:
        print("Keine Lösung gefunden.")
