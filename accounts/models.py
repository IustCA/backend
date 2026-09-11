from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


# ==============================================================================
# 1. User Model
# ==============================================================================
class User(AbstractUser):
    """
    Custom User model inheriting from Django's AbstractUser.
    Includes username, password, email (optional), first_name, last_name.
    """
    email = models.EmailField(unique=True, blank=True, null=True, verbose_name="ایمیل")

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"
        db_table = "users"

    def __str__(self):
        full_name = self.get_full_name()
        return full_name if full_name else self.username


# ==============================================================================
# 2. Student Profile Model
# ==============================================================================
class EducationRole(models.TextChoices):
    BACHELOR = 'bachelor', 'کارشناسی'
    MASTER = 'master', 'کارشناسی ارشد'
    PHD = 'phd', 'دکتری'
    ALUMNI = 'alumni', 'فارغ‌التحصیل'
    FACULTY = 'faculty', 'هیئت علمی / استاد'
    OTHER = 'other', 'سایر'


class AvailabilityStatus(models.TextChoices):
    AVAILABLE = 'available', 'آماده همکاری'
    INTERNSHIP = 'internship', 'آماده کارآموزی'
    STUDENT_PROJECTS = 'student_projects', 'فقط پروژه‌های دانشجویی'
    UNAVAILABLE = 'unavailable', 'در حال حاضر در دسترس نیستم'


class Student(models.Model):
    """
    Student profile model linked 1:1 with User.
    Contains personal info matching frontend personal header & about section.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student',
        verbose_name="کاربر"
    )
    student_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="شماره دانشجویی",
        help_text="شماره دانشجویی یکتا"
    )
    national_id = models.CharField(
        max_length=10,
        unique=True,
        blank=True,
        null=True,
        verbose_name="کد ملی",
        help_text="کد ملی یکتا برای ورود کاربر",
    )
    headline = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="عنوان حرفه‌ای / بیو کوتاه",
        help_text="مثلاً: دانشجوی مهندسی کامپیوتر و توسعه‌دهنده فرانت‌اند"
    )
    university = models.CharField(
        max_length=150,
        blank=True,
        default="دانشگاه علم و صنعت ایران",
        verbose_name="دانشگاه / موسسه"
    )
    field_of_study = models.CharField(
        max_length=150,
        blank=True,
        default="مهندسی کامپیوتر",
        verbose_name="رشته تحصیلی"
    )
    semester = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="ترم تحصیلی",
        help_text="مثلاً: ترم ششم"
    )
    role = models.CharField(
        max_length=50,
        choices=EducationRole.choices,
        default=EducationRole.BACHELOR,
        verbose_name="مقطع تحصیلی"
    )
    phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="شماره تماس",
        help_text="شماره تماس مورد استفاده برای ورود",
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="شهر / استان",
        help_text="مثلاً: تهران، ایران"
    )
    address = models.TextField(
        blank=True,
        verbose_name="آدرس کامل"
    )
    birth_date = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="تاریخ تولد",
        help_text="مثلاً: ۱۳۸۲/۰۵/۱۴"
    )
    linkedin_url = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="لینکدین"
    )
    github_url = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="گیت‌هاب"
    )
    website_url = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="وب‌سایت شخصی"
    )
    availability = models.CharField(
        max_length=50,
        choices=AvailabilityStatus.choices,
        default=AvailabilityStatus.AVAILABLE,
        verbose_name="وضعیت در دسترس بودن"
    )
    about = models.TextField(
        blank=True,
        verbose_name="درباره من / بیوگرافی"
    )
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/',
        blank=True,
        null=True,
        verbose_name="تصویر پروفایل"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ بروزرسانی"
    )

    class Meta:
        verbose_name = "دانشجو"
        verbose_name_plural = "دانشجویان"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.student_id})"


# ==============================================================================
# 3. Project Model (1:N with Student)
# ==============================================================================
class ProjectCategory(models.TextChoices):
    ACADEMIC = 'دانشگاهی', 'دانشگاهی'
    PERSONAL = 'شخصی', 'شخصی'
    TEAM = 'تیمی', 'تیمی'
    RESEARCH = 'پژوهشی', 'پژوهشی'
    OPEN_SOURCE = 'متن‌باز', 'متن‌باز'


class Project(models.Model):
    """
    Student portfolio projects matching ProjectForm.
    """
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='projects',
        verbose_name="دانشجو"
    )
    title = models.CharField(
        max_length=200,
        verbose_name="عنوان پروژه"
    )
    description = models.TextField(
        verbose_name="توضیحات پروژه"
    )
    technologies = models.JSONField(
        default=list,
        blank=True,
        verbose_name="فناوری‌های استفاده‌شده",
        help_text="لیست نام فناوری‌ها مثل ['React', 'TypeScript', 'Node.js']"
    )
    category = models.CharField(
        max_length=50,
        choices=ProjectCategory.choices,
        default=ProjectCategory.PERSONAL,
        verbose_name="دسته‌بندی پروژه"
    )
    start_date = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="تاریخ شروع",
        help_text="مثلاً: فروردین ۱۴۰۳"
    )
    end_date = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="تاریخ پایان",
        help_text="مثلاً: دی ۱۴۰۳ یا خالی"
    )
    github = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="لینک گیت‌هاب"
    )
    demo = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="لینک دمو"
    )
    image = models.TextField(
        blank=True,
        verbose_name="تصویر / پیش‌نمایش پروژه"
    )
    team = models.CharField(
        max_length=20,
        default='فردی',
        verbose_name="نوع تیم (فردی / تیمی)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ بروزرسانی"
    )

    class Meta:
        verbose_name = "پروژه"
        verbose_name_plural = "پروژه‌ها"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.student}"


# ==============================================================================
# 4. Job History / Experience Model (1:N with Student)
# ==============================================================================
class EmploymentType(models.TextChoices):
    FULL_TIME = 'تمام‌وقت', 'تمام‌وقت'
    PART_TIME = 'پاره‌وقت', 'پاره‌وقت'
    INTERNSHIP = 'کارآموزی', 'کارآموزی'
    PROJECT = 'پروژه‌ای', 'پروژه‌ای'
    REMOTE = 'دورکاری', 'دورکاری'
    VOLUNTEER = 'داوطلبانه', 'داوطلبانه'


class JobHistory(models.Model):
    """
    Work experiences and job history matching ExperienceForm.
    """
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='job_histories',
        verbose_name="دانشجو"
    )
    job_title = models.CharField(
        max_length=200,
        verbose_name="عنوان شغلی"
    )
    company = models.CharField(
        max_length=200,
        verbose_name="نام شرکت یا سازمان"
    )
    type = models.CharField(
        max_length=50,
        choices=EmploymentType.choices,
        default=EmploymentType.INTERNSHIP,
        verbose_name="نوع همکاری"
    )
    start_date = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="تاریخ شروع",
        help_text="مثلاً: تیر ۱۴۰۳"
    )
    end_date = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="تاریخ پایان",
        help_text="مثلاً: اسفند ۱۴۰۳"
    )
    ongoing = models.BooleanField(
        default=False,
        verbose_name="هم‌اکنون مشغول به کار هستم"
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="محل کار / شهر"
    )
    description = models.TextField(
        blank=True,
        verbose_name="شرح فعالیت و دستاوردها"
    )
    responsibilities = models.JSONField(
        default=list,
        blank=True,
        verbose_name="مسئولیت‌ها و وظایف"
    )
    skills_used = models.JSONField(
        default=list,
        blank=True,
        verbose_name="مهارت‌های به‌کاررفته"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ بروزرسانی"
    )

    class Meta:
        verbose_name = "سابقه کاری"
        verbose_name_plural = "سوابق کاری"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.job_title} در {self.company} - {self.student}"


# ==============================================================================
# 5. Education History Model (1:N with Student)
# ==============================================================================
class EducationHistory(models.Model):
    """
    Academic education background matching EducationForm.
    """
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='education_histories',
        verbose_name="دانشجو"
    )
    degree = models.CharField(
        max_length=100,
        verbose_name="مقطع تحصیلی",
        help_text="مثلاً: کارشناسی، دیپلم، کارشناسی ارشد"
    )
    field = models.CharField(
        max_length=150,
        verbose_name="رشته تحصیلی",
        help_text="مثلاً: مهندسی کامپیوتر"
    )
    university = models.CharField(
        max_length=200,
        verbose_name="نام دانشگاه یا مؤسسه"
    )
    start_date = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="تاریخ شروع",
        help_text="مثلاً: مهر ۱۴۰۱"
    )
    end_date = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="تاریخ پایان"
    )
    ongoing = models.BooleanField(
        default=False,
        verbose_name="در حال تحصیل"
    )
    gpa = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="معدل"
    )
    description = models.TextField(
        blank=True,
        verbose_name="توضیحات"
    )
    courses = models.JSONField(
        default=list,
        blank=True,
        verbose_name="دروس کلیدی و مرتبط",
        help_text="مثلاً: ['ساختمان داده', 'پایگاه داده‌ها']"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ بروزرسانی"
    )

    class Meta:
        verbose_name = "سابقه تحصیلی"
        verbose_name_plural = "سوابق تحصیلی"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.degree} {self.field} ({self.university}) - {self.student}"


# ==============================================================================
# 6. Skills Model (1:N with Student)
# ==============================================================================
class SkillCategory(models.TextChoices):
    TECHNICAL = 'مهارت‌های فنی', 'مهارت‌های فنی'
    PROGRAMMING_LANGUAGES = 'زبان‌های برنامه‌نویسی', 'زبان‌های برنامه‌نویسی'
    TOOLS = 'ابزارها و نرم‌افزارها', 'ابزارها و نرم‌افزارها'
    SOFT_SKILLS = 'مهارت‌های نرم', 'مهارت‌های نرم'


class SkillLevel(models.TextChoices):
    BEGINNER = 'مقدماتی', 'مقدماتی'
    INTERMEDIATE = 'متوسط', 'متوسط'
    ADVANCED = 'پیشرفته', 'پیشرفته'
    EXPERT = 'حرفه‌ای', 'حرفه‌ای'


class Skill(models.Model):
    """
    Skills acquired by student matching SkillForm.
    """
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='skills',
        verbose_name="دانشجو"
    )
    name = models.CharField(
        max_length=150,
        verbose_name="نام مهارت"
    )
    level = models.CharField(
        max_length=50,
        choices=SkillLevel.choices,
        default=SkillLevel.INTERMEDIATE,
        verbose_name="سطح تسلط"
    )
    category = models.CharField(
        max_length=100,
        choices=SkillCategory.choices,
        default=SkillCategory.TECHNICAL,
        verbose_name="دسته‌بندی مهارت"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )

    class Meta:
        verbose_name = "مهارت"
        verbose_name_plural = "مهارت‌ها"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.level}) - {self.student}"


# ==============================================================================
# 7. Language Model (1:N with Student)
# ==============================================================================
class LanguageLevel(models.TextChoices):
    NATIVE = 'زبان مادری', 'زبان مادری'
    BEGINNER = 'مقدماتی', 'مقدماتی'
    INTERMEDIATE = 'متوسط', 'متوسط'
    ADVANCED = 'پیشرفته', 'پیشرفته'
    EXPERT = 'حرفه‌ای', 'حرفه‌ای'


class Language(models.Model):
    """
    Language proficiencies matching LanguageForm.
    """
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='languages',
        verbose_name="دانشجو"
    )
    name = models.CharField(
        max_length=100,
        verbose_name="نام زبان"
    )
    level = models.CharField(
        max_length=50,
        choices=LanguageLevel.choices,
        default=LanguageLevel.INTERMEDIATE,
        verbose_name="سطح تسلط"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )

    class Meta:
        verbose_name = "زبان"
        verbose_name_plural = "زبان‌ها"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.level}) - {self.student}"


# ==============================================================================
# 8. Activity Model (1:N with Student)
# ==============================================================================
class Activity(models.Model):
    """
    Extracurricular activities, student associations, TA roles, ICPC, etc. matching ActivityForm.
    """
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='activities',
        verbose_name="دانشجو"
    )
    title = models.CharField(
        max_length=200,
        verbose_name="عنوان فعالیت"
    )
    organization = models.CharField(
        max_length=200,
        verbose_name="نام دانشگاه یا سازمان"
    )
    role = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="نقش / سمت"
    )
    date = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="بازه زمانی / تاریخ"
    )
    description = models.TextField(
        blank=True,
        verbose_name="شرح فعالیت"
    )
    achievements = models.TextField(
        blank=True,
        verbose_name="دستاوردها یا نتایج"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ بروزرسانی"
    )

    class Meta:
        verbose_name = "فعالیت و مسابقه"
        verbose_name_plural = "فعالیت‌ها و مسابقات"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.organization}) - {self.student}"


# ==============================================================================
# 9. Course / Certificate Model (1:N with Student)
# ==============================================================================
class Course(models.Model):
    """
    Courses completed & certificates earned matching CertificateForm.
    """
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='courses',
        verbose_name="دانشجو"
    )
    name = models.CharField(
        max_length=200,
        verbose_name="نام دوره یا گواهینامه"
    )
    issuer = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="صادرکننده / مؤسسه"
    )
    date = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="تاریخ اخذ"
    )
    credential_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="شناسه گواهینامه"
    )
    link = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="لینک گواهینامه / دوره"
    )
    description = models.TextField(
        blank=True,
        verbose_name="توضیحات"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ بروزرسانی"
    )

    class Meta:
        verbose_name = "دوره و گواهینامه"
        verbose_name_plural = "دوره‌ها و گواهینامه‌ها"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.issuer}) - {self.student}"


# ==============================================================================
# 10. Achievement Model (1:N with Student)
# ==============================================================================
class AchievementType(models.TextChoices):
    ACADEMIC_AWARD = 'جایزه تحصیلی', 'جایزه تحصیلی'
    COMPETITION_RANK = 'رتبه مسابقه', 'رتبه مسابقه'
    SCHOLARSHIP = 'بورسیه', 'بورسیه'
    HACKATHON = 'هکاتون', 'هکاتون'
    RESEARCH_PAPER = 'مقاله پژوهشی', 'مقاله پژوهشی'
    RESEARCH_ACHIEVEMENT = 'دستاورد پژوهشی', 'دستاورد پژوهشی'
    TOP_STUDENT = 'دانشجوی نمونه', 'دانشجوی نمونه'


class Achievement(models.Model):
    """
    Honors and achievements matching AchievementForm.
    """
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='achievements',
        verbose_name="دانشجو"
    )
    title = models.CharField(
        max_length=255,
        verbose_name="عنوان دستاورد"
    )
    type = models.CharField(
        max_length=100,
        choices=AchievementType.choices,
        default=AchievementType.ACADEMIC_AWARD,
        verbose_name="نوع دستاورد"
    )
    date = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="تاریخ دستاورد"
    )
    description = models.TextField(
        blank=True,
        verbose_name="توضیحات"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )

    class Meta:
        verbose_name = "افتخار و دستاورد"
        verbose_name_plural = "افتخارات و دستاوردها"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.type}) - {self.student}"


# ==============================================================================
# 11. Interest Model (1:N with Student)
# ==============================================================================
class Interest(models.Model):
    """
    Field of interest / topic tag for a student.
    """
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='interests',
        verbose_name="دانشجو"
    )
    name = models.CharField(
        max_length=100,
        verbose_name="عنوان علاقه‌مندی"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )

    class Meta:
        verbose_name = "علاقه‌مندی"
        verbose_name_plural = "علاقه‌مندی‌ها"
        ordering = ['created_at']

    def __str__(self):
        return f"{self.name} ({self.student})"


# ==============================================================================
# 12. Contact Message Model
# ==============================================================================
class ContactMessage(models.Model):
    """
    Messages sent from the frontend ContactModal to a student.
    """
    recipient = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='received_messages',
        verbose_name="دانشجوی دریافت‌کننده",
        null=True,
        blank=True
    )
    name = models.CharField(
        max_length=150,
        verbose_name="نام فرستنده"
    )
    email = models.EmailField(
        verbose_name="ایمیل فرستنده"
    )
    subject = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="موضوع پیام"
    )
    message = models.TextField(
        verbose_name="متن پیام"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ارسال"
    )

    class Meta:
        verbose_name = "پیام تماس"
        verbose_name_plural = "پیام‌های تماس"
        ordering = ['-created_at']

    def __str__(self):
        return f"پیام از {self.name} ({self.email})"
