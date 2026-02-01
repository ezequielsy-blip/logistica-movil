import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Configuración visual para celular
st.set_page_config(page_title="WMS Master Móvil", layout="centered")

# Estilo CSS para que parezca una App nativa
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; height: 70px; font-size: 20px; border-radius: 15px; background-color: #2e7d32; color: white; }
    .stTextInput>div>div>input { height: 50px; font-size: 18px; }
    [data-testid="stMetricValue"] { font-size: 24px; color: #4caf50; }
    </style>
    """, unsafe_allow_html=True)

# Conexión a la base de datos
# NOTA: Asegúrate de subir tu archivo 'inventario_wms.db' a GitHub también
def conectar():
    return sqlite3.connect('inventario_wms.db', check_same_thread=False)

st.title("🚀 WMS LOGISTICA & DESPACHO")

# Pestañas para separar las Apps
tab1, tab2 = st.tabs(["📤 DESPACHO (Salida)", "📥 LOGÍSTICA (Entrada)"])

# --- PESTAÑA 1: DESPACHO ---
with tab1:
    st.subheader("Buscador para Salida")
    busqueda_salida = st.text_input("Escribe nombre o código", key="bus_sal")
    
    if busqueda_salida:
        conn = conectar()
        query = f"SELECT cod_int, nombre FROM maestra WHERE nombre LIKE '%{busqueda_salida}%' OR cod_int LIKE '%{busqueda_salida}%' LIMIT 5"
        df_res = pd.read_sql(query, conn)
        
        if not df_res.empty:
            item = st.selectbox("Selecciona producto:", df_res['nombre'].tolist(), key="sel_sal")
            cod_id = df_res[df_res['nombre'] == item]['cod_int'].values[0]
            
            st.info(f"Código: {cod_id}")
            
            # Ver Lotes
            df_stock = pd.read_sql(f"SELECT rowid, cantidad, ubicacion, fecha FROM inventario WHERE cod_int = '{cod_id}' AND cantidad > 0", conn)
            
            if not df_stock.empty:
                for i, row in df_stock.iterrows():
                    with st.expander(f"📍 {row['ubicacion']} | Stock: {row['cantidad']}"):
                        cant_baja = st.number_input(f"Cantidad a sacar", min_value=0.0, max_value=float(row['cantidad']), key=f"n_{row['rowid']}")
                        if st.button(f"CONFIRMAR DESPACHO", key=f"btn_{row['rowid']}"):
                            cursor = conn.cursor()
                            cursor.execute("UPDATE inventario SET cantidad = cantidad - ? WHERE rowid = ?", (cant_baja, row['rowid']))
                            conn.commit()
                            st.success("¡Despacho registrado!")
                            st.rerun()
            else:
                st.error("No hay stock disponible.")
        conn.close()

# --- PESTAÑA 2: LOGÍSTICA ---
with tab2:
    st.subheader("Ingreso de Mercadería")
    busqueda_entrada = st.text_input("Buscar para ingresar", key="bus_ent")
    
    if busqueda_entrada:
        conn = conectar()
        df_res_ent = pd.read_sql(f"SELECT cod_int, nombre FROM maestra WHERE nombre LIKE '%{busqueda_entrada}%' LIMIT 5", conn)
        
        if not df_res_ent.empty:
            item_ent = st.selectbox("Selecciona para ingresar:", df_res_ent['nombre'].tolist())
            cod_ent = df_res_ent[df_res_ent['nombre'] == item_ent]['cod_int'].values[0]
            
            with st.form("form_entrada"):
                f_cant = st.number_input("Cantidad entrante", min_value=1.0)
                f_ubica = st.text_input("Ubicación (Ej: A-10)")
                f_fecha = st.date_input("Fecha de Vencimiento", datetime.now())
                
                if st.form_submit_button("GUARDAR INGRESO"):
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO inventario (cod_int, cantidad, ubicacion, fecha) VALUES (?,?,?,?)", 
                                 (cod_ent, f_cant, f_ubica, f_fecha.strftime('%Y-%m-%d')))
                    conn.commit()
                    st.success("¡Entrada guardada en la nube!")
        conn.close()
                      
