from .models import Profile

def user_profile(request):
    if request.user.is_authenticated:
        # get or None if it doesn’t exist
        profile = getattr(request.user, 'profile', None)
    else:
        profile = None
    return {'profile': profile}
