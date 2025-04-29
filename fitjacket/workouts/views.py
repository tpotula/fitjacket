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
from django.contrib.auth.decorators import login_required
from django.shortcuts        import get_object_or_404
from django.utils           import timezone
from .models                import Reminder
from .forms                 import ReminderForm
from .reminder_manager import ReminderManager
from .models import WorkoutPlan
from .models import WorkoutPlanDay
from .ai_service import WorkoutAIService


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

    # Get user's active workout plan if exists
    active_plan = WorkoutPlan.objects.filter(
        user=request.user,
        is_active=True
    ).first()

    # Initialize AI service
    ai_service = WorkoutAIService()

    if request.method == 'POST':
        # Handle advancing to next day
        if 'advance_day' in request.POST and active_plan:
            # Get the current day's workout
            current_day = WorkoutPlanDay.objects.get(
                plan=active_plan,
                day_number=active_plan.current_day
            )
            
            # Log the completed workout
            WorkoutLog.objects.create(
                user=request.user,
                workout_type=current_day.workout_type,
                exercise_name=f"Day {active_plan.current_day} Workout",
                duration=current_day.duration,
                notes=current_day.notes,
                date=timezone.now().date()
            )
            
            # Check if there are more days in the plan
            next_day = WorkoutPlanDay.objects.filter(
                plan=active_plan,
                day_number=active_plan.current_day + 1
            ).first()
            
            if next_day:
                active_plan.current_day += 1
                active_plan.save()
            else:
                # Plan completed
                active_plan.is_active = False
                active_plan.save()
            
            return redirect('workouts:ai_recommendations')

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
                    'duration': current_day.duration,
                    'difficulty': user_level,
                    'exercises': current_day.exercises,
                    'progression': 'Complete all exercises with proper form'
                })
            except WorkoutPlanDay.DoesNotExist:
                # If the current day doesn't exist, mark the plan as inactive
                active_plan.is_active = False
                active_plan.save()
                active_plan = None

        # Generate additional workout variations using AI
        for _ in range(2):  # Generate 2 additional variations
            workout_variation = ai_service.generate_workout_variation(
                user_level=user_level,
                recent_workouts=recent_workouts,
                equipment=equipment
            )
            
            if workout_variation:
                recommendations.append(workout_variation)

        # If no recommendations were generated, create a default one
        if not recommendations:
            recommendations.append({
                'title': 'Full Body Workout',
                'description': 'A balanced workout targeting all major muscle groups.',
                'duration': 45,
                'difficulty': user_level,
                'exercises': [
                    {
                        'name': 'Push-ups',
                        'sets': 3,
                        'reps': '10-12',
                        'notes': 'Keep your core tight and maintain proper form'
                    },
                    {
                        'name': 'Squats',
                        'sets': 3,
                        'reps': '12-15',
                        'notes': 'Keep your back straight and knees aligned with toes'
                    },
                    {
                        'name': 'Plank',
                        'sets': 3,
                        'reps': '30 seconds',
                        'notes': 'Maintain a straight line from head to heels'
                    }
                ],
                'progression': 'Increase reps or duration by 10% each week'
            })
    else:
        recommendations = None

    context = {
        'recommendations': recommendations,
        'user_level': user_level,
        'recent_workouts': recent_workouts,
        'active_plan': active_plan,
        'dark_mode': request.COOKIES.get('darkMode') == 'true',
    }
    return render(request, 'workouts/ai_recommendations.html', context)
