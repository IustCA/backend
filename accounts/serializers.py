from rest_framework import serializers
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
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('id',)


class NationalIdPhoneTokenSerializer(serializers.Serializer):
    national_id = serializers.CharField(max_length=10, write_only=True)
    phone_number = serializers.CharField(max_length=30, write_only=True)

    default_error_messages = {
        'no_active_account': 'کد ملی یا شماره تماس نادرست است.',
    }

    def validate(self, attrs):
        national_id = attrs['national_id'].strip()
        phone_number = attrs['phone_number'].strip()
        student = Student.objects.select_related('user').filter(
            national_id=national_id,
            phone=phone_number,
        ).first()

        if student is None or not student.user.is_active:
            self.fail('no_active_account')

        refresh = RefreshToken.for_user(student.user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


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
    fullName = serializers.SerializerMethodField()
    birthDate = serializers.CharField(source='birth_date', required=False, allow_blank=True)
    username = serializers.SerializerMethodField()
    title = serializers.CharField(source='headline', required=False, allow_blank=True)
    field = serializers.CharField(source='field_of_study', required=False, allow_blank=True)
    linkedin = serializers.CharField(source='linkedin_url', required=False, allow_blank=True)
    github = serializers.CharField(source='github_url', required=False, allow_blank=True)
    website = serializers.CharField(source='website_url', required=False, allow_blank=True)

    class Meta:
        model = Student
        fields = [
            'fullName',
            'username',
            'title',
            'university',
            'field',
            'semester',
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

    def get_fullName(self, obj):
        full_name = obj.user.get_full_name()
        return full_name if full_name else obj.user.username

    def get_username(self, obj):
        return obj.user.username


# ==============================================================================
# 4. Nested Full Profile Serializer (Matching Frontend DEFAULT_PROFILE)
# ==============================================================================
class StudentFullProfileSerializer(serializers.ModelSerializer):
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

    def get_interests(self, obj):
        return [interest.name for interest in obj.interests.all()]
