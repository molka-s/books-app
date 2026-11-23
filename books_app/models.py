from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date
from datetime import timedelta

class User(AbstractUser):
    groups = models.ManyToManyField(
        'auth.Group',
        related_name="custom_user_groups",  # Utilisez un related_name unique ici
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name="custom_user_permissions",  # Utilisez un related_name unique ici
        blank=True
    )
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)



from django.core.validators import FileExtensionValidator

class Book(models.Model):
    GENRE_CHOICES = [
        ('science_fiction', 'Science Fiction'),
        ('fantasy', 'Fantasy'),
        ('mystery', 'Mystery'),
        ('thriller', 'Thriller'),
        ('romance', 'Romance'),
        ('adventure', 'Adventure'),
        ('horror', 'Horror'),
        ('biography', 'Biography'),
        ('history', 'History'),
        ('science', 'Science'),
        ('travel', 'Travel'),
        ('philosophy', 'Philosophy'),
        ('psychology', 'Psychology'),
        ('politics', 'Politics'),
        ('business_economics', 'Business and Economics'),
        ('tragedy', 'Tragedy'),
        ('comedy', 'Comedy'),
    ]

    LANGUAGE_CHOICES = [
        ('arabic', 'Arabic'),
        ('french', 'French'),
        ('english', 'English'),
    ]

    id_book = models.AutoField(primary_key=True)
    isbn = models.CharField(max_length=13, unique=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    description = models.TextField()
    cover_img = models.URLField(max_length=200, blank=True, null=True)
    pub_year = models.PositiveIntegerField()
    genre = models.CharField(max_length=100, choices=GENRE_CHOICES)
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES)
    pdf_version = models.FileField(
        upload_to='books_pdf/',  # Le fichier sera enregistré sous /static/books_pdf/
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        blank=True, null=True)

    num_pages = models.PositiveIntegerField(default=0)  # New field for number of pages

    def __str__(self):
        return self.title





class Pret(models.Model):
    id_pret = models.AutoField(primary_key=True)
    period = models.PositiveIntegerField(default=0)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE , default=0)
    
    # Définition explicite des statuts possibles
    STATUT_CHOICES = [
        ('dispo', 'Disponible'),
        ('borrowed', 'Emprunté'),
    ]
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='dispo')
    
    def __str__(self):
        return f"{self.book.title} - {self.statut}"



class Emprunt(models.Model):
    id_emprunt = models.AutoField(primary_key=True)
    period = models.PositiveIntegerField()
    start_date = models.DateField(default=date.today) 
    end_date = models.DateField(null=True, blank=True) 
    reading_statut = models.CharField(max_length=100, choices=[
        ('active', 'Actif'),
        ('finished', 'Terminé'),
        ('waiting','en attente')
    ])
    STATUT_CHOICES = [
        ('borrowed', 'Emprunté'),
        ('reserved', 'Réservé')
    ]
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='dispo')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE , default=0)

    def save(self, *args, **kwargs):
        if self.start_date and self.period:
            self.end_date = self.start_date + timedelta(days=self.period)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.book.title} - {self.statut}"




# books_app/models.py
from django.contrib.auth import get_user_model
from django.db import models
from .models import Book

User = get_user_model()  # Cela récupère le modèle User personnalisé
from django.utils import timezone
class Rating(models.Model):
    id_rating = models.AutoField(primary_key=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')  # Utilisez ici User personnalisé
    rating = models.IntegerField()  # Note (1-5)
    comment = models.TextField(default='No comment yet')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Rating for {self.book.title} by {self.user.username}"


class Following(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followings')
    followed_name = models.CharField(max_length=200)
    role = models.CharField(max_length=50, choices=[('author', 'Author'), ('publisher', 'Publisher')])
    
    def __str__(self):
        return f'{self.user.username} follows {self.followed_name} as {self.role}'

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatGroup(models.Model):
    name = models.CharField(max_length=255)  # Group name, like "Science Fiction Fans"
    created_at = models.DateTimeField(auto_now_add=True)
    users = models.ManyToManyField(User, related_name='chat_groups')  # Users in the group

    def __str__(self):
        return f"{self.name}"

class ChatMessage(models.Model):
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)  # Field to track if the message is read

    def __str__(self):
        return f"Message by {self.user.username} in {self.group.name} at {self.timestamp}"

