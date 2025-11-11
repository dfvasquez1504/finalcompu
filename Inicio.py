import pandas as pd
import streamlit as st
from PIL import Image
import numpy as np
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Análisis de Luminosidad en el Centro de Montería",
    page_icon="🔦",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title('📊 Análisis de datos de Luminosidad en el centro de Montería')
st.markdown("""
    Esta aplicación permite analizar datos de sensores
    recolectados de luz en varios lugares del centro de Montería.
""")

# Create map data for EAFIT
eafit_location = pd.DataFrame({
    'lat': [8.75081],
    'lon': [-75.87823],
    'location': ['Centro de Montería']
})

# Display map
st.subheader("📍 Ubicación de los Sensores de Luz - Centro de Montería")
st.map(eafit_location, zoom=15)

# File uploader
uploaded_file = st.file_uploader('Seleccione archivo CSV', type=['csv'])

if uploaded_file is not None:
    try:
        # Load and process data
        df1 = pd.read_csv(uploaded_file)
        
        # Renombrar la columna a 'variable'
        # Asume que la primera columna después de 'Time' es la variable de interés
        # O busca una columna específica y la renombra
        if 'Time' in df1.columns:
            # Si existe Time, renombrar la otra columna a 'variable'
            other_columns = [col for col in df1.columns if col != 'Time']
            if len(other_columns) > 0:
                df1 = df1.rename(columns={other_columns[0]: 'variable'})
        else:
            # Si no existe Time, renombrar la primera columna a 'variable'
            df1 = df1.rename(columns={df1.columns[0]: 'variable'})
        
        # Procesar columna de tiempo si existe
        if 'Time' in df1.columns:
            df1['Time'] = pd.to_datetime(df1['Time'])
            df1 = df1.set_index('Time')

        # Create tabs for different analyses
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Visualización", "📊 Estadísticas", "🔍 Filtros", "🗺️ Información del Sitio"])

        with tab1:
            st.subheader('Visualización de Datos')
            
            # Chart type selector
            chart_type = st.selectbox(
                "Seleccione tipo de gráfico",
                ["Línea", "Área", "Barra"]
            )
            
            # Create plot based on selection
            if chart_type == "Línea":
                st.line_chart(df1["variable"])
            elif chart_type == "Área":
                st.area_chart(df1["variable"])
            else:
                st.bar_chart(df1["variable"])

            # Raw data display with toggle
            if st.checkbox('Mostrar datos crudos'):
                st.write(df1)

        with tab2:
            st.subheader('Análisis Estadístico')
            
            # Statistical summary
            stats_df = df1["variable"].describe()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.dataframe(stats_df)
            
            with col2:
                # Additional statistics
                st.metric("Valor Promedio", f"{stats_df['mean']:.2f}")
                st.metric("Valor Máximo", f"{stats_df['max']:.2f}")
                st.metric("Valor Mínimo", f"{stats_df['min']:.2f}")
                st.metric("Desviación Estándar", f"{stats_df['std']:.2f}")

        with tab3:
            st.subheader('Filtros de Datos')
            
            # Calcular rango de valores
            min_value = float(df1["variable"].min())
            max_value = float(df1["variable"].max())
            mean_value = float(df1["variable"].mean())
            
            # Verificar si hay variación en los datos
            if min_value == max_value:
                st.warning(f"⚠️ Todos los valores en el dataset son iguales: {min_value:.2f}")
                st.info("No es posible aplicar filtros cuando no hay variación en los datos.")
                st.dataframe(df1)
            else:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Minimum value filter
                    min_val = st.slider(
                        'Valor mínimo',
                        min_value,
                        max_value,
                        mean_value,
                        key="min_val"
                    )
                    
                    filtrado_df_min = df1[df1["variable"] > min_val]
                    st.write(f"Registros con valor superior a {min_val:.2f}:")
                    st.dataframe(filtrado_df_min)
                    
                with col2:
                    # Maximum value filter
                    max_val = st.slider(
                        'Valor máximo',
                        min_value,
                        max_value,
                        mean_value,
                        key="max_val"
                    )
                    
                    filtrado_df_max = df1[df1["variable"] < max_val]
                    st.write(f"Registros con valor inferior a {max_val:.2f}:")
                    st.dataframe(filtrado_df_max)

                # Download filtered data
                if st.button('Descargar datos filtrados'):
                    csv = filtrado_df_min.to_csv().encode('utf-8')
                    st.download_button(
                        label="Descargar CSV",
                        data=csv,
                        file_name='datos_filtrados.csv',
                        mime='text/csv',
                    )

        with tab4:
            st.subheader("Información del Sitio de Medición")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("### Ubicación del Sensor")
                st.write("**Universidad EAFIT**")
                st.write("- Latitud: 6.2006")
                st.write("- Longitud: -75.5783")
                st.write("- Altitud: ~1,495 metros sobre el nivel del mar")
            
            with col2:
                st.write("### Detalles del Sensor")
                st.write("- Tipo: ESP32")
                st.write("- Variable medida: Según configuración del sensor")
                st.write("- Frecuencia de medición: Según configuración")
                st.write("- Ubicación: Campus universitario")

    except Exception as e:
        st.error(f'Error al procesar el archivo: {str(e)}')
        st.info('Asegúrese de que el archivo CSV tenga al menos una columna con datos.')
else:
    st.warning('Por favor, cargue un archivo CSV para comenzar el análisis.')
    
# Footer
st.markdown("""
    ---
    Desarrollado para el análisis de datos de sensores urbanos.
    Ubicación: Universidad EAFIT, Medellín, Colombia
""")
