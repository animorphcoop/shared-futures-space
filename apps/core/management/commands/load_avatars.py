import json

from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from userauth.models import UserAvatar

DATA_DIR = "dev/autoupload/"


def add_avatars(avatars_data):
    for avatar_data in avatars_data:
        try:
            with open(DATA_DIR + avatar_data["avatar"], "rb") as f:
                new_avatar = UserAvatar.objects.create()
                new_avatar.avatar = ImageFile(f)
                new_avatar.save()
        except Exception as e:
            print(
                "could not add avatar with definition: "
                + str(avatar_data)
                + "\nerror given: "
                + repr(e)
            )


class Command(BaseCommand):
    help = "import avatar data"

    def add_arguments(self, parser):
        parser.add_argument("datafile", nargs="?", type=str)

    def handle(self, *args, **options):
        try:
            f = open(options["datafile"])
            try:
                data = json.load(f)
            except:
                print("could not parse valid json from " + options["datafile"])
                exit()
            f.close()
        except:
            print("could not read from file: " + options["datafile"])
            exit()

        add_avatars(data["User Avatars"])
