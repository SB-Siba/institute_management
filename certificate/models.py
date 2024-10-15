from django.db import models

class ExamResult(models.Model):
    student = models.ForeignKey('users.User', on_delete=models.CASCADE)
    course = models.ForeignKey('course.Course', on_delete=models.CASCADE)
    exam_mode = models.CharField(max_length=50)
    objective_marks = models.FloatField()
    practical_marks = models.FloatField()
    percentage = models.FloatField()
    grade = models.CharField(max_length=10)
    result = models.CharField(max_length=10)
    student_exam_date = models.DateField()

    def __str__(self):
        return f"{self.student} - {self.course}"
