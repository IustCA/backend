from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    RegisterView,
    CurrentUserView,
    AccountUpdateView,
    ChangePasswordView,
    StudentProfileView,
    PublicStudentProfileView,
    ProjectViewSet,
    JobHistoryViewSet,
    EducationHistoryViewSet,
    SkillViewSet,
    LanguageViewSet,
    ActivityViewSet,
    CourseViewSet,
    AchievementViewSet,
    InterestViewSet,
    ContactMessageCreateView,
)

app_name = 'accounts'

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'experiences', JobHistoryViewSet, basename='experience')
router.register(r'educations', EducationHistoryViewSet, basename='education')
router.register(r'skills', SkillViewSet, basename='skill')
router.register(r'languages', LanguageViewSet, basename='language')
router.register(r'activities', ActivityViewSet, basename='activity')
router.register(r'certificates', CourseViewSet, basename='certificate')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'achievements', AchievementViewSet, basename='achievement')
router.register(r'interests', InterestViewSet, basename='interest')

urlpatterns = [
    # Auth endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', CurrentUserView.as_view(), name='current_user'),
    path('auth/username/', AccountUpdateView.as_view(), name='update_username'),
    path('auth/password/', ChangePasswordView.as_view(), name='change_password'),

    # Profile endpoints
    path('profile/', StudentProfileView.as_view(), name='profile'),
    path('profile/<str:student_id>/', PublicStudentProfileView.as_view(), name='public_profile'),

    # Contact modal endpoint
    path('contact/', ContactMessageCreateView.as_view(), name='contact'),

    # Sub-resource CRUD endpoints
    path('', include(router.urls)),
]
