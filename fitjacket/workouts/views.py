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
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts        import get_object_or_404
from django.utils           import timezone
from .models                import Reminder
from .forms                 import ReminderForm
from .reminder_manager import ReminderManager
from django.db.models import Avg, Count, Sum
from django.db.models.functions import ExtractWeek, ExtractMonth


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

@login_required
def reminders_view(request):
    reminder_manager = ReminderManager()
    
    if request.method == 'POST':
        form = ReminderForm(request.POST)
        print(f"Form data: {request.POST}")  # Debug
        if form.is_valid():
            print("Form is valid")  # Debug
            rem = form.save(commit=False)
            rem.user = request.user
            rem.save()
            print(f"Saved reminder: {rem}")  # Debug
            # Get next reminder through manager to trigger notification
            next_reminder = reminder_manager.get_next_reminder(request.user)
            print(f"Next reminder: {next_reminder}")  # Debug
            return redirect('workouts:reminders')
        else:
            print(f"Form errors: {form.errors}")  # Debug
    else:
        form = ReminderForm()

    upcoming = reminder_manager.get_all_reminders(request.user)
    print(f"Upcoming reminders: {list(upcoming)}")  # Debug

    context = {
        'form': form,
        'reminders': upcoming,
        'dark_mode': request.COOKIES.get('darkMode') == 'true',
    }
    return render(request, 'workouts/reminders.html', context)

@login_required
def complete_reminder(request, reminder_id):
    reminder_manager = ReminderManager()
    reminder_manager.mark_complete(reminder_id, request.user)
    return redirect('workouts:reminders')


def is_athlete(user):
    return hasattr(user, 'profile') and user.profile.level == 'athlete'


@login_required
@user_passes_test(is_athlete)
def performance_analytics_view(request):
    # Get the user's workout data
    workouts = WorkoutLog.objects.filter(user=request.user)

    # Calculate key metrics
    total_workouts = workouts.count()
    total_duration = workouts.aggregate(Sum('duration'))['duration__sum'] or 0
    avg_duration = workouts.aggregate(Avg('duration'))['duration__avg'] or 0

    # Weekly stats
    current_week = timezone.now().isocalendar()[1]
    weekly_workouts = workouts.filter(
        date__year=timezone.now().year
    ).annotate(
        week=ExtractWeek('date')
    ).values('week').annotate(
        count=Count('id'),
        total_duration=Sum('duration')
    ).order_by('-week')[:8]  # Last 8 weeks

    # Monthly progression
    monthly_workouts = workouts.filter(
        date__year=timezone.now().year
    ).annotate(
        month=ExtractMonth('date')
    ).values('month').annotate(
        count=Count('id'),
        total_duration=Sum('duration'),
        avg_duration=Avg('duration')
    ).order_by('month')

    # Workout type distribution
    workout_types = workouts.values('workout_type').annotate(
        count=Count('id')
    ).order_by('-count')

    context = {
        'total_workouts': total_workouts,
        'total_duration': total_duration,
        'avg_duration': round(avg_duration, 1) if avg_duration else 0,
        'weekly_workouts': weekly_workouts,
        'monthly_workouts': monthly_workouts,
        'workout_types': workout_types,
    }

    return render(request, 'workouts/performance_analytics.html', context)


@login_required
def ai_recommendations_view(request):
    # Get user's profile and workout history
    try:
        profile = Profile.objects.get(user=request.user)
        user_level = profile.level
    except Profile.DoesNotExist:
        user_level = 'beginner'  # Default to beginner if no profile exists

    # Get user's recent workout history
    recent_workouts = WorkoutLog.objects.filter(
        user=request.user
    ).order_by('-date')[:5]  # Get last 5 workouts

    if request.method == 'POST':
        # Check if this is a save workout request
        if 'save_workout' in request.POST:
            workout_data = request.POST.get('workout_data')
            if workout_data:
                # Create a new workout log entry
                WorkoutLog.objects.create(
                    user=request.user,
                    workout_type=request.POST.get('workout_type', 'strength'),
                    exercise_name=request.POST.get('workout_title'),
                    duration=request.POST.get('duration'),
                    notes=request.POST.get('workout_description'),
                    date=timezone.now().date()
                )
                return redirect('workouts:workout_log')

        # Get form data for recommendations
        workout_type = request.POST.get('workout_type')
        duration = request.POST.get('duration')
        difficulty = request.POST.get('difficulty')
        equipment = request.POST.getlist('equipment')

        # Generate recommendations based on user level
        recommendations = []

        # Beginner-focused recommendations
        if user_level == 'beginner':
            recommendations.extend([
                {
                    'title': 'Beginner Full Body Strength',
                    'description': 'A gentle introduction to strength training, perfect for beginners.',
                    'duration': 30,
                    'difficulty': 'Beginner',
                    'exercises': [
                        {'name': 'Bodyweight Squats', 'sets': 3, 'reps': '10-12'},
                        {'name': 'Push-ups (Knee)', 'sets': 3, 'reps': '8-10'},
                        {'name': 'Plank', 'sets': 3, 'reps': '20-30 seconds'},
                    ],
                    'progression': 'Increase reps by 2 each week'
                },
                {
                    'title': 'Beginner Cardio',
                    'description': 'Low-impact cardio workout to build endurance safely.',
                    'duration': 20,
                    'difficulty': 'Beginner',
                    'exercises': [
                        {'name': 'Walking', 'sets': 1, 'reps': '5 minutes'},
                        {'name': 'Light Jogging', 'sets': 1, 'reps': '2 minutes'},
                        {'name': 'Walking', 'sets': 1, 'reps': '5 minutes'},
                    ],
                    'progression': 'Increase jogging time by 1 minute weekly'
                }
            ])

        # Athlete-focused recommendations
        else:
            recommendations.extend([
                {
                    'title': 'Athlete Strength Training',
                    'description': 'Advanced strength training for athletes.',
                    'duration': 45,
                    'difficulty': 'Athlete',
                    'exercises': [
                        {'name': 'Push-ups', 'sets': 4, 'reps': '15-20'},
                        {'name': 'Squats', 'sets': 4, 'reps': '20-25'},
                        {'name': 'Plank', 'sets': 4, 'reps': '60 seconds'},
                    ],
                    'progression': 'Add 1 set each week'
                },
                {
                    'title': 'Athlete HIIT',
                    'description': 'High-intensity interval training for athletes.',
                    'duration': 30,
                    'difficulty': 'Athlete',
                    'exercises': [
                        {'name': 'Jumping Jacks', 'sets': 4, 'reps': '60 seconds'},
                        {'name': 'Mountain Climbers', 'sets': 4, 'reps': '45 seconds'},
                        {'name': 'Burpees', 'sets': 4, 'reps': '60 seconds'},
                    ],
                    'progression': 'Increase work intervals by 5 seconds weekly'
                }
            ])

        # Add variety based on workout history
        if recent_workouts:
            last_workout_type = recent_workouts[0].workout_type
            if last_workout_type == 'strength':
                recommendations.append({
                    'title': 'Active Recovery',
                    'description': 'Light workout to complement your strength training.',
                    'duration': 20,
                    'difficulty': 'Beginner',
                    'exercises': [
                        {'name': 'Light Stretching', 'sets': 1, 'reps': '5 minutes'},
                        {'name': 'Walking', 'sets': 1, 'reps': '10 minutes'},
                        {'name': 'Yoga Flow', 'sets': 1, 'reps': '5 minutes'},
                    ],
                    'progression': 'Gradually increase stretching duration'
                })
    else:
        recommendations = None

    context = {
        'recommendations': recommendations,
        'user_level': user_level,
        'recent_workouts': recent_workouts,
        'dark_mode': request.COOKIES.get('darkMode') == 'true',
    }
    return render(request, 'workouts/ai_recommendations.html', context)
