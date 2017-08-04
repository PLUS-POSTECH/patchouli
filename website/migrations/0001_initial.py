# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-29 07:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Binary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hash', models.CharField(max_length=100, unique=True)),
                ('sla_status', models.CharField(choices=[('OK', 'OK'), ('FAIL', 'FAIL'), ('UNKNOWN', 'UNKNOWN')], default='UNKNOWN', max_length=10)),
                ('description', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Patch',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('binary', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='website.Binary')),
            ],
        ),
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='patch',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='website.Team'),
        ),
        migrations.AddField(
            model_name='binary',
            name='problem',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='website.Problem'),
        ),
    ]
