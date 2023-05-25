from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages
from .forms import TotalizatorForm, SelectGameForm, EditScoreForm
from .models import Totalizator, GameScore


def index(request):
    totalizators = Totalizator.objects.all()

    if request.method == 'POST':
        form = TotalizatorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Guess recorded!")
    else:
        form = TotalizatorForm()

    return render(request, 'zalgiris/totalizator.html', {
        'form': form,
        'totalizators': totalizators,
    })


def edit_score(request):
    if request.method == 'POST':
        game_id = request.POST.get('game_id')
        game = get_object_or_404(GameScore, id=game_id)
        form = EditScoreForm(request.POST, instance=game)
        if form.is_valid():
            form.save()
            return redirect('scores')
    else:
        select_form = SelectGameForm()
        form = None

    context = {
        'select_form': select_form,
        'form': form,
    }

    if request.method == 'POST' and 'select_game' in request.POST:
        select_form = SelectGameForm(request.POST)
        if select_form.is_valid():
            game_id = select_form.cleaned_data['game_id']
            game = get_object_or_404(GameScore, id=game_id)
            form = EditScoreForm(instance=game)
            context.update({'form': form})

    return render(request, 'zalgiris/edit_score.html', context)


def scores(request):
    games = GameScore.objects.all()
    totalizators = Totalizator.objects.all().select_related('game_score')

    for totalizator in totalizators:
        calculate_guess_accuracy(totalizator)

    totalizators = totalizators.order_by('-guess_accuracy')

    context = {
        'games': games,
        'totalizators': totalizators,
    }

    return render(request, 'zalgiris/scores.html', context)


def calculate_guess_accuracy(totalizator_instance):
    # Get actual scores
    actual_zalgiris_score = totalizator_instance.game_score.zalgiris_score
    actual_barcelona_score = totalizator_instance.game_score.barcelona_score

    # Difference between the guesses and the actual scores
    zalgiris_guess_difference = abs(totalizator_instance.zalgiris_guess - actual_zalgiris_score)
    barcelona_guess_difference = abs(totalizator_instance.barcelona_guess - actual_barcelona_score)

    # Calculate the mean percentage error for both guesses
    zalgiris_percentage_error = zalgiris_guess_difference / actual_zalgiris_score * 100
    barcelona_percentage_error = barcelona_guess_difference / actual_barcelona_score * 100
    mean_percentage_error = (zalgiris_percentage_error + barcelona_percentage_error) / 2

    guess_accuracy = 100 - mean_percentage_error

    # Set the guess_accuracy field in the Totalizator model to the guess accuracy
    totalizator_instance.guess_accuracy = round(guess_accuracy, 3)
    totalizator_instance.save()
