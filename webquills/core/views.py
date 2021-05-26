from django.apps import apps
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from webquills.core.models import ArticlePage, CategoryPage, HomePage, Image


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
