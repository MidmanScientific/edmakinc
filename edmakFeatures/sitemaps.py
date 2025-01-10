from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import MainCourse, Course

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return ['homepage', 'courses', 'login', 'register']

    def location(self, item):
        return reverse(item)

class MainCourseSitemap(Sitemap):
    priority = 0.6
    changefreq = 'weekly'

    def items(self):
        # Add explicit ordering to avoid UnorderedObjectListWarning
        return MainCourse.objects.all().order_by('id')

    def lastmod(self, obj):
        return obj.updated_at if hasattr(obj, 'updated_at') else None

class CourseSitemap(Sitemap):
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        # Add explicit ordering to avoid UnorderedObjectListWarning
        return Course.objects.all().order_by('id')

    def lastmod(self, obj):
        return obj.updated_at if hasattr(obj, 'updated_at') else None
