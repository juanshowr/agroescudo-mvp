import streamlit as st
import json
import time
import random
import pandas as pd
import datetime
from shapely.geometry import shape, box
import folium
from folium.plugins import Draw, LocateControl
from streamlit_folium import st_folium

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="AgroEscudo 360° - Plataforma", page_icon="🛰️", layout="wide")

# --- VARIABLES DE SESIÓN ---
if "poligono_geojson" not in st.session_state:
    st.session_state["poligono_geojson"] = None
if "auditoria_superada" not in st.session_state:
    st.session_state["auditoria_superada"] = False
if "mi_finca_b2b" not in st.session_state:
    st.session_state["mi_finca_b2b"] = False

# --- NAVEGACIÓN LATERAL ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Flag_of_Europe.svg/2560px-Flag_of_Europe.svg.png", width=50)
st.sidebar.title("AgroEscudo 360°")
st.sidebar.markdown("---")
pagina = st.sidebar.radio("Navegación del Sistema", [
    "🛡️ 1. Portal Productor (Auditoría EUDR)", 
    "🌍 2. Portal Compradores (B2B Marketplace)"
])

st.sidebar.markdown("---")
modo_demo = st.sidebar.checkbox("🚀 Usar Modo Demo (Pitch)", value=True)

# ==========================================
# PÁGINA 1: PORTAL DEL PRODUCTOR / EXPORTADOR
# ==========================================
if pagina == "🛡️ 1. Portal Productor (Auditoría EUDR)":
    st.title("🛡️ Portal de Cumplimiento EUDR")
    st.markdown("Georreferenciación en campo, conexión M2M con Copernicus y enlace aduanero TRACES NT.")

    st.subheader("1. Captura de Datos del Predio")
    st.markdown("Usa las herramientas para dibujar el lote. En campo, usa el botón de **Ubicación (GPS)**.")
    
    # Mapa de Captura
    m = folium.Map(location=[4.5709, -74.2973], zoom_start=5)
    LocateControl(auto_start=False).add_to(m)
    Draw(export=True, draw_options={'polyline': False, 'rectangle': True, 'circle': False, 'marker': True, 'polygon': True}).add_to(m)
    
    output_mapa = st_folium(m, width=1000, height=400)
    
    if output_mapa["last_active_drawing"]:
        st.session_state["poligono_geojson"] = output_mapa["last_active_drawing"]
        st.success("✅ Polígono capturado exitosamente.")

    # --- NUEVA SECCIÓN: SUSTENTO ADUANERO BÁSICO (REQUERIMIENTO ITC) ---
    st.markdown("---")
    st.subheader("📋 Datos Comerciales y Aduaneros Obligatorios (EUDR)")
    st.markdown("De acuerdo con las exigencias de la Comisión Europea y el catálogo del ITC, asocie los metadatos de la cosecha:")
    
    col_ad1, col_ad2 = st.columns(2)
    with col_ad1:
        hs_code = st.selectbox("Partida Arancelaria (HS Code)", [
            "0901.11.00 (Café sin tostar, sin descafeinar)",
            "1801.00.00 (Cacao en grano, entero o partido)",
            "1511.10.00 (Aceite de palma en bruto)",
            "4407.11.00 (Madera de coníferas aserrada)"
        ])
        nombre_botanico = st.text_input("Nombre Botánico / Científico de la Variedad", value="Coffea arabica")
    with col_ad2:
        volumen_neto = st.number_input("Volumen Neto de Producción (Toneladas)", min_value=0.0, value=12.5, step=0.1)
        
        # Selección segura de rango de fechas para el pitch
        fecha_def_inicio = datetime.date(2026, 1, 1)
        fecha_def_fin = datetime.date(2026, 5, 30)
        rango_cosecha = st.date_input("Rango Específico de Cosecha (Inicio y Fin)", value=(fecha_def_inicio, fecha_def_fin))

    # Auditoría Satelital
    if st.session_state["poligono_geojson"]:
        st.markdown("---")
        st.subheader("2. Auditoría Satelital Copernicus")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            st.download_button("📥 Descargar Polígono (GeoJSON)", json.dumps(st.session_state["poligono_geojson"]), "finca.geojson", "application/json", type="primary")
        
        with col_btn2:
            if st.button("🔍 Ejecutar Auditoría Satelital"):
                if modo_demo:
                    st.success("✅ Conexión M2M exitosa con Sentinel-2.")
                    try:
                        st.image("NDVI_Prueba_Oficial.png", caption="Análisis NDVI - Línea Base 2020", use_column_width=True)
                        st.info("💡 Token de Legalidad emitido. Finca libre de deforestación en 2020.")
                        st.session_state["auditoria_superada"] = True
                    except:
                        st.error("Por favor, asegúrate de subir la imagen 'NDVI_Prueba_Oficial.png' a tu GitHub.")
                else:
                    st.warning("⚠️ Iniciando petición OData real (Desactivado por seguridad de memoria RAM).")

    # Aduanas y Enlace con TRACES NT
    if st.session_state.get("auditoria_superada"):
        st.markdown("---")
        st.subheader("3. Declaración Aduanera Automatizada (DDS)")
        
        # Validar y formatear el rango de cosecha ingresado por el usuario
        if isinstance(rango_cosecha, (list, tuple)) and len(rango_cosecha) == 2:
            cosecha_str = f"{rango_cosecha[0]} a {rango_cosecha[1]}"
        else:
            cosecha_str = str(rango_cosecha)
            
        # Construcción dinámica del Payload con las variables del paso anterior
        payload = {
            "dds_type": "submission",
            "operator_id": "CO-EXP-AGRO360",
            "commodity_hs_code": hs_code.split(" ")[0],
            "botanical_name": nombre_botanico,
            "country_of_production": "CO",
            "net_quantity_ton": volumen_neto,
            "harvest_period": cosecha_str,
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
        
        with st.expander("👀 Ver Payload JSON dinámico a enviar a Europa"):
            st.json(payload)
        
        if st.button("📤 Enviar Expediente a la Unión Europea"):
            with st.spinner("Estableciendo conexión segura con TRACES NT..."):
                time.sleep(1.5)
            
            numero_dds = f"EU-DDS-2026-CO-{random.randint(100000, 999999)}"
            url_qr = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={numero_dds}"
            
            st.success("✅ Declaración Aceptada por las autoridades competentes. Listo para embarque.")
            col_qr1, col_qr2 = st.columns([3, 1])
            with col_qr1:
                st.write(f"**Referencia DDS Oficial:** `{numero_dds}`")
                st.markdown("Imprima este código QR y adhiéralo a los documentos de transporte o al contenedor.")
                
                st.markdown("### 🌍 ¿Desea conseguir nuevos clientes en Europa?")
                if st.button("✅ Incluir mi Finca en el Catálogo B2B de AgroEscudo"):
                    st.session_state["mi_finca_b2b"] = True
                    st.balloons()
                    st.success("¡Perfil comercial activado! Los compradores europeos ahora pueden ver su finca verificada.")
            with col_qr2:
                st.image(url_qr, caption="QR Aduanero Oficial")


# ==========================================
# PÁGINA 2: PORTAL DE COMPRADORES (B2B)
# ==========================================
elif pagina == "🌍 2. Portal Compradores (B2B Marketplace)":
    st.title("🌍 AgroEscudo Hub: European Buyers Portal")
    st.markdown("Directorio exclusivo de proveedores agrícolas colombianos **100% verificados bajo la normativa EUDR**.")
    
    datos_proveedores = [
        {"ID": "EU-DDS-845129", "Nombre": "Asoc. Cafetera del Sur", "Depto": "Huila", "Producto": "Café", "Volumen (Ton)": 150, "Certificación": "Fairtrade", "Exportación": "Japón, EE.UU."},
        {"ID": "EU-DDS-918273", "Nombre": "Cacaoteros Sierra Nevada", "Depto": "Magdalena", "Producto": "Cacao", "Volumen (Ton)": 80, "Certificación": "Orgánico", "Exportación": "Alemania, Suiza"},
        {"ID": "EU-DDS-112233", "Nombre": "Palmeras del Magdalena Medio", "Depto": "Santander", "Producto": "Palma de Aceite", "Volumen (Ton)": 500, "Certificación": "RSPO", "Exportación": "Holanda"},
        {"ID": "EU-DDS-445566", "Nombre": "Café Altura Premium", "Depto": "Antioquia", "Producto": "Café", "Volumen (Ton)": 200, "Certificación": "Rainforest Alliance", "Exportación": "Corea del Sur"},
        {"ID": "EU-DDS-778899", "Nombre": "Cacao Nativo Ancestral", "Depto": "Huila", "Producto": "Cacao", "Volumen (Ton)": 50, "Certificación": "Ninguna", "Exportación": "Primera Exportación"}
    ]
    
    if st.session_state.get("mi_finca_b2b"):
        datos_proveedores.insert(0, {
            "ID": "EU-DDS-NUEVO", "Nombre": "🟢 TU FINCA (Recién Auditada)", "Depto": "Magdalena", "Producto": "Café / Cacao", "Volumen (Ton)": 12.5, "Certificación": "En Proceso", "Exportación": "Lista para Europa"
        })

    df = pd.DataFrame(datos_proveedores)

    st.markdown("### 🔍 Filtrar Proveedores Seguros")
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        filtro_prod = st.selectbox("Producto", ["Todos", "Café", "Cacao", "Palma de Aceite"])
    with f2:
        filtro_depto = st.selectbox("Región", ["Todas"] + list(df["Depto"].unique()))
    with f3:
        filtro_cert = st.selectbox("Certificación", ["Todas"] + list(df["Certificación"].unique()))
    with f4:
        vol_min = st.number_input("Vol. Mínimo (Ton)", value=0.0)

    if filtro_prod != "Todos": df = df[df["Producto"] == filtro_prod]
    if filtro_depto != "Todas": df = df[df["Depto"] == filtro_depto]
    if filtro_cert != "Todas": df = df[df["Certificación"] == filtro_cert]
    df = df[df["Volumen (Ton)"] >= vol_min]

    col_m1, col_m2 = st.columns(2)
    col_m1.metric("📦 Volumen Total Disponible (Ton)", df["Volumen (Ton)"].sum())
    col_m2.metric("✅ Fincas 100% Libres de Deforestación", len(df))

    st.markdown("---")
    for index, row in df.iterrows():
        with st.container():
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1:
                st.image("https://cdn-icons-png.flaticon.com/512/190/190411.png", width=80) 
                st.caption(f"ID: {row['ID']}")
            with col2:
                st.subheader(row["Nombre"])
                st.markdown(f"**📍 Región:** {row['Depto']} | **🌱 Producto:** {row['Producto']} | **📦 Capacidad:** {row['Volumen (Ton)']} Toneladas")
                st.markdown(f"**🏅 Certificaciones:** `{row['Certificación']}` | **🚢 Exp. Previa:** `{row['Exportación']}`")
            with col3:
                st.button("📄 Ver Expediente EUDR", key=f"btn_{index}")
                st.button("✉️ Contactar Productor", key=f"contacto_{index}", type="primary")
            st.markdown("---")
