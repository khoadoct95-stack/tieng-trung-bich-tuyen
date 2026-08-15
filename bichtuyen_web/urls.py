from django.contrib import admin
from django.urls import path, include # Thêm include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('courses.urls')), # Thêm dòng này
    path('accounts/', include('allauth.urls')),
]