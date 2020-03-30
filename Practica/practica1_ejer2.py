#!/usr/bin/env python
# coding: utf-8

# # PRÁCTICA 1: Python, Ejericio 2 - Julia Hernández Elena

# Creamos un environment para este ejercicio ya que mas adelante lo tendremos que exportar:

# In[22]:


#!conda create --yes --name Practica_Python python=3.7


# In[12]:


#!conda activate Practica_Python


# In[24]:


#!conda install unidecode


# In[ ]:


#!conda install pandas


# In[ ]:


#!conda install openpyxl


# ### Conseguir un único DataFrame con toda la información de la carpeta `ine_activos`. Además añadir el campo `ds_provincias` del fichero `provincias.json` (cruzando por el código de cada provincia):

# In[13]:


import pandas as pd
from os import listdir
from os.path import isfile, join


# Leemos un fichero en particular para corroborar que se lee bien y ver que tipos de datos tiene:

# In[ ]:


lectura = pd.read_csv("ine_activos/2008T1_Agricultura.csv",sep=",",header = 0) #coger la primera fila como header


# In[ ]:


lectura.head() #Vemos que cada archivo tiene el cod_provincia y un valor para ese archivo


# Obtenemos una lista de todo lo contenido en el directorio y comprobamos que son archivos (no directorios) con el isfile:

# In[14]:


files = [f for f in listdir("ine_activos") if isfile(join("ine_activos", f))] 

print(len(files))#deberiamos tener 190 archivos


# Creamos una lista de dataframes leyendo cada archivo con pandas y estableciendo el `cod_provincia` como indice:

# In[15]:


lista_df = [pd.read_csv("ine_activos/" + file,sep=",", index_col = 'cod_provincia', header = 0) 
            for file in files]


# In[ ]:


type(lista_df) #tenemos una lista


# In[ ]:


len(lista_df) #tenemos 190 elementos en la lista (los 190 archivos)


# In[ ]:


type(lista_df[0]) #cada elemento de la lista es un dataframe


# Unimos los dataframes para tener un unico DataFrame con toda la información de la carpeta ine_activos:

# In[16]:


df = pd.concat(lista_df, axis=1, ignore_index = True) #concatenamos por columna (axis=1)
df.head()


# Cambiamos el nombre de las columnas usando el nombre de los archivos:
#     Tuve un problema con import unicode a pesar de estar instalado (vease debajo)

# In[17]:


#import unidecode
#df.columns = [unidecode.unidecode(row.split('.')[0]) for row in files]


# Por tanto tuve que hacer un replace para eliminar el acento:

# In[21]:


df.columns = [row.split('.')[0].replace('ó', 'o') for row in files] #establecemos el nombre de cada columna como el nombre del archivo 
df.head()


# Cargamos el archivo provincias.json en un dataframe y establecemos `cod_provincia` como index y con encoding utf-8 para poder leer los caracteres especiales:

# In[5]:


provincias_df = pd.read_json("provincias.json", encoding ='utf-8').set_index('cod_provincia')


# In[ ]:


provincias_df.head()


# Añadimos la provincia cruzando por el `cod_provincia`

# In[6]:


activos = provincias_df.join(df)


# In[ ]:


activos.head(10)


# ### Crear una carpeta en el directorio de trabajo que se llame salidas y guardar dicho Dataframe en CSV (con encoding en UTF-8) con el nombre ine_activos.csv:

# In[ ]:


activos.to_csv("salidas/ine_activos.csv", encoding = "utf-8")


# ### El DataFrame que hemos conseguido tienen muchas columnas. En muchas ocasiones es mejor tener los datos en un formato Narrow. Usar la función pd.melt y tratamientos de DataFrame visto en clase para conseguir pasar a este formato:

# Con pd.melt pivotamos la tabla de formato ancho a formato largo.
# - Establecemos `ds_provincias` y `cod_provincias` como variables identificadoras (tenemos que resetar el index para poder establecer cod_provincia como id_var)
# - Pivotamos el resto de variables llamandolas sector

# In[7]:


narrow = pd.melt(activos.reset_index(), id_vars = ['ds_provincia', 'cod_provincia'], var_name = 'sector')


# In[ ]:


narrow.head(3)


# Para la variable sector, extraemos el año, el trimestre y el nombre del sector:

# In[8]:


sector = [name.split('_')[1] for name in narrow.sector]
anio = [int(name[:4]) for name in narrow.sector] #los cuatro primeros caracteres nos indican el anio
trimestre =  [int(name[5:6]) for name in narrow.sector] #el 6 caracter nos da el trimestre


# Añadimos nuevas columnas con el ano y el trimestre para cada sector extraido y renombramos los valores de la variable sector:

# In[9]:


narrow['anio'] = anio
narrow['trimestre'] = trimestre
narrow.sector = sector


# In[ ]:


narrow.head()


# Reordenamos las columnas para tener el orden del enunciado:

# In[17]:


columnsTitles = ['ds_provincia', 'cod_provincia', 'value', 'anio', 'trimestre', 'sector']
narrow = narrow.reindex(columns=columnsTitles)


# In[ ]:


narrow.head()


# In[ ]:


narrow.dtypes


# ### Guardar este Dataframe en el mismo formato y destino que el anterior con el nombre narrow_data.csv:

# In[ ]:


narrow.to_csv("salidas/narrow_data.csv", encoding = "utf-8")


# ### En este nuevo formato es más fácil hacer algunos cálculos, para comprobar esto se pide calcular la población activa total para cada año y sector económico en el 4º trimestre. Una vez conseguido guardar el DataFrame en poblacion_anio.csv:

# Primero filtramos los del cuarto trimestre y agrupamos por sector y anio:

# In[11]:


filter_group = narrow[narrow.trimestre==4].groupby(['anio','sector'])


# Sumaos el total de poblacion activa del nuevo df:

# In[12]:


activos_anio = filter_group['value'].sum()
activos_anio = activos_anio.to_frame() #lo convertimos en df ya que era un panda series


# In[13]:


activos_anio.head(10)


# Creamos el csv:

# In[ ]:


narrow.to_csv("salidas/activos_anio.csv", encoding = "utf-8")


# ### Aunque el modo narrow puede ser muy cómodo para hacer cálculos no es el mejor para ver los datos y analizarlos. Usando la función pd.pivot_table se pide conseguir el reporte para el sector Servicios:

# Filtramos las entradas del sector servicios:

# In[14]:


servicios = narrow[narrow.sector=='Servicios']


# Usamos pd.pivot_table para establecer como indice la provincia, como columnas el anio y el trimestre y los valores el value

# In[15]:


servicios = pd.pivot_table(servicios, index = 'ds_provincia', columns = (['anio', 'trimestre']), values = 'value')


# In[16]:


servicios.head()


# ### Guardar el reporte de servicios conseguido esta vez en formato excel como servicios.xlsx:

# In[ ]:


servicios.to_excel("salidas/servicios.xlsx", encoding = "utf-8")


# ### Calcular ahora el total de población activa en España para todos los sectores para cada año y trimestre. La población activa al igual que el paro son estacionales (hay periodos del año dónde sube o baja como en verano). Por este motivo se quiere calcular la tasa de crecimiento-decrecimiento comparado con el mismo trimestre del año anterior:

# Agrupamos el dataframe Narrow por anio y trimestre para poder hacer calculos:

# In[119]:


anio_trim = narrow.groupby(['anio', 'trimestre'])


# Calculamos ahora el total de población activa en España para todos los sectores para cada año y trimestre y lo convertimos en un dataframe:

# In[125]:


activa_anio_trim = anio_trim['value'].sum() #obtenemos un panda series
activa_anio_trim = activa_anio_trim.to_frame()
activa_anio_trim.head()


# Creamos un segundo dataframe en el que añadimos 1 al año para poder luego hacer el calculo:

# In[128]:


shifted = activa_anio_trim.reset_index() #reseteamos el indice para poder manipular el año
shifted['anio']+=1
shifted = shifted.set_index(['anio', 'trimestre']) #ponemos el mismo indice que el df activa_anio_trim para poder hacer calculos
shifted.head()


# Caclulamos la tasa de poblacion activa usando la tabla original y la tabla en la que modificamos el año (+1):

# In[136]:


tasa_poblacion_activa = (
    (activa_anio_trim[4:]-shifted[:-4])/shifted[:-4]
)


# In[137]:


tasa_poblacion_activa.head(10)


# ### Guardar las tasas calculadas en el fichero tasas_poblacion_activa.json:

# In[139]:


tasa_poblacion_activa = tasa_poblacion_activa.reset_index() #resetamos el index para tener una entrada del json por fila
tasa_poblacion_activa.head()


# In[140]:


tasa_poblacion_activa.to_json("salidas/tasa_poblacion_activa.json", orient='records') 
    #orient=entrada del json por cada fila de df


# Leemos el fichero para comprobar que tenemos el formato que queremos:

# In[146]:


f = open("salidas/tasa_poblacion_activa.json", 'r')
print(f.read())


# ### Para poder realizar el ejercicio puede que hayas tenido que instalar varias librerías. Genera con conda un fichero environment_ejer2.yml para poder replicar el entorno de trabajo:
# 

# In[ ]:


#!conda env export > environment_ejer2.yml


# ### Una vez terminado el ejercicio convertir el notebook en un script puro de python con:

# In[23]:


get_ipython().system('jupyter nbconvert --to python practica1_ejer2.ipynb')


# In[ ]:





# In[ ]:




