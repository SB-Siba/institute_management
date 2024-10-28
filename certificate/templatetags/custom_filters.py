from django import template

register = template.Library()

@register.filter
def get_exam_result(exam_result_mapping, keys):
    """
    Custom filter to get exam result from a mapping using (student_id, course_id).
    """
    if isinstance(keys, tuple) and len(keys) == 2:
        return exam_result_mapping.get(keys)
    return None
