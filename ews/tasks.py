# Create your tasks here
from celery import shared_task
from .models import *
import requests
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
from decouple import config
import datetime
from ews.helper_functions import *
import pandas as pd
from ews.helper_classes import KRock
import numpy as np
import json
@shared_task
def contextBroker(contextBrokerID):
    
    client_id = config('CLIENT_ID')
    client_secret = config('CLIENT_SECRET')
    redirect_uri = config('REDIRECT_URI')
    client = BackendApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)

    token = oauth.fetch_token(token_url='https://k-rock.xyz/oauth2/token', client_id=client_id,
        client_secret=client_secret)
    headers = { 'X-Auth-Token': token["access_token"]}
    get = requests.get(url="https://www.c-broker.xyz/v2/entities/" + contextBrokerID + "/attrs/precipitation/value", headers = headers, verify = False)
    
    site_id = contextBrokerID.split(":")[-2]

    dt = datetime.datetime.now()
    date = dt.strftime('%Y-%m-%d %H:%M:%S')
    fd = FeatureData()
    fd.date = date
    fd.value = get.json()
    fd.site = Site.objects.get(id = site_id)
    fd.save()
    return print([fd.value, fd.site, fd.date])
    #fd.save()
    
    #x = get.json() + 1
    #requests.put("https://www.c-broker.xyz/v2/entities/BerlinWeatherObserved-Spree/attrs/precipitation/value", 
    #               verify = False, 
    #headers = {
    #'Content-Type':'text/plain',
    #'X-Auth-Token': token["access_token"]
    #},data = str(x))
    #return print(PUT.json())

@shared_task
def predict(model_id):
    model_id = 1
    predict = predict_daterange(start = datetime.datetime.strptime(datetime.datetime.now(), "%Y-%m-%d") ,
                end = datetime.datetime.strptime(datetime.datetime.now(), "%Y-%m-%d"), 
                model_id=model_id).to_json(orient='records')
    print(predict)
  

@shared_task
def predict_testmodel():
    #print(model_id)
    # get current datetime
    today = datetime.datetime.now()
    mu = np.random.normal(2.9, .4, 1)
    sigma = np.random.uniform(0.5, 1, 1)
    dist = np.random.normal(mu, sigma, 10000)
    # Get current ISO 8601 datetime in string format
    iso_date = today.isoformat()
    quantiles = np.quantile(dist, [0.025, 0.5, 0.9, 0.95, 0.975 ])
    
    payload = {"dateCreated": {
                "type": "DateTime",   
                "value": iso_date
                },
        'predictionValues': {'type': 'StructuredValue',
                                    'value': [
                                    {'percentile': '2.5', 'value': quantiles[0]},
                                    {'percentile': '50', 'value': quantiles[1]},
                                    {'percentile': '90', 'value': quantiles[2]},
                                    {'percentile': '95', 'value': quantiles[3]},
                                    {'percentile': '97.5', 'value': quantiles[4]}],
                                    'metadata': {}}}
    patch = requests.patch(url="https://www.c-broker.xyz/v2/entities/urn:ngsi-ld:WaterQualityPredicted:model1/attrs",   
    headers = {
    'Content-Type':'application/json',
    'X-Auth-Token': KRock.KRock.get_token(), ###### token using credentials I’ve sent
    },data = json.dumps(payload),verify = False)


    return print(patch.content)





@shared_task
def aggregate_to_daily(aggregation_date  = datetime.date.today()):
    yesterday = aggregation_date - datetime.timedelta(days=1)

    #aggregate rainfall
    rainfall = pd.DataFrame(list(FeatureData.objects.filter(date__date=yesterday, 
                                                  site__in = Site.objects.filter(feature_type__name = "Rainfall")).values())).set_index("date")
    rainfall = rainfall.groupby(["site_id", "variable_id", "method_id"]).resample("D").sum().drop(["site_id", "variable_id", "method_id"], axis = 1).reset_index()
    # aggregate data from other Feature Types
    others = pd.DataFrame(list(FeatureData.objects.filter(date__date=yesterday, 
                                                  site__in = Site.objects.filter(feature_type__name__in = ["WWTP", "Riverflow", "Network"])).values())).set_index("date")
    others = others.groupby(["site_id", "variable_id", "method_id"]).resample("D").mean().drop(["site_id", "variable_id", "method_id"], axis = 1).reset_index()  
    
    # delete high frequency data
    FeatureData.objects.filter(date__date=yesterday).delete()
    
    # Save rainfall data
    for index, row in rainfall.iterrows():
        dpoint = FeatureData()
        dpoint.date = row["date"]
        dpoint.value = row["value"]
        dpoint.variable = Variable.objects.get(id = row["variable_id"])
        dpoint.method = Method.objects.get(id = row["method_id"])
        dpoint.site = Site.objects.get(id = row["site_id"])
        dpoint.save()

    # Save other data
    for index, row in others.iterrows():
        dpoint = FeatureData()
        dpoint.date = row["date"]
        dpoint.value = row["value"]
        dpoint.variable = Variable.objects.get(id = row["variable_id"])
        dpoint.method = Method.objects.get(id = row["method_id"])
        dpoint.site = Site.objects.get(id = row["site_id"])
        dpoint.save()

        return("data imported")
