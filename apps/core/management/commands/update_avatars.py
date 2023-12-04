import filecmp
import json
from os.path import join, basename, splitext

from django.core.files.images import ImageFile
from django.core.management import BaseCommand

from core.management.commands.loaddevdata import DATA_DIR
from userauth.models import UserAvatar


class Command(BaseCommand):
    help = "update already imported avatars"

    def add_arguments(self, parser):
        parser.add_argument("datafile", nargs="?", type=str)

    def handle(self, *args, **options):
        with open(options["datafile"]) as f:
            data = json.load(f)
            avatars_data = data["User Avatars"]
            for avatar_data in avatars_data:
                update_avatar(avatar_data)


def update_avatar(avatar_data):
    user_avatars = list(UserAvatar.objects.all())
    avatar_path = join(DATA_DIR, avatar_data["avatar"])
    with open(avatar_path, "rb") as f:
        avatar_filename = basename(avatar_data["avatar"])
        avatar_basename = splitext(avatar_filename)[0]
        existing_avatar = None
        for user_avatar in user_avatars:
            # Check for a matching existing one, they have filenames like
            # avatarname_OI3nqeM.png and we need to match without the random bit
            user_avatar_basename = splitext(basename(user_avatar.avatar.name))[0]
            if user_avatar_basename.startswith(avatar_basename):
                existing_avatar = user_avatar
                break
        if existing_avatar:
            if filecmp.cmp(avatar_path, existing_avatar.avatar.path):
                print("nochange", avatar_filename)
            else:
                existing_avatar.avatar = ImageFile(f)
                existing_avatar.save()
                print("updated", avatar_filename)
        else:
            new_avatar = UserAvatar.objects.create()
            new_avatar.avatar = ImageFile(f)
            new_avatar.save()
            print("added", avatar_filename)
