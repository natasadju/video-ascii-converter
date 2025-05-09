# Video v ASCII pretvornik

Aplikacija pretvori videoposnetek v tekstovno ASCII umetnost, s podporo za barvni ali sivinski izpis in sinhronizirano predvajanje zvoka.

## Funkcionalnosti
- Pretvorba videa v ASCII umetnost
- Možnost sivinskega ali barvnega načina
- Predvajanje zvoka vzporedno z videom
- Vmesnik preko ukazne vrstice

## 🛠️ Zagon
```bash
pip install -r requirements.txt
```

Primer zagona programa
```bash
python main.py path_do_videa.mp4 --sound --width 100
```

Ima različne nastavitve:
 -  --grayscale
 - --sound
 - --width
 - --mute
