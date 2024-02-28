from ui import *


pig_score = 0


# Начало игры
def start_game():
    global active_screen
    active_screen = Screen("img/bg.jpg", "Приветствуем вас в PigGame!", text_color='white',
                           blit_screen=screen,
                           buttons=[
                               Button('screen', 'screen', 150, 30, "НАЧАТЬ "
                                                                   "ИГРУ", game),
                               Button('screen', 'screen', 150, 30, "ПРАВИЛА", rules),
                               Button('screen', 'screen', 150, 30, "ВЫЙТИ", terminate)
                           ])


def rules():
    global active_screen
    active_screen = Screen("img/bg.jpg", "Правила игры", text_color='white',
                           blit_screen=screen,
                           buttons=[
                               Button('screen', HEIGHT - 100, 150, 30, "Назад", start_game)
                           ])

    rules = "Ваша задача собрать, как можно больше групп карт, чем соперник. Обыграйте Мистера Свина!"
    rules_text1 = Text(rules, font_size=24)
    # rules_text2 = Text("2", font_size=24)
    active_screen.add_or_change_text('rules', rules_text1, WIDTH / 2 - rules_text1.get_width() / 2, HEIGHT - 400)
    # active_screen.add_or_change_text('rules', rules_text2, WIDTH / 2 - rules_text1.get_width() / 2, HEIGHT - 400 + 10)


# Тосовка карт
def make_cards(count):
    in_row = []
    while True:
        result = []
        for i in range(count):
            card = Card(random.choice(DECK))
            if in_row.count(card.name[0]) >= 3:
                break
            in_row.append(card.name[0])
            result.append(Card(random.choice(DECK)))
            del DECK[DECK.index(result[-1].name)]
        else:
            return result


# Отрисовка доски
def draw_board(scrn, board):
    board.draw()
    scrn.blit(board, (0, HEIGHT - board.height))


def animate(scrn, name, delay):
    global timer_tick
    curr_tick = animate_frames[name]["current"]

    if pygame.time.get_ticks() / 1000 >= timer_tick + delay:
        animate_frames[name]["current"] = curr_tick + 1 if curr_tick + 1 <= animate_frames[name]["max"] else 1
        timer_tick = pygame.time.get_ticks() / 1000
        scrn.add_or_change_picture(name,
                                   pygame.transform.scale(pygame.image.load(animate_frames[name]["images"][curr_tick
                                                                                                           - 1]),
                                                          (200, 200)), scrn.pictures[name][1][0],
                                   scrn.pictures[name][1][1])


def waiting_for_pig_motion(scrn, board):
    global pig_animation_is_end, pig_asking_card_nominal
    if player_cards == [] and DECK:
        card = random.choice(DECK)
        player_cards.append(card)
        board.add_card(Card(card))
        del DECK[DECK.index(card)]
        board.player_motion = False

    if pig_cards == [] and DECK:
        card = random.choice(DECK)
        pig_cards.append(card)
        del DECK[DECK.index(card)]
        board.player_motion = True
        scrn.add_or_change_event("animate_pig", animate, "Pig", 0.2, for_time=2.1)
        pig_sounds['none'].set_volume(1.5)
        pig_sounds['none'].play()

    if not board.player_motion:
        try:
            try:
                if scrn.events["animate_pig_again"]:
                    pass
            except Exception:
                if scrn.events["animate_pig"]:
                    pig_animation_is_end = True
        except KeyError:
            if pig_animation_is_end:
                pig_animation_is_end = False
                ask_for_card(scrn, board, pig_asking_card_nominal)
            else:
                scrn.add_or_change_text("State", Text("Ход Мистера Свина"), 50, 35)
                scrn.add_or_change_event("animate_pig", animate, "Pig", 0.2, for_time=2.1)

                pig_asking_card_nominal = random.choice(pig_cards).split('_')[0]
                if len(pig_already_checked) == len(pig_cards):
                    pig_already_checked.clear()

                while pig_asking_card_nominal in pig_already_checked:
                    pig_asking_card_nominal = random.choice(pig_cards).split('_')[0]

                pig_sounds[pig_asking_card_nominal].set_volume(1.5)
                pig_sounds[pig_asking_card_nominal].play()

                pig_already_checked.append(pig_asking_card_nominal)
    else:
        pig_already_checked.clear()


def check_for_pig_stock():
    global pig_score, active_screen
    try:
        for group in pig_cards:
            group_in_pig_cards = list(filter(lambda x: x.split('_')[0] == group.split('_')[0], pig_cards))
            if len(group_in_pig_cards) >= 4:
                print(pig_stock_cards, pig_score)
                pig_stock_cards.extend(group_in_pig_cards)
                pig_score += 1
                active_screen.add_or_change_text("Pig_score", Text(f"{pig_score}"), WIDTH - 300, 140)
                for i in group_in_pig_cards:
                    del pig_cards[pig_cards.index(i)]
    except RuntimeError:
        pass


def ask_for_card(scrn, board, card_nominal):
    if pig_cards:
        print("Свин спрашивает у вас карту: " + card_nominal)
        need_cards = list(filter(lambda x: x.split("_")[0] == card_nominal, player_cards))
        if need_cards:
            for card in need_cards:
                pig_cards.append(card)
                board.remove_card(card)
                del player_cards[player_cards.index(card)]

                check_for_pig_stock()
            return 0

    if DECK:
        card = random.choice(DECK)
        pig_cards.append(card)
        del DECK[DECK.index(card)]

        check_for_pig_stock()

        random_card_nominal = card.split('_')[0]
        exists_cards = list(filter(lambda x: x.split("_")[0] == random_card_nominal and x != card, pig_cards))
        if not exists_cards:
            board.player_motion = not board.player_motion
            scrn.add_or_change_text("State", Text("Ваш ход"), 50, 35)
        else:
            scrn.add_or_change_event("animate_pig_again", animate, "Pig", 0.2, for_time=3)
            pig_sounds['again'].set_volume(1.5)
            pig_sounds['again'].play()


    print("Player cards: ", player_cards)
    print("Pig cards: ", pig_cards)
    print("Stock cards: ", stock_cards)
    print("Board cards: ", board.cards)
    print("All cards: ", DECK, '\n')


# Запуск игры
def game():
    global active_screen
    active_screen = Screen("img/game.jpg", "", blit_screen=screen)

    pig = pygame.transform.scale(pygame.image.load("img/pig/pig1.png"), (200, 200))
    active_screen.add_or_change_picture("Pig", pig, 825, 0)

    active_screen.add_or_change_text("State", Text("Ваш ход"), 50, 35)
    active_screen.add_or_change_text("Score", Text(str(score)), 50, HEIGHT - 300)
    active_screen.add_or_change_text("Pig_score", Text(f"{pig_score}"), WIDTH - 300, 140)

    board = Board(185)
    active_screen.add_or_change_event("draw_board", draw_board, board)

    active_screen.add_or_change_event("pig_motion", waiting_for_pig_motion, board)

    for card in make_cards(5):
        board.add_card(card)
        player_cards.append(card.name)

    for card in make_cards(5):
        pig_cards.append(card.name)

    print("Player cards: ", player_cards)
    print("Pig cards: ", pig_cards)
    print("Stock cards: ", stock_cards, '\n')


def finish_game(winer):
    global active_screen, DECK, pig_cards, player_cards, stock_cards, pig_stock_cards, score, pig_score
    active_screen.reset()
    DECK = list(CARDS.keys())
    pig_cards = []
    player_cards = []
    stock_cards = []
    pig_stock_cards = []
    score = 0
    pig_score = 0

    pwin = ""
    if winer == "pig":
        pwin = "проиграли"
    elif winer == "gamer":
        pwin = "выиграли"

    active_screen = Screen("img/bg.jpg", f"Вы {pwin}!", text_color='white',
                           blit_screen=screen,
                           buttons=[
                               Button('screen', 'screen', 150, 30, "ЗАНОВО", game),
                               Button('screen', 'screen', 150, 30, "ВЫЙТИ", terminate)
                           ])
    print(1)


# Отрисовка приложения
def draw():
    running = True
    start_game()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        clock.tick(fps)

        if pig_score >= 5:
            finish_game('pig')
        try:
            if int(active_screen.texts['Score'][0].text) >= 5:
                finish_game('gamer')
        except KeyError:
            pass

        active_screen.fill((0, 0, 0))
        active_screen.draw()
        pygame.display.flip()


# Запуск
if __name__ == '__main__':
    pig_asking_card_nominal = ''
    pig_animation_is_end = False
    pig_already_checked = []
    active_screen = None
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('PigGame', 'img/icon.png')

    draw()
    terminate()
