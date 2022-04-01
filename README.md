# Tamo-API
Tamo.lt scraper that acts as an unofficial API  
## Perspėjimai
Norint naudoti API reikia duoti script/server savo prisijungimo duomenis, o tai įprastai yra bloga idėja, tai prašau įsitikinti, kad šis API nieko blogo nedarys.  
Tamo priverčia po tam tikro laiko tarpo atsijungti, šis API to neatpažins, todėl reikės pasinaudot smegenim ir kas 30-60 min susikurti naują login session.  
Šis API nėra oficialus, jei tamo.lt nuspręstų pakeisti savo puslapį, tai šis API nustotų veikti iki kol aš jį atnaujinčiau, todėl šis API neturėtų būti naudojamas labai rimtuose projektuose.  
Šis API pagrinde daro tą patį, ką darytų žmogus naršyklėje tik greičiau ir efektyviau. Jeigu Tamo atpažintų, kad tai nėra naršyklė, o web scraper, tai kaltininko paskyra galėtų sulaukti **ban**. Testuojant šį API savo paskyroje, ban negavau, tai bent kol kas nemanau, kad Tamo tai tikrina, tačiau tas galėtų pasikeisti bet kurią akimirką. Kad būtų mažesnė tikimybė gauti ban tarp requests reiktų padaryti kelių sekundžių pauzę.
## Kaip naudotis?
Kaip API naudojimosi pavyzdį galima paskaityti `server.py`  
Susiinstaliuoti [beautifulsoup4](https://pypi.org/project/beautifulsoup4/) ir, priklausomai nuo pasirinktos versijos, arba [requests](https://pypi.org/project/requests/), arba [aiohttp](https://pypi.org/project/aiohttp/).  
`main.py` turėtu būti importuojamas norint naudoti šį API python script.  
`server.py` turėtu būti naudojamas norint turėti serveri (turbut `http://127.0.0.1:5000/`), kuriuo galima naudotis ir su kitomis programavimo kalbomis. Reikia turėti [flask](https://pypi.org/project/Flask/).  
`scraper.py` neturėtu būti importuojamas, tai duobė į kurią aš sumečiau visą script logiką. Vietoj `scraper.py` reiktų naudoti `main.py`, nes `main.py` yra wrapper aplink `scraper.py`.  
`async` folder yra `main.py` ir `scraper.py` asinchroninės versijos, kurios veikia beveik visiškai taip pat.   
Kaip naudotis `main.py` galima sužinoti atsidarius `main.py`, o `server.py` atsidarius serverio link (turbut `http://127.0.0.1:5000/`). `main.py`, kaip ir `server.py`, grąžina dict ir list populiuotus primityviais tipais, visos funkcijos (jų priimami ir grąžinami parametrai) yra tokios pačios.  
## Ką galima su šitu API padaryti?
Šis API atlieka funkcijas, kurias gali atlikti bet kuris mokinys (neturiu nei premium mokinio, nei mokytojo paskyros, tai nežinau kaip tai veiktų).  
Šis API negali padaryti 100% to ką gali padaryti tamo.lt svetainė, tačiau gali padaryti pakankamai, kad būtų naudingas tikrinant pažymius/vidurkius/pastabas/pranešimus ir pan.  
Šis API gali nuscrapinti šiuos tamo.lt puslapius:
* Tvarkaraštis (tvarkarastis)
* Dienynas (dienynas)
* Pamokos (pamokos)
* Namų darbai (namu_darbai)
* Atsiskaitomieji darbai (atsiskaitomieji_darbai)
* Pagyrimai/ Pastabos (pastabos)
* Trimestrai / Pusmečiai (pusmeciai)  

Šis API taip pat gali perskaityti gautus pranešimus (pranesimai, pranesimas, file_url).
