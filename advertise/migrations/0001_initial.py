# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-07 14:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Advertise',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num', models.PositiveIntegerField(default=0, null=True)),
                ('title', models.CharField(max_length=255)),
                ('event_start', models.DateTimeField()),
                ('event_end', models.DateTimeField()),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_active', models.BooleanField(default=False)),
                ('link', models.CharField(blank=True, max_length=255, null=True)),
                ('banner', models.ImageField(upload_to='banner')),
                ('banner_md', models.ImageField(blank=True, null=True, upload_to='banner')),
                ('banner_sm', models.ImageField(blank=True, null=True, upload_to='banner')),
                ('sort', models.CharField(choices=[('main_advertise', 'main_advertise'), ('sub_top', 'sub_top'), ('profile_top', 'profile_top'), ('community_right', 'community_right')], max_length=255)),
            ],
            options={
                'ordering': ('-num', 'banner'),
            },
        ),
    ]