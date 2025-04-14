# IITM-MAD-1-Project
# 🏠 Household Services Application V-1

**Modern Application Development I - Course Project**  
_A role-based web platform to connect service professionals with customers for household services._

---

## 📖 Introduction

The **Household Services Application** offers an all-in-one solution for managing and delivering home services. It provides separate dashboards and functionality for:

- **Admins**: Who manage services and users  
- **Service Professionals**: Who accept service requests  
- **Customers**: Who book and review services  

The application ensures smooth communication and operation through a user-friendly interface and lightweight backend.

---

## 📝 Project Summary

This is a **multi-user Flask-based application** with the following roles:

### 🔑 Admin
- Access without registration
- Manage users (approve/block)
- Create, update, delete services

### 🧰 Service Professional
- Register/Login
- Accept/reject customer service requests
- Mark completion of services

### 👤 Customer
- Register/Login
- Search and book services
- Manage/close requests and give feedback

---

## 🧱 Tech Stack

| Layer       | Technology       |
|-------------|------------------|
| Backend     | Python (Flask)   |
| Frontend    | Jinja2 + Bootstrap |
| Database    | SQLite           |

> ⚠️ Application runs entirely on a local machine.

---

## ⚙️ Setup and Installation

### 🔧 Prerequisites

Ensure the following are installed:

- [Python 3.x](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads) (optional, for cloning)

---

### 📥 Installation Steps

#### 📁 Step 1: Clone the Repository
<pre><code>git clone https://github.com/your-username/household-services-app.git
cd household-services-app</code></pre>

#### 🧪 Step 2: Create and Activate Virtual Environment
<pre><code># Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
</code></pre>

#### 📦 Step 3: Install Dependencies
<pre><code>pip install -r requirements.txt</code></pre>

> If `requirements.txt` is not available:
<pre><code>pip install flask</code></pre>

#### 🚀 Step 4: Run the Application
<pre><code>python app.py</code></pre>

Then visit 👉 `http://localhost:5000` in your browser.
---

## 🔍 Features at a Glance

✅ Role-based Login for:
- Admin
- Service Professional
- Customer

✅ Admin Capabilities:
- Manage users and services
- Approve/block professionals

✅ Service Management:
- Create/update/delete service types
- Assign service professionals

✅ Customer Interactions:
- Search by service name/pin code
- Request and review services

✅ Service Request Workflow:
- Request → Assign → Accept/Reject → Complete → Review

---

## 📚 Example Database Schema

### `users`
- `id`, `username`, `password`, `role` (admin/professional/customer), etc.

### `services`
- `id`, `name`, `description`, `price`, `time_required`

### `service_requests`
- `id`, `service_id`, `customer_id`, `professional_id`
- `status` (requested, assigned, completed)
- `date_of_request`, `date_of_completion`, `remarks`

---

## 📜 License

This project is built for educational purposes and is not licensed for commercial use.

---

## 🙌 Credits

- [Flask](https://flask.palletsprojects.com/)
- [Bootstrap](https://getbootstrap.com/)
- [Jinja2](https://jinja.palletsprojects.com/)
- SQLite for easy-to-use local database
