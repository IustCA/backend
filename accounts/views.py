from django.db.models import Value, Q
from django.db.models.functions import Concat
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

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
    LoginTokenSerializer,
    NationalIdPhoneTokenSerializer,
    StudentFullProfileSerializer,
    StudentPersonalSerializer,
    StudentSearchItemSerializer,
    StudentSearchResponseSerializer,
    CurrentUserResponseSerializer,
    ChangePasswordSerializer,
    AccountUsernameUpdateSerializer,
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
@extend_schema(
    summary="ورود با شماره دانشجویی و کد ملی/رمز عبور",
    description="در ورود اول، نام کاربری همان شماره دانشجویی و رمز عبور همان کد ملی است. پس از تغییر رمز، با رمز جدید وارد شوید.",
    request=LoginTokenSerializer,
)
class LoginView(TokenObtainPairView):
    """Issue JWT tokens when username/student_id and password match an active user."""

    serializer_class = LoginTokenSerializer


NationalIdPhoneLoginView = LoginView


class CurrentUserView(APIView):
    """
    Get information about the currently authenticated user and linked student profile.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CurrentUserResponseSerializer

    @extend_schema(
        operation_id="accounts_current_user_retrieve",
        summary="اطلاعات کاربر و دانشجوی جاری",
        responses={200: CurrentUserResponseSerializer},
    )
    def get(self, request):
        user = request.user
        student = getattr(user, 'student', None)
        return Response({
            "id": student.id if student else user.id,
            "user": UserSerializer(user).data,
            "student_id": student.student_id if student else None,
            "headline": student.headline if student else None,
        })


class AccountUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AccountUsernameUpdateSerializer

    @extend_schema(
        operation_id="accounts_username_update",
        summary="تغییر نام کاربری",
        request=AccountUsernameUpdateSerializer,
        responses={200: UserSerializer},
    )
    def patch(self, request):
        user = request.user
        data = request.data
        username = data.get('username')
        if username and username != user.username:
            if User.objects.filter(username=username).exclude(id=user.id).exists():
                return Response({"detail": "این نام کاربری قبلاً استفاده شده است."}, status=status.HTTP_400_BAD_REQUEST)
            if len(username) < 3 or len(username) > 30:
                return Response({"detail": "نام کاربری باید بین ۳ تا ۳۰ کاراکتر باشد."}, status=status.HTTP_400_BAD_REQUEST)
            if not username.replace('_', '').replace('.', '').isalnum():
                return Response({"detail": "نام کاربری فقط می‌تواند شامل حروف، عدد، _ و . باشد."}, status=status.HTTP_400_BAD_REQUEST)
            user.username = username
            user.save()
        return Response(UserSerializer(user).data)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    @extend_schema(
        operation_id="accounts_change_password",
        summary="تغییر رمز عبور",
        description="تغییر رمز عبور اولیه (کد ملی) به رمز عبور دلخواه جدید.",
        request=ChangePasswordSerializer,
        responses={200: OpenApiTypes.OBJECT},
    )
    def post(self, request):
        user = request.user
        student = getattr(user, 'student', None)
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        if not old_password or not new_password:
            return Response({"detail": "رمز فعلی (کد ملی) و رمز جدید الزامی است."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if old_password is valid: matches active password or matches national_id if not changed yet
        is_valid = user.check_password(old_password)
        if not is_valid and student and student.national_id:
            if not user.has_usable_password() and student.national_id.strip() == old_password.strip():
                is_valid = True

        if not is_valid:
            return Response({"detail": "رمز فعلی (یا کد ملی) نادرست است."}, status=status.HTTP_400_BAD_REQUEST)
        if len(new_password) < 6:
            return Response({"detail": "رمز جدید باید حداقل ۶ کاراکتر باشد."}, status=status.HTTP_400_BAD_REQUEST)
        if len(new_password) > 128:
            return Response({"detail": "رمز جدید خیلی طولانی است."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"detail": "رمز عبور با موفقیت تغییر یافت. از این پس با رمز عبور جدید وارد شوید."})


# ==============================================================================
# 2. Unified Profile Views (Matching Frontend JSON Schema)
# ==============================================================================
class StudentProfileView(APIView):
    """
    Retrieve or update the full nested profile of the authenticated student.
    Returns data matching the exact frontend `DEFAULT_PROFILE` structure.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = StudentFullProfileSerializer

    @extend_schema(
        operation_id="accounts_profile_retrieve",
        summary="دریافت پروفایل کامل دانشجو",
        description="دریافت کل اطلاعات شخصی و رزومه دانشجو در یک شیء JSON یکپارچه.",
        responses={200: StudentFullProfileSerializer},
    )
    def get(self, request):
        student, _ = Student.objects.get_or_create(
            user=request.user,
            defaults={'student_id': str(request.user.id)}
        )
        serializer = StudentFullProfileSerializer(student, context={'request': request})
        return Response(serializer.data)

    @extend_schema(
        operation_id="accounts_profile_update",
        summary="ویرایش مشخصات شخصی و رزومه دانشجو",
        description="ویرایش مشخصات فردی و رزومه (فیلدهای دانشگاه، رشته و ترم توسط کاربر غیرقابل ویرایش است).",
        request=StudentFullProfileSerializer,
        responses={200: StudentFullProfileSerializer},
    )
    def patch(self, request):
        student = get_object_or_404(Student, user=request.user)
        data = request.data

        # 1. Update personal info if provided
        personal_data = data.get('personal', {})
        if personal_data:
            if 'title' in personal_data:
                student.headline = personal_data['title']
            # 'university', 'field' (field_of_study), 'entryYear', and 'gender' are read-only for students
            # and cannot be modified via profile updates (controlled by university/admin).
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
            # avatar handling - supports multipart file or base64/data-url
            # handle clear
            if 'avatar' in personal_data and personal_data['avatar'] == "":
                if student.avatar:
                    student.avatar.delete(save=False)
                    student.avatar = None
            # also check FILES for avatar
            if 'avatar' in request.FILES:
                student.avatar = request.FILES['avatar']
            elif 'avatar_file' in request.FILES:
                student.avatar = request.FILES['avatar_file']
            # handle base64 avatar sent as string
            elif personal_data.get('avatar') and isinstance(personal_data.get('avatar'), str) and personal_data.get('avatar').startswith('data:image'):
                try:
                    import base64, uuid
                    from django.core.files.base import ContentFile
                    header, b64data = personal_data['avatar'].split(',', 1)
                    ext = 'png'
                    if 'jpeg' in header or 'jpg' in header:
                        ext = 'jpg'
                    elif 'webp' in header:
                        ext = 'webp'
                    decoded = base64.b64decode(b64data)
                    student.avatar.save(f"avatar_{uuid.uuid4().hex[:8]}.{ext}", ContentFile(decoded), save=False)
                except Exception:
                    pass
            student.save()

        # 2. Update interests if provided as a list of strings
        if 'interests' in data and isinstance(data['interests'], list):
            student.interests.all().delete()
            Interest.objects.bulk_create([
                Interest(student=student, name=item) for item in data['interests'] if str(item).strip()
            ])

        serializer = StudentFullProfileSerializer(student, context={'request': request})
        return Response(serializer.data)

    @extend_schema(exclude=True)
    def put(self, request):
        return self.patch(request)


class PublicStudentProfileView(APIView):
    """
    Public read-only view of a student profile by primary key `id`.
    Allows sharing and viewing any student's resume/CV without authentication.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = StudentFullProfileSerializer

    @extend_schema(
        operation_id="accounts_public_profile_retrieve",
        summary="مشاهده عمومی پروفایل دانشجو با شناسه id",
        description="مشاهده رزومه کامل یک دانشجو بدون نیاز به احراز هویت با استفاده از شناسه id (یا شماره دانشجویی).",
        parameters=[
            OpenApiParameter('id', OpenApiTypes.STR, location=OpenApiParameter.PATH, description="شناسه دیتابیس دانشجو (id) یا شماره دانشجویی"),
        ],
        responses={200: StudentFullProfileSerializer},
    )
    def get(self, request, id):
        student = None
        if str(id).isdigit():
            student = Student.objects.filter(id=int(id)).first()
        if not student:
            # Fallback to student_id if not found by numeric id
            student = Student.objects.filter(student_id=str(id)).first()
        if not student:
            return Response({"detail": "پروفایل مورد نظر یافت نشد."}, status=status.HTTP_404_NOT_FOUND)
        serializer = StudentFullProfileSerializer(student, context={'request': request})
        return Response(serializer.data)


class StudentSearchView(APIView):
    """
    Search students by full_name with offset & limit pagination.
    Returns only: id, avatar, fullname, about.
    Requires authentication (JWT token).
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = StudentSearchResponseSerializer

    @extend_schema(
        operation_id="accounts_students_search",
        summary="جستجوی دانشجویان بر اساس نام کامل با صفحه‌بندی آفست (نیاز به توکن ورود)",
        description="جستجوی دانشجویان بر اساس نام کامل (full_name) به همراه offset و limit. دسترسی فقط برای کاربران لاگین‌شده با توکن مجاز است. خروجی فقط شامل id, avatar, fullname, about است.",
        parameters=[
            OpenApiParameter('full_name', OpenApiTypes.STR, location=OpenApiParameter.QUERY, description="جستجو بر اساس نام و نام خانوادگی"),
            OpenApiParameter('search', OpenApiTypes.STR, location=OpenApiParameter.QUERY, description="مستعار فیلد full_name"),
            OpenApiParameter('offset', OpenApiTypes.INT, location=OpenApiParameter.QUERY, description="اندیس شروع (آفست - پیش‌فرض 0)"),
            OpenApiParameter('limit', OpenApiTypes.INT, location=OpenApiParameter.QUERY, description="تعداد آیتم‌ها در هر صفحه (پیش‌فرض 10)"),
        ],
        responses={200: StudentSearchResponseSerializer},
    )
    def get(self, request):
        search_query = (
            request.query_params.get('full_name') or
            request.query_params.get('search') or
            request.query_params.get('q') or
            ''
        ).strip()

        # Parse offset & limit
        try:
            offset = max(0, int(request.query_params.get('offset', 0)))
        except (ValueError, TypeError):
            offset = 0

        try:
            limit = max(1, min(100, int(request.query_params.get('limit', 10))))
        except (ValueError, TypeError):
            limit = 10

        qs = Student.objects.select_related('user').filter(user__is_active=True).order_by('id')

        if search_query:
            qs = qs.annotate(
                full_name_concat=Concat('user__first_name', Value(' '), 'user__last_name')
            )
            # Match query against first_name, last_name, full_name_concat, or user__username
            query_filter = (
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(full_name_concat__icontains=search_query) |
                Q(user__username__icontains=search_query)
            )
            # Support search with multiple words (e.g. "علی رضایی")
            words = search_query.split()
            if len(words) > 1:
                word_q = Q()
                for w in words:
                    word_q &= (
                        Q(user__first_name__icontains=w) |
                        Q(user__last_name__icontains=w) |
                        Q(full_name_concat__icontains=w)
                    )
                query_filter |= word_q

            qs = qs.filter(query_filter).distinct()

        total_count = qs.count()
        page_items = qs[offset:offset + limit]

        serializer = StudentSearchItemSerializer(page_items, many=True, context={'request': request})
        return Response({
            "count": total_count,
            "offset": offset,
            "limit": limit,
            "results": serializer.data
        })



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
