from django.shortcuts import redirect
from .models import GuidedWorkout
from .forms import WorkoutLogForm
from django.shortcuts import render
from .models import WorkoutLog
from accounts.models import Profile
import datetime
from .models import Meal
from .forms import MealForm
from .models import Injury
from .forms import InjuryForm


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

def nutrition_tracking_view(request):
    if not request.user.is_authenticated:
        return redirect('auth_home')
    
    # Get the selected date from the request, default to today
    selected_date = request.GET.get('date')
    if selected_date:
        selected_date = datetime.datetime.strptime(selected_date, '%Y-%m-%d').date()
    else:
        selected_date = datetime.date.today()
    
    # Get meals for the selected date
    meals = Meal.objects.filter(user=request.user, date=selected_date).order_by('meal_type')
    
    # Group meals by type
    meals_by_type = {
        'breakfast': [],
        'lunch': [],
        'dinner': [],
        'snack': []
    }
    
    for meal in meals:
        meals_by_type[meal.meal_type].append(meal)
    
    # Calculate total calories
    total_calories = sum(meal.calories for meal in meals)
    
    context = {
        'meals_by_type': meals_by_type,
        'total_calories': total_calories,
        'selected_date': selected_date,
        'dark_mode': request.COOKIES.get('darkMode') == 'true',
    }
    return render(request, 'workouts/nutrition_tracking.html', context)

def add_meal_view(request):
    if not request.user.is_authenticated:
        return redirect('auth_home')
    
    # Get the date from the request, default to today
    meal_date = request.GET.get('date')
    if meal_date:
        meal_date = datetime.datetime.strptime(meal_date, '%Y-%m-%d').date()
    else:
        meal_date = datetime.date.today()
    
    if request.method == 'POST':
        form = MealForm(request.POST)
        if form.is_valid():
            meal = form.save(commit=False)
            meal.user = request.user
            meal.save()
            return redirect('nutrition_tracking')
    else:
        form = MealForm(initial={'date': meal_date})
    
    context = {
        'form': form,
        'dark_mode': request.COOKIES.get('darkMode') == 'true',
    }
    return render(request, 'workouts/add_meal.html', context)

def injury_log_view(request):
    if not request.user.is_authenticated:
        return redirect('auth_home')
    
    active_injuries = Injury.objects.filter(user=request.user, is_active=True).order_by('-date_logged')
    inactive_injuries = Injury.objects.filter(user=request.user, is_active=False).order_by('-date_logged')
    
    if request.method == 'POST':
        form = InjuryForm(request.POST)
        if form.is_valid():
            injury = form.save(commit=False)
            injury.user = request.user
            injury.save()
            return redirect('injury_log')
    else:
        form = InjuryForm()
    
    context = {
        'active_injuries': active_injuries,
        'inactive_injuries': inactive_injuries,
        'form': form,
        'dark_mode': request.COOKIES.get('darkMode') == 'true',
    }
    return render(request, 'workouts/injury_log.html', context)

def toggle_injury_status(request, injury_id):
    if not request.user.is_authenticated:
        return redirect('auth_home')
    
    try:
        injury = Injury.objects.get(id=injury_id, user=request.user)
        injury.is_active = not injury.is_active
        injury.save()
    except Injury.DoesNotExist:
        pass
    
    return redirect('injury_log')
