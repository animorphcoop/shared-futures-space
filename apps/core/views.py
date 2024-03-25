from typing import Optional


class HTMXMixin:
    """Mixin to allow specifying separate templates for htmx requests"""

    template_name_htmx: Optional[str] = None

    def get_template_names(self):
        if self.request.htmx and self.template_name_htmx:
            return [self.template_name_htmx]
        return super().get_template_names()
