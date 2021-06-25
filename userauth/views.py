from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordResetForm
from django.contrib.auth import authenticate, logout, login
from django.db.models.query_utils import Q
from django.contrib.auth.models import User
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.contrib import messages

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


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            users = User.objects.filter(Q(email=data))
            if users.exists():
                print('email')
                for user in users:
                    subject = "Password Reset Requested"
                    c = {
                    'email': user.email,
                    'domain':'127.0.0.1:8000',
                    'site_name': 'Zooland',
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    'user': user,
                    'token': default_token_generator.make_token(user),
                    'protocol': 'http',
                    }
                    email = render_to_string('password_reset_email.txt', c)
                    try:
                        send_mail(subject, email, 'admin@zooland.com' , [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    messages.success(request, 'A message with reset password instructions has been sent to your inbox.')    
                    return redirect('login')
            messages.error(request, 'An invalid email has been entered.')
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="userauth/password_reset.html", context={"password_reset_form":password_reset_form})


# def lost_password(request):
#     if (request.method == "POST"):
#         form = SetPasswordForm(user=request.user)
#         print(request.user)
#         if form.is_valid():
#             print('VALID')
#             # form.save()
#             # user = authenticate(
#             #     password1=request.POST['password1'], 
#             #     password2=request.POST['password2']
#             # )
#             # login(request, user)
#             return redirect('index')
#     else:
#         form = SetPasswordForm(user=request.user)

#     return render(request, 'userauth/lost_password.html', { 'form': form })


# def password_reset(request):
#     if (request.method == "POST"):
#         form = SetPasswordForm(user=request.user)
#         print(request.user)
#         if form.is_valid():
#             print('VALID')
#             # form.save()
#             # user = authenticate(
#             #     password1=request.POST['password1'], 
#             #     password2=request.POST['password2']
#             # )
#             # login(request, user)
#             return redirect('index')
#     else:
#         form = SetPasswordForm(user=request.user)

#     return render(request, 'userauth/password_reset.html', { 'form': form })

# # def password_change(request, username):
# #     if request.method == 'POST':
# #         form = PasswordChangeForm(data=request.POST, user=request.user)
# #         if form.is_valid():
# #             update_session_auth_hash(request, form.username)
# #             form.save()
# #             return HttpResponseRedirect('/blog/password_change_done/') 
# #         else:
# #             return render(request, 'blog/profile.html', {'form': form })
# #     else:
# #         return redirect(reverse('blog:profile', args=[username]))