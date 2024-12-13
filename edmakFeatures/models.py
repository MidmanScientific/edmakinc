from django.db import models

# Create your models here.
# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, unique=True)

from django.db import models

class MainCourse(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='main_courses/thumbnails/')

    def __str__(self):
        return self.name

class Course(models.Model):
    courses = models.CharField(max_length=255)
    description = models.TextField()
    video = models.FileField(upload_to='videos/')
    thumbnail = models.ImageField(upload_to='thumbnails/')
    main_course = models.ForeignKey(MainCourse, on_delete=models.CASCADE, related_name="courses")

    def __str__(self):
        return self.courses


from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class CourseRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    main_course = models.ForeignKey(MainCourse, on_delete=models.CASCADE , null=True,blank =True)  # Linking to MainCourse
    approved = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)  # Timestamp for OTP generation
    otp_expired = models.BooleanField(default=False)  # Field to track expiration status

    def __str__(self):
        return f"{self.user.username} - {self.main_course} - OTP: {self.otp}"

    def is_otp_valid(self):
        """
        Checks if the OTP is still valid (within 7 days).
        """
        if self.otp_created_at:
            return timezone.now() < self.otp_created_at + timedelta(days=7) and not self.otp_expired
        return False  # No OTP set

    def expire_otp(self):
        """
        Manually expires the OTP by setting `otp_expired` to True.
        """
        self.otp_expired = True
        self.save()

    def approve_request(self):
        """
        Marks the request as approved and generates OTP.
        """
        self.approved = True
        self.otp = self.generate_otp()  # You will need a function to generate OTP
        self.otp_created_at = timezone.now()
        self.save()

    def generate_otp(self):
        """
        Generates a random 6-digit OTP.
        """
        import random
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        return otp




# models.py

from django.db import models
from django.contrib.auth.models import User

from django.db import models

class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()  # This should exist
    timestamp = models.DateTimeField(auto_now_add=True)
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)


class Reply(models.Model):
    message = models.ForeignKey(
        ChatMessage, 
        on_delete=models.CASCADE, 
        related_name='replies_in_reply_model'  # Ensures uniqueness
    )
    reply_text = models.TextField()  # Holds the reply content
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User

from django.db import models
from django.contrib.auth.models import User  # Adjust if using a custom user model

class Assignment(models.Model):
    video = models.OneToOneField('Course', on_delete=models.CASCADE, related_name='assignment',null=True,blank=True)
    question = models.TextField()
    options = models.JSONField()  # Store options as a JSON object
    correct_answer = models.JSONField()  # Store correct answer(s) as a JSON object
    created_at = models.DateTimeField(auto_now_add=True, null=True,blank=True)

    def __str__(self):
        return f"Assignment for {self.video.courses}"


class UserAssignmentCompletion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now=True,null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.assignment.video.title} - {'Completed' if self.is_completed else 'Not Completed'}"



class CourseProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="progress")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="user_progress")
    video = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="watched_videos")
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.course.title} Progress"


class Prices(models.Model):
    main_course = models.OneToOneField(MainCourse, on_delete=models.CASCADE, related_name="price", null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.main_course.name} - {self.price}"





