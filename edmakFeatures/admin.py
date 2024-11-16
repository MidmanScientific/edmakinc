from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import MainCourse
from .models import Profile
from .models import Course
from .models import CourseRequest
from .models import ChatMessage
from .models import Reply
# Register your models here.
admin.site.register(Profile)
admin.site.register(CourseRequest)
admin.site.register(ChatMessage)
admin.site.register(Reply)
admin.site.register(MainCourse)
admin.site.register(Course)

