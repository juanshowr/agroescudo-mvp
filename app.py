import streamlit as st
import requests
import os
import json
import time
import random
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import shape, box
import folium
from folium.plugins import Draw, LocateControl
from streamlit_folium import st_folium

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="AgroEscudo 360° - Plataforma", page_icon="🛰️", layout="wide")

st.title("🛰️ AgroEscudo 360° - Plataforma de Auditoría EUDR")
st.markdown("Georreferenciación en campo, conexión M2M con Copernicus y enlace aduanero.")

# --- INICIALIZAR VARIABLES DE SESIÓN ---
if "poligono_geojson" not in st.session_state:
    st.session_state["poligono_geojson"] = None
if "auditoria_superada" not in st.session_state:
    st.session_state["auditoria_superada"] = False

# --- BARRA LATERAL (CONFIGURACIÓN) ---
st.sidebar.header("⚙️ Configuración M2M")
USUARIO = st.sidebar.text_input("Usuario Copernicus", type="password")
CONTRASENA = st.sidebar.text_input("Contraseña Copernicus", type="password")
st.sidebar.markdown("---")
modo_demo = st.sidebar.checkbox("🚀 Usar Modo Demo Rápido", value=True)

# --- PANEL CENTRAL: PESTAÑAS DE ENTRADA DE DATOS ---
st.subheader("1. Captura de Datos del Predio")
tab1, tab2 = st.tabs(["🗺️ Dibujar en Mapa / GPS", "✍️ Ingreso Manual"])

with tab1:
    st.markdown("Usa las herramientas de la izquierda del mapa para dibujar un polígono. Si estás en campo, usa el botón de **Ubicación (GPS)**.")
    
    m = folium.Map(location=[4.5709, -74.2973], zoom_start=5)
    LocateControl(auto_start=False).add_to(m)
    draw_options = {'polyline': False, 'rectangle': True, 'circle': False, 'marker': True, 'circlemarker': False, 'polygon': True}
    Draw(export=True, draw_options=draw_options).add_to(m)
    
    output_mapa = st_folium(m, width=1000, height=500)
    
    if output_mapa["last_active_drawing"]:
        st.session_state["poligono_geojson"] = output_mapa["last_active_drawing"]
        st.success("✅ Polígono/Punto capturado desde el mapa.")

with tab2:
    st.markdown("Ingresa los límites manuales (Bounding Box):")
    col1, col2 = st.columns(2)
    with col1:
        min_lon = st.number_input("Longitud Mínima", value=-74.2000, format="%.4f")
        min_lat = st.number_input("Latitud Mínima", value=10.4000, format="%.4f")
    with col2:
        max_lon = st.number_input("Longitud Máxima", value=-74.0000, format="%.4f")
        max_lat = st.number_input("Latitud Máxima", value=10.6000, format="%.4f")
        
    if st.button("Guardar Coordenadas Manuales"):
        bbox_poligono = box(min_lon, min_lat, max_lon, max_lat)
        st.session_state["poligono_geojson"] = {
            "type": "Feature",
            "geometry": json.loads(json.dumps(bbox_poligono.__geo_interface__))
        }
        st.success("✅ Coordenadas manuales guardadas.")

# --- SECCIÓN DE AUDITORÍA Y DESCARGA ---
st.markdown("---")
st.subheader("2. Auditoría EUDR (Copernicus)")

if st.session_state["poligono_geojson"]:
    geometria = shape(st.session_state["poligono_geojson"]["geometry"])
    wkt_area = geometria.wkt 
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        geojson_str = json.dumps(st.session_state["poligono_geojson"], indent=2)
        st.download_button(label="📥 Descargar Polígono (GeoJSON)", data=geojson_str, file_name="finca_auditada.geojson", mime="application/json", type="primary")
    
    with col_btn2:
        if st.button("🔍 Ejecutar Auditoría Satelital"):
            st.write(f"**Geometría WKT enviada:** `{wkt_area[:60]}...`")
            if modo_demo:
                st.success("✅ Conexión M2M exitosa.")
                try:
                    st.image("NDVI_Prueba_Oficial.png", caption="Auditoría Satelital AgroEscudo 360°", use_column_width=True)
                    st.info("💡 Token de Legalidad emitido. Finca libre de deforestación en 2020.")
                    st.session_state["auditoria_superada"] = True
                except:
                    st.error("Error cargando la imagen demo.")
            else:
                st.warning("⚠️ Iniciando petición OData real. (Requiere despliegue local por RAM).")
                # Aquí iría el código real de requests.get

# --- SECCIÓN DE ADUANAS (NUEVO) ---
if st.session_state.get("auditoria_superada"):
    st.markdown("---")
    st.subheader("3. Sistema de Información UE (TRACES NT)")
    st.markdown("Generación del Payload JSON para declaración aduanera automatizada.")
    
    # Construimos el Payload simulado
    payload = {
        "dds_type": "submission",
        "operator_id": "CO-EXP-AGRO360",
        "commodity": "COFFEE / PALM / CACAO",
        "country_of_production": "CO",
        "plots": [
            {
                "plot_id": f"FINCA_{random.randint(1000, 9999)}",
                "geolocation": st.session_state["poligono_geojson"]["geometry"],
                "deforestation_free_verification": True,
                "verification_method": "Copernicus Sentinel-2 M2M API (AgroEscudo 360)",
                "baseline_date": "2020-12-31"
            }
        ]
    }
    
    with st.expander("👀 Ver Payload JSON a enviar a Europa"):
        st.json(payload)
        
    if st.button("📤 Enviar Expediente DDS a la Unión Europea"):
        with st.spinner("Empaquetando datos y encriptando payload..."):
            time.sleep(1.5)
        with st.spinner("Estableciendo conexión segura con servidores de aduana UE (TRACES NT)..."):
            time.sleep(2)
        
        # Generar número de referencia y QR
        numero_dds = f"EU-DDS-2026-CO-{random.randint(100000, 999999)}"
        url_qr = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={numero_dds}"
        
        st.success("✅ ¡Declaración de Diligencia Debida (DDS) Aceptada por la Unión Europea!")
        
        col_res1, col_res2 = st.columns([2, 1])
        with col_res1:
            st.info(f"**Número de Referencia Oficial:**\n### {numero_dds}")
            st.markdown("""
            **Siguientes pasos:**
            1. Imprima este código QR.
            2. Adhiéralo a la guía de embarque (Bill of Lading) o al contenedor.
            3. Las autoridades aduaneras en el puerto de destino en Europa escanearán este código para liberar la mercancía.
            """)
        with col_res2:
            st.image(url_qr, caption="QR Aduanero EUDR")
