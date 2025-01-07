from .forms import UserRegistrationForm, LoginForm
from .models import Users, Books, PhysicalBooks, Booksauthors, Booksgenres, Authors, Genres
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from .models import Users  # Assuming you have a custom `Users` model
from django.contrib.auth import login


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()  # Save the user to the MySQL database
            return redirect('login')  # Redirect to login page
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    error_message = None
    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                user = Users.objects.get(username=username)
                if check_password(password, user.password_hash):
                    # Create a session
                    request.session['user_id'] = user.user_id
                    request.session['username'] = user.username
                    return redirect('home')  # Redirect to home page
                else:
                    error_message = "Invalid password!"
            except Users.DoesNotExist:
                error_message = "User does not exist!"

    return render(request, 'login.html', {'form': form, 'error_message': error_message})

def logout_view(request):
    # Clear the session data
    request.session.flush()
    return redirect('home')


def add_book(request):
    if request.method == 'POST':
        # Create the book
        title = request.POST['title']
        publisher = request.POST['publisher']
        published_year = request.POST['published_year']
        number_of_copies = int(request.POST['number_of_copies'])

        book = Books.objects.create(title=title, publisher=publisher, published_year=published_year)


        # Handle authors
        author_names = request.POST['authors'].split(',')
        for name in author_names:
            author, created = Authors.objects.get_or_create(author_name=name.strip())
            Booksauthors.objects.create(book=book, author=author)

        # Handle genres
        genre_names = request.POST['genres'].split(',')
        for name in genre_names:
            genre, created = Genres.objects.get_or_create(genre_name=name.strip())
            Booksgenres.objects.create(book=book, genre=genre)

        for i in range(number_of_copies):
            PhysicalBooks.objects.create(book=book, state=1)

        return redirect('display_books')  # Adjust this to the name of your display_books URL

    return render(request, 'add_book.html')


def display_books(request):
    # Fetch all books
    books = Books.objects.all()

    # Add authors and genres using the intermediary tables
    books_with_details = []
    for book in books:
        authors = Authors.objects.filter(
            author_id__in=Booksauthors.objects.filter(book=book).values_list('author_id', flat=True)
        )
        genres = Genres.objects.filter(
            genre_id__in=Booksgenres.objects.filter(book=book).values_list('genre_id', flat=True)
        )
        books_with_details.append({
            'book': book,
            'authors': authors,
            'genres': genres
        })

    return render(request, 'display_books.html', {'books_with_details': books_with_details})

def index(request):
    # Example query: get all books with genres
    books = Books.objects.all()
    books_with_genres = []

    for book in books:
        genres = Booksgenres.objects.filter(book=book).select_related('genre')
        genre_names = ", ".join([g.genre.genre_name for g in genres])
        books_with_genres.append({
            'title': book.title,
            'published_year': book.published_year,
            'genre_names': genre_names
        })

    return render(request, 'index.html', {'books': books_with_genres})