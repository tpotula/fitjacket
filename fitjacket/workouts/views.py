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
from .models import WorkoutPlan
from .models import WorkoutPlanDay
from .ai_service import WorkoutAIService
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
            return redirect('workouts:workouts_home')
        else:
            form = WorkoutLogForm(request.POST)
            if form.is_valid():
                workout = form.save(commit=False)
                workout.user = request.user
                workout.save()
                return redirect('workouts:workouts_home')
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
            return redirect('workouts:workouts_home')
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
    # Get user's profile and recent workouts
    profile = get_object_or_404(Profile, user=request.user)
    recent_workouts = WorkoutLog.objects.filter(user=request.user).order_by('-date')[:5]
    
    # Get user's level and equipment
    user_level = profile.fitness_level
    equipment = profile.equipment_available
    
    # Initialize AI service
    ai_service = WorkoutAIService()
    
    # Get active workout plan if any
    active_plan = WorkoutPlan.objects.filter(user=request.user, is_active=True).first()
    
    # Generate recommendations using AI
    recommendations = []
    
    # If user is a beginner and doesn't have an active plan, create one
    if user_level == 'beginner' and not active_plan:
        # Create a new workout plan
        active_plan = WorkoutPlan.objects.create(
            user=request.user,
            plan_type='beginner',
            start_date=timezone.now().date(),
            current_day=1
        )
        
        # Generate a 7-day workout plan using AI
        for day in range(1, 8):
            workout_plan = ai_service.generate_workout_plan(
                user_level=user_level,
                recent_workouts=recent_workouts,
                equipment=equipment,
                duration=30,  # Default duration for beginners
                workout_type='strength' if day % 2 == 1 else 'cardio'
            )
            
            if workout_plan:
                # Create workout plan day
                WorkoutPlanDay.objects.create(
                    plan=active_plan,
                    day_number=day,
                    workout_type='strength' if day % 2 == 1 else 'cardio',  # Set workout type based on day
                    exercises=workout_plan['exercises'],
                    duration=workout_plan['duration'],
                    notes=workout_plan['description']
                )
    
    # Get current day's workout if there's an active plan
    if active_plan:
        try:
            current_day = WorkoutPlanDay.objects.get(
                plan=active_plan,
                day_number=active_plan.current_day
            )
            recommendations.append({
                'title': f'Day {active_plan.current_day} Workout',
                'description': current_day.notes,
                'type': 'workout_plan'
            })
        except WorkoutPlanDay.DoesNotExist:
            pass
    
    # Beginner-focused recommendations
    if user_level == 'beginner':
        if not recent_workouts:
            recommendations.append({
                'title': 'Start with Basic Exercises',
                'description': 'Begin with bodyweight exercises like push-ups, squats, and lunges.',
                'type': 'beginner_tip'
            })
        elif recent_workouts[0].workout_type == 'strength':
            recommendations.append({
                'title': 'Try Cardio',
                'description': 'Add some cardio to your routine for better overall fitness.',
                'type': 'workout_suggestion'
            })
    
    return render(request, 'workouts/ai_recommendations.html', {
        'recommendations': recommendations,
        'active_plan': active_plan
    })
