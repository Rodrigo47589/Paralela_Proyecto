from flask import Flask, render_template, request, send_file, session
import pandas as pd
import os
import subprocess

app = Flask(__name__)   #Se crea una instancia Flask 
app.secret_key = 'clave_secreta'  # Clave necesario para utilizar sesiones (session) 

ARCHIVO_ENTRADA = "usuarios.csv" #Nombre del archivo que carga en la pagina
ARCHIVO_SALIDA = "usuarios_ordenados.csv" #Nombre del archivo que se genera en la pagina 

@app.route('/') #Conecta una ruta web con una funcion de python. En este caso la funcion inicio()
def inicio():
    session.clear()  # Reinicia los datos al volver al inicio de la pagina para asi evitar que las tablas usadas estén presentes en otra ventana
    return render_template('inicio.html') #Renderiza y muestra la plantilla HTML de la página de inicio.


@app.route('/mergesort', methods=['GET', 'POST']) #Ruta que gestiona el ordenamiento con Mergesort con los metodos GET y POST 
def mergesort(): #Se define la funcion que manejará la logica de ordenamiento mergesort en OpenMP y CUDA
    if request.method == 'POST': #Verifica si el formulario fue enviado con el metodo POST. 
        archivo = request.files['archivo'] #Extrae el archivo cargado desde el input del formulario HTML ('archivo' es el nombre del input del formulario HTML)
        if archivo: #En caso que se reciba el archivo.
            archivo.save(ARCHIVO_ENTRADA) #El archivo se guarda como usuarios.csv

        if os.path.exists(ARCHIVO_ENTRADA): #Verifica si el archivo esta guardado en el pycharm
            accion = request.form['accion'] #Cuando presionan el boton. Se va obtener el valor de ese boton ya sea OpenMP o CUDA

            if accion == 'omp': #Si se presiono el boton "Ordenamiento con OpenMP"
                try: #Intentará ejecutar el archivo de c++ "MergeSort_OpenMP.cpp" en formato de .exe con sus parametros de el nombre archivo cargado y el nombre del archivo que se va generar 
                    result = subprocess.run(
                        ["MergeSort_OpenMP.exe", ARCHIVO_ENTRADA, ARCHIVO_SALIDA],
                        check=True,    #En caso que ocurra un error, saldra una excepción 
                        cwd=os.getcwd(), #La ruta de ejecucion es el pycharm 
                        capture_output=True, #Captura la salida estándar y de error
                        text=True       #interpreta la salida como texto 
                    )
                    for linea in result.stdout.splitlines(): #Recorre la salida linea por linea hasta que encuentre la palabra "milisegundos" para asi sacar el tiempo
                        if "milisegundos" in linea:
                            session['tiempo_omp'] = linea.strip() #En caso que exista la palabra, se guardara el tiempo en la sesion (session) para mostrarlo en la pagina HTML
                except subprocess.CalledProcessError as e: #La excepcion es que retornará un mensaje de error a la pagina 
                    return f"<h2>Error al ejecutar MergeSort_OpenMP.exe:</h2><pre>{e}</pre>"

                if os.path.exists(ARCHIVO_SALIDA): #Si el archivo existe en el directorio de pycharm. Se va leer el archivo.csv generado
                    df = pd.read_csv(ARCHIVO_SALIDA)
                    session['tabla_omp'] = df.head(4).to_html(classes='tabla', index=False) #la variable guarda las 4 primeras filas para realizar una vista previa
                    session['cantidad_omp'] = len(df) #Guarda la cantidad total de datos ordenados 

            elif accion == 'cuda': #En caso que presionen el "boton de ordenamiento con CUDA"
                try:
                    result = subprocess.run( #Lo mismo que el codigo para openMP en python, se va ejecutar el archivo.cu en formate de .exe con los parametros de nombre de archivo cargado y generado
                        ["MergeSortCuda5.exe", ARCHIVO_ENTRADA, ARCHIVO_SALIDA],
                        check=True,  #Se creara una excepcion si hay un error en la pagina 
                        cwd=os.getcwd(), #La ruta es en pycharm
                        capture_output=True,
                        text=True  #La salida se interpretara como texto
                    )
                    for linea in result.stdout.splitlines(): #Verificara si se encuentra la palabra "ms" en los datos de salida. "ms" significa milisegundos 
                        if "ms" in linea:
                            session['tiempo_cuda'] = linea.strip() #Se guarda el tiempo 
                except subprocess.CalledProcessError as e: #Si no ejecuta el subproceso "run". Retornará un mensaje de error
                    return f"<h2>Error al ejecutar MergeSort_OpenMP.exe:</h2><pre>{e}</pre>"

                if os.path.exists(ARCHIVO_SALIDA): #verifica si esxiste el archivo en el directorio
                    df = pd.read_csv(ARCHIVO_SALIDA) #Lee el archivo generado
                    session['tabla_cuda'] = df.head(4).to_html(classes='tabla', index=False) #guarda las 4 primeras filas
                    session['cantidad_cuda'] = len(df) #guarda la cantidad de datos ordenados

    #renderiza la plantilla mergesort.html y los datos 
    # Variables relacionadas con el resultado del algoritmo OpenMP: tabla_omp,cantidad_omp,tiempo_omp
    # Variables relacionadas con el resultado del algoritmo CUDA: tabla_cuda,cantidad_cuda,tiempo_cuda
    return render_template(
        'mergesort.html',
        tabla_omp=session.get('tabla_omp'),  
        cantidad_omp=session.get('cantidad_omp'),
        tiempo_omp=session.get('tiempo_omp'),
        tabla_cuda=session.get('tabla_cuda'), 
        cantidad_cuda=session.get('cantidad_cuda'),
        tiempo_cuda=session.get('tiempo_cuda')
    )


@app.route('/radixsort', methods=['GET', 'POST'])  #El procedimiento es el mismo que la funcion mergesort()
def radixsort():
    if request.method == 'POST':
        archivo = request.files['archivo']
        if archivo:
            archivo.save(ARCHIVO_ENTRADA)

        if os.path.exists(ARCHIVO_ENTRADA):
            accion = request.form['accion']

            if accion == 'omp': #Si el boton elegido es Ordenamiento con OpenMP
                try:  #Se ejecutara el Radixsort.exe.Se guardará el tiempo de ejecucion , las 4 primeras filas de la tabla del archivo generado por Radixsort_OpenMP.exe y la cantidad de datos ordenados
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

                if os.path.exists(ARCHIVO_SALIDA): #Verifica si el archivo se guardo correctamente en el pycharm. Es decir, en el directorio.
                    df = pd.read_csv(ARCHIVO_SALIDA)
                    session['tabla_omp'] = df.head(4).to_html(classes='tabla', index=False)
                    session['cantidad_omp'] = len(df)

            elif accion == 'cuda': #Caso contrario, se ejecutara el mismo procedimiento del algoritmo en OpenMP. Pero con el archivo.exe de CUDA
                try:
                    result = subprocess.run(
                        ["MergeSortCuda5.exe", ARCHIVO_ENTRADA, ARCHIVO_SALIDA],
                        check=True,
                        cwd=os.getcwd(),
                        capture_output=True,
                        text=True
                    )
                    for linea in result.stdout.splitlines():
                        if "ms" in linea:
                            session['tiempo_cuda'] = linea.strip()
                except subprocess.CalledProcessError as e:
                    return f"<h2>Error al ejecutar MergeSort_OpenMP.exe:</h2><pre>{e}</pre>"

                if os.path.exists(ARCHIVO_SALIDA):
                    df = pd.read_csv(ARCHIVO_SALIDA)
                    session['tabla_cuda'] = df.head(4).to_html(classes='tabla', index=False)
                    session['cantidad_cuda'] = len(df)

    #renderiza la plantilla mergesort.html y los datos 
    # Variables relacionadas con el resultado del algoritmo OpenMP: tabla_omp,cantidad_omp,tiempo_omp
    # Variables relacionadas con el resultado del algoritmo CUDA: tabla_cuda,cantidad_cuda,tiempo_cuda
    return render_template(
        'radixsort.html',
        tabla_omp=session.get('tabla_omp'),
        cantidad_omp=session.get('cantidad_omp'),
        tiempo_omp=session.get('tiempo_omp'),
        tabla_cuda=session.get('tabla_cuda'),
        cantidad_cuda=session.get('cantidad_cuda'),
        tiempo_cuda=session.get('tiempo_cuda')
    )


@app.route('/descargar_openmp')
def descargar_openmp():    #Funcion para descargar archivo ordenado con openMP 
    return send_file(ARCHIVO_SALIDA, as_attachment=True)

@app.route('/descargar_cuda')
def descargar_cuda():      #Funcion para descargar archivo ordenado con openMP 
    return send_file(ARCHIVO_SALIDA, as_attachment=True)


if __name__ == '__main__': #Inicia el servidor local flask
    app.run(debug=True)





