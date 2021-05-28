from django.apps import apps
from django.contrib.syndication.views import Feed
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.feedgenerator import Rss201rev2Feed

from webquills.core.models import ArticlePage, CategoryPage, HomePage, Image

# This file is organized into sections:
# 1. HTML Views that display pages
# 2. XML/JSON views (feeds and utilities)


#######################################################################
# HTML Views
#######################################################################


def archive(request, pagenum: int = 1):
    wq = apps.get_app_config("webquills")
    # We use the homepage template, but no CTA or featured articles
    page = HomePage.objects.live().filter(site=request.site).latest()
    template = page.get_template()
    pg = Paginator(ArticlePage.objects.live(), wq.pagelength).get_page(pagenum)
    context = {
        "page": page,
        "pg": pg,
        "recent_articles": pg.object_list,
        "topmenu": CategoryPage.objects.live(),
    }
    return render(request, template, context)


def article(request, category_slug, article_slug):
    page = get_object_or_404(
        ArticlePage.objects.live(),
        site=request.site,
        slug=article_slug,
        category__slug=category_slug,
    )
    template = page.get_template()
    context = {
        "page": page,
        "topmenu": CategoryPage.objects.live(),
    }
    return render(request, template, context)


def category(request, category_slug: str, pagenum: int = 1):
    page = get_object_or_404(
        CategoryPage.objects.live(), site=request.site, slug=category_slug
    )
    template = page.get_template()
    wq = apps.get_app_config("webquills")

    # The category page wants a list of featured articles, and a list of recent articles.
    pg = Paginator(
        ArticlePage.objects.live().filter(category=page), wq.pagelength
    ).get_page(pagenum)
    featured_articles = ArticlePage.objects.live().filter(
        tags__name__in=[wq.featured_tag],
        category=page,
    )[: wq.num_featured]

    context = {
        "featured_articles": featured_articles,
        "page": page,
        "pg": pg,
        "recent_articles": pg.object_list,
        "topmenu": CategoryPage.objects.live(),
    }
    return render(request, template, context)


def homepage(request):
    wq = apps.get_app_config("webquills")
    # The most recently published live home page. This allows you to schedule a new
    # home page without disturbing the existing one.
    page = HomePage.objects.live().filter(site=request.site).latest()
    template = page.get_template()

    # The home page wants a list of featured articles, and a list of recent articles.
    pg = Paginator(ArticlePage.objects.live(), wq.pagelength).get_page(1)
    featured_articles = ArticlePage.objects.live().filter(
        tags__name__in=[wq.homepage_featured_tag]
    )[: wq.num_featured]

    # If a call to action module is defined, set up the data structure
    cta = None
    if page.target_url:
        cta = {
            "headline": page.headline,
            "lead": page.lead,
            "action_label": page.action_label,
            "link": page.target_url,
            "picture": page.picture,
        }

    context = {
        "cta": cta,
        "featured_articles": featured_articles,
        "page": page,
        "pg": pg,
        "recent_articles": pg.object_list,
        "topmenu": CategoryPage.objects.live(),
    }
    return render(request, template, context)


#######################################################################
# XML/JSON Views
#######################################################################


# Custom feeds are not very well documented. This snippet shows how to
# do this: https://djangosnippets.org/snippets/2202/
class ContentFeed(Rss201rev2Feed):
    "Feed generator supporting content:encoded element"

    def root_attributes(self):
        attrs = super().root_attributes()
        attrs["xmlns:content"] = "http://purl.org/rss/1.0/modules/content/"
        return attrs

    def add_item_elements(self, handler, item):
        super().add_item_elements(handler, item)
        handler.addQuickElement("content:encoded", item["content_encoded"])


class SiteFeed(Feed):
    "RSS feed of site ArticlePages"
    feed_type = ContentFeed

    def get_object(self, request, *args, **kwargs):
        "For site feed, get_object will return the site"
        return request.site

    def title(self, obj):
        return f"{obj.meta.name} -- {obj.meta.tagline}"

    def link(self, obj):
        return reverse("home")

    def description(self, obj):
        page = HomePage.objects.live().filter(site=obj).latest()
        return page.seo_description

    def feed_url(self, obj):
        return reverse("site-feed")

    def author_name(self, obj):
        if obj.meta.author:
            return obj.meta.author.byline
        return None

    def feed_copyright(self, obj):
        page = HomePage.objects.live().filter(site=obj).latest()
        return page.copyright_notice

    def items(self, obj):
        wq = apps.get_app_config("webquills")
        return ArticlePage.objects.live().filter(site=obj)[: wq.pagelength]

    def item_title(self, item):
        return item.headline

    def item_description(self, item):
        return item.seo_description

    def item_link(self, item):
        return item.get_absolute_url()

    def item_author_name(self, item):
        return item.byline

    def item_pubdate(self, item):
        return item.published

    def item_updateddate(self, item):
        return item.updated

    def item_copyright(self, item):
        return item.copyright_notice

    def item_extra_kwargs(self, item):
        return {"content_encoded": self.item_content_encoded(item)}

    def item_content_encoded(self, item):
        return item.excerpt


class CategoryFeed(SiteFeed):
    "Feed of Articles in a specified category"

    def get_object(self, request, *args, **kwargs):
        "Return the CategoryPage for this feed"
        return CategoryPage.objects.live().get(site=request.site, slug=kwargs["slug"])

    def title(self, obj):
        return obj.headline

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return obj.seo_description

    def feed_url(self, obj):
        return reverse("category-feed", kwargs={"slug": obj.slug})

    def author_name(self, obj):
        return obj.byline

    def feed_copyright(self, obj):
        return obj.copyright_notice

    def items(self, obj):
        wq = apps.get_app_config("webquills")
        return ArticlePage.objects.live().filter(category=obj)[: wq.pagelength]


def tiny_image_list(request):
    """
    Returns a list of recently uploaded images, formatted for use by the TinyMCE
    editor.
    """
    config = apps.get_app_config("webquills")
    width, height = config.get_default_image_size()
    images = Image.objects.order_by("created_at")[:24]
    result = [
        {
            "title": img.name,
            "value": img.get_thumb("resize", width=width, height=height).url,
        }
        for img in images
    ]
    return JsonResponse(result, safe=False)
