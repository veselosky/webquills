# Generated by Django 3.2 on 2021-06-06 19:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('webquills', '0002_delete_sitemeta'),
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.CreateModel(
            name='Site',
            fields=[
                ('site_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='sites.site')),
                ('tagline', models.CharField(blank=True, help_text='Subtitle. A few words letting visitors know what to expect.', max_length=255, null=True, verbose_name='tagline')),
                ('author', models.ForeignKey(blank=True, help_text='Default author for any page without an explicit author', null=True, on_delete=django.db.models.deletion.SET_NULL, to='webquills.author', verbose_name='author')),
            ],
            options={
                'verbose_name': 'site',
                'verbose_name_plural': 'sites',
            },
            bases=('sites.site',),
        ),
    ]
