from flask import url_for

def imgGetir(imgName):
    return url_for("static",filename = "img/{}".format(imgName))


# import firebase_admin
# from firebase_admin import credentials
# from firebase_admin import firestore

# cred = credentials.Certificate("seracker-cd8df-firebase-adminsdk-c5wua-8f94ae24d2.json")

# firebase_admin.initialize_app(cred)

# def takipIstekleri(userID):

#     db= firestore.client()
#     doc = db.collection("Users").document(userID).collection("takipciler").where("durum","==",0).stream()

#     eslesmeYok = True 

#     takipciIstekler = list()
#     for i in doc:
            
#         eslesmeYok = False 
#         takipciIstekler.append(i)
        
        
#     if(not eslesmeYok):

#         return takipciIstekler

#     else:
#         return 0
        
    
# def userInfo(userID):

#     result =  db.collection("Users").document(userID).get()

#     return result

