from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import User, Vendor
from django.core.exceptions import ValidationError


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'surname', 'other_names', 'email', 'phone_number', 'profile_picture',
                  'default_shipping_address', 'id_document_number', 'id_image', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'surname': forms.TextInput(attrs={'class': 'form-control'}),
            'other_names': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'default_shipping_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'id_document_number': forms.TextInput(attrs={'class': 'form-control'}),
            'id_image': forms.FileInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        phone_number = cleaned_data.get('phone_number')

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            self.add_error('username', 'A user with this username already exists.')

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            self.add_error('email', 'A user with this email address already exists.')

        # Check if phone number already exists
        if User.objects.filter(phone_number=phone_number).exists():
            self.add_error('phone_number', 'A user with this phone number already exists.')

        return cleaned_data


class VendorDetailsForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['phone_number2', 'company_name', 'location', 'description',]
        widgets = {

            'phone_number2': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        phone_number2 = cleaned_data.get('phone_number2')

        # Check if phone number already exists
        if User.objects.filter(phone_number=phone_number2).exists():
            self.add_error('phone_number2', 'A user with this phone number already exists.')

        # Check if phone number already exists
        if Vendor.objects.filter(phone_number2=phone_number2).exists():
            self.add_error('phone_number2', 'A user with this phone number already exists.')

        return cleaned_data


class CustomLoginForm(forms.Form):
    identifier = forms.CharField(label="Username, Email, or Phone", max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'surname', 'email', 'phone_number', 'profile_picture', 'default_shipping_address']  # Include all relevant fields for profile update

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'surname': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'default_shipping_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }


User = get_user_model()


class VendorProfileForm(forms.ModelForm):
    # Fields from the User model
    first_name = forms.CharField(max_length=50, required=True)
    surname = forms.CharField(max_length=50, required=True)
    other_names = forms.CharField(max_length=100, required=False)
    phone_number = forms.CharField(max_length=15, required=True)
    profile_picture = forms.ImageField(required=False)
    email = forms.EmailField(required=True)
    default_shipping_address = forms.CharField(max_length=400, required=False)

    # Fields from the Vendor model
    phone_number2 = forms.CharField(max_length=15, required=False)
    company_name = forms.CharField(max_length=100, required=True)
    location = forms.CharField(max_length=255, required=True)
    description = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Vendor
        fields = ['phone_number2', 'company_name', 'location', 'description']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Pass user as an argument to initialize the form
        super(VendorProfileForm, self).__init__(*args, **kwargs)

        # Add 'form-control' class to all fields
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': 'form-control', 'rows': '4'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

        # Prepopulate the form fields with user information
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['surname'].initial = user.surname
            self.fields['other_names'].initial = user.other_names
            self.fields['phone_number'].initial = user.phone_number
            self.fields['profile_picture'].initial = user.profile_picture
            self.fields['email'].initial = user.email
            self.fields['default_shipping_address'].initial = user.default_shipping_address

    def save(self, commit=True):
        vendor = super(VendorProfileForm, self).save(commit=False)
        user = vendor.user

        # Update user details
        user.first_name = self.cleaned_data.get('first_name')
        user.surname = self.cleaned_data.get('surname')
        user.other_names = self.cleaned_data.get('other_names')
        user.phone_number = self.cleaned_data.get('phone_number')
        user.profile_picture = self.cleaned_data.get('profile_picture')
        user.email = self.cleaned_data.get('email')
        user.default_shipping_address = self.cleaned_data.get('default_shipping_address')

        if commit:
            user.save()  # Save the user details
            vendor.save()  # Save the vendor details

        return vendor