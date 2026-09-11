from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import (
    Student,
    Project,
    JobHistory,
    EducationHistory,
    Skill,
    Language,
    Activity,
    Course,
    Achievement,
    Interest,
    ContactMessage,
)
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    UserSerializer,
    NationalIdPhoneTokenSerializer,
    StudentFullProfileSerializer,
    StudentPersonalSerializer,
    ProjectSerializer,
    JobHistorySerializer,
    EducationHistorySerializer,
    SkillSerializer,
    LanguageSerializer,
    ActivitySerializer,
    CourseSerializer,
    AchievementSerializer,
    InterestSerializer,
    ContactMessageSerializer,
)

User = get_user_model()


# ==============================================================================
# 1. Authentication Views
# ==============================================================================
class NationalIdPhoneLoginView(TokenObtainPairView):
    """Issue JWT tokens when national ID and phone number match an active user."""

    serializer_class = NationalIdPhoneTokenSerializer


class CurrentUserView(APIView):
    """
    Get information about the currently authenticated user and linked student profile.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        student = getattr(user, 'student', None)
        return Response({
            "user": UserSerializer(user).data,
            "student_id": student.student_id if student else None,
            "headline": student.headline if student else None,
        })


# ==============================================================================
# 2. Unified Profile Views (Matching Frontend JSON Schema)
# ==============================================================================
class StudentProfileView(APIView):
    """
    Retrieve or update the full nested profile of the authenticated student.
    Returns data matching the exact frontend `DEFAULT_PROFILE` structure.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        student, _ = Student.objects.get_or_create(
            user=request.user,
            defaults={'student_id': str(request.user.id)}
        )
        serializer = StudentFullProfileSerializer(student)
        return Response(serializer.data)

    def patch(self, request):
        student = get_object_or_404(Student, user=request.user)
        data = request.data

        # 1. Update personal info if provided
        personal_data = data.get('personal', {})
        if personal_data:
            if 'title' in personal_data:
                student.headline = personal_data['title']
            if 'university' in personal_data:
                student.university = personal_data['university']
            if 'field' in personal_data:
                student.field_of_study = personal_data['field']
            if 'semester' in personal_data:
                student.semester = personal_data['semester']
            if 'birthDate' in personal_data:
                student.birth_date = personal_data['birthDate']
            if 'phone' in personal_data:
                student.phone = personal_data['phone']
            if 'city' in personal_data:
                student.city = personal_data['city']
            if 'linkedin' in personal_data:
                student.linkedin_url = personal_data['linkedin']
            if 'github' in personal_data:
                student.github_url = personal_data['github']
            if 'website' in personal_data:
                student.website_url = personal_data['website']
            if 'availability' in personal_data:
                student.availability = personal_data['availability']
            if 'about' in personal_data:
                student.about = personal_data['about']
            if 'fullName' in personal_data and personal_data['fullName']:
                parts = personal_data['fullName'].split(' ', 1)
                request.user.first_name = parts[0]
                request.user.last_name = parts[1] if len(parts) > 1 else ''
                request.user.save()
            student.save()

        # 2. Update interests if provided as a list of strings
        if 'interests' in data and isinstance(data['interests'], list):
            student.interests.all().delete()
            Interest.objects.bulk_create([
                Interest(student=student, name=item) for item in data['interests'] if str(item).strip()
            ])

        serializer = StudentFullProfileSerializer(student)
        return Response(serializer.data)

    def put(self, request):
        return self.patch(request)


class PublicStudentProfileView(APIView):
    """
    Public read-only view of a student profile by `student_id`.
    Allows sharing and viewing any student's resume/CV without authentication.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, student_id):
        student = get_object_or_404(Student, student_id=student_id)
        serializer = StudentFullProfileSerializer(student)
        return Response(serializer.data)


# ==============================================================================
# 3. Individual Resource ViewSets (REST CRUD)
# ==============================================================================
class BaseStudentItemViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet for student sub-items providing auto-filtering and auto-association.
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        student_id = self.request.query_params.get('student_id')
        if student_id:
            return qs.filter(student__student_id=student_id)
        if self.request.user.is_authenticated and hasattr(self.request.user, 'student'):
            return qs.filter(student=self.request.user.student)
        return qs

    def perform_create(self, serializer):
        student, _ = Student.objects.get_or_create(
            user=self.request.user,
            defaults={'student_id': str(self.request.user.id)}
        )
        serializer.save(student=student)


class ProjectViewSet(BaseStudentItemViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class JobHistoryViewSet(BaseStudentItemViewSet):
    queryset = JobHistory.objects.all()
    serializer_class = JobHistorySerializer


class EducationHistoryViewSet(BaseStudentItemViewSet):
    queryset = EducationHistory.objects.all()
    serializer_class = EducationHistorySerializer


class SkillViewSet(BaseStudentItemViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer


class LanguageViewSet(BaseStudentItemViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer


class ActivityViewSet(BaseStudentItemViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer


class CourseViewSet(BaseStudentItemViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class AchievementViewSet(BaseStudentItemViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer


class InterestViewSet(BaseStudentItemViewSet):
    queryset = Interest.objects.all()
    serializer_class = InterestSerializer


# ==============================================================================
# 4. Contact Message View
# ==============================================================================
class ContactMessageCreateView(generics.CreateAPIView):
    """
    Submit contact form message to a student.
    """
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        recipient_id = self.request.data.get('recipient_student_id')
        recipient = None
        if recipient_id:
            recipient = Student.objects.filter(student_id=recipient_id).first()
        serializer.save(recipient=recipient)
