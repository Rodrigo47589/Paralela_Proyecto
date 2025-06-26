#  Proyecto de Ordenamiento Paralelo con Flask y OpenMP

##  Descripción general

Este proyecto compara el rendimiento entre algoritmos de ordenamiento paralelizado (MergeSort y RadixSort con OpenMP y CUDA) ejecutados desde una aplicación web en Flask. El objetivo es demostrar cómo la computación paralela puede mejorar (o no) el rendimiento según el tipo de algoritmo y el tamaño de los datos.

---

##  Instalación del entorno

###  1. Compilador C++ con soporte OpenMP

Para compilar correctamente los algoritmos en C++ con paralelización, se requiere MinGW con soporte OpenMP.

- Descargar desde:  
  👉 https://github.com/niXman/mingw-builds-binaries/releases

- Recomendaciones de configuración:
  - architecture: `x86_64`
  - threads: `posix`
  - exception: `seh`
  - versión GCC: `13.x` o superior

## Sin esto, los  archivos `.exe` no podrán usar múltiples hilos correctamente.

---

### 2. Entorno Python con Flask

1. Instalar Python 3.x
2. Instalar Flask:

   ```bash
   pip install flask

## 3.Estructura del proyecto en Flask
FlaskProject/
│
├── app.py                        # Backend principal
├── MergeSort_OpenMP.exe          # Algoritmo MergeSort con OpenMP
├── RadixSort_OpenMP.exe         # Algoritmo RadixSort con OpenMP
├── MergeSort_CUDA5.exe          # Algoritmo paralelo basado en OpenMP
│
├── static/                      # Archivos estáticos (CSS, imágenes)
│   ├── cayetano.jpg
│   ├── cayetano_escudo.jpg
│   └── style.css
│
├── templates/                   # Vistas HTML Frontend
│   ├── inicio.html
│   ├── mergesort.html
│   └── radixsort.html


## 4. Ejecución 
 Abrir y ejecutar App.py y entrar al http:localhost creado por Flask
 Subir un archivo csv 
 Elegir el algoritmo a ejecutar (MergeSort o RadixSort)
 Descargar el archivo ordenado (usuarios_ordenados.csv) y visualizar los tiempos.
 


