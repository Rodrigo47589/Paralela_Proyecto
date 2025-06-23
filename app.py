from flask import Flask, render_template, request, send_file
import pandas as pd
import os
import subprocess

app = Flask(__name__)
ARCHIVO_ENTRADA = "usuarios.csv"
ARCHIVO_SALIDA = "usuarios_ordenados.csv"

# Variables temporales
tabla_omp = None
tabla_cuda = None
cantidad_omp = None
cantidad_cuda = None
tiempo_omp = None

@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route('/mergesort', methods=['GET', 'POST'])
def mergesort():
    global tabla_omp, tabla_cuda, cantidad_omp, cantidad_cuda, tiempo_omp


    if request.method == 'POST':
        archivo = request.files['archivo']
        if archivo:
            archivo.save(ARCHIVO_ENTRADA)

        if os.path.exists(ARCHIVO_ENTRADA):
            accion = request.form['accion']

            if accion == 'omp':
                try:
                    # Ejecuta el programa con los 2 parámetros: entrada y salida
                    result = subprocess.run(
                        ["MergeSort_OpenMP.exe", ARCHIVO_ENTRADA, ARCHIVO_SALIDA],
                        check=True,
                        cwd=os.getcwd(),
                        capture_output=True,
                        text=True
                    )
                    lineas = result.stdout.splitlines()
                    tiempo_omp = next((l.strip() for l in lineas if "milisegundos" in l), None)
                except subprocess.CalledProcessError as e:
                    return f"<h2>Error al ejecutar MergeSort_OpenMP.exe:</h2><pre>{e}</pre><pre>{e.stdout}\n{e.stderr}</pre>"

                if os.path.exists(ARCHIVO_SALIDA):
                    df_ordenado = pd.read_csv(ARCHIVO_SALIDA)
                    tabla_omp = df_ordenado.head(4).to_html(classes='tabla', index=False)
                    cantidad_omp = len(df_ordenado)
                else:
                    return "<h3>Error: No se generó el archivo usuarios_ordenados.csv</h3>"

            elif accion == 'cuda':
                df = pd.read_csv(ARCHIVO_ENTRADA)
                tabla_cuda = df.head(4).to_html(classes='tabla', index=False)
                cantidad_cuda = len(df)

    return render_template(
        'mergesort.html',
        tabla_omp=tabla_omp,
        cantidad_omp=cantidad_omp,
        tiempo_omp=tiempo_omp,
        tabla_cuda=tabla_cuda,
        cantidad_cuda=cantidad_cuda
    )

@app.route('/radixsort', methods=['GET', 'POST'])
def radixsort():
    global tabla_omp, tabla_cuda, cantidad_omp, cantidad_cuda, tiempo_omp

    if request.method == 'POST':
        archivo = request.files['archivo']
        if archivo:
            archivo.save(ARCHIVO_ENTRADA)

        if os.path.exists(ARCHIVO_ENTRADA):
            accion = request.form['accion']

            if accion == 'omp':
                try:
                    result = subprocess.run(
                        ["RadixSort_OpenMP.exe", ARCHIVO_ENTRADA, ARCHIVO_SALIDA],
                        check=True,
                        cwd=os.getcwd(),
                        capture_output=True,
                        text=True
                    )
                    # Extraer tiempo
                    lineas = result.stdout.splitlines()
                    tiempo_omp = next((l.strip() for l in lineas if "milisegundos" in l), None)

                except subprocess.CalledProcessError as e:
                    return f"<h2>Error al ejecutar RadixSort_OpenMP.exe:</h2><pre>{e}</pre><pre>{e.stdout}\n{e.stderr}</pre>"

                if os.path.exists(ARCHIVO_SALIDA):
                    df_ordenado = pd.read_csv(ARCHIVO_SALIDA)
                    tabla_omp = df_ordenado.head(4).to_html(classes='tabla', index=False)
                    cantidad_omp = len(df_ordenado)
                else:
                    return "<h3>Error: No se generó el archivo usuarios_ordenados.csv</h3>"

            elif accion == 'cuda':
                df = pd.read_csv(ARCHIVO_ENTRADA)
                tabla_cuda = df.head(4).to_html(classes='tabla', index=False)
                cantidad_cuda = len(df)

    return render_template(
        'radixsort.html',
        tabla_omp=tabla_omp,
        cantidad_omp=cantidad_omp,
        tiempo_omp=tiempo_omp,
        tabla_cuda=tabla_cuda,
        cantidad_cuda=cantidad_cuda
    )
@app.route('/descargar_openmp')
def descargar_openmp():
    return send_file(ARCHIVO_SALIDA, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)




