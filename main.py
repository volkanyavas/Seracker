# Adresten enlem ve boylam değerlerini bulabilmek için ekleeen kütüphane
from geopy.geocoders import Nominatim
import tahlilTo_db
import glob  # klasördeki dosyaları taramak için eklenen kütüphane
import os  # yyüklenen tahlilleri geçici olarak klasörde tutmak için eklenen kütüphane
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, IntegerField, SelectField
from passlib.handlers.sha2_crypt import sha256_crypt

# flask yardımıyla decoratorlarımızı yazabilmek için wraps modülünü dahil ediyoruz
from functools import wraps

import functions  # yazdığım özel fonksyionları dahil eder
from maps import mekanDon  # yazdığımız goog-map fonskiyonunu dahil ediyoruz

# Firebase' a bağlanabilmek için eklenen kütüphaneler
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Ana dizindeki firebase anahtar ile firebase bağlantısı kurulması
# cred = credentials.Certificate("fir-python-52324-firebase-adminsdk-ox1mz-f2f13b9080.json")
cred = credentials.Certificate(
    "seracker-cd8df-firebase-adminsdk-c5wua-8f94ae24d2.json")

firebase_admin.initialize_app(cred)


import tabula #pdften okuma işlemleri yapabilmemiz için eklememiz gerek kütüphane

import requests
import urllib.parse



from datetime import date #Mevcut zamanı alabilemmiz için gerekli kütüphane


import numpy as np


def uzunlukDon(liste):
    return len(liste)

def takipIstekleri(userID):

    db = firestore.client()
    doc = db.collection("Users").document(userID).collection(
        "takipciler").where("durum", "==", 0).stream()

    eslesmeYok = True

    takipciIstekler = list()
    for i in doc:

        eslesmeYok = False
        takipciIstekler.append(i)

    if(not eslesmeYok):

        return takipciIstekler

    else:
        return 0

def onaylananTakipler(userID):

    db = firestore.client()
    doc = db.collection("Users").document(userID).collection(
        "takipEdilenler").where("durum", "==", 1).stream()

    eslesmeYok = True

    takipAkraba = list()
    takipAile = list()
    takipArkadas = list()

    for i in doc:

        eslesmeYok = False

        if(i.to_dict()["yakinlik"] == 0):
            takipAile.append(i)

        elif(i.to_dict()["yakinlik"] == 1):
            takipAkraba.append(i)

        elif(i.to_dict()["yakinlik"] == 2):
            takipArkadas.append(i) 


    onaylanan_takipler = {"aile":takipAile,"akraba":takipAkraba,"arkadas":takipArkadas}

    if(not eslesmeYok):

        return onaylanan_takipler

    else:
        return 0


def izinleriDon(userID,takipEdilen_ID):

    db = firestore.client()
    result = db.collection("Users").document(takipEdilen_ID).collection("takipciler").document(userID).get()

    return result


def userInfo(userID):

    db = firestore.client()
    result = db.collection("Users").document(userID).get()

    return result


def bildirimIslemleri(islem,takipci_yakinlik,tahlil,adim,nabiz):

    bilgi = islem.split("_")

    takipci_userID = bilgi[1]

    if(bilgi[0] == "0"):  # Burada yakın takip isteği ikinci indiste verilecek kullanıcı ID için reddeliyor demektir
        print("Reddetme", bilgi[1])

        

        db = firestore.client()
        doc = db.collection("Users").document(session["userID"]).collection("takipciler").document(takipci_userID)
        takipciGuncelleme = {"userID": takipci_userID, "yakinlik": -1,"durum": 3, "tahlil": False, "nabiz": False, "adim": False}
        doc.set(takipciGuncelleme)

        # takip isteği gönderen takipcinin takipEdilenler listesine oturumu açık olan kullanıcının reddettiği için durumu 3 ile güncellenir
        doc = db.collection("Users").document(takipci_userID).collection(
            "takipEdilenler").document(session["userID"])
        takipGuncelleme = {"userID": takipci_userID, "durum": 3}
        doc.set(takipGuncelleme)

    elif(bilgi[0] == "1"):  # Burada yakın takip isteği ikinci indiste verilecek kullanıcı ID için onaylanıyor demektir

        

        if(tahlil == "tahlil"):
            tahlil = True
        else:
            tahlil = False

        if(adim == "adim"):
            adim = True
        else:
            adim = False

        if(nabiz == "nabiz"):
            nabiz = True
        else:
            nabiz = False

        

        db = firestore.client()
        doc = db.collection("Users").document(session["userID"]).collection("takipciler").document(takipci_userID)
        takipciGuncelleme = {"userID": takipci_userID, "yakinlik": yakinlikDon(takipci_yakinlik),"durum": 1, "tahlil": tahlil, "nabiz": nabiz, "adim": adim}
        doc.set(takipciGuncelleme)

        # takip isteği gönderen takipcinin takipEdilenler listesine oturumu açık olan kullanıcının onaylamış bilgileri ile güncellenir
        doc = db.collection("Users").document(takipci_userID).collection("takipEdilenler").document(session["userID"])
        takipGuncelleme = {"userID": takipci_userID, "durum": 1}
        
        doc.set(takipGuncelleme,merge = True) # Merge true ile önceden va rolan verileri silmemiş oluruz

    elif(bilgi[0] == "2"):

        print("Bşardık")

        print("Onaylama", bilgi[1])



def tahlilOkuma(tahlilYol,userID):

    table1 = tabula.read_pdf(tahlilYol,pages=1)
    #table2 = tabula.read_pdf(tahlilYol,pages=2)

    strTahlil = str(table1)#+str(table2)
    liste = strTahlil.split("\n")


    tahliller = list()
    sozluk =dict()

    for i in liste:
        
        string = list(i)

        sayı=0
        while(sayı<len(string)):

            if(string[sayı]==" " and string[sayı+1]==" " and string[sayı+2]==" "):
                string.pop(sayı)
                
            else:
                sayı+=1
        
        str1 = ''.join(string)
        ayri = str1.split("  ")

        if(ayri[0] != "["):

            sozluk.update({str(ayri[2]) : {"tarih": ayri[1],"sonuç": ayri[3],"birim":ayri[4],"referans":ayri[5]}} )
            #sozluk.update({"{}".format(ayri[2]) : [ayri[3],ayri[4],ayri[5]]} )

    firstTime = True
    db = firestore.client()
    
    tarih = "-"
    for i,j in sozluk.items():

        if(firstTime):
            firstTime = False
            
            tarih = j.get("tarih")

            doc = db.collection("Users").document(userID).collection("tahliller").document(tarih)#Otomatik şekilde idnin oluşturulması
            doc.set({"tarih":tarih})

        doc = db.collection("Users").document(userID).collection("tahliller").document(tarih).collection("sonuclar").document(i)
        doc.set({"sonuc":j.get("sonuç"),"birim":j.get("birim"),"referans":j.get("referans")})


def tahlilAra(userID):

    db = firestore.client()
    doc = db.collection("Users").document(userID).collection("tahliller").stream()

    eslesmeYok = True

    tahliller = list()
    for i in doc:

        eslesmeYok = False
        tahliller.append(i)

    if(not eslesmeYok):

        return tahliller

    else:
        return 0

def kayitliTahliller(userID):
    db = firestore.client()
    doc = db.collection("Users").document(userID).collection("tahliller").stream()

    eslesmeYok = True

    kayitliTahliller = list()
    for i in doc:

        eslesmeYok = False
        kayitliTahliller.append(str(i.id))

    if(not eslesmeYok):

        return kayitliTahliller

    else:
        return 0



def tahlilAyrintilari(userID,tahlilTarih):

    tahlilTarih = str(tahlilTarih).replace("\r","\\r")

    db = firestore.client()
    doc = db.collection("Users").document(userID).collection("tahliller").document(tahlilTarih).collection("sonuclar").stream()

    eslesmeYok = True

    tahlilSonuclar = list()
    for i in doc:

        eslesmeYok = False
        tahlilSonuclar.append(i)

    if(not eslesmeYok):

        return tahlilSonuclar

    else:
        return 0




def nabizGun_veriAra(userID):

    db = firestore.client()
    doc = db.collection("Users").document(userID).collection("nabizOrt").stream()

    eslesmeYok = True

    nabizGunluk_veriler = list()
    for i in doc:

        eslesmeYok = False
        nabizGunluk_veriler.append(str(i.id))

    if(not eslesmeYok):

        return nabizGunluk_veriler

    else:
        return 0


def nabizAyrintilari(userID,nabizTarih):

    db = firestore.client()
    doc = db.collection("Users").document(userID).collection("nabizOrt").document(nabizTarih).get()

    nabizSonuclari = doc.to_dict()["ortalama"]
    

    # nabizDatas = list()

    # for i in nabizSonuclari:
    #     intNabiz = int(i[0:3])
    #     nabizDatas.append(intNabiz)

    # npNabiz_datas = np.array(nabizSonuclari)
    # nabizOrt = npNabiz_datas.mean()

    # return round(nabizOrt)
    return nabizSonuclari

def nabizVerileri(userID,nabizTarih):

    db = firestore.client()
    doc = db.collection("Users").document(userID).collection("nabiz").document(nabizTarih).get()

    nabizSonuclari = doc.to_dict()["nabiz"]


    return nabizSonuclari





def adimGun_veriAra(userID):

    db = firestore.client()
    doc = db.collection("Users").document(userID).collection("adim").stream()

    eslesmeYok = True

    adimGunluk_veriler = list()
    for i in doc:

        eslesmeYok = False
        adimGunluk_veriler.append(str(i.id))

    if(not eslesmeYok):

        return adimGunluk_veriler

    else:
        return 0


def adimAyrintilari(userID,adimTarih):

    db = firestore.client()
    doc = db.collection("Users").document(userID).collection("adim").document(adimTarih).get()

    adimSonucu = doc.to_dict()["adim"]

    return adimSonucu







def yakinlikOgren(yakinlikNumber):

    if(yakinlikNumber == 0):
        return "Aile"
    elif(yakinlikNumber == 1):
        return "Akraba"
    elif(yakinlikNumber == 2):
        return "Arkadas"
    return "BİR HATA MEYDANA GELDİ yakinlikOgren"

def yakinlikDon(yakinlikString):

    if(yakinlikString == "aile"):
        return 0
    elif(yakinlikString == "akraba"):
        return 1
    elif(yakinlikString == "arkadas"):
        return 2
    return "BİR HATA MEYDANA GELDİ yakinlikDon"



def yasHesapla(dogumTarihi):

   dogumTarihi = int(dogumTarihi[0:4])

   today = date.today()
   simdikiYil = int(today.strftime("%Y"))

   return simdikiYil-dogumTarihi


def kitleEndeksi_hesapla(boy,kilo):

    boy = float(float(boy)/100)
    kilo = float(kilo)

    return  "{0:.2f}".format(kilo/(boy*boy))



def intDon(floatDeger):
    return int(floatDeger)




# doc = db.collection("Users").document("yQZwNV5L042W1VGPwiRB").collection("tahliller").document("16.10.2020\\r10:51:00").collection("sonuclar").stream()

# eslesmeYok = True  # yapılan sorgudan firebaseden gelen eşleşme yoksa değer 1 olarak korunur #böylece veri gelmediğini anlamış oluruz
# #print(doc.to_dict())
# for i in doc:

#     # eğer sorgudan değer gelirse for döngüsünün içerisine girilir ve değer 0 olur
#     eslesmeYok = False

#     takip_userID = i.id
#     print(takip_userID)

#     name = i.to_dict()
#     print(name)

# zaman = "16.10.2020\r10:51:00"
# zaman = zaman.replace("\r","-")


# zaman = zaman.split("-")
# tarih = zaman[0]
# saat = zaman[1]


# Kullanıcı Kayıt Formu
class RegisterForm(Form):
    name = StringField("İsim", validators=[validators.Length(min=3, max=50), validators.DataRequired("İsim Alanı Boş Bırakılamaz!")])
    surname =  StringField("Soyisim", validators=[validators.Length(min=2, max=50), validators.DataRequired("Soyisim Alanı Boş Bırakılamaz!")])
    tel = StringField("Telefon:", validators=[validators.Length(min=-1, max=11, message="Telefon formatına uygun şekilde numaranızı giriniz!"), validators.DataRequired("Telefon Alanı Boş Bırakılamaz!")])
    email = StringField("Email Adresi:", validators=[validators.Email(message="Lütfen Geçerli Bir Email Adresi Giriniz.")])
    tcNo = StringField("Tc No:", validators=[validators.Length(min=11, max=11), validators.DataRequired("Tc No Alanı Boş Bırakılamaz!")])
    password = PasswordField("Şifre:", validators=[
        validators.DataRequired("Lütfen Bir Şifre Belirleyin!"),
        validators.EqualTo(fieldname="confirmPass",
                           message="Girmiş Olduğunuz Şifreler Uyuşmuyor!")
    ])
    confirmPass = PasswordField("Şifre Tekrar:")


# Giriş Formu
class LoginForm(Form):
    email = StringField("E-posta Adresi:", validators=[validators.Email(message= "Lütfen Geçerli Bir Email Adresi Giriniz."), validators.DataRequired("E-posta Alanı Boş Bırakılamaz!")])
    password = PasswordField("Parola:")

# Yakın Grubu Formları


class JoinGroup(Form):
    
    yakin_email = StringField("Yakın Email Adresi:", validators=[validators.Email(message="Lütfen Geçerli Bir Email Adresi Giriniz.")])
    yakinlik = SelectField(u'Yakınlık Durumu:', choices=[(
        'aile', 'Aile'), ('akraba', 'Akraba'), ('arkadas', 'Arkadaş')])


# Database ile Bağlantı Kurma
app = Flask(__name__)

app.secret_key = "seracker"  # flush mesajları yayınlayabilmemiz için secret key tanımlamamız gerekiyor

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "seracker"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

# logged_in = False


@app.route("/deneme")
def deneme():

    return render_template("deneme2.html",imgGetir = functions.imgGetir)



@app.route("/about")
def about():

    takip_istekleri = takipIstekleri(session["userID"])


    if (request.method == "POST"):

    
        islem = str(request.form["submit_button"])

        tahlil = request.form.get("tahlil")
        adim = request.form.get("adim")
        nabiz = request.form.get("nabiz")


        takipci_yakinlik = request.form.get("takipci_yakinlik")
        bildirimIslemleri(islem,takipci_yakinlik,tahlil,adim,nabiz)

        return redirect(url_for("about"))

  

    return render_template("about.html", imgGetir = functions.imgGetir, takip_istekleri = takip_istekleri, userInfo = userInfo, uzunlukDon= uzunlukDon)


@app.route("/")
def index():

    return redirect(url_for("login"))


@app.route("/homepage",methods = ["GET", "POST"])
def homepage():

    
    if(session["logged_in"] ):

        takip_istekleri = takipIstekleri(session["userID"])

        nabizGunluk_veriler = nabizGun_veriAra(session["userID"])
        adimGunluk_veriler = adimGun_veriAra(session["userID"])

        if(request.method == "POST"):

            il_plaka = {"adana": "01", "adıyaman": "02","aksaray":"68","ardahan":"75",
                "afyon": "03", "ağrı": "04","amasya":"05","ankara":"06","antalya":"07",
                "artvin": "08", "aydın": "09","balıkesir":"10","bartın":"74","batman":"72",
                "bayburt": "69", "bilecik": "11","bingöl":"12","bitlis":"13","bolu":"14",
                "burdur": "15", "bursa": "16","çanakkale":"17","çankırı":"18","çorum":"19",
                "denizli": "20", "diyarbakır": "21","düzce":"81","edirne":"22","elazığ":"23",
                "erzincan": "24", "erzurum": "25","eskişehir":"26","gaziantep":"27","giresun":"28",
                "gümüşhane": "29", "hakkari": "30","hatay":"31","ığdır":"76","ısparta":"32",
                "mersin": "33", "istanbul": "34","izmir":"35","karabük":"78","karaman":"70",
                "kars": "36", "kastamonu": "37","kayseri":"38","kırıkkale":"71","kırklareli":"39",
                "kırşehir": "40", "kilis": "79","kocaeli":"41","konya":"42","kütahya":"43",
                "malatya": "44", "manisa": "45","kahramanmaraş":"46","mardin":"47","muğla":"48",
                "muş": "49", "nevşehir": "50","niğde":"51","ordu":"52","osmaniye":"80","rize":"53",
                "sakarya": "54", "samsun": "55","siirt":"56","sinop":"57","sivas":"58","şırnak":"73",
                "tekirdağ": "59", "tokat": "60","trabzon":"61","tunceli":"62","şanlıurfa":"63",
                "uşak": "64", "van": "65","yalova":"77","yozgat":"66","zonguldak":"67"}

            if(request.form["submit_button"] == "showHospital"):

                key_list = list(il_plaka.keys())
                val_list = list(il_plaka.values())

                print(request.form.get("ilHospital"),"sadasdasdasd")

                if(int(request.form.get("ilHospital")) < 10):
                    position = val_list.index("0"+request.form.get("ilHospital"))
                else:
                    position = val_list.index(request.form.get("ilHospital"))

                il = key_list[position]
                ilce = request.form.get("ilceHospital")
              
              
                address = '{}, {}'.format(ilce,il)
                url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) +'?format=json'

                response = requests.get(url).json()
                print(response[0]["lat"])
                print(response[0]["lon"])



                # if(ilce == "Merkez"):
                #     ilce = ""

                # print(ilce+"dsadasdas")

                # geolocator = Nominatim(user_agent="my_user_agent")
                # city = "{} {}".format(ilce, il)
                # country = "Tr"
                # loc = geolocator.geocode(city+',' + country)
                # print("latitude is :-" , loc.latitude, "\nlongtitude is:-" , loc.longitude)

                # return redirect(url_for("maps",konummm = [loc.latitude,loc.longitude])) ## otomatik url oluşturma muhabbeti
                return render_template("index.html", imgGetir =functions.imgGetir, mekanDon = mekanDon, konum = [response[0]["lat"], response[0]["lon"]],mekan = "hospital",takip_istekleri = takip_istekleri , userInfo = userInfo, uzunlukDon= uzunlukDon,yasHesapla = yasHesapla, kitleEndeksi_hesapla= kitleEndeksi_hesapla, nabizGunluk_veriler = nabizGunluk_veriler , nabizAyrintilari = nabizAyrintilari, adimGunluk_veriler=adimGunluk_veriler,adimAyrintilari = adimAyrintilari,intDon=intDon )

            elif(request.form["submit_button"] == "showPharmacy"):

                key_list = list(il_plaka.keys())
                val_list = list(il_plaka.values())

                print(request.form.get("ilPharmacy"),"sadasdasdasd")

                if(int(request.form.get("ilPharmacy")) < 10):
                    position = val_list.index("0"+request.form.get("ilPharmacy"))
                else:
                    position = val_list.index(request.form.get("ilPharmacy"))

                il = key_list[position]
                ilce = request.form.get("ilcePharmacy")
              
              
                address = '{}, {}'.format(ilce,il)
                url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) +'?format=json'

                response = requests.get(url).json()
                print(response[0]["lat"])
                print(response[0]["lon"])

                # if(ilce == "Merkez"):
                #     ilce = ""

                # print(ilce+"dsadasdas")

                # geolocator = Nominatim(user_agent="my_user_agent")
                # city = "{} {}".format(ilce, il)
                # country = "Tr"
                # loc = geolocator.geocode(city+',' + country)
                # print("latitude is :-" , loc.latitude, "\nlongtitude is:-" , loc.longitude)

                # return redirect(url_for("maps",konummm = [loc.latitude,loc.longitude])) ## otomatik url oluşturma muhabbeti
                return render_template("index.html", imgGetir =functions.imgGetir, mekanDon = mekanDon, konum = [response[0]["lat"], response[0]["lon"]],mekan = "pharmacy",takip_istekleri = takip_istekleri , userInfo = userInfo, uzunlukDon= uzunlukDon,yasHesapla = yasHesapla, kitleEndeksi_hesapla= kitleEndeksi_hesapla, nabizGunluk_veriler = nabizGunluk_veriler , nabizAyrintilari = nabizAyrintilari, adimGunluk_veriler=adimGunluk_veriler,adimAyrintilari = adimAyrintilari,intDon=intDon)


            else:  # 0_{{i.id}}request.form["submit_button"]

                islem = str(request.form["submit_button"])

                tahlil = request.form.get("tahlil")
                adim = request.form.get("adim")
                nabiz = request.form.get("nabiz")


                takipci_yakinlik = request.form.get("takipci_yakinlik")
                bildirimIslemleri(islem,takipci_yakinlik,tahlil,adim,nabiz)

                return redirect(url_for("homepage"))

        return render_template("index.html", imgGetir=functions.imgGetir, takip_istekleri = takip_istekleri, userInfo = userInfo, konum=0, uzunlukDon= uzunlukDon, yasHesapla = yasHesapla, kitleEndeksi_hesapla= kitleEndeksi_hesapla, nabizGunluk_veriler = nabizGunluk_veriler , nabizAyrintilari = nabizAyrintilari, adimGunluk_veriler=adimGunluk_veriler,adimAyrintilari = adimAyrintilari,intDon=intDon)


    #return render_template("index.html", imgGetir=functions.imgGetir)


@app.route("/personal", methods= ["GET", "POST"])
def personal():

    # Burada kullanıcının databasade takipciler bölümünde, durumu 0 olan yani yeni istekleri ham şekilde userIDye göre listeye atar
    takip_istekleri = takipIstekleri(session["userID"])
    print(takip_istekleri)

    # for i in takip_istekleri:

    #     print(i.to_dict())

    if (request.method == "POST"):


        if(request.form["submit_button"] == "Uyelik"):

            print(request.form["submit_button"])
            print(type(str(request.form["submit_button"])))

            name = request.form.get("name")
            surname = request.form.get("surname")
            tel = int(request.form.get("tel"))
            email = request.form.get("email")
            tcNo = int(request.form.get("tcNo"))

            tahlil = request.form.get("tahlil")
            # adim = request.form.get("adim")
            nabiz = request.form.get("nabiz")
            print("tahlil"+str(tahlil))
            # print("adim"+str(adim))
            print("nabiz"+str(nabiz))

            db = firestore.client()  # Firebase erişimi
            doc = db.collection("Users").document(session["userID"])

            yeniKayit_sozluk = {"name": name, "surname": surname,"tel":tel,"email":email,"tcNo":tcNo,"password":session["password"]}
            doc.set(yeniKayit_sozluk)

            session["telNo"] = tel
            session["name"] = name
            session["surname"] = surname
            session["email"] = email
            session["tcNo"] = tcNo

            # flash("Başarıyla Kayıt Olundu","success")

            return redirect(url_for("personal"))

        elif(request.form["submit_button"] == "Kisisel"):

            cinsiyet = request.form.get("cinsiyet")
            boy = request.form.get("boy")
            kilo = request.form.get("kilo")
            dogumTarihi = request.form.get("dogumTarihi")
            kanGrubu = request.form.get("kanGrubu")

            db = firestore.client()
            doc = db.collection("Users").document(session["userID"]).collection("info").document("kisiselBilgiler")
            kisiselKayit = {"kanGrubu": kanGrubu,"boy":boy,"kilo":kilo}
            doc.set(kisiselKayit)


            age = yasHesapla(dogumTarihi)
            doc = db.collection("Users").document(session["userID"])
            userAna_kayit = {"cinsiyet": cinsiyet,"dogumTarihi":dogumTarihi,"age":age}
            doc.set(userAna_kayit,merge = True)

            

            session["cinsiyet"] = cinsiyet
            session["boy"] = boy
            session["kilo"] = kilo
            session["dogumTarihi"] = dogumTarihi
            session["kanGrubu"] = kanGrubu

            return redirect(url_for("personal"))

        else:  # 0_{{i.id}}request.form["submit_button"]

            islem = str(request.form["submit_button"])

            tahlil = request.form.get("tahlil")
            adim = request.form.get("adim")
            nabiz = request.form.get("nabiz")


            takipci_yakinlik = request.form.get("takipci_yakinlik")
            bildirimIslemleri(islem,takipci_yakinlik,tahlil,adim,nabiz)

            return redirect(url_for("personal"))

    else:

        return render_template("personal_info.html", imgGetir =functions.imgGetir, takip_istekleri = takip_istekleri, userInfo = userInfo, uzunlukDon= uzunlukDon)

# Haritalar Deneme

@app.route("/maps", methods = ["GET", "POST"])
def maps():#konum=516516161516

    takip_istekleri = takipIstekleri(session["userID"])

    if(request.method == "POST"):

        if(request.form["submit_button"] == "showMap"):

            # print(konum)

            il_plaka = {"adana": "01", "adıyaman": "02","aksaray":"68","ardahan":"75",
            "afyon": "03", "ağrı": "04","amasya":"05","ankara":"06","antalya":"07",
            "artvin": "08", "aydın": "09","balıkesir":"10","bartın":"74","batman":"72",
            "bayburt": "69", "bilecik": "11","bingöl":"12","bitlis":"13","bolu":"14",
            "burdur": "15", "bursa": "16","çanakkale":"17","çankırı":"18","çorum":"19",
            "denizli": "20", "diyarbakır": "21","düzce":"81","edirne":"22","elazığ":"23",
            "erzincan": "24", "erzurum": "25","eskişehir":"26","gaziantep":"27","giresun":"28",
            "gümüşhane": "29", "hakkari": "30","hatay":"31","ığdır":"76","ısparta":"32",
            "mersin": "33", "istanbul": "34","izmir":"35","karabük":"78","karaman":"70",
            "kars": "36", "kastamonu": "37","kayseri":"38","kırıkkale":"71","kırklareli":"39",
            "kırşehir": "40", "kilis": "79","kocaeli":"41","konya":"42","kütahya":"43",
            "malatya": "44", "manisa": "45","kahramanmaraş":"46","mardin":"47","muğla":"48",
            "muş": "49", "nevşehir": "50","niğde":"51","ordu":"52","osmaniye":"80","rize":"53",
            "sakarya": "54", "samsun": "55","siirt":"56","sinop":"57","sivas":"58","şırnak":"73",
            "tekirdağ": "59", "tokat": "60","trabzon":"61","tunceli":"62","şanlıurfa":"63",
            "uşak": "64", "van": "65","yalova":"77","yozgat":"66","zonguldak":"67"}

            key_list = list(il_plaka.keys())
            val_list = list(il_plaka.values())

            if(int(request.form.get("il")) < 10):
                position = val_list.index("0"+request.form.get("il"))
            else:
                position = val_list.index(request.form.get("il"))

            il = key_list[position]
            ilce = request.form.get("ilce")
            # if(ilce == "Merkez"):
            #     ilce = ""



            address = '{}, {}'.format(ilce,il)
            url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) +'?format=json'

            response = requests.get(url).json()
            print(response[0]["lat"])
            print(response[0]["lon"])

            # geolocator = Nominatim(user_agent="my_user_agent")
            # city = "{} {}".format(ilce, il)
            # country = "Tr"
            # loc = geolocator.geocode(city+',' + country)
            # print("latitude is :-" , loc.latitude, "\nlongtitude is:-" , loc.longitude)

            # return redirect(url_for("maps",konummm = [loc.latitude,loc.longitude])) ## otomatik url oluşturma muhabbeti
            return render_template("maps.html", imgGetir =functions.imgGetir, mekanDon = mekanDon, konum = [response[0]["lat"], response[0]["lon"]], takip_istekleri = takip_istekleri , userInfo = userInfo, uzunlukDon= uzunlukDon )

        else:
            islem = str(request.form["submit_button"])

            tahlil = request.form.get("tahlil")
            adim = request.form.get("adim")
            nabiz = request.form.get("nabiz")


            takipci_yakinlik = request.form.get("takipci_yakinlik")
            bildirimIslemleri(islem,takipci_yakinlik,tahlil,adim,nabiz)

            return redirect(url_for("maps"))

    return render_template("maps.html", imgGetir =functions.imgGetir, mekanDon = mekanDon, konum = 0, takip_istekleri = takip_istekleri , userInfo = userInfo, uzunlukDon= uzunlukDon)

# Kayıt Ol


@app.route("/kayitol", methods = ["GET", "POST"])
def register():

    form = RegisterForm(request.form)
    
   

    if(request.method == "POST" and form.validate()):

        name = form.name.data
        surname = form.surname.data
        tel = int(form.tel.data)
        email = form.email.data
        tcNo = int(form.tcNo.data)
        # password = sha256_crypt.encrypt(form.password.data) #Kripto ile şifrelenmemiş parola
        password = form.password.data

        db = firestore.client()  # Firebase erişimi
        # Otomatik şekilde idnin oluşturulması
        doc = db.collection("Users").document()

        userID = doc.id

        

        yeniKayit_sozluk = {"userID":userID,"name": name, "surname": surname,"tel":tel,"email":email,"tcNo":tcNo,"password":password}
        doc.set(yeniKayit_sozluk)

        flash("Başarıyla Kayıt Olundu", "success")

        return redirect(url_for("login"))

    else:
        return render_template("register.html", imgGetir =functions.imgGetir, form= form)


# Login İşlemi
@app.route("/girisyap", methods= ["GET", "POST"])
def login():

    form = LoginForm(request.form)

    if(request.method == "POST" and form.validate()):

        email = form.email.data
        passwordEntered = form.password.data

        db = firestore.client()
        doc = db.collection("Users").where("email", "==", email).stream()

        eslesmeYok = True  # yapılan sorgudan firebaseden gelen eşleşme yoksa değer 1 olarak korunur #böylece veri gelmediğini anlamış oluruz
        for i in doc:

            # eğer sorgudan değer gelirse for döngüsünün içerisine girilir ve değer 0 olur
            eslesmeYok = False

            userID = i.id

            # print("i.")
            name = i.to_dict()["name"]
            surname = i.to_dict()["surname"]
            realPassword = i.to_dict()["password"]

            email = i.to_dict()["email"]
            tcNo = i.to_dict()["tcNo"]
            telNo = i.to_dict()["tel"]

            # print(name)
           # print(realPassword)

            # print(i.id,i.to_dict()["tcNo"])

            # alinan = i.to_dict()["tcNo"]

            # if(alinan == ""):
            #     print("tamamdir")

        if(not eslesmeYok):

            if(passwordEntered == realPassword):

                flash("Başarıyla Giriş Yaptınız!", "success")

                session["logged_in"] = True  # Giriş yapıldı
                
                global logged_in  # Burada giriş yapmadan önce ve yaptıktan sonra ana dizinde farklı şablonarın gelebilmesi için logged_in'İN globaline ulaşıyorum
                logged_in = True

                session["userID"] = userID
                session["telNo"] = telNo
                session["name"] = name
                session["surname"] = surname
                session["email"] = email
                session["tcNo"] = tcNo

                session["password"] = realPassword


                result = db.collection("Users").document(userID).collection("info").document("kisiselBilgiler").get()

                if (result.exists):

                    
                    session["boy"] = result.to_dict()["boy"]
                    session["kilo"] = result.to_dict()["kilo"]
                    session["kanGrubu"] = result.to_dict()["kanGrubu"]

                    db = firestore.client()
                    result2 = db.collection("Users").document(userID).get()

                    session["dogumTarihi"] = result2.to_dict()["dogumTarihi"]
                    session["cinsiyet"] = result2.to_dict()["cinsiyet"]


                else:

                    session["cinsiyet"] = -1
                    session["boy"] = -1
                    session["kilo"] = -1
                    session["dogumTarihi"] = -1
                    session["kanGrubu"] = -1


                takip_istekleri = takipIstekleri(session["userID"])

                # return render_template("deneme.html", imgGetir = functions.imgGetir, form = form , takip_istekleri = takip_istekleri , userInfo = userInfo)
                return redirect(url_for("homepage"))

            else:  # Parola yanlış girilmişse

                flash("Parolanızı Yanlış Girdiniz!", "danger")
                return redirect(url_for("login"))

        else:
            flash(
                "Sistemde Girilen Kimlik Numarasıyla Eşleşen Kullanıcı Bulunmamaktadır!", "danger")

            return redirect(url_for("login"))

    form = LoginForm(request.form)

    return render_template("login.html", imgGetir = functions.imgGetir, form = form)


#Şifre Değiştirme
@app.route("/sifredegistir",methods = ["POST","GET"])
def changePass():

    if(request.method == "POST"):

        if(request.form["submit_button"] == "sifreDegistir"):

            mevcutSifre = str(request.form.get("oldPass"))
           
            yeniSifre = str(request.form.get("newPass"))
            yeniSifre_tekrar = str(request.form.get("newPass_again"))


            if(mevcutSifre ==  session["password"]):

                if(yeniSifre == yeniSifre_tekrar):

                    db = firestore.client()  # Firebase erişimi
                    
                    doc = db.collection("Users").document(session["userID"])


                    yeniKayit_sozluk = {"userID":session["userID"],"name": session["name"], "surname": session["surname"],"tel":session["telNo"],"email":session["email"],"tcNo":session["tcNo"],"password":yeniSifre}
                    doc.set(yeniKayit_sozluk)

                    flash("Şifre Başarıyla Değiştirildi.", "success")

                    return redirect(url_for("changePass"))

                else:

                    flash("Girilen Şifreler Birbiriyle Uyuşmuyor!", "danger")

                    return redirect(url_for("changePass"))


            else:
                 
                flash("Mevcut Şifreyi Yanlış Girdiniz", "danger")

                return redirect(url_for("changePass"))

        else:
            islem = str(request.form["submit_button"])

            tahlil = request.form.get("tahlil")
            adim = request.form.get("adim")
            nabiz = request.form.get("nabiz")


            takipci_yakinlik = request.form.get("takipci_yakinlik")
            bildirimIslemleri(islem,takipci_yakinlik,tahlil,adim,nabiz)

            return redirect(url_for("changePass"))

    return render_template("changePassword.html",imgGetir = functions.imgGetir, uzunlukDon= uzunlukDon)


# Logout İşlemi
@app.route("/cikisyap")
def logout():
    session.clear()
    global logged_in
    logged_in = False
    return redirect(url_for("index"))


# Yakinlarim Sayfasi
@app.route("/yakinlarim", methods=["GET", "POST"])
def relatives():

    takip_istekleri = takipIstekleri(session["userID"])
    onaylanan_takipler = onaylananTakipler(session["userID"])

    joinForm = JoinGroup(request.form)

    if(request.method == "POST"):

        if(request.form["submit_button"] == "yakinIstegi_yolla"):

            takip_email = joinForm.yakin_email.data
            takip_yakinlik = joinForm.yakinlik.data
            # print(yakinlik)
            print(request.form.get("deneme"))

            db = firestore.client()
            doc = db.collection("Users").where("email", "==", takip_email).stream()

            eslesmeYok = True  # yapılan sorgudan firebaseden gelen eşleşme yoksa değer 1 olarak korunur #böylece veri gelmediğini anlamış oluruz
            for i in doc:

                # eğer sorgudan değer gelirse for döngüsünün içerisine girilir ve değer 0 olur
                eslesmeYok = False

                takip_userID = i.id

                name = i.to_dict()["name"]


            print(yakinlikDon(takip_yakinlik))

            if(not eslesmeYok):  # Takip isteği gönderilecek kullanıcı sistemde kayıtlı ise

                # takip isteği gönderen kullanıcının takipEdilenler listesine durumu onaylanmamış şeklinde kullanıcı eklenir
                doc = db.collection("Users").document(session["userID"]).collection(
                    "takipEdilenler").document(takip_userID)
                takipKayit = {"userID": takip_userID, "yakinlik": yakinlikDon(takip_yakinlik),"durum":0}
                doc.set(takipKayit)

                # takip isteği gönderilen kullanıcının takipciler listesine takip isteği gönderen kullanıcının bilgileri gönderilir
                doc = db.collection("Users").document(takip_userID).collection(
                    "takipciler").document(session["userID"])
                takipciKayit = {"userID": session["userID"], "durum": 0,"tahlil":False,"nabiz":False,"adim":False,"yakinlik":-1}
                doc.set(takipciKayit)

                flash("{} Email Adresli Kullanıcıya Takip İsteği Gönderildi!".format(
                    takip_email), "success")
                return redirect(url_for("relatives"))

            else:  # Takip isteği gönderilen kullancı sistemde kayıtlı değil ise

                flash(
                    "Sistemde Girmiş Olduğunuz Email Adresi ile Eşleşen Kullanıcı Bulunmamaktadır!", "danger")
                return redirect(url_for("relatives"))

        else:
            islem = str(request.form["submit_button"])

            tahlil = request.form.get("tahlil")
            adim = request.form.get("adim")
            nabiz = request.form.get("nabiz")


            takipci_yakinlik = request.form.get("takipci_yakinlik")
            bildirimIslemleri(islem,takipci_yakinlik,tahlil,adim,nabiz)

            return redirect(url_for("relatives"))

    return render_template("relatives.html", imgGetir = functions.imgGetir, joinForm=joinForm , takip_istekleri = takip_istekleri , userInfo = userInfo, onaylanan_takipler= onaylanan_takipler, userID = session["userID"], izinleriDon = izinleriDon, kayitliTahliller = kayitliTahliller, tahlilAyrintilari = tahlilAyrintilari, uzunlukDon= uzunlukDon,nabizGun_veriAra= nabizGun_veriAra, nabizVerileri=nabizVerileri,adimGun_veriAra = adimGun_veriAra, adimAyrintilari = adimAyrintilari)


@app.route("/tahlil", methods= ["GET", "POST"])
def tahlil():

    takip_istekleri = takipIstekleri(session["userID"])

    kayitli_tahliller = kayitliTahliller(session["userID"])

    if (request.method == "POST"):

        if(request.form["submit_button"] == "tahlilYukle"):
            file = request.files["file"]
            file.save(os.path.join("uploads", file.filename))

            for i in glob.glob("uploads\\*.pdf"):

                db = firestore.client()  # Firebase erişimi

                tahlilOkuma(i,session["userID"])
                
                os.remove(i)

            return render_template("veriler/tahliller.html", imgGetir = functions.imgGetir, takip_istekleri = takip_istekleri, userInfo = userInfo, uzunlukDon= uzunlukDon)

        else:
            islem = str(request.form["submit_button"])

            tahlil = request.form.get("tahlil")
            adim = request.form.get("adim")
            nabiz = request.form.get("nabiz")


            takipci_yakinlik = request.form.get("takipci_yakinlik")
            bildirimIslemleri(islem,takipci_yakinlik,tahlil,adim,nabiz)

            return redirect(url_for("tahlil"))

    tahliller = tahlilAra(session["userID"])

    return render_template("veriler/tahliller.html", imgGetir = functions.imgGetir, takip_istekleri = takip_istekleri, userInfo = userInfo, kayitli_tahliller = kayitli_tahliller, tahlilAyrintilari = tahlilAyrintilari, uzunlukDon= uzunlukDon)


@app.route("/adimbilgisi")
def stepInfo():

    takip_istekleri = takipIstekleri(session["userID"])

    adimGunluk_veriler = adimGun_veriAra(session["userID"])

    if (request.method == "POST"):

    
        islem = str(request.form["submit_button"])

        tahlil = request.form.get("tahlil")
        adim = request.form.get("adim")
        nabiz = request.form.get("nabiz")


        takipci_yakinlik = request.form.get("takipci_yakinlik")
        bildirimIslemleri(islem,takipci_yakinlik,tahlil,adim,nabiz)

        return redirect(url_for("stepInfo"))

  

    return render_template("veriler/stepInfo.html", imgGetir = functions.imgGetir, takip_istekleri = takip_istekleri, userInfo = userInfo, uzunlukDon= uzunlukDon,adimAyrintilari = adimAyrintilari,adimGunluk_veriler = adimGunluk_veriler)


@app.route("/nabizbilgisi")
def nabizInfo():

    takip_istekleri = takipIstekleri(session["userID"])

    nabizGunluk_veriler = nabizGun_veriAra(session["userID"])

    if (request.method == "POST"):

    
        islem = str(request.form["submit_button"])

        tahlil = request.form.get("tahlil")
        adim = request.form.get("adim")
        nabiz = request.form.get("nabiz")


        takipci_yakinlik = request.form.get("takipci_yakinlik")
        bildirimIslemleri(islem,takipci_yakinlik,tahlil,adim,nabiz)

        return redirect(url_for("nabizInfo"))

  

    return render_template("veriler/nabizInfo.html", imgGetir = functions.imgGetir, takip_istekleri = takip_istekleri, userInfo = userInfo, uzunlukDon= uzunlukDon,nabizGunluk_veriler=nabizGunluk_veriler, nabizVerileri=nabizVerileri,intDon=intDon)







@app.route("/modals")
def modals():
    return render_template("modals.html", imgGetir = functions.imgGetir, takipIstekleri =  takipIstekleri, userInfo = functions.userInfo, uzunlukDon= uzunlukDon)


if __name__ == "__main__":

    
    
    app.run(debug=True)
