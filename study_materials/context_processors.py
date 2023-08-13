from .models import Category
from allauth.socialaccount.models import SocialAccount


def common_context(request):
    uid = "103090984604653702161"  # 운영자 uid
    show_buttons = False

    if request.user.is_authenticated:
        try:
            social_account = SocialAccount.objects.get(
                user=request.user, uid=uid)
            show_buttons = True
        except SocialAccount.DoesNotExist:
            pass

    categories = Category.objects.all()
    context = {
        'categories': categories,
        'show_buttons': show_buttons
    }

    return context
