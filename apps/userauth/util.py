# pyre-strict

from .models import CustomUser, UserPair

system_user: CustomUser = CustomUser.objects.get_or_create(id=0, display_name='SYSTEM USER')[0] # pyre-ignore[16]

def get_userpair(usera: CustomUser, userb: CustomUser) -> UserPair:
    if (usera.uuid < userb.uuid):
        return UserPair.objects.get_or_create(user1=usera, user2=userb)[0] # pyre-ignore[16]
    else:
        return UserPair.objects.get_or_create(user1=userb, user2=usera)[0]
