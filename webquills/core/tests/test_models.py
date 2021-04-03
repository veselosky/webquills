from datetime import datetime
import json

import pytest

from webquills.core.blocks import RichTextBlock
from webquills.core.models import ArticlePage


@pytest.mark.django_db
def test_article_excerpt():
    page = ArticlePage(
        title="Test Page",
        body=json.dumps(
            [
                {"type": "text", "value": "This is the first block.", "id": "1"},
                {"type": "text", "value": "This is the second block.", "id": "2"},
            ]
        ),
    )
    assert str(page.excerpt) == "This is the first block."


@pytest.mark.django_db
def test_article_published_previously():
    expect = datetime(2020, 1, 1)
    page = ArticlePage(
        title="test page",
        live=True,
        first_published_at=datetime.now(),
        orig_published_at=expect,
    )

    assert page.published == expect
    assert page.updated == expect


@pytest.mark.django_db
def test_article_published_future():
    expect = datetime(2022, 1, 1)
    page = ArticlePage(
        title="test page",
        live=False,
        go_live_at=expect,
    )

    assert page.published == expect
    assert page.updated == expect


@pytest.mark.django_db
def test_article_updated():
    expect = datetime(2021, 1, 1)
    xmas = datetime(2020, 12, 25)
    page = ArticlePage(
        title="test page",
        live=True,
        first_published_at=xmas,
        updated_at=expect,
    )

    assert page.published == xmas
    assert page.updated == expect
