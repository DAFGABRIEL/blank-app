import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração inicial do Streamlit
st.set_page_config(page_title="Dashboard de Análise de Produção Agrícola", layout="wide")

# Título e introdução
st.title("🌱 Dashboard de Análise de Produção Agrícola")
st.markdown("Este dashboard oferece uma análise abrangente da produção agrícola por município e produto, facilitando insights sobre produtividade e valores de produção do estado PERMANBUCO.")

# Carregar arquivo
uploaded_file = st.file_uploader("📁 Selecione o arquivo Excel, HTML ou CSV", type=["xls", "xlsx", "html", "csv"])

if uploaded_file is not None:
    # Identificar tipo de arquivo e ler os dados
    if uploaded_file.name.endswith('.xls') or uploaded_file.name.endswith('.xlsx'):
        engine = 'openpyxl' if uploaded_file.name.endswith('.xlsx') else 'xlrd'
        try:
            data = pd.read_excel(uploaded_file, engine=engine)
        except Exception as e:
            st.error(f"Erro ao ler o arquivo Excel: {e}")
            data = None
    elif uploaded_file.name.endswith('.csv'):
        try:
            data = pd.read_csv(uploaded_file)
        except Exception as e:
            st.error(f"Erro ao ler o arquivo CSV: {e}")
            data = None
    else:
        try:
            tables = pd.read_html(uploaded_file)
            data = tables[0] if tables else None
            if data is None:
                st.error("Nenhuma tabela encontrada no arquivo HTML.")
        except Exception as e:
            st.error(f"Erro ao ler o arquivo HTML: {e}")
            data = None

    if data is not None:
        data.columns = data.columns.str.strip()  # Limpar espaços nas colunas

        # Divisão em colunas para visual moderno
        col1, col2 = st.columns([3, 1])

        # Exibir estrutura e dados na primeira coluna
        with col1:
            st.subheader("📊 Dados Carregados")
            st.dataframe(data)

        with col2:
            # Estatísticas principais
            st.subheader("📌 Estatísticas Principais")
            producao_total = data.groupby('nome')['quant'].sum().reset_index()
            municipio_top = producao_total.loc[producao_total['quant'].idxmax()]

            st.metric(label="Município com Maior Produção", value=f"{municipio_top['nome']}", delta=f"{municipio_top['quant']} t")

            valor_total = data.groupby('nome')['valor'].sum().reset_index()
            municipio_valor_top = valor_total.loc[valor_total['valor'].idxmax()]
            st.metric(label="Município com Maior Valor de Produção", value=f"{municipio_valor_top['nome']}", delta=f"R${municipio_valor_top['valor']:.2f} mil")

        # Análises por Município
        with st.container():
            st.subheader("🔍 Análise Completa por Município")
            producao_total.columns = ['Município', 'Produção Total (t)']
            area_media = data.groupby('nome')['area'].mean().reset_index().rename(columns={'nome': 'Município', 'area': 'Área Média Colhida (ha)'})
            rendimento_medio = data.groupby('nome')['rend_med'].mean().reset_index().rename(columns={'nome': 'Município', 'rend_med': 'Rendimento Médio (kg/ha)'})
            valor_total.columns = ['Município', 'Valor Total da Produção (R$1.000)']
            
            analise_completa = producao_total.merge(area_media, on='Município').merge(rendimento_medio, on='Município').merge(valor_total, on='Município')
            st.dataframe(analise_completa.sort_values(by='Produção Total (t)', ascending=False))

        # Gráficos de análise
        st.subheader("📈 Gráficos de Análise por Município")
        
        col3, col4 = st.columns(2)
        with col3:
            fig_area = px.bar(analise_completa.sort_values(by='Área Média Colhida (ha)', ascending=False),
                              x='Município', y='Área Média Colhida (ha)', color='Área Média Colhida (ha)',
                              title='Área Média Colhida por Município', color_continuous_scale=px.colors.sequential.Blues)
            st.plotly_chart(fig_area)

        with col4:
            fig_rendimento = px.bar(analise_completa.sort_values(by='Rendimento Médio (kg/ha)', ascending=False),
                                    x='Município', y='Rendimento Médio (kg/ha)', color='Rendimento Médio (kg/ha)',
                                    title='Rendimento Médio por Município', color_continuous_scale=px.colors.sequential.Greens)
            st.plotly_chart(fig_rendimento)

        # Análise por Produto Agrícola
        st.subheader("🌾 Análise por Produto Agrícola")
        producao_produto = data.groupby('prod')['quant'].sum().reset_index().rename(columns={'prod': 'Produto', 'quant': 'Produção Total (t)'})
        valor_produto = data.groupby('prod')['valor'].sum().reset_index().rename(columns={'prod': 'Produto', 'valor': 'Valor Total da Produção (R$1.000)'})
        analise_produto = producao_produto.merge(valor_produto, on='Produto')
        st.dataframe(analise_produto.sort_values(by='Valor Total da Produção (R$1.000)', ascending=False))

        # Gráfico Top 5 produtos
        top5_valor_produto = analise_produto.nlargest(5, 'Valor Total da Produção (R$1.000)')
        fig_top5_valor_produto = px.bar(top5_valor_produto, x='Produto', y='Valor Total da Produção (R$1.000)',
                                        title='Top 5 Produtos por Valor de Produção', color='Valor Total da Produção (R$1.000)',
                                        color_continuous_scale=px.colors.sequential.Inferno)
        st.plotly_chart(fig_top5_valor_produto)

        # Filtro e visualização por município
        st.subheader("🌍 Filtrar Dados por Município")
        municipio_escolhido = st.selectbox("Escolha um Município", data['nome'].unique())
        dados_municipio = data[data['nome'] == municipio_escolhido]
        st.write(f"Dados para o Município: {municipio_escolhido}")
        st.dataframe(dados_municipio)

        # Análise de Produtividade por Produto
        st.subheader("📊 Produtividade Média por Produto")
        produtividade_produto = data.groupby('prod').apply(lambda x: (x['quant'].sum() / x['area'].sum())).reset_index()
        produtividade_produto.columns = ['Produto', 'Produtividade Média (kg/ha)']
        st.dataframe(produtividade_produto.sort_values(by='Produtividade Média (kg/ha)', ascending=False))

        # Gráfico de Produtividade por Produto
        fig_produtividade = px.bar(produtividade_produto.sort_values(by='Produtividade Média (kg/ha)', ascending=False),
                                x='Produto', y='Produtividade Média (kg/ha)', color='Produtividade Média (kg/ha)',
                                title='Produtividade Média por Produto', color_continuous_scale=px.colors.sequential.Plasma)
        st.plotly_chart(fig_produtividade)

        # Análise de Eficiência Econômica por Produto
        st.subheader("💸 Eficiência Econômica por Produto (Valor por Hectare)")
        eficiencia_economica = data.groupby('prod').apply(lambda x: (x['valor'].sum() / x['area'].sum())).reset_index()
        eficiencia_economica.columns = ['Produto', 'Valor por Hectare (R$/ha)']
        st.dataframe(eficiencia_economica.sort_values(by='Valor por Hectare (R$/ha)', ascending=False))

        # Gráfico de Eficiência Econômica por Produto
        fig_eficiencia = px.bar(eficiencia_economica.sort_values(by='Valor por Hectare (R$/ha)', ascending=False),
                                x='Produto', y='Valor por Hectare (R$/ha)', color='Valor por Hectare (R$/ha)',
                                title='Eficiência Econômica por Produto', color_continuous_scale=px.colors.sequential.Sunset)
        st.plotly_chart(fig_eficiencia)
else:
    st.info("Por favor, faça o upload de um arquivo para iniciar a análise.")