
# 📚 Plexus: Your centralized network for managing knowledge resources.

## 🌐 Overview
**Plexus** is a modern and comprehensive Library Management System (LMS) built on the robust Django framework. It provides a seamless, centralized platform for students and administrators to manage book inventory, borrowing, returns, fines, and user accounts efficiently.

---

## ✨ Key Features

This system is designed to provide full functionality for a contemporary library:

### 👤 Student Features
* **Authentication:** Secure Login and Registration.
* **Book Catalogue:** Browse and search the entire book inventory.
* **Borrowing Requests:** Submit requests to borrow available books.



### 🛡️ Administrator Tools
* **Centralized Dashboard:** Monitor key metrics, pending requests, and system status.
* **Resource Management:** CRUD (Create, Read, Update, Delete) functionality for **Books** and **Authors**.
* **Issue Control:** Accept/Reject borrow requests and manage book returns.
* **User Management:** Manage student and user accounts.
* **Reporting:** Generate reports on inventory, issue history, and financial transactions.

---

## 🛠️ Technology Stack

| Category | Technology |
| :--- | :--- |
| **Backend Framework** | **Django (Python)** |
| **Database** | SQLite3 (Default) |
| **Frontend/Styling** | HTML, CSS, JavaScript, Bootstrap |

---

## 📂 Project Structure

The project follows a standard Django architecture, ensuring clear separation of concerns.

```

.
├── db.sqlite3
├── .git
├── .gitignore
├── library
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── **init**.py
│   ├── migrations
│   ├── models.py
│   ├── static
│   ├── templates
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── library\_project
│   ├── asgi.py
│   ├── **init**.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
└── venv/

````


## 🚀 Installation & Setup

Follow these steps to run the project locally on your machine:

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/exploremaruf/Plexus-Web.git](https://github.com/exploremaruf/Plexus-Web.git)
    cd Plexus-Web
    ```

2.  **Create & Activate Virtual Environment**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    *(For Windows: `.\venv\Scripts\activate`)*

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt 
    ```

4.  **Database Migration**
    ```bash
    python manage.py makemigrations library
    python manage.py migrate
    ```

5.  **Create Superuser (Admin Account)**
    ```bash
    python manage.py createsuperuser
    ```

6.  **Run the Server**
    ```bash
    python manage.py runserver
    ```

7.  **Access the Application**
    Open your web browser and navigate to: `http://127.0.0.1:8000/`

---

## 🤝 Contributing

We welcome contributions, issues, and feature requests. Feel free to fork the repository and submit a Pull Request.

---

## 📄 License

This project is licensed under the **MIT License**.

---

For any kind of information You can mail me: **maruf.chats@yandex.ru**
````
