from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout


def home(request):

    if request.user.is_authenticated:
        return redirect('/dashboard/')

    return redirect('/login/')


def user_login(request):

    if request.user.is_authenticated:
        return redirect('/dashboard/')

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect('/dashboard/')

    return render(request, 'users/login.html')


def user_logout(request):

    logout(request)

    return redirect('login')
