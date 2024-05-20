from os.path import basename
from typing import Optional
from PIL import Image
from django.core.files.base import ContentFile


def ensure_image_field_crop(image_field, target_aspect_ratio: float):
    with Image.open(image_field.file) as img:
        cropped = crop_image(img, target_aspect_ratio)
        if cropped:
            cropped.save(image_field.path)


def crop_image(image, target_aspect_ratio: float):
    width, height = image.size
    aspect_ratio = width / height
    # TODO: skip cropping if ratio is VERY close?
    if aspect_ratio > target_aspect_ratio:
        # wider than 16/9
        # need to modify width
        new_width = target_aspect_ratio * height
        offset = int(abs(width - new_width) / 2)
        return image.crop([offset, 0, width - offset, height])
    elif aspect_ratio < target_aspect_ratio:
        # taller than 16 / 9
        # need to modify height
        new_height = width / target_aspect_ratio
        offset = int(abs(new_height - height) / 2)
        return image.crop([0, offset, width, height - offset])


def copy_image_field(field):
    """Copy an image from one model's field to another

    Does the copy in-memory, good enough for now...
    """
    copied_image = ContentFile(field.file.read())
    copied_image.name = basename(field.name)
    return copied_image
