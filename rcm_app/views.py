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


def upload_excel(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                file = request.FILES['file']

                # Validate file size (e.g., 10MB limit)
                if file.size > 10 * 1024 * 1024:
                    raise ValueError("File size exceeds 10MB limit")

                # Read Excel file
                df = pd.read_excel(file, engine='openpyxl')

                # Convert all values to JSON-serializable format
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

                # Create ExcelUpload object
                upload = ExcelUpload.objects.create(
                    file_name=file.name,
                    row_count=len(df),
                    columns=list(df.columns)  # Store column names as list
                )

                # Save each row as ExcelData
                for _, row in df.iterrows():
                    row_data = {col: convert_value(row[col]) for col in df.columns}
                    ExcelData.objects.create(
                        upload=upload,
                        data=row_data
                    )

                return redirect('rcm_app:home')

            except Exception as e:
                error_msg = f"Error processing file: {str(e)}"
                return render(request, 'upload.html', {
                    'form': form,
                    'error': error_msg
                })
        else:
            error_msg = "Invalid form submission. Please check the file."
            return render(request, 'upload.html', {
                'form': form,
                'error': error_msg
            })
    else:
        form = ExcelUploadForm()

    return render(request, 'upload.html', {'form': form})


# from django.shortcuts import render, get_object_or_404
# from .models import ExcelUpload, ExcelData
#
#
# def view_uploaded_data(request, upload_id):
#     # Get the specific upload or return 404
#     upload = get_object_or_404(ExcelUpload, id=upload_id)
#
#     # Get all data rows for this upload
#     data_rows = ExcelData.objects.filter(upload=upload)
#
#     # Prepare the data for the template
#     context = {
#         'upload': upload,
#         'columns': upload.columns,  # Assuming columns is stored as a list
#         'data_rows': data_rows,
#     }
#
#     return render(request, 'view_data.html', context)


# import pandas as pd
# from django.shortcuts import render, get_object_or_404
# from .models import ExcelData, ExcelUpload  # updated model name here
#
#
# def view_uploaded_data(request, upload_id):
#     # Use ExcelUpload model to get the upload instance
#     upload = get_object_or_404(ExcelUpload, pk=upload_id)
#
#     # Query all ExcelData rows for this upload
#     data_qs = ExcelData.objects.filter(upload=upload)
#     data_list = [row.data for row in data_qs if row.data]
#
#     # Load data into DataFrame
#     df = pd.DataFrame(data_list)
#
#     # Drop empty columns
#     df.dropna(axis=1, how='all', inplace=True)
#
#     # Strip whitespace in string columns
#     for col in df.columns:
#         if df[col].dtype == object:
#             df[col] = df[col].str.strip()
#
#     # Fill missing values with empty string
#     df.fillna('', inplace=True)
#
#     # Convert first column to string explicitly and sort
#     if not df.empty and len(df.columns) > 0:
#         df[df.columns[0]] = df[df.columns[0]].astype(str)
#         df.sort_values(by=df.columns[0], inplace=True)
#
#     cleaned_data = df.to_dict(orient='records')
#
#     context = {
#         'upload': upload,
#         'columns': df.columns,
#         'data_rows': cleaned_data,
#     }
#     return render(request, 'view_data.html', context)

# import pandas as pd
# from django.shortcuts import render, get_object_or_404
# from django.core.paginator import Paginator
# from .models import ExcelData, ExcelUpload
#
#
# def view_uploaded_data(request, upload_id):
#     upload = get_object_or_404(ExcelUpload, pk=upload_id)
#
#     # GET filter values
#     payer_filter = request.GET.get('payer', '').strip()
#     payor_category_filter = request.GET.get('payor_category', '').strip()
#     edits_filter = request.GET.get('edits', '').strip()
#
#     # Get all ExcelData for this upload
#     data_qs = ExcelData.objects.filter(upload=upload)
#     data_list = [row.data for row in data_qs if row.data]
#
#     df = pd.DataFrame(data_list)
#     df.dropna(axis=1, how='all', inplace=True)
#     df.fillna('', inplace=True)
#
#     for col in df.columns:
#         if df[col].dtype == object:
#             df[col] = df[col].str.strip()
#
#     # Apply filters in pandas
#     if payer_filter and 'PAYERS' in df.columns:
#         df = df[df['PAYERS'] == payer_filter]
#
#     if payor_category_filter and 'Payor Category' in df.columns:
#         df = df[df['Payor Category'] == payor_category_filter]
#
#     if edits_filter and 'EDITS' in df.columns:
#         df = df[df['EDITS'] == edits_filter]
#
#     if not df.empty and len(df.columns) > 0:
#         df[df.columns[0]] = df[df.columns[0]].astype(str)
#         df.sort_values(by=df.columns[0], inplace=True)
#
#     cleaned_data = df.to_dict(orient='records')
#
#     # Generate dropdown values from full dataset
#     full_df = pd.DataFrame(data_list)
#     full_df.fillna('', inplace=True)
#     for col in full_df.columns:
#         if full_df[col].dtype == object:
#             full_df[col] = full_df[col].str.strip()
#
#     filter_options = {
#         'payers': sorted(full_df['PAYERS'].dropna().unique()) if 'PAYERS' in full_df.columns else [],
#         'payor_categories': sorted(full_df['Payor Category'].dropna().unique()) if 'Payor Category' in full_df.columns else [],
#         'edits': sorted(full_df['EDITS'].dropna().unique()) if 'EDITS' in full_df.columns else [],
#     }
#
#     # Pagination
#     paginator = Paginator(cleaned_data, 100)
#     page_number = request.GET.get("page")
#     page_obj = paginator.get_page(page_number)
#
#     context = {
#         'upload': upload,
#         'columns': df.columns,
#         'data_rows': page_obj,
#         'page_obj': page_obj,
#         'selected_filters': {
#             'payer': payer_filter,
#             'payor_category': payor_category_filter,
#             'edits': edits_filter,
#         },
#         'filter_options': filter_options,
#     }
#     return render(request, 'view_data.html', context)
# import pandas as pd
# from django.shortcuts import render, get_object_or_404
# from django.http import HttpResponse
# from django.core.paginator import Paginator
# from .models import ExcelData, ExcelUpload
#
#
# def view_uploaded_data(request, upload_id):
#     upload = get_object_or_404(ExcelUpload, pk=upload_id)
#     data_qs = ExcelData.objects.filter(upload=upload)
#     data_list = [row.data for row in data_qs if row.data]
#
#     df = pd.DataFrame(data_list)
#     df.columns = df.columns.str.strip()
#     df.dropna(axis=1, how='all', inplace=True)
#     df.fillna('', inplace=True)
#
#     for col in df.columns:
#         if df[col].dtype == object:
#             df[col] = df[col].str.strip()
#
#     # Filters
#     payer_filter = request.GET.get('payer', '').strip()
#     payor_category_filter = request.GET.get('payor_category', '').strip()
#     edits_filter = request.GET.get('edits', '').strip()
#
#     if payer_filter and 'PAYERS' in df.columns:
#         df = df[df['PAYERS'] == payer_filter]
#     if payor_category_filter and 'Payor Category' in df.columns:
#         df = df[df['Payor Category'] == payor_category_filter]
#     if edits_filter and 'EDITS' in df.columns:
#         df = df[df['EDITS'] == edits_filter]
#
#     # Sort
#     if not df.empty and len(df.columns) > 0:
#         df[df.columns[0]] = df[df.columns[0]].astype(str)
#         df.sort_values(by=df.columns[0], inplace=True)
#
#     cleaned_data = df.to_dict(orient='records')
#
#     # Full data for dropdowns
#     full_df = pd.DataFrame(data_list)
#     full_df.columns = full_df.columns.str.strip()
#     full_df.fillna('', inplace=True)
#     for col in full_df.columns:
#         if full_df[col].dtype == object:
#             full_df[col] = full_df[col].str.strip()
#
#     filter_options = {
#         'payers': sorted(full_df['PAYERS'].dropna().unique()) if 'PAYERS' in full_df.columns else [],
#         'payor_categories': sorted(full_df['Payor Category'].dropna().unique()) if 'Payor Category' in full_df.columns else [],
#         'edits': sorted(full_df['EDITS'].dropna().unique()) if 'EDITS' in full_df.columns else [],
#     }
#
#     paginator = Paginator(cleaned_data, 100)
#     page_number = request.GET.get("page")
#     page_obj = paginator.get_page(page_number)
#
#     context = {
#         'upload': upload,
#         'columns': df.columns,
#         'data_rows': page_obj,
#         'page_obj': page_obj,
#         'selected_filters': {
#             'payer': payer_filter,
#             'payor_category': payor_category_filter,
#             'edits': edits_filter,
#         },
#         'filter_options': filter_options,
#     }
#     return render(request, 'view_data.html', context)

import pandas as pd
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import ExcelData, ExcelUpload

def view_uploaded_data(request, upload_id):
    upload = get_object_or_404(ExcelUpload, pk=upload_id)
    data_qs = ExcelData.objects.filter(upload=upload)
    data_list = [row.data for row in data_qs if row.data]

    df = pd.DataFrame(data_list)
    df.columns = df.columns.str.strip()
    df.dropna(axis=1, how='all', inplace=True)
    df.fillna('', inplace=True)

    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].str.strip()

    # Filters
    payer_filter = request.GET.get('payer', '').strip()
    payor_category_filter = request.GET.get('payor_category', '').strip()
    edits_filter = request.GET.get('edits', '').strip()

    if payer_filter and 'PAYERS' in df.columns:
        df = df[df['PAYERS'] == payer_filter]
    if payor_category_filter and 'Payor Category' in df.columns:
        df = df[df['Payor Category'] == payor_category_filter]
    if edits_filter and 'EDITS' in df.columns:
        df = df[df['EDITS'] == edits_filter]

    # Sort by first column
    if not df.empty and len(df.columns) > 0:
        df[df.columns[0]] = df[df.columns[0]].astype(str)
        df.sort_values(by=df.columns[0], inplace=True)

    cleaned_data = df.to_dict(orient='records')

    # Pagination (chunk size = 500)
    paginator = Paginator(cleaned_data, 500)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Full data for dropdown filters
    full_df = pd.DataFrame(data_list)
    full_df.columns = full_df.columns.str.strip()
    full_df.fillna('', inplace=True)
    for col in full_df.columns:
        if full_df[col].dtype == object:
            full_df[col] = full_df[col].str.strip()

    filter_options = {
        'payers': sorted(full_df['PAYERS'].dropna().unique()) if 'PAYERS' in full_df.columns else [],
        'payor_categories': sorted(full_df['Payor Category'].dropna().unique()) if 'Payor Category' in full_df.columns else [],
        'edits': sorted(full_df['EDITS'].dropna().unique()) if 'EDITS' in full_df.columns else [],
    }

    context = {
        'upload': upload,
        'columns': df.columns,
        'data_rows': page_obj.object_list,
        'page_obj': page_obj,
        'selected_filters': {
            'payer': payer_filter,
            'payor_category': payor_category_filter,
            'edits': edits_filter,
        },
        'filter_options': filter_options,
    }
    return render(request, 'view_data.html', context)

def download_filtered_excel(request, upload_id):
    upload = get_object_or_404(ExcelUpload, pk=upload_id)
    data_qs = ExcelData.objects.filter(upload=upload)
    data_list = [row.data for row in data_qs if row.data]

    df = pd.DataFrame(data_list)
    df.columns = df.columns.str.strip()
    df.fillna('', inplace=True)

    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].str.strip()

    payer_filter = request.GET.get('payer', '').strip()
    payor_category_filter = request.GET.get('payor_category', '').strip()
    edits_filter = request.GET.get('edits', '').strip()

    if payer_filter and 'PAYERS' in df.columns:
        df = df[df['PAYERS'] == payer_filter]
    if payor_category_filter and 'Payor Category' in df.columns:
        df = df[df['Payor Category'] == payor_category_filter]
    if edits_filter and 'EDITS' in df.columns:
        df = df[df['EDITS'] == edits_filter]

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = f"filtered_data_upload_{upload_id}.xlsx"
    response['Content-Disposition'] = f'attachment; filename={filename}'

    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='FilteredData')

    return response
