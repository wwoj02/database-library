from django.contrib import admin
from django.urls import path
from libraryapp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('add_book/', views.add_book, name='add_book'),
    path('most_borrowed/', views.add_book, name='most_borrowed'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
    path('books/', views.display_books, name='display_books'),
    path('users/', views.users, name='users'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('profile/', views.update_profile, name='profile'),
    path("update-user-roles/", views.users, name="update_user_roles"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
