def init_classic(game):
    try:
        start_score = int("".join(filter(str.isdigit, game.game_mode)))
    except ValueError:
        start_score = 301
    game.scores = [start_score] * len(game.players)
    game.has_entered = [not game.cb_double_in.isChecked()] * len(game.players)

def check_elimination(game, current_idx, score):
    if score == 0:
        return
    try:
        start_score = int("".join(filter(str.isdigit, game.game_mode)))
    except ValueError:
        start_score = 301
    for i in range(len(game.players)):
        if i != current_idx and i not in game.finished_players and game.scores[i] == score:
            game.scores[i] = start_score
            game.is_bust[i] = True

def process_classic(game, daten):
    val = daten["val"]
    points = daten["points"]
    was_double = daten["was_double"]
    p = game.current_player_idx
    is_elimination = "Elimination" in game.game_mode
    is_mensch = "Mensch" in game.game_mode
    if not game.has_entered[p]:
        if was_double:
            game.has_entered[p] = True
        else:
            game.finish_dart()
            return
    new_score = game.scores[p] - points
    if new_score == 0 and (not game.double_out or was_double):
        game.scores[p] = 0
        game.finished_players.append(p)
        game.wait_and_next_player()
        return
    if (new_score < 0) or (new_score == 1 and game.double_out) or (new_score == 0 and game.double_out and not was_double):
        game.scores[p] = game.score_at_start_of_turn
        game.is_bust[p] = True
        game.darts_thrown += 1
        game.wait_and_next_player()
        return
    game.scores[p] = new_score
    if is_elimination or is_mensch:
        check_elimination(game, p, new_score)
    game.finish_dart()
