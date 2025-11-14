import heapq



# Spielfeld laden
def load_game(path):
    game_board = []
    with open(path) as file:
        for line in file:
            if line.strip():
                o, l, r, c = line.strip().split(", ")
                game_board.append((o, l, r, c))
    return tuple(game_board)


# Ziel erreicht?
def goal_reached(state):
    o, l, r, c = state[0]
    return int(c) + int(l) == 6


# Occupied-Map machen
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


# Auto an Position finden
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


# Blocker in Richtung zählen (bis erstes freies Feld)
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


# Exit-Strategie für Auto bestimmen
def exit_strategie(state, idx):
    o, l, r, c = state[idx]
    l = int(l)
    r = int(r)
    c = int(c)

    strategies = []

    if o == "v":
        # nach oben
        strategies.append(blocking_cars_in_direction(state, r - 1, c, -1, 0))
        # nach unten
        strategies.append(blocking_cars_in_direction(state, r + l, c, 1, 0))
    else:
        # nach links
        strategies.append(blocking_cars_in_direction(state, r, c - 1, 0, -1))
        # nach rechts
        strategies.append(blocking_cars_in_direction(state, r, c + l, 0, 1))

    return min(strategies)


# Advanced-Heuristic
def advanced_heuristic(state):
    red = state[0]
    o, l, r, c = red
    l = int(l)
    r = int(r)
    c = int(c)

    occupied = build_occupied_map(state)
    heuristic_sum = 0

    # Felder rechts vom roten Auto
    for pos_c in range(c + l, 6):
        if (r, pos_c) in occupied:
            blocking_idx = find_car_at_pos(state, r, pos_c)
            heuristic_sum += exit_strategie(state, blocking_idx)

    # +1 final move of red car
    return heuristic_sum + 1


# Successor-Generierung
def get_successors(state):
    successors = []
    occupied = build_occupied_map(state)

    for idx, (o, l, r, c) in enumerate(state):
        l = int(l)
        r = int(r)
        c = int(c)

        # horizontal
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
            # vertikal
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
def perform_a_star(start_state):
    open_set = [(advanced_heuristic(start_state), 0, start_state, [])]
    visited = set()

    while open_set:
        f, g, state, path = heapq.heappop(open_set)

        if state in visited:
            continue
        visited.add(state)

        if goal_reached(state):
            return path + [state]

        for succ in get_successors(state):
            if succ not in visited:
                new_g = g + 1
                new_f = new_g + advanced_heuristic(succ)
                heapq.heappush(open_set, (new_f, new_g, succ, path + [state]))

    return None



if __name__ == "__main__":
    game = load_game("../games/hardest.txt")
    solution = perform_a_star(game)

    if solution:
        print("Lösung in", len(solution) - 1, "Zügen.")
    else:
        print("Keine Lösung.")