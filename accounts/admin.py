from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User,
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


class ProjectInline(admin.TabularInline):
    model = Project
    extra = 0


class JobHistoryInline(admin.TabularInline):
    model = JobHistory
    extra = 0


class EducationHistoryInline(admin.TabularInline):
    model = EducationHistory
    extra = 0


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 0


class LanguageInline(admin.TabularInline):
    model = Language
    extra = 0


class ActivityInline(admin.TabularInline):
    model = Activity
    extra = 0


class CourseInline(admin.TabularInline):
    model = Course
    extra = 0


class AchievementInline(admin.TabularInline):
    model = Achievement
    extra = 0


class InterestInline(admin.TabularInline):
    model = Interest
    extra = 0


class StudentInline(admin.StackedInline):
    model = Student
    can_delete = False
    verbose_name_plural = 'اطلاعات دانشجویی'
    fk_name = 'user'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (StudentInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'national_id', 'phone', 'user', 'headline', 'university', 'field_of_study', 'role', 'created_at')
    list_filter = ('role', 'availability', 'created_at')
    search_fields = ('student_id', 'national_id', 'phone', 'headline', 'university', 'user__username', 'user__first_name', 'user__last_name', 'user__email')
    ordering = ('-created_at',)
    inlines = [
        ProjectInline,
        JobHistoryInline,
        EducationHistoryInline,
        SkillInline,
        LanguageInline,
        ActivityInline,
        CourseInline,
        AchievementInline,
        InterestInline,
    ]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'category', 'team', 'start_date', 'end_date', 'created_at')
    list_filter = ('category', 'team', 'created_at')
    search_fields = ('title', 'description', 'student__student_id', 'student__user__username')


@admin.register(JobHistory)
class JobHistoryAdmin(admin.ModelAdmin):
    list_display = ('job_title', 'company', 'student', 'type', 'start_date', 'end_date', 'ongoing')
    list_filter = ('type', 'ongoing', 'created_at')
    search_fields = ('job_title', 'company', 'description', 'student__student_id')


@admin.register(EducationHistory)
class EducationHistoryAdmin(admin.ModelAdmin):
    list_display = ('degree', 'field', 'university', 'student', 'gpa', 'start_date', 'end_date', 'ongoing')
    search_fields = ('degree', 'field', 'university', 'student__student_id')


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'category', 'student', 'created_at')
    list_filter = ('category', 'level')
    search_fields = ('name', 'student__student_id', 'student__user__username')


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'student', 'created_at')
    list_filter = ('level',)
    search_fields = ('name', 'student__student_id', 'student__user__username')


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'role', 'student', 'date')
    search_fields = ('title', 'organization', 'role', 'student__student_id')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'issuer', 'student', 'date', 'credential_id')
    search_fields = ('name', 'issuer', 'credential_id', 'student__student_id')


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'student', 'date')
    list_filter = ('type',)
    search_fields = ('title', 'description', 'student__student_id')


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ('name', 'student', 'created_at')
    search_fields = ('name', 'student__student_id', 'student__user__username')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'recipient', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    ordering = ('-created_at',)
