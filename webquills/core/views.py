from django.apps import apps
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from webquills.core.models import ArticlePage, CategoryPage, HomePage, Image


def homepage(request):
    # The most recently published live home page. This allows you to schedule a new
    # home page without disturbing the existing one.
    page = HomePage.objects.live().latest()
    template = page.get_template()

    # The home page wants a list of featured articles, and a list of recent articles.
    # TODO These hard-coded values for slice size and tag should be configurable.
    recent_articles = ArticlePage.objects.live()[:26]
    featured_articles = ArticlePage.objects.live().filter(
        tags__name__in=["hpfeatured"]
    )[:4]

    context = {
        "page": page,
        "featured_articles": featured_articles,
        "recent_articles": recent_articles,
        "topmenu": CategoryPage.objects.live(),
    }
    return render(request, template, context)


def category(request, category_slug):
    page = get_object_or_404(CategoryPage.objects.live(), slug=category_slug)
    template = page.get_template()

    # The category page wants a list of featured articles, and a list of recent articles.
    # TODO These hard-coded values for slice size and tag should be configurable.
    recent_articles = ArticlePage.objects.live().filter(category=page)[:26]
    featured_articles = ArticlePage.objects.live().filter(
        tags__name__in=["featured"],
        category=page,
    )[:4]

    context = {
        "page": page,
        "featured_articles": featured_articles,
        "recent_articles": recent_articles,
        "topmenu": CategoryPage.objects.live(),
    }
    return render(request, template, context)


def article(request, category_slug, article_slug):
    page = get_object_or_404(
        ArticlePage.objects.live(), slug=article_slug, category__slug=category_slug
    )
    template = page.get_template()
    context = {
        "page": page,
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
