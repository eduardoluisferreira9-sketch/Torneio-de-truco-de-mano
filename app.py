import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import random
import json
import os
import qrcode
import socket
import requests 
from PIL import Image 
from io import BytesIO
from datetime import datetime, timedelta

# 🃏 CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Central de Torneios de Truco - Planta Baixa",
    page_icon="🃏",
    layout="wide"
)

NOME_CRIADOR = "Eduardo Luis Ferreira"
ARQUIVO_BACKUP = "torneio_atual_pb.json"
ARQUIVO_GALERIA = "galeria_campeoes.json"
CHAVE_ADMINISTRADOR = "truco123"

# ==========================================
# 🖼️ BANCO DE DADOS DE IMAGENS VIA INTERNET
# ==========================================
URL_BASE_IMAGENS = "https://raw.githubusercontent.com/seu-usuario/seu-repositorio/main/imagens"

# Tentativa de carregar a imagem do Baralho Espanhol para o Ícone da Página
icone_pagina = "🃏" 
try:
    resposta = requests.get(f"{URL_BASE_IMAGENS}/baralho_espanhol.png", timeout=5)
    if resposta.status_code == 200:
        icone_pagina = Image.open(BytesIO(resposta.content))
except Exception:
    pass

# 🛠️ ESTILIZAÇÃO CSS (Divisórias Brancas de Alto Contraste)
st.markdown("""
    <style>
    /* Fundo Geral */
    .stApp { background-color: #0d231a; } 
    
    /* Barra Lateral */
    section[data-testid="stSidebar"] {
        background-color: #07140f;
        border-right: 2px solid #1c4234;
    }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2 { color: #d4af37; }
    
    /* Textos, Títulos e Labels Principais em Branco de Alto Contraste */
    h1, h2, h3, p, label, .stText, [data-testid="stMarkdownContainer"] p { 
        color: #ffffff !important; 
    }
    
    /* Customização dos Inputs (Campos de Texto) no Painel Principal */
    div[data-testid="stTextInput"] input {
        color: #ffffff !important;
        background-color: #07140f !important;
        border: 1px solid #1c4234 !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #d4af37 !important;
    }
    div[data-testid="stTextInput"] label {
        color: #d4af37 !important;
        font-weight: bold !important;
    }
    
    /* Abas */
    button[data-baseweb="tab"] { color: #a0c0b5 !important; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #d4af37 !important; font-weight: bold; }

    /* Correção do Pop-up de Lançamento (Dialog) */
    div[data-testid="stDialog"] label, 
    div[data-testid="stDialog"] p,
    div[data-testid="stDialog"] span { 
        color: #111111 !important; 
    }
    div[data-testid="stDialog"] input {
        color: #111111 !important;
        background-color: #ffffff !important;
    }
    
    /* Botões Padrão */
    .stButton>button {
        background-color: #d4af37 !important; color: #111111 !important;
        font-weight: bold !important; border-radius: 8px !important; width: 100%;
        border: 1px solid #aa8312 !important;
    }
    
    /* Elementos de Layout */
    .cronometro-box { 
        background-color: #07140f; border: 3px solid #d4af37; padding: 15px; border-radius: 12px; margin-bottom: 25px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.4);
        text-align: center;
    }
    
    .chapeu-box {
        background-color: #113223;
        border: 2px dashed #d4af37;
        padding: 12px 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        color: #ffffff !important;
    }
    
    .box-campeao { background-color: #d4af37; padding: 25px; border-radius: 15px; text-align: center; color: #111111 !important; border: 3px solid #ffffff; margin-bottom: 15px; }
    .box-pódio { background-color: #113223; border: 2px solid #d4af37; padding: 15px; border-radius: 10px; text-align: center; margin-top: 10px; }
    .creditos { text-align: center; color: #a0c0b5 !important; font-size: 0.8rem; margin-top: 50px; }

    /* 📊 FORÇAR DIVISÓRIAS BRANCAS DE ALTO CONTRASTE NO ST.TABLE */
    div[data-testid="stTable"] table {
        border: 3px solid #ffffff !important;
        background-color: #113223 !important;
        width: 100%;
    }
    div[data-testid="stTable"] th {
        background-color: #07140f !important;
        color: #d4af37 !important;
        font-weight: bold !important;
        border: 2px solid #ffffff !important;
        text-align: center !important;
        font-size: 1.1rem;
    }
    div[data-testid="stTable"] td {
        color: #ffffff !important;
        border: 2px solid #ffffff !important;
        text-align: center !important;
        font-size: 1.05rem;
    }
    </style>
""", unsafe_allow_html=True)

def obter_ip_da_rede():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return f"http://{ip}:8501"
    except Exception: return "http://localhost:8501"

url_oficial = obter_ip_da_rede()

# --- TRAVA MATEMÁTICA TRUCO ---
def conferir_e_ajustar_valores(s1, s2, t1, t2, n1, n2, mesa_id):
    if (s1 == 2 and s2 == 2) or (s1 < 2 and s2 < 2):
        return True, s1, s2, t1, t2, f"Mesa {mesa_id}: Placar de Sets inválido ({s1}x{s2}). Alguém precisa fechar com exatamente 2 sets."
    if s1 == 2 and s2 == 0:
        t1 = 72 
        if t2 > 46: return True, s1, s2, t1, t2, f"Mesa {mesa_id}: Inconsistência! No 2x0, o perdedor ({n2}) não pode somar mais do que 46 tentos."
    elif s2 == 2 and s1 == 0:
        t2 = 72 
        if t1 > 46: return True, s1, s2, t1, t2, f"Mesa {mesa_id}: Inconsistência! No 2x0, o perdedor ({n1}) não pode somar mais do que 46 tentos."
    elif s1 == 2 and s2 == 1:
        if t1 < 48: return True, s1, s2, t1, t2, f"Mesa {mesa_id}: Inconsistência! Como {n1} fez 2 sets, precisa ter no mínimo 48 tentos."
        if t2 < 24: return True, s1, s2, t1, t2, f"Mesa {mesa_id}: Inconsistência! Como {n2} fez 1 set, precisa ter no mínimo 24 tentos."
    elif s2 == 2 and s1 == 1:
        if t2 < 48: return True, s1, s2, t1, t2, f"Mesa {mesa_id}: Inconsistência! Como {n2} fez 2 sets, precisa ter no mínimo 48 tentos."
        if t1 < 24: return True, s1, s2, t1, t2, f"Mesa {mesa_id}: Inconsistência! Como {n1} fez 1 set, precisa ter no mínimo 24 tentos."
    return False, s1, s2, t1, t2, ""

# --- FUNÇÕES DE ARQUIVO ---
def salvar_estado_no_disco():
    estado = {
        "jogadores": st.session_state.jogadores,
        "torneio_iniciado": st.session_state.torneio_iniciado,
        "rodada_atual": st.session_state.rodada_atual,
        "confrontos": st.session_state.confrontos,
        "jogadores_no_chapeu": list(st.session_state.jogadores_no_chapeu),
        "hora_inicio_rodada": st.session_state.hora_inicio_rodada.isoformat() if st.session_state.hora_inicio_rodada else None,
        "cronometro_ativo": st.session_state.cronometro_ativo,
        "historico_rodadas": st.session_state.historico_rodadas,
        "nome_torneio": st.session_state.get("nome_torneio", "Torneio de Truco do CTG"),
        "em_matamata": st.session_state.em_matamata,
        "fase_matamata": st.session_state.fase_matamata,
        "confrontos_mm": st.session_state.confrontos_mm,
        "campeao": st.session_state.campeao,
        "vice_campeao": st.session_state.vice_campeao,
        "terceiro_lugar": st.session_state.terceiro_lugar,
        "quarto_lugar": st.session_state.quarto_lugar,
        "perdedores_semi": st.session_state.perdedores_semi,
        "salvo_na_galeria": st.session_state.get("salvo_na_galeria", False),
        "placares_rodada_atual": st.session_state.placares_rodada_atual
    }
    if st.session_state.classificacao is not None:
        estado["classificacao"] = st.session_state.classificacao.to_dict(orient="index")
    else: estado["classificacao"] = None
        
    with open(ARQUIVO_BACKUP, "w", encoding="utf-8") as f:
        json.dump(estado, f, ensure_ascii=False, indent=4)

def carregar_estado_do_disco():
    if os.path.exists(ARQUIVO_BACKUP):
        try:
            with open(ARQUIVO_BACKUP, "r", encoding="utf-8") as f:
                estado = json.load(f)
            st.session_state.jogadores = estado.get("jogadores", [])
            st.session_state.torneio_iniciado = estado.get("torneio_iniciado", False)
            st.session_state.rodada_atual = estado.get("rodada_atual", 1)
            st.session_state.confrontos = estado.get("confrontos", [])
            st.session_state.jogadores_no_chapeu = set(estado.get("jogadores_no_chapeu", []))
            st.session_state.historico_rodadas = estado.get("historico_rodadas", {})
            st.session_state.nome_torneio = estado.get("nome_torneio", "Torneio de Truco do CTG")
            st.session_state.em_matamata = estado.get("em_matamata", False)
            st.session_state.fase_matamata = estado.get("fase_matamata", "")
            st.session_state.confrontos_mm = estado.get("confrontos_mm", [])
            st.session_state.campeao = estado.get("campeao", None)
            st.session_state.vice_campeao = estado.get("vice_campeao", None)
            st.session_state.terceiro_lugar = estado.get("terceiro_lugar", None)
            st.session_state.quarto_lugar = estado.get("quarto_lugar", None)
            st.session_state.perdedores_semi = estado.get("perdedores_semi", [])
            st.session_state.salvo_na_galeria = estado.get("salvo_na_galeria", False)
            st.session_state.cronometro_ativo = estado.get("cronometro_ativo", False)
            st.session_state.placares_rodada_atual = estado.get("placares_rodada_atual", {})
            
            if estado.get("hora_inicio_rodada"):
                st.session_state.hora_inicio_rodada = datetime.fromisoformat(estado["hora_inicio_rodada"])
            else: st.session_state.hora_inicio_rodada = None
                
            if estado.get("classificacao") is not None:
                st.session_state.classificacao = pd.DataFrame.from_dict(estado["classificacao"], orient="index")
            else: st.session_state.classificacao = None
        except Exception: pass

# --- CONFIGURAÇÃO INICIAL DE MEMÓRIA ---
valores_padrao = {
    "jogadores": [], "torneio_iniciado": False, "rodada_atual": 1, "classificacao": None,
    "confrontos": [], "jogadores_no_chapeu": set(), "hora_inicio_rodada": None, "cronometro_ativo": False,
    "historico_rodadas": {}, "em_matamata": False, "fase_matamata": "", "confrontos_mm": [],
    "campeao": None, "vice_campeao": None, "terceiro_lugar": None, "quarto_lugar": None, 
    "perdedores_semi": [], "salvo_na_galeria": False, "placares_rodada_atual": {}
}

for chave, valor in valores_padrao.items():
    if chave not in st.session_state:
        st.session_state[chave] = valor

if os.path.exists(ARQUIVO_BACKUP):
    carregar_estado_do_disco()

# --- LÓGICA DE GERAÇÃO DE CONFRONTOS ---
def gerar_rodada_web():
    if st.session_state.rodada_atual == 1:
        lista_rodada = list(st.session_state.jogadores)
        random.shuffle(lista_rodada)
    else:
        df_ord = st.session_state.classificacao.sort_values(by=['Vitorias', 'Sets_Ganhos', 'Saldo_Tentos'], ascending=False)
        lista_rodada = list(df_ord.index)

    st.session_state.confrontos = []
    st.session_state.placares_rodada_atual = {}
    
    if len(lista_rodada) % 2 != 0:
        cand = [j for j in lista_rodada if j not in st.session_state.jogadores_no_chapeu]
        chapeu = random.choice(cand if cand else lista_rodada)
        lista_rodada.remove(chapeu)
        st.session_state.jogadores_no_chapeu.add(chapeu)
        st.session_state.confrontos.append((chapeu, "CHAPÉU (Folga)"))

    contador_mesa = 1
    for i in range(0, len(lista_rodada), 2):
        st.session_state.confrontos.append((lista_rodada[i], lista_rodada[i+1]))
        st.session_state.placares_rodada_atual[str(contador_mesa)] = [0, 0, 0, 0, 0, 0, False]
        contador_mesa += 1
    
    st.session_state.hora_inicio_rodada = None
    st.session_state.cronometro_ativo = False
    salvar_estado_no_disco()

def iniciar_fase_matamata(lista_jogadores, nome_fase):
    st.session_state.em_matamata = True
    st.session_state.fase_matamata = nome_fase
    st.session_state.confrontos_mm = []
    st.session_state.placares_rodada_atual = {}
    
    if nome_fase in ["TERCEIRO_E_FINAL", "FINAL"]:
        # Estrutura tratada individualmente na consolidação da semifinal
        return
        
    n = len(lista_jogadores)
    for i in range(n // 2):
        st.session_state.confrontos_mm.append({"tipo": "normal", "j1": lista_jogadores[i], "j2": lista_jogadores[n - 1 - i]})
        st.session_state.placares_rodada_atual[str(i+1)] = [0, 0, 0, 0, 0, 0, False]
        
    st.session_state.hora_inicio_rodada = None
    st.session_state.cronometro_ativo = False
    salvar_estado_no_disco()

# --- INPUT FLUTUANTE (DIALOG) ---
@st.dialog("💾 Lançar Performance da Mesa")
def dialog_entrada_placares(mesa_id_string, j1, j2):
    st.write(f"Competidores: **{j1}** vs **{j2}**")
    
    valores_salvos = st.session_state.placares_rodada_atual.get(mesa_id_string, [0,0,0,0,0,0,False])
    
    with st.form(key=f"form_isolado_mesa_{mesa_id_string}"):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"🧔 **Jogador 1: {j1}**")
            s1 = st.number_input("Sets Concluídos:", 0, 2, int(valores_salvos[0]), key=f"inp_s1_{mesa_id_string}")
            t1 = st.number_input("Tentos Ganhos:", 0, 72, int(valores_salvos[2]), key=f"inp_t1_{mesa_id_string}")
            f1 = st.number_input("Flores Cantadas:", 0, 20, int(valores_salvos[4]), key=f"inp_f1_{mesa_id_string}")
        with col2:
            st.write(f"🧔 **Jogador 2: {j2}**")
            s2 = st.number_input("Sets Concluídos:", 0, 2, int(valores_salvos[1]), key=f"inp_s2_{mesa_id_string}")
            t2 = st.number_input("Tentos Ganhos:", 0, 72, int(valores_salvos[3]), key=f"inp_t2_{mesa_id_string}")
            f2 = st.number_input("Flores Cantadas:", 0, 20, int(valores_salvos[5]), key=f"inp_f2_{mesa_id_string}")
            
        if st.form_submit_button("Confirmar e Plotar no Telão"):
            bloqueia, ns1, ns2, nt1, nt2, msg = conferir_e_ajustar_valores(s1, s2, t1, t2, j1, j2, mesa_id_string)
            if bloqueia:
                st.error(msg)
            else:
                st.session_state.placares_rodada_atual[mesa_id_string] = [ns1, ns2, nt1, nt2, f1, f2, True]
                salvar_estado_no_disco()
                st.rerun()

# --- HTML/CSS PLANTA BAIXA DA MESA ---
def desenhar_mesa_planta_baixa(j1, j2, mesa_num, s1, t1, f1, s2, t2, f2):
    html_mesa = f"""
    <div style="background-color: #113223; border: 8px solid #5a3825; border-radius: 50px; padding: 20px; display: flex; flex-direction: column; align-items: center; justify-content: space-between; position: relative; box-shadow: inset 0px 0px 40px rgba(0,0,0,0.9), 0px 10px 20px rgba(0,0,0,0.6); height: 410px; box-sizing: border-box; color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin-bottom: 5px;">
        <div style="position: absolute; top: 15px; text-align: center; width: 100%;">
            <div style="font-size: 0.85rem; color: #d4af37; font-weight: bold; letter-spacing: 1px; margin-bottom: 4px;">🧔 JOGADOR 1 (CABECEIRA)</div>
            <div style="background: linear-gradient(135deg, #d4af37, #aa8312); color: #111111; padding: 6px 30px; border-radius: 20px; font-size: 1.2rem; font-weight: bold; display: inline-block; box-shadow: 0px 4px 8px rgba(0,0,0,0.4); border: 1px solid #fff;">
                {j1}
            </div>
        </div>
        <div style="background-color: rgba(7, 20, 15, 0.95); border: 2px solid #d4af37; border-radius: 15px; padding: 12px; width: 85%; margin-top: 95px; text-align: center; box-shadow: 0px 5px 15px rgba(0,0,0,0.5);">
            <div style="font-size: 0.8rem; color: #a0c0b5; font-weight: bold; letter-spacing: 2px; text-transform: uppercase;">
                🎰 CONTRATO MESA DE TRUCO {mesa_num}
            </div>
            <hr style="margin: 8px 0; border: 0; border-top: 1px solid #1c4234;">
            <div style="display: flex; justify-content: space-around; align-items: center; font-family: monospace; font-size: 2rem; font-weight: bold;">
                <div style="color: #d4af37;">{int(s1)}<span style="font-size:1.1rem; color:#fff;">s</span> {int(t1)}<span style="font-size:1.1rem; color:#fff;">t</span></div>
                <div style="font-size: 1rem; color: #d4af37; letter-spacing: 1px;">VS</div>
                <div style="color: #ffffff;">{int(s2)}<span style="font-size:1.1rem; color:#a0c0b5;">s</span> {int(t2)}<span style="font-size:1.1rem; color:#a0c0b5;">t</span></div>
            </div>
            <div style="margin-top: 8px; font-size: 0.95rem; color: #ff4b4b; font-weight: bold; background: rgba(0,0,0,0.3); padding: 4px; border-radius: 6px;">
                🌸 {int(f1)} <span style="font-size:0.75rem; color:#a0c0b5;">fl.</span> &nbsp;&nbsp;|&nbsp;&nbsp; 🌸 {int(f2)} <span style="font-size:0.75rem; color:#a0c0b5;">fl.</span>
            </div>
        </div>
        <div style="position: absolute; bottom: 15px; text-align: center; width: 100%;">
            <div style="background: linear-gradient(135deg, #ffffff, #dcdcdc); color: #111111; padding: 6px 30px; border-radius: 20px; font-size: 1.2rem; font-weight: bold; display: inline-block; box-shadow: 0px 4px 8px rgba(0,0,0,0.4); border: 1px solid #aaa; margin-bottom: 4px;">
                {j2}
            </div>
            <div style="font-size: 0.85rem; color: #ffffff; font-weight: bold; letter-spacing: 1px;">🧔 JOGADOR 2 (CABECEIRA)</div>
        </div>
    </div>
    """
    components.html(html_mesa, height=425, scrolling=False)

# -------------------------------------------------------------------------
# 💾 MENU OPERADOR LATERAL (MODELO OCULTÁVEL)
# -------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## ⚙️ Gestão Técnica")
    senha_inserida = st.text_input("Chave Master:", type="password")
    is_admin = (senha_inserida == CHAVE_ADMINISTRADOR)
    
    if is_admin:
        st.success("⚡ Modo Operador Ativo")
        if st.button("⏱️ Disparar Rodada (45m)"):
            st.session_state.hora_inicio_rodada = datetime.now()
            st.session_state.cronometro_ativo = True
            salvar_estado_no_disco(); st.rerun()
        if st.button("⏹️ Pausar Cronômetro"):
            st.session_state.cronometro_ativo = False
            salvar_estado_no_disco(); st.rerun()
            
        st.markdown("---")
        url_torneio = st.text_input("IP Rede Local:", value=st.session_state.get("url_override", url_oficial))
        st.session_state["url_override"] = url_torneio
        
        qr = qrcode.QRCode(version=1, box_size=5, border=1)
        qr.add_data(url_torneio)
        qr.make(fit=True)
        img_qr = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img_qr.save(buf, format="PNG")
        st.image(buf.getvalue(), caption="QR Code Telão Mobile", use_container_width=True)
        
        if st.button("🚨 LIMPAR COMPLETO"):
            if os.path.exists(ARQUIVO_BACKUP): os.remove(ARQUIVO_BACKUP)
            st.session_state.clear(); st.rerun()
    else:
        st.info("Insira a senha técnica para abrir os controles do operador.")

# -------------------------------------------------------------------------
# 🏛️ INTERFACE E ABAS DO TELÃO CENTRAL
# -------------------------------------------------------------------------
st.markdown(f"<h1 style='text-align:center;'>🃏 {st.session_state.get('nome_torneio', 'Torneio de Truco')}</h1>", unsafe_allow_html=True)

aba_arena, aba_tabela, aba_historico = st.tabs(["⚔️ Arena de Confrontos", "📊 Classificação Geral", "📜 Galeria de Campeões"])

# --- ABA 1: ARENA DE CONFRONTOS ---
with aba_arena:
    if not st.session_state.torneio_iniciado:
        st.markdown("### 🎮 Inscrições de Competidores")
        nome_torneio = st.text_input("Nome do Evento:", value=st.session_state.get("nome_torneio", "Torneio de Truco do CTG"))
        if is_admin:
            with st.form(key="form_cad", clear_on_submit=True):
                nj = st.text_input("Nome do Competidor:")
                if st.form_submit_button("➕ Cadastrar") and nj:
                    nj_clean = nj.strip()
                    if nj_clean not in st.session_state.jogadores and nj_clean != "":
                        st.session_state.jogadores.append(nj_clean)
                        salvar_estado_no_disco(); st.rerun()
        
        st.write(f"**Inscritos ({len(st.session_state.jogadores)}):**")
        st.info(", ".join(st.session_state.jogadores) if st.session_state.jogadores else "Nenhum competidor cadastrado ainda.")
        
        if is_admin and len(st.session_state.jogadores) >= 4:
            if st.button("🃏 DISPARAR TORNEIO OFICIAL"):
                st.session_state.nome_torneio = nome_torneio
                st.session_state.classificacao = pd.DataFrame({'Jogador': st.session_state.jogadores, 'Vitorias': 0, 'Sets_Ganhos': 0, 'Tentos_Pro': 0, 'Tentos_Contra': 0, 'Saldo_Tentos': 0, 'Flores': 0}).set_index('Jogador')
                st.session_state.torneio_iniciado = True
                gerar_rodada_web(); st.rerun()
    else:
        if not st.session_state.campeao and st.session_state.cronometro_ativo and st.session_state.hora_inicio_rodada:
            tl = st.session_state.hora_inicio_rodada + timedelta(minutes=45)
            ta = datetime.now()
            if ta < tl:
                tr = tl - ta
                st.markdown(f'<div class="cronometro-box"><h2>⏱️ TEMPO RESTANTE DA RODADA: {int(tr.total_seconds()//60):02d}:{int(tr.total_seconds()%60):02d}</h2></div>', unsafe_allow_html=True)
            else: st.markdown('<div class="cronometro-box"><h2 style="color:#ff4b4b !important;">⏰ TEMPO ESGOTADO!</h2></div>', unsafe_allow_html=True)
            
        if st.session_state.campeao:
            st.markdown(f'<div class="box-campeao"><h1>🥇 CAMPEÃO: {st.session_state.campeao}</h1></div>', unsafe_allow_html=True)
            st.markdown(f"""
                <div class="box-pódio">
                    <h3>🥈 VICE-CAMPEÃO: {st.session_state.vice_campeao}</h3>
                    <h4>🥉 3º LUGAR: {st.session_state.terceiro_lugar} | 🏅 4º LUGAR: {st.session_state.quarto_lugar}</h4>
                </div>
            """, unsafe_allow_html=True)
        
        elif st.session_state.em_matamata:
            st.markdown(f"### ⚡ Eliminatórias: {st.session_state.fase_matamata}")
            for idx, c in enumerate(st.session_state.confrontos_mm):
                j1, j2 = c["j1"], c["j2"]
                m_str = str(idx + 1)
                p = st.session_state.placares_rodada_atual.get(m_str, [0,0,0,0,0,0,False])
                
                label_mesa = f"MESA {m_str} - {st.session_state.fase_matamata}"
                if c["tipo"] == "3place": label_mesa = "🥉 DISPUTA DE TERCEIRO LUGAR"
                if c["tipo"] == "final": label_mesa = "🥇 GRANDE FINAL"
                
                st.write(f"**{label_mesa}**")
                desenhar_mesa_planta_baixa(j1, j2, m_str, p[0], p[2], p[4], p[1], p[3], p[5])
                if is_admin:
                    if st.button(f"✏️ Lançar Mesa {m_str}", key=f"btn_mm_{m_str}"):
                        dialog_entrada_placares(m_str, j1, j2)
                        
        else:
            st.markdown(f"### 📅 Classificatória: Rodada {st.session_state.rodada_atual} de 5")
            
            for j1, j2 in st.session_state.confrontos:
                if j2 == "CHAPÉU (Folga)":
                    st.markdown(f"""
                        <div class="chapeu-box">
                            <span style="font-size: 1.2rem; color: #d4af37; font-weight: bold;">🎩 JOGADOR NO CHAPÉU:</span> 
                            <span style="font-size: 1.3rem; color: #ffffff; font-weight: bold; background-color: #07140f; padding: 4px 12px; border-radius: 6px; border: 1px solid #d4af37;">{j1}</span>
                            <br><span style="font-size: 0.9rem; color: #a0c0b5; display:inline-block; margin-top:6px;">Este competidor está de folga nesta rodada e soma +1 Vitória (3 Sets e 72 Tentos Pró) automaticamente.</span>
                        </div>
                    """, unsafe_allow_html=True)
            
            contador_real_mesa = 1
            for j1, j2 in st.session_state.confrontos:
                if j2 != "CHAPÉU (Folga)":
                    m_str = str(contador_real_mesa)
                    p = st.session_state.placares_rodada_atual.get(m_str, [0,0,0,0,0,0,False])
                    
                    desenhar_mesa_planta_baixa(j1, j2, m_str, p[0], p[2], p[4], p[1], p[3], p[5])
                    
                    if is_admin:
                        if st.button(f"✏️ Lançar Mesa {m_str}", key=f"btn_cl_{m_str}"):
                            dialog_entrada_placares(m_str, j1, j2)
                    contador_real_mesa += 1
            
        # 🚨 SEÇÃO DO BOTÃO DE FECHAMENTO (CORRIGIDA: FORA DOS ESCREVES EXCLUSIVOS DA CLASSIFICATÓRIA)
        if is_admin and not st.session_state.campeao:
            st.markdown("---")
            if not st.session_state.em_matamata:
                # Botão Clássico da Fase Classificatória
                if st.button("🏁 Fechar e Salvar Rodada Atual", type="primary"):
                    contador_consolidacao = 1
                    for j1, j2 in st.session_state.confrontos:
                        if j2 == "CHAPÉU (Folga)":
                            st.session_state.classificacao.loc[j1, ['Vitorias', 'Sets_Ganhos', 'Tentos_Pro']] += [1, 3, 72]
                        else:
                            m_str = str(contador_consolidacao)
                            p = st.session_state.placares_rodada_atual.get(m_str, [0,0,0,0,0,0,False])
                            s1_c = 3 if (p[0] == 2 and p[1] == 0) else p[0]
                            s2_c = 3 if (p[1] == 2 and p[0] == 0) else p[1]
                            st.session_state.classificacao.loc[j1, ['Vitorias', 'Sets_Ganhos', 'Tentos_Pro', 'Tentos_Contra', 'Flores']] += [(1 if p[0] > p[1] else 0), s1_c, p[2], p[3], p[4]]
                            st.session_state.classificacao.loc[j2, ['Vitorias', 'Sets_Ganhos', 'Tentos_Pro', 'Tentos_Contra', 'Flores']] += [(1 if p[1] > p[0] else 0), s2_c, p[3], p[2], p[5]]
                            contador_consolidacao += 1
                    
                    st.session_state.classificacao['Saldo_Tentos'] = st.session_state.classificacao['Tentos_Pro'] - st.session_state.classificacao['Tentos_Contra']
                    st.session_state.rodada_atual += 1
                    if st.session_state.rodada_atual <= 5: 
                        gerar_rodada_web()
                    else:
                        st.success("Fim das 5 rodadas classificatórias!")
                        n_insc = len(st.session_state.jogadores)
                        f_nome = "OITAVAS" if n_insc > 16 else ("QUARTAS" if n_insc >= 8 else "SEMIFINAL")
                        df_v = st.session_state.classificacao.sort_values(by=['Vitorias', 'Sets_Ganhos', 'Saldo_Tentos'], ascending=False)
                        iniciar_fase_matamata(list(df_v.index[:16 if n_insc > 16 else (8 if n_insc >= 8 else 4)]), f_nome)
                    st.rerun()
            else:
                # ⚔️ NOVO: Botão Dinâmico de Avanço Exclusivo para as Eliminatórias
                if st.button("🏆 Consolidar Eliminatória e Avançar", type="primary"):
                    vencedores = []
                    perdedores = []
                    
                    # Analisar quem ganhou cada mesa do Mata-Mata atual
                    for idx, c in enumerate(st.session_state.confrontos_mm):
                        m_str = str(idx + 1)
                        p = st.session_state.placares_rodada_atual.get(m_str, [0,0,0,0,0,0,False])
                        
                        # Se não jogaram, assume vitória do Jogador 1 para não travar o script
                        if p[0] >= p[1]:
                            win, los = c["j1"], c["j2"]
                        else:
                            win, los = c["j2"], c["j1"]
                            
                        if c["tipo"] == "normal":
                            vencedores.append(win)
                            perdedores.append(los)
                        elif c["tipo"] == "3place":
                            st.session_state.terceiro_lugar = win
                            st.session_state.quarto_lugar = los
                        elif c["tipo"] == "final":
                            st.session_state.campeao = win
                            st.session_state.vice_campeao = los
                    
                    # Controlar o fluxo das próximas fases
                    fase_atual = st.session_state.fase_matamata
                    st.session_state.placares_rodada_atual = {}
                    
                    if fase_atual == "OITAVAS":
                        iniciar_fase_matamata(vencedores, "QUARTAS")
                    elif fase_atual == "QUARTAS":
                        iniciar_fase_matamata(vencedores, "SEMIFINAL")
                    elif fase_atual == "SEMIFINAL":
                        # Na Semifinal, geramos a estrutura casada (Disputa de 3º na Mesa 1, Final na Mesa 2)
                        st.session_state.fase_matamata = "FINAL E TERCEIRO"
                        st.session_state.confrontos_mm = [
                            {"tipo": "3place", "j1": perdedores[0], "j2": perdedores[1]},
                            {"tipo": "final", "j1": vencedores[0], "j2": vencedores[1]}
                        ]
                        st.session_state.placares_rodada_atual["1"] = [0,0,0,0,0,0,False]
                        st.session_state.placares_rodada_atual["2"] = [0,0,0,0,0,0,False]
                    elif fase_atual == "FINAL E TERCEIRO":
                        # Gravar na galeria histórico geral se existirem os dados
                        if st.session_state.campeao:
                            registro = {
                                "Data": datetime.now().strftime("%d/%m/%Y"),
                                "Torneio": st.session_state.nome_torneio,
                                "Campeão": st.session_state.campeao,
                                "Vice": st.session_state.vice_campeao,
                                "3º Lugar": st.session_state.terceiro_lugar
                            }
                            dg = []
                            if os.path.exists(ARQUIVO_GALERIA):
                                try:
                                    with open(ARQUIVO_GALERIA, "r", encoding="utf-8") as f: dg = json.load(f)
                                except Exception: dg = []
                            dg.append(registro)
                            with open(ARQUIVO_GALERIA, "w", encoding="utf-8") as f:
                                json.dump(dg, f, ensure_ascii=False, indent=4)
                    
                    salvar_estado_no_disco()
                    st.rerun()

# --- ABA 2: CLASSIFICAÇÃO GERAL AO VIVO ---
with aba_tabela:
    st.markdown("### 📊 Tabela de Classificação Atualizada")
    if st.session_state.classificacao is not None:
        df_rank = st.session_state.classificacao.sort_values(by=['Vitorias', 'Sets_Ganhos', 'Saldo_Tentos'], ascending=False)
        st.table(df_rank)
    else:
        st.info("O torneio ainda não foi iniciado. Aguardando competidores.")

# --- ABA 3: HISTÓRICO / GALERIA DE CAMPEÕES ---
with aba_historico:
    st.markdown("### 🏛️ Galeria de Honra (Torneios Passados)")
    if os.path.exists(ARQUIVO_GALERIA):
        with open(ARQUIVO_GALERIA, "r", encoding="utf-8") as f: dg = json.load(f)
        if dg: 
            st.table(pd.DataFrame(dg))
        else:
            st.info("Nenhum registro encontrado na galeria até o momento.")
    else:
        st.info("Nenhum registro encontrado na galeria até o momento.")

st.markdown(f'<div class="creditos">💻 {NOME_CRIADOR} © 2026</div>', unsafe_allow_html=True)
