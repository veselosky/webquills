# Generated by Django 3.2 on 2021-05-30 11:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.CreateModel(
            name='LinkCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='name')),
                ('slug', models.SlugField(verbose_name='slug')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sites.site', verbose_name='site')),
            ],
            options={
                'verbose_name': 'link list',
                'verbose_name_plural': 'link lists',
                'unique_together': {('site', 'slug')},
            },
        ),
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=255, verbose_name='URL')),
                ('text', models.CharField(max_length=50, verbose_name='text')),
                ('icon', models.CharField(default='link-45deg', help_text='<a href=https://icons.getbootstrap.com/#icons target=iconlist>icon list</a>', max_length=50, verbose_name='icon')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='links', to='linkmgr.linkcategory', verbose_name='list')),
            ],
            options={
                'verbose_name': 'link',
                'verbose_name_plural': 'links',
                'order_with_respect_to': 'category',
            },
        ),
    ]