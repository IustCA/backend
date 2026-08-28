from rest_framework import serializers
from django.contrib.auth import get_user_model
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


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6, style={'input_type': 'password'})
    student_id = serializers.CharField(write_only=True, required=True)
    full_name = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'student_id', 'full_name', 'email')
        extra_kwargs = {
            'email': {'required': False, 'allow_blank': True}
        }

    def validate_student_id(self, value):
        if Student.objects.filter(student_id=value).exists():
            raise serializers.ValidationError("دانشجویی با این شماره دانشجویی قبلاً ثبت‌نام کرده است.")
        return value

    def create(self, validated_data):
        student_id = validated_data.pop('student_id')
        full_name = validated_data.pop('full_name', '')
        first_name = ''
        last_name = ''
        if full_name:
            parts = full_name.split(' ', 1)
            first_name = parts[0]
            last_name = parts[1] if len(parts) > 1 else ''

        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', ''),
            first_name=first_name,
            last_name=last_name
        )
        Student.objects.create(
            user=user,
            student_id=student_id
        )
        return user


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

    class Meta:
        model = Activity
        fields = [
            'id',
            'student',
            'title',
            'organization',
            'role',
            'date',
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
    studentId = serializers.CharField(source='student_id', read_only=True)
    title = serializers.CharField(source='headline', required=False, allow_blank=True)
    field = serializers.CharField(source='field_of_study', required=False, allow_blank=True)
    email = serializers.SerializerMethodField()
    linkedin = serializers.CharField(source='linkedin_url', required=False, allow_blank=True)
    github = serializers.CharField(source='github_url', required=False, allow_blank=True)
    website = serializers.CharField(source='website_url', required=False, allow_blank=True)

    class Meta:
        model = Student
        fields = [
            'fullName',
            'title',
            'university',
            'field',
            'semester',
            'birthDate',
            'studentId',
            'email',
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

    def get_email(self, obj):
        return obj.user.email or ''


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
