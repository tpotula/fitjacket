from django.shortcuts               import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils                   import timezone

from django.db.models               import Sum, Value, F
from django.db.models.functions     import Coalesce

from .models    import Challenge, Participation
from .forms     import ChallengeForm

from accounts.models import Profile


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
    all_challenges = Challenge.objects.all()
    participations = Participation.objects.filter(user=request.user, completed_at__isnull=True)
    joined_ids = participations.values_list('challenge_id', flat=True)
    completed_ids = Participation.objects.filter(user=request.user, completed_at__isnull=False).values_list('challenge_id', flat=True)
    return render(request, 'challenges/list.html', {
        'challenges': all_challenges,
        'joined': joined_ids,
        'participations': participations,
        'completed_ids': completed_ids,
    })

@login_required
def join_challenge(request, pk):
    Participation.objects.get_or_create(user=request.user, challenge_id=pk)
    return redirect('challenges:list')

@login_required
def complete_challenge(request, participation_id):
    p = get_object_or_404(Participation, id=participation_id, user=request.user, completed_at__isnull=True)
    if request.method == 'POST':
        p.completed_at = timezone.now()
        p.points_awarded = p.challenge.point_value
        p.save()
    return redirect('challenges:list')

@login_required
def leaderboard(request):
    # 1) Grab each user’s total challenge points
    ch_qs = (
        Participation.objects
        .filter(completed_at__isnull=False)
        .values('user__username')
        .annotate(challenge_points=Sum('points_awarded'))
    )

    # Build a dict: { username: {'challenge': X, 'workout': 0} }
    points = {
        row['user__username']: {
            'challenge': row['challenge_points'] or 0,
            'workout':   0
        }
        for row in ch_qs
    }

    # 2) Pull in each Profile’s workout‐earned points
    for prof in Profile.objects.select_related('user').all():
        u = prof.user.username
        # ensure entry exists
        if u not in points:
            points[u] = {'challenge': 0, 'workout': 0}
        points[u]['workout'] = prof.points or 0

    # 3) Flatten to a list and sort by total points desc
    ranking = []
    for user, pts in points.items():
        total = pts['challenge'] + pts['workout']
        ranking.append({
            'username': user,
            'points':   total
        })
    ranking.sort(key=lambda x: x['points'], reverse=True)

    # 4) Compute rank & progress bars
    top = ranking[0]['points'] if ranking else 0
    for idx, item in enumerate(ranking, start=1):
        item['rank']     = idx
        item['progress'] = int((item['points'] / top) * 100) if top else 0

    # 5) Highlight the current user
    current = next((r for r in ranking if r['username'] == request.user.username), None)

    return render(request, 'challenges/leaderboard.html', {
        'ranking': ranking,
        'current': current,
    })