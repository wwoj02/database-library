from .models import Users

def custom_user_context(request):
    user_id = request.session.get('user_id')
    user = None
    if user_id:
        try:
            user = Users.objects.get(user_id=user_id)
        except Users.DoesNotExist:
            pass
    return {'custom_user': user}