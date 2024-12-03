from django.contrib import admin
from django.db import connection
from .models import (
    MainCourse,
    Profile,
    Course,
    CourseRequest,
    ChatMessage,
    Reply,
    Assignment,
    UserAssignmentCompletion,
    Prices
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

# Define Assignment Inline for Course
class AssignmentInline(admin.StackedInline):
    model = Assignment
    extra = 0  # No extra empty forms
    min_num = 0  # Allow zero assignments
    fields = ('question', 'options', 'correct_answer')
    verbose_name = 'Assignment'
    verbose_name_plural = 'Assignments'

# Updated CourseAdmin with AssignmentInline
@admin.register(Course)
class CourseAdmin(BaseAdmin):
    list_display = ('id', 'courses', 'description', 'video', 'thumbnail', 'main_course')
    inlines = [AssignmentInline]

@admin.register(Profile)
class ProfileAdmin(BaseAdmin):
    list_display = ('id', 'user', 'phone_number')

@admin.register(Prices)
class PricesAdmin(admin.ModelAdmin):
    list_display = ('main_course', 'price')
    search_fields = ('main_course__name',)

@admin.register(ChatMessage)
class ChatMessageAdmin(BaseAdmin):
    list_display = ('id', 'user', 'message', 'timestamp', 'reply_to')

@admin.register(Reply)
class ReplyAdmin(BaseAdmin):
    list_display = ('id', 'message', 'reply_text', 'user', 'timestamp')

# Register models without custom admin logic
admin.site.register(CourseRequest)

# Separate admin for Assignment and UserAssignmentCompletion
from django.contrib import admin
from django.db import models
from django.forms import Textarea
from .models import Assignment

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    # Display fields in the admin interface
    list_display = ('video', 'created_at')
    search_fields = ('video__title',)
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)
    
    # Organizing fields in the detail view
    fieldsets = (
        (None, {
            'fields': ('video', 'question', 'options', 'correct_answer')
        }),
    )
    
    # Customizing the input widget for JSON fields
    formfield_overrides = {
        models.JSONField: {'widget': Textarea(attrs={'rows': 5, 'cols': 50})},  # Larger input box
    }

@admin.register(UserAssignmentCompletion)
class UserAssignmentCompletionAdmin(admin.ModelAdmin):
    list_display = ('user', 'assignment', 'is_completed', 'submitted_at')
    search_fields = ('user__username', 'assignment__video__title')
    list_filter = ('is_completed', 'submitted_at')

