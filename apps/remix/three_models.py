from os.path import splitext

from django.conf import settings
from django.core.files.storage import default_storage

REMIX_MODEL_URL = f"{settings.MEDIA_URL}remix/models/"
REMIX_MODEL_PREVIEW_URL = f"{REMIX_MODEL_URL}/png/"


def list_three_models():
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
                        "previewUrl": f"{REMIX_MODEL_PREVIEW_URL}{name}.png",
                        "modelUrl": f"{REMIX_MODEL_URL}{filename}",
                    }
                )
    return models
