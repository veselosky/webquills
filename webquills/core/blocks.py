###############################################################################
# Copied from bakerydemo and then modified.
###############################################################################

from wagtail.images.blocks import ImageChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.core.blocks import (
    CharBlock,
    ChoiceBlock,
    RichTextBlock,
    StreamBlock,
    StructBlock,
    TextBlock,
)


class ImageBlock(StructBlock):
    """Image with associated caption"""

    image = ImageChooserBlock(required=True)
    caption = CharBlock(required=False)

    class Meta:
        icon = "image"
        template = "webquills/blocks/image_block.html"


class HeadingBlock(StructBlock):
    "A link-targetable subhead."

    heading_text = CharBlock(classname="title", required=True)
    size = ChoiceBlock(
        choices=[("h2", "H2"), ("h3", "H3"), ("h4", "H4"), ("h5", "H5"), ("h6", "H6")],
        blank=False,
        required=True,
        default="h2",
    )

    class Meta:
        icon = "title"
        template = "webquills/blocks/heading_block.html"


class BlockQuote(StructBlock):
    """Blockquote with citation"""

    text = TextBlock()
    citation = CharBlock(blank=True, required=False, label="e.g. Mary Berry")

    class Meta:
        icon = "fa-quote-left"
        template = "webquills/blocks/blockquote.html"


# StreamBlocks
class BaseStreamBlock(StreamBlock):
    """
    Define the custom blocks that `StreamField` will utilize
    """

    heading_block = HeadingBlock()
    text_block = RichTextBlock()
    image_block = ImageBlock()
    block_quote = BlockQuote()
    embed_block = EmbedBlock(
        help_text="Insert an embed URL e.g https://www.youtube.com/embed/SGJFWirQ3ks",
        icon="fa-s15",
        template="webquills/blocks/embed_block.html",
    )
