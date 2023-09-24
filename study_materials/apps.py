import logging

from django.apps import AppConfig
from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.socialaccount.signals import pre_social_login

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StudyMaterialsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'study_materials'

    def ready(self):
        from django.contrib.auth.models import User
        from .models import Category, Classification, Data, Notice, Subscription, CategorySubscription

        @receiver(pre_social_login)
        def handle_social_login(sender, request, sociallogin, **kwargs):

            # 네이버, 카카오 이름 처리
            # 로그인 제공자 (google, naver 등)
            provider = sociallogin.account.provider

            if provider in ['naver', 'kakao']:
                user = sociallogin.user
                if provider == 'kakao':
                    # 카카오의 경우, 'nickname' 필드에서 이름 정보를 가져옵니다.
                    name = sociallogin.account.extra_data.get(
                        'properties', {}).get('nickname')
                else:
                    # 네이버의 경우, 'name' 필드에서 이름 정보를 가져옵니다.
                    name = sociallogin.account.extra_data.get('name')

                if name:
                    split_name = name.split(' ', 1)
                    if len(split_name) > 1:
                        # 띄어쓰기로 나뉘는 이름이 있다면 그대로 나누기
                        user.first_name = split_name[0]
                        user.last_name = split_name[1]
                        logger.info("First Name: %s, Last Name: %s",
                                    user.first_name, user.last_name)
                    else:
                        # 띄어쓰기가 없다면, 첫 글자를 성으로, 나머지를 이름으로 설정
                        user.last_name = name[0]
                        user.first_name = name[1:]
                        logger.info("First Name: %s, Last Name: %s",
                                    user.first_name, user.last_name)

        @receiver(post_save, sender=User)
        def subscribe_admin_categories(sender, instance, created, **kwargs):
            if created:  # 새로운 유저가 생성되었을 때
                admin_categories = Category.objects.filter(
                    user__is_superuser=True, is_public=True)
                for category in admin_categories:
                    CategorySubscription.objects.create(
                        user=instance, category=category)
