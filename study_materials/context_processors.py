from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers import serialize
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

    current_user_categories_json = serialize('json', current_user_categories)
    context = {
        'current_user_categories': current_user_categories,
        'current_user_categories_json': current_user_categories_json,  # 자바스크립트에서 사용하기 위함
        'admin_categories': admin_categories,
        'subscription': subscription,
    }

    return context
