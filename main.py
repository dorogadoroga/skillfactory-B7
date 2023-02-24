# к коду вебинара в класс Game добавлен метод print_board и  немного исправлен метод greet,
# в классе AI дополнен метод ask


# внутренняя часть
from random import randint


# исключения

class BoardException(Exception):
    pass


class BoardOutException(BoardException):

    def __str__(self):
        return 'Координаты выходят за границы поля'


class BoardUsedException(BoardException):

    def __str__(self):
        return 'В эту клетку уже стреляли'


class BoardWrongShipException(BoardException):
    pass


# логика

class Dot:
    # x, y - координаты типа int
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'Dot({self.x}, {self.y})'


class Ship:
    # front_dot - экземпляр класса Dot, length - длина корабля типа int, orientation - значения 0 или 1
    def __init__(self, front_dot, length, orientation):
        self.length = length
        self.front_dot = front_dot
        self.orientation = orientation
        self.lives = length
        self.ship_dots = self.dots()

    def dots(self):
        ship_dots = []
        for i in range(self.length):
            cur_x = self.front_dot.x
            cur_y = self.front_dot.y
            if self.orientation == 0:
                cur_x += i
            elif self.orientation == 1:
                cur_y += i
            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots

    # shot - экземпляр класса Dot
    def shooten(self, shot):
        return shot in self.ship_dots


class Board:
    # hid - параметр видимости кораблей (True/False), size - размер поля типа int
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid
        self.count = 0
        self.field = [['0'] * size for _ in range(size)]
        self.busy = []
        self.ships = []
        self.list_wound = []

    def __str__(self):
        res = ' ' * 4
        res += ' | '.join([str(i) for i in range(1, self.size + 1)])
        res += ' |'
        for i, row in enumerate(self.field):
            res += f'\n{i + 1} | ' + ' | '.join(row) + ' |'

        if self.hid:
            res = res.replace('■', '0')
        return res

    # d - экземпляр класса Dot
    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    # ship - экземпляр класса Ship, verb - параметр видимости контура (True/False)
    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.ship_dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = '.'
                    self.busy.append(cur)

    # ship - экземпляр класса Ship
    def add_ship(self, ship):
        for d in ship.ship_dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.ship_dots:
            self.field[d.x][d.y] = '■'
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    # d - экземпляр класса Dot
    def shot(self, d):
        if self.out(d):
            raise BoardOutException()
        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if ship.shooten(d):
                ship.lives -= 1
                self.field[d.x][d.y] = 'X'
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print('Корабль уничтожен!')
                    for d in ship.ship_dots:
                        if d in self.list_wound:
                            self.list_wound.remove(d)
                    return False
                else:
                    print('Корабль ранен!')
                    self.list_wound.append(d)
                    return True

        self.field[d.x][d.y] = '.'
        print('Мимо!')
        return False

    def begin(self):
        self.busy = []


# Внешняя часть

class Player:
    # board, enemy - экземпляры класса Board
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
        list_target = [(-1, 0), (0, -1), (0, 1), (1, 0)]
        if self.enemy.list_wound:
            if len(self.enemy.list_wound) == 2:
                if self.enemy.list_wound[0].x == self.enemy.list_wound[1].x:
                    list_target = [(0, -1), (0, 1)]
                else:
                    list_target = [(-1, 0), (1, 0)]
            for d_ in self.enemy.list_wound:
                for dx, dy in list_target:
                    if not self.enemy.out(Dot(d_.x + dx, d_.y + dy)) \
                            and self.enemy.field[d_.x + dx][d_.y + dy] != '.' \
                            and self.enemy.field[d_.x + dx][d_.y + dy] != 'X':
                        d = Dot(d_.x + dx, d_.y + dy)
                        print(f'Ход компьютера: {d.x + 1} {d.y + 1}')
                        return d

        d = Dot(randint(0, self.enemy.size - 1), randint(0, self.enemy.size - 1))
        print(f'Ход компьютера: {d.x + 1} {d.y + 1}')
        return d


class User(Player):

    def ask(self):
        while True:
            cords = input('Ваш ход: ').split()
            if len(cords) != 2:
                print('Введите 2 координаты')
                continue
            x, y = cords
            if not x.isdigit() or not y.isdigit():
                print('Введите 2 числа')
                continue
            x, y = int(x), int(y)
            return Dot(x - 1, y - 1)


class Game:

    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True
        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size - 1), randint(0, self.size - 1)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def print_board(self):
        pl_print = self.us.board.__str__().split('\n')
        co_print = self.us.enemy.__str__().split('\n')
        for i in range(len(pl_print)):
            print(pl_print[i], co_print[i], sep=' ' * self.size)

    def greet(self):
        print('{:^60}'.format("-------------------"))
        print('{:^60}'.format("  Приветсвуем вас  "))
        print('{:^60}'.format("      в игре       "))
        print('{:^60}'.format("    морской бой    "))
        print('{:^60}'.format("-------------------"))
        print('{:^60}'.format(" формат ввода: x y "))
        print('{:^60}'.format(" x - номер строки  "))
        print('{:^60}'.format(" y - номер столбца "))

    def loop(self):
        num = 0
        while True:
            print('-' * self.size * 10)
            print('Доска пользователя', 'Доска компьютера', sep=' ' * self.size * 3)
            self.print_board()
            print('-' * self.size * 10)
            if num % 2 == 0:
                print('Ход пользователя')
                repeat = self.us.move()
            else:
                print('Ход компьютера')
                repeat = self.ai.move()
            if repeat:
                num -= 1
            if self.ai.board.count == len(self.ai.board.ships):
                print('-' * 20)
                print('Пользователь выиграл')
                break
            if self.us.board.count == len(self.us.board.ships):
                print('-' * 20)
                print('Компьютер выиграл')
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
