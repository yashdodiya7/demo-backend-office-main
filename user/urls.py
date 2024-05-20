from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from . import views
from .views import ContactFormAPIView, UserPasswordResetEmailView, UserPasswordResetView

urlpatterns = [
    # simplejwt token urls
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # login register urls
    path('register', views.RegistrationView.as_view(), name='registration'),
    path('login', views.LoginView.as_view(), name="login"),
    path('data/<int:pk>', views.UserDataView.as_view(), name="user_data"),
    path('profile', views.UserProfileView.as_view(), name="user_profile"),
    path('userchoice', views.UserPreferenceAPIView.as_view(), name="user_preference"),
    path('aadharverify', views.AadharVerificationView.as_view(), name="aadhar_verify"),

    # Reset Password urls
    path('reset-password', UserPasswordResetEmailView.as_view(), name='user-reset-password-api-view'),
    path('reset-password/<uid>/<token>', UserPasswordResetView.as_view(),
         name='user-reset-password-uid-token-api-view'),

    # contact us page
    path('submit-contact-form/', ContactFormAPIView.as_view(), name='submit_contact_form'),

]
