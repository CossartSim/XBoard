import http.client
from sseclient import SSEClient
from threading import Thread, Event
import json
import time

class XBoard():
    def __init__(self):
        self.ip = '192.168.4.1'
        self.port = 80

        self.data = [[]]
        self.timestamp = [[]]
        self.event = Event()
        self.start_msg()
        self.time_init = time.perf_counter()


        self.data_thread = Thread(target=self.capture_data, args=(self.data, self.timestamp,))
        self.data_thread.start()

    def stop_reception(self):
        self.event.set()
        self.data_thread.join()

    def start_msg(self):
        """Envoi d'un message pour initier la connexion"""
        connection = http.client.HTTPConnection(self.ip, self.port)
        connection.request('GET', '/', headers={'Accept': 'text/html'})
        response = connection.getresponse()
        connection.close()

    def envoi_commande(self, cmd):
        connection = http.client.HTTPConnection(self.ip, self.port)
        connection.request('POST', '/exercice', cmd, headers={'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8'})
        response = connection.getresponse()
        connection.close()

    def endurance(self, force=0):
        """Exercice endurance, force a maintenir [kg]"""
        commande = {'id_ex': 'ex3', "inputValues":["{}".format(force)]}
        json_data = json.dumps(commande).encode()
        self.envoi_commande(json_data)

    def libre(self):
        """Exercice mesure de la force libre"""
        commande = {'id_ex': 'ex1', "inputValues":[]}
        json_data = json.dumps(commande).encode()
        self.envoi_commande(json_data)

    def concours(self):
        """Exercice concours"""
        commande = {'id_ex': 'ex5', "inputValues":[]}
        json_data = json.dumps(commande).encode()
        self.envoi_commande(json_data)

    def explosivite(self):
        """Exercice mesure de l'explosivite"""
        commande = {'id_ex': 'ex4', "inputValues":[]}
        json_data = json.dumps(commande).encode()
        self.envoi_commande(json_data)

    def programme(self, texte1 = "", texte2 = "", led_vert = True, led_rouge = True, prise = 0, hauteur_ref = [], duree_ref = [], calibration = 0):
        """Pilotage a distance de la poutre"""

        code_led = 0
        if(led_vert == False and led_rouge == False): code_led = 0
        if(led_vert == False and led_rouge == True): code_led = 1
        if(led_vert == True and led_rouge == False): code_led = 2
        if(led_vert == True and led_rouge == True): code_led = 3

        hauteur = [0 for _ in range(16)]
        duree = [0 for _ in range(16)]

        for i in range(len(hauteur_ref)):
            hauteur[i] = hauteur_ref[i]

        for i in range(len(duree_ref)):
            duree[i] = duree_ref[i]

        commande = {'id_ex': 'ex0', "inputValues":[texte1, texte2, code_led, prise, hauteur, duree,  calibration],}
        json_data = json.dumps(commande).encode()
        self.envoi_commande(json_data)

    def capture_data(self, loc_data, timestamp):
        messages = SSEClient('http://192.168.4.1/events')
        raw_prev = []
        for msg in messages:
            if msg.event == "data":
                raw = msg.data[1:-1].split(",")
                if (raw != raw_prev):
                    raw_prev = raw.copy()
                    longeur_msg = int(float(raw[0]))
                    time_loc = time.perf_counter() - self.time_init
                    for ite in range(longeur_msg):
                        loc_data[0].append(float(raw[ite+1]))
                        timestamp[0].append(round(time_loc + ite/80, 3))
                    # print(loc_data[0][-1])

            if self.event.is_set():
                print("Arret du thread")
                break
