from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import CustomLoginForm, CustomUserSignupForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect("redirect_after_login")

    form = CustomLoginForm(request, data=request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome, {user.username}")
                return redirect("redirect_after_login")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "accounts/login.html", {
        "form": form
    })


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("redirect_after_login")

    if request.method == "POST":
        form = CustomUserSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f"Account created successfully for {user.username}. Please login."
            )
            return redirect("login")
    else:
        form = CustomUserSignupForm()

    return render(request, "accounts/signup.html", {
        "form": form
    })


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def redirect_after_login(request):
    return redirect("dashboard")