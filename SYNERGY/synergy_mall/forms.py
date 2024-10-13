from django import forms
from .models import Product, Category, Wishlist, WishlistItem, CustomItem, ProductImage


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image']

        widgets = {
            # 'image': forms.FileInput(attrs={'multiple': True, 'class': 'form-control'}),
            'image': MultipleFileField(label='Select files', required=False),
        }


class ProductForm(forms.ModelForm):
    images = MultipleFileField()  # Add this to allow multiple file uploads

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'sale_price', 'category', 'sku', 'condition', 'color']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'sale_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'condition': forms.Select(choices=[('new', 'New'), ('used', 'Used'), ('refurbished', 'Refurbished')], attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
        }


# These funcctions allow for multiple files to be uploaded.


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']


class InventoryProductForm(forms.ModelForm):
    images = MultipleFileField()
    # tags = forms.CharField(required=False, widget=forms.TextInput(
    # attrs={'placeholder': 'Add tags separated by commas', 'class': 'form-control'})
    # )

    class Meta:
        model = Product
        exclude = ['tags']  # Exclude tags field from being rendered automatically
        # Exclude 'featured' and 'available' from the form
        fields = ['name', 'stock', 'description', 'price', 'sale_price', 'category', 'sku', 'condition',
                  'color', 'tags',
                  ]

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'sale_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'condition': forms.Select(choices=[('new', 'New'), ('used', 'Used'), ('refurbished', 'Refurbished')], attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            # 'tags': forms.Textarea(attrs={'class': 'form-control'}),

        }


class FeaturedAndAvailableForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['available', 'featured']

        widgets = {
            'available': forms.CheckboxInput(attrs={'class': 'form-control'}),
            'featured': forms.CheckboxInput(attrs={'class': 'form-control'}),
        }


class WishlistForm(forms.ModelForm):
    class Meta:
        model = Wishlist
        fields = ['title', 'description', 'privacy', 'expiry_date']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'privacy': forms.Select(attrs={'class': 'form-control'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),

        }


class UpdateExpiryDateForm(forms.ModelForm):
    class Meta:
        model = Wishlist
        fields = ['expiry_date']
        widgets = {
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class WishlistItemForm(forms.ModelForm):
    class Meta:
        model = WishlistItem
        fields = ['product', 'quantity']


class CustomItemForm(forms.ModelForm):
    class Meta:
        model = CustomItem
        fields = ['name', 'description', 'price']
