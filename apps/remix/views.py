from os.path import isdir, splitext
from django.core.files.storage import default_storage
from django.views.generic import TemplateView


from sfs import settings

REMIX_MODEL_DIR = f"{settings.MEDIA_URL}remix/models"
REMIX_MODEL_PNG_DIR = f"{REMIX_MODEL_DIR}/png"


class RemixView(TemplateView):
    template_name = "remix/remix.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        storage = default_storage
        models = []
        if storage.exists("remix/models"):
            _, filenames = storage.listdir("remix/models")
            for filename in sorted(filenames):
                name, ext = splitext(filename)
                if ext == ".glb":
                    models.append(
                        {
                            "name": name,
                            "previewUrl": f"{REMIX_MODEL_PNG_DIR}/{name}.png",
                            "modelUrl": f"{REMIX_MODEL_DIR}/{filename}",
                        }
                    )

        context["models"] = models
        return context
