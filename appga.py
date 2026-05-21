import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página do "site"
st.set_page_config(page_title="Dashboard de Atividades - Grupo A", layout="wide", page_icon="📊")

st.title("📊 Painel de Controle de Atividades")
st.markdown("Suba a sua base de dados em formato CSV para atualizar instantaneamente as visões operacionais.")

# Componente para upload do ficheiro
uploaded_file = st.file_uploader("Selecione o ficheiro da base de dados (CSV)", type=["csv"])

if uploaded_file is not None:
    try:
        # Carregar os dados tentando UTF-8 primeiro, depois Latin-1
try:
    df = pd.read_csv(uploaded_file, low_memory=False, sep=';', encoding='utf-8')
except UnicodeDecodeError:
    df = pd.read_csv(uploaded_file, low_memory=False, sep=';', encoding='latin-1')
        
        st.success("Base de dados carregada com sucesso!")
        
        # ----------------------------------------------------
        # MÉTRICAS RÁPIDAS (Cards no topo)
        # ----------------------------------------------------
        total_atividades = len(df)
        status_col = 'Status da Atividade' if 'Status da Atividade' in df.columns else df.columns[2]
        concluidas = len(df[df[status_col].astype(str).str.lower() == 'concluído'])
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Atividades", f"{total_atividades:,}")
        col2.metric("Atividades Concluídas", f"{concluidas:,}")
        if total_atividades > 0:
            col3.metric("Taxa de Conclusão", f"{(concluidas/total_atividades)*100:.1f}%")

        st.markdown("---")

        # ----------------------------------------------------
        # VISÃO 1: Distribuição por Cidade / Região
        # ----------------------------------------------------
        st.subheader("📍 Visão por Localidade (Cidade)")
        cidade_col = 'Cidade' if 'Cidade' in df.columns else None
        if cidade_col and cidade_col in df.columns:
            cidade_counts = df[cidade_col].value_counts().reset_index()
            cidade_counts.columns = ['Cidade', 'Quantidade']
            
            fig_cidade = px.bar(
                cidade_counts.head(15), 
                x='Quantidade', 
                y='Cidade', 
                orientation='h',
                title="Top 15 Cidades com Maior Volume de Atividades",
                color='Quantidade',
                color_continuous_scale='Blues'
            )
            fig_cidade.update_layout(yaxis={'categoryorder':'total ascending'}, height=400)
            st.plotly_chart(fig_cidade, use_container_width=True)
        else:
            st.warning("Coluna 'Cidade' não encontrada.")

        # ----------------------------------------------------
        # VISÃO 2: Status das Atividades & Tipos
        # ----------------------------------------------------
        st.subheader("📋 Status e Tipologias")
        col_graf1, col_graf2 = st.columns(2)
        
        with col_graf1:
            if status_col in df.columns:
                status_counts = df[status_col].value_counts().reset_index()
                status_counts.columns = ['Status', 'Total']
                fig_status = px.pie(
                    status_counts, 
                    values='Total', 
                    names='Status', 
                    title="Proporção por Status da Atividade",
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(fig_status, use_container_width=True)
                
        with col_graf2:
            # Tenta encontrar a coluna de Tipo de Atividade
            tipo_cols = [c for c in df.columns if 'Tipo de Atividade' in c]
            if tipo_cols:
                tipo_col = tipo_cols[0]
                tipo_counts = df[tipo_col].value_counts().reset_index().head(10)
                tipo_counts.columns = ['Tipo', 'Quantidade']
                fig_tipo = px.bar(
                    tipo_counts, 
                    x='Tipo', 
                    y='Quantidade', 
                    title="Top 10 Tipos de Atividade Mais Frequentes",
                    color='Quantidade',
                    color_continuous_scale='Viridis'
                )
                fig_tipo.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_tipo, use_container_width=True)

        # ----------------------------------------------------
        # VISÃO 3: Linha do Tempo / Evolução Diária
        # ----------------------------------------------------
        st.subheader("📅 Evolução Temporal")
        data_col = 'Data' if 'Data' in df.columns else None
        if data_col and data_col in df.columns:
            df[data_col] = pd.to_datetime(df[data_col], errors='coerce')
            df_datas = df.dropna(subset=[data_col]).groupby(data_col.strip()).size().reset_index(name='Quantidade')
            
            fig_linha = px.line(
                df_datas, 
                x=data_col, 
                y='Quantidade', 
                title="Volume de Atividades Criadas / Executadas ao Longo do Tempo",
                markers=True,
                line_shape='spline'
            )
            fig_linha.update_traces(line_color='#2E86C1', lw=3)
            st.plotly_chart(fig_linha, use_container_width=True)
            
        # ----------------------------------------------------
        # VISÃO EXTRA: Tabela de Dados Interativa
        # ----------------------------------------------------
        st.subheader("🔍 Explorador de Dados Completo")
        st.markdown("Utilize a tabela abaixo para filtrar, ordenar ou pesquisar registos específicos.")
        st.dataframe(df.head(100)) # Mostra as primeiras 100 linhas de forma interativa

    except Exception as e:
        st.error(f"Ocorreu um erro ao processar o ficheiro: {e}")
        st.info("Verifique se o formato do arquivo CSV está correto e contém as colunas esperadas.")
else:
    st.info("💡 Aguardando o upload do ficheiro CSV para gerar os gráficos automaticamente.")
