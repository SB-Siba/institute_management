from django import template
from users.models import Batch, Attendance

register = template.Library()

@register.filter
def get_batch_name(batches, batch_id):
    batch = batches.filter(id=batch_id).first()
    return batch.name if batch else "Unknown"

@register.filter
def get_attendance_for_student(attendance_records, student):
    return attendance_records.filter(student=student)
