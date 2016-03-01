# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_center', '0008_auto_20160229_1700'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datacenterasset',
            name='root_password',
            field=models.CharField(null=True, blank=True, verbose_name='Root PW', max_length=255, help_text='Root Password'),
        ),
    ]
