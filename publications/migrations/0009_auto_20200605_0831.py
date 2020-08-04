# Generated by Django 3.0.5 on 2020-06-05 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0008_auto_20200605_0451'),
    ]

    operations = [
        migrations.AddField(
            model_name='publication',
            name='has_TEI',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='publication',
            name='has_abstract',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='publication',
            name='has_body',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='publication',
            name='has_html',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='publication',
            name='has_pdf',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='publication',
            name='has_pdf_text',
            field=models.BooleanField(default=False),
        ),
    ]
