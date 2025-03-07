from django.contrib.auth import authenticate, login
from .models import Course, CourseRequest, Profile
from .utils import generate_presigned_url
from .utils import generate_presigned_url
import random
from django.contrib.auth.models import User
from .models import ChatMessage, Reply
from django.utils import timezone
import json
from .models import ChatMessage  # Change this line
from django.contrib.auth.decorators import login_required
from .models import User, Course
from django.contrib import messages
from django.contrib.auth import logout
from .utils import generate_presigned_url  # Import the function
from django.http import JsonResponse
from .utils import generate_presigned_url

from urllib.parse import urlparse
import requests
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from .models import MainCourse, Prices, CourseRequest
from decimal import Decimal


def homepage(request):
    # Fetch all main courses
    courses = MainCourse.objects.all()
    return render(request, 'homepage.html', {'courses': courses})


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        password1 = request.POST['password1']
        email = request.POST['email']
        phone_number = request.POST['phone_number']

        if password == password1:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email already exists')
                return redirect('register')
            elif Profile.objects.filter(phone_number=phone_number).exists():
                messages.info(request, 'Phone number already in use')
                return redirect('register')
            else:
                user = User.objects.create_user(username=username, password=password, email=email)
                Profile.objects.create(user=user, phone_number=phone_number)
                return redirect('login')
        else:
            messages.info(request, 'Password mismatch')
            return redirect('register')
    return render(request, 'register.html')


@login_required
def courses(request):
    main_courses = MainCourse.objects.all()
    courses_with_presigned_urls = []

    for main_course in main_courses:
        # Generate pre-signed URL for the thumbnail
        thumbnail_key = main_course.thumbnail.name  # Path in S3: 'main_courses/thumbnails/filename.jpg'
        presigned_url = generate_presigned_url(thumbnail_key)

        courses_with_presigned_urls.append({
            "id": main_course.id,
            "name": main_course.name,
            "description": main_course.description,
            "thumbnail_url": presigned_url,
        })

    return render(request, 'courses.html', {'main_courses': courses_with_presigned_urls})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import MainCourse, CourseRequest, Course
from django.contrib import messages
from django.utils import timezone
from django.http import Http404
import random

@login_required
def request_access(request, course_id):
    main_course = get_object_or_404(MainCourse, id=course_id)
    
    # Create a CourseRequest if it doesn't already exist
    course_request, created = CourseRequest.objects.get_or_create(user=request.user, main_course=main_course)
    
    if created:
        messages.info(request, 'Your request has been sent to the admin for approval.')
    else:
        messages.error(request, 'You already have access to this course or have a pending request.')
    
    return redirect('otp_entry')  # Redirecting to OTP entry page


# Function to generate a 6-digit OTP
def generate_otp():
    return str(random.randint(100000, 999999))

def approve_request(request, request_id):
    course_request = get_object_or_404(CourseRequest, id=request_id)

    if request.method == 'POST':
        # Generate OTP and save approval status
        otp = generate_otp()
        course_request.otp = otp
        course_request.otp_created_at = timezone.now()
        course_request.approved = True
        course_request.save()

        # Notify user and admin (add SMS logic if needed)
        messages.success(request, f"Course request for {course_request.user.username} has been approved, and OTP has been sent.")
        
        return redirect('admin_dashboard')
    
    return render(request, 'admin_dashboard.html', {'course_request': course_request})

@login_required
def otp_entry(request):
    try:
        # Get the latest approved course request for the logged-in user
        course_request = CourseRequest.objects.filter(user=request.user, approved=True).latest('otp_created_at')
    except CourseRequest.DoesNotExist:
        course_request = None

    # If a POST request, verify the OTP entered by the user
    if request.method == 'POST':
        otp_input = request.POST['otp']
        if course_request and course_request.is_otp_valid() and course_request.otp == otp_input:
            request.session['otp_verified'] = True  # Set session OTP verification
            return redirect('course_detail', course_id=course_request.main_course.id)
        else:
            messages.error(request, 'Invalid or expired OTP')
            return redirect('otp_entry')

    # Check if OTP is expired and if so, provide an option to request a new one
    otp_expired = course_request and not course_request.is_otp_valid()
    if otp_expired:
        messages.error(request, 'Your OTP has expired. Please request a new one.')

    otp = course_request.otp if course_request else ''
    return render(request, 'otp_entry.html', {
        'otp': otp,
        'expired': otp_expired,
        'request_new_otp_url': f"/request-new-otp/{course_request.id}/" if otp_expired and course_request else None
    })

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, MainCourse, CourseRequest
from .utils import generate_presigned_url  # Assuming you have a utility function for pre-signed URLs
@login_required
def course_detail(request, course_id):
    # Ensure the user has a valid OTP session
    if not request.session.get('otp_verified'):
        return redirect(f'/otp-entry/?next=/courses/{course_id}/')

    # Fetch the MainCourse associated with the OTP-verified request
    try:
        course_request = CourseRequest.objects.filter(user=request.user, approved=True).latest('otp_created_at')
    except CourseRequest.DoesNotExist:
        messages.error(request, "No approved course request found.")
        return redirect('courses')  # Redirect to the list of courses

    # Get the main course from the approved request
    main_course = course_request.main_course

    # Fetch all courses under the same MainCourse
    courses_under_main = Course.objects.filter(main_course=main_course)

    # Prepare data for rendering
    courses_with_presigned_urls = []
    for course in courses_under_main:
        # Generate pre-signed URLs for video and thumbnail
        thumbnail_key = course.thumbnail.name
        video_key = course.video.name

        thumbnail_url = generate_presigned_url(thumbnail_key)  # Generate pre-signed URL for thumbnail
        video_url = generate_presigned_url(video_key)  # Generate pre-signed URL for video

        courses_with_presigned_urls.append({
            "id": course.id,
            "name": course.courses,
            "description": course.description,
            "thumbnail_url": thumbnail_url,
            "video_url": video_url,
        })

    return render(request, 'course_detail.html', {
        'main_course': main_course,
        'courses': courses_with_presigned_urls,
    })


@login_required
def request_new_otp(request, course_request_id):
    course_request = get_object_or_404(CourseRequest, id=course_request_id, user=request.user)

    # Generate a new OTP
    course_request.otp = f"{random.randint(100000, 999999)}"  # Random 6-digit OTP
    course_request.otp_created_at = timezone.now()
    course_request.otp_expired = False
    course_request.save()

    
    return redirect('otp_entry')

def login_for_chat(request):
    next_url = request.GET.get('next', '/chat/')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect(next_url)  # Redirect directly to chat after login
        else:
            messages.error(request, 'Invalid login credentials for chat access')
    return render(request, 'login_chat.html', {'next': next_url})


@login_required(login_url='/login-chat/')
def chat(request):
    if request.method == "POST":
        message_data = json.loads(request.body)
        message_text = message_data.get("message")
        reply_to = message_data.get("reply_to")  # Capture reply_to if available
        
        if message_text:
            ChatMessage.objects.create(
                user=request.user, 
                message=message_text, 
                reply_to=ChatMessage.objects.get(id=reply_to) if reply_to else None
            )
            return JsonResponse({'status': 'Message sent successfully'})
    return render(request, 'chat.html')


def get_chat_messages(request):
    messages = ChatMessage.objects.all().order_by('timestamp')  # Adjust ordering as needed
    message_data = []

    for msg in messages:
        message_info = {
            'id': msg.id,
            'user': msg.user.username,  # Adjust this based on your User model
            'text': msg.message,  # Correctly using 'message' instead of 'text'
            'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'is_self': msg.user == request.user,  # Assuming request.user is available
        }

        # Include reply information if this message is a reply
        if msg.reply_to:
            message_info['reply_to'] = {
                'user': msg.reply_to.user.username,  # Username of the original message's user
                'text': msg.reply_to.message  # Correctly using 'message' for the replied message
            }

        message_data.append(message_info)

    return JsonResponse({'messages': message_data})


def user_login(request):
    next_url = request.GET.get('next')  # Capture the 'next' parameter from the URL if it exists
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            if next_url:  # Redirect to 'next' if it's set
                return redirect(next_url)
            else:
                return redirect('courses')  # Default to courses if no 'next' URL is specified
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    return render(request, 'login.html', {'next': next_url})


def admin_dashboard(request):
    # Fetch main courses and courses from the database
    main_courses = MainCourse.objects.all()
    courses = Course.objects.all()
    users = User.objects.all()  # Ensure User is imported
    pending_requests = CourseRequest.objects.filter(approved=False)
    context = {
        'main_courses': main_courses,
        'courses': courses,
        'users': users,
        'pending_requests': pending_requests,
    }
    return render(request, 'admin_dashboard.html', context)

def add_main_course(request):
    if request.method == 'POST':
        name = request.POST.get('main_course_name')
        description = request.POST.get('main_course_description')
        thumbnail = request.FILES.get('thumbnail')  # for file upload

        if name and description:  # check for valid input
            MainCourse.objects.create(name=name, description=description, thumbnail=thumbnail)
            messages.success(request, 'Main Course added successfully!')
        else:
            messages.error(request, 'Name and description are required.')
        
        return redirect('admin_dashboard')
    return redirect('admin_dashboard')


def upload_course(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        video = request.FILES.get('video')
        thumbnail = request.FILES.get('thumbnail')
        main_course_id = request.POST.get('main_course')
        main_course = MainCourse.objects.get(id=main_course_id)
        
        Course.objects.create(
            courses=name,
            description=description,
            video=video,
            thumbnail=thumbnail,
            main_course=main_course
        )
        messages.success(request, 'Course uploaded successfully!')
        return redirect('admin_dashboard')
    return redirect('admin_dashboard')

# Delete User View
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully.')
        return redirect('admin_dashboard')
    return render(request, 'delete_user.html', {'user': user})

# Edit Course View

def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        course.name = request.POST['name']
        course.description = request.POST['description']
        if 'video' in request.FILES:
            course.video = request.FILES['video']
        if 'thumbnail' in request.FILES:
            course.thumbnail = request.FILES['thumbnail']
        course.save()
        messages.success(request, 'Course updated successfully.')
        return redirect('admin_dashboard')
    return render(request, 'edit_course.html', {'course': course})

# Delete Course View

def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully.')
        return redirect('admin_dashboard')
    return render(request, 'delete_course.html', {'course': course})


# View for editing MainCourse
def edit_main_course(request, main_course_id):
    if request.method == 'POST':
        main_course = get_object_or_404(MainCourse, id=main_course_id)
        main_course.name = request.POST.get('main_course_name')
        main_course.description = request.POST.get('main_course_description')

        if 'thumbnail' in request.FILES:
            main_course.thumbnail = request.FILES['thumbnail']

        main_course.save()
        messages.success(request, 'Main course updated successfully.')
        return redirect('admin_dashboard')

# View for deleting MainCourse
def delete_main_course(request, main_course_id):
    main_course = get_object_or_404(MainCourse, id=main_course_id)
    main_course.delete()
    messages.success(request, 'Main course deleted successfully.')
    return redirect('admin_dashboard')


# Logout view
def logout_view(request):
    logout(request)
    return redirect('homepage')  # Redirect to the login page after logout


def get_course_content(request, file_key):
    """
    Serve course content using a pre-signed URL.
    """
    if request.user.is_authenticated:  # Ensure the user is logged in
        presigned_url = generate_presigned_url(file_key)
        if presigned_url:
            return JsonResponse({"url": presigned_url})
        else:
            return JsonResponse({"error": "Could not generate URL"}, status=500)
    return JsonResponse({"error": "Unauthorized"}, status=401)


def get_main_course_content(request, main_course_id):
    """
    Serve main course content using a pre-signed URL.
    """
    if request.user.is_authenticated:  # Ensure the user is logged in
        try:
            # Fetch the MainCourse object
            main_course = get_object_or_404(MainCourse, id=main_course_id)

            # Full URL of the thumbnail
            file_url = main_course.thumbnail.url  
            # Parse the URL to extract the object key
            parsed_url = urlparse(file_url)
            file_key = parsed_url.path.lstrip("/")  # Remove leading slash

            # Generate the pre-signed URL
            presigned_url = generate_presigned_url(file_key)

            if presigned_url:
                return JsonResponse({"url": presigned_url})
            else:
                return JsonResponse({"error": "Could not generate URL"}, status=500)

        except Exception as e:
            # Log the error for debugging
            print(f"Error generating pre-signed URL: {e}")
            return JsonResponse({"error": "Server error"}, status=500)
    return JsonResponse({"error": "Unauthorized"}, status=401)


def payment_page(request, course_id):
    """
    Render the payment page for a specific course.
    """
    course = get_object_or_404(MainCourse, id=course_id)
    # Safely access price, check if 'course.price' exists and has a 'price' attribute
    price = course.price.price if course.price and hasattr(course.price, 'price') else 0.00
    return render(request, 'payment_page.html', {'course': course, 'price': price})


def verify_payment(request):
    """
    Verify Paystack payment after the user completes the payment.
    """
    transaction_ref = request.GET.get('reference')
    if not transaction_ref:
        return JsonResponse({'success': False, 'message': 'Transaction reference is missing.'})

    # Set up headers for the Paystack API
    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',  # Ensure the Paystack secret key is set
    }
    url = f"https://api.paystack.co/transaction/verify/{transaction_ref}"

    response = requests.get(url, headers=headers)
    data = response.json()

    if data['status'] == 'success' and data['data']['status'] == 'success':
        # Payment was successful, process the payment
        course_id = data['data']['metadata']['course_id']  # Retrieve the course ID from metadata
        user = request.user

        try:
            # Mark the course request as approved
            course_request = CourseRequest.objects.get(user=user, course_id=course_id)
            course_request.approved = True
            course_request.save()
        except CourseRequest.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Course request not found.'})

        return JsonResponse({'success': True, 'message': 'Payment verified successfully!'})
    else:
        return JsonResponse({'success': False, 'message': 'Payment verification failed!'})



