#Google dan mekanları listeleyebilmemiz için eklememiz hgerken kütüphanler
import googlemaps
import pprint
import time

#IP Adresinden konum öğrenmek için eklememiz gereken kütüphaneler
import geocoder  
g = geocoder.ip('me')
#print(g.latlng[0])


#from GoogleMapsAPIKey import get_my_key

#API_KEY = get_my_key()



from urllib.parse import quote,unquote  #Stringleri link formatına çevirmek ve link formatındaki yazıları Stringlere çevirmek için dahil ettğimiz kütüphane

import http.client  #Nöbetçi eczane apisinden eczaneleri çekebilmemiz için eklememiz gereken kütüphane





gmaps = googlemaps.Client(key = "AIzaSyDFpmvAJ9pYCUmdfOx3tmX3iFUmfm3F894")

def mekanDon(enlem,boylam,mekanAdi):
    places_result = gmaps.places_nearby(location = "{},{}".format(enlem, boylam),radius = 40000,open_now = False,type=str(mekanAdi),language = "tr")

    yakinMekanlar = list()
#pprint.pprint(places_result)
    for i in range(0,5):


        mekan = places_result["results"][i]

        enlem = mekan["geometry"]["location"]["lat"]
        boylam = mekan["geometry"]["location"]["lng"]

        icon = mekan["icon"]

        isim = mekan["name"]

        #acikMi = mekan["opening_hours"]["open_now"]

        adres = mekan["vicinity"]

        yakinMekanlar.append({"enlem":enlem,"boylam":boylam,"icon":icon,"isim":isim,"adres":adres})

    # print({"enlem":enlem,"boylam":boylam,"icon":icon,"isim":isim,"acikMi":acikMi,"adres":adres})

    return yakinMekanlar
    #return {"enlem":enlem,"boylam":boylam,"icon":icon,"isim":isim,"acikMi":acikMi,"adres":adres}


def nobetciDon(il,ilce):

    # ilce = "bayramören"
    url_ilce = quote(ilce)

    # il = "ÇANKIRI"
    url_il = quote(il)

    conn = http.client.HTTPSConnection("api.collectapi.com")

    headers = {
        'content-type': "application/json",
        'authorization': "apikey 77IWojiJOaAwZNUaMZyIJc:3co27WHmUyXmm55mKPnY5G"
        }

    conn.request("GET", "/health/dutyPharmacy?ilce={}&il={}".format(url_ilce,url_il), headers=headers)

    res = conn.getresponse()
    data = res.read()

    sonuclar = data.decode("utf-8")

    return sonuclar

    # if(dict(sonuclar).get("success") =="true"):

    #     print("true")

    # elif(str(sonuclar["success"]) =="false"):

    #     print("false")


# nobetciDon("Çankırı","Merkez")["success"]


#print(mekanDon(40.8884921,29.1896017))

# {"success":true,"result":[{"name":"ÖNDER ECZANESİ","dist":"KURŞUNLU","address":"MÜSLÜM MAH.ISTASYON CAD.NO.23/A KURSUNLU","phone":"3764651365","loc":"40.84089696,33.26142384"}]}
# nobetciDon("ÇANKIRI","MERKEZ")

# {"status":"400","success":false,"result":{"error":"There is no information about this district."}}