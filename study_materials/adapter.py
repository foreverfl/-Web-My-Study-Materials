from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.models import EmailAddress
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logging.info("DefaultSocialAccountAdapter")

    def is_auto_signup_allowed(self, request, sociallogin):
        # sociallogin 객체를 이용해 이메일을 얻습니다.
        email = sociallogin.user.email

        # 이메일이 account_emailaddress 테이블에 있는지 확인합니다.
        # 존재한다면, is_auto_signup_allowed를 True로 설정하여 자동 회원가입을 허용합니다.
        if email:  # 이메일이 있는 경우에만 검사
            try:

                existing_email = EmailAddress.objects.get(email__iexact=email)
                if existing_email:
                    return True  # 자동 회원가입 허용
            except EmailAddress.DoesNotExist:
                pass  # 존재하지 않는 이메일이면 기본 로직을 따릅니다.

        # 기본 로직
        return super().is_auto_signup_allowed(request, sociallogin)
