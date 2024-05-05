import pandas as pd
from graphviz import Digraph

# Leer el archivo CSV con información de películas
ruta_archivo = "C:/Users/51924/Desktop/ComplejidadRepo/Algorithmic-complexity/data/10movies.csv"
data = pd.read_csv(ruta_archivo)

# Crear un nuevo grafo dirigido
graph = Digraph()

# Agregar nodos al grafo (películas)
for index, row in data.iterrows():
    # Utilizamos el Id como etiqueta del nodo y el nombre de la película como su nombre
    graph.node(str(row['Id']), row['Name'])

# Agregar aristas al grafo (basadas en relaciones de similitud de popularidad)
for index, row1 in data.iterrows():
    for index, row2 in data.iterrows():
        if row1['Id'] != row2['Id']:  # Utiliza el nombre correcto de la columna de identificación única
            # Calculamos la diferencia absoluta en popularidad entre las películas
            diferencia_popularidad = abs(row1['Popularity'] - row2['Popularity'])  # Utiliza el nombre correcto de la columna de popularidad
            # Si la diferencia es menor que un cierto umbral (por ejemplo, 100), conectamos las películas
            if diferencia_popularidad < 100:
                # Agregamos una arista entre las películas con un atributo de etiqueta que indica la similitud en popularidad
                graph.edge(str(row1['Id']), str(row2['Id']))



# Guardar el grafo en formato DOT
graph.render('grafo_peliculas_popularidad', format='png', view=True)