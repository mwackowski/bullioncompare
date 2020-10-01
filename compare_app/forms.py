from django import forms

class InputForm(forms.Form):
    # SHOPS = ['GoldSilver.be', 'Europeanmint.com']
    BIRTH_YEAR_CHOICES = ['1980', '1981', '1982']
    FAVORITE_COLORS_CHOICES = [
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('black', 'Black'),
    ]
    shop = forms.ChoiceField(choices=[('blabla', 'BLaaaa'), ('inny', 'other')])
    birth_year = forms.DateField(widget=forms.SelectDateWidget(years=BIRTH_YEAR_CHOICES))
    favorite_colors = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=FAVORITE_COLORS_CHOICES,
    )

    name = forms.CharField()

