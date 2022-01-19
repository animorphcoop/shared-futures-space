# pyre-strict

from .models import CustomUser, UserPair

system_user = CustomUser.objects.get(id=0, display_name='SYSTEM USER')

def get_userpair(usera: CustomUser, userb: CustomUser):
    if (usera.uuid < userb.uuid):
        return UserPair.objects.get_or_create(user1=usera, user2=userb)[0]
    else:
        return UserPair.objects.get_or_create(user1=userb, user2=usera)[0]
