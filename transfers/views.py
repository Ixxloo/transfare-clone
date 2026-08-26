from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Transfer
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import check_password
from django.http import Http404
from .storage import presigned_get


def download(request, token):
    transfer = get_object_or_404(Transfer, token=token)

    if not transfer.is_available:
        return render(request, "transfers/download.html", {
            "transfer": transfer,
            "unavailable": True,
        })

    # password gate
    if transfer.password_hash:
        session_key = f"unlocked_{transfer.token}"
        if not request.session.get(session_key):
            if request.method == "POST":
                if check_password(request.POST.get("password", ""), transfer.password_hash):
                    request.session[session_key] = True
                else:
                    return render(request, "transfers/download.html", {
                        "transfer": transfer,
                        "needs_password": True,
                        "wrong_password": True,
                    })
            else:
                return render(request, "transfers/download.html", {
                    "transfer": transfer,
                    "needs_password": True,
                })

    return render(request, "transfers/download.html", {"transfer": transfer})


def download_file(request, token, file_id):
    transfer = get_object_or_404(Transfer, token=token)

    if not transfer.is_available:
        raise Http404

    if transfer.password_hash and not request.session.get(f"unlocked_{transfer.token}"):
        return redirect("transfers:download", token=token)

    f = get_object_or_404(transfer.files, id=file_id)

    transfer.download_count += 1
    transfer.save(update_fields=["download_count"])

    return redirect(presigned_get(f.key, download_name=f.original_name))
def home(request):
    return render(request, "transfers/home.html")


def register(request):
    if request.user.is_authenticated:
        return redirect("transfers:dashboard")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Account created successfully! Welcome, {user.username}.")
            return redirect("transfers:dashboard")
    else:
        form = UserCreationForm()
        
    return render(request, "transfers/register.html", {"form": form})

@login_required
def dashboard(request):
    # Fetch only the transfers belonging to the currently logged-in user
    user_transfers = Transfer.objects.filter(owner=request.user)
    return render(request, "transfers/dashboard.html", {"transfers": user_transfers})

