# Generated by Django 4.2.11 on 2024-03-15 18:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("wqcontent", "0001_initial"),
        ("sites", "0002_alter_domain_unique"),
        ("wqlinklist", "0001_initial"),
        (
            "taggit",
            "0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx",
        ),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="author",
            name="social_links",
            field=models.ForeignKey(
                blank=True,
                help_text="A list of links to the author's websites and/or social media profiles.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="wqlinklist.linklist",
                verbose_name="social links",
            ),
        ),
        migrations.AddField(
            model_name="attachment",
            name="author",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wqcontent.author",
                verbose_name="author",
            ),
        ),
        migrations.AddField(
            model_name="attachment",
            name="owner",
            field=models.ForeignKey(
                blank=True,
                help_text="The user who created/uploaded the content (for internal permissions, audits).",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="attachment",
            name="site",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="sites.site",
                verbose_name="site",
            ),
        ),
        migrations.AddField(
            model_name="attachment",
            name="tags",
            field=taggit.managers.TaggableManager(
                blank=True,
                help_text="A comma-separated list of tags.",
                through="taggit.TaggedItem",
                to="taggit.Tag",
                verbose_name="Tags",
            ),
        ),
        migrations.AddField(
            model_name="article",
            name="attachment_set",
            field=models.ManyToManyField(
                to="wqcontent.attachment", verbose_name="attachments"
            ),
        ),
        migrations.AddField(
            model_name="article",
            name="author",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wqcontent.author",
                verbose_name="author",
            ),
        ),
        migrations.AddField(
            model_name="article",
            name="image_set",
            field=models.ManyToManyField(
                to="wqcontent.image", verbose_name="related images"
            ),
        ),
        migrations.AddField(
            model_name="article",
            name="owner",
            field=models.ForeignKey(
                blank=True,
                help_text="The user who created/uploaded the content (for internal permissions, audits).",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="article",
            name="section",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="wqcontent.section",
                verbose_name="section",
            ),
        ),
        migrations.AddField(
            model_name="article",
            name="share_image",
            field=models.ForeignKey(
                blank=True,
                help_text="Image for social sharing",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wqcontent.image",
            ),
        ),
        migrations.AddField(
            model_name="article",
            name="site",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="sites.site",
                verbose_name="site",
            ),
        ),
        migrations.AddField(
            model_name="article",
            name="tags",
            field=taggit.managers.TaggableManager(
                blank=True,
                help_text="A comma-separated list of tags.",
                through="taggit.TaggedItem",
                to="taggit.Tag",
                verbose_name="Tags",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="sitevar",
            unique_together={("site", "name")},
        ),
        migrations.AddIndex(
            model_name="section",
            index=models.Index(
                fields=["site", "status", "date_published", "expires"],
                name="wqcontent_s_site_id_4de722_idx",
            ),
        ),
        migrations.AddConstraint(
            model_name="section",
            constraint=models.UniqueConstraint(
                fields=("site", "slug"), name="section_unique_slug_per_site"
            ),
        ),
        migrations.AddIndex(
            model_name="page",
            index=models.Index(
                fields=["site", "status", "date_published", "expires"],
                name="wqcontent_p_site_id_95b25d_idx",
            ),
        ),
        migrations.AddConstraint(
            model_name="page",
            constraint=models.UniqueConstraint(
                fields=("site", "slug"), name="page_unique_slug_per_site"
            ),
        ),
        migrations.AddIndex(
            model_name="image",
            index=models.Index(
                fields=["site", "status", "date_published", "expires"],
                name="wqcontent_i_site_id_35361e_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="homepage",
            index=models.Index(
                fields=["site", "status", "date_published", "expires"],
                name="wqcontent_h_site_id_40a198_idx",
            ),
        ),
        migrations.AddConstraint(
            model_name="author",
            constraint=models.UniqueConstraint(
                fields=("site", "name"), name="unique_author_name_per_site"
            ),
        ),
        migrations.AddIndex(
            model_name="attachment",
            index=models.Index(
                fields=["site", "status", "date_published", "expires"],
                name="wqcontent_a_site_id_9e18e6_idx",
            ),
        ),
        migrations.AddConstraint(
            model_name="article",
            constraint=models.UniqueConstraint(
                fields=("site", "section", "slug"),
                name="article_unique_slug_per_section",
            ),
        ),
    ]
