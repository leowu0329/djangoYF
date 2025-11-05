from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from users import views as user_views
from django.views.generic.base import TemplateView
from django.contrib.auth.views import LogoutView
from users.views import CustomLogoutView
from django.views.generic.base import RedirectView
from pages import views as pages_views

urlpatterns = [
    path('', RedirectView.as_view(url='cases/', permanent=True)), # Redirect root to /cases/
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    # AJAX endpoints without prefix (for compatibility)
    path('ajax/load-townships/', pages_views.load_townships, name='ajax_load_townships_root'),
    path('ajax/get-city-for-township/', pages_views.get_city_for_township, name='ajax_get_city_for_township_root'),
    path('cases/', include('pages.urls')), # Include pages.urls under /cases/
    
    # 認證URLs（包括內置的登入/登出）
    path('users/', include('django.contrib.auth.urls')),
    
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset_form.html',
             email_template_name='registration/password_reset_email.html',
             subject_template_name='registration/password_reset_subject.txt',
             success_url='done/'  # 明確指定成功後跳轉路徑
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html',
             success_url='/password-reset-complete/'  # 使用絕對路徑確保跳轉
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ),
         name='password_reset_complete'),
    
    # 密碼變更（需要登入）
    path('password-change/',
         auth_views.PasswordChangeView.as_view(
             template_name='registration/password_change_form.html',
             success_url='done/'  # 明確指定成功後跳轉路徑
         ),
         name='password_change'),
    path('password-change/done/',
         auth_views.PasswordChangeDoneView.as_view(
             template_name='registration/password_change_done.html'
         ),
         name='password_change_done'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
]
