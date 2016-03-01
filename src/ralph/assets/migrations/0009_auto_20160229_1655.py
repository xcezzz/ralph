# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0008_auto_20160122_1429'),
    ]

    operations = [
        migrations.AddField(
            model_name='assetmodel',
            name='root_password',
            field=models.TextField(verbose_name='Root Password', max_length=255, default="")
        ),
    ]
