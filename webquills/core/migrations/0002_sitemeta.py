# Generated by Django 3.1.7 on 2021-03-30 12:21

from django.db import migrations, models
import django.db.models.deletion
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0060_fix_workflow_unique_constraint'),
        ('webquills', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteMeta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tagline', models.CharField(blank=True, help_text='Subtitle. A few words letting visitors know what to expect.', max_length=255, null=True, verbose_name='tagline')),
                ('copyright_holder', models.CharField(default='WebQuills', help_text='Owner of the copyright (in footer notice)', max_length=255, verbose_name='copyright holder')),
                ('copyright_license_notice', wagtail.core.fields.RichTextField(default='All rights reserved.', help_text='Text to follow the copyright notice indicating any license, e.g. CC-BY', verbose_name='copyright license notice')),
                ('site', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, to='wagtailcore.site')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]