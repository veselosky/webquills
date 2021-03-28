"Tests for custom webquills blocks."
from webquills.core import blocks


def test_heading_block():
    "Check that a heading block will render"
    blk = blocks.HeadingBlock()
    html = blk.render(
        blk.to_python(
            {
                "heading_text": "My Heading",
                "size": "h2",
            }
        )
    )
    assert '<h2 id="my-heading">My Heading' in html
    assert '<a href="#my-heading"' in html
