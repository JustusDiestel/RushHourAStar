from aStar.aSolver import load_game, perform_a_star, advanced_heuristic, distance_heuristic, zero_heuristic

if __name__ == "__main__":
    start = load_game("../games/hardest.txt")
    HEURISTIC = advanced_heuristic  # oder distance_heuristic / zero_heuristic
    sol = perform_a_star(start, HEURISTIC)

    if sol:
        print("Lösung in", len(sol) - 1, "Zügen.")
    else:
        print("Keine Lösung gefunden.")