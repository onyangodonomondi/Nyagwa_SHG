# Generated by Django 5.1 on 2024-08-31 20:05

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('date', models.DateField()),
                ('required_amount', models.DecimalField(decimal_places=2, default=200.0, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('surname', models.CharField(max_length=100)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('phone_number', models.CharField(max_length=15)),
                ('birthdate', models.DateField(blank=True, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('location_type', models.CharField(choices=[('village', 'Village'), ('town', 'Town')], default='Unknown', max_length=10)),
                ('town_name', models.CharField(blank=True, choices=[('Nairobi', 'Nairobi'), ('Mombasa', 'Mombasa'), ('Kisumu', 'Kisumu'), ('Nakuru', 'Nakuru'), ('Eldoret', 'Eldoret')], max_length=100, null=True)),
                ('has_children', models.BooleanField(blank=True, null=True)),
                ('number_of_children', models.PositiveIntegerField(blank=True, null=True)),
                ('date_of_registration', models.DateField(default=datetime.date.today, editable=False, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Contribution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contributions', to='members.event')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contributions', to='members.member')),
            ],
        ),
    ]
