# IPP Project

Interpreter in python for IPPcode23 (assembler-like) language.

## Usage

Use `parse.php` to transform input code into XML. <br>
```
php parse.php [--help]
```
Then run `interpret.py` to run the code.
```
interpret.py [--help] [--source=SOURCE] [--input=INPUT]
```
SOURCE and INPUT are files. If source or input flag is missing, read from stdin. At least one is necessary.

## Evaluation

### PHP script

- Lexikální analýza (detekce chyb): 82 %
- Syntaktická analýza (detekce chyb): 91 %
- Zpracování instrukcí (včetně chyb): 100 %
- Zpracování netriviálních programů: 92 %
- Rozšíření STATP 0 %
  
Celkem bez rozšíření: 94 %

### Interpret

- Lexikální analýza (detekce chyb): 100%
- Syntaktická analýza (detekce chyb): 73%
- Sémantická analýza (detekce chyb): 100%
- Běhové chyby (detekce): 100%
- Interpretace instrukcí: 95%
- Interpretace netriviálních programů: 85%
- Volby příkazové řádky: 82%
- Rozšíření FLOAT 0%
- Rozšíření STACK 0%
- Rozšíření STATI 0%
 
Celkem bez rozšíření: 93%