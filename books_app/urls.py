from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, BookViewSet, PretViewSet, EmpruntViewSet, RatingViewSet
from . import views
from django.conf import settings
from django.conf.urls.static import static


# Créer une instance de DefaultRouter
router = DefaultRouter()
from .views import   User , Rating , Pret , Emprunt
app_name = 'books_app'
# Enregistrer les ViewSets avec le routeur
router.register(r'users', UserViewSet)
router.register(r'books', BookViewSet)
router.register(r'prets', PretViewSet)
router.register(r'emprunts', EmpruntViewSet)
router.register(r'ratings', RatingViewSet)

# Inclure les URLs générées par le routeur dans urlpatterns
urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('home/', views.home, name='home'),
    path('user_profile/', views.user_profile, name='user_profile'),
    path('profil/', views.profil_view, name='profil_view'),
    path('page_rec/', views.page_rec, name='page_rec'),
    path('delete-book/<int:book_id>/', views.delete_book, name='delete_book'),
    path('book_detail/<int:book_id>/', views.book_detail, name='book_detail'),
    path('submit_rating/<int:book_id>/', views.submit_rating, name='submit_rating'),
    path('search/', views.search_books, name='search_books'),  # URL pour la recherche et filtrage
    path('reserve_book/<int:book_id>/', views.reserve_book, name='reserve_book'),
    path('borrow_book/<int:book_id>/', views.borrow_book, name='borrow_book'),
    path('categories/', views.categories, name='categories'),  # URL pour la recherche et filtrage
    path('logout/', views.logout_view, name='logout_view'),
    path('change_book_status/<int:book_id>/', views.change_book_status, name='change_book_status'),
    path('follow_author/<int:book_id>/', views.follow_author, name='follow_author'),
    path('follow_publisher/<str:username>/<int:book_id>/', views.follow_publisher, name='follow_publisher'),
    path('view_book/<int:book_id>/', views.view_book, name='view_book'),
    path('genres/<str:genre>/', views.genre_books, name='genre_books'),  # Dynamic URL for each genre
    path('statistics/', views.statistics_view, name='statistics'),  # Dynamic URL for each genre
    path('join_group/<str:group_name>/', views.join_chat_group, name='join_chat_group'),
    path('chat/', views.chat_page, name='chat_page'),  # Default chat page
    path('chat/<str:group_name>/', views.chat_page, name='chat_page'),  # Chat page for specific group
    path('generate_certificate/', views.generate_certificate, name='generate_certificate'),  # Default chat page

]  
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
