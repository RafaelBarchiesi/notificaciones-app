import os
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Consulta Notificaciones UED", layout="wide")
st.title("📋 Consulta de Notificaciones - Electrodependientes")

if not os.path.exists("Historial_Notificaciones.xlsx"):
    st.warning("⚠️ No hay historial cargado todavía.")
else:
    df_hist = pd.read_excel("Historial_Notificaciones.xlsx")

    for col in ["Visto", "Respondió", "Respuesta", "Estado Caso"]:
        if col not in df_hist.columns:
            df_hist[col] = ""

    if "Fecha Notificación" in df_hist.columns and not pd.api.types.is_datetime64_any_dtype(df_hist["Fecha Notificación"]):
        df_hist["Fecha Notificación"] = pd.to_datetime(df_hist["Fecha Notificación"], errors="coerce")

    st.markdown("### 🔍 Filtros de búsqueda")

    tipo_sel = None
    if "Tipo Notificación" in df_hist.columns:
        tipos = df_hist["Tipo Notificación"].dropna().unique().tolist()
        tipo_sel = st.selectbox("📌 Filtrar por tipo de notificación", ["Todos"] + tipos)
        if tipo_sel != "Todos":
            df_hist = df_hist[df_hist["Tipo Notificación"] == tipo_sel]

    fecha_sel = st.date_input("📆 Filtrar por fecha específica", value=None)
    consulta = st.text_input("🔎 Buscar por NIC, nombre o teléfono").strip().lower()

    resultados = df_hist.copy()

    if fecha_sel:
        resultados = resultados[resultados["Fecha Notificación"].dt.date == fecha_sel]

    if consulta:
        resultados = resultados[resultados.apply(
            lambda row: (
                consulta in str(row.get("telefonos", "")).lower() or
                consulta in str(row.get("Contacto", "")).lower() or
                consulta in str(row.get("NOMBRE ELECTRODEPENDIENTE", "")).lower() or
                consulta in str(row.get("Nº SUMINISTRO", "")).lower()
            ), axis=1
        )]

    if not resultados.empty:
        st.success(f"🔎 Se encontraron {len(resultados)} resultados.")
        st.dataframe(resultados[[
            "Nº SUMINISTRO",
            "NOMBRE ELECTRODEPENDIENTE",
            "telefonos",
            "Fecha Notificación",
            "Tipo Notificación" if "Tipo Notificación" in resultados.columns else resultados.columns[0],
            "Estado Notificación",
            "Observaciones",
            "Estado Caso",
            "Visto",
            "Respondió",
            "Respuesta"
        ]])

        st.download_button(
            "⬇ Descargar resultados",
            data=resultados.to_csv(index=False).encode("utf-8"),
            file_name="Seguimiento_Consulta.csv",
            mime="text/csv"
        )
    else:
        st.info("No se encontraron coincidencias con los filtros ingresados.")
