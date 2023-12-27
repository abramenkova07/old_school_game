from dataclasses import dataclass
from random import choice, randint

from constants import (ACTIONS, ACTION_QUESTION,
                       INTRO_TEXT, PERCENT_OF_POTIONS,
                       PERCENT_OF_VILLAINS)


class PlayingField:

    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.start_x, self.start_y = (self.row-1, 0)
        self.end_x, self.end_y = (0, self.col-1)
        self.chosen_steps = {
            '1': (-1, 0),
            '2': (0, 1),
            '3': (1, 0),
            '4': (0, -1)
        }
        self.reversed_chosen_steps = dict(
            zip(self.chosen_steps.values(), self.chosen_steps.keys())
        )
        self.villains_places = []
        self.potions_places = []
        self.bag = []

    def generating_field(self, step=None):
        """Генерация игрового поля, заданного размера."""
        field = [
            ['   ' for _ in range(self.col)]
            for _ in range(self.row)
        ]
        steps = []
        if step is not None:
            step_x, step_y = self.chosen_steps.get(step)
            self.start_x += step_x
            self.start_y += step_y
        if self.start_x != self.end_x or self.start_y != self.end_y:
            for x, y in self.chosen_steps.values():
                x_num, y_num = self.start_x + x, self.start_y + y
                if 0 <= x_num < self.row and 0 <= y_num < self.col:
                    mark = self.reversed_chosen_steps[
                        (x, y)
                    ]
                    field[x_num][y_num] = ' ' + mark + ' '
                    if mark not in steps:
                        steps.append(mark)
        field[self.end_x][self.end_y] = ' x '
        field[self.start_x][self.start_y] = ' * '
        for row in field:
            row_string = '|' + '|'.join(row) + '|'
            print('-' * len(row_string))
            print(row_string)
        print('-' * len(row_string))
        return steps

    def placing_villains_potions(self, villains_percent, potions_percent):
        """Расстановка злодеев и усиляющих зелий по полю."""
        villains_quantity = int((self.col * self.row) * villains_percent)
        potions_quantity = int((self.col * self.row) * potions_percent)
        villain_index = 0
        potion_index = 0
        while villain_index <= villains_quantity:
            coordinates = (randint(0, self.row-1), randint(0, self.col-1))
            if coordinates not in self.villains_places and \
               coordinates != (self.row-1, 0) and \
               coordinates != (0, self.col-1):
                self.villains_places.append(coordinates)
                villain_index += 1
            else:
                continue
        while potion_index <= potions_quantity:
            coordinates = (randint(0, self.row-1), randint(0, self.col-1))
            if coordinates not in self.villains_places and \
               coordinates != (self.row-1, 0) and \
               coordinates != (0, self.col-1):
                self.potions_places.append(coordinates)
                potion_index += 1
            else:
                continue

    def checking_fight(self):
        """Проверка необходимости боя."""
        if (self.start_x, self.start_y) in \
           self.villains_places:
            return choice([Character('Орк', 10, 5, 1, 0),
                           Character('Темный маг', 8, 2, 5, 0),
                           Character('Закалдованный рыцарь', 9, 4, 2, 0)])

    def removing_dead_villain(self):
        """Удаление с поля побежденного врага."""
        if (self.start_x, self.start_y) in self.villains_places:
            index = self.villains_places.index((self.start_x, self.start_y))
            self.villains_places.pop(index)

    def checking_potion(self):
        """Проверка наличия усиляющего зелья."""
        if (self.start_x, self.start_y) in \
           self.potions_places:
            return choice([Potion('Лечебное зелье', 5),
                           Potion('Усиляющее зелье', 4),
                           Potion('Магическое зелье', 4)])

    def removing_potion(self):
        """Удаление с поля найденного зелья."""
        if (self.start_x, self.start_y) in self.potions_places:
            index = self.potions_places.index((self.start_x, self.start_y))
            self.potions_places.pop(index)


@dataclass
class Character:
    name: str
    health: int
    strength: int
    spell: int
    healing: int

    def __str__(self):
        """Строковое представление экземпляра класса."""
        character_atributes = {
            'name': self.name,
            'health': max(0, self.health),
            'strength': self.strength,
            'spell': self.spell,
            'healing': self.healing
        }
        return ('{name} (здоровье: {health}, '
                'физическая сила: {strength}, магическая сила: '
                '{spell}, самолечение: {healing}'
                ')'.format(**character_atributes))

    def fighting(self, hero, action):
        """Битва с врагом."""
        hero_actions = dict(zip(ACTIONS,
                                [hero.strength, hero.spell]))
        villain_actions = dict(zip(ACTIONS,
                                   [self.strength, self.spell]))
        while action not in ACTIONS:
            action = input(ACTION_QUESTION)
        self.health -= hero_actions[action]
        if self.health > 0:
            villain_action = choice(ACTIONS)
            hero.health -= villain_actions[villain_action]
            hero.healing_power()
            print(f'Враг ответил своим действием: {villain_action}.')
            print(f'По итогу действия: {hero.name} (здоровье: '
                  f'{max(0, hero.health)}), {self.name} '
                  f'(здоровье: {max(0, self.health)}).')
            if hero.health <= 0:
                print('Вы проиграли! Игра окончена!')
        else:
            print('Вы победили врага! Можно двигаться дальше!')

    def healing_power(self):
        pass


class HealerCharacter(Character):

    def healing_power(self):
        if 0 < self.health <= 3:
            self.health += self.healing


@dataclass
class Potion:
    name: str
    value: int

    def __str__(self):
        """Строковое представление экземпляра класса."""
        return f'{self.name} c эффектом +{self.value}'


def main():
    print(INTRO_TEXT)
    warrior = Character('Воин', 9, 5, 2, 0)
    healer = HealerCharacter('Целитель', 7, 2, 4, 1)
    white_witch = Character('Колдунья', 7, 2, 5, 0)
    heroes = {warrior.name: warrior,
              healer.name: healer,
              white_witch.name: white_witch}
    names = (f'({", ".join(heroes.keys())}): ')
    character = input(f'Выберите героя, за которого вы будете играть: '
                      f'{warrior}, {white_witch} или {healer} {names}')
    while character not in heroes:
        character = input(f'Вы ввели несуществующего героя, '
                          f'выберите героя, за которого вы будете играть: '
                          f' {names}')
    print(f'Поздравляем! Вы играете за персонажа {character}!')
    hero = heroes[character]
    print('Ниже представлено игровое поле, по которому вы должны двигаться.')
    fields = PlayingField(8, 8)
    steps = fields.generating_field()
    fields.placing_villains_potions(PERCENT_OF_VILLAINS, PERCENT_OF_POTIONS)
    while (fields.start_x != fields.end_x or fields.start_y != fields.end_y) \
            and hero.health > 0:
        step = input(f'Введите выбранный шаг ({", ".join(steps)}): ')
        while step not in steps:
            step = input(f'Вы ввели некорректный шаг ({step}). '
                         f'Введите корректный шаг '
                         f'({", ".join(steps)}): ')
        villain = fields.checking_fight()
        if villain:
            print(f'На вас напал {villain}. '
                  f'Ваши показатели {hero}')
            while villain.health > 0 and hero.health > 0:
                if fields.bag:
                    potion_usage = input('Будете использовать зелье '
                                         '(да, нет)? ')
                    while potion_usage not in ('да' 'нет'):
                        potion_usage = input('Введите да или нет. ')
                    if potion_usage == 'да':
                        indexed_bag = []
                        for index, potion in enumerate(fields.bag, 1):
                            indexed_bag.append(f'{potion} ({index})')
                        potion_index = input(f'Выберите зелье: '
                                             f'{", ".join(indexed_bag)}. ')
                        used_potion = fields.bag[int(potion_index)-1]
                        if used_potion.name == 'Лечебное зелье':
                            hero.health += used_potion.value
                        elif used_potion.name == 'Усиляющее зелье':
                            hero.strength += used_potion.value
                        else:
                            hero.spell += used_potion.value
                        print(hero)
                        fields.bag.pop(int(potion_index)-1)
                action = input(f'Какое действие выберите '
                               f'({", ".join(ACTIONS)})? ')
                villain.fighting(hero, action)
            fields.removing_dead_villain()
        if hero.health > 0:
            steps = fields.generating_field(step)
        potion = fields.checking_potion()
        if potion:
            print(f'Вы нашли: {potion}')
            fields.bag.append(potion)
            fields.removing_potion()
    if fields.start_x == fields.end_x and fields.start_y == fields.end_y:
        print('Игра окончена. Вы выиграли! Поздравляем!')


if __name__ == '__main__':
    main()
