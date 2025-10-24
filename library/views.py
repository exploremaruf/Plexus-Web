from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import date, timedelta
from django.db.models import Sum

from .forms import (
    UserRegistrationForm,
    StudentProfileForm,
    BookForm,
    IssueBookForm,
    ReturnBookForm,
    RenewBookForm
)
from .models import Book, Student, Issue, BorrowRequest
from django.contrib.auth.models import User


def is_admin(user):
    return user.is_staff and user.is_superuser

def is_student(user):
    return Student.objects.filter(user=user).exists() and not user.is_staff


def register_request(request):
    if request.method == "POST":
        user_form = UserRegistrationForm(request.POST)
        student_form = StudentProfileForm(request.POST)
        
        if user_form.is_valid() and student_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            
            student = student_form.save(commit=False)
            student.user = user
            student.save()
            
            login(request, user)
            messages.success(request, "Registration successful! Welcome to the Library System.")
            return redirect("dashboard")

        for field, errors in user_form.errors.items():
            for error in errors:
                messages.error(request, f"User Error: {error}")
        for field, errors in student_form.errors.items():
            for error in errors:
                messages.error(request, f"Student Error: {error}")

        if 'non_field_errors' in user_form.errors:
            for error in user_form.errors['non_field_errors']:
                messages.error(request, f"Error: {error}")

    else:
        user_form = UserRegistrationForm()
        student_form = StudentProfileForm()
        
    return render(request, "library/register.html", {"user_form": user_form, "student_form": student_form})

def login_request(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.info(request, f"You are now logged in as {username}.")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password.")
            
    return render(request, "library/login.html")

@login_required
def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("login")


@login_required
def dashboard_view(request):
    context = {}
    
    if is_admin(request.user):
        context['is_admin'] = True
        context['total_books'] = Book.objects.aggregate(Sum('quantity'))['quantity__sum'] or 0
        context['total_students'] = Student.objects.count()
        context['issued_books_count'] = Issue.objects.filter(is_returned=False).count()
        context['pending_requests_count'] = BorrowRequest.objects.filter(status='Pending').count()
        context['overdue_books'] = Issue.objects.filter(is_returned=False, due_date__lt=date.today()).count()
        
    elif is_student(request.user):
        context['is_student'] = True
        try:
            student = Student.objects.get(user=request.user)
            context['student'] = student

            issued_books = Issue.objects.filter(student=student, is_returned=False).order_by('due_date')
            context['my_issued_books'] = issued_books
            context['total_issued'] = issued_books.count()

            today = date.today()
            due_soon = today + timedelta(days=3)
            
            context['books_due_soon'] = issued_books.filter(
                due_date__gte=today, 
                due_date__lte=due_soon
            ).count()

            context['overdue_books_count'] = issued_books.filter(
                due_date__lt=today
            ).count()
            
            
            context['pending_requests'] = BorrowRequest.objects.filter(student=student, status='Pending').count()
            context['approved_requests'] = BorrowRequest.objects.filter(student=student, status='Approved').count()
            
        except Student.DoesNotExist:
            context['student'] = None
    
    return render(request, "library/dashboard.html", context)


@login_required
def book_list(request):
    books = Book.objects.all().order_by('title')
    
    
    pending_books = []
    if is_student(request.user):
        try:
            student = Student.objects.get(user=request.user)
            
            pending_requests = BorrowRequest.objects.filter(student=student, status__in=['Pending', 'Approved']) 
            pending_books = [req.book.id for req in pending_requests]
        except Student.DoesNotExist:
            pass

    context = {
        'books': books,
        'pending_books': pending_books, 
    }
    return render(request, 'library/book_list.html', context)


@login_required
@user_passes_test(is_admin, login_url='/dashboard/')
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)

            book.save() 
            messages.success(request, f"Book '{book.title}' added successfully.")
            return redirect('add_book')
    else:
        form = BookForm()
    return render(request, 'library/book_form.html', {'form': form, 'form_title': 'Add New Book'})


@login_required
@user_passes_test(is_admin, login_url='/dashboard/')
def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, f"Book '{book.title}' updated successfully.")
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'library/book_form.html', {'form': form, 'form_title': f'Edit Book: {book.title}'})


@login_required
@user_passes_test(is_admin, login_url='/dashboard/')
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        
        if Issue.objects.filter(book=book, is_returned=False).exists():
            messages.error(request, f"Cannot delete book '{book.title}'. There are still copies issued out.")
            return redirect('book_list')
            
        book.delete()
        messages.success(request, f"Book '{book.title}' and all its records have been successfully deleted.")
        return redirect('book_list')
        
    context = {
        'book': book,
        'title': f'Confirm Deletion: {book.title}'
    }
    return render(request, 'library/book_confirm_delete.html', context)


@login_required
@user_passes_test(is_admin, login_url='/dashboard/')
def issue_book(request):
    if request.method == 'POST':
        form = IssueBookForm(request.POST)
        if form.is_valid():
            reg_no = form.cleaned_data['registration_no']
            isbn = form.cleaned_data['book_isbn']
            due_date = form.cleaned_data['due_date']
            
            try:
                student = Student.objects.get(registration_no=reg_no)
            except Student.DoesNotExist:
                messages.error(request, f"Student with Reg. No. {reg_no} not found.")
                return redirect('issue_book')
            
            try:
                book = Book.objects.get(isbn=isbn)
            except Book.DoesNotExist:
                messages.error(request, f"Book with ISBN {isbn} not found.")
                return redirect('issue_book')
            
            if book.available_copies <= 0:
                messages.error(request, f"Book '{book.title}' is currently out of stock.")
                return redirect('issue_book')

            
            Issue.objects.create(book=book, student=student, due_date=due_date)
            
            
            book.available_copies -= 1
            book.save()
            
            messages.success(request, f"Book '{book.title}' issued to {student.name} successfully.")
            return redirect('issue_book')
    else:
        form = IssueBookForm()
    return render(request, 'library/issue_book_form.html', {'form': form})



@login_required
@user_passes_test(is_admin, login_url='/dashboard/')
def return_book(request):
    if request.method == 'POST':
        form = ReturnBookForm(request.POST)
        if form.is_valid():

            issue = form.cleaned_data['issue_record']


            fine = issue.get_fine

            issue.is_returned = True
            issue.return_date = date.today() 
            issue.save()

            book = issue.book
            book.available_copies += 1
            book.save()

            borrow_req = BorrowRequest.objects.filter(
                student=issue.student,
                book=book,
                status__in=['Approved', 'Pending'] 
            ).order_by('-request_date').first()

            if borrow_req:
                borrow_req.status = 'Completed'
                borrow_req.save()

            fine_message = f" (Fine: {fine} Taka)." if fine > 0 else "."
            messages.success(request, f"Book '{book.title}' returned successfully by {issue.student.name}{fine_message}")
            
            return redirect('return_book')
            
    else:

        form = ReturnBookForm()
        
    context = {
        'form': form,
        'form_title': 'Confirm Book Return (Select from Issued)',
        'submit_button_text': 'Confirm Return'
    }
    return render(request, 'library/return_book_form.html', context)


@login_required
@user_passes_test(is_admin, login_url='/dashboard/')
def manage_students_view(request):
    students = Student.objects.select_related('user').all().order_by('name')
    
    context = {
        'students': students,
        'title': 'Manage Student Accounts'
    }

    return render(request, 'library/manage_students.html', context)


@login_required
@user_passes_test(is_admin, login_url='/dashboard/')
def admin_borrow_requests(request):
    requests = BorrowRequest.objects.filter(status__in=['Pending', 'Approved']).order_by('request_date')
    
    context = {
        'requests': requests,
    }
    return render(request, 'library/admin_request_manager.html', context)


@login_required
@user_passes_test(is_admin, login_url='/dashboard/')
def approve_borrow_request(request, request_id):
    
    req = get_object_or_404(BorrowRequest, id=request_id)
    
    if req.status != 'Pending':
        messages.warning(request, "This request is not pending and cannot be approved.")
        return redirect('admin_requests')

    book = req.book
    
    if book.available_copies <= 0:
        messages.error(request, f"Cannot approve. Book '{book.title}' is out of stock.")
        req.status = 'Rejected'
        req.save()
        return redirect('admin_requests')

    
    due_date = date.today() + timedelta(days=7)
    
    Issue.objects.create(
        book=book,
        student=req.student,
        due_date=due_date
    )
    
    
    book.available_copies -= 1
    book.save()
    
    
    req.status = 'Approved'
    req.save()
    
    messages.success(request, f"Book '{book.title}' issued and request approved for {req.student.name}. Due: {due_date}")
    return redirect('admin_requests')


@login_required
@user_passes_test(is_admin, login_url='/dashboard/')
def reject_borrow_request(request, request_id):
    
    req = get_object_or_404(BorrowRequest, id=request_id)
    
    if req.status != 'Pending':
        messages.warning(request, "Only pending requests can be rejected.")
        return redirect('admin_requests')
        
    req.status = 'Rejected'
    req.save()
    messages.info(request, f"Borrow request for {req.book.title} from {req.student.name} rejected.")
    return redirect('admin_requests')


@login_required
@user_passes_test(is_student, login_url='/login/')
def borrow_request(request, book_id):
    
    book = get_object_or_404(Book, id=book_id)
    
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found. Contact the admin.")
        return redirect('book_list')

    
    if Issue.objects.filter(student=student, book=book, is_returned=False).exists():
        messages.warning(request, f"You already have '{book.title}' issued to you.")
        return redirect('book_list')
        
    
    existing_request = BorrowRequest.objects.filter(
        student=student, 
        book=book, 
        status__in=['Pending', 'Approved']
    ).exists()

    if existing_request:
        messages.warning(request, f"You already have a pending or approved request for '{book.title}'.")
        return redirect('book_list')
        
    
    if book.available_copies <= 0:
        messages.error(request, f"Sorry, '{book.title}' is currently out of stock.")
        return redirect('book_list')

    
    BorrowRequest.objects.create(student=student, book=book, status='Pending')
    
    messages.success(request, f"Request for '{book.title}' submitted successfully. The librarian will review shortly.")
    return redirect('book_list')


@login_required
@user_passes_test(is_admin, login_url='/dashboard/')
def report_generation_view(request):
    
    current_issues = Issue.objects.filter(is_returned=False).select_related('book', 'student').order_by('due_date')

    returned_transactions = Issue.objects.filter(is_returned=True).select_related('book', 'student').order_by('-issue_date')

    overdue_books = current_issues.filter(due_date__lt=date.today())
    
    
    total_books_issued = current_issues.count()
    total_overdue = overdue_books.count()
    
    total_potential_fine = sum(issue.get_fine for issue in overdue_books)


    context = {
        'title': 'Generate Library Reports',
        
        'current_issues': current_issues,
        'returned_transactions': returned_transactions,
        'overdue_books': overdue_books,
        
        'total_books_issued': total_books_issued,
        'total_overdue': total_overdue,
        'total_potential_fine': total_potential_fine,
    }

    return render(request, 'library/report_generation.html', context)


@login_required
@user_passes_test(is_student, login_url='/login/')
def student_return_request(request, issue_id):
    
    issue = get_object_or_404(Issue, id=issue_id)
    
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('dashboard')
        
    if issue.student != student:
        messages.error(request, "This is not your issued book.")
        return redirect('dashboard')
        
    if issue.is_returned:
        messages.warning(request, "This book has already been returned.")
        return redirect('dashboard')
        
    
    messages.info(request, f"You have confirmed the return of '{issue.book.title}'. Please submit the book to the library counter for final check-in by the librarian.")
    
    return redirect('dashboard')


def home_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  
    return render(request, 'library/homepage.html')


@login_required
@user_passes_test(is_admin, login_url='/dashboard/')
def renew_book(request):
    
    if request.method == 'POST':
        form = RenewBookForm(request.POST)
        if form.is_valid():
            issue = form.cleaned_data['issue_record']
            renewal_days = form.cleaned_data['renewal_days']
            
            if issue.is_returned:
                messages.warning(request, f"Book '{issue.book.title}' is already returned.")
                return redirect('renew_book')
                
            fine_due = issue.get_fine
            if fine_due > 0:
                messages.error(request, f"Cannot renew! Book is overdue with a fine of {fine_due} Tk. Fine must be cleared first.")
                return redirect('renew_book')
            
            base_date = max(issue.due_date, date.today())
            new_due_date = base_date + timedelta(days=renewal_days)
            
            issue.due_date = new_due_date
            issue.save()
            
            messages.success(request, f"Book '{issue.book.title}' successfully renewed for {issue.student.name} by {renewal_days} days. New Due Date: {new_due_date}.")
            return redirect('renew_book')
    else:
        form = RenewBookForm()
        
    context = {
        'form': form,
        'form_title': 'Renew Issued Book (Custom Days)',
        'submit_button_text': 'Renew Book'
    }
    return render(request, 'library/issue_book_form.html', context)
