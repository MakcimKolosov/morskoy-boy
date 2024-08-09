
import random

class BoardOutException(Exception):
    pass

class AlreadyShotException(Exception):
    pass

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"

class Ship:
    def __init__(self, bow: Dot, length: int, orientation: str):
        self.bow = bow
        self.length = length
        self.orientation = orientation
        self.health = length

    @property
    def dots(self):
        return [Dot(self.bow.x + i, self.bow.y) if self.orientation == 'horizontal'
                else Dot(self.bow.x, self.bow.y + i) for i in range(self.length)]

class Board:
    def __init__(self, hid=False):
        self.hid = hid
        self.ships = []
        self.shots = []
        self.field = [['O'] * 6 for _ in range(6)]

    def add_ship(self, ship: Ship):
        for dot in ship.dots:
            if self.out(dot) or any(dot in s.dots for s in self.ships):
                raise ValueError("Невозможно разметить корабль")
        for dot in ship.dots:
            self.field[dot.y - 1][dot.x - 1] = '■'
        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship: Ship):
        for dot in ship.dots:
            for x in range(dot.x - 1, dot.x + 2):
                for y in range(dot.y - 1, dot.y + 2):
                    if not (self.out(Dot(x, y)) or Dot(x, y) in ship.dots):
                        self.field[y - 1][x - 1] = '•'

    def out(self, dot: Dot):
        return dot.x < 1 or dot.x > 6 or dot.y < 1 or dot.y > 6

    def shot(self, dot: Dot):
        if self.out(dot):
            raise BoardOutException("Выстрел за пределы поля!")
        if dot in self.shots:
            raise AlreadyShotException("Уже был выстрел в эту зону!")

        self.shots.append(dot)
        if any(dot in ship.dots for ship in self.ships):
            self.field[dot.y - 1][dot.x - 1] = 'X'
            for ship in self.ships:
                if dot in ship.dots:
                    ship.health -= 1
                    if ship.health == 0:
                        self.field[dot.y - 1][dot.x - 1] = 'X'
            return True
        else:
            self.field[dot.y - 1][dot.x - 1] = 'T'
            return False

    def __str__(self):
        result = "  | 1 | 2 | 3 | 4 | 5 | 6 |\n"
        for i in range(6):
            result += str(i + 1) + ' | '
            for j in range(6):
                if self.hid and self.field[i][j] == '■':
                    result += 'O | '
                else:
                    result += self.field[i][j] + ' | '
            result += '\n'
        return result

class Player:
    def __init__(self, board: Board, enemy_board: Board):
        self.board = board
        self.enemy_board = enemy_board

    def ask(self):
        raise NotImplementedError

    def move(self):
        while True:
            try:
                shot = self.ask()
                if self.enemy_board.shot(shot):
                    return True
                else:
                    return False
            except (BoardOutException, AlreadyShotException) as e:
                print(e)

class User(Player):
    def ask(self):
        while True:
            coords = input("Введите координаты (x y): ").split()
            if len(coords) != 2:
                print("Введите две координаты!")
                continue
            x, y = map(int, coords)
            return Dot(x, y)

class AI(Player):
    def ask(self):
        while True:
            x = random.randint(1, 6)
            y = random.randint(1, 6)
            dot = Dot(x, y)
            return dot if dot not in self.enemy_board.shots else None

class Game:
    def __init__(self):
        self.user_board = Board()
        self.ai_board = Board(hid=True)

        self.user = User(self.user_board, self.ai_board)
        self.ai = AI(self.ai_board, self.user_board)

        self.random_board(self.ai_board)

    def random_board(self, board):
        ships = [Ship(Dot(1, 1), 3, 'horizontal')]
        ships += [Ship(Dot(1, 1), 2, 'horizontal') for _ in range(2)]
        ships += [Ship(Dot(1, 1), 1, 'horizontal') for _ in range(4)]

        for ship in ships:
            placed = False
            for _ in range(1000):
                try:
                    orientation = random.choice(['horizontal', 'vertical'])
                    x = random.randint(1, 6)
                    y = random.randint(1, 6)
                    ship.bow = Dot(x, y)
                    ship.orientation = orientation
                    board.add_ship(ship)
                    placed = True
                    break
                except ValueError:
                    continue
            if not placed:
                print("Could not place all ships")
                return

    def loop(self):
        while True:
            print("Доска пользователя:")
            print(self.user_board)
            print("Доска ИИ:")
            print(self.ai_board)

            if not self.user.move():
                print("Ход противника!")
                self.ai.move()

    def start(self):
        print("Добро пожаловать в игру 'Морской бой'!")
        self.loop()

if __name__ == "__main__":
    game = Game()
    game.start()