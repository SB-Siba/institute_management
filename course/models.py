
from django.db import models
from django.utils import timezone  
from ckeditor.fields import RichTextField


class AwardCategory(models.Model):
    category_name = models.CharField(max_length=255)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.category_name
    

class Course(models.Model):
    
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]
    course_code = models.CharField(max_length=100, unique=True, blank=True, null=True)
    award = models.ForeignKey(AwardCategory, on_delete=models.CASCADE, null=True, blank=True)
    course_name = models.CharField(max_length=200, blank=True, null=True)
    course_subject = models.JSONField(default=list, blank=True, null=True)
    course_fees = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    course_mrp = models.DecimalField(default=0.0 ,max_digits=10, decimal_places=2,blank=True, null=True)
    minimum_fees = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    course_duration = models.CharField(max_length=100,blank=True, null=True)
    exam_fees = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    course_video_link_1 = models.URLField(blank=True, null=True)
    course_video_link_2 = models.URLField(blank=True, null=True)
    course_syllabus = models.TextField(blank=True, null=True)
    eligibility = models.TextField(blank=True, null=True)
    course_image = models.ImageField(upload_to='course_images/', blank=True, null=True)
    pdf_files = models.FileField(upload_to='course_materials/', blank=True, null=True)
    course_video_links = models.JSONField(default=list, blank=True, null=True)
    display_course_fees_on_website = models.BooleanField(default=False,blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active',blank=True, null=True)
    batch = models.ForeignKey('users.Batch', on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return self.course_name 
    

class Exam(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('appeared', 'Appeared'),
        ('postponed', 'Postponed'),
        ('cancel', 'Cancel'),
     )
    exam_name = models.CharField(max_length=200, default='exam', blank=True)
    date = models.DateField(default=timezone.now)  # This will now work correctly
    duration = models.DurationField(help_text="Enter the duration in HH:MM:SS format")
    total_marks = models.PositiveIntegerField(null=False, blank=False)
    total_questions = models.PositiveIntegerField(null=True, blank=True, help_text="Enter the total number of questions")
    passing_marks = models.PositiveIntegerField(null=True, blank=True, help_text="Enter the minimum passing marks")
    course = models.ForeignKey('course.Course', on_delete=models.CASCADE, related_name='exams', null=True, blank=True)
    subjects = models.JSONField(default=list, blank=True)
    batch = models.ForeignKey('users.Batch', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
  
    def __str__(self):
        return self.get_status_display()

    class Meta:
        verbose_name = 'Exam Status'
        verbose_name_plural = 'Exam Statuses'
def __str__(self):
        return f"{self.course} - {self.exam_date}"

class ExamResult(models.Model):
    student = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='exam_results',null=True, blank=True)
    course = models.ForeignKey('course.Course', on_delete=models.CASCADE, related_name='exam_results', null=True, blank=True)
    theory_marks = models.IntegerField(null=True, blank=True)
    practical_marks = models.IntegerField(null=True, blank=True)
    total_mark = models.DecimalField(max_digits=5, decimal_places=2)
    obtained_mark = models.DecimalField(max_digits=5, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)

    grade = models.CharField(max_length=2, choices=[
        ('A+', 'A+'), ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')
    ])
    result = models.CharField(max_length=7, choices=[('passed', 'Passed'), ('failed', 'Failed')])
    created_on = models.DateField(auto_now_add=True)

    # Updated __str__ method to handle potential None values
    def __str__(self):
        student_name = self.student.name if self.student else "Unknown Student"
        course_name = self.course.course_name if self.course and self.course.course_name else "No Course"
        return f"Result for {student_name} in {course_name}"

    def calculate_percentage(self):
        if self.total_mark > 0:
            self.percentage = (self.obtained_mark / self.total_mark) * 100
        return self.percentage

    def save(self, *args, **kwargs):
        # Ensure obtained marks are calculated based on theory and practical
        self.obtained_mark = self.theory_marks + self.practical_marks
        self.calculate_percentage()
        
        # Assign grade based on percentage
        if self.percentage >= 90:
            self.grade = 'A+'
        elif self.percentage >= 80:
            self.grade = 'A'
        elif self.percentage >= 70:
            self.grade = 'B'
        elif self.percentage >= 60:
            self.grade = 'C'
        elif self.percentage >= 50:
            self.grade = 'D'
        else:
            self.grade = 'E'
        
        super().save(*args, **kwargs)
