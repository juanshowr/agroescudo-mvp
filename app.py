import streamlit as st
import requests
import os
import json
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import shape, box
import folium
from folium.plugins import Draw, LocateControl
from streamlit_folium import st_folium

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="AgroEscudo 360° - Plataforma", page_icon="🛰️", layout="wide")

st.title("🛰️ AgroEscudo 360° - Plataforma de Auditoría EUDR")
st.markdown("Georreferenciación en campo y conexión M2M con Copernicus Data Space.")

# --- INICIALIZAR VARIABLES DE SESIÓN ---
if "poligono_geojson" not in st.session_state:
    st.session_state["poligono_geojson"] = None

# --- BARRA LATERAL (CONFIGURACIÓN) ---
st.sidebar.header("⚙️ Configuración M2M")
USUARIO = st.sidebar.text_input("Usuario Copernicus", type="password")
CONTRASENA = st.sidebar.text_input("Contraseña Copernicus", type="password")
st.sidebar.markdown("---")
modo_demo = st.sidebar.checkbox("🚀 Usar Modo Demo Rápido", value=True)

# --- PANEL CENTRAL: PESTAÑAS DE ENTRADA DE DATOS ---
st.subheader("1. Captura de Datos del Predio")
tab1, tab2, tab3 = st.tabs(["🗺️ Dibujar en Mapa / GPS", "✍️ Ingreso Manual", "📁 Subir Archivo"])

with tab1:
    st.markdown("Usa las herramientas de la izquierda del mapa para dibujar un polígono. Si estás en campo, usa el botón de **Ubicación (GPS)** debajo de las herramientas de zoom para centrar el mapa en tu posición actual.")
    
    # Crear el mapa base centrado en Colombia
    m = folium.Map(location=[4.5709, -74.2973], zoom_start=5)
    
    # 1. Herramienta de GPS (Geolocalización)
    LocateControl(auto_start=False).add_to(m)
    
    # 2. Herramienta de Dibujo
    draw_options = {'polyline': False, 'rectangle': True, 'circle': False, 'marker': True, 'circlemarker': False, 'polygon': True}
    Draw(export=True, draw_options=draw_options).add_to(m)
    
    # Mostrar el mapa en Streamlit y capturar lo que el usuario dibuja
    output_mapa = st_folium(m, width=1000, height=500)
    
    # Si el usuario dibuja algo, lo guardamos
    if output_mapa["last_active_drawing"]:
        st.session_state["poligono_geojson"] = output_mapa["last_active_drawing"]
        st.success("✅ Polígono/Punto capturado desde el mapa.")

with tab2:
    st.markdown("Ingresa las coordenadas en formato GeoJSON o los límites manuales (Bounding Box):")
    texto_geojson = st.text_area("Pega aquí tu código GeoJSON (opcional):", height=150)
    
    col1, col2 = st.columns(2)
    with col1:
        min_lon = st.number_input("Longitud Mínima", value=-74.2000, format="%.4f")
        min_lat = st.number_input("Latitud Mínima", value=10.4000, format="%.4f")
    with col2:
        max_lon = st.number_input("Longitud Máxima", value=-74.0000, format="%.4f")
        max_lat = st.number_input("Latitud Máxima", value=10.6000, format="%.4f")
        
    if st.button("Guardar Coordenadas Manuales"):
        if texto_geojson:
            try:
                st.session_state["poligono_geojson"] = json.loads(texto_geojson)
                st.success("✅ GeoJSON manual cargado.")
            except:
                st.error("❌ El formato GeoJSON es inválido.")
        else:
            # Crear un polígono a partir del Bounding Box
            bbox_poligono = box(min_lon, min_lat, max_lon, max_lat)
            st.session_state["poligono_geojson"] = {
                "type": "Feature",
                "geometry": json.loads(json.dumps(bbox_poligono.__geo_interface__))
            }
            st.success("✅ Coordenadas manuales guardadas.")

with tab3:
    st.markdown("Próximamente: Carga de archivos .shp y .kml.")

# --- SECCIÓN DE AUDITORÍA Y DESCARGA ---
st.markdown("---")
st.subheader("2. Auditoría EUDR y Exportación")

if st.session_state["poligono_geojson"]:
    # 1. BOTÓN PARA DESCARGAR EL GEOJSON
    geojson_str = json.dumps(st.session_state["poligono_geojson"], indent=2)
    st.download_button(
        label="📥 Descargar Polígono (GeoJSON)",
        data=geojson_str,
        file_name="finca_auditada.geojson",
        mime="application/json",
        type="primary"
    )
    
    # 2. BOTÓN DE AUDITORÍA COPERNICUS
    if st.button("🔍 Ejecutar Auditoría Satelital Copernicus"):
        
        # --- EL PUENTE MÁGICO: De GeoJSON a WKT ---
        geometria = shape(st.session_state["poligono_geojson"]["geometry"])
        wkt_area = geometria.wkt 
        
        st.write(f"**Geometría enviada a Europa:** `{wkt_area[:80]}...`")
        
        if modo_demo:
            st.success("✅ Conexión M2M simulada exitosa. Generando expediente...")
            try:
                st.image("NDVI_Prueba_Oficial.png", caption="Auditoría Satelital AgroEscudo 360° - Línea Base 2020", use_column_width=True)
                st.info("💡 Token de Legalidad emitido y adjuntado al expediente DDS.")
            except:
                st.error("Error cargando la imagen demo. Asegúrate de que 'NDVI_Prueba_Oficial.png' está en GitHub.")
        else:
            if not USUARIO or not CONTRASENA:
                st.error("⚠️ Ingresa credenciales reales de Copernicus arriba a la izquierda.")
            else:
                with st.spinner("📡 Buscando en los archivos de la Agencia Espacial Europea (Dic 2020)..."):
                    try:
                        # 1. BÚSQUEDA EN COPERNICUS (Usando el polígono dibujado)
                        url = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
                        query = f"?$filter=Collection/Name eq 'SENTINEL-2' and Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq 'S2MSI2A') and ContentDate/Start gt 2020-11-01T00:00:00.000Z and ContentDate/Start lt 2021-01-31T23:59:59.000Z and OData.CSC.Intersects(area=geography'SRID=4326;{wkt_area}') and Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value lt 80.0)"
                        
                        response = requests.get(url + query)
                        response.raise_for_status()
                        resultados = response.json().get('value', [])
                        
                        if not resultados:
                            st.warning("No se encontraron imágenes sin nubes para esa zona exacta en la línea base (Dic 2020).")
                            st.stop()
                        
                        mejor_imagen = resultados[0]
                        imagen_id = mejor_imagen['Id']
                        st.success(f"✅ Satélite encontrado. ID: {imagen_id}. Solicitando pista de descarga...")
                        
                        # 2. AUTENTICACIÓN Y DESCARGA
                        token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
                        token_data = {"client_id": "cdse-public", "grant_type": "password", "username": USUARIO, "password": CONTRASENA}
                        
                        token_response = requests.post(token_url, data=token_data)
                        token_response.raise_for_status()
                        token = token_response.json().get("access_token")
                        
                        st.info("⬇️ Descargando bandas espectrales (~1GB). No cierres la pestaña...")
                        download_url = f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products({imagen_id})/$value"
                        ruta_zip = "temp_sat.zip"
                        
                        respuesta_descarga = requests.get(download_url, headers={"Authorization": f"Bearer {token}"}, allow_redirects=False)
                        while respuesta_descarga.is_redirect:
                            url_redireccion = respuesta_descarga.headers['Location']
                            respuesta_descarga = requests.get(url_redireccion, headers={"Authorization": f"Bearer {token}"}, allow_redirects=False, stream=True)
                        
                        with open(ruta_zip, 'wb') as f:
                            for chunk in respuesta_descarga.iter_content(chunk_size=8192):
                                if chunk: f.write(chunk)
                        
                        # 3. PROCESAMIENTO NDVI
                        st.info("🧮 Ejecutando Motor Analítico (Calculando NDVI)...")
                        directorio_extraccion = "temp_extract"
                        os.makedirs(directorio_extraccion, exist_ok=True)
                        with zipfile.ZipFile(ruta_zip, 'r') as zip_ref:
                            zip_ref.extractall(directorio_extraccion)
                        
                        archivos_jp2 = glob.glob(f"{directorio_extraccion}/**/*.jp2", recursive=True)
                        ruta_b04 = next((f for f in archivos_jp2 if "B04_10m" in f), None)
                        ruta_b08 = next((f for f in archivos_jp2 if "B08_10m" in f), None)
                        
                        if ruta_b04 and ruta_b08:
                            escala = 0.20 # Reducimos escala para no colapsar la RAM del servidor
                            with rasterio.open(ruta_b04) as src_red:
                                red = src_red.read(1, out_shape=(int(src_red.height * escala), int(src_red.width * escala)), resampling=Resampling.bilinear).astype('float32')
                            with rasterio.open(ruta_b08) as src_nir:
                                nir = src_nir.read(1, out_shape=(int(src_red.height * escala), int(src_red.width * escala)), resampling=Resampling.bilinear).astype('float32')
                            
                            np.seterr(divide='ignore', invalid='ignore')
                            ndvi = np.where((nir + red) == 0., 0, (nir - red) / (nir + red))
                            
                            st.success("🎉 ¡Auditoría Completada Exitosamente!")
                            fig, ax = plt.subplots(figsize=(10, 8))
                            cax = ax.imshow(ndvi, cmap='RdYlGn', vmin=-0.2, vmax=0.9)
                            fig.colorbar(cax, label='Índice NDVI', shrink=0.8)
                            ax.set_title("Auditoría Satelital AgroEscudo 360° - Línea Base 2020", fontsize=14)
                            ax.axis('off')
                            
                            st.pyplot(fig) 
                            
                        else:
                            st.error("No se encontraron las bandas a 10m en el archivo descargado.")

                    except Exception as e:
                        st.error(f"❌ Error en la conexión M2M: {e}")

else:
    st.info("👆 Por favor, dibuja un polígono en el mapa o ingresa coordenadas para habilitar la auditoría.")
