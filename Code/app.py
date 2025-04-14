from flask import Flask, render_template, request, redirect, url_for, session,flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
from sqlalchemy import func, and_
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///admin_dashboard.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # Set a secure key for session management

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' # Redirect to admin login if not authenticated

# In-memory storage for customers
customers = []
service_professionals = {}

# Database models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # role can be 'customer', 'professional', 'admin'

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.String(250), nullable=False)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    base_price = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(100), nullable=False) 

class Professional(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    fullname = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="Pending")  # Status can be "Pending", "Accepted", or "Rejected"
    category = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.String(100), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    pincode = db.Column(db.String(20), nullable=True)

class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False) 
    status = db.Column(db.String(50), nullable=False, default="Pending")  # Status can be "Pending", "Approved", or "Rejected"
    request_date = db.Column(db.Date, nullable=False) 
    rating = db.Column(db.Integer, nullable=True) 
    professional = db.relationship('Professional', backref=db.backref('service_requests', lazy=True))
    service = db.relationship('Service', backref=db.backref('requests', lazy=True))
    customer = db.relationship('Customer', backref=db.backref('service_requests', lazy=True))

# Initialize the database (run once)
with app.app_context():
    db.create_all()

# Initialize the Admin (run once)
# Admin username = Jatin123 and Password = 123
with app.app_context():
    admin_user = User.query.filter_by(username='Jatin123').first()
    if not admin_user:
        new_user = User(username='Jatin123', password='123', role='Admin')
        db.session.add(new_user)
        db.session.commit()

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Home route
@app.route('/')
def home():
    return redirect(url_for('login'))

# Email of each user (may it be professional or may it be customer) has to be diffrent otherwise code will give error

# Customer signup route
@app.route('/customer_signup', methods=['GET', 'POST'])
def customer_signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        fullname = request.form['fullname']
        address = request.form['address']
        
        # Check if the email is already used as a username
        existing_user = User.query.filter_by(username=email).first()
        if existing_user:
            print('Email is already in use. Please try a different email.', 'error')
            return render_template('customer_signup.html')  # Reload the signup page with the message
        
        # Create a new Customer and User instance if email is not in use
        new_customer = Customer(email=email, name=fullname, address=address)
        new_user = User(username=email, password=password, role="customer")
        
        # Add to the session and commit
        db.session.add(new_customer)
        db.session.add(new_user)
        db.session.commit()
        
        print('Customer signup successful! Please login.')
        return redirect(url_for('login'))
        
    return render_template('customer_signup.html')

# Service professional signup route
@app.route('/professional_signup', methods=['GET', 'POST'])
def professional_signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        fullname = request.form['fullname']
        category = request.form['service']
        experience = request.form['experience']
        address = request.form['address']
        pincode = request.form['pincode']
        
        # Check if the email is already used as a username
        existing_user = User.query.filter_by(username=email).first()
        if existing_user:
            print('Email is already in use. Please try a different email.', 'error')
            return render_template('professional_signup.html')  # Reload the signup page with the message
        
        # Create a new Professional and User instance if email is not in use
        new_professional = Professional(
            email=email,
            fullname=fullname,
            category=category,
            experience=experience,
            address=address,
            pincode=pincode,
            status="Pending"  # Initial status
        )
        new_user = User(username=email, password=password, role="professional")
        
        # Add to the session and commit
        db.session.add(new_professional)
        db.session.add(new_user)
        db.session.commit()
        
        print('Service professional signup successful! Awaiting admin approval.')
        return redirect(url_for('login'))
        
    return render_template('professional_signup.html')

# login route for all user including Admin, User and Professional
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form['role']
        username = request.form['email_or_username'] 
        password = request.form['password']

        if role == "customer":
            # Customer login logic
            customer = User.query.filter_by(username=username, role='customer').first()  # Use email or username
            if customer and customer.password == password:
                session['user'] = username
                login_user(customer)# Store username in session
                print('Customer login successful!')
                return redirect(url_for('customer_dashboard'))
            else:
                print('Invalid username or password')

        elif role == "professional":
            # Professional login logic
            user = User.query.filter_by(username=username, role="professional").first()
            if user and user.password == password:
                professional = Professional.query.filter_by(email=user.username).first()
                if professional:
                    if professional.status == "Accepted":
                        session['user'] = username
                        login_user(user)# Store username in session
                        print('Professional login successful!')
                        return redirect(url_for('professional_dashboard'))
                    elif professional.status == "Pending":
                        print('Pending admin approval. Try logging in again later.')
                    elif professional.status == "Rejected":
                        print('Sorry, your application was rejected. Please try signing up again.')
            else:
                print('Invalid username or password')

        elif role == "admin":
            # Admin login logic
            admin = User.query.filter_by(username=username).first() 
            if admin and admin.password == password: 
                login_user(admin)# Store username in session
                print('Admin login successful!')
                return redirect(url_for('admin_dashboard'))
            else:
                print('Invalid admin credentials')

    return render_template('login.html')


# Admin Functionalities
# Admin Dashboard functionality to add, update and delete service and Accept or reject the professional user
@app.route('/admin-dashboard')
@login_required
def admin_dashboard():
    professionals = Professional.query.all()
    services = Service.query.all()
    service_requests = ServiceRequest.query.all()
    pending_professionals = [prof for prof in professionals if prof.status == "Pending"]
    categories = Service.query.with_entities(Service.category).distinct().all()
    return render_template(
        'admin_dashboard.html',view='home',
        professionals=pending_professionals,
        services=services,
        service_requests=service_requests,
        categories=[category[0] for category in categories]
    )

# To add service in Admin Dashboard
@app.route('/admin/add-service', methods=['POST'])
@login_required
def add_service():
    service_name = request.form.get("serviceName")
    description = request.form.get("description")
    base_price = request.form.get("basePrice")
    category = request.form.get("category")

    new_service = Service(name=service_name, description=description, base_price=int(base_price), category=category)
    db.session.add(new_service)
    db.session.commit()
    return redirect(url_for("admin_dashboard"))

# To edit service in Admin Dashboard
@app.route("/admin/edit-service/<int:service_id>", methods=["POST"])
def edit_service(service_id):
    service = Service.query.get(service_id)
    if service:
        service.name = request.form.get("serviceName")
        service.description = request.form.get("description")
        service.base_price = request.form.get("basePrice", type=int)
        service.category = request.form.get("category")
        db.session.commit()
        print("Service updated successfully!", "success")
    else:
        print("Service not found.", "error")
    
    return redirect(url_for("admin_dashboard"))
    
# To delete service in Admin Dashboard
@app.route("/admin/delete-service/<int:service_id>", methods=["POST"])
def delete_service(service_id):
    service = Service.query.get(service_id)
    if service:
        # Check if there are related records
        related_requests = ServiceRequest.query.filter_by(service_id=service_id).count()
        if related_requests > 0:
            print("Cannot delete service because there are related service requests.", "error")
        else:
            db.session.delete(service)
            db.session.commit()
            print("Service deleted successfully!", "success")
    else:
        print("Service not found.", "error")
    
    return redirect(url_for("admin_dashboard"))

# To accept or reject the professional sign-up in Admin Dashboard
@app.route('/admin/manage-professionals/<int:professional_id>/<action>', methods=['POST'])
@login_required
def manage_professionals(professional_id, action):
    professional = Professional.query.get(professional_id)
    if professional and action in ["accept", "reject"]:
        professional.status = "Accepted" if action == "accept" else "Rejected"
        db.session.commit()
    return redirect(url_for("admin_dashboard"))

# Admin Search Functionality
@app.route('/admin/search', methods=['GET'])
@login_required
def admin_search():
    search_by = request.args.get('searchBy')
    search_text = request.args.get('searchText')
    results = []

    print("Search by:", search_by)
    print("Search text:", search_text)

    if search_by == 'service':
        # Querying the Service table
        results = Service.query.filter(
            (Service.name.contains(search_text)) | (Service.category.contains(search_text))
        ).all()
    elif search_by == 'professional':
        # Querying the Professional table
        results = Professional.query.filter(Professional.fullname.contains(search_text)).all()
    elif search_by == 'request':
        # Querying the ServiceRequest table by joining Service and Professional
        results = ServiceRequest.query.join(Professional).join(Service).filter(
            (Service.name.contains(search_text)) | 
            (Service.category.contains(search_text)) | 
            (Professional.fullname.contains(search_text))
        ).all()

    print("Results:", results)
    return render_template('admin_dashboard.html', view='search', results=results, section='search-functionality')

# Delete Functionality of Admin Search
@app.route('/admin/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete(id):
    # First, check if it's a ServiceRequest, then delete it
    service_request = ServiceRequest.query.get(id)
    if service_request:
        db.session.delete(service_request)
        db.session.commit()
        print('Service Request deleted successfully!', 'success')
    else:
        # If it's not a ServiceRequest, check if it's a Service
        service = Service.query.get(id)
        if service:
            related_requests = ServiceRequest.query.filter_by(service_id=id).count()
            if related_requests > 0:
                print("Cannot delete service because there are related service requests.", "error")
            else:
                db.session.delete(service)
                db.session.commit()
                print("Service deleted successfully!", "success")
        else:
            # If not a Service, check for Professional
            professional = Professional.query.get(id)
    
            if professional:
                db.session.delete(professional)
                db.session.commit()
                print('Professional deleted successfully!', 'success')
            else:
                print('Record not found!', 'error')
    return redirect(url_for('admin_search'))

# To accept or Block the professionals
@app.route('/admin/search-manage-professionals/<int:professional_id>/<action>', methods=['POST'])
@login_required
def search_manage_professionals(professional_id, action):
    professional = Professional.query.get(professional_id)
    if professional and action in ["accept", "block"]:
        # Update the status based on the action
        if action == "accept":
            professional.status = "Accepted"
        elif action == "block":
            professional.status = "Blocked"
        
        # Commit the changes to the database
        db.session.commit()
    
    # Redirect back to the admin dashboard or the search results page
    return redirect(url_for("admin_search"))


# Admin Summary functionality
@app.route('/admin/summary', methods=['GET'])
@login_required
def admin_summary():
    # Count total services, professionals, and requests
    summary_data = {
        "total_services": Service.query.count(),
        "total_professionals": Professional.query.count(),
        "total_requests": ServiceRequest.query.count()
    }

    # Services completed by name
    services_by_name = db.session.query(
        Service.name,
        Service.id,
        func.count(ServiceRequest.id).label('completed_request_count')
        ).join(
            ServiceRequest, ServiceRequest.service_id == Service.id
        ).filter(
            ServiceRequest.status == 'Completed'
        ).group_by(
            Service.id
        ).all()

    # Services by category
    services_by_category = db.session.query(Service.category, db.func.count(Service.id).label('category_count')) \
        .group_by(Service.category).all()

    # Ratings and rating% of each professional, sorted by lowest rating%
    professionals_with_ratings = db.session.query(
    Professional.id,
    Professional.fullname,
    db.func.avg(ServiceRequest.rating).label('avg_rating'),
    (db.func.avg(ServiceRequest.rating) / 5 * 100).label('rating_percentage')
    ).join(ServiceRequest).group_by(Professional.id) \
    .order_by(db.func.avg(ServiceRequest.rating).asc()).all()


    # Print data for debugging
    print(services_by_name)
    print(services_by_category)
    print(professionals_with_ratings)

    return render_template('admin_dashboard.html', view='summary',
                           summary_data=summary_data,
                           services_by_name=services_by_name,
                           services_by_category=services_by_category,
                           professionals_with_ratings=professionals_with_ratings)

# Professional Functionalities
# Fucntionality to Accept, reject and complete service request
@app.route('/professional-dashboard')
@login_required
def professional_dashboard():
    # Fetch the logged-in professional's ID based on their username
    professional = Professional.query.filter_by(email=current_user.username).first()
    
    if not professional:
        print("No professional profile found for this user.", "warning")
        return redirect(url_for('professional_dashboard'))
    
    # Print professional ID to confirm retrieval
    print(f"Professional ID: {professional.id}")

    # Filter pending and approved service requests for the logged-in professional
    pending_services = ServiceRequest.query.options(
        db.joinedload(ServiceRequest.customer),
        db.joinedload(ServiceRequest.service)
    ).filter(
        ServiceRequest.professional_id == professional.id,
        ServiceRequest.status.in_(["Pending", "Accepted"])
    ).all()

    # Filter completed service requests for the logged-in professional
    completed_services = ServiceRequest.query.options(
        db.joinedload(ServiceRequest.customer),
        db.joinedload(ServiceRequest.service)
    ).filter(
        ServiceRequest.professional_id == professional.id,
        ServiceRequest.status.in_(["Completed"])
    ).all()

    # Filter rejected service requests for the logged-in professional
    rejected_services = ServiceRequest.query.options(
        db.joinedload(ServiceRequest.customer),
        db.joinedload(ServiceRequest.service)
    ).filter(
        ServiceRequest.professional_id == professional.id,
        ServiceRequest.status.in_(["Rejected"])
    ).all()

    # Print to confirm data retrieval
    print(f"Pending Services: {pending_services}")
    print(f"Completed Services: {completed_services}")
    print(f"Rejected Services: {rejected_services}")
    services = ServiceRequest.query.filter_by(professional_id=professional.id).all()
    print(services)

    # Organize customers and services for pending and completed requests
    pending_customers = {service.id: service.customer for service in pending_services}
    completed_customers = {service.id: service.customer for service in completed_services}
    rejected_customers = {service.id: service.customer for service in rejected_services}
    pending_services_dict = {service.id: service.service for service in pending_services}
    completed_services_dict = {service.id: service.service for service in completed_services}
    rejected_services_dict = {service.id: service.service for service in rejected_services}

    return render_template(
        'professional_dashboard.html', 
        view='dashboard',
        pending_services=pending_services,
        completed_services=completed_services,
        rejected_services=rejected_services,
        pending_customers=pending_customers,
        completed_customers=completed_customers,
        rejected_customers=rejected_customers,
        pending_services_dict=pending_services_dict,
        completed_services_dict=completed_services_dict,
        rejected_services_dict=rejected_services_dict
    )

# Professional Search Functionality
@app.route('/professional-dashboard/search', methods=['GET'])
@login_required
def professional_search():
    # Fetch the logged-in professional's ID based on their username
    professional = Professional.query.filter_by(email=current_user.username).first()
    
    if not professional:
        print("No professional profile found for this user.", "warning")
        return redirect(url_for('professional_dashboard'))

    search_text = request.args.get('searchText', '')
    results = []

    # Debugging: Print the search text
    print("Search text:", search_text)

    if search_text:
        # Querying ServiceRequest and joining with Customer, Service, and Professional,
        # filtering by professional_id for the logged-in professional
        results = ServiceRequest.query.join(Service).join(Customer).filter(
            ServiceRequest.professional_id == professional.id,  # Filter by professional_id
            (Service.name.contains(search_text)) |
            (Customer.name.contains(search_text)) |
            (Customer.email.contains(search_text))
        ).all()

    # Debugging: Print the fetched results
    print("Results:", results)
    
    return render_template(
        'professional_dashboard.html', 
        view='search', 
        results=results, 
        section='search-functionality'
    )


# Professional Summary Functionality (Rating)
@app.route('/professional-dashboard/summary')
@login_required
def professional_summary():
    # Fetch the logged-in professional's ID based on their username
    professional = Professional.query.filter_by(email=current_user.username).first()
    
    if not professional:
        print("No professional profile found for this user.", "warning")
        return redirect(url_for('professional_dashboard'))

    # Ratings summary data for the specific professional
    positive_reviews = ServiceRequest.query.filter(
        ServiceRequest.professional_id == professional.id,
        ServiceRequest.rating >= 4
    ).count()
    neutral_reviews = ServiceRequest.query.filter(
        ServiceRequest.professional_id == professional.id,
        ServiceRequest.rating == 3
    ).count()
    negative_reviews = ServiceRequest.query.filter(
        ServiceRequest.professional_id == professional.id,
        ServiceRequest.rating < 3
    ).count()

    reviews_ratings = {
        "positive": positive_reviews,
        "neutral": neutral_reviews,
        "negative": negative_reviews
    }

    # Service requests summary data for the specific professional
    total_requests = ServiceRequest.query.filter_by(professional_id=professional.id).count()
    completed_requests = ServiceRequest.query.filter(
        ServiceRequest.professional_id == professional.id,
        ServiceRequest.status == "Completed"
    ).count()
    accepted_requests = ServiceRequest.query.filter(
        ServiceRequest.professional_id == professional.id,
        ServiceRequest.status == "Accepted"
    ).count()
    pending_requests = ServiceRequest.query.filter(
        ServiceRequest.professional_id == professional.id,
        ServiceRequest.status == "Pending"
    ).count()

    service_requests = {
        "total": total_requests,
        "completed": completed_requests,
        "accepted": accepted_requests,
        "pending": pending_requests
    }

    # Render the template with the filtered data and 'view' set to 'summary'
    return render_template(
        'professional_dashboard.html',
        view='summary',
        reviews_ratings=reviews_ratings,
        service_requests=service_requests
    )


#Profesional Dashboard Accept functionality
@app.route('/professional/accept-service/<int:service_id>', methods=['GET', 'POST'])
@login_required
def accept_service(service_id):
    # Fetch the logged-in professional's ID based on their username
    professional = Professional.query.filter_by(email=current_user.username).first()
    
    if not professional:
        print("No professional profile found for this user.", "warning")
        return redirect(url_for('professional_dashboard'))

    # Retrieve the service request using the service_id
    service_request = ServiceRequest.query.get(service_id)
    
    if not service_request:
        print("Service request not found.", "danger")
        return redirect(url_for('professional_dashboard'))

    # Check if the service request belongs to the professional
    if service_request.professional_id != professional.id:
        print("You cannot accept this service request.", "danger")
        return redirect(url_for('professional_dashboard'))

    # Update the service request status to 'Accepted'
    service_request.status = 'Accepted'
    db.session.commit()
    
    print("Service request accepted successfully.", "success")
    return redirect(url_for('professional_dashboard'))

#Profesional Dashboard Complete functionality
@app.route('/professional/complete-service/<int:service_id>', methods=['GET', 'POST'])
@login_required
def complete_service(service_id):
    # Fetch the logged-in professional's ID based on their username
    professional = Professional.query.filter_by(email=current_user.username).first()

    if not professional:
        print("No professional profile found for this user.", "warning")
        return redirect(url_for('professional_dashboard'))

    # Retrieve the service request using the service_id
    service_request = ServiceRequest.query.get(service_id)
    
    if not service_request:
        print("Service request not found.", "danger")
        return redirect(url_for('professional_dashboard'))

    # Check if the service request belongs to the professional
    if service_request.professional_id != professional.id:
        print("You cannot complete this service request.", "danger")
        return redirect(url_for('professional_dashboard'))

    # Update the service request status to 'Completed'
    service_request.status = 'Completed'
    db.session.commit()
    
    print("Service request completed successfully.", "success")
    return redirect(url_for('professional_dashboard'))

#Profesional Dashboard Reject functionality
@app.route('/professional/reject_service/<int:service_id>', methods=['GET', 'POST'])
@login_required
def reject_service(service_id):
    # Fetch the logged-in professional's ID based on their username
    professional = Professional.query.filter_by(email=current_user.username).first()

    if not professional:
        print("No professional profile found for this user.", "warning")
        return redirect(url_for('professional_dashboard'))

    # Retrieve the service request using the service_id
    service_request = ServiceRequest.query.get(service_id)
    
    if not service_request:
        print("Service request not found.", "danger")
        return redirect(url_for('professional_dashboard'))

    # Check if the service request belongs to the professional
    if service_request.professional_id != professional.id:
        print("You cannot complete this service request.", "danger")
        return redirect(url_for('professional_dashboard'))

    # Update the service request status to 'Completed'
    service_request.status = 'Rejected'
    db.session.commit()
    
    print("Service request completed successfully.", "success")
    return redirect(url_for('professional_dashboard'))



# Customer Functionality
@app.route('/customer-dashboard')
@login_required
def customer_dashboard():
    # Fetch all available services
    services = Service.query.all()

    # Fetch all service requests for the logged-in customer
    requests = ServiceRequest.query.filter_by(customer_id=current_user.id).all()
    completed_requests = ServiceRequest.query.filter_by(customer_id=current_user.id, status='Completed').all()

    # Render the customer dashboard template, passing 'view' and services data
    return render_template(
        'customer_dashboard.html',
        view='home',  # Set the view to 'home' to display the available services
        services=services,
        requests=requests,
        completed_requests=completed_requests,
    )

# Customer Search Functionality
@app.route('/customer-dashboard/search', methods=['GET'])
@login_required
def customer_search():
    # Fetch the logged-in customer's ID based on their username
    customer = Customer.query.filter_by(email=current_user.username).first()
    
    if not customer:
        print("No customer profile found for this user.", "warning")
        return redirect(url_for('customer_dashboard'))

    search_by = request.args.get('searchBy')
    search_text = request.args.get('searchText')
    results = []

    # Debugging: Print the selected search options
    print("Search by:", search_by)
    print("Search text:", search_text)

    if search_by == 'service':
        # Querying the Service table
        results = Service.query.filter(
            (Service.name.contains(search_text)) | (Service.category.contains(search_text))
        ).all()
    elif search_by == 'professional':
        # Querying the Professional table
        results = Professional.query.filter(Professional.fullname.contains(search_text)).all()
    elif search_by == 'request':
        # Querying the ServiceRequest table by joining Service and Professional
        # Filter by customer_id to ensure the search is for the logged-in customer's requests
        results = ServiceRequest.query.join(Professional).join(Service).filter(
            ServiceRequest.customer_id == customer.id,  # Ensure search is filtered by the logged-in customer
            (Service.name.contains(search_text)) | 
            (Professional.fullname.contains(search_text))
        ).all()

    # Debugging: Print the results fetched from the database
    print("Results:", results)

    return render_template(
        'customer_dashboard.html', 
        view='search', 
        results=results, 
        section='search-functionality'
    )

# Customer Service Request Functionality
@app.route('/customer/request-service', methods=['GET', 'POST'])
@login_required
def customer_request_service():
    # Log current user for debugging purposes
    print("Current User:", current_user)

    # Retrieve customer data based on the logged-in user
    customer = Customer.query.filter_by(email=current_user.username).first()

    # Debug: Check if customer is found
    print("Customer found:", customer)

    if not customer:
        return jsonify({'success': False, 'message': 'Customer not found'}), 400

    if request.method == 'GET':
        # Render the form only if the view is set to 'request-service'
        return render_template('customer_dashboard.html', view='request-service')
    
    # If the request method is POST, process the form submission
    data = request.get_json()

    service_id = data.get('serviceId')
    professional_id = data.get('professionalId')
    request_date = data.get('requestDate')

    # Check if the provided data is valid
    if not service_id or not professional_id or not request_date:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    # Create a new ServiceRequest instance
    new_request = ServiceRequest(
        service_id=service_id,
        professional_id=professional_id,
        customer_id=customer.id,
        request_date=datetime.strptime(request_date, "%Y-%m-%d"),
    )

    # Add the service request to the session and commit
    db.session.add(new_request)
    db.session.commit()
    # Return a success response
    return jsonify({'success': True, 'message': 'Service request created successfully'}), 200


# Customer Requested Services
@app.route('/customer/requested-services', methods=['GET'])
@login_required
def requested_services():
    # Fetch the logged-in customer's details using their email
    customer = Customer.query.filter_by(email=current_user.username).first()
    
    if not customer:
        print("No customer profile found for this user.", "warning")
        return redirect(url_for('home'))
    
    # Fetch all service requests for the logged-in customer
    all_services = ServiceRequest.query.options(
        db.joinedload(ServiceRequest.customer),
        db.joinedload(ServiceRequest.service),
        db.joinedload(ServiceRequest.professional)
    ).filter(ServiceRequest.customer_id == customer.id).all()

    # Categorize services by status
    categorized_services = {
        'Accepted': [],
        'Pending': [],
        'Rejected': [],
        'Completed': []
    }

    for service in all_services:
        categorized_services[service.status].append(service)

    # Debug prints for verification
    print(f"Accepted Services: {categorized_services['Accepted']}")
    print(f"Pending Services: {categorized_services['Pending']}")
    print(f"Rejected Services: {categorized_services['Rejected']}")
    print(f"Completed Services: {categorized_services['Completed']}")
    
    # Render the template with categorized services
    return render_template(
        'customer_dashboard.html',
        view='requested-services',
        categorized_services=categorized_services
    )


# Customer Submit Rating
@app.route('/customer/service_requests', methods=['GET'])
def show_service_requests():
    service_requests = ServiceRequest.query.filter(
        and_(
            ServiceRequest.status == 'Completed',
            ServiceRequest.rating == None  # Checks if rating is not null
        )
    ).all()
    return render_template('customer_dashboard.html',view='review', service_requests=service_requests)

@app.route('/customer/submit_rating', methods=['POST'])
def submit_rating():
    service_request_id = request.json.get('serviceRequestId')
    rating = request.json.get('rating')

    if service_request_id and rating is not None:
        service_request = ServiceRequest.query.get(service_request_id)
        if service_request:
            service_request.rating = rating
            db.session.commit()

            return jsonify({"success": True, "message": "Rating submitted successfully"})
        else:
            return jsonify({"success": False, "message": "Service request not found"})
    else:
        return jsonify({"success": False, "message": "Invalid data provided"})
    
# Get Professionals by Category
@app.route('/get_professionals/<category>', methods=['GET'])
def get_professionals(category):
    professionals = Professional.query.filter_by(category=category).all()
    return jsonify({'professionals': [{'id': p.id, 'fullname': p.fullname} for p in professionals]})

# Get Services by Category
@app.route('/get_services/<category>', methods=['GET'])
def get_services(category):
    services = Service.query.filter_by(category=category).all()
    return jsonify({'services': [{'id': s.id, 'name': s.name} for s in services]})



# Logout Route for all the users
@app.route('/logout')
def logout():
    session.clear()  # Clear all session data
    print("You have been logged out.")
    return redirect(url_for('login'))



#calling the main and implementing th code
if __name__ == '__main__':
    app.run(debug=True)
