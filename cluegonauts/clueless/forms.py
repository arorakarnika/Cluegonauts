from django import forms


class SuggestAccuseForm(forms.Form):
    # Set choices in view function
    character = forms.ChoiceField(required=True, label="Character", choices=[])
    location = forms.ChoiceField(required=True, label="Location", choices=[])
    weapon = forms.ChoiceField(required=True, label="Weapon", choices=[])
    actor = forms.CharField(widget=forms.HiddenInput(), required=True)

class DisproveSuggestionForm(forms.Form):
    # Set choices in view function
    card = forms.ChoiceField(required=True, label="Card", choices=[])
    actor = forms.CharField(widget=forms.HiddenInput(), required=True)