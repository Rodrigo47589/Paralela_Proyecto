from flask import Flask, render_template, request, send_file, session
import pandas as pd
import os
import subprocess

app = Flask(__name__)
app.secret_key = 'clave_secreta'  # Necesario para session

ARCHIVO_ENTRADA = "usuarios.csv"
ARCHIVO_SALIDA = "usuarios_ordenados.csv"

@app.route('/')
def inicio():
    session.clear()  # Reinicia sesión al volver al inicio
    return render_template('inicio.html')


@app.route('/mergesort', methods=['GET', 'POST'])
def mergesort():
    if request.method == 'POST':
        archivo = request.files['archivo']
        if archivo:
            archivo.save(ARCHIVO_ENTRADA)

        if os.path.exists(ARCHIVO_ENTRADA):
            accion = request.form['accion']

            if accion == 'omp':
                try:
                    result = subprocess.run(
                        ["MergeSort_OpenMP.exe", ARCHIVO_ENTRADA, ARCHIVO_SALIDA],
                        check=True,
                        cwd=os.getcwd(),
                        capture_output=True,
                        text=True
                    )
                    for linea in result.stdout.splitlines():
                        if "milisegundos" in linea:
                            session['tiempo_omp'] = linea.strip()
                except subprocess.CalledProcessError as e:
                    return f"<h2>Error al ejecutar MergeSort_OpenMP.exe:</h2><pre>{e}</pre>"

                if os.path.exists(ARCHIVO_SALIDA):
                    df = pd.read_csv(ARCHIVO_SALIDA)
                    session['tabla_omp'] = df.head(4).to_html(classes='tabla', index=False)
                    session['cantidad_omp'] = len(df)

            elif accion == 'cuda':
                df = pd.read_csv(ARCHIVO_ENTRADA)
                session['tabla_cuda'] = df.head(4).to_html(classes='tabla', index=False)
                session['cantidad_cuda'] = len(df)

    return render_template(
        'mergesort.html',
        tabla_omp=session.get('tabla_omp'),
        cantidad_omp=session.get('cantidad_omp'),
        tiempo_omp=session.get('tiempo_omp'),
        tabla_cuda=session.get('tabla_cuda'),
        cantidad_cuda=session.get('cantidad_cuda')
    )


@app.route('/radixsort', methods=['GET', 'POST'])
def radixsort():
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
                    for linea in result.stdout.splitlines():
                        if "milisegundos" in linea:
                            session['tiempo_omp'] = linea.strip()
                except subprocess.CalledProcessError as e:
                    return f"<h2>Error al ejecutar RadixSort_OpenMP.exe:</h2><pre>{e}</pre>"

                if os.path.exists(ARCHIVO_SALIDA):
                    df = pd.read_csv(ARCHIVO_SALIDA)
                    session['tabla_omp'] = df.head(4).to_html(classes='tabla', index=False)
                    session['cantidad_omp'] = len(df)

            elif accion == 'cuda':
                df = pd.read_csv(ARCHIVO_ENTRADA)
                session['tabla_cuda'] = df.head(4).to_html(classes='tabla', index=False)
                session['cantidad_cuda'] = len(df)

    return render_template(
        'radixsort.html',
        tabla_omp=session.get('tabla_omp'),
        cantidad_omp=session.get('cantidad_omp'),
        tiempo_omp=session.get('tiempo_omp'),
        tabla_cuda=session.get('tabla_cuda'),
        cantidad_cuda=session.get('cantidad_cuda')
    )


@app.route('/descargar_openmp')
def descargar_openmp():
    return send_file(ARCHIVO_SALIDA, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)






