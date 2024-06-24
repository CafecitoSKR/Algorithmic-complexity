from flask import Flask, render_template, send_from_directory, jsonify, request, url_for
import pandas as pd
import os
from collections import defaultdict

app = Flask(__name__)

# Leer el archivo CSV con información de películas
ruta_archivo = "C:/Users/LCDP/Desktop/CICLO-2024-01/Algorithmic-complexity/data/10movies.csv"
data = pd.read_csv(ruta_archivo)

user_preferences = defaultdict(int)

def dfs(data, start_movie, visited=None):
    if visited is None:
        visited = set()
    
    visited.add(start_movie)
    yield start_movie
    
    for vecino in data:
        if vecino not in visited:
            yield from dfs(data, vecino, visited)

# Definir una función de heurística para estimar la popularidad de una película en relación con otra
def heuristica_popularidad(pelicula_referencia, pelicula_actual):
    return abs(pelicula_referencia['Popularity'] - pelicula_actual['Popularity'])

# Implementar el algoritmo de búsqueda A*
def buscar_películas_populares(pelicula_referencia, data, k=5):
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
    peliculas = [{
        "Name": pelicula['Name'],
        "Popularity": pelicula['Popularity'],
        "Vote_average": pelicula['Vote_average'],  # Asegúrate de incluir estas columnas
        "Original_name": pelicula['Original_name'],
        "Genre": pelicula['Genre']
    } for pelicula in resultados]

    top_movies = data.sort_values(by='Popularity', ascending=False).head(10).to_dict(orient='records')
    # Renderizar el template con los resultados
    return render_template('page/index.html', peliculas=top_movies, enumerate = enumerate)

@app.route('/filter_movies', methods=['POST'])
def filter_movies():

    global user_preferences

    genre = request.json['genre']

    if genre:
        user_preferences[genre] += 1
        # Filtrar películas por el género seleccionado
        # filtered_movies = data[data['Genre'] == genre].to_dict(orient='records')
        filtered_movies = data[data['Genre'] == genre].sort_values(by='Popularity', ascending=False).to_dict(orient='records')
    else:
        # Si no se selecciona ningún género, devolver todas las películas
        filtered_movies = data.sort_values(by='Popularity', ascending=False).to_dict(orient='records')

    return jsonify(filtered_movies)

@app.route('/dfs_movies')
def dfs_movies():
    start_movie = data.iloc[0]  # Ejemplo: seleccionar la primera película como inicio
    resultados = list(dfs(data, start_movie))
    
    # Preparar los datos para pasar al template
    peliculas = [{
        "Name": pelicula['Name'],
        "Popularity": pelicula['Popularity'],
        "Vote_average": pelicula['Vote_average'],
        "Original_name": pelicula['Original_name'],
        "Genre": pelicula['Genre']
    } for pelicula in resultados]
    
    return render_template('page/dfs_movies.html', peliculas=peliculas)


@app.route('/recommendations')
def recommendations():
    global user_preferences

    # Obtener los géneros más frecuentes elegidos por el usuario
    top_genres = sorted(user_preferences.items(), key=lambda x: x[1], reverse=True)[:3]  # Obtener los 3 géneros más frecuentes

    # Filtrar películas que pertenecen a los géneros más frecuentes
    recommended_movies = data[data['Genre'].isin([genre for genre, count in top_genres])].head(10).to_dict(orient='records')

    return render_template('page/recommendations.html', peliculas=recommended_movies, enumerate = enumerate)

if __name__ == '__main__':
    app.run(debug=True)
