from time import sleep        # Для имитации "времени размышления" перед ходом компьютера
from random import randint


# внутренняя логика (классы исключений,Dot, Ship, Board):

class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Ваш выстрел ушел за пределы поля сраженмя. Повторите попытку."


class BoardBusyException(BoardException):
    def __str__(self):
        return "Это поле уже обстреляно. Повторите попытку."


class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"({self.x}, {self.y})"

    def __eq__(self, other_dot):
        return self.x == other_dot.x and self.y == other_dot.y


class Ship:
    def __init__(self, ship_lenght, bow_dot, orientation):
        self.bow_dot = bow_dot
        self.ship_lenght = ship_lenght
        self.orientation = orientation
        self.lives = ship_lenght

    @property
    def ship_dots(self):
        dots = [self.bow_dot]
        next_x, next_y = self.bow_dot.x, self.bow_dot.y
        for i in range(self.ship_lenght - 1):
            if self.orientation == 0:  # корабль вертикальный
                next_x += 1
            else:
                next_y += 1
            dots.append(Dot(next_x, next_y))
        return dots


class Board:
    def __init__(self, hid=False, size_of_map=6):  # параметра hid нет т.к. поля битвы на экране сделаны горизонтально
        self.hid = hid
        self.size_of_map = size_of_map
        self.ships_list = []
        self.live_ships_count = 7
        self.battle_map = [["o"] * size_of_map for _ in range(size_of_map)]
        self.occupied_dots = []  # ячейки непригодые для стрельбы - обстрелянные и границы вокруг потопленных

    def new_board_in_game(self):
        self.occupied_dots = []

    def add_ship(self, ship):
        for i_dot in ship.ship_dots:
            if self.out(i_dot) or i_dot in self.occupied_dots:
                raise BoardWrongShipException()
        for i_dot in ship.ship_dots:
            self.battle_map[i_dot.x][i_dot.y] = "■"
            self.occupied_dots.append(i_dot)
        self.ships_list.append(ship)
        self.contour(ship)

    def contour(self, ship, ship_status=1):  # ship_status = 0 - корабль потоплен, 1 - корабль на плаву

        # around_ship_deltas = [(-1,-1), (0,-1),   (1,-1),  - схема обхода окрестностей корабля
        #                       (-1,0),  dot(0,0), (1,0),
        #                       (-1,1),   (0,1),   (1,1)]

        for d in ship.ship_dots:
            for delta_y in range(-1, 2):  # обход окрестностей корабля в пределах 1 ячейки
                for delta_x in range(-1, 2):
                    around_dot = Dot(d.x + delta_x, d.y + delta_y)
                    if not self.out(around_dot) and around_dot not in self.occupied_dots:
                        if ship_status == 0:
                            self.battle_map[around_dot.x][around_dot.y] = '.'
                        self.occupied_dots.append(around_dot)

    def out(self, dot):
        return not (0 <= dot.x < 6) or not (0 <= dot.y < 6)

    def shot(self, dot):
        if self.out(dot):
            raise BoardOutException()
        elif dot in self.occupied_dots:
            raise BoardBusyException()
        self.occupied_dots.append(dot)
        for ship in self.ships_list:
            if dot in ship.ship_dots:
                ship.lives -= 1
                self.battle_map[dot.x][dot.y] = "x"
                if ship.lives == 0:
                    self.live_ships_count -= 1
                    self.contour(ship, ship_status=0)
                    print("Корабль потоплен!")
                    sleep(1)
                    return False
                else:
                    print("Корабль повреждён!")
                    sleep(1)
                    return True
        self.battle_map[dot.x][dot.y] = "T"
        print("Промах!")
        sleep(1)
        return False


# внешняя логика (классы пользователей,Game):

class Player:
    def __init__(self, my_board, opponent_board):
        self.my_board = my_board
        self.opponent_board = opponent_board

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target_dot = self.ask()
                shot_result = self.opponent_board.shot(target_dot)
                return shot_result
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        target_dot = Dot(randint(0, 5), randint(0, 5))
        sleep(1)
        print(f"Противник выстрелил в точку {target_dot.x + 1} {target_dot.y + 1}!")
        sleep(1)
        return target_dot


class User(Player):
    def ask(self):
        while True:
            shot_coordinates = input("Координаты выстрела: ").split()
            try:
                x, y = shot_coordinates
            except ValueError:
                print("Неверно. Требуются 2 координаты через пробел: ")
                continue
            if (x.isdigit() is False) or (y.isdigit() is False):
                print("Неверно. Укажите цифры 1-6 в координатах выстрела: ")
                continue
            elif int(x) and int(y) not in range(1, 7):
                print("Требуются координаты в диапазоне 1...6: ")
            return Dot(int(x) - 1, int(y) - 1)


class Game:
    def calculate_random_board(self):
        ship_set = [3, 2, 2, 1, 1, 1, 1]
        attempts = 0
        board = Board(size_of_map=self.size_of_board)
        for ship_type in ship_set:
            while True:
                attempts += 1
                if attempts > 1800:
                    return None
                ship = Ship(ship_type, Dot(randint(0, self.size_of_board), randint(0, self.size_of_board)),
                            randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.new_board_in_game()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.calculate_random_board()
        return board

    def __init__(self, size_of_board=6):
        self.size_of_board = size_of_board
        my_board = self.random_board()
        opponent_board = self.random_board()
        opponent_board.hid = True
        self.user = User(my_board, opponent_board)
        self.opponent = AI(opponent_board, my_board)

    def greet(self):
        message = '''
         *************************************************
         ***      "Морской бой" приветствует Вас!      ***
         ***   Дайте координаты выстрела в виде: X Y   ***
         ***   X - номер строки, Y - номер столбца     ***
         *************************************************
           '''
        print(message)

    def battle_maps_print(self):
        print("======= Cвоё поле =============      ========= Поле противника =====")
        print("    | 1 | 2 | 3 | 4 | 5 | 6 |            | 1 | 2 | 3 | 4 | 5 | 6 |")
        for i, value in enumerate(zip(self.user.my_board.battle_map, self.user.opponent_board.battle_map)):
            print(f"  {i + 1} | " + " | ".join(value[0]) + " |" + " " * 10 +
                  f"{i + 1} | " + " | ".join(value[1]).replace("■", "o") + " |")
        print("====================================================================")

    def loop(self):
        shooting_player = True  # чья очередь стрелять True - user, false - AI
        while True:
            self.battle_maps_print()
            if shooting_player:
                print("Ваш ход. Дайте координаты: ")
                result_of_shot = self.user.move()
            else:
                print("Стреляет противник! Огонь!")
                result_of_shot = self.opponent.move()
            if self.user.my_board.live_ships_count == 0:
                self.battle_maps_print()
                print("********* Вы проиграли.  **********")
                break
            elif self.user.opponent_board.live_ships_count == 0:
                self.battle_maps_print()
                print("********* Вы выиграли! **********")
                break
            if result_of_shot:
                print("Есть попадание!")
                continue
            shooting_player = not shooting_player  # смена текущего игрока

    def start(self):
        self.greet()
        self.loop()


sea_battle_game = Game()
sea_battle_game.start()
