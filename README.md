# Universidad del Valle de Guatemala

## Facultad de Ingeniería

### Teoría de la Computación

#### Laboratorio 7: Simplificación de gramáticas libres de contexto

**Juan Francisco Orozco Mijangos (24647)**

## Descripción

En este laboratorio se implementó un programa que lee gramáticas libres de contexto desde archivos de texto, valida la sintaxis de cada producción y elimina las producciones épsilon. El programa muestra el procedimiento utilizado para encontrar símbolos anulables y generar las producciones equivalentes mediante las combinaciones posibles. Además, se desarrollan por separado los ejercicios de simplificación de gramáticas y conversión a Forma Normal de Chomsky.

## Organización del repositorio

- `main`: contiene la información general del laboratorio.
- `problema-1`: contiene el programa y los dos archivos de gramáticas.
- `problema-2`: rama reservada para el PDF con el desarrollo de los ejercicios teóricos.

## Problema 1

El programa acepta `->` o `→` como flecha, letras mayúsculas como no terminales, letras minúsculas o dígitos como terminales y `ε` para la cadena vacía. Cada alternativa se separa con `|`.

### Ejecución

```bash
python3 main.py gramaticas/gramatica1.txt gramaticas/gramatica2.txt
```

Si una línea no tiene el formato correcto, el programa muestra el archivo y el número de línea del error y se detiene antes de simplificar las gramáticas.
