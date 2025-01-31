import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go


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


#rellenamos la columna de observacion con valores ausentes con "no alcanzó vacante"
resultados_exam['OBSERVACION'] = resultados_exam['OBSERVACION'].fillna('NO ALCANZO VACANTE')

#rellenamos la columna de location con valores ausentes con "LIMA"
resultados_exam['location'] = resultados_exam['location'].fillna('LIMA')
resultados_exam['location_2'] = resultados_exam['location_2'].fillna('LIMA')

#analizamos los tipos de datos y corregimos en base a las necesidades para el analisis
resultados_exam['CODIGO DEL ESTUDIANTE'] = resultados_exam['CODIGO DEL ESTUDIANTE'].astype(object)

# Reemplazar los valores específicos en la columna 'carrera'
resultados_exam['CARRERA (PRIMERA OPCION)'] = resultados_exam['CARRERA (PRIMERA OPCION)'].replace({
    'CIENCIA DE LA COMPUTACIÓN': 'CIENCIAS DE LA COMPUTACION',
    'CIENCIAS DE LA COMPUTACIÓN': 'CIENCIAS DE LA COMPUTACION'
})

#cruzamos los dataframes para que cada carrera tenga su area
resultados_exam = resultados_exam.merge(areas_sm, on = 'CARRERA (PRIMERA OPCION)', how = 'left')

st.sidebar.title('Encuentra a tu postulante')

# Sidebar: Selección de periodo
periodos = resultados_exam['periodo'].unique()
periodo_seleccionado = st.sidebar.selectbox('Selecciona un periodo', periodos)

# Filtrar los datos según el periodo seleccionado
periodo_filter = resultados_exam[resultados_exam['periodo'] == periodo_seleccionado]

# Sidebar: Buscador para filtrar por nombre
name_searched = st.sidebar.text_input('Buscar por nombre:')

if name_searched:
    name_filtered = periodo_filter[periodo_filter['APELLIDOS Y NOMBRES'].str.contains(name_searched, case=False, na=False)]

    if not name_filtered.empty:
        st.sidebar.write(f'Resultado para la búsqueda: ({len(name_filtered)})')
        st.sidebar.dataframe(name_filtered[['APELLIDOS Y NOMBRES', 'CARRERA (PRIMERA OPCION)', 'PUNTAJE']])
    else:
        st.sidebar.write('No se encontraron resultados para su búsqueda.')

# Sidebar: Mostrar los puntajes más altos junto con su carrera y postulante por periodo
idx_max_PUNTAJE = periodo_filter['PUNTAJE'].idxmax()

if idx_max_PUNTAJE in periodo_filter.index:
    resultado_maximo = periodo_filter.loc[[idx_max_PUNTAJE], ['APELLIDOS Y NOMBRES', 'CARRERA (PRIMERA OPCION)', 'PUNTAJE']]
    st.sidebar.write(f"Postulante con el puntaje más alto en el periodo {periodo_seleccionado}:")
    # Mostrar el texto con formato Markdown y salto de línea
    st.sidebar.markdown('***Postulante:***  \n' + resultado_maximo['APELLIDOS Y NOMBRES'].iloc[0])
    st.sidebar.markdown('***Carrera:***  \n' + resultado_maximo['CARRERA (PRIMERA OPCION)'].iloc[0])
    st.sidebar.markdown('***Puntaje:***  \n' + str(resultado_maximo['PUNTAJE'].iloc[0]))

else:
    st.sidebar.write(f"Índice {idx_max_PUNTAJE} no encontrado en el DataFrame.")


st.title('Informe Integral sobre los Resultados del Examen de Admisión')

st.write('El analisis detallado de los resultados del examen de admision', 
        'proporcion una vision profunda sobre el desempeño de los postulantes',
        'permitiendo identificar tendencias, fortalezas y áreas de mejora.',
        'Este estudio ofrece un interepretacion clara de los datos, brindando informacion',
        'valiosa para optimizar los procesos y estrategias de seleccion.',
        'Ademas, facilita la toma de decisiones informadas para futuras ediciones del examen.'
)
st.write(' ')

st.markdown(
    "<h1 style='text-align: center; font-family: Arial, sans-serif; font-size: 24px;'>Variación de postulantes e ingresantes</h1>",
    unsafe_allow_html=True
)

#seleccionaremos el periodo
periodo_metrics = resultados_exam['periodo'].unique()
periodo_metrics_sb = st.selectbox('Selecciona un periodo: ', periodo_metrics)

# Contenedor para las tarjetas
#armamos un df con el numero de postulantes por periodo y su variacion porcentual
var_periodo = resultados_exam.groupby('periodo')['CODIGO DEL ESTUDIANTE'].count().reset_index()
# Calcular la variación absoluta (diferencia) respecto al periodo anterior
var_periodo['variacion_absoluta'] = var_periodo['CODIGO DEL ESTUDIANTE'].diff().fillna(0)
# Calcular la variación porcentual respecto al periodo anterior
var_periodo['variacion_porcentual'] = var_periodo['CODIGO DEL ESTUDIANTE'].pct_change().fillna(0) * 100

var_ingre = resultados_exam.pivot_table(
     index='periodo',
     columns='OBSERVACION',
     values = 'CODIGO DEL ESTUDIANTE',
     aggfunc='count'
).reset_index()

#eliminamos las columnas innecesarioas, solo queremos ver los ingresados en primera opcion
var_ingre = var_ingre.drop(['ALCANZO VACANTE SEGUNDA OPCION', 'ANULADO', 'AUSENTE', 'NO ALCANZO VACANTE'], 
                           axis = 1)

# Calcular la variación absoluta (diferencia) respecto al periodo anterior
var_ingre['VARIACION ABSOLUTA'] = var_ingre['ALCANZO VACANTE PRIMERA OPCION'].diff().fillna(0)

# Calcular la variación porcentual respecto al periodo anterior
var_ingre['VARIACION PORCENTUAL'] = var_ingre['ALCANZO VACANTE PRIMERA OPCION'].pct_change().fillna(0) * 100


ingresados = resultados_exam.pivot_table(
    index = 'periodo', columns='OBSERVACION', values = 'CODIGO DEL ESTUDIANTE', aggfunc='count'
).fillna(0).reset_index()


ingresados['total_students'] = ingresados['ALCANZO VACANTE PRIMERA OPCION'] + ingresados['ALCANZO VACANTE SEGUNDA OPCION'] + ingresados['ANULADO'] + ingresados['AUSENTE'] + ingresados['NO ALCANZO VACANTE']

ingresados['PORCENTAJE'] = ingresados['ALCANZO VACANTE PRIMERA OPCION'] / ingresados['total_students'] * 100

# Formatea como porcentaje después de ordenar
ingresados['PORCENTAJE'] = ingresados['PORCENTAJE'].apply(lambda x: f'{x:.2f}%')

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
        por_ing = ingresados[ingresados['periodo'] == periodo_metrics_sb]
        st.metric(
             label= 'Numero de ingresantes',
             value= f'{num_ing: ,} ({por_ing['PORCENTAJE'].values[0]})',
             delta = var_ing
        )

st.write(f'De los {num_post} postulantes en el periodo {periodo_metrics_sb}, solo el {por_ing['PORCENTAJE'].values[0]} logró ingresar.') 


st.markdown(
    "<h1 style='text-align: center; font-family: Arial, sans-serif; font-size: 24px;'>Variación de puntajes maximos, minimos y promedios</h1>",
    unsafe_allow_html=True
)


st.write('Conoceremos los puntajes mas importantes de cada periodo de examen de admision',
         'entre ellos el puntaje maximo, puntaje minimo, el puntaje promedio', 
         'para poder alcanzar una vacante en la prestigiosa UNMSM',
         'ademas de sus respectivas carreras',
         'para tener un panorama mas completo para la toma de decisiones.',
         'Además se conocerá la variacion de cada una de las secciones.',

)

solo_ingresantes = resultados_exam[resultados_exam['OBSERVACION'] == 'ALCANZO VACANTE PRIMERA OPCION']

#conseguimos el maximo puntaje de los ingresados
max = solo_ingresantes.groupby('periodo')['PUNTAJE'].max().reset_index()

# Calcular la variación porcentual respecto al periodo anterior
max['variacion (%)'] = max['PUNTAJE'].pct_change().fillna(0) * 100

#conseguimos el minimo puntaje de los ingresados
min = solo_ingresantes.groupby('periodo')['PUNTAJE'].min().reset_index()

# Calcular la variación porcentual respecto al periodo anterior
min['variacion (%)'] = min['PUNTAJE'].pct_change().fillna(0) * 100

#conseguimos el minimo puntaje de los ingresados
mean = solo_ingresantes.groupby('periodo')['PUNTAJE'].mean().round(2).reset_index()

# Calcular la variación porcentual respecto al periodo anterior
mean['variacion (%)'] = mean['PUNTAJE'].pct_change().fillna(0) * 100


#creamos un df seleccionado por el periodo que elegimos en el selectbox

max_min = resultados_exam[(resultados_exam['periodo'] == periodo_metrics_sb) & (resultados_exam['OBSERVACION'] == 'ALCANZO VACANTE PRIMERA OPCION')]

idx_max_score = max_min['PUNTAJE'].idxmax()
idx_min_score = max_min['PUNTAJE'].idxmin()

if idx_max_score in max_min.index and idx_min_score in max_min.index :
    result_max = max_min.loc[[idx_max_score], ['CARRERA (PRIMERA OPCION)', 'PUNTAJE']] 
    result_min = max_min.loc[[idx_min_score], ['CARRERA (PRIMERA OPCION)', 'PUNTAJE']] 

with st.container():
    # Tarjetas en una fila
    k1, k2, k3 = st.columns(3)
    
    with k1:
        max_score = max[max['periodo'] == periodo_metrics_sb]['PUNTAJE'].values[0]
        max_var = max[max['periodo'] == periodo_metrics_sb]['variacion (%)'].values[0]
        var = f'{max_var:.2f}% (resp. al año anterior)'
        st.metric(
             label=f'Puntaje maximo del periodo {periodo_metrics_sb}', 
             value= f'{max_score:,}',
             delta= var
        )

        st.write(f'**Perteneciente a la carrera:** \n{result_max['CARRERA (PRIMERA OPCION)'].values[0]}')

        button_max = st.button('Ver grafico', key = 1)

    with k2:
        min_score = min[min['periodo'] == periodo_metrics_sb]['PUNTAJE'].values[0]
        min_var = min[min['periodo'] == periodo_metrics_sb]['variacion (%)'].values[0]
        var = f'{min_var:.2f}% (resp. al año anterior)'
        st.metric(
             label=f'Puntaje minimo del periodo {periodo_metrics_sb}', 
             value= f'{min_score:,}',
             delta= var
        )
        st.write(f'**Perteneciente a la carrera:** \n{result_min['CARRERA (PRIMERA OPCION)'].values[0]}')

        button_min = st.button('Ver grafico', key = 2)

    with k3:
        mean_score = mean[mean['periodo'] == periodo_metrics_sb]['PUNTAJE'].values[0]
        mean_var = mean[mean['periodo'] == periodo_metrics_sb]['variacion (%)'].values[0]
        var = f'{mean_var:.2f}% (resp. al año anterior)'
        st.metric(
             label=f'Puntaje meanimo del periodo {periodo_metrics_sb}', 
             value= f'{mean_score:,}',
             delta= var
        )
        st.write(f'**Promedio en general:** \nPara el examen {periodo_metrics_sb}')
        button_mean = st.button('Ver grafico')        
st.write(f'El puntaje máximo alcanzado para el periodo {periodo_metrics_sb} fue de {max_score}, mientras que el mínimo para ingresar fue de {min_score}. El puntaje promedio de los ingresantes fue de {mean_score}.')


if button_max: 
    # Asegurarse de que 'max' sea un DataFrame y tenga las columnas necesarias
    if isinstance(max, pd.DataFrame) and 'periodo' in max.columns and 'PUNTAJE' in max.columns:
        # Crear el gráfico de barras
        fig = px.bar(
            max, 
            x='periodo', 
            y='PUNTAJE', 
            title='Puntaje Maximo de cada periodo', 
            labels={'PUNTAJE': 'Puntaje', 'periodo': 'Periodo'},
            color = 'PUNTAJE',
            color_continuous_scale="Reds"
        )
        
        # Mejorar la visualización
        fig.update_traces(texttemplate=f'%{{y:,.2f}}', textposition='outside')  # Mostrar valores en las barras
        fig.update_layout(
            xaxis_title='Periodo',
            yaxis_title='Puntaje',
            title_x=0.5, 
            coloraxis_colorbar = dict(title='Puntaje')
            # Centrar el título
        )
        
        # Mostrar el gráfico en Streamlit
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("El DataFrame 'max' no es válido o no contiene las columnas requeridas.")

        
if button_min: 
    # Asegurarse de que 'max' sea un DataFrame y tenga las columnas necesarias
    if isinstance(min, pd.DataFrame) and 'periodo' in min.columns and 'PUNTAJE' in min.columns:
        # Crear el gráfico de barras
        fig = px.bar(
            min, 
            x='periodo', 
            y='PUNTAJE', 
            title='Puntaje por Periodo', 
            labels={'PUNTAJE': 'Puntaje', 'periodo': 'Periodo'},
            color = 'PUNTAJE',
            color_continuous_scale="Reds"
        )
        
        # Mejorar la visualización
        fig.update_traces(texttemplate='%{y:,.2f}', textposition='outside')  # Mostrar valores en las barras
        fig.update_layout(
            xaxis_title='Periodo',
            yaxis_title='Puntaje',
            title_x=0.5, 
            coloraxis_colorbar = dict(title='Puntaje')
            # Centrar el título
        )
        
        # Mostrar el gráfico en Streamlit
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("El DataFrame 'min' no es válido o no contiene las columnas requeridas.")



if button_mean: 
    # Asegurarse de que 'max' sea un DataFrame y tenga las columnas necesarias
    if isinstance(mean, pd.DataFrame) and 'periodo' in mean.columns and 'PUNTAJE' in mean.columns:
        # Crear el gráfico de barras
        fig = px.bar(
            mean, 
            x='periodo', 
            y='PUNTAJE', 
            title='Puntaje por Periodo', 
            labels={'PUNTAJE': 'Puntaje', 'periodo': 'Periodo'},
            color = 'PUNTAJE',
            color_continuous_scale="Reds"            
        )
        
        # Mejorar la visualización
        fig.update_traces(texttemplate='%{y:,.2f}', textposition='outside')  # Mostrar valores en las barras
        fig.update_layout(
            xaxis_title='Periodo',
            yaxis_title='Puntaje',
            title_x=0.5, 
            coloraxis_colorbar = dict(title='Puntaje')
            # Centrar el título
        )
        
        # Mostrar el gráfico en Streamlit
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("El DataFrame 'mean' no es válido o no contiene las columnas requeridas.")

st.markdown(
    "<h1 style='text-align: center; font-family: Arial, sans-serif; font-size: 24px;'>Complejidad de ingreso por área</h1>",
    unsafe_allow_html=True
)

# #filtramos los valores de los periodos
# areas_periodo = resultados_exam['periodo'].unique()
# areas_periodo_sb = st.selectbox('Escoge un periodo', areas_periodo)
# areas_periodo_filtered = resultados_exam[resultados_exam['periodo'] == areas_periodo_sb]

competencia_areas = resultados_exam.pivot_table(
    index = ['periodo', 'CODIGO DE AREA'], columns = 'OBSERVACION', values='CODIGO DEL ESTUDIANTE', aggfunc= 'count'
).fillna(0).reset_index()

#ccreamos una fila con el total de postulanes sumando todas las observaciones
competencia_areas['TOTAL POSTULANTES'] = (
      competencia_areas.get('ALCANZO VACANTE PRIMERA OPCION', 0) 
      + competencia_areas.get('ALCANZO VACANTE SEGUNDA OPCION', 0)
      + competencia_areas.get('ANULADO', 0)
      + competencia_areas.get('AUSENTE', 0)
      + competencia_areas.get('NO ALCANZO VACANTE', 0)
)

#borramos las columnas que no nos sirve porque solo queremos ver los que ingresaron con primera opcion
competencia_areas = competencia_areas[
    ['periodo', 'CODIGO DE AREA','ALCANZO VACANTE PRIMERA OPCION', 'TOTAL POSTULANTES']
].dropna(axis = 1, how = 'all')

competencia_areas['proportion'] = ((
      competencia_areas['ALCANZO VACANTE PRIMERA OPCION']

) / competencia_areas['TOTAL POSTULANTES'])

# # Ordena los valores numéricos
competencia_areas = competencia_areas.sort_values('proportion').reset_index()

ponderado_mean = competencia_areas.groupby('CODIGO DE AREA').agg(
    {
        'TOTAL POSTULANTES':'sum',
        'ALCANZO VACANTE PRIMERA OPCION': 'sum'
    }
).reset_index()

ponderado_mean['ponderado'] = ponderado_mean ['ALCANZO VACANTE PRIMERA OPCION'] / ponderado_mean ['TOTAL POSTULANTES']

# Crear la gráfica con Plotly Express
fig = px.scatter(
    ponderado_mean, 
    x="ponderado", 
    y = 'TOTAL POSTULANTES',
    color="TOTAL POSTULANTES", 
    size = 'ALCANZO VACANTE PRIMERA OPCION',
    color_continuous_scale= 'Inferno',
    title=f"Areas mas complejas para alcanzar una vacante",

    labels={
        "periodo": "Periodo",
        "ALCANZO VACANTE PRIMERA OPCION": "Cantidad de ingresantes",
        "CODIGO DE AREA": "Área"
    },
    hover_data={'CODIGO DE AREA':True}
)

# fig.update_traces(mode="lines+markers", line_shape="spline")  # Suavizar líneas y mantener marcadores

# Configurar el rango del eje X
# Expandir límites automáticamente y agregar margen
fig.update_xaxes(
    range=None,  # Habilitar rango dinámico
    autorange=True,  # Expandir los límites automáticamente
    title=dict(text="Proporción")  # Etiqueta personalizada
)


# Mostrar la gráfica en Streamlit
st.plotly_chart(fig)

with st.container():
    # Tarjetas en una fila
    a1, a2, a3 = st.columns(3)

    with a1:
        st.subheader('Áreas más competitivas')
        st.write('Área A y Área C son las más competitivas:')
        st.write('Área A tiene el mayor número de postulantes (36,292), pero la proporción más baja (0.0464). Esto indica que, aunque hay muchos interesados, pocos logran obtener una vacante en su primera opción.')
        st.write('Área C también tiene una proporción baja (0.0819), aunque con menos postulantes en comparación con el área A (36,292 postulantes).')

    with a2:
        st.subheader('Áreas intermedias competitivas')
        st.write('Área E y Área D son medianamente competitivas:')
        st.write('Área E y Área D presentan proporciones más altas (0.1269 y 0.1637, respectivamente). Esto sugiere que aunque siguen siendo competitivas, ofrecen mayores probabilidades de éxito en comparación con A y C.')
        st.write('Área D tiene una ventaja adicional al tener menos postulantes (17,858), lo que puede significar una menor competencia en términos absolutos.')

    with a3:
        st.subheader('Área menos competitiva')
        st.write('Area B la area menos competitiva:')
        st.write('Área B tiene el menor número de postulantes (3,050) y la proporción más alta (0.2866). Esto indica que los postulantes en esta área tienen una mayor probabilidad de obtener una vacante en su primera opción.')
        



st.markdown(
    "<h1 style='text-align: center; font-family: Arial, sans-serif; font-size: 24px;'>Ranking de carreras más difíciles de ingresar</h1>",
    unsafe_allow_html=True)

st.write(
    """
    El **Ranking de carreras más difíciles de ingresar** presenta un análisis basado en los resultados 
    de los últimos cuatro exámenes de admisión, destacando las opciones académicas con mayor nivel 
    de competencia. Este ranking ofrece dos alternativas: explorar las carreras de manera general 
    o visualizar los resultados por áreas específicas. De esta forma, los aspirantes pueden identificar 
    las carreras más demandadas y desafiantes, considerando tanto el panorama general como la 
    competitividad dentro de cada área.
    """
)



# general = st.button('TODAS LAS CARRERAS', key = 'general', use_container_width=True)

# if general:

examanes = resultados_exam['periodo'].unique()

examenes_slider = st.select_slider('Selecciona un examen', options=examanes)

examanes_filtered = resultados_exam[resultados_exam['periodo'] == examenes_slider]

competencia_career = examanes_filtered.pivot_table(
    index = ['periodo', 'CARRERA (PRIMERA OPCION)', 'CODIGO DE AREA'], columns = 'OBSERVACION', values='CODIGO DEL ESTUDIANTE', aggfunc= 'count'
).fillna(0).reset_index()


# #ccreamos una fila con el total de postulanes sumando todas las observaciones
competencia_career['TOTAL POSTULANTES'] = (
    competencia_career.get('ALCANZO VACANTE PRIMERA OPCION', 0) 
    + competencia_career.get('ALCANZO VACANTE SEGUNDA OPCION', 0)
    + competencia_career.get('ANULADO', 0)
    + competencia_career.get('AUSENTE', 0)
    + competencia_career.get('NO ALCANZO VACANTE', 0)
)

# #borramos las columnas que no nos sirve porque solo queremos ver los que ingresaron con primera opcion    
competencia_career = competencia_career[
    ['periodo', 'CARRERA (PRIMERA OPCION)','ALCANZO VACANTE PRIMERA OPCION', 'TOTAL POSTULANTES']
].dropna(axis = 1, how = 'all')

competencia_career['proportion'] = ((
    competencia_career['ALCANZO VACANTE PRIMERA OPCION']

) / competencia_career['TOTAL POSTULANTES'])

# # # Ordena los valores numéricos
competencia_career = competencia_career.sort_values('proportion').reset_index()

ponderado_career_mean = competencia_career.groupby('CARRERA (PRIMERA OPCION)').agg(
    {
        'TOTAL POSTULANTES':'sum',
        'ALCANZO VACANTE PRIMERA OPCION': 'sum'
    }
).reset_index()

ponderado_career_mean['ponderado'] = (ponderado_career_mean ['ALCANZO VACANTE PRIMERA OPCION'] / 
ponderado_career_mean ['TOTAL POSTULANTES']).sort_values(ascending = False)

ponderado_career_mean = ponderado_career_mean.sort_values(by='ponderado', ascending=False)

# Crear la gráfica con Plotly Express
figE = px.scatter(
    ponderado_career_mean, 
    x="ponderado", 
    y = 'TOTAL POSTULANTES',
    color="ponderado", 
    size = 'ALCANZO VACANTE PRIMERA OPCION',
    color_continuous_scale= 'Inferno',
    title=f"Carreras mas complejas para alcanzar una vacante en el periodo {examenes_slider}",
    hover_data={'CARRERA (PRIMERA OPCION)': True}
)


# Configurar el rango del eje X
# Expandir límites automáticamente y agregar margen
fig.update_xaxes(
    range=None,  # Habilitar rango dinámico
    autorange=True,  # Expandir los límites automáticamente
    title=dict(text="Proporción")  # Etiqueta personalizada
)

st.plotly_chart(figE)

st.divider()
st.title('Carreras mas complejas por area')
st.write(
    """
        En esta seccion se analizará las carreras mas complejas a las mas accesibles por periodo
        de cada area del examen de admision.
    """
)
# por_area = st.button('POR AREA', key = 'area', use_container_width=True)    

# if por_area:

examanes_area = resultados_exam['periodo'].unique()

examenes_area_slider = st.select_slider('Selecciona un examen', options=examanes_area, key = 'area')

examanes_area_filtered = resultados_exam[resultados_exam['periodo'] == examenes_area_slider]

for area in examanes_area_filtered['CODIGO DE AREA'].unique():
        filtered_area = examanes_area_filtered[examanes_area_filtered['CODIGO DE AREA'] == area]
        competencia_career = filtered_area.pivot_table(
            index = ['periodo', 'CARRERA (PRIMERA OPCION)', 'CODIGO DE AREA'], columns = 'OBSERVACION', values='CODIGO DEL ESTUDIANTE', aggfunc= 'count'
        ).fillna(0).reset_index()
        
        # #ccreamos una fila con el total de postulanes sumando todas las observaciones
        competencia_career['TOTAL POSTULANTES'] = (
            competencia_career.get('ALCANZO VACANTE PRIMERA OPCION', 0) 
            + competencia_career.get('ALCANZO VACANTE SEGUNDA OPCION', 0)
            + competencia_career.get('ANULADO', 0)
            + competencia_career.get('AUSENTE', 0)
            + competencia_career.get('NO ALCANZO VACANTE', 0)
        )



        # #borramos las columnas que no nos sirve porque solo queremos ver los que ingresaron con primera opcion    
        competencia_career = competencia_career[
            ['periodo', 'CARRERA (PRIMERA OPCION)','ALCANZO VACANTE PRIMERA OPCION', 'TOTAL POSTULANTES']
        ].dropna(axis = 1, how = 'all')



        competencia_career['proportion'] = ((
            competencia_career['ALCANZO VACANTE PRIMERA OPCION']

        ) / competencia_career['TOTAL POSTULANTES'])



        # # # Ordena los valores numéricos
        competencia_career = competencia_career.sort_values('proportion').reset_index()

        ponderado_career_mean = competencia_career.groupby('CARRERA (PRIMERA OPCION)').agg(
            {
                'TOTAL POSTULANTES':'sum',
                'ALCANZO VACANTE PRIMERA OPCION': 'sum'
            }
        ).reset_index()

        ponderado_career_mean['ponderado'] = (ponderado_career_mean ['ALCANZO VACANTE PRIMERA OPCION'] / 
        ponderado_career_mean ['TOTAL POSTULANTES']).sort_values(ascending = False)

        ponderado_career_mean = ponderado_career_mean.sort_values(by='ponderado')
        
        # Crear la gráfica con Plotly Express
        figal = px.scatter(
            ponderado_career_mean, 
            x="ponderado", 
            y = 'TOTAL POSTULANTES',
            color="ponderado", 
            size = 'ALCANZO VACANTE PRIMERA OPCION',
            color_continuous_scale= 'Inferno',
            title=f"Carreras mas complejas para alcanzar una vacante en el area {area}",
            hover_data={'CARRERA (PRIMERA OPCION)': True}

        )

        # fig.update_traces(mode="lines+markers", line_shape="spline")  # Suavizar líneas y mantener marcadores

        # Configurar el rango del eje X
        # Expandir límites automáticamente y agregar margen
        fig.update_xaxes(
            range=None,  # Habilitar rango dinámico
            autorange=True,  # Expandir los límites automáticamente
            title=dict(text="Proporción")  # Etiqueta personalizada
        )

        st.plotly_chart(figal)


        st.write(
            f"""  
            Las 2 carreras con mayor dificultad para alcanzar una vacante para el area {area} son:
            {ponderado_career_mean['CARRERA (PRIMERA OPCION)'].iloc[0]} ({round(ponderado_career_mean['ponderado'].iloc[0] * 100,2)}%) , y {ponderado_career_mean['CARRERA (PRIMERA OPCION)'].iloc[1]}
            ({round(ponderado_career_mean['ponderado'].iloc[1] * 100,2)}%)

                    """
        )
        

    