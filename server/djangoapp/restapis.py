import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 \
    import Features, SentimentOptions, EntitiesOptions, KeywordsOptions

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, api_key=None, **kwargs):    
    print("GET from {} ".format(url))
    try:
        if api_key:
            # Call get method of requests library with URL and parameters            
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                        params=kwargs, auth=HTTPBasicAuth('apikey', api_key))
        else:
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                        params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)    
    return json_data, status_code


# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    try:
        response = requests.post(url, params=kwargs, json=json_payload)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)    
    # print("resp: {} ".format(response))
    # print("resp: {} ".format(response.text))
    return json_data

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result, _ = get_request(url, **kwargs)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)
    return results


# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, dealerId, **kwargs):
    results = []
    new_args = kwargs.copy()
    new_args["dealerId"] = dealerId
    json_result, code = get_request(url, **new_args)    
    if code==404:
        print("no review")
        return None
    elif json_result:
        for review in json_result:
            doc = review            
            review_obj = DealerReview(
                dealership=doc.get("dealership", ""),
                name=doc.get("name", ""),
                purchase=doc.get("purchase", ""),
                review=doc.get("review", ""),
                purchase_date=doc.get("purchase_date", ""),
                car_make=doc.get("car_make", ""),
                car_model=doc.get("car_model", ""),
                car_year=doc.get("car_year", ""),
                id=doc.get("id"),
                sentiment="null")
            review_obj.sentiment = analyze_review_sentiments(review_obj.review)            
            results.append(review_obj)
    return results    


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(text):    
    url="https://api.au-syd.natural-language-understanding.watson.cloud.ibm.com/instances/9ff4fda8-151d-4d6f-96f2-0e95cd6cb344"    
    authenticator = IAMAuthenticator('Y4GTm1rCp9BXV7XMFXRNpUvNYM4cQsFpdaCfCH4T0Ob8')
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2022-04-07',
        authenticator=authenticator
    )
    natural_language_understanding.set_service_url(url)

    response = natural_language_understanding.analyze(
        text=text,
        features=Features(            
            sentiment=SentimentOptions(document=True)
        )).get_result()    
    return response['sentiment']['document']['label']