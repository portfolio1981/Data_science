# -*- coding: utf-8 -*-
"""Proyecto final data_science.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1tXRvJKWGO9C-JcQDjsT-k2rqGz_KdMi1

#Sistema de Recomendación de Películas de Amazon Prime

# Hipótesis de interés
  
*  ¿Qué es lo que se ve con mayor frecuencia en la plataforma series o películas?
*   ¿Cuáles son las mejores puntuadas según imbd?
*   ¿Para mejorar la experiencia de cada usuario podremos ofrecer una lista de las 10 mejores películas y/o series relacionadas con un titulo?

#Importamos Librerías
"""

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import missingno as msno

import scipy
import sklearn # Paquete base de ML

from scipy.stats import norm
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler, MaxAbsScaler, RobustScaler, StandardScaler

# %matplotlib inline

from google.colab import drive
drive.mount('/content/drive')
root_path= '/content/drive/MyDrive/Trabajo Final/titles.csv'

"""#Descarga de API's Públicas"""

import requests
import json

url = "https://moviesminidatabase.p.rapidapi.com/genres/"

headers = {
	"X-RapidAPI-Key": "e7e0cd03c5mshe81cc920304684bp1b2d41jsn457a1ad9fab1",
	"X-RapidAPI-Host": "moviesminidatabase.p.rapidapi.com"
}

response = requests.request("GET", url, headers=headers)

print(response.text)

texto = response.text
json.loads(texto)

jsondata=json.loads(texto)
df0=pd.DataFrame.from_dict(jsondata)
df0.head()

df0.shape

"""#Data Wrangling

#Cargamos la base de datos
"""

df = pd.read_csv("/content/drive/MyDrive/Trabajo Final/titles.csv")
df

"""# Cambio de nombres de Variables para un mejor entendimiento del dataset"""

df.columns

df2 = df.rename(columns={'title':'titulo', 'description':'descripcion', 'release_year':'año_lanzamiento', 'age_certification':'apto_edad', 'runtime':'duracion', 'genres':'genero', 'production_countries':'pais_produccion', 'seasons':'temporadas',  'imdb_score':'ranking_imdb', 'imdb_votes':'puntacion_imdb', 'type':'tv_o_pelicula'})
df2.columns

df2

df2.info()

print(df2.isnull().sum())

df2.isnull().sum().sum()

"""#Popularidad con respecto a la relacion tv o pelicula si es más popular las series o las peliculas utilizando un grafico de barras"""

sns.barplot(data=df2, x= 'tv_o_pelicula', y= 'tmdb_popularity')

"""En este gráfico se puede ver las diferencias de puntuaciones en IMDB (Internet Movie Database) entre series y películas, y que cual de las dos es más popular, en este caso se puede ver que las series denota una amplia popularidad de las series frente a las películas.


"""

plt.figure(figsize=(10,6))
sns.boxplot(x=df2.tv_o_pelicula, y= df2.año_lanzamiento, hue=df2.apto_edad,showfliers=False)
plt.title('Boxplot comparativo tv_o_Pelicula vs año_lanzamiento')
plt.xlabel('tv_o_Pelicula')
plt.ylabel('año_lanzamiento')

"""Se puede ver que, en este boxplot, hay una correlatividad que a partir de los primeros años de 1930 aproximadamente, cuando arranca el cine estos son populares hasta nuestros días, pero con la llegada de la televisión a las masas esta comienza a ganar terreno y con ellas las series de a poco. En la actualidad las series ganan terreno ya que son más visualizadas, además que hay gran variedad de géneros (las familiares, infantiles o de adultos) lo que demuestra el gráfico a través de los distintos colores de las cajas donde se muestra el sistema de clasificación de edades.

Chequeamos que no existan datos duplicados en nuestro dataframe
"""

df2.duplicated()

"""Chequeamos Datos faltantes"""

df2.info()

print(df2.isnull().sum())

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline
msno.matrix(df2.sample(250))

"""Notamos que en las features apto_edad y temporadas no hay sufientes datos como para valorarlas.

Dreamos un nuevo data frame eliminando los datos faltantes
"""

df3 = df2.dropna()
df3

"""Verificamos que el data frame nuevo no contiene datos faltantes"""

df3.info()

print(df3.isnull().sum())

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline
msno.matrix(df3.sample(250))

"""Teniendo en cuenta que el dataframe se reduce muchisimo de 9871 instancias a 581 creemos que aplicar este metodo es muy poco favorable. Intentaremos crear otro dataframe solamente eliminando las columnas.

Eliminando las columnas
"""

df4 = df2.dropna()
df4

df4.info()

print(df4.isnull().sum())

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline
msno.matrix(df4.sample(250))

"""Creemos que esta es una decisión más acertada que la anterior. Se evaluara más adelante cuando se plantee, el modelo a desarrollar si son pocas las features.

# Análisis exploratorio de datos
Correlación lineal de las variables involucradas

Realizamos una exploración grafica visual vinculando las variables, para detectar si entre ellas existe una correlación lineal para luego analizarlas
"""

sns.pairplot (df)

"""Según los gráficos de puntos no se aprecia una correlación lineal entre las variables aplicadas

Realizamos un nuevo dataset de correlacion utilizando el metodo spearman
"""

df2_corr = df2.corr("spearman", numeric_only=True)
df2_corr

sns.heatmap(df2_corr,
            xticklabels=df2.columns,
            yticklabels=df2.columns,
            cmap="bwr"
            )

"""En la grafica de calor se notan algunas correlaciones en las variables. Utilizaremos la matriz para ver mas en detalle"""

# Heatmap matriz de correlaciones
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(5, 5))

sns.heatmap(
    df2_corr,
    annot     = True,
    cbar      = False,
    annot_kws = {"size": 8},
    vmin      = -1,
    vmax      = 1,
    center    = 0,
    cmap      = sns.diverging_palette(20, 220, n=200),
    square    = True,
    ax        = ax
)

ax.set_xticklabels(
    ax.get_xticklabels(),
    rotation = 45,
    horizontalalignment = 'right',
)

ax.tick_params(labelsize = 10)

"""Según la grafica demuestra que el grupo de variables: ranking_imdb - tmdb_popularity, puntuación_imb - tmdb_popularity, ranking_imdb - tmdb_score poseen una correlacion positiva. Siendo por el contrario temporadas- año de lanzamiento una correlacion negativa. Con respecto a el resto de las variables no encontramos una correlacion fuerte entre ellas."""

df3 = df2.dropna()
df3

print(df3.isnull().sum())

"""#EDA

Vamos a ver como se comportan esas variables
"""

# Entre ranking_imdb y tmdb_popularity
plt.figure(figsize=(15,6))
plt.subplot(121)
# Hacemos un scatter plot
plt.scatter(df3['ranking_imdb'], df3['tmdb_popularity'], edgecolor='k', alpha=0.5)
plt.ylim(0, 500)
plt.yticks(fontsize=12)
plt.ylabel('Ranking_imdb [$]', fontsize=12)
plt.xticks(fontsize=12)
plt.xlim(0, 1200)
plt.xlabel('tmdb_popularity [$]', fontsize=12)
plt.title('Entre Ranking_imdb y tmdb_popularity', fontsize=16)

# Entre puntuación_imb y tmdb_popularity
plt.subplot(122)
plt.scatter(df3['puntacion_imdb'], df3['tmdb_popularity'], edgecolor='b', alpha=0.5)
plt.xlim(0, 100)
plt.xlabel('Puntuación_imb', fontsize=12)
plt.xticks(fontsize=12)
plt.ylim(0, 1200)
plt.ylabel('tmdb_popularity [$]', fontsize=12)
plt.yticks(fontsize=12)
plt.title('Entre puntuación_imb y tmdb_popularity', fontsize=16)
plt.show()


# Entre ranking_imdb y tmdb_score
plt.figure(figsize=(15,6))
plt.subplot(121)
# Hacemos un scatter plot
plt.scatter(df3['ranking_imdb'], df3['tmdb_score'], edgecolor='k', alpha=0.5)
plt.ylim(0, 50)
plt.yticks(fontsize=12)
plt.ylabel('Ranking_imdb [$]', fontsize=12)
plt.xticks(fontsize=12)
plt.xlim(0, 1200)
plt.xlabel('tmdb_score [$]', fontsize=12)
plt.title('Entre Ranking_imdb y tmdb_score', fontsize=16)

# Entre temporadas y año de lanzamiento
plt.subplot(122)
plt.scatter(df3['temporadas'], df3['año_lanzamiento'], edgecolor='b', alpha=0.5)
plt.xlim(0, 100)
plt.xlabel('Temporadas', fontsize=12)
plt.xticks(fontsize=12)
plt.ylim(0, 12000)
plt.ylabel('año_lanzamiento	 [$]', fontsize=12)
plt.yticks(fontsize=12)
plt.title('Entre temporadas y año_lanzamiento	', fontsize=16)
plt.show()

"""No es muy claro el grafico

Realizamos la normalización de los datos
"""

df3.columns

def normalize(df3):
    result = df.copy()

    for feature_name in df3.columns:
        max_val = df3[feature_name].max()
        min_val = df3[feature_name].min()
        result[feature_name] = (df3[feature_name] - min_val) / (max_val - min_val)

    return result

df3

df3_norm = normalize(df3[['año_lanzamiento', 'temporadas', 'ranking_imdb', 'puntacion_imdb', 'tmdb_popularity',
       'tmdb_score']])

"""# En cambio si lo reemplazamos en vez de eliminarlos"""

df5 = df2.fillna(0)
df5

"""Eliminamos las columnas que no nos aportan datos"""

df6 = df5.drop(['apto_edad', 'temporadas'],axis=1)

df6.info()

print(df6.isnull().sum())

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline
msno.matrix(df6.sample(250))

"""De esta manera mantenemos la estructura del data más completa y podemos evaluar con un campo más ampliado.

# Storytelling
El proyecto está dirigido a analizar las bases de datos y las tendencias de visualización de los distintos usuarios que utilizan la plataforma. Buscando en el modelo un sistema de recomendación para el usuario final. De esta manera cada usuario obtenga un abanico de sugerencias, las cuales sean de su interés.
Los sistemas basados en el contenido intentan averiguar cuáles son los aspectos favoritos de un usuario, y luego hacen recomendaciones sobre películas y/o series que comparten dichos aspectos. El filtrado se basa en que los usuarios de gustos similares probablemente le gusten películas semejantes a sus preferencias o intereses. Con el fin de mejorar la experiencia del streaming de la plataforma. En resumen, se supone que un usuario puede estar interesado en lo que les interesa a otros.
En los enfoques basados en la memoria se utilizan técnicas estadísticas para aproximar usuarios a las películas. Ejemplos de estas técnicas son la Correlación de Pearson, la Similitud de Coseno, la Distancia Euclidiana. En los enfoques basados en modelos, se desarrolla un modelo de usuarios que pueden crearse utilizando técnicas de machine learning como la regresión, la agrupación, la clasificación, etc.

# Análisis univariado
"""

sns.histplot(data = df6, x="ranking_imdb", kde = True)

"""En este histograma podemos visualizar la distribución el ranking de imdb (comunidad internacional de recomendación de series y peliculas) podemos ver que la distribución simetrica de este ranking. el nivel 0 este corresponde a niveles que no tienen datos (0.0)"""

sns.histplot (data = df6, x="año_lanzamiento", kde = True)

"""En este grafico podemos ver el aumento de lanzamientos a lo largo de los años, coincide en lo visto en gráficos anteriores (boxplot), donde visualizamos el aumento progresivo desde aparición de cine en 1930 aprox. hasta el año 2020. Con la llegada de la televisión en cada hogar, comienzan a aumentar las producciones lo que provoca el aumento exponencial a los producciones cinematográficas y las producciones que llegan a cada hogar en sus diferentes formas y categorías años atrás año."""

sns.kdeplot(df6["ranking_imdb"], bw=0.5)

"""En este grafico podemos ver la distribución netamente en los puntos de distribución de los ranking de imdb, con un ancho de banda de 0,5. El grafico comienza en numeros negativo y hay un pequeño aumento en ranking 0.0 y luego aumenta exponencialmente hasta llegar a un pico de aproximadamente 6 aprox. y luego decae exponencialmente hasta valores cercano a 10

# Análisis Bivariado
"""

df6_corr = df6.corr("spearman", numeric_only=True)
df6_corr

df6_corr = df6.corr("pearson", numeric_only=True)
df6_corr

"""Se nota una correlacion negativa entre años

Mapa de calor, correlaciones entre variables
"""

# Heatmap matriz de correlaciones
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(5, 5))

sns.heatmap(
    df6_corr,
    annot     = True,
    cbar      = False,
    annot_kws = {"size": 8},
    vmin      = -1,
    vmax      = 1,
    center    = 0,
    cmap      = sns.diverging_palette(20, 220, n=200),
    square    = True,
    ax        = ax
)

ax.set_xticklabels(
    ax.get_xticklabels(),
    rotation = 45,
    horizontalalignment = 'right',
)

ax.tick_params(labelsize = 10)

"""En este gráfico se relacionan la correlación entre variables a través de los colores y los índices. Según la gráfica demuestra que el grupo de variables: ranking_imdb - tmdb_popularity, puntuación_imb - tmdb_popularity, ranking_imdb - tmdb_score poseen una correlación positiva. Siendo por el contrario ranking_imdb-año_lanzamiento, tmdb_score-año_lanzamiento una correlación negativa. Con respecto al resto de las variables no encontramos una correlación fuerte entre ellas.

# Relaciones entre variables
"""

sns.pairplot (df6)

"""En estos gráficos de puntos no es posible visualizar una correlación lineal entre variables."""

sns.lineplot(x = "tv_o_pelicula", y="tmdb_popularity", data = df6)

"""En este gráfico ponemos visulizar la tendencia decreciente de la popularidad hacia las películas en comparación con las serie."""

sns.lineplot(x = "tv_o_pelicula", y="año_lanzamiento", data = df6)

"""Se puede ver una tendencia creciente a producir mayor cantidad de series en comparación con las peliculas"""

sns.lineplot(x = "tmdb_score", y="ranking_imdb", data = df6)

"""Se puede visualizar en este gráfico la puntación que dan los usuarios de tmdb y el ranking dado por los usuarios de imdb, encontrando una variación entre ambas variables.

# Primeras concluciones:
Se eliminaron dos columnas ('apto_edad', 'temporadas), ya que eran dos categorias que no aportaban al modelo esperado. Según lo recomendado por el profesor y debatido entre nosostros.

Con la eliminación de estas dos columnas, se realizan los gráficos de esta primer entrega y hasta el momento vemos que no podemos definir un modelo para explicar el dataframe, lo mismo que sucedia con anterioridad. Seguimos en la misma línea rientada al Procesamiento de lenguajes naturales (Natural language processing), que por lo visto será ideal para este proyecto.

# Sistema de recomendación

Para este algoritmo buscamos la similitud entre películas y/o series, las cuales a partir de una sugerencia arroja el top 10 de las mismas. Nos basaremos en la descripción de cada instancia, la cual da una característica de las mismas.
"""

df6['descripcion'].head()

"""Convertimos el vector de palabra de cada descripción general. Calculamos los vectores de frecuencia para cada descripción."""

from sklearn.feature_extraction.text import TfidfVectorizer

#Definimos un objeto vectorizador TF-IDF. Eliminamos todas las palabras vacías en ingles, como"the", "a", etc. con stopwords
tfidf = TfidfVectorizer(stop_words="english")

#Pasamos las instancias de descripcion a una cadena str sin enteros
df6['descripcion'] = [x for x in df6['descripcion'].map(lambda x: str(x).lower())]
#Reemplazamos los nulos con una cadena vacía
df6['descripcion'] = df6['descripcion'].fillna("")
#Construimos una matriz TF-IDF ajustando y transformando los datos del dataset
tfidf_matrix = tfidf.fit_transform(df6['descripcion'])
#Mostramos la matriz
tfidf_matrix.shape

"""Como utilizamos el vectorizador TF-IDF, el cálculo del producto nos arrojara la puntuación de similitud del coseno."""

#Importamos linear_kernel
from sklearn.metrics.pairwise import linear_kernel

cosine_sin = linear_kernel(tfidf_matrix, tfidf_matrix)

#Construimos un mapa inverso de indices y titulos de películas  y/o tv show
indices = pd.Series(df6.index, index=df6['titulo']).drop_duplicates()

#Definimos una función que a partir del título genere una lista de las 10 más similares
def get_recommendation(titulo, cosine_sin=cosine_sin):
  idx = indices[titulo]
  #Obtenemos las puntuaciones de similitud por pares de todas las peliculas con dicha pelicula  y/o tv show
  sin_scores = sorted(sin_scores, key=lambda x: x[1], reverse=True)
  #Obtenemos las puntuaciones de las primeras 10 peliculas  y/o tv show mas similares
  sin_scores = sin_scores[1:11]
  #Obtenemos los indices de las peliculas
  movie_indices = [i[0] for i in sin_scores]
  #Devuelve el top 10 de peliculas  y/o tv show mas similares o preferidas
  return df6['titulo'].iloc[movie_indices]

"""Se agregan más datos para tomar la decisión más acertada"""

features=['genero','titulo', 'tv_o_pelicula', 'descripcion' ]
filters = df6[features]

#Realizamos una limpieza de los datos. Colocamos todo en minusculas
def clean_data(x):
      return str.lower(x.replace(" "," "))

for features in features:
  filters[features] = filters[features].apply(clean_data)
filters.head()

#A partir de esta función alimentamos el vectorizador con los datos
def create_soup(x):
  return x['genero'] + ' ' + x['titulo'] + ' ' + x[ 'tv_o_pelicula'] + ' ' + x['descripcion']

filters["soup"] = filters.apply(create_soup, axis=1)

#Importamos CountVectorizer y creamos la matriz
from sklearn.feature_extraction.text import CountVectorizer

count = CountVectorizer(stop_words="english")
count_matrix = count.fit_transform(filters['soup'])

from sklearn.metrics.pairwise import cosine_similarity

cosine_sim2 = cosine_similarity(count_matrix, count_matrix)

filters.head()

#Restablecemos el indice de nuestro dataframe original y contruimos el mapeo inverso
filters = filters.reset_index()
indices = pd.Series(filters.index, index = filters['titulo'])

def get_recommendation_new(titulo, cosine_sin = cosine_sin):
  titulo=titulo.replace(" ", " ").lower()
  idx = indices[titulo]

#Obtenemos las puntuaciones de similitudes por pares de todas las peliculas  y/o tv show con dicha pelicula y/o tv show
  sin_scores = list(enumerate(cosine_sin[idx]))

  #Ordenamos las peliculas  y/o tv show segun sus similitudes
  sin_scores = sorted(sin_scores, key=lambda x: x[1], reverse=True)
  #Obtenemos las puntuaciones del top 10
  sin_scores = sin_scores[1:11]
  #Obtenemos los indices de las peliculas  y/o tv show
  movie_indices = [i[0] for i in sin_scores]
  #Nos devuelve el top 10
  return df6['titulo'].iloc[movie_indices]

"""# Probando el sistema

Realizamos una consulta de recomendación
"""

get_recommendation_new("i love lucy", cosine_sim2)

"""Realizamos otras consultas de recomendación"""

get_recommendation_new("dark shadows", cosine_sim2)

get_recommendation_new("lupin the third", cosine_sim2)

"""#Teniendo en cuenta la puntución de imb, generaremos una escala descendente de las 10 mejores puntuadas"""

df_puntuacion = df6.sort_values (by="puntacion_imdb", ascending = False)
df_puntuacion_final = df_puntuacion.drop(df_puntuacion.columns[[0, 5, 8, 7, 9, 11, 12]], axis=1)
df_puntuacion_final.head(10)

"""#Conclusión Final:

Por lo que hemos concluido, a partir de este algoritmo, de un título de nuestra base de datos logramos que arroje el top 10 de las más similares, las cuales utilizaremos a la hora de recomendar las preferencias de cada usuario. También se creó una lista de las 10 mejores puntuadas según IMDB. Concluimos también que hoy en día son más vistas las series respecto a las películas, de acuerdo a los datos arrojados en esta base de datos.
"""
