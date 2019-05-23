from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Question, Choice


class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username', 'email', 'about')


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'about')


# class QuestionForm(forms.ModelForm):
#     class Meta:
#         model = Question
#         fields = ('question_text', 'owner')


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ('choice_text',)


CreatePollFormSet = inlineformset_factory(
    Question, Choice, form=ChoiceForm, extra=1)
