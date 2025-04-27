from django.shortcuts import redirect
from .models import GuidedWorkout
from .forms import WorkoutLogForm
from django.shortcuts import render
from .models import WorkoutLog
from accounts.models import Profile
import datetime


def workouts_home_view(request):
    profile = None
    if request.user.is_authenticated:
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            profile = None  # or redirect to create profile if needed
    guided_workouts = GuidedWorkout.objects.all()

    show_custom_form = False
    if hasattr(request.user, 'profile') and request.user.profile.level == 'athlete':
        show_custom_form = True

    if request.method == 'POST':
        if 'guided_workout_id' in request.POST:
            workout_id = request.POST.get('guided_workout_id')
            guided = GuidedWorkout.objects.get(id=workout_id)
            WorkoutLog.objects.create(
                user=request.user,
                workout_type='cardio',  # default (later we can add smarter logic)
                exercise_name=guided.title,
                duration=guided.duration_minutes,
                notes=guided.description,
                date=request.POST.get('date') or datetime.date.today()
            )
            return redirect('workouts_home')
        else:
            form = WorkoutLogForm(request.POST)
            if form.is_valid():
                workout = form.save(commit=False)
                workout.user = request.user
                workout.save()
                return redirect('workouts_home')
    else:
        form = WorkoutLogForm()

    return render(request, 'workouts/workouts_home.html', {
        'guided_workouts': guided_workouts,
        'show_custom_form': show_custom_form,
        'form': form,
        'profile': profile,
    })

def guided_workouts_view(request):
    guided_workouts = GuidedWorkout.objects.all()
    return render(request, 'workouts/guided_workouts.html', {'guided_workouts': guided_workouts})

def log_workout_view(request):
    if request.method == 'POST':
        form = WorkoutLogForm(request.POST)
        if form.is_valid():
            workout = form.save(commit=False)
            workout.user = request.user
            workout.save()
            return redirect('workouts_home')
    else:
        form = WorkoutLogForm()
    return render(request, 'workouts/log_workout.html', {'form': form})

def workout_history_view(request):
    workouts = WorkoutLog.objects.filter(user=request.user).order_by('-date')
    return render(request, 'workouts/workout_log.html', {
        'workouts': workouts
    })

def workout_log_view(request):
    workouts = WorkoutLog.objects.filter(user=request.user).order_by('-date')
    context = {
        'workouts': workouts,
        'dark_mode': request.COOKIES.get('darkMode') == 'true',
    }
    return render(request, 'workouts/workout_log.html', context)
