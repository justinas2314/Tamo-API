# Tamo-API
Tamo.lt scraper that acts as an unofficial API
The Documentation is in Lithuanian as only people in Lithuania would find this useful.
## Kaip naudotis?
`main.py` turėtu būti importuojamas norint naudoti šį API python script.  
`server.py` turėtu būti naudojamas norint turėti serveri (turbut `http://127.0.0.1:5000/`), kuriuo galima naudotis ir su kitomis programavimo kalbomis.  
`host_server.py` turėtų būti naudojamas norint turėti serverį skirtą hostinti internete.  
`scraper.py` neturėtu būti importuojamas, tai duobė į kurią aš sumečiau visą script logiką. Vietoj `scraper.py` reiktų naudoti `main.py`, nes `main.py` yra wrapper aplink `scraper.py`.  
Kaip naudotis `main.py` galima sužinoti atsidarius `main.py`, o `server.py` atsidarius serverio link (turbut `http://127.0.0.1:5000/`). `main.py`, kaip ir `server.py`, grąžina dict ir list populiuotus primitiviais tipais, visos funkcijos (jų priimami ir grąžinami parametrai) yra tokios pačios.  
## Ką galima su šitu API padaryti?
Šis API atlieka funkcijas, kurias gali atlikti bet kuris mokinys (neturiu nei premium mokinio, nei mokytojo paskyros, tai nežinau kaip tai veikia).  
Šis API negali padaryti 100% to ką gali padaryti tamo.lt svetainė, tačiau gali padaryti pakankamai, kad būtų naudingas tikrinant pažymius/vidurkius/pastabas ir pan.  
Šis API gali nuscrapinti šiuos tamo.lt puslapius:
* tvarkarastis
* dienynas
* pamokos
* namu_darbai
* atsiskaitomieji_darbai
* pastabos
* pusmeciai
