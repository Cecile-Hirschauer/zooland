from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate, logout, login

def log_in(request):
    if (request.method == 'POST'):
        form = AuthenticationForm(None, request.POST)
        user = authenticate(
            username=request.POST['username'], 
            password=request.POST['password']
        )
        if user is not None:
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'userauth/login.html', { 'form': form })


def log_out(request):
    logout(request)
    return redirect('index')


def register(request):
    if (request.method == "POST"):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(
                username=request.POST['username'], 
                password=request.POST['password1']
            )
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()

    return render(request, 'userauth/register.html', { 'form': form })
