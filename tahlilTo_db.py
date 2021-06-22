import tabula

import mysql.connector

'''import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

#Ana dizindeki firebase anahtar ile firebase bağlantısı kurulması
cred = credentials.Certificate("fir-python-52324-firebase-adminsdk-ox1mz-f2f13b9080.json")
firebase_admin.initialize_app(cred)
'''

#db = firestore.client()


def tahlil2_db(tcNo,tarih,tahlil,sonuc,birim,referans):

    cnx = mysql.connector.connect(user='root',password='',host='127.0.0.1',database='seracker')
    cursor = cnx.cursor()

    sql= ("insert into tahlil_verileri(tcNo,tarih,tahlil,sonuc,birim,referans) values(%s,%s,%s,%s,%s,%s)")

    
    val=(tcNo,tarih,tahlil,sonuc,birim,referans)

    cursor.execute(sql,val)

    cnx.commit()

    cursor.close()
    cnx.close()

tarih = ""
def tahlil(tahlilYol,db,userID):

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


        firstTime = False


        if(len(ayri)==6 and ayri[0] != "["):

            
            if(firstTime):
                firstTime = False
                
                global tarih
                
                tarih = ayri[1][0:10]


            sozluk.update({str(ayri[2]) : {"tarih": ayri[1],"sonuç": ayri[3],"birim":ayri[4],"referans":ayri[5]}} )
            #sozluk.update({"{}".format(ayri[2]) : [ayri[3],ayri[4],ayri[5]]} )


    
    doc = db.collection("Users").document(userID).collection("tahliller").document(tarih)#Otomatik şekilde idnin oluşturulması
    doc.set({"tarih":tarih})

    for i,j in sozluk.items():
        doc = db.collection("Users").document(userID).collection("tahliller").document(tarih).collection("sonuclar").document(i)
       
        #doc = doc.collection("sonuclar").document(i)
       
        doc.set({"sonuc":j.get("sonuç"),"birim":j.get("birim"),"referans":j.get("referans")})


   



#tahlil("tahlil.pdf","2P7LNiGjlFaDdDnPnpjG")



































# datas = string.split("  ")

# sayı=0
# for i in datas: 
#     if(i.strip()==""):
#         datas.pop(sayı)
#     else:
#         sayı+=1
    


# for i in datas:
#     print("----------\n")
#     print(i)





