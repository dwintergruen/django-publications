# Generated by Django 3.0.5 on 2020-04-16 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0006_type_zotero_types'),
    ]

    operations = [
        migrations.AddField(
            model_name='publication',
            name='zoterokey',
            field=models.CharField(default='', max_length=512),
            preserve_default=False,
        ),
    ]
