from django.contrib import admin
from .models import *
from django.utils.html import format_html


@admin.register(PayerCodeInfo)
class PayerCodeInfoAdmin(admin.ModelAdmin):
    list_display = (
        'payers', 'payor_category', 'edits',
        'remarks', 'cpt_edits_sub_category',
        'l_codes', 'l_codes_instructions',
        'e_codes', 'e_codes_instructions',
        'a_codes', 'a_codes_instructions',
        'k_codes', 'k_codes_instructions'
    )
    search_fields = ('payers', 'payor_category', 'edits', 'remarks')
    list_filter = ('payers', 'payor_category', 'edits','l_codes','e_codes')


@admin.register(ExcelUpload)
class ExcelUploadAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'uploaded_at', 'row_count')
    readonly_fields = ('columns_preview',)

    def columns_preview(self, obj):
        return format_html("<br>".join(obj.columns.keys()))

    columns_preview.short_description = "Columns"
