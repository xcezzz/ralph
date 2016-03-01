# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0009_auto_20160229_1655'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssetExtra',
            fields=[
                ('baseobject_ptr', models.OneToOneField(auto_created=True, primary_key=True, serialize=False, parent_link=True, to='assets.BaseObject')),
                ('content', models.TextField(null=True, verbose_name='Extra Content', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('assets.baseobject',),
        ),
        migrations.AlterField(
            model_name='assetmodel',
            name='root_password',
            field=models.TextField(null=True, verbose_name='Root Password', blank=True),
        ),
    ]
