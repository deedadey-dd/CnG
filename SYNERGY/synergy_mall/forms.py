from django import forms
from .models import Product, Category, Wishlist, WishlistItem, CustomItem, ProductImage, ProductVariant


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
    images = MultipleFileField()  # To allow multiple file uploads
    # colors = forms.CharField(required=False, help_text="Enter multiple colors separated by commas.")
    # sizes = forms.CharField(required=False, help_text="Enter multiple sizes separated by commas.")

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'sale_price', 'category', 'condition']  # Removed sku

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'sale_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'condition': forms.Select(choices=[('new', 'New'), ('used', 'Used'), ('refurbished', 'Refurbished')],
                                      attrs={'class': 'form-control'}),
        }

    def clean_colors(self):
        """ Ensure the input for colors is valid """
        colors = self.cleaned_data.get('colors')
        if colors:
            return [color.strip() for color in colors.split(',')]
        return []

    def clean_sizes(self):
        """ Ensure the input for sizes is valid """
        sizes = self.cleaned_data.get('sizes')
        if sizes:
            return [size.strip() for size in sizes.split(',')]
        return []


class ProductVariantForm(forms.ModelForm):
    colors = forms.ChoiceField(required=False, label="Color", widget=forms.Select(attrs={'class': 'form-control'}))
    sizes = forms.ChoiceField(required=False, label="Size", widget=forms.Select(attrs={'class': 'form-control'}))
    sku = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))  # SKU will be generated and readonly

    class Meta:
        model = ProductVariant
        fields = ['color', 'size', 'sku', 'stock', 'price', 'sale_price']

    def __init__(self, *args, **kwargs):
        product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)

        # Prepopulate choices for colors and sizes from existing variants
        if product:
            self.fields['colors'].choices = [(v.color, v.color) for v in product.variants.all() if v.color]
            self.fields['sizes'].choices = [(v.size, v.size) for v in product.variants.all() if v.size]

    def clean_sku(self):
        """Generate the SKU automatically based on the product, color, and size"""
        color = self.cleaned_data.get('color')
        size = self.cleaned_data.get('size')
        product = self.instance.product

        if color and size:
            # Generate SKU as a combination of product name, color, and size (e.g., PROD-RED-M)
            sku = f"{product.name[:3].upper()}-{color[:3].upper()}-{size[:2].upper()}"
            return sku

        return self.cleaned_data['sku']


class BulkProductUploadForm(forms.Form):
    file = forms.FileField(label='Upload Excel file')

# These funcctions allow for multiple files to be uploaded.


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }


class BulkCategoryUploadForm(forms.Form):
    file = forms.FileField(label='Upload Excel or CSV file', required=True)


# class InventoryProductForm(forms.ModelForm):
#     images = MultipleFileField(required=False)  # Optional: Allow multiple file uploads
#
#     class Meta:
#         model = Product
#         exclude = ['tags', 'sku', 'color']  # Exclude fields that don't exist or are not applicable
#
#         fields = ['name', 'description', 'price', 'sale_price', 'category', 'condition']
#
#         widgets = {
#             'name': forms.TextInput(attrs={'class': 'form-control'}),
#             'description': forms.Textarea(attrs={'class': 'form-control'}),
#             'price': forms.NumberInput(attrs={'class': 'form-control'}),
#             'sale_price': forms.NumberInput(attrs={'class': 'form-control'}),
#             'category': forms.Select(attrs={'class': 'form-control'}),
#             'condition': forms.Select(choices=[('new', 'New'), ('used', 'Used'), ('refurbished', 'Refurbished')],
#                                       attrs={'class': 'form-control'}),
#         }

class InventoryProductForm(forms.ModelForm):
    # Define fields for colors and sizes
    colors = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter colors separated by commas'})
    )
    sizes = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter sizes separated by commas'})
    )
    sku = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter SKU for the product variant'})
    )
    stock = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter stock for the variant'})
    )

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'sale_price', 'category', 'condition', 'tags']  # Include other fields as needed
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'sale_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'condition': forms.Select(attrs={'class': 'form-control'}),
        }


class FeaturedAndAvailableForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['available', 'featured']

        widgets = {
            'available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
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
