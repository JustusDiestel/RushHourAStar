import random

from aStar.aSolver import perform_a_star, goal_reached

class GameGenerator:
    def __init__(self, count=3):
        self.count = count
        self.size = 6
        self.generated_games = []

    def random_car(self, existing_cars):
        orientation = random.choice(['h', 'v'])
        length = random.choice([1, 2, 3])
        attempts = 0
        while attempts < 100:
            if orientation == 'h':
                row = random.randint(0, self.size - 1)
                col = random.randint(0, self.size - length)
            else:
                row = random.randint(0, self.size - length)
                col = random.randint(0, self.size - 1)
            new_car_coords = self.get_car_coordinates(orientation, length, row, col)
            if not self.check_collision(new_car_coords, existing_cars):
                return (orientation, str(length), str(row), str(col))
            attempts += 1
        # Falls kein Platz gefunden wird, gib None zurück
        return None

    def get_car_coordinates(self, orientation, length, row, col):
        coords = []
        for i in range(length):
            if orientation == 'h':
                coords.append((row, col + i))
            else:
                coords.append((row + i, col))
        return coords

    def check_collision(self, new_car_coords, existing_cars):
        for car in existing_cars:
            o, l, r, c = car
            car_coords = self.get_car_coordinates(o, int(l), int(r), int(c))
            if set(new_car_coords) & set(car_coords):
                return True
        return False

    def create_random_game(self):
        # Rotes Auto immer an erster Stelle (horizontal, Länge 2, in Zeile 2, Spalte 0-1)
        red_car = ('h', '2', '2', '0')
        game = [red_car]

        for _ in range(random.randint(4, 15)):  # zufällige Anzahl anderer Autos
            car = self.random_car(game)
            if car is not None:
                game.append(car)
        return tuple(game)

    def generate_and_test(self):
        valid_games = []
        while len(valid_games) < self.count:
            game = self.create_random_game()
            try:
                result = perform_a_star(game)
                if result and goal_reached(result[-1]):
                    valid_games.append(game)
                    print(f"✔ Lösbares Spiel #{len(valid_games)} gefunden")
            except Exception:
                pass  # falls A* fehlschlägt oder inkonsistent
        self.generated_games = valid_games

    def save_games(self, folder="games"):
        for i, game in enumerate(self.generated_games):
            with open(f"../{folder}/auto_game_{i}.txt", "w") as f:
                for o, l, r, c in game:
                    f.write(f"{o}, {l}, {r}, {c}\n")
        print(f"{len(self.generated_games)} lösbare Spiele gespeichert.")

if __name__ == "__main__":
    gg = GameGenerator()
    gg.generate_and_test()
    gg.save_games()