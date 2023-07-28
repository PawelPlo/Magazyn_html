from flask import Flask, render_template, request
import os

app = Flask(__name__)
pliki_w_folderze = os.listdir()

saldo=0

if "konto.txt" in pliki_w_folderze:
    with open("konto.txt", "r") as plik:
        for linia in plik:
            konto = float(linia)

else:
    konto = float(0)

konto = float(konto)

if "zadluzenie.txt" in pliki_w_folderze:
    with open("zadluzenie.txt", "r") as plik:
        for linia in plik:
            zadluzenie = float(linia)
else:
    zadluzenie = float(0)

zadluzenie = float(zadluzenie)

"""zmienne i funkcje do stanu magazynu"""

stan_magazynu = dict()

with open("stan_magazynu.txt", "r") as plik:
    for linia in plik:
        linia = linia.split()
        produkt, ilosc, cena, wartosc = linia
        produkt = str(produkt)
        produkt = produkt.replace("_"," ")
        stan_magazynu[produkt] = {}
        ilosc = float(ilosc)
        cena = float(cena)
        wartosc = float(wartosc)
        stan_magazynu[produkt] = {"ilosc": ilosc, "cena": cena, "wartosc": wartosc}
stan_magazynu = stan_magazynu

def zapasy(stan_magazynu):
    suma = 0
    for v in stan_magazynu.values():
        suma += v["wartosc"]
    return suma

wartosc_zapasow = zapasy(stan_magazynu)


"""zmienne do historii zdarzen"""
historia = []

with open("historia.txt", "r") as plik:
    for linia in plik:
        linia = linia.strip('\n')
        historia.append(linia)

historia = historia

@app.route("/")
def home():
    context = {
        "konto": konto,
        "zadluzenie": zadluzenie,
        "wartosc_zapasow": wartosc_zapasow,
        "saldo": konto + wartosc_zapasow - zadluzenie
    }
    return render_template("Strona_glowna.html", context=context)

@app.route("/Finanse", methods=['POST', 'GET'])
def Finanse():
    # if request.method == 'POST':
    kwota_wplaty = request.form.get("kwota_wplaty", 0)
    kwota_wplaty = float(kwota_wplaty)
    #     konto += kwota_wplaty
    context = {
        "konto": konto,
        "zadluzenie": zadluzenie,
        "saldo": konto + wartosc_zapasow - zadluzenie,
            }
    return render_template("Finanse.html", context=context)

@app.route("/Magazyn")
def Magazyn():
    context = {
        "wartosc_zapasow": wartosc_zapasow,
    }
    return render_template("Magazyn.html", context=context)

@app.route("/Sprzedaz")
def Sprzedaz():
    context = {
        "konto": konto,
        "wartosc_zapasow": wartosc_zapasow
    }
    return render_template("Sprzedaz.html", context=context)

@app.route("/Zakup")
def Zakup():
    context = {
        "konto": konto,
        "wartosc_zapasow": wartosc_zapasow
    }
    return render_template("Zakup.html", context=context)

@app.route("/Historia")
def Historia():
    context = {
        "historia": historia,
           }
    return render_template("Historia.html", context=context)


# with open("stan_magazynu.txt", "w") as plik:
#     for k, v in stan_magazynu.items():
#         v = ilosc, cena, wartosc
#         ilosc = stan_magazynu[k]["ilosc"]
#         cena = stan_magazynu[k]["cena"]
#         wartosc = stan_magazynu[k]["wartosc"]
#         k = k.replace(" ","_")
#         plik.write(f"{k} {ilosc} {cena} {wartosc}\n")
#     with open("konto.txt", "w") as plik:
#         plik.write(f"{konto}")
#     with open("zadluzenie.txt", "w") as plik:
#         plik.write(f"{zadluzenie}")
#     with open("historia.txt", "w") as plik:
#         for linia in historia:
#             plik.write(f"{linia}")
#             plik.write(f"\n")