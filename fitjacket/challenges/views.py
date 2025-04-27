from django.shortcuts               import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models                         import Challenge
from .forms                          import ChallengeForm


def is_staff(user):
    return user.is_staff


@login_required
@user_passes_test(is_staff)
def create_challenge(request):
    if request.method == 'POST':
        form = ChallengeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('challenges:list')
    else:
        form = ChallengeForm()

    return render(request, 'challenges/create.html', {
        'form': form
    })


@login_required
def challenge_list(request):
    all_challenges = Challenge.objects.all()
    joined         = request.user.profile.joined_challenges.all()
    return render(request, 'challenges/list.html', {
        'challenges': all_challenges,
        'joined':     joined,
    })


@login_required
def join_challenge(request, pk):
    ch = get_object_or_404(Challenge, pk=pk)
    request.user.profile.joined_challenges.add(ch)
    return redirect('challenges:list')