from wagtail.core import blocks


class LinkValue(blocks.StructValue):
    """Additional logic for the links"""

    def url(self) -> str:
        external_link = self.get("external_link")
        return external_link.url


class Link(blocks.StructBlock):
    link_text = blocks.CharBlock(max_length=50, default="More Details")
    external_link = blocks.URLBlock(required=False)

    class Meta:
        value_class = LinkValue


class RichTextSimpleBlock(blocks.StructBlock):
    content = blocks.RichTextBlock(features=["bold", "italic", "ol", "ul", "link"])

    class Meta:
        template = "streams/simple_richtext_block.html"
