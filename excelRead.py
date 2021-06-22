import xlrd

path = "denemeExcel.xlsx"

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


cred = credentials.Certificate("seracker-cd8df-firebase-adminsdk-c5wua-8f94ae24d2.json")
firebase_admin.initialize_app(cred)

dosyaAc = xlrd.open_workbook(path)
dataSheet =dosyaAc.sheet_by_index(0)





db = firestore.client() 
doc = db.collection("Users").document("yQZwNV5L042W1VGPwiRB").collection("nabiz").document("2021-05-17")



satirSayisi = dataSheet.nrows
print(satirSayisi) 

nabizVerileri = list()

for i in range(1,10300):



    nabizVeri = str(dataSheet.cell_value(i,0))
    nabizVeri = nabizVeri[10:]

    if(nabizVeri[10] == "M"): #iki haneli saat
       
        if(nabizVeri[9] == "A"):
            saat = nabizVeri[0:8]
        elif(nabizVeri[9] == "P"):
            ham = int(nabizVeri[0:2])
            if(ham < 12):
                ham +=12
            elif(ham == 12):
                ham ="00"
            saat =str(ham) + nabizVeri[2:8]

        nabizData = nabizVeri[12:]

        nabizVerileri.append(int(nabizData))

    else:#tek haneli saat
        if(nabizVeri[8] == "A"):
            saat = "0"+nabizVeri[0:7]
        elif(nabizVeri[8] == "P"):
            ham = int(nabizVeri[0:1])
            ham +=12

            saat =str(ham) + nabizVeri[1:7]

        nabizData = nabizVeri[11:]

        nabizVerileri.append(int(nabizData))

#saat iki haneli oluyor   11:16:49 PM,53     9:35:16 PM,59
#am pm kontrol el
#nabız 2 ve 3 haneli oluyor  10:11:09 PM,55



nabiz = {"nabizDatas":nabizVerileri}
doc.set(nabiz,merge=True)


for j in range(0,10000):

    pass
    #print(nabizVerileri[j][10:])






















# import xlrd

# path = "denemeExcel.xlsx"

# import firebase_admin
# from firebase_admin import credentials
# from firebase_admin import firestore


# cred = credentials.Certificate("seracker-cd8df-firebase-adminsdk-c5wua-8f94ae24d2.json")
# firebase_admin.initialize_app(cred)

# dosyaAc = xlrd.open_workbook(path)
# dataSheet =dosyaAc.sheet_by_index(0)





# db = firestore.client() 
# doc = db.collection("Users").document("yQZwNV5L042W1VGPwiRB").collection("nabiz").document("2021-05-21")



# satirSayisi = dataSheet.nrows
# print(satirSayisi) 

# nabizVerileri = list()

# for i in range(40180,66615):



#     nabizVeri = str(dataSheet.cell_value(i,0))
#     nabizVeri = nabizVeri[10:]

#     if(nabizVeri[10] == "M"): #iki haneli saat
       
#         if(nabizVeri[9] == "A"):
#             saat = nabizVeri[0:8]
#         elif(nabizVeri[9] == "P"):
#             ham = int(nabizVeri[0:2])
#             if(ham < 12):
#                 ham +=12
#             elif(ham == 12):
#                 ham ="00"
#             saat =str(ham) + nabizVeri[2:8]

#         nabizData = nabizVeri[12:]

#         nabizVerileri.append(nabizData+" "+"saat: "+saat)

#     else:#tek haneli saat
#         if(nabizVeri[8] == "A"):
#             saat = "0"+nabizVeri[0:7]
#         elif(nabizVeri[8] == "P"):
#             ham = int(nabizVeri[0:1])
#             ham +=12

#             saat =str(ham) + nabizVeri[1:7]

#         nabizData = nabizVeri[11:]

#         nabizVerileri.append(nabizData+" "+"saat: "+saat)

# #saat iki haneli oluyor   11:16:49 PM,53     9:35:16 PM,59
# #am pm kontrol el
# #nabız 2 ve 3 haneli oluyor  10:11:09 PM,55



# nabiz = {"nabiz":nabizVerileri}
# doc.set(nabiz)


# for j in range(0,10000):

#     pass
#     #print(nabizVerileri[j][10:])

