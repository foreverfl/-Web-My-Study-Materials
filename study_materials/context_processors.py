from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers import serialize
from .models import Category, Subscription


def common_context(request):
    # 현재 유저 카테고리
    current_user_categories = Category.objects.none()  # 빈 쿼리셋으로 초기화

    # 구독 중인 카테고리
    if request.user.is_authenticated:
        subscribed_categories = Category.objects.filter(
            subscribers__user=request.user,  # ForeignKey 역참조
            is_public=True
        )
    else:
        subscribed_categories = Category.objects.none()  # 빈 쿼리셋

    # 운영자 카테고리
    admin_categories = Category.objects.filter(
        user__is_superuser=True,
        is_public=True
    )

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
        'current_user_categories_json': current_user_categories_json,
        'subscribed_categories': subscribed_categories,
        'admin_categories': admin_categories,
        'subscription': subscription,

    }

    return context
