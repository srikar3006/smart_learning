from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def game_list(request):
    return render(request, "games/game_list.html")
