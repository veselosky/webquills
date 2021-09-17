# Generated by Django 3.2.7 on 2021-09-16 18:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webquills', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='categorypage',
            options={'get_latest_by': 'published', 'ordering': ['site', 'menu_order'], 'verbose_name': 'category page', 'verbose_name_plural': 'category pages'},
        ),
        migrations.AddField(
            model_name='categorypage',
            name='menu_order',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='menu order'),
        ),
        migrations.AddIndex(
            model_name='categorypage',
            index=models.Index(fields=['site', 'menu_order'], name='webquills_c_site_id_7d6bd1_idx'),
        ),
    ]
