from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_request, name='register'),
    path('login/', views.login_request, name='login'),
    path('logout/', views.logout_request, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    path('books/', views.book_list, name='book_list'),
    path('books/add/', views.add_book, name='add_book'),
    path('issue/', views.issue_book, name='issue_book'),
    path('return/', views.return_book, name='return_book'),
    
    path('students/', views.manage_students_view, name='manage_students'),
    
    path('requests/', views.admin_borrow_requests, name='admin_requests'),
    path('requests/approve/<int:request_id>/', views.approve_borrow_request, name='approve_request'),
    path('requests/reject/<int:request_id>/', views.reject_borrow_request, name='reject_request'),
    
    path('borrow/<int:book_id>/', views.borrow_request, name='borrow_request'),
    path('return/confirm/<int:issue_id>/', views.student_return_request, name='student_return_request'),
    
    path('reports/', views.report_generation_view, name='report_generation'),
    
    
    path('renew/', views.renew_book, name='renew_book'), 
    
    path('book/edit/<int:book_id>/', views.edit_book, name='edit_book'),
    path('book/delete/<int:book_id>/', views.delete_book, name='delete_book'),
]
