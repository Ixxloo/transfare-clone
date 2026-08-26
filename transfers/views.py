from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Transfer, TransferFile
import uuid

def home(request):
    return render(request, "transfers/home.html")

def download(request, token):
    return render(request, "transfers/download.html", {"token": token})

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

def upload_view(request):
    if request.method == 'POST':
        # Handle file upload logic...
        # Example: generating a unique token for the transfer
        token = str(uuid.uuid4())
        
        # Check if the user is authenticated to assign the owner
        owner = request.user if request.user.is_authenticated else None
        
        # Create the Transfer object with the owner set
        transfer = Transfer.objects.create(
            token=token,
            owner=owner,
            # include any other fields your Transfer model requires (e.g., expiration, notes)
        )
        
        # Process and save associated files (TransferFile)
        files = request.FILES.getlist('files') # Adjust based on your form field name
        for f in files:
            TransferFile.objects.create(
                transfer=transfer,
                file=f
            )
            
        messages.success(request, "Files uploaded successfully!")
        
        # Redirect to download/success page or user dashboard if authenticated
        if request.user.is_authenticated:
            return redirect('transfers:dashboard')
        return redirect('transfers:home')

    return render(request, 'transfers/upload.html')