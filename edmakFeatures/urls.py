# urls.py


from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap, MainCourseSitemap, CourseSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'main_courses': MainCourseSitemap,
    'courses': CourseSitemap,
}

urlpatterns = [
    path('', views.homepage, name='homepage'),  # Homepage
    path('payment/<int:course_id>/', views.payment_page, name='course_payment'),
    path('register', views.register, name='register'),
    path('login', views.user_login, name='login'),
    path('courses', views.courses, name='courses'),
    path('admin-dashboard1912officials/', views.admin_dashboard, name='admin_dashboard'),
    path('chat/', views.chat, name='chat'),
    path('chat/get_messages/', views.get_chat_messages, name='get_chat_messages'),
    path('login-chat/', views.login_for_chat, name='login_chat'),
    path('upload-course/', views.upload_course, name='upload_course'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('edit_course/<int:course_id>/', views.edit_course, name='edit_course'),
    path('delete_course/<int:course_id>/', views.delete_course, name='delete_course'),
    path('request-new-otp/<int:course_request_id>/', views.request_new_otp, name='request_new_otp'),
    path('add-main-course/', views.add_main_course, name='add_main_course'),
    path('edit-main-course/<int:main_course_id>/', views.edit_main_course, name='edit_main_course'),
    path('delete-main-course/<int:main_course_id>/', views.delete_main_course, name='delete_main_course'),
    path('logout/', views.logout_view, name='logout'),
    path('get-course-content/<str:file_key>/', views.get_course_content, name='get_course_content'),
    path('get-main-course-content/<int:main_course_id>/', views.get_main_course_content, name='get_main_course_content'),
    path('verify-payment/', views.verify_payment, name='verify_payment'), 

    path('request-access/<int:course_id>/', views.request_access, name='request_access'),
    path('approve-request/<int:request_id>/', views.approve_request, name='approve_request'),
    path('otp-entry/', views.otp_entry, name='otp_entry'),
    path('course-detail/<int:course_id>/', views.course_detail, name='course_detail'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

]
 

#if settings.DEBUG:
 #   urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
