from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Job, Application, ContactSupport

class SignupForm(UserCreationForm):
    full_name = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Enter your full name',
        'class': 'form-input',
    }))
    
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'placeholder': 'Enter your email',
        'class': 'form-input',
    }))
    
    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Choose a username',
        'class': 'form-input',
    }))
    
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-input',
        })
    )
    
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Create a password',
        'class': 'form-input',
    }))
    
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm your password',
        'class': 'form-input',
    }))
    
    class Meta:
        model = User
        fields = ('full_name', 'email', 'username', 'role', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.full_name = self.cleaned_data['full_name']
        user.email = self.cleaned_data['email']
        user.role = self.cleaned_data['role']
        
        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={
        'placeholder': 'Enter your email',
        'class': 'form-input',
    }))
    
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter your password',
        'class': 'form-input',
    }))
    
    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError("This account is inactive.")
        super().confirm_login_allowed(user)

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ('title', 'location', 'description')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }

class ApplicationForm(forms.ModelForm):
    applicant_name = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Your full name',
        'class': 'form-input',
    }))
    
    applicant_email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'Your email address',
        'class': 'form-input',
    }))
    
    cv_path = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-input',
            'accept': '.pdf,.doc,.docx',
        }),
        help_text='Upload your CV/Resume (PDF, DOC, DOCX formats only)'
    )
    
    class Meta:
        model = Application
        fields = ('applicant_name', 'applicant_email', 'cv_path')
        
    def clean_cv_path(self):
        cv_file = self.cleaned_data.get('cv_path')
        if cv_file:
            # Get file extension
            ext = cv_file.name.split('.')[-1].lower()
            if ext not in ['pdf', 'doc', 'docx']:
                raise forms.ValidationError("Only PDF, DOC, and DOCX files are allowed.")
            # Check file size (limit to 5MB)
            if cv_file.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError("File size should not exceed 5MB.")
        return cv_file

class ContactSupportForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Your full name',
        'class': 'form-input',
    }))
    
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'Your email address',
        'class': 'form-input',
    }))
    
    subject = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Message subject',
        'class': 'form-input',
    }))
    
    message = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder': 'Type your message here...',
        'class': 'form-input',
        'rows': 5,
    }))
    
    class Meta:
        model = ContactSupport
        fields = ('name', 'email', 'subject', 'message')
    
    def clean_message(self):
        message = self.cleaned_data.get('message')
        if len(message) < 10:
            raise forms.ValidationError("Your message is too short. Please provide more details.")
        return message 