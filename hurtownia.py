from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
db = SQLAlchemy()
pliki_w_folderze = os.listdir()

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db.init_app(app)

class Produkty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produkt = db.Column(db.String, nullable=False)
    ilosc = db.Column(db.Float)
    cena = db.Column(db.Float)
    wartosc = db.Column(db.Float)
    akcje = db.Column

    def __str__ (self):
        return f'{self.produkt} / {self.ilosc} / {self.cena} zł / {self.wartosc} zł'


saldo=0
def wczytanie_konta(pliki_w_folderze):
    if "konto.txt" in pliki_w_folderze:
        with open("konto.txt", "r") as plik:
            for linia in plik:
                konto = float(linia)
    else:
        konto = float(0)
    return konto

konto = float(wczytanie_konta(pliki_w_folderze))


def wczytanie_zadluzenia(pliki_w_folderze):
    if "zadluzenie.txt" in pliki_w_folderze:
        with open("zadluzenie.txt", "r") as plik:
            for linia in plik:
                zadluzenie = float(linia)
    else:
        zadluzenie = float(0)
    return zadluzenie

zadluzenie = float(wczytanie_zadluzenia(pliki_w_folderze))

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


with app.app_context():
    db.create_all()
    for produkt, v in stan_magazynu.items():
        v = stan_magazynu[produkt]["ilosc"], stan_magazynu[produkt]["cena"], stan_magazynu[produkt]["wartosc"]
        ilosc = stan_magazynu[produkt]["ilosc"]
        cena = stan_magazynu[produkt]["cena"]
        wartosc = stan_magazynu[produkt]["wartosc"]
        p = Produkty(produkt=produkt, ilosc=ilosc, cena=cena, wartosc=wartosc)
        db.session.add(p)
        db.session.commit()

"""zmienne do historii zdarzen"""

historia = []

with open("historia.txt", "r") as plik:
    for linia in plik:
        linia = linia.strip('\n')
        historia.append(linia)

historia = historia
def zapasy(stan_magazynu):
    suma = 0
    for v in stan_magazynu.values():
        suma += v["wartosc"]
    return suma

wartosc_zapasow = zapasy(stan_magazynu)


@app.route("/")
def home():
    konto = float(wczytanie_konta(pliki_w_folderze))
    zadluzenie = float(wczytanie_zadluzenia(pliki_w_folderze))
    context = {
        "konto": konto,
        "zadluzenie": zadluzenie,
        "wartosc_zapasow": wartosc_zapasow,
        "saldo": konto + wartosc_zapasow - zadluzenie
    }
    return render_template("Strona_glowna.html", context=context)

@app.route("/Finanse", methods=['POST', 'GET'])
def Finanse(konto=konto):
    konto = float(wczytanie_konta(pliki_w_folderze))
    zadluzenie = float(wczytanie_zadluzenia(pliki_w_folderze))
    if request.method == 'POST':
        kwota_wplaty = request.form.get("kwota_wplaty",0 )
        kwota_wplaty = float(kwota_wplaty)
        konto += kwota_wplaty
        historia.append(f"Wpłata na konto: {kwota_wplaty} zł")
    if request.method == 'POST':
        kwota_wyplaty = request.form.get("kwota_wyplaty",0 )
        kwota_wyplaty = float(kwota_wyplaty)
        konto -= kwota_wyplaty
        historia.append(f"Wypłata z konta: {kwota_wyplaty} zł")
    if request.method == 'POST':
        nowy_kredyt = request.form.get("nowy_kredyt", 0)
        nowy_kredyt = float(nowy_kredyt)
        konto += nowy_kredyt
        zadluzenie += nowy_kredyt
        historia.append(f"Zaciągnięty kredyt w kwocie: {nowy_kredyt} zł")
    if request.method == 'POST':
        splata_kredytu = request.form.get("splata_kredytu", 0)
        splata_kredytu = float(splata_kredytu)
        konto -= splata_kredytu
        zadluzenie -= splata_kredytu
        historia.append(f"Spłata kredytu w kwocie: {splata_kredytu} zł")
    with open("konto.txt", "w") as plik:
        plik.write(f"{konto}")
    with open("zadluzenie.txt", "w") as plik:
        plik.write(f"{zadluzenie}")
    with open("historia.txt", "w") as plik:
        for linia in historia:
            plik.write(f"{linia}")
            plik.write(f"\n")
    context = {
        "konto": konto,
        "zadluzenie": zadluzenie,
        "saldo": konto + wartosc_zapasow - zadluzenie
            }
    return render_template("Finanse.html", context=context)

@app.route("/Szukanie_produktu", methods=['POST', 'GET'])
def Szukanie_produktow():
    if request.method == 'POST':
        szukany_produkt = request.form.get("nazwa_produktu")
        if szukany_produkt:
            db.session.query(Produkty).filter(Produkty.username=="szukany_produkt").first()
            print(db.session.query(Produkty).filter(Produkty.username=="szukany_produkt").first())
        else:
            print("brak produktu")
    #return redirect(url_for('Magazyn'))



@app.route("/Usuwanie_produktow", methods=['POST', 'GET'])
def Usuwanie_produktow():
    product_id = request.form.get("product_id")
    if product_id:
        product=db.get_or_404(Produkty, int(product_id))
        db.session.delete(product)
        db.session.commit()
    return redirect(url_for('Magazyn'))

@app.route("/Dodawanie_produktow", methods=['POST', 'GET'])
def Dodawanie_produktow():
    if request.method == 'POST':
        produkt = request.form.get("nazwa_produktu")
        ilosc = request.form.get("ilosc_produktu")
        ilosc = float(ilosc)
        cena = request.form.get("cena_produktu")
        cena = float(cena)
        wartosc = ilosc * cena
        wartosc = float(wartosc)
        if produkt and ilosc and cena and wartosc:
            historia.append(f"Do magazynu dodano {produkt}, w ilości {ilosc}, w cenie {cena} zł o wartości {wartosc}")
            p = Produkty (produkt=produkt, ilosc=ilosc, cena=cena, wartosc=wartosc)
            stan_magazynu[produkt] = {"ilosc": ilosc, "cena": cena, "wartosc": wartosc}
            db.session.add(p)
            db.session.commit()
        with open("stan_magazynu.txt", "w") as plik:
            for k, v in stan_magazynu.items():
                v = ilosc, cena, wartosc
                ilosc = stan_magazynu[k]["ilosc"]
                cena = stan_magazynu[k]["cena"]
                wartosc = stan_magazynu[k]["wartosc"]
                k = k.replace(" ", "_")
                plik.write(f"{k} {ilosc} {cena} {wartosc}\n")
        with open("historia.txt", "w") as plik:
            for linia in historia:
                plik.write(f"{linia}")
                plik.write(f"\n")
        return redirect(url_for('Magazyn'))

    context = {
        "wartosc_zapasow": wartosc_zapasow,

    }
    return render_template("Dodawanie_produktow.html", context=context)

@app.route("/Magazyn")
def Magazyn():
    lista_produktow=db.session.query(Produkty).all()
    context = {
        "wartosc_zapasow": wartosc_zapasow,
        "lista_produktow": lista_produktow
    }
    return render_template("Magazyn.html", context=context)




# me = db.session.query(User).filter(User.username=="robergo").first()
# me.lastname = "Coś"
#
# db.session.add(me)
# db.session.commit()
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


with open("stan_magazynu.txt", "w") as plik:
    for k, v in stan_magazynu.items():
        v = ilosc, cena, wartosc
        ilosc = stan_magazynu[k]["ilosc"]
        cena = stan_magazynu[k]["cena"]
        wartosc = stan_magazynu[k]["wartosc"]
        k = k.replace(" ","_")
        plik.write(f"{k} {ilosc} {cena} {wartosc}\n")
with open("konto.txt", "w") as plik:
    plik.write(f"{konto}")
with open("zadluzenie.txt", "w") as plik:
    plik.write(f"{zadluzenie}")
with open("historia.txt", "w") as plik:
    for linia in historia:
        plik.write(f"{linia}")
        plik.write(f"\n")