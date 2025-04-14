# 🏡 Household Services Application

A multi-user platform for comprehensive home servicing and solutions, developed as part of the **Modern Application Development I** course project.

---

## 📌 Project Overview

This web application serves as a centralized platform that connects **service professionals** with **customers** for various household services such as plumbing, AC repair, electrical maintenance, and more. The system includes role-based access for **Admin**, **Service Professionals**, and **Customers**, enabling efficient management of services and service requests.

---

## 👥 Roles

### 🔑 Admin (Superuser)
- No registration required.
- Access to Admin Dashboard.
- Approve service professionals after document verification.
- Monitor and manage all users (customers and professionals).
- Create, update, delete services with base prices.
- Block users for fraudulent activity or poor reviews.

### 👨‍🔧 Service Professional
- Register/Login.
- Accept or reject service requests.
- One professional handles one specific service type.
- Profile includes ID, name, experience, description, service type, etc.
- Visible to customers based on reviews.
- Mark service as completed after job is done.

### 👤 Customer
- Register/Login.
- Search for services by name or location/pin code.
- Create and manage service requests.
- Close service requests and post reviews.

---

## 🧱 Technologies Used

| Component       | Technology        |
|----------------|-------------------|
| Backend         | Flask             |
| Templating      | Jinja2            |
| Frontend Styling| Bootstrap         |
| Database        | SQLite            |

> ⚠️ All functionalities run on a local machine environment.

---

## 🛠️ Core Functionalities

### 1. 🔐 User Authentication
- Separate login/register forms for Admin, Customers, and Service Professionals.
- Simple HTML forms for user credentials.
- Role-based redirection after login.

### 2. 🖥️ Admin Dashboard
- Monitor all users and service requests.
- Approve or block users.
- Add/update/delete services.

### 3. 🧾 Service Management
- Create new services with attributes like name, price, time_required, and description.
- Edit or delete services as needed.

### 4. 📬 Service Requests
- Customers can raise service requests.
- Include fields like:
  - `service_id`, `customer_id`, `professional_id`
  - `date_of_request`, `date_of_completion`
  - `service_status` (requested, assigned, closed)
  - `remarks`

### 5. 🔍 Search Functionality
- Customers: Search services by name or pin code.
- Admin: Search users (for monitoring/blocking).

### 6. ✅ Professional Actions
- View all service requests.
- Accept/reject service jobs.
- Mark request as completed after service delivery.

---

## 🧩 Database Overview

### Tables (Suggested Schema)
- `users`: Stores user info (Admin/Customer/Professional)
- `services`: List of service types with base pricing
- `service_requests`: Tracks customer service requests
- `reviews`: Stores customer feedback

---

## 💡 Project Notes
- Wireframes provided are for reference only. You are free to customize the UI/UX.
- Extend database models and views as per your implementation needs.
- Focus is on functionality, not production-level security.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.x
- Flask
- SQLite
- Bootstrap (CDN or local)

### Running the App Locally
```bash
# Install dependencies
pip install flask

# Run the app
python app.py
