from random import randint
import time
import sys

def countdown(t):
    while t > 0:
        sys.stdout.write('\rДо старта : {}'.format(t))
        t -= 1
        sys.stdout.flush()
        time.sleep(1)
        if t == 0:
            print("\rСтартуем!!!")
            time.sleep(1)

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return " Вы пытаетесь выстрелить за поле!"
    time.sleep(2)


class BoardUsedException(BoardException):
    def __str__(self):
        return " Вы сюда уже стреляли! "

    time.sleep(2)


class BoardWrongShipException(BoardException):
    pass


class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.count = 0

        self.field = [["| 0"] * size for _ in range(size)]

        self.busy = []
        self.ships = []

    def add_ship(self, ship):

        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "| ■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "| ⚓"
                    self.busy.append(cur)

    def __str__(self):
        res = ""
        res += "    | а | б | в | г | д | е |"
        for i, row in enumerate(self.field):
            res +=f"\n{i + 1}   " + " ".join(row) + " |"

        if self.hid:
            res = res.replace("| ■", "| O")
        return res

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "| ✭"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print(" Корабль потоплен.Так держать!")
                    time.sleep(3)
                    return False
                else:
                    print("Корабль ранен!")
                    time.sleep(3)
                    return True

        self.field[d.x][d.y] = "| ⁕"
        print("Промах!")
        time.sleep(2)
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)
class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d

class User(Player):
    def ask(self):
        while True:
            cords_y = str(input("Ваш ход: Введите ,БУКВУ(на кириллице) от а до е: ")).lower()
            if len(cords_y) != 1:
                print(" Введите 1 букву! ")
                continue
            list = ["а", "б", "в", "г", "д", "е"]
            if cords_y in list:
                for a, val in enumerate(list):
                    if cords_y == val:
                        y = a
            else:
                print("Ошибка ввода буквы")
                continue
            cords_x = input("Ваш ход: Введите цифру! ")
            if len(cords_x) != 1:
                print(" Введите только 1 координату! ")
                continue
            x = cords_x
            if not(x.isdigit()):
                print(" Введите число! ")
                continue
            x, y = int(x), int(y)
            return Dot(x - 1, y)

class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        player = str(input(" Введите имя игрока: ").title())
        print(f" Приветствуем вас {player} в игре МОРСКОЙ БОЙ!!!")
        print("____________________________________________")
        print('   Условные обозначения:')
        print('   ■ - корабль,')
        print('   ⁕ - промах(там точно нет корабля),')
        print('   ⚓ -  место где нельзя ставить корабль ')
        print('   0 - "неизвестное поле"')
        print('   ✰ - попадание по кораблю ')

        countdown(10)

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print(f"Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Пользователь выиграл!")
                time.sleep(5)
                break

            if self.us.board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                time.sleep(5)
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()