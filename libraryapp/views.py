from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from .forms import UserRegistrationForm, LoginForm, ContactForm
from .models import Users, Books, PhysicalBooks, Booksauthors, Booksgenres, Authors, Genres, Contact, FAQ
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        else:
            return render(request, 'register.html', {'form': form})
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

        # Handle the image
        image = request.FILES.get('image')
        if image:
            fs = FileSystemStorage()
            image_path = fs.save(image.name, image)
        else:
            image_path = None

        # Create the book object with the image path
        book = Books.objects.create(
            title=title,
            publisher=publisher,
            published_year=published_year,
            image=image_path
        )

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

        # Create physical copies
        for i in range(number_of_copies):
            PhysicalBooks.objects.create(book=book, state=1)

        return redirect('home')

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


def contact(request):
    contact_info, created = Contact.objects.get_or_create(pk=1, defaults={
        'phone': '+48 123-456-789',  # Wartości domyślne
        'email': 'contact@example.com',
        'address': '123 Main Street',
        'working_hours': '9 AM - 5 PM',
    })

    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact_info)
        if form.is_valid():
            form.save()
            return redirect('contact')
    else:
        form = ContactForm(instance=contact_info)

    return render(request, 'contact.html', {'form': form, 'contact_info': contact_info})


def faq(request):
    faqs = FAQ.objects.all()  # Pobranie wszystkich pytań i odpowiedzi
    return render(request, 'faq.html', {'faqs': faqs})


def users(request):
    if request.method == "POST":
        # Pobierz słownik ról z formularza
        roles = request.POST.getlist("roles")
        for user_id, role in zip(request.POST.getlist("roles[]"), roles):
            try:
                # Znajdź użytkownika i zaktualizuj jego rolę
                user = Users.objects.get(user_id=user_id)
                user.role = role
                user.save()
            except Users.DoesNotExist:
                continue
        return redirect("users")  # Przekieruj na tę samą stronę po zapisaniu zmian

    # Dla żądania GET pobierz listę użytkowników
    users_list = Users.objects.all()

    # Pobierz aktualnie zalogowanego użytkownika z sesji
    custom_user = None
    user_id = request.session.get('user_id')
    if user_id:
        try:
            custom_user = Users.objects.get(user_id=user_id)
        except Users.DoesNotExist:
            pass  # Jeśli użytkownik nie istnieje, `custom_user` pozostanie jako None

    # Przekaż listę użytkowników i aktualnie zalogowanego użytkownika do szablonu
    return render(request, "users.html", {"users": users_list, "custom_user": custom_user})

def index(request):
    # Example query: get all books with genres
    books = Books.objects.all()
    books_with_genres = []

    for book in books:
        genres = Booksgenres.objects.filter(book=book).select_related('genre')
        genre_names = ", ".join([g.genre.genre_name for g in genres])
        books_with_genres.append({
            'id': book.book_id,
            'title': book.title,
            'published_year': book.published_year,
            'genre_names': genre_names,
            'image': book.image.url if book.image else None,
        })

    return render(request, 'index.html', {'books': books_with_genres})


def book_detail(request, book_id):
    try:
        # Get the book and its related details
        book = Books.objects.get(pk=book_id)
        genres = Booksgenres.objects.filter(book=book).select_related('genre')
        genre_names = ", ".join([g.genre.genre_name for g in genres])
        authors = Booksauthors.objects.filter(book=book).select_related('author')
        author_names = ", ".join([a.author.author_name for a in authors])
        copies = PhysicalBooks.objects.filter(book_id=1).count()
        # Pass the book's details to the template
        print(f"Image URL: {book.image.url}")
        context = {
            'book': book,
            'genre_names': genre_names,
            'author_names': author_names,
            'image': book.image.url if book.image else None,
            'copies': copies
        }
        return render(request, 'book_detail.html', context)
    except Books.DoesNotExist:
        return HttpResponse("Book not found.", status=404)

def update_profile(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        if not user_id:
            return HttpResponse("You are not logged in.", status=401)

        try:
            user = Users.objects.get(pk=user_id)
            user.first_name = request.POST.get("first_name", user.first_name)
            user.last_name = request.POST.get("last_name", user.last_name)
            user.email = request.POST.get("email", user.email)
            user.phone_number = request.POST.get("phone_number", user.phone_number)
            user.save()
            return redirect('/profile/')  # Przekierowanie na stronę profilu
        except Users.DoesNotExist:
            return HttpResponse("User not found.", status=404)
    else:
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('/login')

        user = Users.objects.get(pk=user_id)
        return render(request, 'profile.html', {'user': user})