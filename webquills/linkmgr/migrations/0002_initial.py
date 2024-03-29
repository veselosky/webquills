# Generated by Django 3.2 on 2021-06-07 17:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sites', '0001_initial'),
        ('linkmgr', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='linkcategory',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='link_lists', to='sites.site', verbose_name='site'),
        ),
        migrations.AddField(
            model_name='link',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='links', to='linkmgr.linkcategory', verbose_name='list'),
        ),
        migrations.AlterUniqueTogether(
            name='linkcategory',
            unique_together={('site', 'slug')},
        ),
        migrations.AlterOrderWithRespectTo(
            name='link',
            order_with_respect_to='category',
        ),
    ]
