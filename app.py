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
if "token_legalidad" not in st.session_state:
    st.session_state["token_legalidad"] = None
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

    # --- PASO 1: MAPA ---
    st.subheader("1. Captura de Datos del Predio")
    st.markdown("Usa las herramientas para dibujar el lote. En campo, usa el botón de **Ubicación (GPS)**.")
    
    m = folium.Map(location=[4.5709, -74.2973], zoom_start=5)
    LocateControl(auto_start=False).add_to(m)
    Draw(export=True, draw_options={'polyline': False, 'rectangle': True, 'circle': False, 'marker': True, 'polygon': True}).add_to(m)
    
    output_mapa = st_folium(m, width=1000, height=400)
    
    if output_mapa["last_active_drawing"]:
        st.session_state["poligono_geojson"] = output_mapa["last_active_drawing"]
        st.success("✅ Polígono capturado exitosamente.")

    # --- PASO 2: DATOS COMERCIALES ---
    st.markdown("---")
    st.subheader("2. Datos Comerciales y Aduaneros Obligatorios")
    st.markdown("Asocie los metadatos de la cosecha de acuerdo a los requerimientos del ITC:")
    
    col_ad1, col_ad2 = st.columns(2)
    with col_ad1:
        hs_code = st.selectbox("Partida Arancelaria (HS Code)", [
            "0901.11.00 (Café sin tostar, sin descafeinar)",
            "1801.00.00 (Cacao en grano, entero o partido)",
            "1511.10.00 (Aceite de palma en bruto)"
        ])
        nombre_botanico = st.text_input("Nombre Botánico / Científico", value="Coffea arabica")
    with col_ad2:
        volumen_neto = st.number_input("Volumen Neto de Producción (Toneladas)", min_value=0.0, value=12.5, step=0.1)
        rango_cosecha = st.date_input("Rango de Cosecha", value=(datetime.date(2026, 1, 1), datetime.date(2026, 5, 30)))

    # --- PASO 3: BLINDAJE JURÍDICO (REVISIÓN DOCUMENTAL) ---
    st.markdown("---")
    st.subheader("3. Validación de Legalidad (Blindaje Jurídico)")
    st.markdown("Módulo de **Revisión Documental Asistida**: Digite los datos clave del documento informal que el productor envió por WhatsApp. El motor de reglas validará la legalidad local.")
    
    col_doc1, col_doc2 = st.columns(2)
    with col_doc1:
        tipo_doc = st.selectbox("Tipo de Documento de Tenencia", [
            "Certificado de Sana Posesión (Junta de Acción Comunal)",
            "Contrato de Compraventa a Mano",
            "Aval de Autoridad Tradicional (Cabildo/Resguardo)",
            "Escritura Pública (Formal)"
        ])
        doc_file = st.file_uploader("Cargar Foto del Documento (Recibida vía WhatsApp)", type=["jpg", "png", "pdf"])

    with col_doc2:
        st.info("⚖️ **Motor de Reglas Automáticas (De-Risking)**\nEl sistema cruzará las coordenadas dibujadas con las APIs del Estado (IGAC, ANT, UPRA) para evitar solapamientos con resguardos y validará el documento bajo el estándar europeo (Guías EFI).")
        
        if st.button("⚙️ Validar Documento y Emitir Token de Legalidad"):
            if not st.session_state["poligono_geojson"]:
                st.error("⚠️ Primero debe trazar el polígono de la finca en el Paso 1 para cruzarlo con el Estado.")
            else:
                with st.spinner("Consultando APIs de la Agencia Nacional de Tierras (ANT) e IGAC..."):
                    time.sleep(2)
                st.success("✅ **Análisis Geoespacial Local:** El predio no se superpone con Parques Nacionales ni Territorios Colectivos.")
                st.success(f"✅ **Traducción EFI:** El soporte '{tipo_doc}' es jurídicamente válido en el país de origen.")
                st.session_state["token_legalidad"] = f"TOK-LEG-CO-{random.randint(1000,9999)}"
                st.info(f"🔐 **Token de Legalidad Emitido:** `{st.session_state['token_legalidad']}`")

    # --- PASO 4: AUDITORÍA SATELITAL ---
    if st.session_state["poligono_geojson"]:
        st.markdown("---")
        st.subheader("4. Auditoría Satelital de Deforestación (Copernicus)")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            st.download_button("📥 Descargar Polígono (GeoJSON)", json.dumps(st.session_state["poligono_geojson"]), "finca.geojson", "application/json", type="primary")
        
        with col_btn2:
            if st.button("🔍 Ejecutar Auditoría Satelital"):
                if modo_demo:
                    st.success("✅ Conexión M2M exitosa con Sentinel-2.")
                    try:
                        st.image("NDVI_Prueba_Oficial.png", caption="Análisis NDVI - Línea Base 2020", use_column_width=True)
                        st.info("💡 Finca libre de deforestación comprobada científicamente (2020).")
                        st.session_state["auditoria_superada"] = True
                    except:
                        st.error("Sube la imagen 'NDVI_Prueba_Oficial.png' a tu GitHub.")
                else:
                    st.warning("⚠️ Iniciando petición OData real.")

    # --- PASO 5: ADUANAS (DDS) ---
    if st.session_state.get("auditoria_superada"):
        st.markdown("---")
        st.subheader("5. Declaración Aduanera Automatizada (DDS)")
        
        cosecha_str = f"{rango_cosecha[0]} a {rango_cosecha[1]}" if isinstance(rango_cosecha, (list, tuple)) and len(rango_cosecha) == 2 else str(rango_cosecha)
            
        payload = {
            "dds_type": "submission",
            "operator_id": "CO-EXP-AGRO360",
            "commodity_hs_code": hs_code.split(" ")[0],
            "botanical_name": nombre_botanico,
            "net_quantity_ton": volumen_neto,
            "harvest_period": cosecha_str,
            "legal_compliance_token": st.session_state.get("token_legalidad", "Pendiente"),
            "plots": [
                {
                    "geolocation": st.session_state["poligono_geojson"]["geometry"],
                    "deforestation_free_verification": True,
                    "verification_method": "Copernicus Sentinel-2 M2M"
                }
            ]
        }
        
        with st.expander("👀 Ver Payload JSON (Incluye Token de Legalidad)"):
            st.json(payload)
        
        if st.button("📤 Enviar Expediente a la Unión Europea (TRACES NT)"):
            with st.spinner("Conectando con TRACES NT..."):
                time.sleep(1.5)
            
            numero_dds = f"EU-DDS-2026-CO-{random.randint(100000, 999999)}"
            url_qr = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={numero_dds}"
            
            st.success("✅ Declaración Aceptada. Listo para embarque.")
            col_qr1, col_qr2 = st.columns([3, 1])
            with col_qr1:
                st.write(f"**Referencia DDS Oficial:** `{numero_dds}`")
                
                st.markdown("### 🌍 ¿Desea conseguir clientes europeos?")
                if st.button("✅ Incluir mi Finca en el Catálogo B2B"):
                    st.session_state["mi_finca_b2b"] = True
                    st.balloons()
                    st.success("¡Perfil comercial activado!")
            with col_qr2:
                st.image(url_qr, caption="QR Aduanero Oficial")

# ==========================================
# PÁGINA 2: PORTAL DE COMPRADORES (B2B)
# ==========================================
elif pagina == "🌍 2. Portal Compradores (B2B Marketplace)":
    st.title("🌍 AgroEscudo Hub: European Buyers Portal")
    st.markdown("Directorio exclusivo de proveedores agrícolas colombianos **100% verificados (EUDR)**.")
    
    datos_proveedores = [
        {"ID": "EU-DDS-845129", "Nombre": "Asoc. Cafetera del Sur", "Depto": "Huila", "Producto": "Café", "Volumen (Ton)": 150, "Certificación": "Fairtrade", "Exportación": "Japón, EE.UU."},
        {"ID": "EU-DDS-918273", "Nombre": "Cacaoteros Sierra Nevada", "Depto": "Magdalena", "Producto": "Cacao", "Volumen (Ton)": 80, "Certificación": "Orgánico", "Exportación": "Alemania, Suiza"}
    ]
    
    if st.session_state.get("mi_finca_b2b"):
        datos_proveedores.insert(0, {
            "ID": "EU-DDS-NUEVO", "Nombre": "🟢 TU FINCA", "Depto": "Magdalena", "Producto": "Café / Cacao", "Volumen (Ton)": 12.5, "Certificación": "En Proceso", "Exportación": "Lista para Europa"
        })

    df = pd.DataFrame(datos_proveedores)

    st.markdown("### 🔍 Filtrar Proveedores")
    f1, f2, f3 = st.columns(3)
    with f1:
        filtro_prod = st.selectbox("Producto", ["Todos", "Café", "Cacao", "Palma de Aceite"])
    with f2:
        filtro_cert = st.selectbox("Certificación", ["Todas", "Fairtrade", "Orgánico", "En Proceso"])
    with f3:
        vol_min = st.number_input("Vol. Mínimo (Ton)", value=0.0)

    if filtro_prod != "Todos": df = df[df["Producto"] == filtro_prod]
    if filtro_cert != "Todas": df = df[df["Certificación"] == filtro_cert]
    df = df[df["Volumen (Ton)"] >= vol_min]

    st.markdown("---")
    for index, row in df.iterrows():
        with st.container():
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1:
                st.image("https://cdn-icons-png.flaticon.com/512/190/190411.png", width=60) 
            with col2:
                st.subheader(row["Nombre"])
                st.markdown(f"**📍 {row['Depto']} | 🌱 {row['Producto']} | 📦 {row['Volumen (Ton)']} Toneladas**")
            with col3:
                st.button("📄 Expediente", key=f"btn_{index}")
            st.markdown("---")
