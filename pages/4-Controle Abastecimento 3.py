# ==========================================
# DASHBOARD DE ABASTECIMENTO - STREAMLIT
# ==========================================
# Salve este código como: app.py
# Execute com: streamlit run app.py
# ==========================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

# -----------------------
# CONFIGURAÇÕES INICIAIS
# -----------------------
st.set_page_config(page_title="Dashboard de Abastecimento", layout="wide")
st.title("⛽ Dashboard de Abastecimento de Veículos")

# -----------------------
# UPLOAD DO ARQUIVO
# -----------------------
uploaded_file = st.file_uploader(
    "📂 Faça upload do arquivo Excel ou CSV com os dados de abastecimento",
    type=["xlsx", "csv"]
)

if uploaded_file:
    # Leitura do arquivo
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file, encoding="utf-8", sep=",")
    else:
        df = pd.read_excel(uploaded_file)

    # Normalizar nomes das colunas
    df.columns = df.columns.str.strip().str.replace(" ", "_")

    # Converter data
    if 'Data' in df.columns:
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce', dayfirst=True)

    # Garantir tipos numéricos
    for col in ['Litros', 'Preço_Litro', 'Quilometragem']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Calcular valor total (se não existir)
    if 'Valor_Total' not in df.columns:
        df['Valor_Total'] = df['Litros'] * df['Preço_Litro']

    # Ordenar por veículo e data
    if 'Placa' in df.columns and 'Data' in df.columns:
        df = df.sort_values(['Placa', 'Data'])
        df['Km_Anterior'] = df.groupby('Placa')['Quilometragem'].shift(1)
        df['Km_Rodado'] = df['Quilometragem'] - df['Km_Anterior']
        df['Km_por_Litro'] = df['Km_Rodado'] / df['Litros']

    # -----------------------
    # FILTROS LATERAIS
    # -----------------------
    st.sidebar.header("Filtros")

    placas = st.sidebar.multiselect("Selecione a Placa:", df['Placa'].unique())
    motoristas = st.sidebar.multiselect("Selecione o Motorista:", df['Motorista'].unique())
    postos = st.sidebar.multiselect("Selecione o Posto:", df['Posto'].unique())
    combustiveis = st.sidebar.multiselect("Tipo de Combustível:", df['Combustível'].unique())
    estados = st.sidebar.multiselect("Estado:", df['Estado'].unique())

    # Aplicar filtros
    df_filtrado = df.copy()
    if placas:
        df_filtrado = df_filtrado[df_filtrado['Placa'].isin(placas)]
    if motoristas:
        df_filtrado = df_filtrado[df_filtrado['Motorista'].isin(motoristas)]
    if postos:
        df_filtrado = df_filtrado[df_filtrado['Posto'].isin(postos)]
    if combustiveis:
        df_filtrado = df_filtrado[df_filtrado['Combustível'].isin(combustiveis)]
    if estados:
        df_filtrado = df_filtrado[df_filtrado['Estado'].isin(estados)]

    # -----------------------
    # INDICADORES
    # -----------------------
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💸 Gasto Total (R$)", f"{df_filtrado['Valor_Total'].sum():,.2f}")
    col2.metric("⛽ Litros Totais", f"{df_filtrado['Litros'].sum():,.0f}")
    col3.metric("🚘 Consumo Médio (Km/L)", f"{df_filtrado['Km_por_Litro'].mean():.2f}")
    col4.metric("📅 Total de Abastecimentos", f"{len(df_filtrado):,.0f}")

    st.divider()

    # -----------------------
    # GRÁFICOS
    # -----------------------
    st.subheader("📊 Gasto Total por Veículo")
    gasto_por_placa = df_filtrado.groupby('Placa')['Valor_Total'].sum().sort_values(ascending=False)
    st.bar_chart(gasto_por_placa)

    st.subheader("📈 Consumo Médio por Motorista (Km/L)")
    consumo_motorista = df_filtrado.groupby('Motorista')['Km_por_Litro'].mean().sort_values(ascending=False)
    st.bar_chart(consumo_motorista)

    st.subheader("💰 Evolução do Preço do Combustível")
    if 'Data' in df_filtrado.columns:
        preco_tempo = df_filtrado.groupby('Data')['Preço_Litro'].mean()
        st.line_chart(preco_tempo)

    st.subheader("🛢️ Gasto por Tipo de Combustível")
    gasto_combustivel = df_filtrado.groupby('Combustível')['Valor_Total'].sum().sort_values(ascending=False)
    st.bar_chart(gasto_combustivel)

    # -----------------------
    # TABELA DETALHADA
    # -----------------------
    st.subheader("📋 Detalhamento dos Abastecimentos")
    st.dataframe(df_filtrado)

    # -----------------------
    # DOWNLOAD RESULTADOS
    # -----------------------
    buffer = BytesIO()
    df_filtrado.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)

    st.download_button(
        label="⬇️ Baixar Dados Filtrados (Excel)",
        data=buffer,
        file_name="dados_filtrados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("👆 Faça upload do arquivo para iniciar a análise.")
