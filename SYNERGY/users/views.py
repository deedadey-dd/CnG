from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import UserRegistrationForm, CustomLoginForm, VendorDetailsForm, VendorProfileForm, \
    UserProfileForm
from django.contrib.auth import authenticate, login, logout, get_backends
from django.contrib import messages
from .models import User


def user_register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            # Set the user role as 'regular'
            user.role = 'regular'
            form.save()
            return redirect('custom_login')
    else:
        form = UserRegistrationForm()  # Only RegularUser form
    return render(request, 'users/register.html', {'form': form})


def vendor_register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the user, but don't commit yet
            user = form.save(commit=False)
            # Set the user role as 'vendor'
            user.role = 'vendor'
            user.save()

            # Set a message directing the user to log in to fill in extra details
            messages.success(request, 'Registration successful. Log in to continue and fill in extra details.')

            return redirect('custom_login')  # Redirect to the login page
    else:
        form = UserRegistrationForm()  # Only Vendor form

    return render(request, 'users/register.html', {'form': form})


@login_required
def vendor_detail(request):
    if request.method == 'POST':
        form = VendorDetailsForm(request.POST, request.FILES)
        if form.is_valid():
            # Link the vendor details to the currently logged-in user
            vendor = form.save(commit=False)
            vendor.user = request.user
            vendor.save()

            # Set a message confirming the details were saved
            messages.success(request, 'Vendor details saved successfully!')

            return redirect('custom_login')  # Redirect to login or another page
    else:
        form = VendorDetailsForm()  # Only Vendor form

    return render(request, 'users/vendor_detail.html', {'form': form})


def custom_login(request):
    form = CustomLoginForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            identifier = form.cleaned_data.get('identifier')
            password = form.cleaned_data.get('password')

            # Authenticate the user using email, phone number, or username
            user = authenticate(request, username=identifier, password=password)

            if user is not None:
                # Log the user in
                login(request, user)
                messages.success(request, 'Login successful!')

                # Redirect based on user type
                if user.role == 'vendor':
                    if not hasattr(user, 'vendor_profile') or user.vendor_profile.location == '':
                        return redirect('vendor_detail')
                    return redirect('index')  # Redirect vendors to the vendor dashboard
                else:
                    return redirect('index')  # Redirect regular users to the homepage
            else:
                messages.error(request, 'Invalid login credentials. Please try again.')

    return render(request, 'users/login.html', {'form': form})


def profile_view(request):
    user = request.user

    if user.role == 'vendor':
        vendor = user.vendor_profile

        if request.method == 'POST':
            form = VendorProfileForm(request.POST, request.FILES, user=user, instance=vendor)
        else:
            form = VendorProfileForm(user=user, instance=vendor)  # Prepopulate vendor data
    else:
        if request.method == 'POST':
            form = UserProfileForm(request.POST, request.FILES, instance=user)
        else:
            form = UserProfileForm(instance=user)  # Prepopulate user data

    if form.is_valid():
        form.save()
        messages.success(request, 'Your profile has been updated successfully!')
        return redirect('profile')

    return render(request, 'users/profile.html', {'form': form})


@login_required
def logout_me_out(request):
    logout(request)
    messages.success(request, 'You have successfully logged out')
    return redirect('index')


# @login_required
# def profile_view(request):
#     user = request.user
#
#     if request.method == 'POST':
#         form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Your profile has been updated.")
#             return redirect('profile')  # Redirect back to profile after successful update
#         else:
#             messages.error(request, "Please correct the error(s) below.")
#     else:
#         form = ProfileUpdateForm(instance=user)
#
#     return render(request, 'users/profile.html', {'form': form})
