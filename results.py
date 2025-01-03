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
        var = f'{max_var:.2f}%'
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
        var = f'{min_var:.2f}%'
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
        var = f'{mean_var:.2f}%'
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
            title='Puntaje por Periodo', 
            labels={'PUNTAJE': 'Puntaje', 'periodo': 'Periodo'},
            color = 'PUNTAJE',
            color_continuous_scale= 'Cividis'

            
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
            color_continuous_scale= 'Cividis'

            
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
            color_continuous_scale= 'Cividis'

            
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
