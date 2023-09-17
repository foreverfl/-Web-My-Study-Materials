from django.contrib.sitemaps import Sitemap
from django.contrib.sitemaps import ping_google
from django.urls import reverse
from .models import Data


class StudyMaterialsSitemap(Sitemap):
    protocol = 'https'

    def items(self):
        return Data.objects.all().order_by('id')

    def location(self, obj):
        return reverse('data_detail', args=[obj.classification.category.id, obj.classification.id, obj.id])

    def save(self, *args, **kwargs):
        super(Data, self).save(*args, **kwargs)  # 원래의 save 메소드 호출
        try:
            ping_google()  # Google에 핑 보내기
        except Exception:
            pass  # 오류가 발생해도 무시하고 계속 진행
