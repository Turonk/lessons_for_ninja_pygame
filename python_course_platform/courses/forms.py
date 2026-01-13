from django import forms
from django.contrib.auth import get_user_model
from .models import Class, Topic, Task, TestCase

User = get_user_model()


class ClassForm(forms.ModelForm):
    """Форма для создания/редактирования класса"""
    class Meta:
        model = Class
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название класса'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Описание класса'}),
        }


class StudentForm(forms.ModelForm):
    """Форма для создания/редактирования ученика"""
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Минимум 8 символов'
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Логин'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Пароли не совпадают')
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.role = User.Role.STUDENT
        if commit:
            user.save()
        return user


class TopicForm(forms.ModelForm):
    """Форма для создания/редактирования темы"""
    class Meta:
        model = Topic
        fields = ['title', 'description', 'order', 'theory_content', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'theory_content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class TaskForm(forms.ModelForm):
    """Форма для создания/редактирования задания"""
    class Meta:
        model = Task
        fields = ['title', 'description', 'hint', 'example_code', 'order', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'hint': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'example_code': forms.Textarea(attrs={'class': 'form-control', 'rows': 8}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class TestCaseForm(forms.ModelForm):
    """Форма для создания/редактирования тестового случая"""
    class Meta:
        model = TestCase
        fields = ['test_type', 'variable_name', 'expected_value', 'description', 'order']
        widgets = {
            'test_type': forms.Select(attrs={'class': 'form-control'}),
            'variable_name': forms.TextInput(attrs={'class': 'form-control'}),
            'expected_value': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class TopicAccessForm(forms.Form):
    """Форма для управления доступом к теме"""
    topic = forms.ModelChoiceField(
        queryset=Topic.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Тема'
    )
    is_accessible = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Открыть доступ'
    )
