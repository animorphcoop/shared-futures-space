from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()

DJANGO_VITE_DEV_MODE = getattr(settings, "DJANGO_VITE_DEV_MODE", False)


@register.simple_tag
@mark_safe
def sfs_vite_prevent_unstyled_flash(*args):
    """Prevent a flash of unstyled html for full page loads in dev mode

    Without this, as the CSS is loaded with vite via js module,
    there is a delay between when the browser has received all the
    html and when the CSS is ready.

    This hides sets visibility: hidden on the body until later on...

    The "DOMContentLoaded" event fires when all deferred scripts have
    been executed, and vite has injected the CSS by then.
    """
    if not DJANGO_VITE_DEV_MODE:
        return ""

    return """
        <script>
            if (!window.__sfs_vite_prevent_unstyled_flash) {
                document.body.style.visibility = 'hidden'
            }
            window.addEventListener('DOMContentLoaded', () => {
                window.__sfs_vite_prevent_unstyled_flash = true
                document.body.style.visibility = ''
            })
        </script>
        """
