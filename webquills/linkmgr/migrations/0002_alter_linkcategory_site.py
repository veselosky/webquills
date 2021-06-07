# Generated by Django 3.2 on 2021-06-07 11:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wqsites', '0001_initial'),
        ('linkmgr', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='linkcategory',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='link_lists', to='wqsites.site', verbose_name='site'),
        ),
    ]
