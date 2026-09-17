from typing import List, Optional
from rest_framework import serializers
from django.db import models
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
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

User = get_user_model()


# ==============================================================================
# 1. Auth & User Serializers
# ==============================================================================
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'gender')
        read_only_fields = ('id', 'gender')


class LoginTokenSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True, help_text="شماره دانشجویی")
    password = serializers.CharField(write_only=True, help_text="کد ملی (یا رمز عبور جدید پس از تغییر)")

    default_error_messages = {
        'no_active_account': 'شماره دانشجویی یا رمز عبور (کد ملی) نادرست است.',
    }

    def validate(self, attrs):
        login_id = attrs['username'].strip()
        password = attrs['password'].strip()

        # 1. First find student by student_id (شماره دانشجویی)
        student = Student.objects.select_related('user').filter(student_id=login_id).first()
        if student:
            user = student.user
        else:
            # Fallback to User.username
            user = User.objects.filter(username__iexact=login_id).first()
            student = getattr(user, 'student', None) if user else None

        # 2. Verify user exists and is active
        if user is None or not user.is_active:
            self.fail('no_active_account')

        # 3. Check password:
        # A) Standard check: matches current password (including custom new password)
        password_valid = user.check_password(password)

        # B) Fallback if user doesn't have a usable password set yet: initial password is national_id
        if not password_valid and not user.has_usable_password() and student and student.national_id:
            if student.national_id.strip() == password:
                password_valid = True
                user.set_password(password)
                user.save(update_fields=['password'])

        if not password_valid:
            self.fail('no_active_account')

        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data,
        }


# Alias for backward compatibility
NationalIdPhoneTokenSerializer = LoginTokenSerializer


# ==============================================================================
# 2. Individual Sub-Resource Serializers
# ==============================================================================
class ProjectSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    student = serializers.PrimaryKeyRelatedField(read_only=True)
    startDate = serializers.CharField(source='start_date', required=False, allow_blank=True)
    endDate = serializers.CharField(source='end_date', required=False, allow_blank=True)

    class Meta:
        model = Project
        fields = [
            'id',
            'student',
            'title',
            'description',
            'technologies',
            'category',
            'startDate',
            'endDate',
            'ongoing',
            'github',
            'demo',
            'image',
            'team',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'student', 'created_at', 'updated_at']


class JobHistorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    student = serializers.PrimaryKeyRelatedField(read_only=True)
    jobTitle = serializers.CharField(source='job_title')
    startDate = serializers.CharField(source='start_date', required=False, allow_blank=True)
    endDate = serializers.CharField(source='end_date', required=False, allow_blank=True)
    skillsUsed = serializers.ListField(source='skills_used', required=False, child=serializers.CharField())

    class Meta:
        model = JobHistory
        fields = [
            'id',
            'student',
            'jobTitle',
            'company',
            'type',
            'startDate',
            'endDate',
            'ongoing',
            'location',
            'description',
            'responsibilities',
            'skillsUsed',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'student', 'created_at', 'updated_at']


class EducationHistorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    student = serializers.PrimaryKeyRelatedField(read_only=True)
    startDate = serializers.CharField(source='start_date', required=False, allow_blank=True)
    endDate = serializers.CharField(source='end_date', required=False, allow_blank=True)

    class Meta:
        model = EducationHistory
        fields = [
            'id',
            'student',
            'degree',
            'field',
            'university',
            'startDate',
            'endDate',
            'ongoing',
            'gpa',
            'description',
            'courses',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'student', 'created_at', 'updated_at']


class SkillSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    student = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Skill
        fields = ['id', 'student', 'name', 'level', 'category', 'created_at']
        read_only_fields = ['id', 'student', 'created_at']


class LanguageSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    student = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Language
        fields = ['id', 'student', 'name', 'level', 'created_at']
        read_only_fields = ['id', 'student', 'created_at']


class ActivitySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    student = serializers.PrimaryKeyRelatedField(read_only=True)
    startDate = serializers.CharField(source='start_date', required=False, allow_blank=True)
    endDate = serializers.CharField(source='end_date', required=False, allow_blank=True)

    class Meta:
        model = Activity
        fields = [
            'id',
            'student',
            'title',
            'organization',
            'role',
            'date',
            'startDate',
            'endDate',
            'ongoing',
            'description',
            'achievements',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'student', 'created_at', 'updated_at']


class CourseSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    student = serializers.PrimaryKeyRelatedField(read_only=True)
    credentialId = serializers.CharField(source='credential_id', required=False, allow_blank=True)

    class Meta:
        model = Course
        fields = [
            'id',
            'student',
            'name',
            'issuer',
            'date',
            'credentialId',
            'link',
            'description',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'student', 'created_at', 'updated_at']


class AchievementSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    student = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Achievement
        fields = ['id', 'student', 'title', 'type', 'date', 'description', 'created_at']
        read_only_fields = ['id', 'student', 'created_at']


class InterestSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    student = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Interest
        fields = ['id', 'student', 'name', 'created_at']
        read_only_fields = ['id', 'student', 'created_at']


class ContactMessageSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = ContactMessage
        fields = ['id', 'recipient', 'name', 'email', 'subject', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']


# ==============================================================================
# 3. Student Personal Serializer (Frontend Personal Section)
# ==============================================================================
class StudentPersonalSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    studentId = serializers.CharField(source='student_id', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    fullName = serializers.SerializerMethodField()
    gender = serializers.CharField(source='user.gender', read_only=True)
    birthDate = serializers.CharField(source='birth_date', required=False, allow_blank=True)
    username = serializers.SerializerMethodField()
    title = serializers.CharField(source='headline', required=False, allow_blank=True)
    field = serializers.CharField(source='field_of_study', read_only=True)
    entryYear = serializers.CharField(source='entry_year', read_only=True)
    linkedin = serializers.CharField(source='linkedin_url', required=False, allow_blank=True)
    github = serializers.CharField(source='github_url', required=False, allow_blank=True)
    website = serializers.CharField(source='website_url', required=False, allow_blank=True)

    class Meta:
        model = Student
        fields = [
            'id',
            'studentId',
            'email',
            'fullName',
            'username',
            'gender',
            'title',
            'university',
            'field',
            'entryYear',
            'role',
            'birthDate',
            'phone',
            'city',
            'linkedin',
            'github',
            'website',
            'availability',
            'about',
            'avatar',
        ]
        read_only_fields = ['university', 'entryYear', 'role', 'gender']

    def get_fullName(self, obj) -> str:
        return obj.user.get_full_name().strip()

    def get_username(self, obj) -> str:
        return obj.user.username


# ==============================================================================
# 4. Nested Full Profile Serializer (Matching Frontend DEFAULT_PROFILE)
# ==============================================================================
class StudentFullProfileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    personal = StudentPersonalSerializer(source='*')
    skills = SkillSerializer(many=True, read_only=True)
    education = EducationHistorySerializer(source='education_histories', many=True, read_only=True)
    experiences = JobHistorySerializer(source='job_histories', many=True, read_only=True)
    activities = ActivitySerializer(many=True, read_only=True)
    projects = ProjectSerializer(many=True, read_only=True)
    certificates = CourseSerializer(source='courses', many=True, read_only=True)
    achievements = AchievementSerializer(many=True, read_only=True)
    languages = LanguageSerializer(many=True, read_only=True)
    interests = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'id',
            'personal',
            'skills',
            'education',
            'experiences',
            'activities',
            'projects',
            'certificates',
            'achievements',
            'languages',
            'interests',
        ]

    def get_interests(self, obj) -> List[str]:
        return [interest.name for interest in obj.interests.all()]


# ==============================================================================
# 5. Lightweight Search Serializer (Only: id, avatar, fullname, about)
# ==============================================================================
class StudentSearchItemSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ['id', 'avatar', 'fullname', 'about']

    def get_fullname(self, obj) -> str:
        return obj.user.get_full_name().strip()

    def get_avatar(self, obj) -> Optional[str]:
        if not obj.avatar:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.avatar.url)
        return obj.avatar.url


# ==============================================================================
# 6. Additional Request / Response Serializers for Swagger Documentation
# ==============================================================================
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True, help_text="کد ملی اولیه یا رمز فعلی")
    new_password = serializers.CharField(required=True, write_only=True, min_length=6, help_text="رمز عبور جدید دلخواه")


class StudentSearchResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField(help_text="تعداد کل نتایج یافت‌شده")
    offset = serializers.IntegerField(help_text="اندیس شروع")
    limit = serializers.IntegerField(help_text="تعداد آیتم‌ها در صفحه")
    results = StudentSearchItemSerializer(many=True)


class CurrentUserResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text="شناسه دیتابیس دانشجو")
    user = UserSerializer()
    student_id = serializers.CharField(allow_null=True, help_text="شماره دانشجویی")
    headline = serializers.CharField(allow_null=True)


class AccountUsernameUpdateSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, min_length=3, max_length=30)


