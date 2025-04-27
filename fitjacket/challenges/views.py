from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .models import Challenge, Participation
from .forms import ChallengeForm

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
    return render(request, 'challenges/create.html', {'form': form})

@login_required
def challenge_list(request):
    # Fetch all challenges
    all_challenges = Challenge.objects.all()

    # Participations joined but not completed
    participations = Participation.objects.filter(
        user=request.user,
        completed_at__isnull=True
    )
    joined_ids = participations.values_list('challenge_id', flat=True)

    # Participations that have been completed
    completed_ids = Participation.objects.filter(
        user=request.user,
        completed_at__isnull=False
    ).values_list('challenge_id', flat=True)

    return render(request, 'challenges/list.html', {
        'challenges':     all_challenges,
        'joined':         joined_ids,
        'participations': participations,
        'completed_ids':  completed_ids,
    })

@login_required
def join_challenge(request, pk):
    Participation.objects.get_or_create(
        user=request.user,
        challenge_id=pk
    )
    return redirect('challenges:list')

@login_required
def complete_challenge(request, participation_id):
    p = get_object_or_404(
        Participation,
        id=participation_id,
        user=request.user,
        completed_at__isnull=True
    )
    if request.method == 'POST':
        p.completed_at    = timezone.now()
        p.points_awarded  = p.challenge.point_value
        p.save()
    return redirect('challenges:list')


@login_required
def leaderboard(request):
    # 1. Sum points per user
    qs = (
        Participation.objects
        .filter(completed_at__isnull=False)
        .values('user__username')
        .annotate(total_points=Sum('points_awarded'))
        .order_by('-total_points')
    )

    top = qs[0]['total_points'] if qs else 0

    # 2. Build ranking list with progress%
    ranking = []
    for i, row in enumerate(qs, start=1):
        pts = row['total_points']
        ranking.append({
            'rank':     i,
            'username': row['user__username'],
            'points':   pts,
            'progress': int((pts / top) * 100) if top else 0,
        })

    # 3. Find current user’s entry (if any)
    current = next((r for r in ranking if r['username'] == request.user.username), None)

    return render(request, 'challenges/leaderboard.html', {
        'ranking': ranking,
        'current': current,
    })