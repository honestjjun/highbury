
# 각 선수별의 평균을 내기
after_review_players = AfterReview.objects.filter(user=users, player__isnull=False).values_list('player', 'point')
for after_review_player in after_review_players:
    in_player = PlayerSeason.objects.get(id=after_review_player[0])
    if in_player in after_player:
        after_player[in_player]['point'] += after_review_player[1]
        after_player[in_player]['game'] += 1
    else:
        after_player[in_player] = {'point': after_review_player[1], 'game': 1}
player_keys = after_player.keys()
for player_key in player_keys:
    after_list.append((player_key, round(after_player[player_key]['point']/after_player[player_key]['game'],1)))
after_sorted = sorted(after_list, key=lambda x:x[1], reverse=True)