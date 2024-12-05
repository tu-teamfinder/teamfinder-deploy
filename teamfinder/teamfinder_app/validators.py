from django.core.exceptions import ValidationError

def validate_file_size(value):
    max_size_kb = 1000  # Maximum size in KB (adjust as needed)
    if value.size > max_size_kb * 1024:
        raise ValidationError(f"File size exceeds {max_size_kb} KB.")
