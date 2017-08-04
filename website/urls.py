from django.conf.urls import url, include
from django.conf.urls.static import static

from patchouli import settings
import website.views as views

urlpatterns = [
    url(r'^$', views.IndexView.as_view()),
    url(r'^problem/(?P<name>\w+)$', views.ProblemView.as_view()),
    url(r'^binary/(?P<hash>\w+)$', views.BinaryView.as_view()),
    url(r'^api/new_patch$', views.ApiNewPatchView.as_view()),
    url(r'^api/new_attack$', views.ApiNewAttackView.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
