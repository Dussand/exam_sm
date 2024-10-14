import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

# Título de la aplicación
st.title("ANALISIS DE RESULTADOS DEL EXAMEN DE ADMISION DE SAN MARCOS")

st.header('ANALISIS GENERAL')
#texto explicativo
st.write('Esta página web muestra un analisis exhaustivo de los resultados de los examenes de san marcos de los periodos 2023II, 2024I, 2024II, 2025I')

# Cargar datos
resultados_exam = pd.read_csv('data_scrap/resultados_consolidados.csv')
areas_sm = pd.read_csv('data_scrap/areas_sanmarcos')

#cambiamos el nombre de las columnas a nombres mas tecnicos
columns = {
     'area_code':'CODIGO DE AREA',
     'career_1':'CARRERA (PRIMERA OPCION)'
}

areas_sm.rename(columns=columns, inplace = True)

columns = {
     
    'CODIGO':'CODIGO DEL ESTUDIANTE',
    'APELLIDOS Y NOMBRES':'APELLIDOS Y NOMBRES',
    'ESCUELA PROFESIONAL':'CARRERA (PRIMERA OPCION)',
    'PUNTAJE FINAL':'PUNTAJE',
    'MERITOE.P':'PUESTO',
    'OBSERVACI&OacuteN':'OBSERVACION',
    'MERITOE.P ALCANZA VACANTE':'PUESTO_1',
    'ESCUELA SEGUNDA OPCIÓN':'CARRERA (SEGUNDA OPCION)',
    'ESCUELA PROFESIONAL (PRIMERA OPCIÓN)':'CARRERA (PRIMERA OPCION)_1',
    'PUNTAJE':'PUNTAJE_1',
    'ESCUELA PROFESIONAL (SEGUNDA OPCIÓN)':'CARRERA (SEGUNDA OPCION)_1'
}

resultados_exam.rename(columns=columns, inplace = True)

def unir_columnas(df, col1, col2):
    # Fusionar las dos columnas y asignar el resultado a la columna original
    df[col1] = df[col1].combine_first(df[col2])
    # Eliminar la columna duplicada
    df.drop(columns=[col2], inplace=True)
    return df

# Aplicar la función a las columnas duplicadas
resultados_exam = unir_columnas(resultados_exam, 'PUESTO', 'PUESTO_1')
resultados_exam = unir_columnas(resultados_exam, 'CARRERA (PRIMERA OPCION)', 'CARRERA (PRIMERA OPCION)_1')
resultados_exam = unir_columnas(resultados_exam, 'PUNTAJE', 'PUNTAJE_1')
resultados_exam = unir_columnas(resultados_exam, 'CARRERA (SEGUNDA OPCION)', 'CARRERA (SEGUNDA OPCION)_1')

#separamos las ciudades de las carreras para un mejor analisis
resultados_exam['location'] = resultados_exam['CARRERA (PRIMERA OPCION)'].str.extract(r' - (.+)')  # Extraer 'LIMA'
resultados_exam['CARRERA (PRIMERA OPCION)'] = resultados_exam['CARRERA (PRIMERA OPCION)'].str.replace(r' - .+', '', regex=True)  # Remover '- LIMA' de 'CARRERA (PRIMERA OPCION)'

#separamos las ciudades de las carreras para un mejor analisis
resultados_exam['location_2'] = resultados_exam['CARRERA (SEGUNDA OPCION)'].str.extract(r' - (.+)')  # Extraer 'LIMA'
resultados_exam['CARRERA (SEGUNDA OPCION)'] = resultados_exam['CARRERA (SEGUNDA OPCION)'].str.replace(r' - .+', '', regex=True)  # Remover '- LIMA' de 'CARRERA (PRIMERA OPCION)'

#corregimos los textos
resultados_exam['OBSERVACION'] = resultados_exam['OBSERVACION'].replace({
    'ALCANZO VACANTE SEGUNDA OPCIÃ\x93N':'ALCANZO VACANTE SEGUNDA OPCION',
    'ALCANZO VACANTE PRIMERA OPCIÃ\x93N':'ALCANZO VACANTE PRIMERA OPCION',
    'ALCANZO VACANTE':'ALCANZO VACANTE PRIMERA OPCION',
    'ALCANZO VACANTE SEGUNDA OPCIÓN':'ALCANZO VACANTE SEGUNDA OPCION'
})

#ARREGLAMOS LA CARRERA
resultados_exam['CARRERA (PRIMERA OPCION)'].replace('CIENCIA DE LA COMPUTACION', 'CIENCIAS DE LA COMPUNTACIÓN', inplace=True)

#rellenamos la columna de observacion con valores ausentes con "no alcanzó vacante"
resultados_exam['OBSERVACION'] = resultados_exam['OBSERVACION'].fillna('NO ALCANZO VACANTE')

#rellenamos la columna de location con valores ausentes con "LIMA"
resultados_exam['location'] = resultados_exam['location'].fillna('LIMA')
resultados_exam['location_2'] = resultados_exam['location_2'].fillna('LIMA')

#analizamos los tipos de datos y corregimos en base a las necesidades para el analisis
resultados_exam['CODIGO DEL ESTUDIANTE'] = resultados_exam['CODIGO DEL ESTUDIANTE'].astype(object)

#cruzamos los dataframes para que cada carrera tenga su area
resultados_exam = resultados_exam.merge(areas_sm, on = 'CARRERA (PRIMERA OPCION)', how = 'left')

#st.dataframe(resultados_exam)
#colocamos en una variable los periodos que existen en el dataframe
periodos = resultados_exam['periodo'].unique()
periodo_seleccionado = st.selectbox('Selecciona un periodo', periodos)

#filtramos los datos segun el periodo seleccionado
periodo_filter = resultados_exam[resultados_exam['periodo'] == periodo_seleccionado]

#mostramos los puntajes mas altos junto su carrera y postulante por periodo
idx_max_PUNTAJE = periodo_filter['PUNTAJE'].idxmax()

if idx_max_PUNTAJE in periodo_filter.index:
     resultado_maximo = periodo_filter.loc[[idx_max_PUNTAJE], ['APELLIDOS Y NOMBRES', 'CARRERA (PRIMERA OPCION)', 'PUNTAJE']]
     st.write("Postulante con el puntaje más alto:")
     st.dataframe(resultado_maximo, hide_index=True,  width=1000)
else:
     print(f"Índice {idx_max_PUNTAJE} no encontrado en el DataFrame.")

#mostramos un buscador para filtrar por nombre
name_searched = st.text_input('Buscar por nombre: ')

if name_searched:
    name_filtered = periodo_filter[periodo_filter['APELLIDOS Y NOMBRES'].str.contains(name_searched, case = False, na = False)]

    #mostramos el resultado
    if not name_filtered.empty:
        st.write(f'Resultado para la busqueda:({len(name_filtered)})')
        st.dataframe(name_filtered)
    else:
        st.write('No se encontraron resultados para su búsqueda')


#entramos al analisis en si
#mostraaremos los puntajes mas altos junto a la carrera y estudiante

st.header('ANALISIS DETALLADO')
st.subheader('En esta seccion se mostrarán graficos y tablas con mas detalles de analisis por periodo y por carrera.')


# Contenedor para las tarjetas
#armamos un df con el numero de postulantes por periodo y su variacion porcentual
var_periodo = resultados_exam.groupby('periodo')['CODIGO DEL ESTUDIANTE'].count().reset_index()
# Calcular la variación absoluta (diferencia) respecto al periodo anterior
var_periodo['variacion_absoluta'] = var_periodo['CODIGO DEL ESTUDIANTE'].diff().fillna(0)
# Calcular la variación porcentual respecto al periodo anterior
var_periodo['variacion_porcentual'] = var_periodo['CODIGO DEL ESTUDIANTE'].pct_change().fillna(0) * 100


#hacemuns pivot table con las observaciones del examen
var_ingre = resultados_exam.pivot_table(
     index='periodo',
     columns='OBSERVACION',
     values = 'CODIGO DEL ESTUDIANTE',
     aggfunc='count'
).reset_index()
#eliminamos las columnas innecesarioas, solo queremos ver los ingresados en primera opcion
var_ingre = var_ingre.drop(['ALCANZO VACANTE SEGUNDA OPCION', 'ANULADO', 'AUSENTE', 'NO ALCANZO VACANTE'], axis = 1)
# Calcular la variación absoluta (diferencia) respecto al periodo anterior
var_ingre['VARIACION ABSOLUTA'] = var_ingre['ALCANZO VACANTE PRIMERA OPCION'].diff().fillna(0)
# Calcular la variación porcentual respecto al periodo anterior
var_ingre['VARIACION PORCENTUAL'] = var_ingre['ALCANZO VACANTE PRIMERA OPCION'].pct_change().fillna(0) * 100


#seleccionaremos el periodo
periodo_metrics = resultados_exam['periodo'].unique()
periodo_metrics_sb = st.selectbox('Selecciona un periodo: ', periodo_metrics)


with st.container():
    # Tarjetas en una fila
    col1, col2, col3 = st.columns(3)
    
    with col1:
        num_post = resultados_exam[resultados_exam['periodo'] == periodo_metrics_sb]['CODIGO DEL ESTUDIANTE'].count()
        var = var_periodo[var_periodo['periodo'] == periodo_metrics_sb]['variacion_porcentual'].values[0]
        var = f'{var:.2f}%'
        st.metric(
             label='Numero de postulantes', 
             value= f'{num_post:,}',
             delta= var
        )

    with col2:
        num_ing = resultados_exam[(resultados_exam['periodo'] == periodo_metrics_sb) 
                                    & (resultados_exam['OBSERVACION'] == 'ALCANZO VACANTE PRIMERA OPCION')]['CODIGO DEL ESTUDIANTE'].count()
        var_ing = var_ingre[var_ingre['periodo'] == periodo_metrics_sb]['VARIACION PORCENTUAL'].values[0]
        var_ing = f'{var_ing:.2f}%'
        st.metric(
             label= 'Numero de ingresantes',
             value= f'{num_ing: ,}',
             delta = var_ing
        )

st.write('Porcentaje de alumnos que alcanzaron una vacante en el examen de la UNMSM de cada periodo.')

ingresados = resultados_exam.pivot_table(
    index = 'periodo', columns='OBSERVACION', values = 'CODIGO DEL ESTUDIANTE', aggfunc='count'
).fillna(0).reset_index()

ingresados['total_students'] = ingresados['ALCANZO VACANTE PRIMERA OPCION'] + ingresados['ALCANZO VACANTE SEGUNDA OPCION'] + ingresados['ANULADO'] + ingresados['AUSENTE'] + ingresados['NO ALCANZO VACANTE']

ingresados['PORCENTAJE'] = ingresados['ALCANZO VACANTE PRIMERA OPCION'] / ingresados['total_students'] * 100

# Formatea como porcentaje después de ordenar
ingresados['PORCENTAJE'] = ingresados['PORCENTAJE'].apply(lambda x: f'{x:.2f}%')


c1, c2 = st.columns(2)

with c1:
     por_ing = ingresados[ingresados['periodo'] == '2023II']
     st.metric(
          label = '2023II',
          value = por_ing['PORCENTAJE'].values[0]
     )

with c2:
     por_ing = ingresados[ingresados['periodo'] == '2024I']
     st.metric(
          label = '2024I',
          value = por_ing['PORCENTAJE'].values[0]
     )

c3, c4 = st.columns(2)     
with c3:
     por_ing = ingresados[ingresados['periodo'] == '2024II']
     st.metric(
          label = '2024II',
          value = por_ing['PORCENTAJE'].values[0]
     )
with c4:
     por_ing = ingresados[ingresados['periodo'] == '2025I']
     st.metric(
          label = '2025I',
          value = por_ing['PORCENTAJE'].values[0]
     )


fig = go.Figure()

fig.add_trace(
    go.Bar(
        x = ingresados.index,
        y = ingresados['total_students'],
        name = 'TOTAL ESTUDIANTES'
        
    )
)

# Agregar un título a la figura
fig.update_layout(
    title='TOTAL DE ESTUDIANTES QUE ALCANZARON UNA VACANTE Y NO POR PERIODO'
)


fig.add_trace(
    go.Scatter(
        x = ingresados.index,
        y = ingresados['ALCANZO VACANTE PRIMERA OPCION'],
        name = 'ALCANZARON UNA VACANTE'
    )
)

fig.add_trace(
    go.Scatter(
        x = ingresados.index,
        y = ingresados['ALCANZO VACANTE SEGUNDA OPCION'],
        name = 'ALCANZARON UNA VACANTE (SEGUNDA OPCION)'
    )
)

fig.add_trace(
    go.Scatter(
        x = ingresados.index,
        y = ingresados['NO ALCANZO VACANTE'],
        name = 'NO ALCANZARON VACANTE'
    )
)
st.plotly_chart(fig)

st.subheader('¿Cuál es la distribución de puntajes entre los estudiantes de diferentes carreras?')
st.write('Se verá si hay carreras con puntajes consistentemente más altos o más bajos.')


#periodos unicos en el df
periodo_career = resultados_exam['periodo'].unique()
#mostramos una lista desplegable con los periodos a escoger
periodo_career_sb = st.selectbox('Selecciona un periodo a analizar', periodo_career)

#seleccionamos la ubicacion de la carrera
location_career = resultados_exam['location'].unique()
#creamos un selectbox con las ubicaciones
location_career_selectbox = st.selectbox('Selecciona la ubicacion de tu carrera: ', location_career)

#carreras unicas en el df
filtered_careers = resultados_exam[resultados_exam['location'] == location_career_selectbox]['CARRERA (PRIMERA OPCION)'].unique()
#mostramos una lista desplegable con los periodos a escoger
career_sb = st.selectbox('Selecciona una carrera a analizar', filtered_careers)
#filtramos los datos con el periodo seleccionado
career_period_filtered = resultados_exam[(resultados_exam['location'] == location_career_selectbox) & (resultados_exam['CARRERA (PRIMERA OPCION)'] == career_sb) & (resultados_exam['periodo'] == periodo_career_sb)]
career_period_filtered[career_period_filtered['OBSERVACION'] == 'ALCANZO VACANTE PRIMERA OPCION'] 

# Verificar si hay datos para la carrera especificada
if not career_period_filtered.empty:
        fig = px.histogram(career_period_filtered, x = 'PUNTAJE', nbins = 10, title = f'DISTRUBCION DE LOS PUNTAJES DE {career_sb} EN EL PERIODO {periodo_career_sb}')
        fig.update_traces(histnorm = 'density', marker_color = 'skyblue')
        fig.add_vline(
            x=career_period_filtered['PUNTAJE'].max(), 
            line_width=2, line_dash='dash', 
            line_color='green',  
            annotation_text=f"Puntaje Máximo: {career_period_filtered['PUNTAJE'].max()}"
        )
        fig.add_vline(
            x=career_period_filtered[career_period_filtered['OBSERVACION'] == 'ALCANZO VACANTE PRIMERA OPCION']['PUNTAJE'].min(), 
            line_width=2, line_dash='dash', line_color='red',
            annotation_text=f"Puntaje Máximo: {career_period_filtered[career_period_filtered['OBSERVACION'] == 'ALCANZO VACANTE PRIMERA OPCION']['PUNTAJE'].min()}"
        )
        st.plotly_chart(fig)
        
        # Imprimir el puntaje máximo
        max_PUNTAJE = career_period_filtered['PUNTAJE'].max()
        min_PUNTAJE = career_period_filtered[career_period_filtered['OBSERVACION'] == 'ALCANZO VACANTE PRIMERA OPCION']['PUNTAJE'].min()
    
        st.write(f'EL PUNTAJE MÁXIMO PARA {career_sb} ES {max_PUNTAJE} Y EL PUNTAJE MINIMO DE INGRESO ES {min_PUNTAJE} EN EL PERIODO {periodo_career_sb}')
else:
        st.write(f'No hay datos disponibles para la carrera {career_sb}.')

st.header('¿Cuál es el maximo de puntaje por carrera de cada area?')
st.write('Revisaremos los puntajes maximos de cada carrera por cada area')

#reducimos a valores unicos los periodos
max_score_periodo = resultados_exam['periodo'].unique()
#mostramos una lista desplegable de los mismos
max_score_periodo_sb = st.selectbox("Selecciona el periodo de interes: ", max_score_periodo)


max_score_area = resultados_exam[resultados_exam['periodo'] == max_score_periodo_sb]['CODIGO DE AREA'].sort_values().unique()
max_score_area_sb = st.selectbox('Selecciona el area de interes: ', max_score_area)

max_score_filtered = resultados_exam[
     (resultados_exam['periodo'] == max_score_periodo_sb) 
     & (resultados_exam['CODIGO DE AREA'] == max_score_area_sb)
]

#agrupamos por carrera y mostramos el promedio
max_score = max_score_filtered.groupby('CARRERA (PRIMERA OPCION)')['PUNTAJE'].max().sort_values(ascending = False).reset_index()

#mostramos un grafico de lines de la libreria plotly.express
fig = px.line(max_score, x = 'CARRERA (PRIMERA OPCION)', y = 'PUNTAJE', title=f'Puntaje maximo por carrera en el periodo {periodo_career_sb} del área {max_score_area_sb}')
fig.add_hline(y=max_score['PUNTAJE'].mean(), line_dash = 'dash', line_color = 'red', annotation_text =f'Promedio de puntajes totales: {round(max_score['PUNTAJE'].mean(), 2)}', annotation_position = 'top right')
fig.update_layout(width=1000, height=700)
st.plotly_chart(fig)

promedio_puntaje = max_score['PUNTAJE'].mean()

st.write(f'PUNTAJE PROMEDIO DEL AREA {max_score_area_sb} DEL PERIODO {periodo_career_sb} FUE DE: {promedio_puntaje:.2f} PTS ')

st.dataframe(max_score, height=400, width=700) #mostramos el dataframe con los PUNTAJE con el puntaje maximo de las carreras

st.header('¿ES POSIBLE INGRESAR CON 900?')
st.write('Veremos una proporcion de estudiantes que ingresan con un puntaje igual o mayor a 900')

periodo_900 = resultados_exam['periodo'].unique()
periodo_selectbox = st.selectbox('Selecciona el periodo a analizar:' , periodo_900)

carrera_900 = resultados_exam[resultados_exam['periodo'] == periodo_selectbox]['CARRERA (PRIMERA OPCION)'].unique()
carrera_selectbox = st.selectbox('Selecciona la carrera a analizar:' , carrera_900)

#armamos el grafico de pie
#filtramos los datos con el periodo seleccionado
career_period_filtered_900 = resultados_exam[(resultados_exam['CARRERA (PRIMERA OPCION)'] == carrera_selectbox) & (resultados_exam['periodo'] == periodo_selectbox) & (resultados_exam['PUNTAJE'] >= 900) & (resultados_exam['PUNTAJE'] <= 1000)]
#agrupamos por observacion (si alcanzo vacante o no alcanzo vacante)
proportion = career_period_filtered_900.groupby('OBSERVACION')['OBSERVACION'].count().reset_index(name = 'count')  #agrupamos por observacion para contar cuantos postulantes alcanzaron vacantes
#creamos una columna con la proporcion de las observaciones
proportion['proportion'] = proportion['count'] / proportion['count'].sum() * 100 # mostramos el porcentaje

#creamos el grafico de pie
labels = proportion['OBSERVACION'] #denominamos las etiquetas

#configuramos el pie chart
fig = px.pie(proportion, values = 'proportion', names = labels, title = f"PROPORCION DE LOS POSTULANTES DE LA CARRERA DE {carrera_selectbox} QUE ALCANZARON UNA VACANTE CON PUNTAJE MAYOR A 900 PUNTOS DEL {periodo_selectbox}" )
st.plotly_chart(fig) #mostramos el piechart


st.header('¿QUE CARRERAS ESCOGEN COMO SEGUNDA OPCION')
st.write('Tienes en mente asegurarte con una carrera como una segunda opcion, en caso no alcances una vacante a la carrera que estás postulando.\nRevisa aqui que carreras tienen mas acogida como segunda opcion a la carrera que escogiste como primera opcion')


period_2_choice = resultados_exam[resultados_exam['CARRERA (SEGUNDA OPCION)'].notnull()]['periodo'].unique() #reduce el array a los valores unicos de la columna periodos (2023II, 2024I ,2024II)
#crea el select box con los periodos unicos establecidos en la anterior linea
periodo_second_choice = st.selectbox('Selecciona tu periodo de preferencia', period_2_choice)

#reduce el array a los valores unicos de la columna de carreras como primera opcion
#carrera_segunda_choice = resultados_exam['CARRERA (PRIMERA OPCION)'].unique()
carrera_segunda_choice = resultados_exam[resultados_exam['CARRERA (SEGUNDA OPCION)'].notnull()]['CARRERA (PRIMERA OPCION)'].unique()
#crea la lista desplegable con las valores unicos de las carreras
segunda_choice = st.selectbox('Selecciona la carrera que escogiste como primera opcion: ', carrera_segunda_choice)
#filtra el main dataframe pro periodo elegido, por carrera escogida y por los que alcanzaron vacante como primera opcion
segunda_opcion = resultados_exam[
    (resultados_exam['CARRERA (PRIMERA OPCION)'] == segunda_choice) 
    & (resultados_exam['periodo'] == periodo_second_choice)
    & (resultados_exam['OBSERVACION'] == 'ALCANZO VACANTE SEGUNDA OPCION')
]  
if not segunda_opcion.empty:
    heat_segundaopcion = segunda_opcion.pivot_table(
        index='CARRERA (SEGUNDA OPCION)', columns='CARRERA (PRIMERA OPCION)', values = 'CODIGO DEL ESTUDIANTE', aggfunc='count'
    ).reset_index().sort_values(by = segunda_choice, ascending = False)
    st.dataframe(heat_segundaopcion, width=1500)
    # plt.figure(figsize=(10,6))
    # sns.barplot(x = 'CARRERA (SEGUNDA OPCION)', y = segunda_choice, data=heat_segundaopcion )
    # plt.xticks(rotation = 90)
    # plt.xlabel('CARRERA COMO SEGUNDA OPCION')
    # plt.ylabel('CANTIDAD DE INGRESANTES')
    # plt.title(f'CANTIDAD DE ALUMNOS QUE ESCOGEN OTRA CARRERA COMO SEGUNDA OPCION DE LA CARRERA DE {segunda_choice} EN EL PERIODO {periodo_second_choice}')
    # st.pyplot(plt)

    fig = px.bar(
        heat_segundaopcion,
        x = 'CARRERA (SEGUNDA OPCION)',
        y = segunda_choice,
        title = f'CANTIDAD DE ALUMNOS DE LA CARRERA DE {segunda_choice} EN EL PERIODO {periodo_second_choice}'
    )

    st.plotly_chart(fig)

else:
    st.write(f'No se encontraron datos para la carrera de {segunda_choice}')

st.header('¿CUALES SON LOS PUNTAJES MINIMOS DE INGRESO DE LAS CARRERAS EN LOS EXAMENES?')
st.write('Si quieres saber el puntaje minimo a la carrera a la que postulas, ese mapa de calor te ayudará a saberlo.')

#seleccionamremos la area de interes
cohort_location = resultados_exam['location'].unique()
cohort_location_selectbox = st.selectbox('Selecciona tu ubicacion de interes:', cohort_location)

cohorte_carrera = resultados_exam[resultados_exam['location'] == cohort_location_selectbox ]['CARRERA (PRIMERA OPCION)'].unique()
cohorte_carrera_sb = st.selectbox('Selecciona la carrera: ', cohorte_carrera)
filtro_carrera_cohorte = resultados_exam[
    (resultados_exam['CARRERA (PRIMERA OPCION)'] == cohorte_carrera_sb) 
    & (resultados_exam['OBSERVACION'] == 'ALCANZO VACANTE PRIMERA OPCION')
    & (resultados_exam['location'] == cohort_location_selectbox )
]

if not filtro_carrera_cohorte.empty:
      #filtro_carrera_cohorte = resultados_exam[(resultados_exam['OBSERVACION'] == 'ALCANZO VACANTE PRIMERA OPCION') ]
      cohort_students = filtro_carrera_cohorte.pivot_table(index = 'CARRERA (PRIMERA OPCION)', columns ='periodo', values ='PUNTAJE', aggfunc = 'min')
      st.dataframe(cohort_students, width=1000)
      sns.heatmap(cohort_students, annot=True, fmt=".2f")
      plt.title(f'PUNTAJE MINIMO PARA INGRESAR A LA CARRERA {cohorte_carrera_sb} POR PERIODO')
      st.pyplot(plt)
      plt.clf()
      
else:
    st.write(f'No hay datos disponibles para la carrera {cohorte_carrera_sb}.')
    
st.header('¿QUIERES SABER QUE AREA ES LA MAS COMPETITIVA?')
st.write('A continuacion te mostraremos la area con mayor porcentaje de ingresados')

#filtramos los valores unicos de los periodos
area_periodo = resultados_exam['periodo'].unique()
#creamos una lista desplegable con los periodos
area_periodo_selectbox = st.selectbox('Seleccion un periodo', area_periodo)
#filtramos el df para que solo muestre las filas con el periodo seleccionad
area_periodo_filtered = resultados_exam[resultados_exam['periodo'] == area_periodo_selectbox]

#se crea una tabla pivot con las areas y el conteo de estudiantes por OBSERVACION
competencia = area_periodo_filtered.pivot_table(
      index='CODIGO DE AREA', columns='OBSERVACION', values ='CODIGO DEL ESTUDIANTE', aggfunc='count'
).fillna(0).reset_index()

#ccreamos una fila con el total de postulanes sumando todas las observaciones
competencia['TOTAL POSTULANTES'] = (
      competencia.get('ALCANZO VACANTE PRIMERA OPCION', 0) 
      + competencia.get('ALCANZO VACANTE SEGUNDA OPCION', 0)
      + competencia.get('ANULADO', 0)
      + competencia.get('AUSENTE', 0)
      + competencia.get('NO ALCANZO VACANTE', 0)
)

#borramos las columnas que no nos sirve porque solo queremos ver los que ingresaron con primera opcion
competencia = competencia[
    ['CODIGO DE AREA','ALCANZO VACANTE PRIMERA OPCION', 'TOTAL POSTULANTES']
].dropna(axis = 1, how = 'all')

competencia['proportion'] = ((
      competencia['ALCANZO VACANTE PRIMERA OPCION']

) / competencia['TOTAL POSTULANTES'] * 100)

# Ordena los valores numéricos
competencia = competencia.sort_values('proportion')

# Formatea como porcentaje después de ordenar
competencia['proportion'] = competencia['proportion'].apply(lambda x: f'{x:.2f}%')

st.dataframe(competencia, hide_index = True, width=1000)

#Veremos cuantos estudiantes ingresaron por carrera y periodo
st.header('¿QUIERES SABER EL PORCENTAJE DE INGRESADOS EN LA CARRERA QUE ELEGISTE?')
st.write('Este embudo que se muestra te muestra el porcentaje de postulantes que ingresaron a la carrera que elegiste, muchachon')

#colocamos un selectbox que nos filtre por periodo
funnel_periodo = resultados_exam['periodo'].unique()
funnel_periodo_sb = st.selectbox('Selecciona un periodo:' , funnel_periodo)

#colocamos un selectbox que nos filtre por periodo y por el codigo del area
funnel_area = resultados_exam[resultados_exam['periodo'] == funnel_periodo_sb]['CODIGO DE AREA'].unique()
funnel_area_sb  = st.selectbox('Selecciona un area:', funnel_area)

#colocamos un selectbox que nos filtre por periodo el codigo del area para poder escoger una carrera
funnel_career = resultados_exam[(resultados_exam['periodo'] == funnel_periodo_sb) & (resultados_exam['CODIGO DE AREA'] == funnel_area_sb)]['CARRERA (PRIMERA OPCION)'].unique()
funnel_career_sb = st.selectbox('Selecciona una carrera: ', funnel_career)

#filtramos el df para que nos muestre solo la carrera la seleccionada
funnel_filteresd = resultados_exam[
    (resultados_exam['periodo'] == funnel_periodo_sb) 
    & (resultados_exam['CODIGO DE AREA'] == funnel_area_sb)
    & (resultados_exam['CARRERA (PRIMERA OPCION)'] == funnel_career_sb)
]

#creamos una tabla pivot para tener un mejor analisis de los datos
funnel = funnel_filteresd.pivot_table(
    index = 'CARRERA (PRIMERA OPCION)',
    columns= 'OBSERVACION',
    values= 'CODIGO DEL ESTUDIANTE',
    aggfunc='count'
).fillna(0).reset_index()

#creamos una columna mas con la suma del total de estudiantes
funnel['TOTAL ESTUDIANTES'] = (
        funnel.get('ALCANZO VACANTE PRIMERA OPCION', 0) 
      + funnel.get('ALCANZO VACANTE SEGUNDA OPCION', 0)
      + funnel.get('ANULADO', 0)
      + funnel.get('AUSENTE', 0)
      + funnel.get('NO ALCANZO VACANTE', 0)
)


#creamos 3 columnas con el porcentaje de cada observacion en base a la cantidad de alumnos
funnel['ALCANZO VACANTE PRIMERA OPCION (%)'] = (funnel['ALCANZO VACANTE PRIMERA OPCION'] / funnel['TOTAL ESTUDIANTES']) * 100
funnel['NO ALCANZO VACANTE (%)'] = (funnel['NO ALCANZO VACANTE'] / funnel['TOTAL ESTUDIANTES']) * 100
funnel['TOTAL ESTUDIANTES (%)'] = (funnel['TOTAL ESTUDIANTES'] / funnel['TOTAL ESTUDIANTES']) *100 

#utilizamso el metodo melt para tener un mayor orden en el df y poder armar el embudo que queremos
melted_df = pd.melt(funnel, 
                     id_vars=['CARRERA (PRIMERA OPCION)'], 
                     value_vars=['ALCANZO VACANTE PRIMERA OPCION (%)','TOTAL ESTUDIANTES (%)'],
                     var_name='ESTADO', 
                     value_name='CANTIDAD').sort_values(by = 'CANTIDAD' , ascending=False)
#colocamos en porcentaje la cantidad calculada
melted_df['CANTIDAD'] = melted_df['CANTIDAD'].apply(lambda x: f'{x:.2f}%')


k1, k2 = st.columns(2)

with k1:
     st.metric(
          label = 'Cantidad de postulantes',
          value= f'{funnel_filteresd['CODIGO DEL ESTUDIANTE'].count()} (100%)'
     )
    
with k2:
     value_funnel = funnel_filteresd[funnel_filteresd['OBSERVACION'] == 'ALCANZO VACANTE PRIMERA OPCION']['CODIGO DEL ESTUDIANTE'].count()
     value_funnel_var = melted_df[melted_df['ESTADO'] == 'ALCANZO VACANTE PRIMERA OPCION (%)']['CANTIDAD'].values[0]
     st.metric(
          label = 'Cantidad de ingresantes',
          value= f'{value_funnel} ({value_funnel_var})'
     )
     

#armamos el embudo 
fig = px.funnel(
      melted_df,
      x = 'ESTADO',
      y = 'CANTIDAD',
      title= f'CANTIDAD DE ALUMNOS INGRESADOS A {funnel_career_sb} EN EL PERIODO {funnel_periodo_sb}',
      
      )

#mostramos el embudo
st.plotly_chart(fig)

st.write('POSTULA P CICLERO')

