from flask import Flask, render_template, send_from_directory, request, url_for
import pandas as pd
import os


app = Flask(__name__)

# Leer el archivo CSV con información de películas
ruta_archivo = "C:/Users/LCDP/Desktop/CICLO-2024-01/Algorithmic-complexity/data/10movies.csv"
data = pd.read_csv(ruta_archivo)

# Definir una función de heurística para estimar la popularidad de una película en relación con otra
def heuristica_popularidad(pelicula_referencia, pelicula_actual):
    return abs(pelicula_referencia['Popularity'] - pelicula_actual['Popularity'])

# Implementar el algoritmo de búsqueda A*
def buscar_películas_populares(pelicula_referencia, data, k=10):
    # Inicializar una lista de películas visitadas y una cola de prioridad para almacenar las películas a explorar
    visitados = set()
    cola_prioridad = []

    # Agregar la película de referencia a la cola de prioridad
    cola_prioridad.append((0, pelicula_referencia))

    # Realizar la búsqueda A*
    while cola_prioridad:
        # Extraer la película con la prioridad más alta de la cola de prioridad
        _, pelicula_actual = cola_prioridad.pop(0)
        
        # Convertir la serie de pandas a una tupla
        pelicula_actual_tupla = tuple(pelicula_actual)
        
        # Si la película actual no ha sido visitada, la marcamos como visitada y la agregamos a la lista de resultados
        if pelicula_actual_tupla not in visitados:
            visitados.add(pelicula_actual_tupla)
            yield pelicula_actual
            
            # Si hemos encontrado k películas populares, terminamos la búsqueda
            if len(visitados) == k:
                break
            
            # Explorar las películas vecinas (basadas en similitud de popularidad)
            for _, vecino in data.iterrows():
                if vecino['Id'] != pelicula_actual['Id']:
                    heuristica = heuristica_popularidad(pelicula_referencia, vecino)
                    cola_prioridad.append((heuristica, vecino))
            
            # Ordenar la cola de prioridad por la heurística
            cola_prioridad.sort(key=lambda x: x[0])

@app.route('/')
def index():
    # Obtener una película de referencia (por ejemplo, la más popular)
    pelicula_referencia = data.loc[data['Popularity'].idxmax()]

    # Buscar las 5 películas más populares en relación con la película de referencia
    resultados = list(buscar_películas_populares(pelicula_referencia, data))

    # Preparar los datos para pasar al template
    peliculas = [{"Name": pelicula['Name'], "Popularity": pelicula['Popularity']} for pelicula in resultados]

    # Renderizar el template con los resultados
    return render_template('page/index.html', peliculas=peliculas, enumerate = enumerate)

if __name__ == '__main__':
    app.run(debug=True)
