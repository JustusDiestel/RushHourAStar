import heapq
import time

def load_game(path):
    game_board = []
    with open(path) as file:
        for line in file:
            if line.strip():
                o, l, r, c = line.strip().split(", ")
                game_board.append((o, l, r, c))
    return tuple(game_board)


# Ziel
def goal_reached(state):
    o, l, r, c = state[0]
    return int(c) + int(l) == 6


def build_occupied_map(state):
    occupied = set()
    for o, l, r, c in state:
        l = int(l)
        r = int(r)
        c = int(c)
        if o == "h":
            for i in range(c, c + l):
                occupied.add((r, i))
        else:
            for i in range(r, r + l):
                occupied.add((i, c))
    return occupied


# Car at position
def find_car_at_pos(state, row, col):
    row = int(row)
    col = int(col)
    for i, (o, l, r, c) in enumerate(state):
        l = int(l)
        r = int(r)
        c = int(c)
        if o == "h" and row == r and c <= col < c + l:
            return i
        if o == "v" and col == c and r <= row < r + l:
            return i
    return None


# Blocking cars in direction until free field
def blocking_cars_in_direction(state, r, c, step_r, step_c):
    occupied = build_occupied_map(state)
    cost = 0
    while 0 <= r < 6 and 0 <= c < 6:
        if (r, c) in occupied:
            cost += 1
            r += step_r
            c += step_c
        else:
            break
    return cost


# Exit-Strategy for one blocking car
def exit_strategie(state, idx):
    o, l, r, c = state[idx]
    l = int(l)
    r = int(r)
    c = int(c)

    strategies = []

    if o == "v":
        strategies.append(blocking_cars_in_direction(state, r - 1, c, -1, 0))
        strategies.append(blocking_cars_in_direction(state, r + l, c, 1, 0))
    else:
        strategies.append(blocking_cars_in_direction(state, r, c - 1, 0, -1))
        strategies.append(blocking_cars_in_direction(state, r, c + l, 0, 1))

    return min(strategies)


# Heuristik 1: zero
def zero_heuristic(state):
    return 0


# Heuristik 2: distance + blocking count
def distance_heuristic(state):
    red = state[0]
    o, l, r, c = red
    l = int(l)
    r = int(r)
    c = int(c)

    distance_to_exit = 6 - (c + l)

    occupied = build_occupied_map(state)
    blocking = 0

    for col in range(c + l, 6):
        if (r, col) in occupied:
            blocking += 1

    return distance_to_exit + blocking


# Heuristik 3: advanced heuristic
def advanced_heuristic(state):
    red = state[0]
    o, l, r, c = red
    l = int(l)
    r = int(r)
    c = int(c)

    occupied = build_occupied_map(state)
    hsum = 0

    for col in range(c + l, 6):
        if (r, col) in occupied:
            bid = find_car_at_pos(state, r, col)
            hsum += exit_strategie(state, bid)

    return hsum + 1


# Successors
def get_successors(state):
    successors = []
    occupied = build_occupied_map(state)

    for idx, (o, l, r, c) in enumerate(state):
        l = int(l)
        r = int(r)
        c = int(c)

        if o == "h":
            # links
            cc = c - 1
            while cc >= 0 and (r, cc) not in occupied:
                new = list(state)
                new[idx] = (o, str(l), str(r), str(cc))
                successors.append(tuple(new))
                cc -= 1

            # rechts
            cc = c + 1
            while cc + l - 1 < 6 and (r, cc + l - 1) not in occupied:
                new = list(state)
                new[idx] = (o, str(l), str(r), str(cc))
                successors.append(tuple(new))
                cc += 1

        else:
            # oben
            rr = r - 1
            while rr >= 0 and (rr, c) not in occupied:
                new = list(state)
                new[idx] = (o, str(l), str(rr), str(c))
                successors.append(tuple(new))
                rr -= 1

            # unten
            rr = r + 1
            while rr + l - 1 < 6 and (rr + l - 1, c) not in occupied:
                new = list(state)
                new[idx] = (o, str(l), str(rr), str(c))
                successors.append(tuple(new))
                rr += 1

    return successors


# A*
def perform_a_star(start_state, HeuristicParam):
    HEURISTIC = HeuristicParam
    open_set = [(HEURISTIC(start_state), 0, start_state, [])]
    visited = set()
    expanded_states = 0
    while open_set:
        f, g, state, path = heapq.heappop(open_set)

        if state in visited:
            continue
        visited.add(state)
        expanded_states += 1

        if goal_reached(state):
            return path + [state], expanded_states

        for succ in get_successors(state):
            if succ not in visited:
                new_g = g + 1
                new_f = new_g + HEURISTIC(succ)
                heapq.heappush(open_set, (new_f, new_g, succ, path + [state]))

    return None


if __name__ == "__main__":

    start = load_game("../games/game1.txt")


    HEURISTIC = advanced_heuristic
    start_time = time.perf_counter()
    sol, nr_expanded = perform_a_star(start, HEURISTIC)
    end_time = time.perf_counter()
    print("Heuristik:", HEURISTIC.__name__)
    if sol:
        print("Lösung in", len(sol) - 1, "Zügen.")
        print("Zeit:", end_time - start_time, "Sekunden")
        print("Expanded States:", nr_expanded)
    else:
        print("Keine Lösung gefunden.")

    HEURISTIC = zero_heuristic
    start_time = time.perf_counter()
    sol, nr_expanded = perform_a_star(start, HEURISTIC)
    end_time = time.perf_counter()
    print("Heuristik:", HEURISTIC.__name__)
    if sol:
        print("Lösung in", len(sol) - 1, "Zügen.")
        print("Zeit:", end_time - start_time, "Sekunden")
        print("Expanded States:", nr_expanded)
    else:
        print("Keine Lösung gefunden.")

    HEURISTIC = distance_heuristic
    start_time = time.perf_counter()
    sol, nr_expanded = perform_a_star(start, HEURISTIC)
    end_time = time.perf_counter()
    print("Heuristik:", HEURISTIC.__name__)
    if sol:
        print("Lösung in", len(sol) - 1, "Zügen.")
        print("Zeit:", end_time - start_time, "Sekunden")
        print("Expanded States:", nr_expanded)
    else:
        print("Keine Lösung gefunden.")