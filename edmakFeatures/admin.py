from django.contrib import admin
from django.db import connection
from .models import (
    MainCourse,
    Profile,
    Course,
    CourseRequest,
    ChatMessage,
    Reply,
)

# Function to reset sequence for a given table
def reset_sequence(table_name):
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT setval(
                pg_get_serial_sequence('{table_name}', 'id'),
                COALESCE(MAX(id), 1),
                false
            );
        """)

# Custom admin classes with sequence resetting after deletion
class BaseAdmin(admin.ModelAdmin):
    """Base admin class with automatic sequence resetting after deletion."""
    def delete_queryset(self, request, queryset):
        super().delete_queryset(request, queryset)
        reset_sequence(self.model._meta.db_table)

@admin.register(MainCourse)
class MainCourseAdmin(BaseAdmin):
    list_display = ('id', 'name', 'description', 'thumbnail')

@admin.register(Course)
class CourseAdmin(BaseAdmin):
    list_display = ('id', 'courses', 'description', 'video', 'thumbnail', 'main_course')

@admin.register(Profile)
class ProfileAdmin(BaseAdmin):
    list_display = ('id', 'user', 'phone_number')

@admin.register(ChatMessage)
class ChatMessageAdmin(BaseAdmin):
    list_display = ('id', 'user', 'message', 'timestamp', 'reply_to')

@admin.register(Reply)
class ReplyAdmin(BaseAdmin):
    list_display = ('id', 'message', 'reply_text', 'user', 'timestamp')

# Register models without custom admin logic
admin.site.register(CourseRequest)
