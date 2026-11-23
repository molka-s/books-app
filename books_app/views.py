from django.shortcuts import render
from rest_framework import viewsets
from .serializers import UserSerializer, BookSerializer, PretSerializer, EmpruntSerializer, RatingSerializer
from .models import User, Pret, Emprunt, Rating, Book
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class PretViewSet(viewsets.ModelViewSet):
    queryset = Pret.objects.all()
    serializer_class = PretSerializer

class EmpruntViewSet(viewsets.ModelViewSet):
    queryset = Emprunt.objects.all()
    serializer_class = EmpruntSerializer



class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import User


def login_view(request):
    return render(request, 'login.html')


def signup(request):
    if request.method == 'POST':
        # Récupération des données du formulaire
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        if User.objects.filter(email=email).exists():
            # Handle the case where the email is already taken
            return render(request, 'login.html', {'error': 'Email already exists.'})

        # Créer un nouvel utilisateur
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            address=address
        )
        user.save()

    return render(request, 'login.html')



from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from django.shortcuts import render
from .models import Book

# In your view (views.py)
from .models import Book

from .models import Book

def home(request):
    # Retrieve all books from the database
    featured_books = Book.objects.all()[:15]  # Limit to 15 books

    genre_choices = dict(Book.GENRE_CHOICES)  # Convert to a dictionary

    # Convert book genres to a list of tuples (value, label) for each book
    for book in featured_books:
        book_genres = book.genre.split(',')  # Split the genre string into a list
        book.genre = [(genre, genre_choices.get(genre, genre)) for genre in book_genres]  # Map genre values to labels

    # Get the current year

        # Filter books that were published in the current year
    new_arrivals = Book.objects.all()[:10]  # Limit to 10 books


    return render(request, 'home.html', {'featured_books': featured_books , 'new_arrivals': new_arrivals})



    
def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # Email de l'utilisateur
        password = request.POST.get('password')

        # Authentification de l'utilisateur en utilisant l'email comme username
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Si l'utilisateur existe et est authentifié
            login(request, user)
            messages.success(request, "Logged in successfully")
            return redirect('books_app:page_rec')
        else:
            # Si l'authentification échoue
            messages.error(request, "Incorrect email or password")

    return render(request, 'login.html') 

from django.shortcuts import render
from .models import Book, Pret
from datetime import date

def user_profile(request):
    user = request.user  # Utilisateur actuellement connecté

    # Calcul des initiales
    initials = f"{user.first_name[:1].upper()}{user.last_name[:1].upper()}" if user.first_name and user.last_name else "NA"

    # Récupération des données utilisateur
    user_data = {
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'initials': initials,
        'email': user.email,
        'phone': getattr(user, 'phone', 'Not Provided'),  # Utilisation de getattr pour éviter les erreurs
        'address': getattr(user, 'address', 'Not Provided'),
    }

    # Livres prêtés
    prets = Pret.objects.filter(user=user).select_related('book')
    books_data = []
    for pret in prets:
        book = pret.book
        rating = Rating.objects.filter(book=book).first()  # Récupération de la première note (si disponible)
        book_rating = rating.rating if rating else 'Not rated yet'

        books_data.append({
                'id': book.id_book,  # Cela est correct pour ajouter l'ID
                'title': book.title,
                'author': book.author,
                'description': book.description,
                'genre': book.genre,
                'image_url': book.cover_img,
                'rating': book_rating,
                'dispo': "Available" if pret.statut == "dispo" else "Not Available",
})


    # Livres en cours d'emprunt
    in_progress_books = Emprunt.objects.filter(user=user, end_date__gt=date.today()).select_related('book')
    in_progress_books_data = [{
        'title': emprunt.book.title,
        'author': emprunt.book.author,
        'cover_img': emprunt.book.cover_img,
        'start_date': emprunt.start_date,
    } for emprunt in in_progress_books]

    # Livres terminés
    completed_books_emprunt = Emprunt.objects.filter(user=user, end_date__lt=date.today()).select_related('book')
    completed_books_pret = Pret.objects.filter(user=user, statut="dispo").select_related('book')  # Supposant un statut 'completed'

    completed_books_data = [
        {
            'title': completed.book.title,
            'author': completed.book.author,
            'cover_img': completed.book.cover_img,
        } for completed in list(completed_books_emprunt) + list(completed_books_pret)
    ]

    # Contexte pour le template
    context = {
        'user': user_data,
        'books': books_data,
        'in_progress_books': in_progress_books_data,
        'completed_books': completed_books_data,
    }

    return render(request, 'user_profile.html', context)

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from django.contrib import messages

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Book

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Book

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

def delete_book(request, book_id):
    book = get_object_or_404(Book, id_book=book_id)  # Utilisation de get_object_or_404 pour éviter les erreurs
    book.delete()
    messages.success(request, "Book deleted successfully!")
    return redirect('books_app:user_profile')  # Redirection après la suppression






from django.shortcuts import render
from .models import Book, Pret
from django.core.files.storage import FileSystemStorage

from django.core.files.storage import FileSystemStorage
import os
import PyPDF2

from django.core.files.storage import FileSystemStorage
import os
import PyPDF2
from django.http import HttpResponse
from pathlib import Path  # Import pathlib

from django.core.files.storage import FileSystemStorage
import PyPDF2
from django.conf import settings

from django.core.files.storage import FileSystemStorage
from django.conf import settings
from pathlib import Path  # Import pathlib
import PyPDF2
from django.http import HttpResponse
from django.shortcuts import render
from .models import Book, Pret

import os
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .models import Book, Pret
import PyPDF2

def profil_view(request):
    book_genre_choices = Book.GENRE_CHOICES
    language_choices = Book.LANGUAGE_CHOICES

    if request.method == 'POST':
        isbn = request.POST.get('isbn')
        title = request.POST.get('title')
        author = request.POST.get('author')
        description = request.POST.get('description')
        cover_img = request.POST.get('cover_img')
        pub_year = request.POST.get('pub_year')
        genres = request.POST.getlist('genre')
        genre_str = ', '.join(genres)
        period = request.POST.get('period')
        language = request.POST.get('language')
        pdf_version = request.FILES.get('pdf_version')  # Récupérer le fichier PDF

        user = request.user

        # Vérifier si un fichier PDF a été téléchargé
        if pdf_version:
            # Définir l'emplacement du dossier où les fichiers PDF seront sauvegardés
            media_root = os.path.join(settings.BASE_DIR, 'books_app', 'static', 'books_pdf')
            os.makedirs(media_root, exist_ok=True)  # Créer le dossier si nécessaire

            # Sauvegarder le fichier dans le dossier 'books_pdf/'
            fs = FileSystemStorage(location=media_root)
            pdf_filename = fs.save(pdf_version.name, pdf_version)  # Sauvegarder le fichier
            pdf_file_url = fs.url(pdf_filename)  # URL du fichier pour y accéder via le navigateur

            # Compter le nombre de pages du PDF
            try:
                with open(fs.path(pdf_filename), 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    num_pages = len(pdf_reader.pages)
            except Exception as e:
                print(f"Erreur lors de la lecture du PDF : {e}")
                num_pages = 0  # Défaut en cas d'erreur

            # Créer un enregistrement du livre
            book = Book.objects.create(
                isbn=isbn,
                title=title,
                author=author,
                description=description,
                cover_img=cover_img if cover_img else None,
                pub_year=pub_year,
                genre=genre_str,
                language=language,
                pdf_version=pdf_filename,  # Sauvegarder le chemin du PDF
                num_pages=num_pages  # Sauvegarder le nombre de pages du PDF
            )

            # Ajouter une entrée dans la table 'pret' pour ce livre
            Pret.objects.create(
                book=book,
                statut='dispo',  # Par défaut, le livre est disponible
                period=period,
                user=user  # L'utilisateur qui a ajouté le livre
            )

            # Message de succès
            popup_message = "Livre ajouté avec succès!"
            return render(request, 'profil.html', {
                'book_genre_choices': book_genre_choices,
                'language_choices': language_choices,
                'popup_message': popup_message,
            })
        else:
            return HttpResponse("Erreur : Aucun fichier PDF téléchargé.", status=400)

    return render(request, 'profil.html', {
        'book_genre_choices': book_genre_choices,
        'language_choices': language_choices,
    })


    
    

    
    
    

 # books_app/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Book, Rating

from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, Rating
from django.contrib.auth.decorators import login_required
from django.db.models import Avg  # Ajout de l'import de Avg
from django.http import HttpResponse

# Exemple de vue pour afficher les détails du livre et calculer la moyenne des évaluations
from django.shortcuts import render
from .models import Book, Rating
from django.db import models


from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, Rating
from django.db.models import Avg
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Avg
from .models import Book, Rating
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Avg
from .models import Book, Rating
import requests

def get_author_image_url(author_name):
    # Rechercher l'image de l'auteur sur Google Images
    search_url = f"https://www.google.com/search?q={author_name.replace(' ', '+')}+author+photo&tbm=isch"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(search_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        img_tag = soup.find('img')
        if img_tag and 'src' in img_tag.attrs:
            return img_tag.attrs['src']
    return None  # Retourne None si aucune image n'est trouvée

from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Rating, Book
from django.shortcuts import render, get_object_or_404, redirect





 # books_app/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Book, Rating

from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, Rating
from django.contrib.auth.decorators import login_required
from django.db.models import Avg  # Ajout de l'import de Avg
from django.http import HttpResponse

# Exemple de vue pour afficher les détails du livre et calculer la moyenne des évaluations
from django.shortcuts import render
from .models import Book, Rating
from django.db import models


from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, Rating
from django.db.models import Avg
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Avg
from .models import Book, Rating
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Avg
from .models import Book, Rating
import requests

def get_author_image_url(author_name):
    # Rechercher l'image de l'auteur sur Google Images
    search_url = f"https://www.google.com/search?q={author_name.replace(' ', '+')}+author+photo&tbm=isch"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(search_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        img_tag = soup.find('img')
        if img_tag and 'src' in img_tag.attrs:
            return img_tag.attrs['src']
    return None  # Retourne None si aucune image n'est trouvée

from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Rating, Book
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Book, Rating
from django.db.models import Avg
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg
from django.contrib.auth.decorators import login_required
from .models import Book, Rating

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Book, Rating
from django.db.models import Avg
from django.contrib.auth.decorators import login_required




from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import pandas as pd
from .models import Book  

def create_car(book):
    """Combiner les champs pertinents d'un livre pour créer une description complète."""
    return f"{book['title']} {book['author']} {book['description']} {book['genre']}"



def get_similar_books(book_id):
    """Trouver des livres similaires en utilisant k-NN sur la base de la vectorisation TF-IDF."""
    # Récupérer tous les livres de la base de données
    books = Book.objects.all()
    books_df = pd.DataFrame(list(books.values('id_book', 'title', 'author', 'description', 'genre')))
    
    # Créer une colonne 'car' qui combine les informations pertinentes de chaque livre
    books_df['car'] = books_df.apply(lambda x: create_car(x), axis=1)
    
    # Utiliser TF-IDF pour transformer le texte de la colonne 'car'
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(books_df['car'])
    
    # Initialiser k-NN pour la recherche des livres similaires
    knn = NearestNeighbors(n_neighbors=6, metric='cosine', algorithm='brute')
    knn.fit(tfidf_matrix)
    
    # Trouver l'index du livre choisi dans books_df
    book_idx = books_df[books_df['id_book'] == book_id].index[0]
    
    # Obtenir les indices des livres les plus similaires
    distances, indices = knn.kneighbors(tfidf_matrix[book_idx], n_neighbors=6)
    
    # Ignorer le premier résultat (qui est le livre lui-même) et récupérer les livres similaires
    similar_books_indices = indices.flatten()[1:]
    
    # Retourner un DataFrame contenant les livres similaires
    similar_books_df = books_df.iloc[similar_books_indices]
    
    return similar_books_df



@login_required
def book_detail(request, book_id):
    book = get_object_or_404(Book, id_book=book_id)
    user = request.user

    # Calculate the average rating for the book
    average_rating = Rating.objects.filter(book=book).aggregate(Avg('rating'))['rating__avg']
    average_rating = round(average_rating, 1) if average_rating else None

    # Fetch all reviews for the book
    reviews = Rating.objects.filter(book=book).order_by('-created_at').select_related('user')
    similar_books_df = get_similar_books(book_id)
    similar_books = Book.objects.filter(id_book__in=similar_books_df['id_book'].tolist())

    # Get the Pret object (if it exists)
    pret = Pret.objects.filter(book=book).select_related('user').first()
    statut = pret.statut if pret else 'dispo'  # Default to 'dispo'
    # Récupérer la période du livre à partir de la table Pret
    period = pret.period if pret else None  # Si la période est dans Pret
    
    # Vérifier si l'utilisateur a emprunté ce livre
    user = request.user
    emprunt = Emprunt.objects.filter(book=book, user=user, statut='active').first()

    # Vérifier si l'utilisateur peut voir le livre (emprunté)
    can_view_book = emprunt is not None
    book_owner = pret.user if pret else None  # Book owner (user who posted the book)

    # Check borrowing/reservation status
    borrowed_by_user = Emprunt.objects.filter(user=user, book_id=book.id_book, statut='borrowed').exists()
    emprunt_record = Emprunt.objects.filter(user=user, book_id=book.id_book, statut='borrowed').first()
    reading_statut = emprunt_record.reading_statut if emprunt_record else None
    reserved_by_user = Emprunt.objects.filter(user=user, book_id=book.id_book, statut='reserved').exists()
    reserved_by_other = Emprunt.objects.filter(book_id=book.id_book, statut='reserved').exclude(user=user).exists()
    borrowed = Emprunt.objects.filter(book_id=book.id_book, statut='borrowed').exclude(user=user).exists()

    # Following status
    following_author = Following.objects.filter(user=user, followed_name=book.author, role='author').exists()
    following_publisher = Following.objects.filter(user=user, followed_name=book_owner.username, role='publisher').exists() if book_owner else False

    follow_status_list = []
    reviews_and_followers = []  # New list to store review and follower count info

    for review in reviews:
        # Calculate number of reviews for the user
        num_reviews = Rating.objects.filter(user=review.user).count()

        # Calculate number of followers for the user
        num_followers = Following.objects.filter(followed_name=review.user.username).count()

        # Store the review data along with the number of reviews and followers
        review_data = {
            'review': review,
            'num_reviews': num_reviews,
            'num_followers': num_followers
        }
        reviews_and_followers.append(review_data)

        # Check if the user is following the reviewer (publisher)
        follow_status = Following.objects.filter(user=user, followed_name=review.user.username, role='publisher').exists()
        follow_status_list.append({'review_user_id': review.user.id, 'is_following': follow_status})

    # Fetch the book posted by the user
    posted_book = Pret.objects.filter(user_id=user.id, book_id=book.id_book).first()

    # Handle rating/comment form submission
    if request.method == 'POST':
        rating_value = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()

        if rating_value and comment:
            try:
                rating_value = int(rating_value)
                if 1 <= rating_value <= 5:
                    existing_rating = Rating.objects.filter(book=book, user=request.user).first()
                    if existing_rating:
                        # Update existing rating and comment
                        existing_rating.rating = rating_value
                        existing_rating.comment = comment
                        existing_rating.created_at = timezone.now()
                        existing_rating.save()
                        messages.success(request, "Votre note a été mise à jour avec succès !")
                    else:
                        # Create new rating and comment
                        Rating.objects.create(
                            book=book,
                            user=request.user,
                            rating=rating_value,
                            comment=comment,
                            created_at=timezone.now()
                        )
                        messages.success(request, "Votre note et votre commentaire ont été soumis avec succès !")
                else:
                    messages.error(request, "Veuillez fournir une note entre 1 et 5.")
            except ValueError:
                messages.error(request, "Valeur de note invalide. Veuillez entrer un nombre entre 1 et 5.")
        else:
            messages.error(request, "Veuillez fournir à la fois une note et un commentaire.")

        return redirect('books_app:book_detail', book_id=book.id_book)

    # Render the page
    return render(request, 'book_details.html', {
        'book': book,
        'average_rating': average_rating,
        'reviews_and_followers': reviews_and_followers,  # Pass the reviews and followers data
        'follow_status_list': follow_status_list,
        'statut': statut,
        'book_owner': book_owner,
        'following_author': following_author,
        'following_publisher': following_publisher,
        'posted_book': posted_book,
        'borrowed_by_user': borrowed_by_user,
        'reserved_by_user': reserved_by_user,
        'reserved_by_other': reserved_by_other,
        'reading_statut': reading_statut,
        'borrowed': borrowed,
        'pret': pret,
        'period': period,
        'stars': range(1, 6),
        'similar_books': similar_books,
        'language': book.language,
        'num_pages': book.num_pages,
        'can_view_book': can_view_book  # Si l'utilisateur peut voir le livre

    })




def submit_rating (request,book_id):
    book = get_object_or_404(Book, id_book=book_id)
    # Si l'utilisateur soumet un formulaire
    if request.method == 'POST':
        rating_value = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()

        if rating_value and comment:
            try:
                rating_value = int(rating_value)
                if 1 <= rating_value <= 5:
                    existing_rating = Rating.objects.filter(book=book, user=request.user).first()
                    if existing_rating:
                        existing_rating.rating = rating_value
                        existing_rating.comment = comment
                        existing_rating.created_at = timezone.now()
                        existing_rating.save()
                        messages.success(request, "Your rating has been updated successfully!")
                    else:
                        Rating.objects.create(
                            book=book,
                            user=request.user,
                            rating=rating_value,
                            comment=comment,
                            created_at=timezone.now()
                        )
                        messages.success(request, "Your rating and comment have been submitted successfully!")
                else:
                    messages.error(request, "Please provide a rating between 1 and 5.")
            except ValueError:
                messages.error(request, "Invalid rating value. Please enter a number between 1 and 5.")
        else:
            messages.error(request, "Please provide both a rating and a comment.")
        return redirect('books_app:book_detail', book_id=book.id_book)  # Redirection 


    
    
    
    
    
    
    
from django.shortcuts import render
from .models import Book

from django.shortcuts import render
from .models import Book
def search_books(request):
    query = request.GET.get('query', '')  # Term of search

    # Get the selected categories (multiple)
    selected_categories = request.GET.getlist('category')

    # Get the selected years (multiple)
    selected_years = request.GET.getlist('year')

    # Get the selected authors (multiple)
    selected_authors = request.GET.getlist('author')

    # Start with all books
    books = Book.objects.all()

    # Filter by query on title, author, genre, or year
    if query:
        books = books.filter(
            Q(title__icontains=query) | 
            Q(author__icontains=query) |
            Q(genre__icontains=query) |
            Q(pub_year__icontains=query)
        )

    # Filter by categories if selected categories exist
    if selected_categories:
        books = books.filter(genre__in=selected_categories)

    # Filter by years if selected years exist
    if selected_years:
        books = books.filter(pub_year__in=selected_years)

    # Filter by authors if selected authors exist
    if selected_authors:
        books = books.filter(author__in=selected_authors)

    # Get available genres for the checklist
    genres = Book.GENRE_CHOICES

    # Get distinct years available
    available_years = Book.objects.values_list('pub_year', flat=True).distinct()

    # Get distinct authors available
    authors = Book.objects.values_list('author', flat=True).distinct()

    # Retrieve book details for each book (like publisher details)
    book_details = []
    for book in books:
        pret = Pret.objects.filter(book=book).first()
        publisher = pret.user.username if pret else None
        book_details.append({
            'book': book,
            'publisher': publisher
        })

    # Render the page with filtered books and related data
    return render(request, 'search_books.html', {
        'books': books,
        'query': query,
        'selected_categories': selected_categories,
        'selected_years': selected_years,
        'selected_authors': selected_authors,
        'genres': genres,  # For category checkboxes
        'available_years': available_years,  # Available years for filtering
        'authors': authors,  # Available authors for filtering
        'book_details': book_details  # Including publisher information for each book
    })


    
    
    
    
from django.db.models import Avg
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
import numpy as np
from .models import User, Book, Rating

import numpy as np
from collections import defaultdict
from sklearn.metrics.pairwise import cosine_similarity

def get_similar_users_and_books(target_user_id):
    # Step 1: Get the target user's ratings
    target_user_ratings = Rating.objects.filter(user_id=target_user_id)
    
    # Ensure that the target user has rated some books
    if not target_user_ratings:
        return []  # No recommendations if the user has not rated any books

    target_user_ratings_dict = {rating.book.id_book: rating.rating for rating in target_user_ratings}

    # Step 2: Get other users' ratings for the same books the target user has rated
    books_rated_by_target_user = list(target_user_ratings_dict.keys())
    other_users_ratings = Rating.objects.filter(book_id__in=books_rated_by_target_user).exclude(user_id=target_user_id)

    # Step 3: Organize the ratings of both the target and other users
    user_ratings_matrix = defaultdict(lambda: [0] * len(books_rated_by_target_user))
    user_list = []

    for rating in other_users_ratings:
        book_index = books_rated_by_target_user.index(rating.book.id_book)
        user_ratings_matrix[rating.user_id][book_index] = rating.rating
    
    # Convert target user ratings into a vector (list)
    target_user_vector = np.array([target_user_ratings_dict[book] for book in books_rated_by_target_user])
    
    # Step 4: Ensure other users' ratings are in the correct format (2D array)
    user_ids = list(user_ratings_matrix.keys())
    other_user_vectors = np.array([user_ratings_matrix[user] for user in user_ids])

    if len(other_user_vectors) == 0:
        return []  # No similar users found

    # Reshape target_user_vector to 2D for cosine_similarity
    target_user_vector = target_user_vector.reshape(1, -1)

    # Step 5: Calculate similarity between the target user and all other users
    similarities = cosine_similarity(target_user_vector, other_user_vectors)[0]

    # Step 6: Get the top 5 most similar users
    similar_user_indices = similarities.argsort()[-5:][::-1]
    similar_user_ids = [user_ids[i] for i in similar_user_indices]

    # Step 7: Get book recommendations based on similar users' ratings (ratings > 3)
    books_rated_by_similar_users = (Rating.objects.filter(user_id__in=similar_user_ids, rating__gt=3)  # Filter ratings > 3
                                    .exclude(book_id__in=books_rated_by_target_user)
                                    .values('book')
                                    .annotate(avg_rating=Avg('rating'))
                                    .order_by('-avg_rating'))

    # Get the actual book objects
    recommended_book_ids = [rec['book'] for rec in books_rated_by_similar_users]
    recommended_books = Book.objects.filter(id_book__in=recommended_book_ids)
    
    return recommended_books







from django.shortcuts import render
from .models import Book, Rating

from django.shortcuts import render
from .models import Book, Rating
from django.db.models import Avg

def get_trending_books_in_favorite_genre(user):
    # Obtenez toutes les évaluations de l'utilisateur
    user_ratings = Rating.objects.filter(user=user)

    # Calculez la moyenne des évaluations pour chaque genre
    genre_avg_rating = user_ratings.values('book__genre').annotate(avg_rating=Avg('rating')).order_by('-avg_rating')

    trending_books = []
    favorite_genre = None

    if genre_avg_rating.exists():
        # Obtenez le genre préféré basé sur la note moyenne la plus élevée
        favorite_genre = genre_avg_rating[0]['book__genre']

        # Découpez le genre préféré en sous-genres (en supposant qu'ils sont séparés par des virgules)
        sub_genres = [genre.strip() for genre in favorite_genre.split(',')]

        # Construisez une requête Q pour rechercher des livres contenant au moins un des sous-genres
        genre_query = Q()
        for sub_genre in sub_genres:
            genre_query |= Q(genre__icontains=sub_genre)

        # Obtenez les livres correspondant à l'un des sous-genres,
        # qui n'ont pas été évalués par l'utilisateur
        trending_books = Book.objects.filter(
            genre_query  # Correspondance avec l'un des sous-genres
        ).exclude(
            ratings__user=user  # Exclure les livres déjà évalués par l'utilisateur
        ).distinct().order_by('-id_book')  # Tri par date d'ajout (du plus récent au plus ancien)

    return trending_books, favorite_genre



from django.shortcuts import render
from .models import Book, Rating
from django.db.models import Avg

from django.db.models import Q


def get_trending_books_in_favorite_author(user):
    # Obtenez les évaluations de l'utilisateur
    user_ratings = Rating.objects.filter(user=user)

    # Calculez la moyenne des évaluations par auteur
    author_avg_rating = user_ratings.values('book__author').annotate(avg_rating=Avg('rating')).order_by('-avg_rating')

    trending_author_books = []
    favorite_author = None

    if author_avg_rating.exists():
        # Obtenez l'auteur avec la note moyenne la plus élevée
        favorite_author = author_avg_rating[0]['book__author'].strip().title()

        # Obtenez tous les livres de cet auteur non évalués par l'utilisateur
        trending_author_books = Book.objects.filter(
            author__icontains=favorite_author  # Livres de l'auteur préféré
        ).exclude(
            ratings__user=user  # Exclure les livres déjà évalués par cet utilisateur
        ).distinct().order_by('-id_book')  # Trier par le plus récent

    return trending_author_books, favorite_author



from collections import defaultdict
from django.db.models import Avg
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np



from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from django.utils import timezone
from datetime import timedelta

@login_required
def page_rec(request):
    user = request.user

    # Obtenez les livres les plus récents
    latest_books = Book.objects.all().order_by('-id_book')[:4]

    # Vérifiez si l'utilisateur a évalué des livres
    user_ratings = Rating.objects.filter(user=user)
    has_rated_books = user_ratings.exists()
    
    similar_books = []  # Liste pour stocker les livres similaires
    recommended_books = []  # Liste pour les livres recommandés
    rated_books = []  # Initialize rated_books as an empty list
    if has_rated_books:
        # Obtenez des livres recommandés basés sur les évaluations d'utilisateurs similaires
        recommended_books = get_similar_users_and_books(user.id)

        # Obtenez les livres que l'utilisateur a notés
        rated_books = Book.objects.filter(ratings__user=user).distinct()
        rated_book_ids = set(rated_books.values_list('id_book', flat=True))  # Liste des livres notés par l'utilisateur

        # Pour chaque livre noté par l'utilisateur, récupérez des livres similaires
        for rated_book in rated_books:
            similar_books_for_rated = get_similar_books(rated_book.id_book)

            # Convertir les résultats en objets Book et récupérer les informations manquantes
            similar_books += Book.objects.filter(id_book__in=similar_books_for_rated['id_book'].tolist())
    
    # Filtrer les livres similaires pour exclure les livres déjà notés par l'utilisateur et supprimer les doublons
    similar_books = list(set(similar_books))  # Remove duplicates
    similar_books = [book for book in similar_books if book.id_book not in rated_book_ids]

    # Obtenez les livres tendance dans le genre préféré de l'utilisateur
    trending_books, favorite_genre = get_trending_books_in_favorite_genre(user)

    # Obtenez les livres tendance de l'auteur préféré de l'utilisateur
    trending_author_books, favorite_author = get_trending_books_in_favorite_author(user)

    # Ajouter cover_img et dispo à chaque livre dans les différentes listes
    for book_list in [latest_books, recommended_books, trending_books, trending_author_books, similar_books]:
        for book in book_list:
            # Récupérer le statut de disponibilité du livre
            pret = Pret.objects.filter(book_id=book.id_book).first()
            book.dispo = "Available" if pret and pret.statut == "dispo" else "Not Available"
            
            # Ajouter l'image de couverture
            book.cover_img = book.cover_img

    # Fetch books the user is currently reading
    currently_reading_books = Emprunt.objects.filter(user=user, reading_statut="active")

    # Initialize notifications list
    notifications = []
    
    # Check if a book the user owns has been borrowed
    owned_books = Pret.objects.filter(user=user)  # Books the user owns
    borrowed_books = Emprunt.objects.filter(book_id__in=[book.book_id for book in owned_books])  # Books that are borrowed
    for borrowed_book in borrowed_books:
        book = Book.objects.get(id_book=borrowed_book.book_id)
        notification = {
            'message': f"Your posted book '{book.title}' has been borrowed by {borrowed_book.user.username} on {borrowed_book.start_date}.",
            'type': 'borrowed',
            'username': borrowed_book.user.username,
            'title': book.title,
            'start_date': borrowed_book.start_date,
        }
        notifications.append(notification)

    # Check if a followed publisher posts a new book
    followed_publishers = Following.objects.filter(user=user, role='publisher')

    for followed_publisher in followed_publishers:
        # Fetch the user's ID from the Pret table based on the followed publisher
        followed_user = User.objects.get(username=followed_publisher.followed_name)  # Get the User object using followed publisher's username
        followed_books = Pret.objects.filter(user=followed_user)[:2]  # Fetch last two books posted by this publisher

        # Now, check for new books posted by this publisher
        for followed_book in followed_books:
            book = Book.objects.get(id_book=followed_book.book_id)  # Get book details
            notification = {
                'message': f"The publisher '{followed_user.username}' has posted a new book: '{book.title}'.",
                'type': 'new_publisher_book',
                'username': followed_user.username,
                'title': book.title,
            }
            notifications.append(notification)

    # Check if a followed author posts a new book
    followed_authors = Following.objects.filter(user=user, role='author')
    for followed_author in followed_authors:
        new_books_by_author = Book.objects.filter(author=followed_author.followed_name)[:2]  # Get last two books by the followed author
        for new_book in new_books_by_author:
            notification = {
                'message': f"A new book by author '{followed_author.followed_name}' titled '{new_book.title}' has been posted.",
                'type': 'new_author_book',
                'username': followed_author.followed_name,
                'title': new_book.title,
            }
            notifications.append(notification)
    # Check if a book the user reserved is now available
    reserved_books = Emprunt.objects.filter(user=user, statut="reserved")  # Books reserved by the user
    available_books = Pret.objects.filter(book_id__in=[book.book_id for book in reserved_books], statut="dispo")  # Available books

    # Loop through available books and create notifications
    for available_book in available_books:
    # Ensure the notification is created inside the loop
        notification = {
        'message': f"Your reserved book '{available_book.book.title}' is now available!",
        'type': 'available',
        'title': available_book.book.title,
        'id':available_book.book.id_book
    }
        notifications.append(notification)  # Add to the notifications list


    # Notify if a book the user is reading has an end_date near (within 2 days)
    current_date = timezone.now().date()
    for borrowed_book in currently_reading_books:
        if borrowed_book.end_date and borrowed_book.end_date - current_date <= timedelta(days=2):
            notification = {
                'message': f"Reminder: You need to finish reading '{borrowed_book.book.title}' before {borrowed_book.end_date}. Time is running out!",
                'type': 'end_date',
                'title': borrowed_book.book.title,
                'end_date': borrowed_book.end_date,
            }
            notifications.append(notification)
    
    
    # Existing logic to get books, notifications, etc.
    recommended_groups = get_similar_users_chat_groups(user.id)  # Fetch recommended groups
    joined_groups = ChatGroup.objects.filter(users=user)  # Groups the user has already joined

    # Clean the recommended_groups list by filtering out the groups the user is already a member of
    recommended_groups = [
        group for group in recommended_groups if group not in [joined_group.name for joined_group in joined_groups]
    ]

    unread_messages_count=0
    # Get unread messages for the user
    unread_messages_count = ChatMessage.objects.filter(read=False).exclude(user=user).count() 


    # Gestion du certificat : L'utilisateur ayant le plus grand nombre d'emprunts dans le mois actuel
    current_year = timezone.now().year
    current_month = timezone.now().month

    monthly_emprunts = Emprunt.objects.filter(user=user, start_date__year=current_year, start_date__month=current_month)

    max_borrower = None
    max_borrow_count = 0
    users_with_borrow_count = Emprunt.objects.filter(start_date__year=current_year, start_date__month=current_month).values('user').annotate(borrow_count=Count('id_emprunt')).order_by('-borrow_count')

    if users_with_borrow_count:
        max_borrower_id = users_with_borrow_count[0]['user']
        max_borrow_count = users_with_borrow_count[0]['borrow_count']
        max_borrower = User.objects.get(id=max_borrower_id)

    # Certificat PDF : Vérifier si l'utilisateur a le plus d'emprunts dans le mois et lui attribuer un certificat
    certificate = None
    if max_borrower == user:
        certificate = 'Certificate.pdf'  # Le fichier PDF du certificat est dans le dossier static

    # Contexte pour le rendu du template
    context = {
        'name': user.first_name,
        'surname': user.last_name,
        'latest_books': latest_books,
        'recommended_books': recommended_books,  
        'trending_books': trending_books,
        'favorite_genre': favorite_genre,
        'trending_author_books': trending_author_books,
        'favorite_author': favorite_author,
        'rated_books': rated_books,  
        'notifications_count': len(notifications),  
        'similar_books': similar_books, 
        'currently_reading_books': currently_reading_books, 
        'notifications': notifications,  
        'recommended_groups': recommended_groups,  
        'joined_groups': joined_groups,  
        'unread_messages_count': unread_messages_count,
        'certificate': certificate,  



    }

    return render(request, 'page_rec.html', context)

import os
from io import BytesIO
from django.http import HttpResponse
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.conf import settings

def generate_certificate(request):
    user = request.user

    # Vérifier le chemin absolu du fichier Certificate.pdf dans le dossier static
    certificate_path = os.path.join(settings.BASE_DIR, 'books_app', 'static', 'Certificate.pdf')

    # Vérifier si le fichier Certificate.pdf existe dans le dossier static
    if not os.path.exists(certificate_path):
        return HttpResponse("Certificate template not found.", status=404)

    # Créer un buffer en mémoire pour ajouter les informations de l'utilisateur
    buffer = BytesIO()

    # Créer un canvas pour ajouter les informations de l'utilisateur sur le PDF
    c = canvas.Canvas(buffer, pagesize=letter)

    # Dimensions de la page
    width, height = letter

    # Position du texte "P R O U D L Y P R E S E N T E D T O"
    c.setFont("Helvetica-Bold", 24)
    text = "PROUDLY PRESENTED TO :"
    text_width = c.stringWidth(text, "Helvetica-Bold", 24)
    x_position = (width - text_width) / 2  # Centrer le texte horizontalement
    c.drawString(x_position, height - 350, text)

    # Position du nom de l'utilisateur
    user_name = f"{user.first_name} {user.last_name}"
    c.setFont("Times-Roman", 30)  # Police élégante pour le nom
    name_width = c.stringWidth(user_name, "Times-Roman", 30)
    x_position_name = (width - name_width) / 2  # Centrer le nom horizontalement
    c.drawString(x_position_name, height - 400, user_name)

    # Sauvegarder dans le buffer
    c.showPage()
    c.save()

    # Revenir au début du buffer
    buffer.seek(0)

    # Lire le fichier PDF existant
    existing_pdf = PdfReader(certificate_path)
    new_pdf = PdfReader(buffer)

    # Créer un écrivain pour combiner les pages
    writer = PdfWriter()

    # Copier la première page du certificat original
    original_page = existing_pdf.pages[0]

    # Fusionner la nouvelle page (avec les noms) dans le certificat existant
    original_page.merge_page(new_pdf.pages[0])

    # Ajouter la page fusionnée à l'écrivain
    writer.add_page(original_page)

    # Créer une réponse HttpResponse pour envoyer le PDF généré
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Certificate_{user.username}.pdf"'

    # Écrire le PDF final dans la réponse HTTP
    writer.write(response)

    return response



from collections import Counter

# Function to fetch chat groups based on similarities
def get_similar_users_chat_groups(user_id):
    # Get the ratings of the user
    user_ratings = Rating.objects.filter(user_id=user_id)
    
    # List to store recommended groups
    recommended_groups = []
    
    # Fetch all other users' ratings
    all_ratings = Rating.objects.exclude(user_id=user_id)
    
    # Create a list of users who have similar book ratings (use shared book ratings as a measure of similarity)
    for rating in all_ratings:
        similarity_score = 0
        similar_books = user_ratings.filter(book_id=rating.book_id)
        
        # Count the number of common ratings between the users
        if similar_books.exists():
            similarity_score += 1
        
        if similarity_score > 0:
            # If they have common ratings, consider them as similar
            similar_user = rating.user
            # Add groups based on shared interests or book genres
            group_interests = get_interests_for_user(similar_user)  # Define this function based on your requirements
            recommended_groups.extend(group_interests)
    
    # Remove duplicates from the recommended groups list
    recommended_groups = list(set(recommended_groups))
    
    return recommended_groups

from collections import Counter

from collections import Counter
import re

from collections import Counter
import re

from collections import Counter
import re
from collections import Counter

# Custom genre names based on your GENRE_CHOICES
GENRE_CUSTOM_NAMES = {
    'science_fiction': 'Galactic Voyagers',
    'fantasy': 'Magical Realms',
    'mystery': 'Whodunit Investigators',
    'thriller': 'Adrenaline Rush Seekers',
    'romance': 'Love and Passion Fans',
    'adventure': 'Epic Journey Seekers',
    'horror': 'Nightmare Enthusiasts',
    'biography': 'Life Story Explorers',
    'history': 'History Buffs',
    'science': 'Science Innovators',
    'travel': 'World Wanderers',
    'philosophy': 'Philosophical Thinkers',
    'psychology': 'Mind and Behavior Enthusiasts',
    'politics': 'Political Debate Lovers',
    'business_economics': 'Entrepreneurial Minds',
    'tragedy': 'Tragic Story Aficionados',
    'comedy': 'Comedy Lovers'
}

# Helper function to get user interests based on their ratings or reviews
def get_interests_for_user(user):
    # Get user ratings
    user_ratings = Rating.objects.filter(user=user)
    
    # Extract genres and authors from the user's ratings
    genre_interests = []
    author_interests = []
    
    for rating in user_ratings:
        # Split the genres stored as comma-separated values and add to the list
        genres = rating.book.genre.split(',')
        genre_interests.extend([genre.strip() for genre in genres])
        author_interests.append(rating.book.author)
    
    # Creative group names based on genre and author interests
    genre_groups = []
    for genre in Counter(genre_interests).keys():
        # Look up the custom genre names from GENRE_CUSTOM_NAMES
        if genre.lower() in GENRE_CUSTOM_NAMES:
            genre_groups.append(GENRE_CUSTOM_NAMES[genre.lower()])
        else:
            genre_groups.append(f"{genre.capitalize()} Enthusiasts")
    
    # Creative group names for authors
    author_groups = []
    for author in Counter(author_interests).keys():
        author_groups.append(f"Fans of {author}'s World")
    
    # Combine all the group names
    all_groups = genre_groups + author_groups
    
    return all_groups




from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404, FileResponse
import os
from .models import Book
from django.conf import settings

def display_pdf(request, book_id):
    # Get the book from the database
    book = get_object_or_404(Book, id_book=book_id)

    # Get the absolute file path of the PDF version
    pdf_path = book.pdf_version.path  # This gives the file path
    pdf_path = request.build_absolute_uri(book.pdf_version.url)

    # Print the path to debug
    return render(request,'pdf_view.html',{'pdf_path':pdf_path})

from django.shortcuts import render
from .models import Book

def categories(request):
    # Fetch all books and genres
    books = Book.objects.all()
    genres = Book.GENRE_CHOICES

    # Create a dictionary to hold genre and associated book covers, along with the count
    genre_books = {}
    for value, label in genres:
        # Use icontains to match books that contain the genre in a comma-separated list
        genre_books[label] = {
            'books': books.filter(genre__icontains=value).distinct()[:3],  # Retrieve up to 3 books
            'count': books.filter(genre__icontains=value).distinct().count()  # Count books for this genre
        }

    # Pass the genre_books dictionary to the template
    return render(request, 'categories.html', {'genre_books': genre_books})

def genre_books(request, genre):
    # Convert the genre string from the URL to a case-insensitive match
    books = Book.objects.filter(genre__icontains=genre)

    # Pass the books and genre to the template
    return render(request, 'genre_books.html', {'genre': genre, 'books': books})

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Book, Pret, Emprunt
from datetime import date
from django.contrib.auth.decorators import login_required

from datetime import date
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Book, Pret, Emprunt

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date
from .models import Book, Pret, Emprunt

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date
from .models import Book, Pret, Emprunt

from datetime import date, timedelta
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from .models import Book, Emprunt, Pret

@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id_book=book_id)
    user = request.user

    try:
        # Check if the user has reserved the book
        emprunt = Emprunt.objects.get(book=book, user=user, statut='reserved')
        pret = Pret.objects.get(book=book, statut='dispo')

        if pret and emprunt:
            # When the book is reserved and now borrowed
            emprunt.statut = 'borrowed'
            emprunt.reading_statut = 'active'
            emprunt.start_date = date.today()  # Set the borrowing start date

            # Ensure that the correct period from 'Pret' is used
            period = pret.period  # Use the period from 'Pret' model

            # Manually calculate the end_date based on the start_date and period
            emprunt.end_date =emprunt.start_date + timedelta(days=period)

            # Save the updated emprunt object
            emprunt.save()

            # Update the Pret (loan) status to 'borrowed'
            pret.statut = 'borrowed'
            pret.save()

            # Success message
            messages.success(request, f"The book '{book.title}' has been successfully borrowed!")
        else:
            messages.error(request, f"The book '{book.title}' is currently unavailable.")

    except Emprunt.DoesNotExist:
        # If no reservation exists, check if the book is available for borrowing
        pret = Pret.objects.filter(book=book, statut='dispo').first()

        if pret:
            # Create a new Emprunt and update Pret to 'borrowed'
            emprunt = Emprunt.objects.create(
                book=book,
                user=user,
                period=pret.period,  # Loan period from Pret model
                start_date=date.today(),
                statut='borrowed',
                reading_statut='active'
            )

            # Save the Emprunt object to trigger the overridden save() method
            emprunt.save()  # This will automatically calculate the end_date based on the overridden save method

            pret.statut = 'borrowed'
            pret.save()

            # Success message
            messages.success(request, f"The book '{book.title}' has been successfully borrowed!")
        else:
            messages.error(request, f"The book '{book.title}' is currently unavailable for borrowing.")

    # Redirect to the book detail page
    return redirect('books_app:book_detail', book_id=book.id_book)



@login_required
def reserve_book(request, book_id):
    book = get_object_or_404(Book, id_book=book_id)  # Use `id` instead of `id_book`
    user = request.user

    # Check if the book is currently borrowed
    pret = Pret.objects.filter(book=book, statut='borrowed').first()
    if pret:
        # Create a reservation record (Emprunt) with status 'reserved'
        Emprunt.objects.create(
            book=book,
            user=user,
            period=pret.period,  # Reservation period is 15 days
            start_date=date.today(),
            statut='reserved',  # Set status to 'reserved'
            reading_statut='waiting'  # Reservation is active
        )

        # Success message
        messages.success(request, f"The book '{book.title}' has been reserved successfully.")
    else:
        # If the book is not currently borrowed, no reservation can be made
        messages.error(request, f"Sorry, the book '{book.title}' cannot be reserved at the moment.")

    return redirect('books_app:book_detail', book_id=book_id)

from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def logout_view(request):
    logout(request)
    return redirect('books_app:login')  # Redirect to the login page after logout
from django.shortcuts import redirect
from django.contrib import messages
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail

@login_required
def change_book_status(request, book_id):
    user = request.user

    # Update the status of the book from borrowed to dispo
    pret = Pret.objects.get(book_id=book_id, statut='borrowed')
    emprunt=Emprunt.objects.get(book_id=book_id, statut='borrowed',reading_statut='active',user=user)
    if pret and emprunt:
        pret.statut = 'dispo'
        pret.save()
        emprunt.reading_statut = 'finished'
        emprunt.save()

        # Now, find the first reserved book where the start_date is the oldest
        reserved_books =Emprunt.objects.filter(book_id=book_id, statut='reserved').order_by('start_date')
        if reserved_books.exists():
            reserved_book = reserved_books.first()
            reserved_user = reserved_book.user  # User who reserved the book

            # Send notification to the user about availability
            notification_message = f"Your reserved book '{reserved_book.book.title}' is now available!"
            # Send email (or use other methods like notifications system)

            # Add a flash message for the user
            messages.success(request, notification_message)

    return redirect('books_app:page_rec')  # Redirect back to the page with the book list

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Following

@login_required
def follow_author(request, book_id):
    user = request.user
    book = get_object_or_404(Book, id_book=book_id)  # Use `id` instead of `id_book`

    # Check if the user is already following this author
    if not Following.objects.filter(user=user, followed_name=book.author, role='author').exists():
        Following.objects.create(user=user, followed_name=book.author, role='author')
        message = "You are now following this author!"
    else:
        message = "You are already following this author."

    # Optionally add a success message
    request.session['message'] = message
    return redirect('books_app:book_detail',book_id=book.id_book)  # Redirect to book detail page or any page you want

from django.shortcuts import redirect, get_object_or_404

@login_required
def follow_publisher(request, username, book_id):
    # Get the publisher by their username
    publisher = get_object_or_404(User, username=username)
    user = request.user  # Get the logged-in user

    # Check if the user is already following this publisher
    if not Following.objects.filter(user=user, followed_name=publisher.username, role='publisher').exists():
        Following.objects.create(user=user, followed_name=publisher.username, role='publisher')
        message = "You are now following this publisher!"
    else:
        message = "You are already following this publisher."

    # Optionally add a success message
    request.session['message'] = message

    # Redirect back to the book_detail page with the book_id
    return redirect('books_app:book_detail', book_id=book_id)



from django.contrib.auth.decorators import login_required

import logging

logger = logging.getLogger(__name__)
from .models import Book
from django.conf import settings
from django.conf import settings
from django.http import HttpResponse
from .models import Book
from django.templatetags.static import static



import os
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from .models import Book, User

import os
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from .models import Book, Emprunt  # Assuming you have an Emprunt model that tracks loans

def view_book(request, book_id):
    # Récupérer le livre par son ID
    book = get_object_or_404(Book, id_book=book_id)

    # Récupérer l'utilisateur connecté (vous pouvez ajuster cela en fonction de votre logique d'authentification)
    user = request.user

    # Récupérer l'emprunt correspondant au livre et à l'utilisateur
    emprunt = Emprunt.objects.filter(user=user, book=book, reading_statut='active').first()

    # Vérifier si l'utilisateur a un accès valide
    if emprunt:
        end_date = emprunt.end_date  # Date de fin de l'emprunt
        if end_date and end_date <= datetime.now().date():
            # Si le temps est expiré, on bloque l'accès au PDF
            file_exists = False
        else:
            # Si le temps n'est pas expiré, on permet l'accès au PDF
            file_exists = True
    else:
        file_exists = False

    pdf_path = f'books_pdf/{book.title}.pdf'  # Chemin relatif sous static/books_pdf/
    
    file_exists_on_disk = os.path.exists(os.path.join(settings.BASE_DIR, 'books_app', 'static', pdf_path))
    
    file_exists = file_exists and file_exists_on_disk

    return render(request, 'view_book.html', {
        'book': book,
        'file_exists': file_exists,
        'pdf_path': pdf_path,
    })



from django.shortcuts import render
from django.db.models import Count
from django.db.models.functions import TruncMonth
from .models import User, Pret, Emprunt, Book, Rating
from datetime import datetime

def statistics_view(request):
    user = request.user

    # Retrieve statistics for loans and borrowed books
    borrowed_books = Pret.objects.filter(user=user, statut='borrowed').count()
    available_books = Pret.objects.filter(user=user, statut='dispo').count()

    active_emprunts = Emprunt.objects.filter(user=user, reading_statut='active').count()
    finished_emprunts = Emprunt.objects.filter(user=user, reading_statut='finished').count()
    waiting_emprunts = Emprunt.objects.filter(user=user, reading_statut='waiting').count()

    # Calculate reading frequency (borrowings per month)
    reading_frequency = Emprunt.objects.filter(user=user)\
        .annotate(month=TruncMonth('start_date'))\
        .values('month')\
        .annotate(count=Count('book'))\
        .order_by('month')

    # Extract labels and values for the chart
    reading_frequency_labels = [item['month'].strftime('%Y-%m') for item in reading_frequency]
    reading_frequency_values = [item['count'] for item in reading_frequency]

    # Calculate preferred genres (Use the correct field name for genre)
    genre_counts = Book.objects.filter(pret__user=user).values('genre').annotate(count=Count('id_book')).order_by('-count')
    genre_labels = [item['genre'] for item in genre_counts]
    genre_values = [item['count'] for item in genre_counts]

    # Number of rated books
    books_rated = Rating.objects.filter(user=user).count()

    # Prepare additional statistics (borrowed books, waiting books)
    last_month = datetime.now().month - 1 if datetime.now().month > 1 else 12
    borrowed_last_month = Emprunt.objects.filter(user=user, start_date__month=last_month).count()

    # User engagement KPIs (total books borrowed, finished emprunts, books rated, etc.)
    total_books_engaged = borrowed_books + books_rated
    total_books_in_hand = borrowed_books + available_books

    # Books per rating distribution (1-5 stars) (Bar chart for user ratings)
    rating_counts = Rating.objects.filter(user=user).values('rating').annotate(count=Count('rating')).order_by('rating')
    rating_labels = [str(item['rating']) + " stars" for item in rating_counts]
    rating_values = [item['count'] for item in rating_counts]

    # Pie chart for reading time - short, medium, and long books
    short_reads = Book.objects.filter(num_pages__lt=100).count()
    medium_reads = Book.objects.filter(num_pages__gte=100, num_pages__lt=300).count()
    long_reads = Book.objects.filter(num_pages__gte=300).count()

    # Pie chart data
    reading_time_labels = ['Short (<100 pages)', 'Medium (100-300 pages)', 'Long (>300 pages)']
    reading_time_values = [short_reads, medium_reads, long_reads]

    # **Graphique en anneau** : Répartition des statuts d'emprunts
    emprunt_status_counts = Emprunt.objects.filter(user=user).values('reading_statut').annotate(count=Count('book')).order_by('reading_statut')
    donut_labels = [item['reading_statut'].capitalize() for item in emprunt_status_counts]
    donut_values = [item['count'] for item in emprunt_status_counts]

    # **Radar Chart** : Engagement par genre (top 5 genres)
    radar_genres = Book.objects.filter(pret__user=user).values('genre').annotate(count=Count('id_book')).order_by('-count')[:5]
    radar_labels = [item['genre'] for item in radar_genres]
    radar_values = [item['count'] for item in radar_genres]

    # **Scatter Plot** : Relation entre le nombre de pages et les ratings
    scatter_data = Book.objects.filter(ratings__user=user).values('num_pages', 'ratings__rating')
    scatter_pages = [item['num_pages'] for item in scatter_data]
    scatter_ratings = [item['ratings__rating'] for item in scatter_data]

    # Return data to template
    return render(request, 'statistics.html', {
        'user': user,
        'borrowed_books': borrowed_books,
        'available_books': available_books,
        'active_emprunts': active_emprunts,
        'finished_emprunts': finished_emprunts,
        'waiting_emprunts': waiting_emprunts,
        'reading_frequency_labels': reading_frequency_labels,
        'reading_frequency_values': reading_frequency_values,
        'genre_labels': genre_labels,
        'genre_values': genre_values,
        'books_rated': books_rated,
        'borrowed_last_month': borrowed_last_month,
        'total_books_engaged': total_books_engaged,
        'total_books_in_hand': total_books_in_hand,
        'rating_labels': rating_labels,
        'rating_values': rating_values,
        'reading_time_labels': reading_time_labels,
        'reading_time_values': reading_time_values,
        # Donut chart data
        'donut_labels': donut_labels,
        'donut_values': donut_values,
        # Radar chart data
        'radar_labels': radar_labels,
        'radar_values': radar_values,
        # Scatter plot data
        'scatter_pages': scatter_pages,
        'scatter_ratings': scatter_ratings,
    })


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import ChatGroup, ChatMessage, User
from books_app.models import Rating, Book
from django.db.models import Count


from django.shortcuts import render, get_object_or_404, redirect
from .models import ChatGroup, ChatMessage
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ChatGroup  # Import your ChatGroup model

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import ChatGroup

@login_required
def join_chat_group(request, group_name):
    # Check if the group exists in the database, or create it if it doesn't
    group, created = ChatGroup.objects.get_or_create(name=group_name)

    # Add the user to the group if they are not already in it
    if request.user not in group.users.all():
        group.users.add(request.user)
        messages.success(request, f"Successfully joined the {group_name} group!")
    else:
        messages.info(request, f"You are already a member of the {group_name} group.")
    
    # Fetch all groups the user has joined
    user_groups = ChatGroup.objects.filter(users=request.user)
    
    # Redirect to the page showing the groups (make sure the URL name is correct)
    return redirect('books_app:page_rec')  # You may need to change this URL name based on your configuration



from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Q
from .models import ChatGroup, ChatMessage

def chat_page(request, group_name=None):
    user = request.user

    # Retrieve the user's groups
    user_groups = ChatGroup.objects.filter(users=user)

    # Annotate each group with the count of unread messages (excluding the current user's messages)
    user_groups = user_groups.annotate(
        unread_count=Count('messages', filter=Q(messages__read=False) & ~Q(messages__user=user))
    )

    # Initialize variables for selected group and messages
    group = None
    messages = []

    # If a specific group is selected
    if group_name:
        # Retrieve the selected group and its messages
        group = get_object_or_404(ChatGroup, name=group_name)
        messages = group.messages.all()

        # Handle form submission if the user sends a message
        if request.method == 'POST':
            # Get the message content from the form
            message_content = request.POST.get('message')
            
            # Create and save the new message
            new_message = ChatMessage(
                group=group,
                user=user,
                message=message_content
            )
            new_message.save()

            # Redirect to the same page to see the new message
            return redirect('books_app:chat_page', group_name=group.name)

        # Mark the messages in the selected group as read, but only after the group is opened
        unread_messages = group.messages.filter(read=False).exclude(user=user)
        unread_messages.update(read=True)

    return render(request, 'chat_page.html', {
        'user_groups': user_groups,  # User groups with unread message count
        'selected_group': group,     # The currently selected group, if any
        'messages': messages,        # Messages in the selected group
    })



