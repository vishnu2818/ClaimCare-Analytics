# Generated by Django 5.2.1 on 2025-06-17 10:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rcm_app', '0002_remove_payercodeinfo_dummy_field_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='payercodeinfo',
            name='upload',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='rcm_app.excelupload'),
        ),
    ]
