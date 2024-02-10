# !pip install xboard>=1.0.2

from xboard import XBoard
import matplotlib.pyplot as plt
import numpy as np
import time


IP = "192.168.4.1"
myboard = XBoard(IP)

nom_user = "Sim"
temps_debut = []
temps_fin = []
Nombre_repetitions = 24 # 24 suspensions en tout
temps_on = 7 # 7s d'effort
temps_off = 3 # 3s de repos

myboard.programme("Force crit.", nom_user, True, True, 0, [1500], [75], 1)
time.sleep(1)

for i in range(5,0,-1): # compte a rebours du debut d'exercice
    myboard.programme("Poids ds {}s".format(i), nom_user, True, True, 0)
    time.sleep(1)

myboard.programme("Mesure poids", nom_user, True, False, 0, [750, 1000], [75, 100])
t1 = time.perf_counter() - myboard.time_init
time.sleep(3)
t2 = time.perf_counter() - myboard.time_init

poids = myboard.data[0][-1]
print("Poids mesuré: {}kg".format(poids))

for i in range(10,0,-1): # compte a rebours du debut d'exercice
    myboard.programme("Attention {}s".format(i), nom_user, True, True, 0)
    time.sleep(1)

# debut exercice
for repetition in range(Nombre_repetitions):
    temps_debut.append(time.perf_counter() - myboard.time_init)
    for t in range(int(temps_on)):
        if t==0:
            myboard.programme("Rep {} {}s".format(repetition+1, t), nom_user, True, False, 0, [750, 1000, 1500], [75, 100, 100])
        else:
            myboard.programme("Rep {} {}s".format(repetition+1, t), nom_user, True, False, 0, [0], [0])
        time.sleep(1)

    temps_fin.append(time.perf_counter() - myboard.time_init)
    for t in range(int(temps_off)):
        if t == temps_off//2:
            myboard.programme("Pause {}s".format(t), nom_user, False, True, 0, [0], [0], 1) # Calibration sur les pauses
        elif t == 0:
            myboard.programme("Pause {}s".format(t), nom_user, False, True, 0, [1500, 1000, 750], [75, 100, 100])
        else:
            myboard.programme("Pause {}s".format(t), nom_user, False, True, 0, [0], [0])
        time.sleep(1)

time.sleep(1)
myboard.programme("Fin exercice", nom_user, False, True, 0, [1500, 1000, 750, 1500, 1000, 750], [75, 100, 100, 75, 100, 100])
myboard.stop_reception()


####

# On redimensionne les tableau de données
len_temps = len(myboard.timestamp[0])
len_data = len(myboard.data[0])
len_plot = np.minimum(len_temps, len_data)
temps_debut_exo = temps_debut[0]
force = np.array(myboard.data[0][:len_plot])
temps = np.array(myboard.timestamp[0][:len_plot])

# On synchronise les données avec le début de l'exercice
indice_debut = np.argmin(abs(temps - temps_debut_exo))
force = force[indice_debut - 10:]
temps = temps[indice_debut - 10:]

force_max = np.max(force)


# on recherche le centre de chaque repetition
indice_centre = []
for i in range(len(temps_debut)):
    arg_debut = np.argmin(np.abs(temps - temps_debut[i]))
    arg_fin = np.argmin(np.abs(temps - temps_fin[i]))
    indice_centre.append((arg_debut + arg_fin)//2)

# on trouve la plage de données valide pour chaque répétitions
seuil = (force>5)
reps = np.zeros([len(temps_debut), len(seuil)])*False
indice_debut = []
indice_fin = []
for indice in enumerate(indice_centre):
    i = indice[1]
    while seuil[i] == True:
        i -= 1
    indice_debut.append(i) # debut de la plage de donnée

    i = indice[1]
    while seuil[i] == True:
        i += 1
    indice_fin.append(i) # fin de la plage de donnée

    reps[indice[0], indice_debut[-1]:indice_fin[-1]] = True


# Calcul de la force moyenne sur une répétition en ne tenant en compte que des 85% des valeurs les plus importantes
# Calcul de la force moyenne pour chaque répétitions
tri_force = np.sort(reps*force)[:,::-1] # valeurs de force triés par répétitions et par force decroissante
nombre_valeur = reps.sum(axis=1)
force_moyenne_85 = np.empty(len(reps))
for i in range(len(reps)):
    tri_force[i, int(.85*nombre_valeur[i]):] = 0 # on supprime les valeurs les plus faibles
    force_moyenne_85[i] = tri_force[i].sum()/int(.85*nombre_valeur[i]) # on fait la moyenne des valeurs restantes

force_moyenne = np.round((reps*force).sum(axis=1)/reps.sum(axis=1), 2)

# force maximum pour chaque répétition
force_max = (reps*force).max(axis = 1)
arg_force_max = np.argmax(reps*force, axis = 1)

plt.figure(figsize=(15,8))
plt.plot(temps[arg_force_max], force_max, "rx", linewidth=2, markersize=12)
for i in range(len(force_max)):
    plt.text(temps[arg_force_max[i]]+1, force_max[i]+1, np.round(force_max[i], 1), fontsize="x-large", color="red", weight="demibold")

plt.plot(temps, force)
for i in range(len(force_moyenne_85)):
    plt.plot([temps[indice_debut[i]], temps[indice_fin[i]]], [force_moyenne_85[i], force_moyenne_85[i]], "k")
for i in range(len(force_max)):
    plt.text(temps[indice_debut[i]], force_moyenne_85[i]-4, np.round(force_moyenne_85[i], 1), fontsize="x-large", weight="bold")
plt.plot([temps[indice_debut[0]], temps[-1]], [poids, poids], 'r')


plt.ylabel("Force [kg]")
plt.xlabel("Temps [s]")
plt.title("Exercice force critique, {}, reglette 22mm, force crit. {}kg, ratio force/poids:{}".format(nom_user, np.round(force_moyenne_85[-6:].mean(), 2), np.round(force_moyenne_85[-6:].mean()/poids,2)))
plt.ylim([-10, 1.2*np.max(force)])
plt.ylim([-10, np.maximum(np.quantile(force, .999)*1.5, poids*1.5)])
plt.grid()
plt.show()