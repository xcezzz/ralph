# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('data_center', '0007_auto_20160225_1818'),
    ]

    operations = [
        migrations.AddField(
            model_name='datacenterasset',
            name='root_password',
            field=models.TextField(verbose_name='Root Password', max_length=255, default="")
        ),
    ]
