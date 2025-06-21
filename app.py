from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)
ARCHIVO_CSV = "uploads/entrada.csv"

# variables temporales en memoria (solo mientras corre la app)
tabla_omp = None
tabla_cuda = None
cantidad_omp = None
cantidad_cuda = None
@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route('/mergesort', methods=['GET', 'POST'])
def mergesort():
    global tabla_omp, tabla_cuda , cantidad_omp, cantidad_cuda

    if request.method == 'POST':
        archivo = request.files['archivo']
        if archivo:
            archivo.save(ARCHIVO_CSV)  # guarda el CSV original

        if os.path.exists(ARCHIVO_CSV):
            df = pd.read_csv(ARCHIVO_CSV)
            accion = request.form['accion']

            if accion == 'omp':
                tabla_omp = df.head(4).to_html(classes='tabla', index=False)
                cantidad_omp = len(df)
            elif accion == 'cuda':
                tabla_cuda = df.head(4).to_html(classes='tabla', index=False)
                cantidad_cuda = len(df)
    return render_template('mergesort.html', tabla_omp=tabla_omp,cantidad_omp=cantidad_omp, tabla_cuda=tabla_cuda,cantidad_cuda=cantidad_cuda)

@app.route('/radixsort', methods=['GET', 'POST'])
def radixsort():
    global tabla_omp, tabla_cuda, cantidad_omp, cantidad_cuda

    if request.method == 'POST':
        archivo = request.files['archivo']
        if archivo:
            archivo.save(ARCHIVO_CSV)

        if os.path.exists(ARCHIVO_CSV):
            df = pd.read_csv(ARCHIVO_CSV)
            accion = request.form['accion']

            if accion == 'omp':
                tabla_omp = df.head(4).to_html(classes='tabla', index=False)
                cantidad_omp = f"{len(df):,}".replace(",", ".")

            elif accion == 'cuda':
                tabla_cuda = df.head(4).to_html(classes='tabla', index=False)
                cantidad_cuda = f"{len(df):,}".replace(",", ".")

    return render_template('radixsort.html',
                           tabla_omp=tabla_omp, cantidad_omp=cantidad_omp,
                           tabla_cuda=tabla_cuda, cantidad_cuda=cantidad_cuda)


if __name__ == '__main__':
    app.run(debug=True)



