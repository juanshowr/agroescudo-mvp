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
        # Convertimos el GeoJSON a WKT para que Copernicus lo entienda
        geometria = shape(st.session_state["poligono_geojson"]["geometry"])
        wkt_area = geometria.wkt
        
        st.write(f"**Geometría a auditar:** `{wkt_area[:100]}...`")
        
        if modo_demo:
            st.success("✅ Conexión M2M simulada exitosa. Generando expediente...")
            try:
                st.image("NDVI_Prueba_Oficial.png", caption="Auditoría Satelital AgroEscudo 360°", use_column_width=True)
                st.info("💡 Token de Legalidad emitido y adjuntado al expediente.")
            except:
                st.error("Error cargando la imagen demo. Sube 'NDVI_Prueba_Oficial.png' a GitHub.")
        else:
            if not USUARIO or not CONTRASENA:
                st.error("⚠️ Ingresa credenciales reales de Copernicus arriba a la izquierda.")
            else:
                with st.spinner("Conectando con la constelación Sentinel-2..."):
                    st.warning("⚠️ Iniciando petición OData real con el polígono dibujado.")
                    # Aquí va la lógica real de descarga (requests.get...) que ya probaron.
else:
    st.info("👆 Por favor, dibuja un polígono en el mapa o ingresa coordenadas para habilitar la auditoría.")
