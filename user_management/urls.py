from django.urls import path
from . import views

urlpatterns = [

    path('send_otp/', views.OtpVerificationView.as_view(),
         name='send_otp'),
    path('user_account/', views.UserAccountView.as_view(),
         name='user_account'),
    path('get_auth_token/', views.CreateTokenView.as_view(),
         name='get_auth_token'),
    path('registration_job/', views.RegistrationAndJobProfileView.as_view(),
         name='registration_job'),
    path('registration/', views.RegistrationProfileView.as_view(),
         name='registration'),
    path('jobs/', views.JobProfileView.as_view(),
         name='jobs'),
    path('profilepic_upload/', views.ProfilePicUploadView.as_view(),
         name='profilepic_upload'),
    path('country_code/', views.CountryCodeView.as_view(),
         name='country_code'),
    path('designations/', views.Designations.as_view(),
         name='designations'),
]
