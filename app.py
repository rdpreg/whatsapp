import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime
import io

class ZAPIWhatsAppSender:
    def __init__(self, instance_id: str, token: str):
        self.instance_id = instance_id
        self.token = token
        self.base_url = f"https://api.z-api.io/instances/{instance_id}/token/{token}"
        
    def send_text_message(self, phone: str, message: str):
        url = f"{self.base_url}/send-text"
        payload = {"phone": phone, "message": message}
        
        try:
            response = requests.post(url, json=payload)
            return {
                "phone": phone,
                "status": "✅ Sucesso" if response.status_code == 200 else "❌ Erro",
                "response": response.json() if response.status_code == 200 else response.text,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
        except Exception as e:
            return {
                "phone": phone,
                "status": "❌ Erro",
                "error": str(e),
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
    
    def send_image_message(self, phone: str, image_url: str, caption: str = ""):
        url = f"{self.base_url}/send-image"
        payload = {"phone": phone, "image": image_url, "caption": caption}
        
        try:
            response = requests.post(url, json=payload)
            return {
                "phone": phone,
                "status": "✅ Sucesso" if response.status_code == 200 else "❌ Erro",
                "response": response.json() if response.status_code == 200 else response.text,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
        except Exception as e:
            return {
                "phone": phone,
                "status": "❌ Erro",
                "error": str(e),
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }

# Configuração da página
st.set_page_config(
    page_title="WhatsApp Bulk Sender - Convexa",
    page_icon="📱",
    layout="wide"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        border-radius: 4px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">📱 WhatsApp Bulk Sender</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Convexa Investimentos - Disparo em Massa via ZAPI</div>', unsafe_allow_html=True)

# Sidebar - Configurações
with st.sidebar:
    st.header("⚙️ Configurações ZAPI")
    
    # Salvar credenciais na sessão
    if 'instance_id' not in st.session_state:
        st.session_state.instance_id = ""
    if 'token' not in st.session_state:
        st.session_state.token = ""
    
    instance_id = st.text_input(
        "Instance ID",
        value=st.session_state.instance_id,
        type="password",
        help="Seu Instance ID do ZAPI"
    )
    
    token = st.text_input(
        "Token",
        value=st.session_state.token,
        type="password",
        help="Seu token de autenticação do ZAPI"
    )
    
    if st.button("💾 Salvar Credenciais"):
        st.session_state.instance_id = instance_id
        st.session_state.token = token
        st.success("Credenciais salvas!")
    
    st.divider()
    
    st.header("⏱️ Configurações de Envio")
    delay = st.slider(
        "Delay entre mensagens (segundos)",
        min_value=3,
        max_value=15,
        value=5,
        help="Recomendado: 5 segundos para evitar bloqueios"
    )
    
    st.divider()
    
    # Download template
    st.header("📥 Template Excel")
    if st.button("Baixar Template"):
        template_data = {
            'phone': ['5521999999999', '5521988888888'],
            'name': ['João Silva', 'Maria Santos'],
            'produto': ['CDB', 'LCI'],
            'valor': ['10000', '15000']
        }
        df_template = pd.DataFrame(template_data)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_template.to_excel(writer, index=False, sheet_name='Contatos')
        
        st.download_button(
            label="📄 Download Template.xlsx",
            data=output.getvalue(),
            file_name="template_contatos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# Tabs principais
tab1, tab2, tab3 = st.tabs(["📤 Envio em Massa", "🖼️ Envio com Imagem", "📊 Histórico"])

# TAB 1 - Envio em Massa
with tab1:
    st.header("Envio de Mensagens em Massa")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1️⃣ Upload da Base de Contatos")
        uploaded_file = st.file_uploader(
            "Envie sua planilha Excel",
            type=['xlsx', 'xls'],
            help="Planilha deve conter ao menos a coluna 'phone'"
        )
        
        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file)
                st.success(f"✅ {len(df)} contatos carregados!")
                
                with st.expander("👁️ Visualizar dados"):
                    st.dataframe(df, use_container_width=True)
                
                # Detecta colunas disponíveis
                available_columns = df.columns.tolist()
                st.info(f"**Colunas detectadas:** {', '.join(available_columns)}")
                
                # Verifica se tem coluna phone
                if 'phone' not in available_columns:
                    st.error("❌ A planilha precisa ter uma coluna chamada 'phone'")
                else:
                    st.session_state.df = df
                    st.session_state.available_columns = available_columns
                    
            except Exception as e:
                st.error(f"Erro ao ler arquivo: {str(e)}")
    
    with col2:
        st.subheader("2️⃣ Escreva sua Mensagem")
        
        # Mostra placeholders disponíveis
        if 'available_columns' in st.session_state:
            placeholders = [f"{{{col}}}" for col in st.session_state.available_columns]
            st.info(f"**Placeholders disponíveis:** {', '.join(placeholders)}")
        
        message_template = st.text_area(
            "Mensagem (use {name}, {produto}, etc para personalizar)",
            value="""Olá {name}! 👋

Temos uma novidade importante sobre {produto}.

Gostaria de receber mais informações?

Att,
Rafael - Convexa Investimentos""",
            height=250
        )
        
        # Preview da mensagem
        if 'df' in st.session_state and len(st.session_state.df) > 0:
            st.subheader("👁️ Preview")
            first_contact = st.session_state.df.iloc[0].to_dict()
            try:
                preview = message_template.format(**first_contact)
                st.text_area("Exemplo com primeiro contato:", preview, height=150, disabled=True)
            except KeyError as e:
                st.warning(f"⚠️ Placeholder não encontrado na planilha: {e}")
    
    # Botão de envio
    st.divider()
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
    
    with col_btn1:
        if st.button("🚀 ENVIAR MENSAGENS", type="primary", use_container_width=True):
            if not st.session_state.instance_id or not st.session_state.token:
                st.error("❌ Configure as credenciais ZAPI na barra lateral!")
            elif 'df' not in st.session_state:
                st.error("❌ Faça upload da planilha de contatos!")
            else:
                # Inicia envio
                sender = ZAPIWhatsAppSender(
                    st.session_state.instance_id,
                    st.session_state.token
                )
                
                df = st.session_state.df
                contacts = df.to_dict('records')
                
                # Progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                results = []
                
                for i, contact in enumerate(contacts):
                    try:
                        # Personaliza mensagem
                        message = message_template.format(**contact)
                        
                        # Envia
                        result = sender.send_text_message(contact['phone'], message)
                        result['name'] = contact.get('name', 'N/A')
                        results.append(result)
                        
                        # Atualiza progress
                        progress = (i + 1) / len(contacts)
                        progress_bar.progress(progress)
                        status_text.text(f"Enviando {i+1}/{len(contacts)}: {contact.get('name', contact['phone'])}")
                        
                        # Delay
                        if i < len(contacts) - 1:
                            time.sleep(delay)
                            
                    except Exception as e:
                        results.append({
                            'phone': contact.get('phone', 'N/A'),
                            'name': contact.get('name', 'N/A'),
                            'status': '❌ Erro',
                            'error': str(e),
                            'timestamp': datetime.now().strftime("%H:%M:%S")
                        })
                
                # Salva resultados na sessão
                st.session_state.last_results = results
                st.session_state.last_campaign_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                
                # Estatísticas
                df_results = pd.DataFrame(results)
                success_count = len([r for r in results if '✅' in r['status']])
                error_count = len(results) - success_count
                
                st.balloons()
                
                col_stat1, col_stat2, col_stat3 = st.columns(3)
                with col_stat1:
                    st.metric("Total Enviado", len(results))
                with col_stat2:
                    st.metric("Sucessos", success_count, delta=f"{success_count/len(results)*100:.1f}%")
                with col_stat3:
                    st.metric("Erros", error_count)
                
                # Tabela de resultados
                st.subheader("📊 Resultados Detalhados")
                st.dataframe(df_results, use_container_width=True)
                
                # Download relatório
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_results.to_excel(writer, index=False, sheet_name='Resultados')
                
                st.download_button(
                    label="📥 Download Relatório",
                    data=output.getvalue(),
                    file_name=f"relatorio_envios_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

# TAB 2 - Envio com Imagem
with tab2:
    st.header("Envio de Mensagens com Imagem")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1️⃣ Upload da Base")
        uploaded_file_img = st.file_uploader(
            "Envie sua planilha",
            type=['xlsx', 'xls'],
            key="upload_img"
        )
        
        if uploaded_file_img:
            df_img = pd.read_excel(uploaded_file_img)
            st.success(f"✅ {len(df_img)} contatos carregados!")
            st.session_state.df_img = df_img
    
    with col2:
        st.subheader("2️⃣ URL da Imagem")
        image_url = st.text_input(
            "Cole a URL da imagem",
            placeholder="https://exemplo.com/imagem.jpg",
            help="A imagem precisa estar hospedada online e ser acessível publicamente"
        )
        
        if image_url:
            try:
                st.image(image_url, caption="Preview da imagem", width=300)
            except:
                st.warning("⚠️ Não foi possível carregar preview")
        
        caption = st.text_area(
            "Legenda da imagem",
            value="Confira nosso novo produto! 🚀",
            height=100
        )
    
    if st.button("🚀 ENVIAR COM IMAGEM", type="primary"):
        if not st.session_state.instance_id or not st.session_state.token:
            st.error("❌ Configure as credenciais ZAPI!")
        elif 'df_img' not in st.session_state:
            st.error("❌ Faça upload da planilha!")
        elif not image_url:
            st.error("❌ Adicione a URL da imagem!")
        else:
            sender = ZAPIWhatsAppSender(
                st.session_state.instance_id,
                st.session_state.token
            )
            
            df = st.session_state.df_img
            contacts = df.to_dict('records')
            
            progress_bar = st.progress(0)
            results = []
            
            for i, contact in enumerate(contacts):
                result = sender.send_image_message(
                    contact['phone'],
                    image_url,
                    caption
                )
                result['name'] = contact.get('name', 'N/A')
                results.append(result)
                
                progress_bar.progress((i + 1) / len(contacts))
                
                if i < len(contacts) - 1:
                    time.sleep(delay)
            
            st.success(f"✅ Enviado para {len(results)} contatos!")
            st.dataframe(pd.DataFrame(results))

# TAB 3 - Histórico
with tab3:
    st.header("📊 Histórico da Última Campanha")
    
    if 'last_results' in st.session_state:
        st.info(f"**Campanha realizada em:** {st.session_state.last_campaign_time}")
        
        df_hist = pd.DataFrame(st.session_state.last_results)
        
        # Métricas
        col1, col2, col3, col4 = st.columns(4)
        
        success_count = len([r for r in st.session_state.last_results if '✅' in r['status']])
        total = len(st.session_state.last_results)
        
        with col1:
            st.metric("Total", total)
        with col2:
            st.metric("Sucessos", success_count)
        with col3:
            st.metric("Erros", total - success_count)
        with col4:
            st.metric("Taxa de Sucesso", f"{success_count/total*100:.1f}%")
        
        # Tabela completa
        st.dataframe(df_hist, use_container_width=True)
        
        # Download
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_hist.to_excel(writer, index=False)
        
        st.download_button(
            label="📥 Download Histórico",
            data=output.getvalue(),
            file_name=f"historico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("Nenhuma campanha realizada ainda.")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>💼 Convexa Investimentos - Automação WhatsApp</p>
    <p style='font-size: 0.8rem;'>Desenvolvido com Streamlit + ZAPI</p>
</div>
""", unsafe_allow_html=True)
