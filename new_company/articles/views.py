from django.shortcuts import render, redirect
from django.http import Http404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from .models import Shipment

def archive(request):
    return render(request, 'archive.html', {"posts": Shipment.objects.all()})

def get_article(request, article_id):
    try:
        post = Shipment.objects.get(id=article_id)
        return render(request, 'article.html', {"post": post})
    except Shipment.DoesNotExist:
        raise Http404

def create_post(request):
    # Проверяем, авторизован ли пользователь (is_anonymous - свойство, без скобок)
    if not request.user.is_anonymous:
        if request.method == "POST":
            # Обрабатываем данные формы, если метод POST
            form = {
                'text': request.POST.get("text", ""),
                'title': request.POST.get("title", "")
            }
            
            # Проверяем, что оба поля заполнены
            if form["text"] and form["title"]:
                # Проверка на уникальность названия маршрута
                if Shipment.objects.filter(title=form["title"]).exists():
                    form['errors'] = "Перевозка с таким названием маршрута уже существует!"
                    return render(request, 'create_post.html', {'form': form})
                
                # Если название уникально — создаем запись
                article = Shipment.objects.create(
                    text=form["text"],
                    title=form["title"],
                    author=request.user
                )
                return redirect('get_article', article_id=article.id)
            else:
                # Если поля пустые — возвращаем форму с ошибкой
                form['errors'] = "Не все поля заполнены"
                return render(request, 'create_post.html', {'form': form})
        else:
            # Если метод GET — просто показываем пустую форму
            return render(request, 'create_post.html', {})
    else:
        # Если пользователь не авторизован — ошибка 404 (как в методичке)
        raise Http404

def register(request):
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        email = request.POST.get("email", "")
        
        # Проверка на пустые поля
        if not username or not password:
            return render(request, 'register.html', {'error': "Заполните все поля"})
        
        # Проверка на уникальность логина
        try:
            User.objects.get(username=username)
            # Если пользователь найден, get не вызовет исключение, и мы попадем сюда
            return render(request, 'register.html', {'error': "Пользователь с таким именем уже существует"})
        except User.DoesNotExist:
            # Если пользователя нет — регистрируем
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            # Сразу авторизуем после регистрации
            login(request, user)
            return redirect('archive')
    else:
        return render(request, 'register.html', {})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        
        # Проверка на пустые поля
        if not username or not password:
            return render(request, 'login.html', {'error': "Заполните все поля"})
        
        # Аутентификация
        user = authenticate(username=username, password=password)
        
        if user is not None:
            # Если пользователь найден — логиним
            login(request, user)
            return redirect('archive')
        else:
            return render(request, 'login.html', {'error': "Неверный логин или пароль"})
    else:
        return render(request, 'login.html', {})

    

def logout_view(request):
    logout(request)
    return redirect('archive')