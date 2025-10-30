import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# CONFIGURAÇÃO INICIAL
# -----------------------------
st.set_page_config(page_title="Dashboard de Abastecimento", layout="wide")
st.title("⛽ Dashboard de Abastecimento de Frota")

# -----------------------------
# LEITURA DOS DADOS
# -----------------------------
uploaded_file = st.file_uploader("📂 Envie o arquivo XLSX de abastecimento", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Conversões de dados
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
    df['Mês'] = df['Mês'].astype(str)
    df['Ano'] = df['Ano'].astype(str)

    # -----------------------------
    # FILTROS
    # -----------------------------
    with st.sidebar:
        st.header("🔍 Filtros")
        ano = st.selectbox("Ano", options=["Todos"] + sorted(df['Ano'].unique().tolist()))
        mes = st.selectbox("Mês", options=["Todos"] + sorted(df['Mês'].unique().tolist()))
        motorista = st.selectbox("Motorista", options=["Todos"] + sorted(df['Motorista'].unique().tolist()))
        placa = st.selectbox("Placa", options=["Todos"] + sorted(df['Placa'].unique().tolist()))
        combustivel = st.selectbox("Combustível", options=["Todos"] + sorted(df['Combustível'].unique().tolist()))

    # Aplicando filtros
    df_filtrado = df.copy()
    if ano != "Todos":
        df_filtrado = df_filtrado[df_filtrado['Ano'] == ano]
    if mes != "Todos":
        df_filtrado = df_filtrado[df_filtrado['Mês'] == mes]
    if motorista != "Todos":
        df_filtrado = df_filtrado[df_filtrado['Motorista'] == motorista]
    if placa != "Todos":
        df_filtrado = df_filtrado[df_filtrado['Placa'] == placa]
    if combustivel != "Todos":
        df_filtrado = df_filtrado[df_filtrado['Combustível'] == combustivel]

    # -----------------------------
    # CÁLCULOS E INDICADORES
    # -----------------------------
    gasto_total = df_filtrado['Valor_Total'].sum()
    litros_total = df_filtrado['Litros'].sum()
    preco_medio = df_filtrado['Preço_Litro'].mean()
    km_total = df_filtrado['Quilometragem'].sum()
    consumo_medio = km_total / litros_total if litros_total > 0 else 0

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("💰 Gasto Total (R$)", f"{gasto_total:,.2f}")
    col2.metric("⛽ Litros Totais", f"{litros_total:,.1f}")
    col3.metric("🧾 Preço Médio (R$/L)", f"{preco_medio:,.2f}")
    col4.metric("🚗 Quilometragem Total (km)", f"{km_total:,.0f}")
    col5.metric("⚙️ Consumo Médio (km/L)", f"{consumo_medio:,.2f}")

    st.divider()

    # -----------------------------
    # GRÁFICOS
    # -----------------------------
    st.subheader("📊 Análises Visuais")

    colA, colB = st.columns(2)

    # Gráfico 1: Gasto total por mês
    with colA:
        df_mes = df_filtrado.groupby('Mês')['Valor_Total'].sum().sort_index()
        fig, ax = plt.subplots()
        ax.bar(df_mes.index, df_mes.values)
        ax.set_title("Gasto Total por Mês")
        ax.set_xlabel("Mês")
        ax.set_ylabel("Valor Total (R$)")
        st.pyplot(fig)

    # Gráfico 2: Preço médio do litro por posto
    with colB:
        df_posto = df_filtrado.groupby('Posto')['Preço_Litro'].mean().sort_values(ascending=False)
        fig, ax = plt.subplots()
        ax.barh(df_posto.index, df_posto.values)
        ax.set_title("Preço Médio do Litro por Posto")
        ax.set_xlabel("Preço Médio (R$/L)")
        st.pyplot(fig)

    st.divider()

    # Gráfico 3: Ranking de motoristas
    st.subheader("🏆 Ranking de Motoristas (por gasto total)")
    df_motorista = df_filtrado.groupby('Motorista')['Valor_Total'].sum().sort_values(ascending=False)
    fig, ax = plt.subplots()
    ax.bar(df_motorista.index, df_motorista.values)
    ax.set_title("Gasto Total por Motorista")
    ax.set_xlabel("Motorista")
    ax.set_ylabel("Valor Total (R$)")
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # -----------------------------
    # TABELA FINAL
    # -----------------------------
    st.subheader("📋 Dados Filtrados")
    st.dataframe(df_filtrado)

    st.download_button(
        label="💾 Baixar dados filtrados (XLSX)",
        data=df_filtrado.to_excel(index=False).encode('utf-8'),
        file_name="dados_filtrados.csv",
        mime="text/xlsx"
    )

else:
    st.info("Envie o arquivo XLSX para começar a análise 🚀")
