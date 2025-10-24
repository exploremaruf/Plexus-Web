from django.db import models
from django.contrib.auth.models import User
from datetime import date


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    registration_no = models.CharField(max_length=30, unique=True)
    roll = models.CharField(max_length=10)
    department = models.CharField(max_length=50)
    season = models.CharField(max_length=50)
    semester = models.CharField(max_length=20)
    shift = models.CharField(max_length=20)
    
    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    author_name = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, unique=True)
    book_type = models.CharField(max_length=50)
    quantity = models.IntegerField(default=1)
    available_copies = models.IntegerField(default=1)

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.available_copies = self.quantity
        else:
            old_book = Book.objects.get(pk=self.pk)
            quantity_difference = self.quantity - old_book.quantity
            self.available_copies += quantity_difference
            if self.available_copies < 0:
                self.available_copies = 0
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.title


class Issue(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    is_returned = models.BooleanField(default=False)
    return_date = models.DateField(null=True, blank=True)

    FINE_PER_DAY = 10 
    
    @property
    def get_fine(self):
        if self.is_returned:
            if self.return_date and self.return_date > self.due_date:
                days_overdue = (self.return_date - self.due_date).days
                return days_overdue * self.FINE_PER_DAY
            return 0
        
        if self.due_date < date.today():
            days_overdue = (date.today() - self.due_date).days
            return days_overdue * self.FINE_PER_DAY
        return 0

    @property
    def days_until_due(self):
        if self.is_returned:
            return 0
        
        days = (self.due_date - date.today()).days
        return days
        
    def __str__(self):
        return f"{self.book.title} issued to {self.student.name}"


class BorrowRequest(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    request_date = models.DateField(auto_now_add=True)
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Completed', 'Completed'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"Request for {self.book.title} by {self.student.name} ({self.status})"
