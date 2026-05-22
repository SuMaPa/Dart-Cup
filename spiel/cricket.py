def init_cricket(game):
    game.scores = [0] * len(game.players)
    game.cricket_stat = {player_idx: {num: 0 for num in [15, 16, 17, 18, 19, 20, 25]}
                         for player_idx in range(len(game.players))}
    game.has_entered = [True] * len(game.players)

def process_cricket(game, daten):
    val = daten["val"]
    p = game.current_player_idx
    modifier = daten["points"] // val if val > 0 else 1
    if val in game.cricket_stat[p]:
        treffer_zufuhr = modifier
        for _ in range(treffer_zufuhr):
            if game.cricket_stat[p][val] < 3:
                game.cricket_stat[p][val] += 1
            else:
                gegner_haben_offen = any(game.cricket_stat[g_idx][val] < 3
                                         for g_idx in range(len(game.players)) if g_idx != p)
                if gegner_haben_offen:
                    game.scores[p] += 25 if val == 25 else val
        alles_zu = all(game.cricket_stat[p][num] == 3 for num in game.cricket_stat[p])
        meiste_punkte = game.scores[p] == max(game.scores)
        if alles_zu and meiste_punkte:
            game.finished_players.append(p)
            game.wait_and_next_player()
            return

    game.finish_dart()
