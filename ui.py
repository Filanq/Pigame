import colorama
import pygame
import sys
import random

# Объявляем глобальные переменные
pygame.init()

pygame.mixer.init()
pygame.mixer.music.load('sound/music.mp3')
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.35)

pig_sounds = {
    '6': pygame.mixer.Sound('sound/pig/6.wav'),
    '7': pygame.mixer.Sound('sound/pig/7.wav'),
    '8': pygame.mixer.Sound('sound/pig/8.wav'),
    '9': pygame.mixer.Sound('sound/pig/9.wav'),
    '10': pygame.mixer.Sound('sound/pig/10.wav'),
    'v': pygame.mixer.Sound('sound/pig/v.wav'),
    'd': pygame.mixer.Sound('sound/pig/d.wav'),
    'k': pygame.mixer.Sound('sound/pig/k.wav'),
    't': pygame.mixer.Sound('sound/pig/t.wav'),
    'none': pygame.mixer.Sound('sound/pig/none.wav'),
    'again': pygame.mixer.Sound('sound/pig/again.wav')
}

WIDTH = 1024
HEIGHT = 768
CARD_W = 100
CARD_H = 150
title_font = pygame.font.Font(None, 48)
button_font = pygame.font.Font(None, 24)
fps = 30
clock = pygame.time.Clock()
cards_folder = "img/cards"
card_click_delay = 0
CARDS = {
    "6_k": f'{cards_folder}/6k.jpg', "6_b": f'{cards_folder}/6b.jpg', "6_ch": f'{cards_folder}/6ch.jpg',
    "6_p": f'{cards_folder}/6p.jpg', "7_k": f'{cards_folder}/7k.jpg', "7_b": f'{cards_folder}/7b.jpg',
    "7_ch": f'{cards_folder}/7ch.jpg', "7_p": f'{cards_folder}/7p.jpg', "8_k": f'{cards_folder}/8k.jpg',
    "8_b": f'{cards_folder}/8b.jpg', "8_ch": f'{cards_folder}/8ch.jpg', "8_p": f'{cards_folder}/8p.jpg',
    "9_k": f'{cards_folder}/9k.jpg', "9_b": f'{cards_folder}/9b.jpg', "9_ch": f'{cards_folder}/9ch.jpg',
    "9_p": f'{cards_folder}/9p.jpg', "10_k": f'{cards_folder}/10k.jpg', "10_b": f'{cards_folder}/10b.jpg',
    "10_ch": f'{cards_folder}/10ch.jpg', "10_p": f'{cards_folder}/10p.jpg', "v_k": f'{cards_folder}/vk.jpg',
    "v_b": f'{cards_folder}/vb.jpg', "v_ch": f'{cards_folder}/vch.jpg', "v_p": f'{cards_folder}/vp.jpg',
    "d_k": f'{cards_folder}/dk.jpg', "d_b": f'{cards_folder}/db.jpg', "d_ch": f'{cards_folder}/dch.jpg',
    "d_p": f'{cards_folder}/dp.jpg', "k_k": f'{cards_folder}/kk.jpg', "k_b": f'{cards_folder}/kb.jpg',
    "k_ch": f'{cards_folder}/kch.jpg', "k_p": f'{cards_folder}/kp.jpg', "t_k": f'{cards_folder}/tk.jpg',
    "t_b": f'{cards_folder}/tb.jpg', "t_ch": f'{cards_folder}/tch.jpg', "t_p": f'{cards_folder}/tp.jpg'
}

timer_tick = 0
animate_frames = {
    "Pig": {"current": 1, "max": 2, "images": ['img/pig/pig1.png', 'img/pig/pig2.png']}
}
DECK = list(CARDS.keys())
pig_cards = []
player_cards = []
stock_cards = []
pig_stock_cards = []
score = 0


# Выход из игры
def terminate():
    pygame.quit()
    sys.exit()


# Класс экрана (например, стартовый экран, главный и т.д.)
class Screen(pygame.surface.Surface):
    def __init__(self, bg_image, text="", text_color='black', blit_screen=None, buttons=None):
        super().__init__((WIDTH, HEIGHT))
        try:
            self.bg = pygame.transform.scale(pygame.image.load(bg_image), (WIDTH, HEIGHT))
        except FileNotFoundError:
            print('\n' + colorama.Back.RED + f'Картинка {bg_image} не найдена')
            terminate()

        self.buttons = buttons
        self.blit_screen = blit_screen
        self.btn_padding = 10
        self.texts = {}
        self.events = {}
        self.pictures = {}

        self.string_rendered = title_font.render(text, 1, pygame.Color(text_color))
        self.text_intro_rect = self.string_rendered.get_rect()
        self.text_intro_rect.y = HEIGHT // 3
        self.text_intro_rect.x = WIDTH // 2 - self.text_intro_rect.w // 2

    def reset(self):
        global DECK, pig_cards, player_cards, stock_cards, pig_stock_cards, score
        DECK = list(CARDS.keys())
        pig_cards = []
        player_cards = []
        stock_cards = []
        pig_stock_cards = []
        score = 0

    # Добавить текст на окно
    def add_or_change_text(self, name, text, x, y):
        self.texts[name] = (text, (x, y))

    # Удалить текст
    def remove_text(self, name):
        del self.texts[name]

    # Добавить картинку
    def add_or_change_picture(self, name, pic, x, y):
        self.pictures[name] = (pic, (x, y))

    # Удалить картинку
    def remove_picture(self, name):
        del self.pictures[name]

    # Добавить обработчик
    def add_or_change_event(self, name, event, *args, for_time=None):
        self.events[name] = [event, args]
        if for_time:
            self.events[name].append(for_time + pygame.time.get_ticks() / 1000)

    # Удалить обработчик
    def remove_event(self, name):
        del self.events[name]

    # Отрисовка кнопок
    def draw(self):
        self.blit(self.bg, (0, 0))
        self.blit(self.string_rendered, self.text_intro_rect)
        if self.buttons:
            for num, btn in enumerate(self.buttons):
                if btn.y == 'screen':
                    btn.y = (((HEIGHT / 2) -
                              (len(self.buttons) * btn.height + (self.btn_padding * (len(self.buttons) - 1))))
                             + num * btn.height + num * self.btn_padding) + 50
                    btn.rect = pygame.Rect(btn.x, btn.y, btn.width, btn.height)
                else:
                    self.blit(btn.surface, btn.rect)
                btn.process()
        if self.texts:
            for txt in self.texts.values():
                self.blit(*txt)

        if self.events:
            try:
                for name, event in zip(self.events.keys(), self.events.values()):
                    event[0](self, *event[1])
                    try:
                        if pygame.time.get_ticks() / 1000 >= event[2]:
                            self.remove_event(name)
                            break
                    except IndexError:
                        pass
            except RuntimeError:
                pass

        if self.pictures:
            for picture in self.pictures.values():
                self.blit(*picture)

        self.blit_screen.blit(self, (0, 0))

    def blit(
        self,
        source,
        dest,
        area=None,
        special_flags=0,
    ):
        super().blit(source, dest, area=area, special_flags=special_flags)
        try:
            source.main_screen = self
        except AttributeError:
            pass


# Клас текста
class Text(pygame.Surface):
    def __init__(self, text, text_color='white', font_size=48):
        font = pygame.font.Font(None, font_size)
        text_render = font.render(text, 1, pygame.Color(text_color))
        super().__init__(text_render.get_size(), pygame.SRCALPHA, 32)
        self.blit(text_render, (0, 0))
        self.text = text


# Класс кнопки
class Button:
    def __init__(self, x, y, width, height, button_text='Button', onclick=None, blit_screen=None, fill_colors=None):
        if fill_colors is None:
            fill_colors = {'normal': '#ffffff', 'hover': '#dddddd', 'pressed': '#cccccc'}

        if x == 'screen':
            self.x = WIDTH / 2 - width / 2
        else:
            self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.onclick = onclick
        self.pressed = False
        self.blit_screen = blit_screen
        self.delay = 100
        self.success_time = 0

        self.fillColors = fill_colors
        self.surface = pygame.Surface((self.width, self.height))
        self.rect = pygame.Rect(self.x, self.y if self.y != 'screen' else 0, self.width, self.height)

        self.text = button_font.render(button_text, True, (0, 0, 0))

    # Рендеринг
    def process(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.fillColors:
            self.surface.fill(self.fillColors['normal'])
        if self.rect.collidepoint(mouse_pos):
            if self.fillColors:
                self.surface.fill(self.fillColors['hover'])
            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                if self.fillColors:
                    self.surface.fill(self.fillColors['pressed'])
                if not self.pressed:
                    self.pressed = True
            else:
                if self.pressed and pygame.time.get_ticks() >= self.success_time:
                    self.pressed = False
                    self.success_time = pygame.time.get_ticks() + self.delay
                    self.onclick()
        else:
            self.pressed = False
        self.surface.blit(self.text, [
            self.rect.width / 2 - self.text.get_rect().width / 2,
            self.rect.height / 2 - self.text.get_rect().height / 2
        ])
        if self.blit_screen:
            self.blit_screen.blit(self.surface, self.rect)


class Card(Button):
    def __init__(self, name, onclick=None):
        super().__init__(0, 0, CARD_W, CARD_H, button_text="", onclick=onclick, fill_colors=0)
        self.name = name
        self.board = None
        try:
            self.bg = pygame.transform.scale(pygame.image.load(CARDS[name]), (CARD_W, CARD_H))
        except FileNotFoundError:
            print('\n' + colorama.Back.RED + f'Картинка {CARDS[name]} не найдена')
            terminate()

    def press(self):
        global card_click_delay
        if not self.board.player_motion or pygame.time.get_ticks() < card_click_delay:
            return False

        card_click_delay = pygame.time.get_ticks() + 500

        card_nominal = self.name.split('_')[0]
        need_cards = list(filter(lambda x: x.split("_")[0] == card_nominal, pig_cards))
        if need_cards:
            for card in need_cards:
                player_cards.append(card)
                self.board.add_card(Card(card))
                del pig_cards[pig_cards.index(card)]

                self.board.check_for_stock()
        else:
            if DECK:
                card = random.choice(DECK)
                player_cards.append(card)
                self.board.add_card(Card(card))
                del DECK[DECK.index(card)]
                self.board.check_for_stock()

                random_card_nominal = card.split('_')[0]
                exists_cards = list(filter(lambda x: x.split("_")[0] == random_card_nominal and x != card, player_cards))
                if not exists_cards:
                    self.board.player_motion = not self.board.player_motion
            else:
                self.board.player_motion = not self.board.player_motion

    def process(self):
        super().process()
        self.surface.blit(self.bg, (0, 0))


# Класс доски с картами
class Board(pygame.Surface):
    def __init__(self, height):
        super().__init__((WIDTH, height), pygame.SRCALPHA, 32)
        self.height = height
        self.cards = {}
        self.x_padding = 25
        self.y_padding = 10
        self.main_screen = None
        self.player_motion = True

    def add_card(self, card):
        card.board = self
        try:
            self.cards[card.name.split('_')[0]][card.name.split('_')[1]] = card
        except KeyError:
            self.cards[card.name.split('_')[0]] = {}
            self.cards[card.name.split('_')[0]][card.name.split('_')[1]] = card
        self.repos_cards()
        card.onclick = card.press

    def remove_card(self, card_name):
        del self.cards[card_name.split('_')[0]][card_name.split('_')[1]]
        if not self.cards[card_name.split('_')[0]]:
            del self.cards[card_name.split('_')[0]]
        self.repos_cards()

    def repos_cards(self):
        for xpos, group in enumerate(self.cards.values()):
            for ypos, card in enumerate(group.values()):
                card.x = (self.x_padding * (xpos + 1)) + (CARD_W * xpos)
                card.y = (HEIGHT - self.height) + (self.y_padding * (ypos + 1))
                card.rect = pygame.Rect(card.x, card.y, card.width, card.height)

    def check_for_stock(self):
        global score
        for group in self.cards.keys():
            group_in_player_cards = list(filter(lambda x: x.split('_')[0] == group, player_cards))
            if len(group_in_player_cards) >= 4:
                score += 1
                stock_cards.extend(group_in_player_cards)
                for i in group_in_player_cards:
                    del player_cards[player_cards.index(i)]
                    self.remove_card(i)
                self.main_screen.add_or_change_text("Score", Text(str(score)), 50, HEIGHT - 300)

    def draw(self):
        try:
            self.fill(pygame.SRCALPHA)
            for group in self.cards.values():
                for card in group.values():
                    card.process()
                    self.blit(card.surface, (card.x, card.y - (HEIGHT - self.height)))
        except RuntimeError:
            pass
