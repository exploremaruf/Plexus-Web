from django import forms
from .models import Book, Student, Issue
from django.contrib.auth.models import User
from datetime import date


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Password and Confirm Password do not match.")

        return cleaned_data


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'registration_no', 'roll', 'department', 'season', 'semester', 'shift']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'registration_no': forms.TextInput(attrs={'class': 'form-control'}),
            'roll': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'season': forms.TextInput(attrs={'class': 'form-control'}),
            'semester': forms.TextInput(attrs={'class': 'form-control'}),
            'shift': forms.TextInput(attrs={'class': 'form-control'}),
        }


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author_name', 'isbn', 'book_type', 'quantity']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'author_name': forms.TextInput(attrs={'class': 'form-control'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'book_type': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class IssueBookForm(forms.Form):
    registration_no = forms.CharField(
        max_length=30,  
        label='Student Reg. No.',  
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    book_isbn = forms.CharField(
        max_length=13,  
        label='Book ISBN',  
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )


class ReturnBookForm(forms.Form):
    issue_record = forms.ModelChoiceField(
        queryset=Issue.objects.filter(is_returned=False).select_related('student', 'book').order_by('issue_date'),
        label='Select Book/Student to Return',
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="--- Select an Issued Book to Confirm Return ---"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['issue_record'].label_from_instance = self.get_issue_label

    def get_issue_label(self, issue):
        due_date_str = issue.due_date.strftime('%Y-%m-%d')
        return f"{issue.book.title} | {issue.student.name} (Reg: {issue.student.registration_no}) | Due: {due_date_str}" 


class RenewBookForm(forms.Form):
    
    issue_record = forms.ModelChoiceField(
        queryset=Issue.objects.filter(is_returned=False, due_date__gte=date.today()).select_related('book', 'student'),
        label="Select Issued Book to Renew",
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="--- Select a Non-Overdue Issued Book ---"
    )
    
    renewal_days = forms.IntegerField(
        label="Renewal Period (Days)",
        min_value=1,
        max_value=30,
        initial=7,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter days (e.g., 5, 10)'}),
        help_text="Enter the number of days to extend the due date."
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['issue_record'].label_from_instance = self.get_issue_label

    def get_issue_label(self, issue):
        due_date_str = issue.due_date.strftime('%Y-%m-%d')
        return f"{issue.book.title} | {issue.student.name} | Current Due: {due_date_str}"
