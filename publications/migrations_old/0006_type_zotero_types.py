# Generated by Django 3.0.5 on 2020-04-16 08:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0005_collection'),
    ]

    operations = [
        migrations.AddField(
            model_name='type',
            name='zotero_types',
            field=models.CharField(default='', help_text='Possible Zotero types, separated by comma.', max_length=256, verbose_name='zotero type'),
        ),
    ]