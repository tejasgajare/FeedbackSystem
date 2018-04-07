from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm
from .models import Subject, Department, Profile, Student, Faculty, TeacherSubject, Classroom


class AddSubjectForm(forms.ModelForm):
	class Meta:
		model = Subject
		exclude=()

class AddDepartmentForm(forms.ModelForm):
	class Meta:
		model = Department
		exclude=()

class AddClassroomForm(forms.ModelForm):
	class Meta:
		model = Classroom
		exclude=()


class SignUpForm(UserCreationForm):
	student_name = forms.CharField(
		label='student_name',
		max_length=50,
		help_text='Enter your full name'
	)
	email = forms.EmailField(
		label='email',
		max_length=254,
		help_text='Enter your email id'
	)
	phone_number = forms.CharField(
		label='phone_number',
		max_length=254,
		help_text='Enter your phone_number'
	)

	class Meta:
		model = User
		fields = ('username', 'student_name' , 'password1' , 'password2', 'email','phone_number')
		widgets = {
			'username': forms.TextInput(),
			'student_name':forms.TextInput(),
			'password1':forms.TextInput(),
			'password2':forms.TextInput(),
			'email':forms.TextInput(),
			'phone_number':forms.TextInput(),
		}

class LogInForm(forms.Form):

	username = forms.CharField(
		label='Username',
		max_length=50,
		help_text='Enter username',
		widget=forms.TextInput(
			attrs= {
				'class': 'validate'
			}
		)
	)

	password = forms.CharField(
		label='Password',
		max_length=50,
		help_text='Enter Password',
		widget=forms.TextInput(
			attrs={
				'class': 'validate',
				'type': 'password'
			}
		)
	)
	class Meta:
		fields = ['username','password']
		widgets = {
			'username':forms.TextInput(),
			'password':forms.PasswordInput(),
		}

class CreateNewForm(forms.Form):
	title = forms.CharField(
		label='Form Name',
		max_length=50,
		help_text='Enter form name',
		widget=forms.TextInput(
			attrs={
				'id':'form_name'
			}
		)
	)