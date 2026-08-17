from django.contrib import admin
from django.urls import path, include # Thêm include
from django.urls import path
from courses.views import github_webhook  # Sửa 'ten_app_cua_ban' thành tên app chứa file views.py ở Bước 1
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('courses.urls')), # Thêm dòng này
    path('accounts/', include('allauth.urls')),
    path('webhook/update/', github_webhook, name='github_webhook'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)