from .models import CustomUser, UserPair


def get_system_user() -> CustomUser:
    return CustomUser.objects.get_or_create(id=0, display_name="salmon")[0]


def get_userpair(usera: CustomUser, userb: CustomUser) -> UserPair:
    if usera.uuid < userb.uuid:
        return UserPair.objects.get_or_create(user1=usera, user2=userb)[0]
    else:
        return UserPair.objects.get_or_create(user1=userb, user2=usera)[0]


def user_to_slug(user: CustomUser) -> str:
    return f"{str(user.display_name).replace(' ','-')}-{str(user.pk)}".lower()


def slug_to_user(slug: str) -> CustomUser:
    return CustomUser.objects.get(pk=int(slug.rsplit("-")[-1]))
