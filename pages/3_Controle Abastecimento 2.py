import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import chardet

# -----------------------------
# CONFIGURAÇÃO INICIAL
# -----------------------------
st.set_page_config(page_title="Dashboard de Abastecimento", layout="wide")
st.title("⛽ Dashboard de Abastecimento de Frota")

# -----------------------------
# UPLOAD DO ARQUIVO
# -----------------------------
uploaded_file = st.file_uploader("📂 Envie o arquivo de abastecimento (.xlsx ou .csv)", type=["xlsx", "csv"])

if uploaded_file:
    # -----------------------------
    # LEITURA DOS DADOS
    # -----------------------------
    file_name = uploaded_file.name.lower()

    try:
        if file_name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            # Detectar encoding automaticamente para CSV
            raw_data = uploaded_file.read()
            result = chardet.detect(raw_data)
            encoding_detectado = result['encoding']

            # Voltar o ponteiro do arquivo para o início antes de ler com pandas
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding=encoding_detectado)
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
        st.stop()

    # -----------------------------
    # LIMPEZA E CONVERSÕES
    # -----------------------------
    # Converter datas e tipos básicos
    if 'Data' in df.columns:
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce')

    for col in ['Mês', 'Ano']:
        if col in df.columns:
            df[col] = df[col].astype(str)

    # -----------------------------
    # FILTROS LATERAIS
    # -----------------------------
    with st.sidebar:
        st.header("🔍 Filtros")

        def selectbox_opcional(label, coluna):
            if coluna in df.columns:
                return st.selectbox(label, ["Todos"] + sorted(df[coluna].dropna().unique().tolist()))
            return "Todos"

        ano = selectbox_opcional("Ano", "Ano")
        mes = selectbox_opcional("Mês", "Mês")
        motorista = selectbox_opcional("Motorista", "Motorista")
        placa = selectbox_opcional("Placa", "Placa")
        combustivel = selectbox_opcional("Combustível", "Combustível")

    # Aplicar filtros dinamicamente
    df_filtrado = df.copy()

    if ano != "Todos" and "Ano" in df.columns:
        df_filtrado = df_filtrado[df_filtrado['Ano'] == ano]
    if mes != "Todos" and "Mês" in df.columns:
        df_filtrado = df_filtrado[df_filtrado['Mês'] == mes]
    if motorista != "Todos" and "Motorista" in df.columns:
        df_filtrado = df_filtrado[df_filtrado['Motorista'] == motorista]
    if placa != "Todos" and "Placa" in df.columns:
        df_filtrado = df_filtrado[df_filtrado['Placa'] == placa]
    if combustivel != "Todos" and "Combustível" in df.columns:
        df_filtrado = df_filtrado[df_filtrado['Combustível'] == combustivel]

    # -----------------------------
    # CÁLCULOS E INDICADORES
    # -----------------------------
    def soma(col):
        return df_filtrado[col].sum() if col in df_filtrado.columns else 0

    def media(col):
        return df_filtrado[col].mean() if col in df_filtrado.columns else 0

    gasto_total = soma('Valor_Total')
    litros_total = soma('Litros')
    preco_medio = media('Preço_Litro')
    km_total = soma('Quilometragem')
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
    if 'Mês' in df_filtrado.columns and 'Valor_Total' in df_filtrado.columns:
        with colA:
            df_mes = df_filtrado.groupby('Mês')['Valor_Total'].sum().sort_index()
            fig, ax = plt.subplots()
            ax.bar(df_mes.index, df_mes.values)
            ax.set_title("Gasto Total por Mês")
            ax.set_xlabel("Mês")
            ax.set_ylabel("Valor Total (R$)")
            st.pyplot(fig)

    # Gráfico 2: Preço médio do litro por posto
    if 'Posto' in df_filtrado.columns and 'Preço_Litro' in df_filtrado.columns:
        with colB:
            df_posto = df_filtrado.groupby('Posto')['Preço_Litro'].mean().sort_values(ascending=False)
            fig, ax = plt.subplots()
            ax.barh(df_posto.index, df_posto.values)
            ax.set_title("Preço Médio do Litro por Posto")
            ax.set_xlabel("Preço Médio (R$/L)")
            st.pyplot(fig)

    st.divider()

    # Gráfico 3: Ranking de motoristas
    if 'Motorista' in df_filtrado.columns and 'Valor_Total' in df_filtrado.columns:
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

    # Converter para Excel para download
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_filtrado.to_excel(writer, index=False, sheet_name='Dados Filtrados')
    output.seek(0)

    st.download_button(
        label="💾 Baixar dados filtrados (.xlsx)",
        data=output,
        file_name="dados_filtrados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("Envie o arquivo XLSX para começar a análise 🚀")
