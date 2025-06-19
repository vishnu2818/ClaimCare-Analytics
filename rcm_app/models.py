# models.py
from django.db import models


class PayerCodeInfo(models.Model):
    upload = models.ForeignKey('ExcelUpload', on_delete=models.CASCADE, null=True, blank=True)
    # Basic Info
    payers = models.CharField(max_length=100, null=True, blank=True)
    payor_category = models.CharField(max_length=100, null=True, blank=True)
    edits = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=100, null=True, blank=True)
    cpt_edits_sub_category = models.CharField(max_length=100, null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)

    # L Codes
    l_codes = models.TextField(verbose_name="L Codes", null=True, blank=True)
    l_codes_instructions = models.TextField(verbose_name="L Codes Instructions", null=True, blank=True)

    # E Codes
    e_codes = models.TextField(verbose_name="E Codes", null=True, blank=True)
    e_codes_instructions = models.TextField(verbose_name="E Codes Instructions", null=True, blank=True)

    # A Codes
    a_codes = models.TextField(verbose_name="A Codes", null=True, blank=True)
    a_codes_instructions = models.TextField(verbose_name="A Codes Instructions", null=True, blank=True)

    # K Codes
    k_codes = models.TextField(verbose_name="K Codes", null=True, blank=True)
    k_codes_instructions = models.TextField(verbose_name="K Codes Instructions", null=True, blank=True)

    def __str__(self):
        return self.payers


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
