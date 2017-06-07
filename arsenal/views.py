from collections import Counter

from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.db.models.functions import TruncMonth
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls.base import reverse
from django.utils import timezone
from django.contrib import messages

from data.models import Match, TeamSeason, Team
from arsenal.models import EventVote, VoteUser
from .models import VoteQuestion, VoteAnswer
from board_free.models import AfterReview
from lib.point import point

import datetime


def match(request, year_value=None, month_value=None, value=None):
    # next, prev 를 클릭하게 되면 now_year 와 now_month 값을 넣어줌
    if year_value:
        now_year = int(year_value)
        now_month = int(month_value)
    else:
        now_year = int(timezone.now().strftime('%Y'))
        now_month = int(timezone.now().strftime('%m'))
    acquire_date = datetime.datetime(year=now_year, month=now_month, day=1)

    if value == 'prev':
        acquire_date -= relativedelta(months=1)
    elif value == 'next':
        acquire_date += relativedelta(months=1)
    # Match 를 TruncMonth 로 이용해서 달마다 묶어줌
    match_sort = Match.objects.annotate(date=TruncMonth('match_date'))

    year = acquire_date.strftime('%Y')
    month = acquire_date.strftime('%m')
    matchs = match_sort.filter(date=year+'-'+month+'-01T00:00:00Z')

    # 팀 순위를 불러오기 위해서 검색을 함
    team_lists = TeamSeason.objects.filter(league='england').order_by('ranking',)

    return render(request, 'league/league_game.jinja', {'team_lists': team_lists, 'match_games':matchs, 'year':year, 'month':month})


def match_point(request, game):
    # 팀 순위를 불러오기 위해서 검색을 함
    team_lists = TeamSeason.objects.all().order_by('ranking',)

    # 아스날을 찾음
    arsenal = Team.objects.get(name='Arsenal')

    # 해당 게임을 구하고 그 게임에서 유저들이 점수를 준 평균을 구한다.
    match = Match.objects.prefetch_related('afterreview_match').get(id=game)
    match_player = [
        match.player1, match.player2, match.player3, match.player4, match.player5, match.player6, match.player7,
        match.player8, match.player9, match.player10, match.player11, match.player12, match.player13, match.player14
    ]
    by_all = []
    source = []
    if match:
        # by_all에 모든 유저들이 남긴 점수를 넣음
        avg_team = match.afterreview_match.filter(sort='0').aggregate(Avg('point'))
        for player in match_player:
            if player:
                avg = match.afterreview_match.filter(player=player).aggregate(Avg('point'))
                avg_value = [player, round(avg['point__avg'], 1)]
                by_all.append(avg_value)
        sort_player = sorted(by_all, key=lambda x:x[1], reverse=True)
        source = [round(avg_team['point__avg'], 1), sort_player[0], sort_player.pop(), len(match.afterreview_match.filter(sort='0'))]
    return render(request, 'league/league_point.jinja', {'team_lists': team_lists, 'by_all': by_all, 'source': source, 'arsenal': arsenal, 'game': match})


@login_required()
def vote(request):
    # 스코어 맞추기 이벤트를 위해서 가장 최근 경기와 가장 최근에 끝난 경기를 불러옴
    after_game = Match.recent.all()[0]
    before_game = Match.next.all()[0]
    match_player = [
        after_game.player1, after_game.player2, after_game.player3, after_game.player4, after_game.player5, after_game.player6,
        after_game.player7, after_game.player8, after_game.player9, after_game.player10, after_game.player11, after_game.player12,
        after_game.player13, after_game.player14
    ]
    if request.method == 'POST':
        post_value = request.POST.get('value', None)
        if post_value == 'simple_point':
            i = 0
            while i <= 14:
                if i == 0:
                    AfterReview.objects.create(
                        match=after_game, sort=str(i), point=request.POST.get('team_point'),
                        user=request.user, is_simple=True
                    )
                if i > 0:
                    if match_player[i - 1]:
                        AfterReview.objects.create(
                            match=after_game, sort=str(i), player=match_player[i - 1], user=request.user,
                            point=request.POST.get('player' + str(i) + '_point'), is_simple=True
                        )
                    else:
                        AfterReview.objects.create(
                            match=after_game, sort=str(i), user=request.user, is_simple=True
                        )
                i += 1
            # 포인트 함수
            point(request.user, 'easy_point')
            return HttpResponseRedirect(reverse('arsenal:vote'))

        elif post_value == 'score':
            EventVote.objects.create(
                user=request.user , match=before_game, home_score=request.POST.get('home_score'), away_score=request.POST.get('away_score')
            )
            # 포인트 함수
            point(request.user, 'vote')
            return redirect('http://127.0.0.1:8000/arsenal/vote/#vote_result')
    # freeboard 에서 가장 최근 경기의 평점을 유저가 남겼는지 여부 파악
    recent_game_by_user = AfterReview.objects.filter(match=after_game, user=request.user)
    if recent_game_by_user:
        by_all = []
        # by_all에 모든 유저들이 남긴 점수를 넣음
        avg_team = after_game.afterreview_match.filter(sort='0').aggregate(Avg('point'))
        by_all.append(avg_team['point__avg'])
        for player in match_player:
            if player:
                avg = after_game.afterreview_match.filter(player=player).aggregate(Avg('point'))
                if avg['point__avg'] == 10:
                    avg_value = [player, round(avg['point__avg'])]
                else:
                    avg_value = [player, round(avg['point__avg'],1)]
                by_all.append(avg_value)
    else:
        by_all = None

    #가장 최근 끝난 경기의 결과를 맞춘 사람을 불러옴
    event_result = EventVote.objects.filter(match=after_game, home_score=after_game.home_score, away_score=after_game.away_score, is_result=True).order_by('user', 'vote_date')

    end_event_round = event_result[0].event_round
    next_event_round = end_event_round + 1

    # 스코어 맞추기 이벤트의 가장 최근 경기 이며, 회원이 아니면 결과가 보여지게 만듬
    try:
        EventVote.objects.get(user=request.user, match=before_game)
    except EventVote.DoesNotExist:
        vote_results = None
    else:
        # 경기 결과를 예측한 유저를 구해서 많은 순대로 나열함
        vote_results = EventVote.objects.filter(match=before_game).values_list('home_score', 'away_score')
        vote_results = Counter(vote_results)
        vote_results = sorted(vote_results.items(), key=lambda x:x[1], reverse=True)[:5]
        vote_results = [[str(result[0][0]) + ":" + str(result[0][1]), round(result[1] / len(EventVote.objects.filter(match=before_game)) * 100, 1)] for result in vote_results]

    # 모든 vote 항목을 가져옴
    votes = VoteQuestion.active.all()
    return render(request, 'gooner/vote.jinja', {'votes': votes, 'end_event_round': end_event_round, 'vote_results': vote_results,
                                                  'event_result': event_result, 'next_event_round': next_event_round,
                                                  'next_match': before_game, 'by_all': by_all, 'match': after_game, 'match_player': match_player})


@login_required()
def question(request, question_id):
    question = VoteQuestion.objects.get(id=question_id)
    if request.method == 'POST':
        if question.is_sort == 'select' or question.is_sort == 'picture':
            value_list = request.POST.getlist('select_answer')
            if len(value_list) == 0:
                messages.error(request, '아무것도 선택되지 않았습니다.')
                return redirect('http://127.0.0.1:8000/arsenal/vote/#error-alert')
            elif len(value_list) <= question.choice_num:
                vote_result = VoteUser.objects.create(
                    question=question, user=request.user, is_sort=question.is_sort
                )
                for value in value_list:
                    answer = VoteAnswer.objects.get(question=question, id=value)
                    answer.vote += 1
                    answer.save()
                    vote_result.select_answer.add(answer)
            else:
                messages.error(request, '최대 답변의 개수가 넘어갔습니다. 확인부탁드립니다.')
                return redirect('http://127.0.0.1:8000/arsenal/vote/#error-alert')
        elif question.is_sort == 'write':
            write = request.POST.get('write_answer', None)
            if not write:
                messages.error(request, '답변이 입력 되지 않았습니다. 확인부탁드립니다.')
                return redirect('http://127.0.0.1:8000/arsenal/vote/#error-alert')
            else:
                VoteUser.objects.create(
                    question=question, user=request.user, is_sort=question.is_sort, write_answer=write
                )
        return HttpResponseRedirect(reverse('arsenal:vote'))


@login_required()
def dead_survey(request):
    dead_surveys = VoteQuestion.dead.all()
    return render(request, 'gooner/dead_survey.jinja', {'dead_surveys': dead_surveys})
