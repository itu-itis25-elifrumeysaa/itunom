import random """bir ihanın verilerini takip edemiyoruz şu an o 
o yüzden random verileri takip ettirip değerlerini değişkenlere 
atayacağım
"""
import json
import threading
import numpy as np
import cv2
import socket
import time
telemetri_port = 14550
video_port = 14551
GCP = '127.0.0.1'
class IHASimulator():
    def __init__(self, ilk_irtifa=0.0):
        #konum verileri
        #alan kısıtlı muhtemelen o yüzden x y z kullanıyorum, enlem boylam değil
        self.konum_x= 0.0
        self.konum_y = 0.0
        self.konum_z = ilk_irtifa
        #hız verileri
        self.yatay_hız= 0.0
        self.dikey_hız= 0.0
        #batarya durumu
        self.batarya_yüzdesi=100
        self.kalan_sure= 1900 #sn
        #uçuş modu
        self.ucus_modu= "GUIDED"
        #çevresel veriler
        self.ortam_sıcaklıgı= 22.3
        self.nem = 42.1 #%
        self.ruzgar_hızı= 2.9 #m/s
        self.running = True
    def guncel_veri(self):
        self.konum_x += random.uniform(-5,5) #m
        #random.uniform sayesinde belirttiğimiz aralıkta rastgele sayı ürettirdik
        self.konum_y += random.uniform(-5, 5)
        self.konum_z += max(0, random.uniform(-1.5, 1.5))
        """iha olsaydı sensörlerden aldığımız verileri değişkenlere
        atıyor olacaktık"""
        self.yatay_hız+= random.uniform(-10,10) #m/s
        self.dikey_hız+= random.uniform(-10,10)
        self.batarya_yüzdesi-= max(0, random.uniform(-1.5,1.5)) #%
        self.kalan_sure-= max(0, random.uniform(-10,10)) #sn
        modlar = ["GUIDED","AUTO","RTL","MANUAL"]
        self.ucus_modu= random.choice(modlar) #modlar arasında rastgele seçim
        self.ortam_sıcaklıgı += random.uniform(-2,2)
        self.nem += max(0, min(100, random.uniform(-3,3)))
        self.ruzgar_hızı += random.uniform(-5,5)
    def format_json (self):
        data = {
            "konum_x": round(self.konum_x,2),
            "konum_y": round(self.konum_y,2),
            "konum_z" : round(self.konum_z, 2),
            "yatay_hız" : round(self.yatay_hız,1),
            "dikey_hız" :round(self.dikey_hız),
            "batarya_yüzdesi": round(self.batarya_yüzdesi,2),
            "kalan_sure" : round(self.kalan_sure,2),
            "ucus_modu" : self.ucus_modu,
            "ortam_sıcaklıgı": round(self.ortam_sıcaklıgı,2),
            "nem":round(self.nem,2),
            "ruzgar_hızı":round(self.ruzgar_hızı,2),
        }
        json_string = json.dumps(data)
        return json_string
    def telemetri_producer(self, port=telemetri_port):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        hedef_adres = (GCP, port)
        while self.running and self.batarya_yüzdesi >0 :
            self.guncel_veri()
            json_mesajı= self.format_json()
            try:
                udp_socket.sendto(json_mesajı.encode('utf-8'), port)
            except:
                pass
            time.sleep(0.1)
            self.running =0
    def video_producer(self,port=video_port):
        udp_socket_v =socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        hedef_adres_v= (GCP,port)
        kamera = cv2.VideoCapture(0)
        if not kamera.isOpened():
            self.running = False
        while self.running:
            basarili,frame= kamera.read()
            if not basarili: break

