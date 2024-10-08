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

# C2023II = pd.read_csv(r'C:\Users\Dussand\Desktop\proyectsDS\Python\Scrapping\postulantes_por_carrera2023II.csv')
# C2024I = pd.read_csv(r'C:\Users\Dussand\Desktop\proyectsDS\Python\Scrapping\postulantes_por_carrera2024I.csv')
# C2024II = pd.read_csv(r'C:\Users\Dussand\Desktop\proyectsDS\Python\Scrapping\postulantes_por_carrera2024II.csv')
# C2025I = pd.read_csv(r'C:\Users\Dussand\Desktop\proyectsDS\Python\Scrapping\postulantes_por_carrera2025I.csv')
# areas_sm = pd.read_csv(r'C:\Users\Dussand\Desktop\proyectsDS\Python\Scrapping\areas_sanmarcos')

C2023II = pd.read_csv('postulantes_por_carrera2023II.csv')
C2024I = pd.read_csv('postulantes_por_carrera2024I.csv')
C2024II = pd.read_csv('postulantes_por_carrera2024II.csv')
C2025I = pd.read_csv('postulantes_por_carrera2025I.csv')
areas_sm = pd.read_csv('areas_sanmarcos')

#creamos una columna con el periodo del examen para cada periodo
C2023II['periodo'] = "2023II"
C2024I['periodo'] = "2024I"
C2024II['periodo'] = "2024II"
C2025I['periodo'] = "2025I"

#cambiamos el nombre de las columnas
columns = {
    'CODIGO':'student_id',
    'APELLIDOS Y NOMBRES':'full_name',
    'ESCUELA PROFESIONAL':'career_1',
    'PUNTAJE FINAL':'score',
    'MERITOE.P':'merit_order',
    'OBSERVACI&OacuteN':'observation'
}

C2023II.rename(columns=columns, inplace = True)

columns = {
    'CODIGO':'student_id',
    'APELLIDOS Y NOMBRES':'full_name',
    'ESCUELA PROFESIONAL':'career_1',
    'PUNTAJE FINAL':'score',
    'MERITOE.P ALCANZA VACANTE':'merit_order',
    'OBSERVACI&OacuteN':'observation',
    'ESCUELA SEGUNDA OPCIÓN':'career_2'
}

C2024I.rename(columns=columns, inplace = True)

columns = {
    'CODIGO':'student_id',
    'APELLIDOS Y NOMBRES':'full_name',
    'ESCUELA PROFESIONAL (PRIMERA OPCIÓN)':'career_1',
    'PUNTAJE':'score',
    'MERITOE.P':'merit_order',
    'OBSERVACI&OacuteN':'observation',
    'ESCUELA PROFESIONAL (SEGUNDA OPCIÓN)':'career_2'
}

C2024II.rename(columns=columns, inplace = True)

columns = {
    'CODIGO':'student_id',
    'APELLIDOS Y NOMBRES':'full_name',
    'ESCUELA PROFESIONAL':'career_1',
    'PUNTAJE':'score',
    'MERITOE.P':'merit_order',
    'OBSERVACI&OacuteN':'observation'
}

C2025I.rename(columns=columns, inplace = True)

#anexamos los dataframes
resultados_exam = pd.concat([C2023II, C2024I, C2024II, C2025I], ignore_index = True)

#separamos las ciudades de las carreras para un mejor analisis
resultados_exam['location'] = resultados_exam['career_1'].str.extract(r' - (.+)')  # Extraer 'LIMA'
resultados_exam['career_1'] = resultados_exam['career_1'].str.replace(r' - .+', '', regex=True)  # Remover '- LIMA' de 'career_1'

#separamos las ciudades de las carreras para un mejor analisis
resultados_exam['location_2'] = resultados_exam['career_2'].str.extract(r' - (.+)')  # Extraer 'LIMA'
resultados_exam['career_2'] = resultados_exam['career_2'].str.replace(r' - .+', '', regex=True)  # Remover '- LIMA' de 'career_1'

#corregimos los textos
resultados_exam['observation'] = resultados_exam['observation'].replace({
    'ALCANZO VACANTE SEGUNDA OPCIÃ\x93N':'ALCANZO VACANTE SEGUNDA OPCION',
    'ALCANZO VACANTE PRIMERA OPCIÃ\x93N':'ALCANZO VACANTE PRIMERA OPCION',
    'ALCANZO VACANTE':'ALCANZO VACANTE PRIMERA OPCION',
    'ALCANZO VACANTE SEGUNDA OPCIÓN':'ALCANZO VACANTE SEGUNDA OPCION'
})

#rellenamos la columna de observacion con valores ausentes con "no alcanzó vacante"
resultados_exam['observation'] = resultados_exam['observation'].fillna('NO ALCANZO VACANTE')

#rellenamos la columna de location con valores ausentes con "LIMA"
resultados_exam['location'] = resultados_exam['location'].fillna('LIMA')
resultados_exam['location_2'] = resultados_exam['location_2'].fillna('LIMA')

#analizamos los tipos de datos y corregimos en base a las necesidades para el analisis
resultados_exam['student_id'] = resultados_exam['student_id'].astype(object)

#cruzamos los dataframes para que cada carrera tenga su area
resultados_exam = resultados_exam.merge(areas_sm, on = 'career_1', how = 'left')

#st.dataframe(resultados_exam)
#colocamos en una variable los periodos que existen en el dataframe
periodos = resultados_exam['periodo'].unique()
periodo_seleccionado = st.selectbox('Selecciona un periodo', periodos)

#filtramos los datos segun el periodo seleccionado

periodo_filter = resultados_exam[resultados_exam['periodo'] == periodo_seleccionado]

#mostramos los puntajes mas altos junto su carrera y postulante por periodo
idx_max_score = periodo_filter['score'].idxmax()

# Extraemos la fila con el puntaje más alto
#resultado_maximo = periodo_filter.loc[[idx_max_score], ['full_name', 'career_1', 'score']]

if idx_max_score in periodo_filter.index:
     resultado_maximo = periodo_filter.loc[[idx_max_score], ['full_name', 'career_1', 'score']]
     st.write("Postulante con el puntaje más alto:")
     st.dataframe(resultado_maximo)
else:
     print(f"Índice {idx_max_score} no encontrado en el DataFrame.")

#mostramos un buscador para filtrar por nombre
name_searched = st.text_input('Buscar por nombre: ')

if name_searched:
    name_filtered = periodo_filter[periodo_filter['full_name'].str.contains(name_searched, case = False, na = False)]

    #mostramos el resultado
    if not name_filtered.empty:
        st.write(f'Resultado para la busqueda:({len(name_filtered)})')
        st.dataframe(name_filtered)
    else:
        st.write('No se encontraron resultados para su búsqueda')


#entramos al analisis en si
#mostraaremos los puntajes mas altos junto a la carrera y estudiante

st.header('ANALISIS DETALLADO')

st.write('En esta seccion se mostrarán graficos y tablas con mas detalles de analisis por periodo y por carrera.')

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
filtered_careers = resultados_exam[resultados_exam['location'] == location_career_selectbox]['career_1'].unique()
#mostramos una lista desplegable con los periodos a escoger
career_sb = st.selectbox('Selecciona una carrera a analizar', filtered_careers)
#filtramos los datos con el periodo seleccionado
career_period_filtered = resultados_exam[(resultados_exam['location'] == location_career_selectbox) & (resultados_exam['career_1'] == career_sb) & (resultados_exam['periodo'] == periodo_career_sb)]
career_period_filtered

# Verificar si hay datos para la carrera especificada
if not career_period_filtered.empty:
        # Crear un histograma de los puntajes
        plt.figure(figsize=(10, 6))
        sns.histplot(career_period_filtered['score'], bins=10, kde=True)  # Agregar KDE para suavizar la curva
        plt.title(f'DISTRIBUCIÓN DE PUNTAJES EN {career_sb} - {periodo_career_sb}')
        plt.xlabel('Puntaje')
        plt.ylabel('Frecuencia')
        plt.axvline(career_period_filtered['score'].max(), color='green', linestyle='--', label='Puntaje Máximo')
        plt.axvline(career_period_filtered[career_period_filtered['observation'] == 'ALCANZO VACANTE PRIMERA OPCION']['score'].min(), color='red', linestyle='--', label='Puntaje Minimo de ingreso')
        plt.legend()
        st.pyplot(plt.gcf())
        
        # Imprimir el puntaje máximo
        max_score = career_period_filtered['score'].max()
        min_score = career_period_filtered[career_period_filtered['observation'] == 'ALCANZO VACANTE PRIMERA OPCION']['score'].min()
    
        st.write(f'EL PUNTAJE MÁXIMO PARA {career_sb} ES {max_score} Y EL PUNTAJE MINIMO DE INGRESO ES {min_score} EN EL PERIODO {periodo_career_sb}')
else:
        st.write(f'No hay datos disponibles para la carrera {career_sb}.')

st.header('¿Cuál es el maximo de puntaje por carrera de cada area?')
st.write('Revisaremos los puntajes maximos de cada carrera por cada area')

max_score_periodo = resultados_exam['periodo'].unique()
max_score_periodo_sb = st.selectbox("Selecciona el periodo de interes: ", max_score_periodo)

max_score_area = resultados_exam['area_code'].sort_values().unique()
max_score_area_sb = st.selectbox('Selecciona el area de interes: ', max_score_area)

max_score_filtered = resultados_exam[(resultados_exam['periodo'] == periodo_career_sb) & (resultados_exam['location'] == location_career_selectbox) & (resultados_exam['area_code'] == max_score_area_sb)]

#agrupamos por carrera y mostramos el promedio
max_score = max_score_filtered.groupby('career_1')['score'].max().sort_values(ascending = False).reset_index()
#top10 = max_score.nlargest(20, 'score')
#Creamos un grafico de lineas

plt.figure(figsize = (15,6))
sns.lineplot(x = 'career_1', y = 'score', data=max_score, label='PUNTAJE MAXIMO DE CADA CARRERA')
plt.axhline(y=max_score['score'].mean(), color='green', linestyle='--', label='PUNTAJE PROMEDIO DEL AREA')
#plt.text(max_score['score'].mean(), plt.ylim()[1] * 0.9, f'{max_score['score'].mean()}', ha='center', color='green')
plt.xlabel('Carrera')
plt.ylabel('Puntaje maximo')
plt.title(f'Puntaje maximo por carrera en el periodo {periodo_career_sb}')
plt.xticks(rotation = 90)
plt.legend()
st.pyplot(plt.gcf())

promedio_puntaje = max_score['score'].mean()

st.write(f'PUNTAJE PROMEDIO DEL AREA {max_score_area_sb} DEL PERIODO {periodo_career_sb} FUE DE: {promedio_puntaje:.2f} PTS ')

st.dataframe(max_score) #mostramos el dataframe con los score con el puntaje maximo de las carreras

st.header('¿ES POSIBLE INGRESAR CON 900?')
st.write('Veremos una proporcion de estudiantes que ingresan con un puntaje igual o mayor a 900')

periodo_900 = resultados_exam['periodo'].unique()
periodo_selectbox = st.selectbox('Selecciona el periodo a analizar:' , periodo_900)

carrera_900 = resultados_exam['career_1'].unique()
carrera_selectbox = st.selectbox('Selecciona la carrera a analizar:' , carrera_900)

#armamos el grafico de pie
#filtramos los datos con el periodo seleccionado
career_period_filtered_900 = resultados_exam[(resultados_exam['career_1'] == carrera_selectbox) & (resultados_exam['periodo'] == periodo_selectbox) & (resultados_exam['score'] >= 900) & (resultados_exam['score'] <= 1000)]
#agrupamos por observacion (si alcanzo vacante o no alcanzo vacante)
proportion = career_period_filtered_900.groupby('observation')['observation'].count().reset_index(name = 'count')  #agrupamos por observacion para contar cuantos postulantes alcanzaron vacantes
#creamos una columna con la proporcion de las observaciones
proportion['proportion'] = proportion['count'] / proportion['count'].sum() * 100 # mostramos el porcentaje

#creamos el grafico de pie
labels = proportion['observation'] #denominamos las etiquetas

fig, ax = plt.subplots(figsize = (8,8))
ax.pie(proportion['proportion'], labels=labels, autopct='%1.1f%%', startangle=90)
ax.axis('equal')
plt.title(f"PROPORCION DE LOS POSTULANTES DE LA CARRERA DE {carrera_selectbox} QUE ALCANZARON UNA VACANTE CON PUNTAJE MAYOR A 900 PUNTOS DEL {periodo_selectbox}")

#mostramos el grafico en el web
st.pyplot(fig)
plt.close()

st.header('¿QUE CARRERAS ESCOGEN COMO SEGUNDA OPCION')
st.write('Tienes en mente asegurarte con una carrera como una segunda opcion, en caso no alcances una vacante a la carrera que estás postulando.\nRevisa aqui que carreras tienen mas acogida como segunda opcion a la carrera que escogiste como primera opcion')


period_2_choice = resultados_exam[resultados_exam['career_2'].notnull()]['periodo'].unique() #reduce el array a los valores unicos de la columna periodos (2023II, 2024I ,2024II)
#crea el select box con los periodos unicos establecidos en la anterior linea
periodo_second_choice = st.selectbox('Selecciona tu periodo de preferencia', period_2_choice)

#reduce el array a los valores unicos de la columna de carreras como primera opcion
#carrera_segunda_choice = resultados_exam['career_1'].unique()
carrera_segunda_choice = resultados_exam[resultados_exam['career_2'].notnull()]['career_1'].unique()
#crea la lista desplegable con las valores unicos de las carreras
segunda_choice = st.selectbox('Selecciona la carrera que escogiste como primera opcion: ', carrera_segunda_choice)
#filtra el main dataframe pro periodo elegido, por carrera escogida y por los que alcanzaron vacante como primera opcion
segunda_opcion = resultados_exam[
    (resultados_exam['career_1'] == segunda_choice) 
    & (resultados_exam['periodo'] == periodo_second_choice)
    & (resultados_exam['observation'] == 'ALCANZO VACANTE SEGUNDA OPCION')
]  
if not segunda_opcion.empty:
    heat_segundaopcion = segunda_opcion.pivot_table(
        index='career_2', columns='career_1', values = 'student_id', aggfunc='count'
    ).reset_index().sort_values(by = segunda_choice, ascending = False)
    heat_segundaopcion
    plt.figure(figsize=(10,6))
    sns.barplot(x = 'career_2', y = segunda_choice, data=heat_segundaopcion )
    plt.xticks(rotation = 90)
    plt.xlabel('CARRERA COMO SEGUNDA OPCION')
    plt.ylabel('CANTIDAD DE INGRESANTES')
    plt.title(f'CANTIDAD DE ALUMNOS QUE ESCOGEN OTRA CARRERA COMO SEGUNDA OPCION DE LA CARRERA DE {segunda_choice} EN EL PERIODO {periodo_second_choice}')
    st.pyplot(plt) 

else:
    st.write(f'No se encontraron datos para la carrera de {segunda_choice}')

st.header('¿CUALES SON LOS PUNTAJES MINIMOS DE INGRESO DE LAS CARRERAS EN LOS EXAMENES?')
st.write('Si quieres saber el puntaje minimo a la carrera a la que postulas, ese mapa de calor te ayudará a saberlo.')

#seleccionamremos la area de interes
cohort_location = resultados_exam['location'].sort_values().unique()
cohort_location_selectbox = st.selectbox('Selecciona tu ubicacion de interes:', cohort_location)

cohorte_carrera = resultados_exam[resultados_exam['location'] == cohort_location_selectbox ]['career_1'].unique()
cohorte_carrera_sb = st.selectbox('Selecciona la carrera: ', cohorte_carrera)
filtro_carrera_cohorte = resultados_exam[(resultados_exam['career_1'] == cohorte_carrera_sb) & (resultados_exam['observation'] == 'ALCANZO VACANTE PRIMERA OPCION') & (resultados_exam['location'] == cohort_location_selectbox )]

if not filtro_carrera_cohorte.empty:
      #filtro_carrera_cohorte = resultados_exam[(resultados_exam['observation'] == 'ALCANZO VACANTE PRIMERA OPCION') ]
      cohort_students = filtro_carrera_cohorte.pivot_table(index = 'career_1', columns='periodo', values='score', aggfunc='min')
      cohort_students
      sns.heatmap(cohort_students, annot=True, fmt=".2f")
      plt.title(f'PUNTAJE MINIMO PARA INGRESAR A LA CARRERA {cohorte_carrera_sb} POR PERIODO')
      st.pyplot(plt)
      plt.clf() 
else:
     st.write(f'No hay datos disponibles para la carrera {cohorte_carrera_sb}.')


cohorte_carrera_2 = resultados_exam['career_2'].dropna().unique()
cohorte_carrera_sb_2 = st.selectbox('Selecciona la carrera: ', cohorte_carrera_2)
filtro_carrera_cohorte_2= resultados_exam[(resultados_exam['career_2'] == cohorte_carrera_sb_2) & (resultados_exam['observation'] == 'ALCANZO VACANTE SEGUNDA OPCION')]

if not filtro_carrera_cohorte_2.empty:
      #filtro_carrera_cohorte = resultados_exam[(resultados_exam['observation'] == 'ALCANZO VACANTE PRIMERA OPCION') ]
      cohort_students_2 = filtro_carrera_cohorte_2.pivot_table(index = 'career_2', columns='periodo', values='score', aggfunc='min')
      cohort_students_2
      sns.heatmap(cohort_students_2, annot=True, fmt=".2f")
      plt.title(f'PUNTAJE MINIMO PARA INGRESAR A LA CARRERA {cohorte_carrera_sb_2} POR PERIODO')
      st.pyplot(plt)
      plt.clf()
else:
        st.write(f'No hay datos disponibles para la carrera {cohorte_carrera_sb_2}.')

        
st.header('¿QUIERES SABER QUE AREA ES LA MAS COMPETITIVA?')
st.write('A continuacion te mostraremos la area con mayor porcentaje de ingresados')

#filtramos los valores unicos de los periodos
area_periodo = resultados_exam['periodo'].unique()
#creamos una lista desplegable con los periodos
area_periodo_selectbox = st.selectbox('Seleccion un periodo', area_periodo)
#filtramos el df para que solo muestre las filas con el periodo seleccionad
area_periodo_filtered = resultados_exam[resultados_exam['periodo'] == area_periodo_selectbox]

#se crea una tabla pivot con las areas y el conteo de estudiantes por observation
competencia = area_periodo_filtered.pivot_table(
      index='area_code', columns='observation', values ='student_id', aggfunc='count'
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
    ['area_code','ALCANZO VACANTE PRIMERA OPCION', 'TOTAL POSTULANTES']
].dropna(axis = 1, how = 'all')

competencia['proportion'] = ((
      competencia['ALCANZO VACANTE PRIMERA OPCION']

) / competencia['TOTAL POSTULANTES'] * 100)

# Ordena los valores numéricos
competencia = competencia.sort_values('proportion')

# Formatea como porcentaje después de ordenar
competencia['proportion'] = competencia['proportion'].apply(lambda x: f'{x:.2f}%')

st.dataframe(competencia, hide_index = True)

#ahora vamos a mostrar la cantidad de postulantes y postulantes para cada carrera por area

code_area =  resultados_exam['area_code'].sort_values().unique()

code_area_selectbox = st.selectbox('Selecciona la area de interes: ', code_area)

code_area_filtered = resultados_exam[(resultados_exam['area_code'] == code_area_selectbox) & (resultados_exam['periodo'] == area_periodo_selectbox)]

code_area_group = code_area_filtered.pivot_table(
    index='career_1', columns='observation', values = 'student_id', aggfunc = 'count'
).fillna(0)


code_area_group['TOTAL POSTULANTES'] = (
      code_area_group.get('ALCANZO VACANTE PRIMERA OPCION', 0) 
      + code_area_group.get('ALCANZO VACANTE SEGUNDA OPCION', 0)
      + code_area_group.get('ANULADO', 0)
      + code_area_group.get('AUSENTE', 0)
      + code_area_group.get('NO ALCANZO VACANTE', 0)
)

code_area_group = code_area_group[
    ['ALCANZO VACANTE PRIMERA OPCION', 'TOTAL POSTULANTES']
].dropna(axis = 1)

code_area_group['proportion'] = ((
      code_area_group['ALCANZO VACANTE PRIMERA OPCION']

) / code_area_group['TOTAL POSTULANTES'] * 100)

# Ordena los valores numéricos
code_area_group = code_area_group.sort_values('proportion')

# Formatea como porcentaje después de ordenar
code_area_group['proportion'] = code_area_group['proportion'].apply(lambda x: f'{x:.2f}%')

st.dataframe(code_area_group)

if not code_area_group.empty:
      sns.barplot(data= code_area_group, x='career_1', y = 'TOTAL POSTULANTES')
      sns.lineplot(data= code_area_group, x ='career_1', y='ALCANZO VACANTE PRIMERA OPCION', color='red', linestyle='-')
      #plt.fill_between(code_area_group['career_1'], code_area_group['ALCANZO VACANTE PRIMERA OPCION'], alpha=0.3)
      plt.title(f'CANTIDAD DE VACANTES ALCANZADAS COMO PRIMERA OPCION EN EL PERIODO {area_periodo_selectbox}')
      plt.ylabel('CANTIDAD')
      plt.xlabel(f'CARRERA DEL AREA {code_area_selectbox}')
      plt.xticks(rotation = 90)
      st.pyplot(plt)
      plt.clf()
else:
      st.write('No se encontraron resultados par el area de interes')




