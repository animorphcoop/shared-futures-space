# pyre-strict
from django.conf import settings
from django.urls import include, path, URLResolver, URLPattern
from .views import CustomUserUpdateView, CustomUserDeleteView, CustomUserProfileView
from typing import List, Union

urlpatterns: List[Union[URLResolver, URLPattern]] = [
    #path('profile/', profile_view, name='account_profile'),
    path('<int:pk>/view/', CustomUserProfileView.as_view(template_name='account/view.html'), name='account_view'),
    path('<int:pk>/update/', CustomUserUpdateView.as_view(template_name='account/update.html'), name='account_update'),
    path('<int:pk>/delete/', CustomUserDeleteView.as_view(template_name='account/delete.html'), name='account_delete'),

]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    import debug_toolbar
    # Serve static and media files from development server
    MIDDLEWARE_CLASSES: List[str] = ['debug_toolbar.middleware.DebugToolbarMiddleware',]
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
