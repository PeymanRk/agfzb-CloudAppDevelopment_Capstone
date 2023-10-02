from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)

dealership_url = "https://us-south.functions.appdomain.cloud/api/v1/web/6b4c87a1-fb5b-406c-b608-50383fed62a0/dealership-package/dealership"
review_url = "https://us-south.functions.appdomain.cloud/api/v1/web/6b4c87a1-fb5b-406c-b608-50383fed62a0/dealership-package/review"

args = {
    "COUCH_URL": "https://56b90a26-c500-4d17-a692-797d5dceb66d-bluemix.cloudantnosqldb.appdomain.cloud",
    "IAM_API_KEY": "gSeugYqaUmOWRXcsCyyeYxHCmr9wmM_BhpB0mPz2BcUH",
    "COUCH_USERNAME": "56b90a26-c500-4d17-a692-797d5dceb66d-bluemix"
}

cars = [
        {'id': 1, "make": "Subaru", "name": "Forester", "year": "2020"},
        {'id': 2, "make": "BMW", "name": "i8", "year": "2019"},
        {'id': 3, "make": "Mersedes-Benz", "name": "GLA250", "year": "2021"},
        {'id': 4, "make": "Lamborghini", "name": "Aventador", "year": "2015"},
        {'id': 5, "make": "Toyota", "name": "CH-R", "year": "2018"},
        {'id': 6, "make": "Toyota", "name": "Rav4", "year": "2020"},
        {'id': 7, "make": "Mazda", "name": "SX5", "year": "2022"},
        {'id': 8, "make": "Hyundai", "name": "SantaFe", "year": "2020"},
        {'id': 9, "make": "Ford", "name": "Mustang", "year": "2023"},
        {'id': 10, "make": "Chevrolet", "name": "Camaro", "year": "2023"},
    ]
# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    if request.method == "GET":
        return render(request, 'static/about.html')


# Create a `contact` view to return a static contact page
def contact(request):
        if request.method == "GET":
            return render(request, 'static/contact.html')

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['psw']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            return redirect('djangoapp:index')
        else:
            # If not, return to login page again
            return render(request, 'djangoapp/user_login.html', context)
    else:
        return render(request, 'djangoapp/user_login.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    # Get the user object based on session id in request
    print("Log out the user `{}`".format(request.user.username))
    # Logout user in the request
    logout(request)
    # Redirect user back to course list view
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        # Get user information from request.POST
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            # Login the user and redirect to course list page
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":        
        dealerships = get_dealers_from_cf(dealership_url, **args)
        context = {'dealership_list': dealerships}
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        reviews = get_dealer_reviews_from_cf(review_url, dealerId = dealer_id,**args)
        dealerships = get_dealers_from_cf(dealership_url, **args)
        dealers = list(filter(lambda x: x.id == dealer_id, dealerships))        
        if len(dealers) == 1:
            dealer = dealers[0]
        else:
            dealer["full_name"] = "undefined"          
        context = {'reviews': reviews, 'dealer': dealer}
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...
def add_review(request, dealer_id):
    context = {'dealer_id': dealer_id}
    if request.method == "GET":
        dealerships = get_dealers_from_cf(dealership_url, **args)
        dealers = list(filter(lambda x: x.id == dealer_id, dealerships))        
        if len(dealers) == 1:
            context['dealer_name'] = dealers[0].full_name
        else:
            context['dealer_name'] = "undefined"          
        context['cars']= cars
        return render(request, 'djangoapp/add_review.html', context)

    elif request.method == "POST":
        review= dict()
        review["time"] = datetime.utcnow().isoformat()
        review["name"] = request.user.username
        review["dealership"] = dealer_id
        review["review"] = request.POST["content"]
        review["purchase"] = request.POST["purchasecheck"]
        # review["another"] = "another"
        review["purchase_date"] = request.POST["purchasedate"]
        car = [x for x in cars if x['id']==int(request.POST["car"])][0]
        review["car_make"] = car['make']
        review["car_model"] = car['name']
        review["car_year"] = car['year']
        json_payload = dict()
        json_payload["review"] = review
        new_args = args.copy()
        new_args["dealerId"] = dealer_id

        resp = post_request(review_url, json_payload, **new_args)
        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
