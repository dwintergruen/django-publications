# Generated by Django 3.0.5 on 2020-04-16 12:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import filer.fields.file
import filer.fields.image


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.FILER_IMAGE_MODEL),
        ('filer', '0011_auto_20190418_0137'),
        ('publications', '0014_person_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='PDFAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zoterokey', models.CharField(max_length=30)),
                ('file', filer.fields.file.FilerFileField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='filer.File')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='publications.Publication')),
            ],
        ),
        migrations.CreateModel(
            name='ImageAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zoterokey', models.CharField(max_length=30)),
                ('file', filer.fields.image.FilerImageField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.FILER_IMAGE_MODEL)),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='publications.Publication')),
            ],
        ),
    ]
