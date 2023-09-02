from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from .models import Category, Subscription


def common_context(request):
    current_user_categories = Category.objects.none()  # 빈 쿼리셋으로 초기화+
    # __: 외래키 필드를 참조할 때 사용
    admin_categories = Category.objects.filter(user__is_superuser=True)

    subscription = None
    if request.user.is_authenticated:
        current_user_categories = Category.objects.filter(user=request.user)
        try:
            subscription = Subscription.objects.get(user=request.user)
        except ObjectDoesNotExist:
            subscription = None

    context = {
        'current_user_categories': current_user_categories,
        'admin_categories': admin_categories,
        'subcription': subscription,
    }

    return context
