# Generated by Django 2.2.2 on 2019-06-15 12:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0005_campaign_request'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='request',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='reports.Request'),
        ),
    ]
