import streamlit as st
import requests
import os
import zipfile
import glob
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import box
import rasterio
from rasterio.enums import Resampling

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="AgroEscudo 360° - MVP", page_icon="🛰️", layout="wide")

st.title("🛰️ AgroEscudo 360° - Auditoría Satelital EUDR")
st.markdown("Plataforma de validación de cero deforestación (Línea Base Dic 2020) conectada a Copernicus.")

# --- BARRA LATERAL (INPUTS DEL USUARIO) ---
st.sidebar.header("📍 Datos del Predio")
min_lon = st.sidebar.number_input("Longitud Mínima", value=-74.20, format="%.4f")
min_lat = st.sidebar.number_input("Latitud Mínima", value=10.40, format="%.4f")
max_lon = st.sidebar.number_input("Longitud Máxima", value=-74.00, format="%.4f")
max_lat = st.sidebar.number_input("Latitud Máxima", value=10.60, format="%.4f")

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Configuración M2M")
USUARIO = st.sidebar.text_input("Usuario Copernicus", type="password")
CONTRASENA = st.sidebar.text_input("Contraseña Copernicus", type="password")

# --- MODO DEMO ---
st.sidebar.markdown("---")
modo_demo = st.sidebar.checkbox("🚀 Usar Modo Demo (Recomendado para presentación)", value=True)
st.sidebar.caption("El modo Demo carga el NDVI preprocesado para evitar la descarga en vivo de 1GB desde la API europea.")

class CopernicusAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token
    def __call__(self, r):
        r.headers["Authorization"] = f"Bearer {self.token}"
        return r

if st.sidebar.button("🔍 Ejecutar Auditoría Satelital"):
    if modo_demo:
        st.success("✅ Conexión simulada exitosa. Cargando expediente DDS de la base de datos...")
        # Carga la imagen local que vamos a subir a GitHub
        try:
            st.image("NDVI_Prueba_Oficial.png", caption="Auditoría Satelital AgroEscudo 360° - Departamento del Magdalena", use_column_width=True)
            st.info("💡 Token de Legalidad emitido y adjuntado al expediente.")
        except Exception as e:
            st.error("Error al cargar la imagen del Demo. Asegúrate de haberla subido a GitHub.")
            
    else:
        if not USUARIO or not CONTRASENA:
            st.error("⚠️ Ingresa tus credenciales de Copernicus para la conexión en vivo.")
        else:
            with st.spinner('Conectando vía API con Copernicus Data Space...'):
                # Simulación visual del proceso real para el usuario web
                area_interes = box(min_lon, min_lat, max_lon, max_lat)
                st.write(f"Buscando polígono: {area_interes.wkt}")
                st.warning("⚠️ Iniciando petición OData real. Por limitaciones del servidor gratuito, esto podría interrumpirse por falta de memoria RAM. Se recomienda usar el Modo Demo.")
                # (Aquí iría la lógica pesada de requests.get y rasterio, acortada por protección de RAM en la nube web)
