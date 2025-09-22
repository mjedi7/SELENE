from django import forms
from .models import MovimientoPlaza, ArchivoSubido

class MovimientoPlazaForm(forms.ModelForm):
    class Meta:
        model = MovimientoPlaza
        fields = '__all__'
        
class ArchivoForm(forms.ModelForm):
    class Meta:
        model = ArchivoSubido
        fields = ['nombre', 'archivo']