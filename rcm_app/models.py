# models.py
from django.db import models

class ExcelUpload(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_name = models.CharField(max_length=255)
    row_count = models.PositiveIntegerField()
    columns = models.JSONField()

    def __str__(self):
        return f"{self.file_name} ({self.row_count} rows)"


class ExcelData(models.Model):
    upload = models.ForeignKey(ExcelUpload, on_delete=models.CASCADE, related_name='rows')
    data = models.JSONField()  # Stores all row data

    def __str__(self):
        return f"Row from {self.upload.file_name}"