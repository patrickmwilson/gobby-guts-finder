import csv;
import requests;
import os;

resultsFileName = "results.csv";
searchTermsFileName = 'PNPSearchTerms.csv';
searchRadius = '100';
zipCode = '94108';
pickAndPullVehicleLink = "https://www.picknpull.com/check-inventory/vehicle-details/%s"
pickAndPullApiURI = "https://www.picknpull.com/api/vehicle/search?&makeId=%s&modelId=%s&year=%s&distance=%s&zip=%s&language=english";
pickAndPullSearchByVinApiURI = "https://www.picknpull.com/api/vehicle/%s"
vinDecoderApiURI = "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValuesExtended/%s?format=json&modelyear=%s"

#from vin decoder: ModelYear, Model, Trim, BodyClass, VIN
#from PNP by vin: transmission, engine, dateAdded (get substring of first 10), city

def makeVinDecoderRequest(vin,year):
     return requests.get(vinDecoderApiURI%(vin,year)).json()

def writeVehicleDataToCsv(pnpData):
     file_exists = os.path.isfile(resultsFileName)
     with open(resultsFileName, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if file_exists == False:
            writer.writerow(['Year','Model','Transmission','Engine','Body','VIN','Set Date','City','Link'])

        vinDecoderData = makeVinDecoderRequest(pnpData['vin'],pnpData['year'])['Results'][0]
        year = vinDecoderData['ModelYear']
        model = vinDecoderData['Model']
        trans = pnpData['transmission']
        if '|' in trans:
             trans = ''
        engine = pnpData['engine']
        body = vinDecoderData['BodyClass']
        vin = vinDecoderData['VIN']
        setDate = (pnpData['dateAdded'])[0:10]
        city = pnpData['city']
        link = pickAndPullVehicleLink%vin
        print(year,model,trans,engine,body,vin,setDate,city,link)
        writer.writerow([year,model,trans,engine,body,vin,setDate,city,link])

def makePickAndPullGetRequestByVin(vin):
     return requests.get(pickAndPullSearchByVinApiURI%(vin)).json()

def getVehicleInfoByVin(vin):
     pnpData = makePickAndPullGetRequestByVin(vin)['vehicle']
     writeVehicleDataToCsv(pnpData)

def parsePickAndPullInventory(data):
     for location in data:
          for vehicle in location['vehicles']:
               getVehicleInfoByVin(vehicle['vin'])
     
def makePickAndPullGetRequest(makeID,modelID,year):
        data = requests.get(pickAndPullApiURI%(makeID,modelID,year,searchRadius,zipCode)).json()
        parsePickAndPullInventory(data)

def searchJunkyards(): 
    with open(searchTermsFileName, newline='') as csvfile: 
        reader = csv.DictReader(csvfile)
        for row in reader: 
            makePickAndPullGetRequest(row['Make_ID'],row['Model_ID'],row['Year']);

searchJunkyards()