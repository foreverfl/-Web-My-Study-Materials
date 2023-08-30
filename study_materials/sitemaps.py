from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Data


class StudyMaterialsSitemap(Sitemap):
    protocol = 'https'

    def items(self):
        return Data.objects.all().order_by('id')

    def location(self, obj):
        return reverse('data_detail', args=[obj.classification.category.id, obj.classification.id, obj.id])
