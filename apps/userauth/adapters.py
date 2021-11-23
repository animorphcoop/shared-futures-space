# pyre-strict

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        u = sociallogin.user
        if 'first_name' in data and 'last_name' in data:
            u.display_name = data['first_name'] + " " + data['last_name']
        else:
            u.display_name = 'New User'
        if 'email' in data:
            u.email = data['email']
        return u
