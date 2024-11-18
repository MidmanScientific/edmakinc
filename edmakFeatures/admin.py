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

# Register models without custom admin logic
admin.site.register(CourseRequest)

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
class MainCourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'thumbnail')

    def delete_queryset(self, request, queryset):
        super().delete_queryset(request, queryset)
        reset_sequence(MainCourse._meta.db_table)

admin.site.register(MainCourse, MainCourseAdmin)

class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'courses', 'description', 'video', 'thumbnail', 'main_course')

    def delete_queryset(self, request, queryset):
        super().delete_queryset(request, queryset)
        reset_sequence(Course._meta.db_table)

admin.site.register(Course, CourseAdmin)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'phone_number')

    def delete_queryset(self, request, queryset):
        super().delete_queryset(request, queryset)
        reset_sequence(Profile._meta.db_table)

admin.site.register(Profile, ProfileAdmin)

class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'message', 'timestamp', 'reply_to')

    def delete_queryset(self, request, queryset):
        super().delete_queryset(request, queryset)
        reset_sequence(ChatMessage._meta.db_table)

admin.site.register(ChatMessage, ChatMessageAdmin)

class ReplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'reply_text', 'user', 'timestamp')

    def delete_queryset(self, request, queryset):
        super().delete_queryset(request, queryset)
        reset_sequence(Reply._meta.db_table)

admin.site.register(Reply, ReplyAdmin)
