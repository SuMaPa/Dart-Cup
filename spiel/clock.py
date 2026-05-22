def init_around_the_clock(game):
    game.scores = [1] * len(game.players)


def process_around_the_clock(game, daten):
    val = daten["val"]
    p = game.current_player_idx
    if val == game.scores[p]:
        if val == 20:
            game.scores[p] = 25
        elif val == 25:
            game.scores[p] = 0
            game.finished_players.append(p)
            game.darts_thrown += 1
            game.wait_and_next_player()
            return
        else:
            game.scores[p] += 1

    game.finish_dart()


def process_around_the_clock_extreme(game, daten):
    val = daten["val"]
    p = game.current_player_idx
    modifier = daten["points"] // val if val > 0 else 1
    if val == game.scores[p]:
        neues_ziel = game.scores[p] + modifier
        if neues_ziel <= 20:
            game.scores[p] = neues_ziel
        elif val == 20:
            game.scores[p] = 25
        elif val == 25:
            game.scores[p] = 0
            game.finished_players.append(p)
            game.darts_thrown += 1
            game.wait_and_next_player()
            return
        else:
            pass

    game.finish_dart()
