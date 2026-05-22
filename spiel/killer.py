def init_killer(game):
    game.scores = [3] * len(game.players)
    game.killer_numbers = [0] * len(game.players)
    game.killer_status = [False] * len(game.players)
    game.has_entered = [True] * len(game.players)

def process_killer(game, daten):
    p = game.current_player_idx
    val = daten["val"]
    is_triple = (daten["points"] == val * 3) if val > 0 else False
    if val == 0:
        game.finish_dart()
        return
    if game.killer_numbers[p] == 0:
        if val in game.killer_numbers or val == 25:
            if game.last_darts[p]:
                game.last_darts[p].pop()
            game.update_display()
            return
        else:
            game.killer_numbers[p] = val
            game.wait_and_next_player()
            return
    else:
        if val == game.killer_numbers[p] and not game.killer_status[p]:
            if is_triple:
                game.killer_status[p] = True
        elif game.killer_status[p] and is_triple:
            if val in game.killer_numbers:
                g_idx = game.killer_numbers.index(val)

                if g_idx not in game.finished_players:
                    game.scores[g_idx] = max(0, game.scores[g_idx] - 1)

                    if game.scores[g_idx] == 0:
                        game.finished_players.append(g_idx)
    lebende_spieler = [i for i in range(len(game.players)) if i not in game.finished_players]
    if len(lebende_spieler) == 1:
        gewinner = lebende_spieler[0]
        game.finished_players.insert(0, gewinner)
        game.wait_and_next_player()
        return
    game.finish_dart()
