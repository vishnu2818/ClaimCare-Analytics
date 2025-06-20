from datetime import datetime
import numpy as np
from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
import pandas as pd
from .models import ExcelUpload, PayerCodeInfo


@login_required
def home(request):
    uploads = ExcelUpload.objects.all().order_by('-uploaded_at')
    return render(request, 'home.html', {'uploads': uploads})


# @login_required
# def upload_excel(request):
#     if request.method == 'POST':
#         form = ExcelUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             try:
#                 file = request.FILES['file']
#
#                 # File size validation (10MB max)
#                 if file.size > 10 * 1024 * 1024:
#                     raise ValueError("File size exceeds 10MB limit")
#
#                 # Read Excel
#                 df = pd.read_excel(file, engine='openpyxl')
#
#                 # Normalize columns
#                 df.columns = df.columns.str.strip().str.upper().str.replace(" ", "_").str.replace("&", "_")
#
#                 # Required columns in normalized format
#                 required_columns = [
#                     'PAYERS', 'PAYOR_CATEGORY', 'EDITS', 'REMARKS',
#                      '',
#                     'L_CODES', 'L_CODES_INSTRUCTIONS',
#                     'E_CODES', 'E_CODES_INSTRUCTIONS',
#                     'A_CODES', 'A_CODES_INSTRUCTIONS',
#                     'K_CODES', 'K_CODES_INSTRUCTIONS',
#                 ]
#
#                 # Validate required columns
#                 for col in required_columns:
#                     if col not in df.columns:
#                         raise ValueError(f"Missing required column: {col}")
#
#                 # Create ExcelUpload record
#                 upload = ExcelUpload.objects.create(
#                     file_name=file.name,
#                     row_count=len(df),
#                     columns=list(df.columns)
#                 )
#
#                 # Helper to convert values
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
#                 # Save each row to PayerCodeInfo
#                 for _, row in df.iterrows():
#                     PayerCodeInfo.objects.create(
#                         upload=upload,
#                         payers=convert_value(row['PAYERS']),
#                         payor_category=convert_value(row['PAYOR_CATEGORY']),
#                         edits=convert_value(row['EDITS']),
#                         remarks=convert_value(row['REMARKS']),
#                         l_codes=convert_value(row['L_CODES']),REMARKS
#                         l_codes_instructions=convert_value(row['L_CODES_INSTRUCTIONS']),
#                         e_codes=convert_value(row['E_CODES']),
#                         e_codes_instructions=convert_value(row['E_CODES_INSTRUCTIONS']),
#                         a_codes=convert_value(row['A_CODES']),
#                         a_codes_instructions=convert_value(row['A_CODES_INSTRUCTIONS']),
#                         k_codes=convert_value(row['K_CODES']),
#                         k_codes_instructions=convert_value(row['K_CODES_INSTRUCTIONS']),
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
#             return render(request, 'upload.html', {
#                 'form': form,
#                 'error': "Invalid form submission. Please check the file."
#             })
#
#     else:
#         form = ExcelUploadForm()
#
#     return render(request, 'upload.html', {'form': form})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ExcelUploadForm
from .models import ExcelUpload, PayerCodeInfo
import pandas as pd
import numpy as np
from datetime import datetime
import re


@login_required
def upload_excel(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                file = request.FILES['file']

                # ✅ Validate file size (max 10 MB)
                if file.size > 10 * 1024 * 1024:
                    raise ValueError("File size exceeds 10MB limit")

                # ✅ Read Excel file
                df = pd.read_excel(file, engine='openpyxl')

                # ✅ Normalize column names
                def normalize_column(col):
                    col = col.strip()  # Trim spaces
                    col = re.sub(r'[\s/&\-]+', '_', col)  # Replace space, /, &, - with _
                    col = re.sub(r'_+', '_', col)  # Replace multiple underscores with a single _
                    return col.upper()  # Convert to uppercase

                df.columns = [normalize_column(col) for col in df.columns]

                print("✅ Normalized headers:", df.columns.tolist())

                # ✅ Define all expected columns
                expected_columns = [
                    'PAYERS', 'PAYOR_CATEGORY', 'EDITS',
                    # 'REMARKS',
                    'BILLING_CODING_INSTRUCTIONS',
                    'EDIT_TYPE',
                    'ENTER_CODE',
                    # 'TYPE',
                    'CPT_EDITS_SUB_CATEGORY',
                    # 'L_CODES', 'L_CODES_INSTRUCTIONS',
                    # 'E_CODES', 'E_CODES_INSTRUCTIONS',
                    # 'A_CODES', 'A_CODES_INSTRUCTIONS',
                    # 'K_CODES', 'K_CODES_INSTRUCTIONS',
                ]

                # ✅ Fill missing columns with None
                for col in expected_columns:
                    if col not in df.columns:
                        df[col] = None

                # ✅ Confirm column exists
                if 'CPT_EDITS_SUB_CATEGORY' not in df.columns:
                    raise ValueError("Column 'CPT/EDITS Sub-Category' not found or not normalized properly")

                # ✅ Create upload log entry
                upload = ExcelUpload.objects.create(
                    file_name=file.name,
                    row_count=len(df),
                    columns=list(df.columns)
                )

                # ✅ Helper to safely convert values
                def convert_value(value):
                    if pd.isna(value):
                        return None
                    if isinstance(value, (pd.Timestamp, datetime)):
                        return value.isoformat()
                    if isinstance(value, np.integer):
                        return int(value)
                    if isinstance(value, np.floating):
                        return float(value)
                    return str(value).strip()

                # ✅ Save each row into PayerCodeInfo
                for index, row in df.iterrows():
                    try:
                        PayerCodeInfo.objects.create(
                            upload=upload,
                            payers=convert_value(row.get('PAYERS')),
                            payor_category=convert_value(row.get('PAYOR_CATEGORY')),
                            edits=convert_value(row.get('EDITS')),
                            # type=convert_value(row.get('TYPE')),
                            edit_type=convert_value(row.get('EDIT_TYPE')),
                            enter_code=convert_value(row.get('ENTER_CODE')),
                            cpt_edits_sub_category=convert_value(row.get('CPT_EDITS_SUB_CATEGORY')),
                            # remarks=convert_value(row.get('REMARKS')),
                            billing_coding_instructions=convert_value(row['BILLING_CODING_INSTRUCTIONS']),
                            # l_codes=convert_value(row.get('L_CODES')),
                            # l_codes_instructions=convert_value(row.get('L_CODES_INSTRUCTIONS')),
                            # e_codes=convert_value(row.get('E_CODES')),
                            # e_codes_instructions=convert_value(row.get('E_CODES_INSTRUCTIONS')),
                            # a_codes=convert_value(row.get('A_CODES')),
                            # a_codes_instructions=convert_value(row.get('A_CODES_INSTRUCTIONS')),
                            # k_codes=convert_value(row.get('K_CODES')),
                            # k_codes_instructions=convert_value(row.get('K_CODES_INSTRUCTIONS')),
                        )
                        print(f"✅ Row {index + 1} saved: {row}")
                    except Exception as row_error:
                        print(f"❌ Row {index + 1} skipped due to error: {row_error}")
                        continue

                return redirect('rcm_app:home')

            except Exception as e:
                return render(request, 'upload.html', {
                    'form': form,
                    'error': f"❌ Error processing file: {str(e)}"
                })
        else:
            return render(request, 'upload.html', {
                'form': form,
                'error': "❌ Invalid form submission. Please upload a valid Excel file."
            })

    else:
        form = ExcelUploadForm()

    return render(request, 'upload.html', {'form': form})


# @login_required
# def view_uploaded_data(request, upload_id):
#     upload = get_object_or_404(ExcelUpload, pk=upload_id)
#
#     queryset = PayerCodeInfo.objects.filter(upload=upload).values(
#         'payers', 'payor_category', 'edits',
#         'edit_type', 'enter_code',
#         'cpt_edits_sub_category',
#         'billing_coding_instructions',
#         # 'remarks',
#         # 'type',
#         # 'l_codes', 'l_codes_instructions',
#         # 'e_codes', 'e_codes_instructions',
#         # 'a_codes', 'a_codes_instructions',
#         # 'k_codes', 'k_codes_instructions'
#     )
#     df = pd.DataFrame(list(queryset))
#
#     expected_columns = [
#         'PAYERS', 'PAYOR_CATEGORY',
#         'EDITS',
#         # 'REMARKS',
#         'EDIT_TYPE', 'ENTER_CODE',
#         'BILLING_CODING_INSTRUCTIONS',
#         # 'TYPE',
#         'CPT_EDITS_SUB_CATEGORY',
#         # 'L_CODES', 'L_CODES_INSTRUCTIONS',
#         # 'E_CODES', 'E_CODES_INSTRUCTIONS',
#         # 'A_CODES', 'A_CODES_INSTRUCTIONS',
#         # 'K_CODES', 'K_CODES_INSTRUCTIONS'
#     ]
#     if df.empty:
#         df = pd.DataFrame(columns=expected_columns)
#
#     df.columns = df.columns.str.strip().str.upper()
#     df.dropna(axis=1, how='all', inplace=True)
#     df.fillna('', inplace=True)
#
#     for col in df.columns:
#         if df[col].dtype == object:
#             df[col] = df[col].astype(str).str.strip()
#
#     # Capture Filters
#     filters = {
#         'payer': request.GET.get('payer', '').strip(),
#         'payor_category': request.GET.get('payor_category', '').strip(),
#         'edits': request.GET.get('edits', '').strip(),
#         # 'code_category': request.GET.get('code_category', '').strip().upper(),
#         # 'code_value': request.GET.get('code_value', '').strip().upper()
#     }
#
#     unfiltered_df = df.copy()
#
#     # 5️⃣ Apply Filters
#     if filters['payer'] and 'PAYERS' in df.columns:
#         df = df[df['PAYERS'] == filters['payer']]
#
#     if filters['payor_category'] and 'PAYOR_CATEGORY' in df.columns:
#         df = df[df['PAYOR_CATEGORY'] == filters['payor_category']]
#
#     if filters['edits'] and 'EDITS' in df.columns:
#         df = df[df['EDITS'] == filters['edits']]
#
#     # ✅ Code Category and Code Value Filtering
#     code_col = filters['code_category']  # e.g. 'L_CODES'
#     code_val = filters['code_value']  # e.g. 'L123'
#     code_val_upper = code_val.upper()
#
#     code_columns = ['L_CODES', 'E_CODES', 'A_CODES', 'K_CODES']
#
#     # 🟩 Case 1: Both category and value are provided
#     if code_col and code_val and code_col in df.columns:
#         df[code_col] = df[code_col].astype(str).str.upper().str.strip()
#         df = df[
#             df[code_col].str.contains(code_val_upper, na=False) &
#             df[code_col].ne('') &
#             df[code_col].ne('()')
#             ]
#
#     # 🟨 Case 2: Only code_category selected
#     elif code_col and code_col in df.columns:
#         df[code_col] = df[code_col].astype(str).str.upper().str.strip()
#         df = df[
#             df[code_col].ne('') &
#             df[code_col].ne('()')
#             ]
#
#     # 🟦 Case 3: Only code_value provided (search all code columns)
#     elif code_val:
#         condition = None
#         for col in code_columns:
#             if col in df.columns:
#                 df[col] = df[col].astype(str).str.upper().str.strip()
#                 match = df[col].str.contains(code_val_upper, na=False)
#                 condition = match if condition is None else condition | match
#         if condition is not None:
#             df = df[condition]
#
#     paginator = Paginator(df.to_dict(orient='records'), 500)
#     page_number = request.GET.get('page', 1)
#     page_obj = paginator.get_page(page_number)
#
#     filter_options = {
#         'payers': sorted(unfiltered_df['PAYERS'].dropna().unique()) if 'PAYERS' in unfiltered_df.columns else [],
#         'payor_categories': sorted(
#             unfiltered_df['PAYOR_CATEGORY'].dropna().unique()) if 'PAYOR_CATEGORY' in unfiltered_df.columns else [],
#         'edits': sorted([e for e in unfiltered_df['EDITS'].dropna().unique() if
#                          e.strip()]) if 'EDITS' in unfiltered_df.columns else [],
#         # 'code_categories': [
#         #     {'label': 'L Codes', 'key': 'L_CODES'},
#         #     {'label': 'E Codes', 'key': 'E_CODES'},
#         #     {'label': 'A Codes', 'key': 'A_CODES'},
#         #     {'label': 'K Codes', 'key': 'K_CODES'},
#         # ]
#     }
#
#     context = {
#         'upload': upload,
#         'data_rows': page_obj.object_list,
#         'page_obj': page_obj,
#         'selected_filters': filters,
#         'filter_options': filter_options,
#     }
#     return render(request, 'view_data.html', context)

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
import pandas as pd
from .models import ExcelUpload, PayerCodeInfo


@login_required
def view_uploaded_data(request, upload_id):
    upload = get_object_or_404(ExcelUpload, pk=upload_id)

    queryset = PayerCodeInfo.objects.filter(upload=upload).values(
        'payers', 'payor_category', 'edits',
        'edit_type', 'enter_code',
        'cpt_edits_sub_category', 'billing_coding_instructions',
        'l_codes', 'e_codes', 'a_codes', 'k_codes',
    )
    df = pd.DataFrame(list(queryset))

    expected_columns = [
        'PAYERS', 'PAYOR_CATEGORY', 'EDITS',
        'EDIT_TYPE', 'ENTER_CODE',
        'CPT_EDITS_SUB_CATEGORY', 'BILLING_CODING_INSTRUCTIONS',
        'L_CODES', 'E_CODES', 'A_CODES', 'K_CODES'
    ]
    if df.empty:
        df = pd.DataFrame(columns=expected_columns)

    # Normalize column names
    df.columns = df.columns.str.strip().str.upper()
    df.dropna(axis=1, how='all', inplace=True)
    df.fillna('', inplace=True)

    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.strip()

    # 🔎 Capture filters from GET
    filters = {
        'payer': request.GET.get('payer', '').strip(),
        'payor_category': request.GET.get('payor_category', '').strip(),
        'edits': request.GET.get('edits', '').strip(),
        'edit_type': request.GET.get('edit_type', '').strip(),
        'enter_code': request.GET.get('enter_code', '').strip().upper(),
        'cpt_edits_sub_category': request.GET.get('cpt_edits_sub_category', '').strip(),
        # 'billing_coding_instructions': request.GET.get('billing_coding_instructions', '').strip(),
        'code_search': request.GET.get('code_search', '').strip().upper(),
        # 🔍 single free-text search across code columns
    }

    unfiltered_df = df.copy()

    # ✅ Apply field filters
    if filters['payer'] and 'PAYERS' in df.columns:
        df = df[df['PAYERS'] == filters['payer']]

    if filters['payor_category'] and 'PAYOR_CATEGORY' in df.columns:
        df = df[df['PAYOR_CATEGORY'] == filters['payor_category']]

    if filters['edits'] and 'EDITS' in df.columns:
        df = df[df['EDITS'] == filters['edits']]

    if filters['edit_type'] and 'EDIT_TYPE' in df.columns:
        df = df[df['EDIT_TYPE'] == filters['edit_type']]

    if filters['enter_code'] and 'ENTER_CODE' in df.columns:
        df['ENTER_CODE'] = df['ENTER_CODE'].astype(str).str.upper().str.strip()
        df = df[df['ENTER_CODE'].str.contains(filters['enter_code'], na=False)]

    if filters['cpt_edits_sub_category'] and 'CPT_EDITS_SUB_CATEGORY' in df.columns:
        df = df[df['CPT_EDITS_SUB_CATEGORY'] == filters['cpt_edits_sub_category']]

    # if filters['billing_coding_instructions'] and 'BILLING_CODING_INSTRUCTIONS' in df.columns:
    #     df = df[df['BILLING_CODING_INSTRUCTIONS'] == filters['billing_coding_instructions']]

    code_search = request.GET.get('code_search', '').strip()

    if code_search and 'ENTER_CODE' in df.columns:
        df['ENTER_CODE'] = df['ENTER_CODE'].astype(str).str.upper().str.strip()
        code_search_upper = code_search.upper()

        # Matches A123 exactly in a comma-separated list (like A123, A456)
        df = df[df['ENTER_CODE'].str.contains(rf'\b{code_search_upper}\b', na=False, regex=True)]

    # ✅ Pagination
    paginator = Paginator(df.to_dict(orient='records'), 500)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # ✅ Dropdown options (no enter_codes included)
    filter_options = {
        'payers': sorted(unfiltered_df['PAYERS'].dropna().unique()) if 'PAYERS' in unfiltered_df.columns else [],
        'payor_categories': sorted(
            unfiltered_df['PAYOR_CATEGORY'].dropna().unique()) if 'PAYOR_CATEGORY' in unfiltered_df.columns else [],
        'edits': sorted([e for e in unfiltered_df['EDITS'].dropna().unique() if
                         e.strip()]) if 'EDITS' in unfiltered_df.columns else [],
        'edit_types': sorted(
            unfiltered_df['EDIT_TYPE'].dropna().unique()) if 'EDIT_TYPE' in unfiltered_df.columns else [],
        'cpt_edits_sub_categories': sorted(unfiltered_df[
                                               'CPT_EDITS_SUB_CATEGORY'].dropna().unique()) if 'CPT_EDITS_SUB_CATEGORY' in unfiltered_df.columns else [],
        # 'billing_coding_instructions': sorted(unfiltered_df['BILLING_CODING_INSTRUCTIONS'].dropna().unique()) if 'BILLING_CODING_INSTRUCTIONS' in unfiltered_df.columns else [],
    }

    context = {
        'upload': upload,
        'data_rows': page_obj.object_list,
        'page_obj': page_obj,
        'selected_filters': filters,
        'filter_options': filter_options,
    }
    return render(request, 'view_data.html', context)


@login_required
def download_filtered_excel(request, upload_id):
    upload = get_object_or_404(ExcelUpload, pk=upload_id)

    # Filter only records related to this upload
    data_qs = PayerCodeInfo.objects.filter(upload=upload)

    if not data_qs.exists():
        return HttpResponse("❌ No data found for this upload ID.", status=404)

    # Convert to DataFrame
    # df = pd.DataFrame.from_records(data_qs.values())
    df = pd.DataFrame.from_records(data_qs.values(
        'payers', 'payor_category', 'edits',
        # 'remarks',
        'edit_type', 'enter_code',
        'billing_coding_instructions',
        # 'type',
        'cpt_edits_sub_category',
        # 'l_codes', 'l_codes_instructions',
        # 'e_codes', 'e_codes_instructions',
        # 'a_codes', 'a_codes_instructions',
        # 'k_codes', 'k_codes_instructions'
    ))
    df.columns = df.columns.str.strip().str.upper()
    df.fillna('', inplace=True)

    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.strip()

    # Filters
    payer_filter = request.GET.get('payer', '').strip()
    payor_category_filter = request.GET.get('payor_category', '').strip()
    edits_filter = request.GET.get('edits', '').strip()
    code_category = request.GET.get('code_category', '').strip().upper()
    code_value = request.GET.get('code_value', '').strip().upper()

    if payer_filter and 'PAYERS' in df.columns:
        df = df[df['PAYERS'] == payer_filter]
    if payor_category_filter and 'PAYOR_CATEGORY' in df.columns:
        df = df[df['PAYOR_CATEGORY'] == payor_category_filter]
    if edits_filter and 'EDITS' in df.columns:
        df = df[df['EDITS'] == edits_filter]
    # if code_category and code_value and code_category in df.columns:
    #     df[code_category] = df[code_category].astype(str).str.upper()
    #     df = df[df[code_category].str.contains(code_value, na=False)]

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = f"filtered_data_upload_{upload_id}.xlsx"
    response['Content-Disposition'] = f'attachment; filename={filename}'

    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='FilteredData')

    return response
