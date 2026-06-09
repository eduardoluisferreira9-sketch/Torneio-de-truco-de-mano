import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import random
import json
import os
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

icone_pagina = "🃏" 
try:
    resposta = requests.get(f"{URL_BASE_IMAGENS}/baralho_espanhol.png", timeout=5)
    if resposta.status_code == 200:
        icone_pagina = Image.open(BytesIO(resposta.content))
except Exception:
    pass

# 🛠️ ESTILIZAÇÃO CSS ATUALIZADA (FUNDO VERDE FELTRO DE MESA E MÁXIMO CONTRASTE)
st.markdown("""
    <style>
    /* Suavizado para o verde feltro tradicional de mesa de cartas */
    .stApp { background-color: #1e4d3a; } 
    
    section[data-testid="stSidebar"] {
        background-color: #0f2b20;
        border-right: 2px solid #2d6b52;
    }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2 { color: #d4af37; }
    
    h1, h2, h3, h4, h5, p, label, .stText, [data-testid="stMarkdownContainer"] p { 
        color: #ffffff !important; 
    }
    
    /* Força os títulos dos passos do painel administrativo a ficarem Brancos e visíveis */
    .titulo-passo-admin {
        color: #ffffff !important;
        font-weight: bold !important;
        margin-top: 10px !important;
        margin-bottom: 10px !important;
    }
    
    div[data-testid="stNotification"] p {
        color: #ffffff !important;
        font-weight: bold !important;
    }
    
    /* Títulos de Mesas e Fases com Destaque Forte */
    .titulo-mesa-destaque {
        color: #d4af37 !important;
        font-size: 1.6rem !important;
        font-weight: bold !important;
        border-left: 5px solid #d4af37;
        padding-left: 10px;
        margin-top: 20px;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Inputs de Texto (Tentos 2x1) */
    div[data-testid="stTextInput"] input {
        color: #ffffff !important;
        background-color: #0f2b20 !important;
        border: 2px solid #d4af37 !important;
        text-align: center !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
    }
    
    /* Inputs Numéricos */
    div[data-testid="stNumberInput"] input {
        color: #ffffff !important;
        background-color: #0f2b20 !important;
        border: 2px solid #d4af37 !important;
        text-align: center !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        height: 35px !important;
    }
    
    /* Labels acima das caixas de texto e números totalmente Brancos */
    div[data-testid="stNumberInput"] label, div[data-testid="stTextInput"] label {
        color: #ffffff !important;
        font-size: 0.95rem !important;
        font-weight: bold !important;
    }
    
    button[data-baseweb="tab"] { color: #bfe3d5 !important; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #d4af37 !important; font-weight: bold; }
    
    .stButton>button {
        background-color: #d4af37 !important; color: #111111 !important;
        font-weight: bold !important; border-radius: 8px !important; width: 100%;
        border: 1px solid #aa8312 !important;
        font-size: 1.1rem !important;
    }
    
    .cronometro-box { 
        background-color: #0f2b20; border: 3px solid #d4af37; padding: 15px; border-radius: 12px; margin-bottom: 25px;
        text-align: center;
    }
    
    .chapeu-box {
        background-color: #265c45; border: 2px dashed #d4af37; padding: 12px 20px; border-radius: 10px; margin-bottom: 20px;
    }
    
    /* Pódio Atualizado */
    .podio-container { display: flex; flex-direction: column; gap: 15px; width: 100%; align-items: center; margin-top: 20px; }
    .card-campeao { background: linear-gradient(135deg, #d4af37, #aa8312); color: #000 !important; width: 80%; padding: 30px; border-radius: 20px; text-align: center; border: 5px solid #fff; box-shadow: 0px 10px 30px rgba(0,0,0,0.5); }
    .card-vice { background-color: #0f2b20; color: #fff !important; width: 70%; padding: 20px; border-radius: 15px; text-align: center; border: 3px solid #c0c0c0; }
    .honor-row { display: flex; gap: 15px; width: 70%; justify-content: center; }
    .card-terceiro { background-color: #0f2b20; color: #fff !important; flex: 1; padding: 15px; border-radius: 10px; text-align: center; border: 2px solid #cd7f32; }
    .card-quarto { background-color: #0f2b20; color: #fff !important; flex: 1; padding: 15px; border-radius: 10px; text-align: center; border: 2px solid #2d6b52; }
    .card-flor { background-color: #ff69b4; color: #000 !important; width: 60%; padding: 10px; border-radius: 50px; text-align: center; font-weight: bold; margin-top: 20px; border: 2px solid #fff; }
    
    .box-auditoria { background-color: #0f2b20; border: 2px solid #2d6b52; padding: 20px; border-radius: 10px; margin-top: 30px; }
    
    .creditos { text-align: center; color: #ffffff !important; font-size: 0.8rem; margin-top: 50px; }

    div[data-testid="stTable"] table { border: 3px solid #ffffff !important; background-color: #265c45 !important; width: 100%; }
    div[data-testid="stTable"] th { background-color: #0f2b20 !important; color: #d4af37 !important; border: 2px solid #ffffff !important; text-align: center !important; }
    div[data-testid="stTable"] td { color: #ffffff !important; border: 2px solid #ffffff !important; text-align: center !important; }
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÃO DE LIMPEZA DE MEMÓRIA (RESET DE CAMPOS) ---
def limpar_placares_memoria():
    st.session_state.placares_rodada_atual = {}
    if "semente_reset" not in st.session_state:
        st.session_state.semente_reset = 1
    else:
        st.session_state.semente_reset += 1
        
    chaves_para_remover = [k for k in st.session_state.keys() if k.startswith("dir_s") or k.startswith("dir_t") or k.startswith("dir_f")]
    for k in chaves_para_remover:
        del st.session_state[k]

def obter_ip_da_rede():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return f"http://{ip}:8501"
    except Exception: return "http://localhost:8501"

url_oficial = obter_ip_da_rede()

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
        "nome_torneio": st.session_state.get("nome_torneio", "Torneio de Truco"),
        "em_matamata": st.session_state.em_matamata,
        "fase_matamata": st.session_state.fase_matamata,
        "confrontos_mm": st.session_state.confrontos_mm,
        "campeao": st.session_state.campeao,
        "vice_campeao": st.session_state.vice_campeao,
        "terceiro_lugar": st.session_state.terceiro_lugar,
        "quarto_lugar": st.session_state.quarto_lugar,
        "placares_rodada_atual": st.session_state.placares_rodada_atual,
        "semente_reset": st.session_state.get("semente_reset", 1)
    }
    if st.session_state.classificacao is not None:
        estado["classificacao"] = st.session_state.classificacao.to_dict(orient="index")
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
            st.session_state.em_matamata = estado.get("em_matamata", False)
            st.session_state.fase_matamata = estado.get("fase_matamata", "")
            st.session_state.confrontos_mm = estado.get("confrontos_mm", [])
            st.session_state.campeao = estado.get("campeao", None)
            st.session_state.vice_campeao = estado.get("vice_campeao", None)
            st.session_state.terceiro_lugar = estado.get("terceiro_lugar", None)
            st.session_state.quarto_lugar = estado.get("quarto_lugar", None)
            st.session_state.historico_rodadas = estado.get("historico_rodadas", {})
            st.session_state.placares_rodada_atual = estado.get("placares_rodada_atual", {})
            st.session_state.semente_reset = estado.get("semente_reset", 1)
            if estado.get("classificacao") is not None:
                st.session_state.classificacao = pd.DataFrame.from_dict(estado["classificacao"], orient="index")
            if estado.get("hora_inicio_rodada"):
                st.session_state.hora_inicio_rodada = datetime.fromisoformat(estado["hora_inicio_rodada"])
        except Exception: pass

# --- INICIALIZAÇÃO ---
if "jogadores" not in st.session_state:
    st.session_state.jogadores = []
    st.session_state.torneio_iniciado = False
    st.session_state.rodada_atual = 1
    st.session_state.classificacao = None
    st.session_state.confrontos = []
    st.session_state.jogadores_no_chapeu = set()
    st.session_state.hora_inicio_rodada = None
    st.session_state.cronometro_ativo = False
    st.session_state.em_matamata = False
    st.session_state.fase_matamata = ""
    st.session_state.confrontos_mm = []
    st.session_state.campeao = None
    st.session_state.vice_campeao = None
    st.session_state.terceiro_lugar = None
    st.session_state.quarto_lugar = None
    st.session_state.historico_rodadas = {}
    st.session_state.placares_rodada_atual = {}
    st.session_state.semente_reset = 1

carregar_estado_do_disco()

# --- RECALCULADOR MATRIZ ---
def reconstruir_classificacao_global():
    st.session_state.classificacao = pd.DataFrame({
        'Jogador': st.session_state.jogadores, 'Vitorias': 0, 'Sets_Ganhos': 0, 
        'Tentos_Pro': 0, 'Tentos_Contra': 0, 'Saldo_Tentos': 0, 'Flores': 0
    }).set_index('Jogador')
    
    for r_num, mesas in st.session_state.historico_rodadas.items():
        for m_id, dados in mesas.items():
            if dados.get("is_chapeu", False):
                st.session_state.classificacao.loc[dados["j1"], ['Vitorias', 'Sets_Ganhos', 'Tentos_Pro']] += [1, 3, 72]
            else:
                j1, j2 = dados["j1"], dados["j2"]
                s1, s2, t1, t2, f1, f2 = dados["s1"], dados["s2"], dados["t1"], dados["t2"], dados["f1"], dados["f2"]
                
                s1_c = 3 if (s1 == 2 and s2 == 0) else s1
                s2_c = 3 if (s2 == 2 and s1 == 0) else s2
                
                v1 = 1 if s1 > s2 else 0
                v2 = 1 if s2 > s1 else 0
                
                st.session_state.classificacao.loc[j1, ['Vitorias','Sets_Ganhos','Tentos_Pro','Tentos_Contra','Flores']] += [v1, s1_c, t1, t2, f1]
                st.session_state.classificacao.loc[j2, ['Vitorias','Sets_Ganhos','Tentos_Pro','Tentos_Contra','Flores']] += [v2, s2_c, t2, t1, f2]
                
    st.session_state.classificacao['Saldo_Tentos'] = st.session_state.classificacao['Tentos_Pro'] - st.session_state.classificacao['Tentos_Contra']
    salvar_estado_no_disco()

# --- LÓGICA DE RODADAS ---
def gerar_rodada_web():
    limpar_placares_memoria()
    if st.session_state.rodada_atual == 1:
        lista_rodada = list(st.session_state.jogadores)
        random.shuffle(lista_rodada)
    else:
        df_ord = st.session_state.classificacao.sort_values(by=['Vitorias', 'Sets_Ganhos', 'Saldo_Tentos'], ascending=False)
        lista_rodada = list(df_ord.index)

    st.session_state.confrontos = []
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
    limpar_placares_memoria()
    st.session_state.em_matamata = True
    st.session_state.fase_matamata = nome_fase
    st.session_state.confrontos_mm = []
    
    if nome_fase == "FINAL E TERCEIRO": return 

    n = len(lista_jogadores)
    for i in range(n // 2):
        id_m = str(i+1)
        st.session_state.confrontos_mm.append({"id_original": id_m, "tipo": "normal", "j1": lista_jogadores[i], "j2": lista_jogadores[n-1-i]})
        st.session_state.placares_rodada_atual[id_m] = [0, 0, 0, 0, 0, 0, False]
    
    st.session_state.hora_inicio_rodada = None
    st.session_state.cronometro_ativo = False
    salvar_estado_no_disco()

# --- DISPARADOR DE ATUALIZAÇÃO ---
def disparar_atualizacao_placar(m_str, j1, j2):
    sem = st.session_state.get("semente_reset", 1)
    s1 = st.session_state[f"dir_s1_{m_str}_r{sem}"]
    s2 = st.session_state[f"dir_s2_{m_str}_r{sem}"]
    
    p_antigo = st.session_state.placares_rodada_atual.get(m_str, [0, 0, 0, 0, 0, 0, False])
    
    if (s1 == 2 and s2 == 0):
        t1 = 72
        t2 = st.session_state.get(f"dir_t2_{m_str}_r{sem}_2x0j1", p_antigo[3])
        if t2 > 46: t2 = 46
    elif (s2 == 2 and s1 == 0):
        t2 = 72
        t1 = st.session_state.get(f"dir_t1_{m_str}_r{sem}_2x0j2", p_antigo[2])
        if t1 > 46: t1 = 46
    else:
        t1_raw = st.session_state.get(f"dir_t1_{m_str}_r{sem}_2x1", "")
        t2_raw = st.session_state.get(f"dir_t2_{m_str}_r{sem}_2x1", "")
        
        try: t1 = int(t1_raw) if t1_raw.strip() != "" else 0
        except ValueError: t1 = 0
            
        try: t2 = int(t2_raw) if t2_raw.strip() != "" else 0
        except ValueError: t2 = 0

    f1 = st.session_state.get(f"dir_f1_{m_str}_r{sem}", p_antigo[4])
    f2 = st.session_state.get(f"dir_f2_{m_str}_r{sem}", p_antigo[5])
    
    st.session_state.placares_rodada_atual[m_str] = [s1, s2, t1, t2, f1, f2, True]
    salvar_estado_no_disco()

# --- CALLBACK PARA EDICAO RETROATIVA ---
def salvar_mudanca_retroativa(r_alvo, m_id, j1, j2):
    st.session_state.historico_rodadas[r_alvo][m_id]["s1"] = st.session_state[f"ret_s1_{r_alvo}_{m_id}"]
    st.session_state.historico_rodadas[r_alvo][m_id]["t1"] = st.session_state[f"ret_t1_{r_alvo}_{m_id}"]
    st.session_state.historico_rodadas[r_alvo][m_id]["f1"] = st.session_state[f"ret_f1_{r_alvo}_{m_id}"]
    st.session_state.historico_rodadas[r_alvo][m_id]["s2"] = st.session_state[f"ret_s2_{r_alvo}_{m_id}"]
    st.session_state.historico_rodadas[r_alvo][m_id]["t2"] = st.session_state[f"ret_t2_{r_alvo}_{m_id}"]
    st.session_state.historico_rodadas[r_alvo][m_id]["f2"] = st.session_state[f"ret_f2_{r_alvo}_{m_id}"]
    reconstruir_classificacao_global()

# --- DESENHO DA MESA DO TORNEIO ---
def desenhar_mesa_planta_baixa(j1, j2, mesa_num, s1, t1, f1, s2, t2, f2):
    html_mesa = f"""
    <div style="background-color: #265c45; border: 8px solid #5a3825; border-radius: 50px; padding: 20px; display: flex; flex-direction: column; align-items: center; justify-content: space-between; position: relative; box-shadow: inset 0px 0px 40px rgba(0,0,0,0.8), 0px 10px 20px rgba(0,0,0,0.4); height: 410px; box-sizing: border-box; color: #ffffff; font-family: sans-serif; margin-bottom: 5px;">
        <div style="position: absolute; top: 15px; text-align: center; width: 100%;">
            <div style="font-size: 0.85rem; color: #d4af37; font-weight: bold;">🧔 JOGADOR 1</div>
            <div style="background: linear-gradient(135deg, #d4af37, #aa8312); color: #000; padding: 8px 30px; border-radius: 20px; font-size: 1.2rem; font-weight: bold; display: inline-block; border: 1px solid #fff;">{j1}</div>
        </div>
        <div style="background-color: rgba(15, 43, 32, 0.95); border: 2px solid #d4af37; border-radius: 15px; padding: 12px; width: 85%; margin-top: 95px; text-align: center;">
            <div style="font-size: 0.85rem; color: #d4af37; font-weight: bold; letter-spacing: 2px;">🎰 MESA {mesa_num}</div>
            <hr style="margin: 8px 0; border-top: 1px solid #2d6b52;">
            <div style="display: flex; justify-content: space-around; align-items: center; font-size: 2rem; font-weight: bold;">
                <div style="color: #d4af37;">{int(s1)}<span style="font-size:1.1rem;">s</span> {int(t1)}<span style="font-size:1.1rem;">t</span></div>
                <div style="font-size: 1rem; color: #d4af37;">VS</div>
                <div style="color: #fff;">{int(s2)}<span style="font-size:1.1rem;">s</span> {int(t2)}<span style="font-size:1.1rem;">t</span></div>
            </div>
            <div style="margin-top: 8px; font-size: 0.95rem; color: #ff69b4; font-weight: bold;">🌸 {int(f1)} fl. &nbsp;|&nbsp; 🌸 {int(f2)} fl.</div>
        </div>
        <div style="position: absolute; bottom: 15px; text-align: center; width: 100%;">
            <div style="background: linear-gradient(135deg, #fff, #dcdcdc); color: #000; padding: 8px 30px; border-radius: 20px; font-size: 1.2rem; font-weight: bold; display: inline-block; border: 1px solid #aaa;">{j2}</div>
            <div style="font-size: 0.85rem; color: #fff; font-weight: bold;">🧔 JOGADOR 2</div>
        </div>
    </div>
    """
    components.html(html_mesa, height=425, scrolling=False)

# --- CONFIGURAÇÃO DO FORMULÁRIO DO PAINEL DE CONTROLE DE ENTRADAS ---
def renderizar_formulario_mesa_admin(m, j1, j2, sem_id):
    p = st.session_state.placares_rodada_atual.get(m, [0,0,0,0,0,0,False])
    s1, s2, t1, t2, f1, f2 = p[0], p[1], p[2], p[3], p[4], p[5]
    
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.markdown(f"<h4 class='titulo-passo-admin'>• SETS (Passo 1)</h4>", unsafe_allow_html=True)
        s1_in = st.number_input(f"Sets - {j1}", 0, 2, int(s1), key=f"dir_s1_{m}_r{sem_id}", on_change=disparar_atualizacao_placar, args=(m, j1, j2))
        s2_in = st.number_input(f"Sets - {j2}", 0, 2, int(s2), key=f"dir_s2_{m}_r{sem_id}", on_change=disparar_atualizacao_placar, args=(m, j1, j2))

    jogo_encerrado = (s1_in == 2 or s2_in == 2)
    
    with c2:
        if not jogo_encerrado:
            st.warning("Definir os Sets para liberar os Tentos.")
        else:
            st.markdown(f"<h4 class='titulo-passo-admin'>• TENTOS (Passo 2)</h4>", unsafe_allow_html=True)
            
            # CASO 1: Vencedor por 2x0 seco (Jogador 1)
            if s1_in == 2 and s2_in == 0:
                st.info(f"{j1} 2x0. Fixo 72.")
                st.number_input(f"Tentos - {j1}", 72, 72, 72, key=f"dir_t1_{m}_r{sem_id}_2x0j1", disabled=True)
                st.number_input(f"Tentos - {j2} (Máx: 46)", 0, 46, min(int(t2), 46), key=f"dir_t2_{m}_r{sem_id}_2x0j1", on_change=disparar_atualizacao_placar, args=(m, j1, j2))
            
            # CASO 2: Vencedor por 2x0 seco (Jogador 2)
            elif s2_in == 2 and s1_in == 0:
                st.number_input(f"Tentos - {j1} (Máx: 46)", 0, 46, min(int(t1), 46), key=f"dir_t1_{m}_r{sem_id}_2x0j2", on_change=disparar_atualizacao_placar, args=(m, j1, j2))
                st.info(f"{j2} 2x0. Fixo 72.")
                st.number_input(f"Tentos - {j2}", 72, 72, 72, key=f"dir_t2_{m}_r{sem_id}_2x0j2", disabled=True)
                
            # CASO 3: Cenário 2x1 solicitado: Traz caixas de texto Totalmente VAZIAS!
            else:
                t1_val_str = "" if (t1 == 72 or t1 == 0) else str(t1)
                t2_val_str = "" if (t2 == 72 or t2 == 0) else str(t2)
                
                st.text_input(f"Digite Tentos - {j1}", value=t1_val_str, key=f"dir_t1_{m}_r{sem_id}_2x1", on_change=disparar_atualizacao_placar, args=(m, j1, j2), placeholder="Em branco - Digite...")
                st.text_input(f"Digite Tentos - {j2}", value=t2_val_str, key=f"dir_t2_{m}_r{sem_id}_2x1", on_change=disparar_atualizacao_placar, args=(m, j1, j2), placeholder="Em branco - Digite...")
            
            st.markdown(f"<h4 class='titulo-passo-admin'>• FLORES (Passo 3)</h4>", unsafe_allow_html=True)
            st.number_input(f"Flores - {j1}", 0, 20, int(f1), key=f"dir_f1_{m}_r{sem_id}", on_change=disparar_atualizacao_placar, args=(m, j1, j2))
            st.number_input(f"Flores - {j2}", 0, 20, int(f2), key=f"dir_f2_{m}_r{sem_id}", on_change=disparar_atualizacao_placar, args=(m, j1, j2))

# --- BARRA LATERAL ---
with st.sidebar:
    st.markdown("## ⚙️ Gestão Técnico")
    senha = st.text_input("Chave Master:", type="password")
    is_admin = (senha == CHAVE_ADMINISTRADOR)
    if is_admin:
        if st.button("⏱️ Disparar Rodada (45m)"):
            st.session_state.hora_inicio_rodada = datetime.now()
            st.session_state.cronometro_ativo = True
            salvar_estado_no_disco(); st.rerun()
        if st.button("⏹️ Pausar Cronômetro"):
            st.session_state.cronometro_ativo = False
            salvar_estado_no_disco(); st.rerun()
        st.markdown("---")
        if st.button("🗑️ Limpar Galeria de Campeões", type="secondary"):
            if os.path.exists(ARQUIVO_GALERIA): os.remove(ARQUIVO_GALERIA)
            st.success("Galeria de campeões resetada com sucesso!")
            st.rerun()
        if st.button("🚨 LIMPAR COMPLETO (Reset Torneio)"):
            if os.path.exists(ARQUIVO_BACKUP): os.remove(ARQUIVO_BACKUP)
            st.session_state.clear(); st.rerun()

# --- INTERFACE PRINCIPAL ---
st.markdown(f"<h1 style='text-align:center;'>🃏 {st.session_state.get('nome_torneio', 'Torneio de Truco')}</h1>", unsafe_allow_html=True)
aba_arena, aba_tabela, aba_historico = st.tabs(["⚔️ Arena de Confrontos", "📊 Classificação Geral", "📜 Galeria de Campeões"])

with aba_arena:
    if not st.session_state.torneio_iniciado:
        st.markdown("### 🎮 Inscrições de Competidores")
        nome_t = st.text_input("Nome do Evento:", value="Torneio de Truco do CTG")
        if is_admin:
            with st.form("cad", clear_on_submit=True):
                nj = st.text_input("Nome do Competidor:")
                if st.form_submit_button("➕ Cadastrar") and nj:
                    st.session_state.jogadores.append(nj.strip())
                    salvar_estado_no_disco(); st.rerun()
        st.write(f"**Inscritos ({len(st.session_state.jogadores)}):**")
        st.info(", ".join(st.session_state.jogadores) if st.session_state.jogadores else "Vazio.")
        if is_admin and len(st.session_state.jogadores) >= 4:
            if st.button("🃏 DISPARAR TORNEIO"):
                st.session_state.nome_torneio = nome_t
                st.session_state.classificacao = pd.DataFrame({'Jogador': st.session_state.jogadores, 'Vitorias': 0, 'Sets_Ganhos': 0, 'Tentos_Pro': 0, 'Tentos_Contra': 0, 'Saldo_Tentos': 0, 'Flores': 0}).set_index('Jogador')
                st.session_state.torneio_iniciado = True
                gerar_rodada_web(); st.rerun()
    else:
        if st.session_state.campeao:
            st.markdown("<h2 style='text-align:center;'>🏆 RESULTADO FINAL</h2>", unsafe_allow_html=True)
            rei_flor_nome = st.session_state.classificacao['Flores'].idxmax()
            rei_flor_val = int(st.session_state.classificacao['Flores'].max())

            st.markdown(f"""
                <div class="podio-container">
                    <div class="card-campeao">
                        <h1 style="font-size: 4rem;">🥇 1º LUGAR</h1>
                        <h2 style="font-size: 3rem;">{st.session_state.campeao}</h2>
                        <p>GRANDE CAMPEÃO DO CTG</p>
                    </div>
                    <div class="card-vice">
                        <h2>🥈 2º LUGAR: {st.session_state.vice_campeao}</h2>
                    </div>
                    <div class="honor-row">
                        <div class="card-terceiro"><h3>🥉 3º: {st.session_state.terceiro_lugar}</h3></div>
                        <div class="card-quarto"><h3>🏅 4º: {st.session_state.quarto_lugar}</h3></div>
                    </div>
                    <div class="card-flor">
                        🌸 REI DA FLOR DO CAMPEONATO: {rei_flor_nome} ({rei_flor_val} flores cantadas)
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if is_admin and st.button("💾 Gravar Campeão na Galeria Histórica"):
                novo_registro = {
                    "Data": datetime.now().strftime("%d/%m/%Y"),
                    "Torneio": st.session_state.nome_torneio,
                    "Campeão": st.session_state.campeao,
                    "Vice": st.session_state.vice_campeao,
                    "Rei da Flor": f"{rei_flor_nome} ({rei_flor_val})"
                }
                lista_g = []
                if os.path.exists(ARQUIVO_GALERIA):
                    try:
                        with open(ARQUIVO_GALERIA, "r", encoding="utf-8") as f: lista_g = json.load(f)
                    except Exception: pass
                lista_g.append(novo_registro)
                with open(ARQUIVO_GALERIA, "w", encoding="utf-8") as f:
                    json.dump(lista_g, f, ensure_ascii=False, indent=4)
                st.success("Campeão imortalizado na galeria!")
        
        else:
            if st.session_state.cronometro_ativo and st.session_state.hora_inicio_rodada:
                tl = st.session_state.hora_inicio_rodada + timedelta(minutes=45)
                tr = tl - datetime.now()
                if tr.total_seconds() > 0:
                    st.markdown(f'<div class="cronometro-box"><h2>⏱️ TEMPO RESTANTE: {int(tr.total_seconds()//60):02d}:{int(tr.total_seconds()%60):02d}</h2></div>', unsafe_allow_html=True)
                else: st.markdown('<div class="cronometro-box"><h2 style="color:red !important;">⏰ TEMPO ESGOTADO!</h2></div>', unsafe_allow_html=True)

            sem_id = st.session_state.get("semente_reset", 1)

            # FASE 1: RODADAS REGULARES (PONTOS CORRIDOS)
            if not st.session_state.em_matamata:
                st.markdown(f"### 📅 Rodada {st.session_state.rodada_atual} de 5")
                for j1, j2 in st.session_state.confrontos:
                    if j2 == "CHAPÉU (Folga)":
                        st.markdown(f"<div class='chapeu-box'>🎩 CHAPÉU: <b>{j1}</b> está de folga.</div>", unsafe_allow_html=True)
                
                cont = 1
                for j1, j2 in st.session_state.confrontos:
                    if j2 != "CHAPÉU (Folga)":
                        m = str(cont)
                        p = st.session_state.placares_rodada_atual.get(m, [0,0,0,0,0,0,False])
                        
                        st.markdown(f'<div class="titulo-mesa-destaque">🎰 MESA {m}</div>', unsafe_allow_html=True)
                        
                        if is_admin:
                            col_painel, col_entradas = st.columns([2, 3])
                            with col_painel: 
                                desenhar_mesa_planta_baixa(j1, j2, m, p[0], p[2], p[4], p[1], p[3], p[5])
                            with col_entradas: 
                                renderizar_formulario_mesa_admin(m, j1, j2, sem_id)
                        else: 
                            desenhar_mesa_planta_baixa(j1, j2, m, p[0], p[2], p[4], p[1], p[3], p[5])
                        cont += 1
                
                if is_admin:
                    st.markdown("### 🏁 Finalizar Etapa")
                    if st.button("Fechar Rodada e Avançar", type="primary"):
                        erro_validacao = False
                        m_c = 1
                        for j1, j2 in st.session_state.confrontos:
                            if j2 != "CHAPÉU (Folga)":
                                p = st.session_state.placares_rodada_atual.get(str(m_c), [0,0,0,0,0,0,False])
                                s1, s2, t1, t2 = p[0], p[1], p[2], p[3]
                                
                                if not (s1 == 2 or s2 == 2):
                                    st.error(f"❌ Erro na Mesa {m_c}: Partida inacabada! Alguém precisa ter 2 sets."); erro_validacao = True
                                
                                if s1 == 2 and s2 == 1:
                                    if t1 < 48: st.error(f"❌ Erro na Mesa {m_c}: No placar de 2x1, quem fez 2 Sets ({j1}) precisa ter no mínimo 48 tentos!"); erro_validacao = True
                                    if t2 < 24: st.error(f"❌ Erro na Mesa {m_c}: No placar de 2x1, quem fez 1 Set ({j2}) precisa ter no mínimo 24 tentos!"); erro_validacao = True
                                elif s2 == 2 and s1 == 1:
                                    if t2 < 48: st.error(f"❌ Erro na Mesa {m_c}: No placar de 2x1, quem fez 2 Sets ({j2}) precisa ter no mínimo 48 tentos!"); erro_validacao = True
                                    if t1 < 24: st.error(f"❌ Erro na Mesa {m_c}: No placar de 2x1, quem fez 1 Set ({j1}) precisa ter no mínimo 24 tentos!"); erro_validacao = True
                                m_c += 1
                                
                        if not erro_validacao:
                            id_rodada_str = str(st.session_state.rodada_atual)
                            st.session_state.historico_rodadas[id_rodada_str] = {}
                            
                            m_c = 1
                            for j1, j2 in st.session_state.confrontos:
                                if j2 == "CHAPÉU (Folga)":
                                    st.session_state.historico_rodadas[id_rodada_str][f"chapeu_{j1}"] = {
                                        "is_chapeu": True, "j1": j1, "j2": "Folga", "s1": 3, "s2": 0, "t1": 72, "t2": 0, "f1": 0, "f2": 0
                                    }
                                else:
                                    p = st.session_state.placares_rodada_atual.get(str(m_c), [0,0,0,0,0,0,False])
                                    st.session_state.historico_rodadas[id_rodada_str][str(m_c)] = {
                                        "is_chapeu": False, "j1": j1, "j2": j2, "s1": p[0], "s2": p[1], "t1": p[2], "t2": p[3], "f1": p[4], "f2": p[5]
                                    }
                                    m_c += 1
                            
                            reconstruir_classificacao_global()
                            st.session_state.rodada_atual += 1
                            
                            if st.session_state.rodada_atual <= 5: gerar_rodada_web()
                            else:
                                n_in = len(st.session_state.jogadores)
                                f_n = "OITAVAS DE FINAL" if n_in > 16 else ("QUARTAS DE FINAL" if n_in >= 8 else "SEMIFINAL")
                                dv = st.session_state.classificacao.sort_values(by=['Vitorias','Sets_Ganhos','Saldo_Tentos'], ascending=False)
                                iniciar_fase_matamata(list(dv.index[:16 if n_in>16 else (8 if n_in>=8 else 4)]), f_n)
                            st.rerun()

            # FASE 2: MATA-MATAS ATÉ A FINAL
            else:
                st.markdown(f"### ⚡ Eliminatórias Correndo: {st.session_state.fase_matamata}")
                lista_m = st.session_state.confrontos_mm
                if st.session_state.fase_matamata == "FINAL E TERCEIRO":
                    lista_m = sorted(st.session_state.confrontos_mm, key=lambda x: 0 if x["tipo"]=="final" else 1)

                for c in lista_m:
                    m = c["id_original"]
                    j1, j2 = c["j1"], c["j2"]
                    p = st.session_state.placares_rodada_atual.get(m, [0,0,0,0,0,0,False])
                    
                    if c["tipo"] == "final":
                        tit = "🏆 GRANDE FINAL DO TORNEIO"
                    elif c["tipo"] == "3place":
                        tit = "🥉 DISPUTA DE 3º E 4º LUGAR"
                    else:
                        tit = f"⚔️ {st.session_state.fase_matamata} - MESA {m}"
                    
                    st.markdown(f'<div class="titulo-mesa-destaque">{tit}</div>', unsafe_allow_html=True)
                    
                    if is_admin:
                        col_p_mm, col_e_mm = st.columns([2, 3])
                        with col_p_mm: 
                            desenhar_mesa_planta_baixa(j1, j2, m, p[0], p[2], p[4], p[1], p[3], p[5])
                        with col_e_mm: 
                            renderizar_formulario_mesa_admin(m, j1, j2, sem_id)
                    else: 
                        desenhar_mesa_planta_baixa(j1, j2, m, p[0], p[2], p[4], p[1], p[3], p[5])

                if is_admin:
                    st.markdown("---")
                    if st.button("🏆 Confirmar Resultados e Avançar Fase", type="primary"):
                        erro_mm = False
                        for c in st.session_state.confrontos_mm:
                            p = st.session_state.placares_rodada_atual.get(c["id_original"], [0,0,0,0,0,0,False])
                            s1, s2, t1, t2 = p[0], p[1], p[2], p[3]
                            if not (s1 == 2 or s2 == 2):
                                st.error(f"❌ Partida inacabada na mesa {c['id_original']}!"); erro_mm = True
                            if (s1 == 2 and s2 == 1 and (t1 < 48 or t2 < 24)) or (s2 == 2 and s1 == 1 and (t2 < 48 or t1 < 24)):
                                st.error(f"❌ Erro na Mesa {c['id_original']}: Verifique os mínimos exigidos para o placar 2x1 (48 e 24 tentos)."); erro_mm = True
                        
                        if not erro_mm:
                            venc, perd = [], []
                            for c in st.session_state.confrontos_mm:
                                p = st.session_state.placares_rodada_atual.get(c["id_original"], [0,0,0,0,0,0,False])
                                st.session_state.classificacao.loc[c["j1"], 'Flores'] += p[4]
                                st.session_state.classificacao.loc[c["j2"], 'Flores'] += p[5]
                                
                                w, l = (c["j1"], c["j2"]) if p[0] >= p[1] else (c["j2"], c["j1"])
                                if c["tipo"]=="normal": venc.append(w); perd.append(l)
                                elif c["tipo"]=="final": st.session_state.campeao=w; st.session_state.vice_campeao=l
                                elif c["tipo"]=="3place": st.session_state.terceiro_lugar=w; st.session_state.quarto_lugar=l

                            f_at = st.session_state.fase_matamata
                            if f_at == "OITAVAS DE FINAL": iniciar_fase_matamata(venc, "QUARTAS DE FINAL")
                            elif f_at == "QUARTAS DE FINAL": iniciar_fase_matamata(venc, "SEMIFINAL")
                            elif f_at == "SEMIFINAL":
                                limpar_placares_memoria()
                                st.session_state.fase_matamata = "FINAL E TERCEIRO"
                                st.session_state.confrontos_mm = [
                                    {"id_original": "1", "tipo": "final", "j1": venc[0], "j2": venc[1]},
                                    {"id_original": "2", "tipo": "3place", "j1": perd[0], "j2": perd[1]}
                                ]
                                st.session_state.placares_rodada_atual = {"1": [0,0,0,0,0,0,False], "2": [0,0,0,0,0,0,False]}
                            salvar_estado_no_disco(); st.rerun()

# --- ABA 2: CLASSIFICAÇÃO GERAL E HISTÓRICO RETROATIVO ---
with aba_tabela:
    if st.session_state.classificacao is not None:
        st.markdown("### 📊 Tabela Oficial de Pontos")
        df_r = st.session_state.classificacao.sort_values(by=['Vitorias','Sets_Ganhos','Saldo_Tentos'], ascending=False)
        st.table(df_r)
        
        if st.session_state.historico_rodadas:
            st.markdown("---")
            st.markdown("<div class='box-auditoria'>", unsafe_allow_html=True)
            st.markdown("### 🔍 Auditoria e Correção de Rodadas Passadas")
            
            rodadas_concluidas = list(st.session_state.historico_rodadas.keys())
            r_selecionada = st.selectbox("Escolha a Rodada:", rodadas_concluidas)
            
            if r_selecionada:
                mesas_salvas = st.session_state.historico_rodadas[r_selecionada]
                for m_id, dados in mesas_salvas.items():
                    if dados.get("is_chapeu", False):
                        st.warning(f"🎩 **Jogador no Chapéu:** {dados['j1']} ganhou folga automática (+1V, 3S, 72T).")
                    else:
                        j1, j2 = dados["j1"], dados["j2"]
                        st.markdown(f"**Mesa {m_id}: {j1} VS {j2}**")
                        
                        if is_admin:
                            col_e1, col_e2 = st.columns(2)
                            with col_e1:
                                st.write(f"🥇 Controles {j1}")
                                st.number_input(f"Sets ({j1})", 0, 2, int(dados["s1"]), key=f"ret_s1_{r_selecionada}_{m_id}", on_change=salvar_mudanca_retroativa, args=(r_selecionada, m_id, j1, j2))
                                st.number_input(f"Tentos ({j1})", 0, 72, int(dados["t1"]), key=f"ret_t1_{r_selecionada}_{m_id}", on_change=salvar_mudanca_retroativa, args=(r_selecionada, m_id, j1, j2))
                                st.number_input(f"Flores ({j1})", 0, 20, int(dados["f1"]), key=f"ret_f1_{r_selecionada}_{m_id}", on_change=salvar_mudanca_retroativa, args=(r_selecionada, m_id, j1, j2))
                            with col_e2:
                                st.write(f"🥈 Controles {j2}")
                                st.number_input(f"Sets ({j2})", 0, 2, int(dados["s2"]), key=f"ret_s2_{r_selecionada}_{m_id}", on_change=salvar_mudanca_retroativa, args=(r_selecionada, m_id, j1, j2))
                                st.number_input(f"Tentos ({j2})", 0, 72, int(dados["t2"]), key=f"ret_t2_{r_selecionada}_{m_id}", on_change=salvar_mudanca_retroativa, args=(r_selecionada, m_id, j1, j2))
                                st.number_input(f"Flores ({j2})", 0, 20, int(dados["f2"]), key=f"ret_f2_{r_selecionada}_{m_id}", on_change=salvar_mudanca_retroativa, args=(r_selecionada, m_id, j1, j2))
                        else:
                            st.markdown(f"👉 **Placar Registrado:** {dados['s1']}s {dados['t1']}t (🌸{dados['f1']}fl)  **VS** {dados['s2']}s {dados['t2']}t (🌸{dados['f2']}fl)")
                        st.markdown("---")
            st.markdown("</div>", unsafe_allow_html=True)

# --- ABA 3: HISTÓRICO DE CAMPEÕES ---
with aba_historico:
    st.markdown("### 📜 Galeria Tradicionalista de Campeões")
    if os.path.exists(ARQUIVO_GALERIA):
        try:
            with open(ARQUIVO_GALERIA, "r", encoding="utf-8") as f: dg = json.load(f)
            if dg: st.table(pd.DataFrame(dg))
            else: st.info("A galeria está vazia por enquanto.")
        except Exception: st.info("A galeria está vazia por enquanto.")
    else: st.info("Nenhum torneio foi imortalizado nesta galeria ainda.")

st.markdown(f'<div class="creditos">💻 {NOME_CRIADOR} © 2026</div>', unsafe_allow_html=True)
