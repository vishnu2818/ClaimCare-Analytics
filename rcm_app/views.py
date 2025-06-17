# rcm_app/views.py
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import ExcelUpload, ExcelData
from .forms import ExcelUploadForm
import pandas as pd
import numpy as np
from datetime import datetime


def home(request):
    uploads = ExcelUpload.objects.all().order_by('-uploaded_at')
    return render(request, 'home.html', {'uploads': uploads})


import pandas as pd
from datetime import datetime
import numpy as np
from django.shortcuts import render, redirect
from .forms import ExcelUploadForm
from .models import *


def upload_excel(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                file = request.FILES['file']

                # File size validation (10MB max)
                if file.size > 10 * 1024 * 1024:
                    raise ValueError("File size exceeds 10MB limit")

                # Read Excel
                df = pd.read_excel(file, engine='openpyxl')

                # Normalize columns
                df.columns = df.columns.str.strip().str.upper().str.replace(" ", "_")

                # Required columns in normalized format
                required_columns = [
                    'PAYERS', 'PAYOR_CATEGORY', 'EDITS', 'REMARKS',
                    'L_CODES', 'L_CODES_INSTRUCTIONS',
                    'E_CODES', 'E_CODES_INSTRUCTIONS',
                    'A_CODES', 'A_CODES_INSTRUCTIONS',
                    'K_CODES', 'K_CODES_INSTRUCTIONS',
                ]

                # Validate required columns
                for col in required_columns:
                    if col not in df.columns:
                        raise ValueError(f"Missing required column: {col}")

                # Create ExcelUpload record
                upload = ExcelUpload.objects.create(
                    file_name=file.name,
                    row_count=len(df),
                    columns=list(df.columns)
                )

                # Helper to convert values
                def convert_value(value):
                    if pd.isna(value):
                        return None
                    if isinstance(value, (pd.Timestamp, datetime)):
                        return value.isoformat()
                    if isinstance(value, (np.integer)):
                        return int(value)
                    if isinstance(value, (np.floating)):
                        return float(value)
                    return str(value)

                # Save each row to PayerCodeInfo
                for _, row in df.iterrows():
                    PayerCodeInfo.objects.create(
                        payers=convert_value(row['PAYERS']),
                        payor_category=convert_value(row['PAYOR_CATEGORY']),
                        edits=convert_value(row['EDITS']),
                        remarks=convert_value(row['REMARKS']),
                        l_codes=convert_value(row['L_CODES']),
                        l_codes_instructions=convert_value(row['L_CODES_INSTRUCTIONS']),
                        e_codes=convert_value(row['E_CODES']),
                        e_codes_instructions=convert_value(row['E_CODES_INSTRUCTIONS']),
                        a_codes=convert_value(row['A_CODES']),
                        a_codes_instructions=convert_value(row['A_CODES_INSTRUCTIONS']),
                        k_codes=convert_value(row['K_CODES']),
                        k_codes_instructions=convert_value(row['K_CODES_INSTRUCTIONS']),
                    )

                return redirect('rcm_app:home')

            except Exception as e:
                error_msg = f"Error processing file: {str(e)}"
                return render(request, 'upload.html', {
                    'form': form,
                    'error': error_msg
                })
        else:
            return render(request, 'upload.html', {
                'form': form,
                'error': "Invalid form submission. Please check the file."
            })

    else:
        form = ExcelUploadForm()

    return render(request, 'upload.html', {'form': form})


# loki old
# def upload_excel(request):
#     if request.method == 'POST':
#         form = ExcelUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             try:
#                 file = request.FILES['file']
#
#                 # Validate file size (e.g., 10MB limit)
#                 if file.size > 10 * 1024 * 1024:
#                     raise ValueError("File size exceeds 10MB limit")
#
#                 # Read Excel file
#                 df = pd.read_excel(file, engine='openpyxl')
#
#                 # Convert all values to JSON-serializable format
#                 def convert_value(value):
#                     if pd.isna(value):
#                         return None
#                     if isinstance(value, (pd.Timestamp, datetime)):
#                         return value.isoformat()
#                     if isinstance(value, (np.integer)):
#                         return int(value)
#                     if isinstance(value, (np.floating)):
#                         return float(value)
#                     return str(value)
#
#                 # Create ExcelUpload object
#                 upload = ExcelUpload.objects.create(
#                     file_name=file.name,
#                     row_count=len(df),
#                     columns=list(df.columns)  # Store column names as list
#                 )
#
#                 # Save each row as ExcelData
#                 for _, row in df.iterrows():
#                     row_data = {col: convert_value(row[col]) for col in df.columns}
#                     ExcelData.objects.create(
#                         upload=upload,
#                         data=row_data
#                     )
#
#                 return redirect('rcm_app:home')
#
#             except Exception as e:
#                 error_msg = f"Error processing file: {str(e)}"
#                 return render(request, 'upload.html', {
#                     'form': form,
#                     'error': error_msg
#                 })
#         else:
#             error_msg = "Invalid form submission. Please check the file."
#             return render(request, 'upload.html', {
#                 'form': form,
#                 'error': error_msg
#             })
#     else:
#         form = ExcelUploadForm()
#
#     return render(request, 'upload.html', {'form': form})


import pandas as pd
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponse
from .models import ExcelData, ExcelUpload

from django.core.paginator import Paginator
from .models import PayerCodeInfo


def view_uploaded_data(request, upload_id):
    upload = get_object_or_404(ExcelUpload, pk=upload_id)
    queryset = PayerCodeInfo.objects.all().values()

    # Convert to DataFrame
    df = pd.DataFrame(list(queryset))
    if df.empty:
        df = pd.DataFrame(columns=[
            'PAYERS', 'PAYOR_CATEGORY', 'EDITS', 'REMARKS',
            'L_CODES', 'L_CODES_INSTRUCTIONS',
            'E_CODES', 'E_CODES_INSTRUCTIONS',
            'A_CODES', 'A_CODES_INSTRUCTIONS',
            'K_CODES', 'K_CODES_INSTRUCTIONS',
        ])

    # Normalize columns
    df.columns = df.columns.str.strip().str.upper()
    df.dropna(axis=1, how='all', inplace=True)
    df.fillna('', inplace=True)

    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.strip()

    # Filters from request
    payer_filter = request.GET.get('payer', '').strip()
    payor_category_filter = request.GET.get('payor_category', '').strip()
    edits_filter = request.GET.get('edits', '').strip()
    code_category = request.GET.get('code_category', '').strip().upper()
    code_value = request.GET.get('code_value', '').strip().upper()

    # Apply dropdown filters
    if payer_filter and 'PAYERS' in df.columns:
        df = df[df['PAYERS'] == payer_filter]
    if payor_category_filter and 'PAYOR_CATEGORY' in df.columns:
        df = df[df['PAYOR_CATEGORY'] == payor_category_filter]
    if edits_filter and 'EDITS' in df.columns:
        df = df[df['EDITS'] == edits_filter]

    # Apply code category filter (supports partial matches)
    if code_category and code_value and code_category in df.columns:
        df[code_category] = df[code_category].astype(str).str.upper()
        df = df[df[code_category].str.contains(code_value, na=False)]

    # Prepare pagination
    cleaned_data = df.to_dict(orient='records')
    paginator = Paginator(cleaned_data, 500)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Prepare dropdown filters
    filter_options = {
        'payers': sorted(df['PAYERS'].dropna().unique()) if 'PAYERS' in df.columns else [],
        'payor_categories': sorted(df['PAYOR_CATEGORY'].dropna().unique()) if 'PAYOR_CATEGORY' in df.columns else [],
        'edits': sorted(df['EDITS'].dropna().unique()) if 'EDITS' in df.columns else [],
        'code_categories': ['L_CODES', 'E_CODES', 'A_CODES', 'K_CODES'],
    }

    context = {
        'upload': upload,  # You can remove this if you're not using ExcelUpload
        'columns': df.columns,
        'data_rows': page_obj.object_list,
        'page_obj': page_obj,
        'selected_filters': {
            'payer': payer_filter,
            'payor_category': payor_category_filter,
            'edits': edits_filter,
            'code_category': code_category,
            'code_value': code_value,
        },
        'filter_options': filter_options,
    }

    return render(request, 'view_data.html', context)


# def view_uploaded_data(request, upload_id):
#     upload = get_object_or_404(ExcelUpload, pk=upload_id)
#     data_qs = ExcelData.objects.filter(upload=upload)
#     data_list = [row.data for row in data_qs if row.data]
#
#     df = pd.DataFrame(data_list)
#     df.columns = df.columns.str.strip().str.upper()
#     df.dropna(axis=1, how='all', inplace=True)
#     df.fillna('', inplace=True)
#
#     for col in df.columns:
#         if df[col].dtype == object:
#             df[col] = df[col].astype(str).str.strip()
#
#     # Filters from request
#     payer_filter = request.GET.get('payer', '').strip()
#     payor_category_filter = request.GET.get('payor_category', '').strip()
#     edits_filter = request.GET.get('edits', '').strip()
#     code_category = request.GET.get('code_category', '').strip().upper()
#     code_value = request.GET.get('code_value', '').strip().upper()
#
#     # Apply dropdown filters
#     if payer_filter and 'PAYERS' in df.columns:
#         df = df[df['PAYERS'] == payer_filter]
#     if payor_category_filter and 'PAYOR CATEGORY' in df.columns:
#         df = df[df['PAYOR CATEGORY'] == payor_category_filter]
#     if edits_filter and 'EDITS' in df.columns:
#         df = df[df['EDITS'] == edits_filter]
#
#     # Apply code category filter (supports partial matches)
#     if code_category and code_value:
#         print("🧪 FILTERING ON:", code_category, "→", code_value)
#         print("📊 AVAILABLE COLUMNS:", df.columns.tolist())
#
#         if code_category in df.columns:
#             df[code_category] = df[code_category].astype(str).str.upper()
#             matched_df = df[df[code_category].str.contains(code_value, na=False)]
#             print(f"✅ MATCHED {len(matched_df)} ROWS")
#             df = matched_df
#         else:
#             print("❌ Column not found for code category!")
#
#     # Prepare data for pagination
#     cleaned_data = df.to_dict(orient='records')
#     paginator = Paginator(cleaned_data, 500)
#     page_number = request.GET.get('page', 1)
#     page_obj = paginator.get_page(page_number)
#
#     # Prepare dropdown values from full unfiltered data
#     full_df = pd.DataFrame(data_list)
#     full_df.columns = full_df.columns.str.strip().str.upper()
#     full_df.fillna('', inplace=True)
#     for col in full_df.columns:
#         if full_df[col].dtype == object:
#             full_df[col] = full_df[col].astype(str).str.strip()
#
#     filter_options = {
#         'payers': sorted(full_df['PAYERS'].dropna().unique()) if 'PAYERS' in full_df.columns else [],
#         'payor_categories': sorted(
#             full_df['PAYOR CATEGORY'].dropna().unique()) if 'PAYOR CATEGORY' in full_df.columns else [],
#         'edits': sorted(full_df['EDITS'].dropna().unique()) if 'EDITS' in full_df.columns else [],
#         'code_categories': ['L CODES', 'E CODES', 'A CODES', 'K CODES'],
#     }
#
#     context = {
#         'upload': upload,
#         'columns': df.columns,
#         'data_rows': page_obj.object_list,
#         'page_obj': page_obj,
#         'selected_filters': {
#             'payer': payer_filter,
#             'payor_category': payor_category_filter,
#             'edits': edits_filter,
#             'code_category': code_category,
#             'code_value': code_value,
#         },
#         'filter_options': filter_options,
#     }
#
#     return render(request, 'view_data.html', context)


def download_filtered_excel(request, upload_id):
    upload = get_object_or_404(ExcelUpload, pk=upload_id)
    data_qs = ExcelData.objects.filter(upload=upload)
    data_list = [row.data for row in data_qs if row.data]

    df = pd.DataFrame(data_list)
    df.columns = df.columns.str.strip().str.upper()
    df.fillna('', inplace=True)

    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.strip()

    payer_filter = request.GET.get('payer', '').strip()
    payor_category_filter = request.GET.get('payor_category', '').strip()
    edits_filter = request.GET.get('edits', '').strip()
    code_category = request.GET.get('code_category', '').strip().upper()
    code_value = request.GET.get('code_value', '').strip().upper()

    if payer_filter and 'PAYERS' in df.columns:
        df = df[df['PAYERS'] == payer_filter]
    if payor_category_filter and 'PAYOR CATEGORY' in df.columns:
        df = df[df['PAYOR CATEGORY'] == payor_category_filter]
    if edits_filter and 'EDITS' in df.columns:
        df = df[df['EDITS'] == edits_filter]

    if code_category and code_value and code_category in df.columns:
        df[code_category] = df[code_category].astype(str).str.upper()
        df = df[df[code_category].str.contains(code_value, na=False)]

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = f"filtered_data_upload_{upload_id}.xlsx"
    response['Content-Disposition'] = f'attachment; filename={filename}'

    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='FilteredData')

    return response
