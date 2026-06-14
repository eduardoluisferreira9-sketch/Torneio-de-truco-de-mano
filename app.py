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

# 🛠️ ESTILIZAÇÃO CSS
st.markdown("""
    <style>
    .stApp { background-color: #0d231a; } 
    
    section[data-testid="stSidebar"] {
        background-color: #07140f;
        border-right: 2px solid #1c4234;
    }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2 { color: #d4af37; }
    
    h1, h2, h3, h4, h5, p, label, .stText, [data-testid="stMarkdownContainer"] p { 
        color: #ffffff !important;
    }
    
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
    
    div[data-testid="stTextInput"] input {
        color: #ffffff !important;
        background-color: #07140f !important;
        border: 2px solid #d4af37 !important;
        text-align: center !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
    }
    
    div[data-testid="stNumberInput"] input {
        color: #ffffff !important;
        background-color: #07140f !important;
        border: 2px solid #d4af37 !important;
        text-align: center !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        height: 35px !important;
    }
    
    div[data-testid="stNumberInput"] label, div[data-testid="stTextInput"] label {
        color: #ffffff !important;
        font-size: 0.95rem !important;
        font-weight: bold !important;
    }
    
    button[data-baseweb="tab"] { color: #a0c0b5 !important; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #d4af37 !important; font-weight: bold; }
    
    .stButton>button {
        background-color: #d4af37 !important;
        color: #111111 !important;
        font-weight: bold !important; border-radius: 8px !important; width: 100%;
        border: 1px solid #aa8312 !important;
        font-size: 1.1rem !important;
    }
    
    div.botao-excluir > button {
        background-color: #8b0000 !important;
        color: #ffffff !important;
        border: 1px solid #ff0000 !important;
        font-size: 0.9rem !important;
    }
    div.botao-editar > button {
        background-color: #1c4234 !important;
        color: #ffffff !important;
        border: 1px solid #d4af37 !important;
        font-size: 0.9rem !important;
    }
    
    .cronometro-box { 
        background-color: #07140f;
        border: 3px solid #d4af37; padding: 15px; border-radius: 12px; margin-bottom: 25px;
        text-align: center;
    }
    
    .chapeu-container-novo {
        background: linear-gradient(135deg, #07140f, #113223);
        border: 3px solid #d4af37;
        border-radius: 20px;
        padding: 25px;
        margin-top: 15px;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0px 8px 25px rgba(0,0,0,0.5);
    }
    .chapeu-badge {
        background-color: #d4af37; color: #000000 !important;
        padding: 5px 15px;
        font-weight: bold; border-radius: 50px; font-size: 0.9rem; display: inline-block;
        margin-bottom: 10px; text-transform: uppercase;
    }
    .chapeu-nome {
        font-size: 2.2rem !important; color: #ffffff !important;
        font-weight: 900 !important;
        margin: 5px 0 !important; text-transform: uppercase; letter-spacing: 1px;
    }
    .chapeu-subtexto { font-size: 1.1rem !important;
        color: #d4af37 !important; font-weight: bold !important; margin-bottom: 5px !important; }
    .chapeu-regras { font-size: 0.9rem !important;
        color: #a0c0b5 !important; font-style: italic !important; }
    
    .galeria-card {
        background: linear-gradient(135deg, #07140f, #143527);
        border: 3px double #d4af37;
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0px 6px 15px rgba(0,0,0,0.4);
    }
    .galeria-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px dashed #1c4234;
        padding-bottom: 10px;
        margin-bottom: 15px;
    }
    .galeria-titulo-evento { font-size: 1.4rem; color: #d4af37; font-weight: bold;
    }
    .galeria-data { font-size: 0.9rem; color: #a0c0b5; font-weight: bold; }
    .galeria-corpo { display: flex;
        flex-direction: column; gap: 8px; }
    .galeria-linha-campeao { font-size: 1.6rem; color: #ffffff; font-weight: bold;
    }
    .galeria-ouro { color: #d4af37 !important; font-weight: 900; }
    .galeria-linha-secundaria { font-size: 1.1rem;
        color: #e0e0e0; }
    
    box-auditoria { background-color: #07140f; border: 2px solid #1c4234; padding: 20px;
        border-radius: 10px; margin-top: 30px; }
    .creditos { text-align: center; color: #ffffff !important; font-size: 0.8rem; margin-top: 50px;
    }

    div[data-testid="stTable"] table { border: 3px solid #ffffff !important; background-color: #113223 !important; width: 100%;
    }
    div[data-testid="stTable"] th { background-color: #07140f !important; color: #d4af37 !important; border: 2px solid #ffffff !important;
        text-align: center !important; }
    div[data-testid="stTable"] td { color: #ffffff !important; border: 2px solid #ffffff !important;
        text-align: center !important; }
    </style>
""", unsafe_allow_html=True)

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

def salvar_estado_no_disco():
    estado = {
        "jogadores": st.session_state.jogadores,
        "torneio_iniciado": st.session_state.torneio_iniciado,
        "rodada_atual": st.session_state.rodada_atual,
        "confrontos": st.session_state.confrontos,
        "jogadores_no_chapeu": list(st.session_state.jogadores_no_chapeu),
        "hora_inicio_rodada": st.session_state.hora_inicio_rodada.isoformat() if st.session_state.hora_inicio_rodada else None,
        "duracao_rodada_minutos": st.session_state.get("duracao_rodada_minutos", 45),
        "cronometro_ativo": st.session_state.cronometro_ativo,
        "historico_rodadas": st.session_state.historico_rodadas,
        "historico_matamata": st.session_state.get("historico_matamata", {}),
        "nome_torneio": st.session_state.get("nome_torneio", "Torneio de Truco"),
        "em_matamata": st.session_state.em_matamata,
        "fase_matamata": st.session_state.fase_matamata,
        "confrontos_mm": st.session_state.confrontos_mm,
        "campeao": st.session_state.campeao,
        "vice_campeao": st.session_state.vice_campeao,
        "terceiro_lugar": st.session_state.terceiro_lugar,
        "quarto_lugar": st.session_state.quarto_lugar,
        "placares_rodada_atual": st.session_state.placares_rodada_atual,
        "semente_reset": st.session_state.get("semente_reset", 1),
        "aguardando_escolha_mm": st.session_state.get("aguardando_escolha_mm", False),
        "flores_acumuladas_matamata": st.session_state.get("flores_acumuladas_matamata", {})
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
            st.session_state.historico_matamata = estado.get("historico_matamata", {})
            st.session_state.placares_rodada_atual = estado.get("placares_rodada_atual", {})
            st.session_state.semente_reset = estado.get("semente_reset", 1)
            st.session_state.aguardando_escolha_mm = estado.get("aguardando_escolha_mm", False)
            st.session_state.flores_acumuladas_matamata = estado.get("flores_acumuladas_matamata", {})
            st.session_state.duracao_rodada_minutos = estado.get("duracao_rodada_minutos", 45)
            if estado.get("nome_torneio"):
                st.session_state.nome_torneio = estado.get("nome_torneio")
            if estado.get("classificacao") is not None:
                st.session_state.classificacao = pd.DataFrame.from_dict(estado["classificacao"], orient="index")
            if estado.get("hora_inicio_rodada"):
                st.session_state.hora_inicio_rodada = datetime.fromisoformat(estado["hora_inicio_rodada"])
        except Exception: pass

if "jogadores" not in st.session_state:
    st.session_state.jogadores = []
    st.session_state.torneio_iniciado = False
    st.session_state.rodada_atual = 1
    st.session_state.classificacao = None
    st.session_state.confrontos = []
    st.session_state.jogadores_no_chapeu = set()
    st.session_state.hora_inicio_rodada = None
    st.session_state.duracao_rodada_minutos = 45
    st.session_state.cronometro_ativo = False
    st.session_state.em_matamata = False
    st.session_state.fase_matamata = ""
    st.session_state.confrontos_mm = []
    st.session_state.campeao = None
    st.session_state.vice_campeao = None
    st.session_state.terceiro_lugar = None
    st.session_state.quarto_lugar = None
    st.session_state.historico_rodadas = {}
    st.session_state.historico_matamata = {}
    st.session_state.placares_rodada_atual = {}
    st.session_state.semente_reset = 1
    st.session_state.nome_torneio = "Torneio de Truco"
    st.session_state.jogador_sendo_editado = None
    st.session_state.aguardando_escolha_mm = False
    st.session_state.flores_acumuladas_matamata = {}

carregar_estado_do_disco()

def reconstruir_classificacao_global():
    st.session_state.classificacao = pd.DataFrame({
        'Jogador': st.session_state.jogadores, 'Vitorias': 0, 'Sets_Ganhos': 0, 
        'Tentos_Pro': 0, 'Tentos_Contra': 0, 'Saldo_Tentos': 0, 'Flores': 0
    }).set_index('Jogador')
    
    for r_num, mesas in list(st.session_state.historico_rodadas.items()):
        for m_id, dados in mesas.items():
            if dados.get("is_chapeu", False):
                if dados["j1"] in st.session_state.classificacao.index:
                    st.session_state.classificacao.loc[dados["j1"], ['Vitorias', 'Sets_Ganhos', 'Tentos_Pro']] += [1, 3, 72]
            else:
                j1, j2 = dados["j1"], dados["j2"]
                if j1 in st.session_state.classificacao.index and j2 in st.session_state.classificacao.index:
                    s1 = int(dados.get("s1", 0))
                    s2 = int(dados.get("s2", 0))
                    t1 = int(dados.get("t1", 0))
                    t2 = int(dados.get("t2", 0))
                    f1_gravado = int(dados.get("f1", 0))
                    f2_gravado = int(dados.get("f2", 0))
                    
                    s1_c = 3 if (s1 == 2 and s2 == 0) else s1
                    s2_c = 3 if (s2 == 2 and s1 == 0) else s2
                    v1 = 1 if s1 > s2 else 0
                    v2 = 1 if s2 > s1 else 0
                    
                    st.session_state.classificacao.loc[j1, ['Vitorias','Sets_Ganhos','Tentos_Pro','Tentos_Contra','Flores']] += [v1, s1_c, t1, t2, f1_gravado]
                    st.session_state.classificacao.loc[j2, ['Vitorias','Sets_Ganhos','Tentos_Pro','Tentos_Contra','Flores']] += [v2, s2_c, t2, t1, f2_gravado]
                
    if "flores_acumuladas_matamata" in st.session_state:
        for jogador, flores_mm in st.session_state.flores_acumuladas_matamata.items():
            if jogador in st.session_state.classificacao.index:
                st.session_state.classificacao.loc[jogador, 'Flores'] += int(flores_mm)

    st.session_state.classificacao['Saldo_Tentos'] = st.session_state.classificacao['Tentos_Pro'] - st.session_state.classificacao['Tentos_Contra']
    salvar_estado_no_disco()

def ja_se_enfrentaram(j1, j2):
    for r_num, mesas in st.session_state.historico_rodadas.items():
        for m_id, dados in mesas.items():
            if not dados.get("is_chapeu", False):
                if (dados["j1"] == j1 and dados["j2"] == j2) or (dados["j1"] == j2 and dados["j2"] == j1):
                    return True
    return False

def gerar_rodada_com_travas():
    limpar_placares_memoria()
    lista_rodada = list(st.session_state.jogadores)
    random.shuffle(lista_rodada)
    st.session_state.confrontos = []
    
    if len(lista_rodada) % 2 != 0:
        cand_chapeu = [j for j in lista_rodada if j not in st.session_state.jogadores_no_chapeu]
        chapeu = random.choice(cand_chapeu if cand_chapeu else lista_rodada)
        lista_rodada.remove(chapeu)
        st.session_state.jogadores_no_chapeu.add(chapeu)
        st.session_state.confrontos.append((chapeu, "CHAPÉU (Folga)"))

    pares_definidos = []
    while len(lista_rodada) > 0:
        j1 = lista_rodada[0]
        par_encontrado = None
        for idx in range(1, len(lista_rodada)):
            possivel_j2 = lista_rodada[idx]
            if not ja_se_enfrentaram(j1, possivel_j2):
                par_encontrado = possivel_j2
                lista_rodada.pop(idx)
                lista_rodada.pop(0)
                break
        if par_encontrado:
            pares_definidos.append((j1, par_encontrado))
        else:
            par_encontrado = lista_rodada[1]
            lista_rodada.pop(1)
            lista_rodada.pop(0)
            pares_definidos.append((j1, par_encontrado))

    contador_mesa = 1
    for j1, j2 in pares_definidos:
        st.session_state.confrontos.append((j1, j2))
        st.session_state.placares_rodada_atual[str(contador_mesa)] = [0, 0, 0, 0, 0, 0, False]
        contador_mesa += 1
    st.session_state.hora_inicio_rodada = None
    st.session_state.cronometro_ativo = False
    salvar_estado_no_disco()

def re_sortear_mata_mata_manual():
    if not st.session_state.em_matamata or not st.session_state.confrontos_mm:
        return
    
    vivos = []
    for c in st.session_state.confrontos_mm:
        if c["j1"] != "CHAPÉU (Folga)": vivos.append(c["j1"])
        if c["j2"] != "CHAPÉU (Folga)": vivos.append(c["j2"])
    
    limpar_placares_memoria()
    random.shuffle(vivos)
    
    st.session_state.confrontos_mm = []
    idx_mesa = 1
    n = len(vivos)
    
    for i in range(n // 2):
        id_m = str(idx_mesa)
        j1 = vivos[i]
        j2 = vivos[n-1-i]
        st.session_state.confrontos_mm.append({"id_original": id_m, "tipo": "normal", "j1": j1, "j2": j2})
        st.session_state.placares_rodada_atual[id_m] = [0, 0, 0, 0, 0, 0, False]
        idx_mesa += 1
        
    st.session_state.hora_inicio_rodada = None
    st.session_state.cronometro_ativo = False
    salvar_estado_no_disco()

def iniciar_fase_matamata_manual(vagas, nome_fase):
    limpar_placares_memoria()
    st.session_state.em_matamata = True
    st.session_state.aguardando_escolha_mm = False
    st.session_state.fase_matamata = nome_fase
    st.session_state.confrontos_mm = []
    
    df_classificado = st.session_state.classificacao.sort_values(by=['Vitorias', 'Sets_Ganhos', 'Saldo_Tentos'], ascending=False)
    lista_vivos = list(df_classificado.index[:vagas])
    
    while len(lista_vivos) < vagas:
        lista_vivos.append("CHAPÉU (Folga)")
        
    n = len(lista_vivos)
    idx_mesa = 1
    for i in range(n // 2):
        id_m = str(idx_mesa)
        j1 = lista_vivos[i]
        j2 = lista_vivos[n-1-i]
        
        if j2 == "CHAPÉU (Folga)" and j1 != "CHAPÉU (Folga)":
            st.session_state.confrontos_mm.append({"id_original": id_m, "tipo": "normal", "j1": j1, "j2": j2})
            st.session_state.placares_rodada_atual[id_m] = [2, 0, 72, 0, 0, 0, True]
        else:
            st.session_state.confrontos_mm.append({"id_original": id_m, "tipo": "normal", "j1": j1, "j2": j2})
            st.session_state.placares_rodada_atual[id_m] = [0, 0, 0, 0, 0, 0, False]
        idx_mesa += 1
        
    st.session_state.hora_inicio_rodada = None
    st.session_state.cronometro_ativo = False
    salvar_estado_no_disco()

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

def salvar_mudanca_retroativa(r_alvo, m_id, j1, j2):
    st.session_state.historico_rodadas[r_alvo][m_id]["s1"] = st.session_state[f"ret_s1_{r_alvo}_{m_id}"]
    st.session_state.historico_rodadas[r_alvo][m_id]["t1"] = st.session_state[f"ret_t1_{r_alvo}_{m_id}"]
    st.session_state.historico_rodadas[r_alvo][m_id]["f1"] = st.session_state[f"ret_f1_{r_alvo}_{m_id}"]
    st.session_state.historico_rodadas[r_alvo][m_id]["s2"] = st.session_state[f"ret_s2_{r_alvo}_{m_id}"]
    st.session_state.historico_rodadas[r_alvo][m_id]["t2"] = st.session_state[f"ret_t2_{r_alvo}_{m_id}"]
    st.session_state.historico_rodadas[r_alvo][m_id]["f2"] = st.session_state[f"ret_f2_{r_alvo}_{m_id}"]
    reconstruir_classificacao_global()

def desenhar_mesa_planta_baixa(j1, j2, mesa_num, s1, t1, f1, s2, t2, f2):
    html_mesa = f"""
    <div style="background-color: #113223; border: 8px solid #5a3825; border-radius: 50px; padding: 20px; display: flex; flex-direction: column; align-items: center; justify-content: space-between; position: relative; box-shadow: inset 0px 0px 40px rgba(0,0,0,0.9), 0px 10px 20px rgba(0,0,0,0.6); height: 410px; box-sizing: border-box; color: #ffffff; font-family: sans-serif; margin-bottom: 5px;">
        <div style="position: absolute; top: 15px; text-align: center; width: 100%;">
            <div style="font-size: 0.85rem; color: #d4af37; font-weight: bold;">🧔 JOGADOR 1</div>
            <div style="background: linear-gradient(135deg, #d4af37, #aa8312); color: #000; padding: 8px 30px; border-radius: 20px; font-size: 1.2rem; font-weight: bold; display: inline-block; border: 1px solid #fff;">{j1}</div>
        </div>
        <div style="background-color: rgba(7, 20, 15, 0.95); border: 2px solid #d4af37; border-radius: 15px; padding: 12px; width: 85%; margin-top: 95px; text-align: center;">
            <div style="font-size: 0.85rem; color: #d4af37; font-weight: bold; letter-spacing: 2px;">🎰 MESA {mesa_num}</div>
            <hr style="margin: 8px 0; border-top: 1px solid #1c4234;">
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
            if s1_in == 2 and s2_in == 0:
                st.info(f"{j1} 2x0. Fixo 72.")
                st.number_input(f"Tentos - {j1}", 72, 72, 72, key=f"dir_t1_{m}_r{sem_id}_2x0j1", disabled=True)
                st.number_input(f"Tentos - {j2} (Máx: 46)", 0, 46, min(int(t2), 46), key=f"dir_t2_{m}_r{sem_id}_2x0j1", on_change=disparar_atualizacao_placar, args=(m, j1, j2))
            elif s2_in == 2 and s1_in == 0:
                st.number_input(f"Tentos - {j1} (Máx: 46)", 0, 46, min(int(t1), 46), key=f"dir_t1_{m}_r{sem_id}_2x0j2", on_change=disparar_atualizacao_placar, args=(m, j1, j2))
                st.info(f"{j2} 2x0. Fixo 72.")
                st.number_input(f"Tentos - {j2}", 72, 72, 72, key=f"dir_t2_{m}_r{sem_id}_2x0j2", disabled=True)
            else:
                t1_val_str = "" if (t1 == 72 or t1 == 0) else str(t1)
                t2_val_str = "" if (t2 == 72 or t2 == 0) else str(t2)
                st.text_input(f"Digite Tentos - {j1}", value=t1_val_str, key=f"dir_t1_{m}_r{sem_id}_2x1", on_change=disparar_atualizacao_placar, args=(m, j1, j2), placeholder="Digite...")
                st.text_input(f"Digite Tentos - {j2}", value=t2_val_str, key=f"dir_t2_{m}_r{sem_id}_2x1", on_change=disparar_atualizacao_placar, args=(m, j1, j2), placeholder="Digite...")

    st.markdown(f"<h4 class='titulo-passo-admin'>• FLORES (Passo 3)</h4>", unsafe_allow_html=True)
    st.number_input(f"Flores - {j1}", 0, 20, int(f1), key=f"dir_f1_{m}_r{sem_id}", on_change=disparar_atualizacao_placar, args=(m, j1, j2))
    st.number_input(f"Flores - {j2}", 0, 20, int(f2), key=f"dir_f2_{m}_r{sem_id}", on_change=disparar_atualizacao_placar, args=(m, j1, j2))

# =====================================================================
# ⏱️ IMPLEMENTAÇÃO ITEM 2: CRONÔMETRO DINÂMICO ISOLADO EM FRAGMENTO
# =====================================================================
@st.fragment(run_every=1.0)
def renderizar_cronometro_torneio():
    if not st.session_state.get("torneio_iniciado") or st.session_state.get("campeao"):
        return

    if st.session_state.hora_inicio_rodada is not None and st.session_state.cronometro_ativo:
        hora_inicio = st.session_state.hora_inicio_rodada
        duracao_definida = timedelta(minutes=st.session_state.get("duracao_rodada_minutos", 45))
        hora_fim = hora_inicio + duracao_definida
        tempo_restante = hora_fim - datetime.now()
        total_segundos = int(tempo_restante.total_seconds())
        
        if total_segundos <= 0:
            st.markdown("""
                <div class='cronometro-box' style='border-color: #ff0000 !important; background-color: #2a0000 !important;'>
                    <h2 style='color: #ff0000 !important; margin: 0; font-weight: bold; font-size: 2.2rem;'>🚨 FIM DE TEMPO!</h2>
                    <p style='color: #ffffff !important; margin: 5px 0 0 0; font-weight: bold; font-size: 1.2rem;'>MESA PRETA DISPARADA!</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            minutos = total_segundos // 60
            segundos = total_segundos % 60
            cor_visor = "#d4af37" if minutos >= 10 else "#ff3333"
            
            # Formatação do rótulo da etapa corrente
            fase_label = st.session_state.fase_matamata.upper() if st.session_state.em_matamata else f"RODADA {st.session_state.rodada_atual}"
            
            st.markdown(f"""
                <div class='cronometro-box' style='border-color: {cor_visor} !important;'>
                    <span style='color: #a0c0b5; font-size: 0.9rem; font-weight: bold; letter-spacing: 2px;'>🕒 TEMPO RESTANTE - {fase_label}</span>
                    <h1 style='color: {cor_visor} !important; font-family: "Courier New", monospace; font-size: 3.8rem; margin: 5px 0 0 0; font-weight: bold; letter-spacing: 2px;'>
                        {minutos:02d}:{segundos:02d}
                    </h1>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class='cronometro-box' style='border-color: #555555 !important;'>
                <span style='color: #888888; font-size: 0.9rem; font-weight: bold; letter-spacing: 1px;'>⏱️ CRONÔMETRO</span>
                <h1 style='color: #666666 !important; font-family: "Courier New", monospace; font-size: 3.2rem; margin: 5px 0 0 0; font-weight: bold;'>PAUSADO</h1>
            </div>
        """, unsafe_allow_html=True)

# --- BARRA LATERAL ---
with st.sidebar:
    st.markdown("## ⚙️ Gestão Técnico")
    senha = st.text_input("Chave Master:", type="password")
    is_admin = (senha == CHAVE_ADMINISTRADOR)
    
    if is_admin:
        if st.session_state.torneio_iniciado and not st.session_state.campeao:
            st.markdown("### ⏱️ Cronômetro da Rodada")
            # Configuração travada entre 40 e 120 minutos conforme especificado nas regras de negócio
            minutos_escolhidos = st.number_input(
                "Duração da rodada (min):", 
                min_value=40, 
                max_value=120, 
                value=int(max(40, min(120, st.session_state.get("duracao_rodada_minutos", 45)))), 
                step=5
            )
            st.session_state.duracao_rodada_minutos = minutos_escolhidos
            
            if st.button("▶️ Iniciar/Disparar Tempo"):
                st.session_state.hora_inicio_rodada = datetime.now()
                st.session_state.cronometro_ativo = True
                salvar_estado_no_disco()
                st.rerun()
                
            if st.button("⏹️ Pausar Cronômetro"):
                st.session_state.cronometro_ativo = False
                salvar_estado_no_disco()
                st.rerun()

        if st.session_state.torneio_iniciado and not st.session_state.campeao and not st.session_state.get("aguardando_escolha_mm", False):
            st.markdown("---")
            st.markdown("🎲 **Ajuste de Confrontos**")
            if st.button("🔄 Refazer Sorteio Desta Etapa"):
                if not st.session_state.em_matamata:
                    gerar_rodada_com_travas()
                else:
                    re_sortear_mata_mata_manual()
                st.success("Confrontos re-sorteados com sucesso!")
                st.rerun()

# 🏆 CABEÇALHO DO APLICATIVO
st.markdown(f"""
    <div style="text-align: center; margin-bottom: 25px;">
        <h1 style="color: #d4af37 !important; font-size: 2.8rem; font-weight: bold; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 2px;">
            {st.session_state.nome_torneio}
        </h1>
        <p style="color: #a0c0b5 !important; font-size: 1.1rem; font-style: italic;">
            Desenvolvido por: {NOME_CRIADOR} | Link de Acesso Público: <strong style="color: #d4af37;">{url_oficial}</strong>
        </p>
    </div>
""", unsafe_allow_html=True)

aba_arena, aba_classificacao, aba_admin, aba_galeria = st.tabs([
    "🏟️ PLANTA BAIXA DA ARENA", 
    "📊 CLASSIFICAÇÃO GERAL", 
    "🛠️ PAINEL DO ADMINISTRADOR",
    "🏆 GALERIA DOS CAMPEÕES"
])

# ==========================================
# 🏟️ ABA ARENA (VISUALIZAÇÃO PÚBLICA)
# ==========================================
with aba_arena:
    # Renderização reativa do cronômetro sem travar a interface
    renderizar_cronometro_torneio()
    
    if not st.session_state.torneio_iniciado:
        st.info("Aguardando o início oficial do torneio pelo Administrador.")
    else:
        confrontos_ativos = st.session_state.confrontos_mm if st.session_state.em_matamata else []
        if not st.session_state.em_matamata:
            confrontos_ativos = [{"id_original": str(i+1), "j1": pair[0], "j2": pair[1], "tipo": "normal"} for i, pair in enumerate(st.session_state.confrontos) if pair[1] != "CHAPÉU (Folga)"]
            
        chapeu_da_rodada = None
        if not st.session_state.em_matamata:
            for pair in st.session_state.confrontos:
                if pair[1] == "CHAPÉU (Folga)": chapeu_da_rodada = pair[0]
        else:
            for c in st.session_state.confrontos_mm:
                if c["j2"] == "CHAPÉU (Folga)": chapeu_da_rodada = c["j1"]

        if chapeu_da_rodada:
            st.markdown(f"""
                <div class="chapeu-container-novo">
                    <span class="chapeu-badge">🎩 Jogador no Chapéu</span>
                    <div class="chapeu-nome">{chapeu_da_rodada}</div>
                    <div class="chapeu-subtexto">Ganhou Folga e somou automaticamente +1 Vitória (+3 Sets e +72 Tentos)</div>
                    <div class="chapeu-regras">Regra oficial de chaves ímpares: Ninguém joga no Chapéu duas vezes!</div>
                </div>
            """, unsafe_allow_html=True)

        if len(confrontos_ativos) > 0:
            st.markdown("<h2 style='text-align: center; color: #d4af37 !important;'>MAPA DE DISPOSIÇÃO DAS MESAS</h2>", unsafe_allow_html=True)
            colunas_por_linha = 3
            linhas_confrontos = [confrontos_ativos[i:i + colunas_por_linha] for i in range(0, len(confrontos_ativos), colunas_por_linha)]
            
            for linha in linhas_confrontos:
                cols_streamlit = st.columns(colunas_por_linha)
                for idx_col, conf in enumerate(linha):
                    with cols_streamlit[idx_col]:
                        m_id = conf["id_original"]
                        j1, j2 = conf["j1"], conf["j2"]
                        pl = st.session_state.placares_rodada_atual.get(m_id, [0,0,0,0,0,0,False])
                        desenhar_mesa_planta_baixa(j1, j2, m_id, pl[0], pl[2], pl[4], pl[1], pl[3], pl[5])
        else:
            if st.session_state.campeao:
                st.balloons()
                st.success(f"🏆 O Torneio chegou ao fim! Grande Campeão: {st.session_state.campeao}")

# ==========================================
# 📊 ABA CLASSIFICAÇÃO
# ==========================================
with aba_classificacao:
    if st.session_state.classificacao is None or len(st.session_state.classificacao) == 0:
        st.info("Nenhum dado de classificação disponível ainda.")
    else:
        st.markdown("<h3 style='color: #d4af37;'>TABELA DE CLASSIFICAÇÃO UNIFICADA</h3>", unsafe_allow_html=True)
        df_exibicao = st.session_state.classificacao.sort_values(by=['Vitorias', 'Sets_Ganhos', 'Saldo_Tentos'], ascending=False).copy()
        df_exibicao.insert(0, 'Posição', range(1, len(df_exibicao) + 1))
        
        st.table(df_exibicao.reset_index()[['Posição', 'Jogador', 'Vitorias', 'Sets_Ganhos', 'Tentos_Pro', 'Tentos_Contra', 'Saldo_Tentos', 'Flores']])
        
        if st.session_state.historico_rodadas:
            st.markdown("---")
            st.markdown("<h3 style='color: #d4af37;'>📖 MEMÓRIA DE JOGOS (AUDITORIA DE RODADAS)</h3>", unsafe_allow_html=True)
            for r_num, mesas in sorted(st.session_state.historico_rodadas.items(), reverse=True):
                with st.expander(f"➔ DETALHES COMPLETOS - RODADA COMPUTAÇÃO {r_num}", expanded=False):
                    for m_id, dados in mesas.items():
                        if dados.get("is_chapeu", False):
                            st.write(f"🎩 **{dados['j1']}** ficou no Chapéu (Folga compulsória regulamentada).")
                        else:
                            st.write(f"🎰 **Mesa {m_id}**: {dados['j1']} ({int(dados['s1'])}s {int(dados['t1'])}t) VS {dados['j2']} ({int(dados['s2'])}s {int(dados['t2'])}t) | Flores: {dados.get('f1',0)}x{dados.get('f2',0)}")

# ==========================================
# 🛠️ ABA ADMINISTRADOR
# ==========================================
with aba_admin:
    if not is_admin:
        st.warning("Insira a Chave Master correta na barra lateral esquerda para liberar o acesso.")
    else:
        # Renderização do cronômetro também no painel administrativo
        renderizar_cronometro_torneio()
        
        st.markdown("<h2 style='color: #d4af37;'>PAINEL CENTRAL DE OPERAÇÕES</h2>", unsafe_allow_html=True)
        
        if not st.session_state.torneio_iniciado:
            st.subheader("Passo 1: Gerenciamento e Inscrição de Competidores")
            
            c1, c2 = st.columns([2, 1])
            with c1:
                novo_j = st.text_input("Nome Completo do Atleta:", key="campo_novo_jogador")
                if st.button("➕ Confirmar Inscrição"):
                    nome_limpo = novo_j.strip()
                    if nome_limpo and nome_limpo not in st.session_state.jogadores:
                        st.session_state.jogadores.append(nome_limpo)
                        reconstruir_classificacao_global()
                        st.success(f"Atleta '{nome_limpo}' cadastrado com sucesso.")
                        st.rerun()
                    elif nome_limpo in st.session_state.jogadores:
                        st.error("Este nome já consta na lista de inscritos.")
            with c2:
                st.markdown(f"**Total Inscritos:** {len(st.session_state.jogadores)}")
                
            if len(st.session_state.jogadores) > 0:
                st.markdown("---")
                st.markdown("### Lista de Atletas Homologados")
                for idx, jog in enumerate(st.session_state.jogadores):
                    col_j, col_btn_ed, col_btn_ex = st.columns([4, 1, 1])
                    with col_j:
                        st.markdown(f"**{idx+1}.** {jog}")
                    with col_btn_ed:
                        if st.button("✏️ Editar", key=f"btn_edit_{idx}"):
                            st.session_state.jogador_sendo_editado = jog
                    with col_btn_ex:
                        st.markdown("<div class='botao-excluir'>", unsafe_allow_html=True)
                        if st.button("🗑️ Excluir", key=f"btn_del_{idx}"):
                            st.session_state.jogadores.remove(jog)
                            reconstruir_classificacao_global()
                            st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                if st.session_state.jogador_sendo_editado:
                    st.markdown("---")
                    st.markdown(f"#### Editando Cadastro: {st.session_state.jogador_sendo_editado}")
                    novo_nome = st.text_input("Modificar Nome para:", value=st.session_state.jogador_sendo_editado)
                    if st.button("💾 Salvar Alteração"):
                        n_nome_limpo = novo_nome.strip()
                        if n_nome_limpo and n_nome_limpo != st.session_state.jogador_sendo_editado:
                            idx_orig = st.session_state.jogadores.index(st.session_state.jogador_sendo_editado)
                            st.session_state.jogadores[idx_orig] = n_nome_limpo
                            st.session_state.jogador_sendo_editado = None
                            reconstruir_classificacao_global()
                            st.rerun()

            if len(st.session_state.jogadores) >= 2:
                st.markdown("---")
                st.session_state.nome_torneio = st.text_input("Defina o Nome Deste Evento Truqueiro:", value=st.session_state.nome_torneio)
                if st.button("🚀 LOCK-IN: CONGELAR LISTA E INICIAR TORNEIO"):
                    st.session_state.torneio_iniciado = True
                    st.session_state.rodada_atual = 1
                    st.session_state.em_matamata = False
                    st.session_state.fase_matamata = ""
                    st.session_state.historico_rodadas = {}
                    st.session_state.jogadores_no_chapeu = set()
                    reconstruir_classificacao_global()
                    gerar_rodada_com_travas()
                    st.rerun()
        else:
            # Torneio em andamento
            if not st.session_state.campeao:
                if not st.session_state.em_matamata:
                    st.subheader(f"Gerenciador de Resultados: Rodada Corrente Número {st.session_state.rodada_atual}")
                else:
                    st.subheader(f"Gerenciador de Resultados: Fase Eliminação Direta ({st.session_state.fase_matamata})")
                
                confrontos_formulario = []
                if not st.session_state.em_matamata:
                    confrontos_formulario = [{"id_original": str(i+1), "j1": p[0], "j2": p[1]} for i, p in enumerate(st.session_state.confrontos) if p[1] != "CHAPÉU (Folga)"]
                else:
                    confrontos_formulario = st.session_state.confrontos_mm

                sem_id = st.session_state.get("semente_reset", 1)
                
                for conf in confrontos_formulario:
                    m_str = conf["id_original"]
                    j1, j2 = conf["j1"], conf["j2"]
                    
                    st.markdown(f"<div class='titulo-mesa-destaque'>🎰 MESA DE CONTROLE {m_str}: {j1} VS {j2}</div>", unsafe_allow_html=True)
                    renderizar_formulario_mesa_admin(m_str, j1, j2, sem_id)
                    st.markdown("---")
                    
                # Fluxo de encerramento e validações de etapas
                todos_com_placar = True
                for conf in confrontos_formulario:
                    m_str = conf["id_original"]
                    pl = st.session_state.placares_rodada_atual.get(m_str, [0,0,0,0,0,0,False])
                    if not pl[6] or (pl[0] < 2 and pl[1] < 2):
                        todos_com_placar = False
                        
                if todos_com_placar:
                    if not st.session_state.em_matamata:
                        if st.button("💾 COMPLEMENTAR HISTÓRICO E AVANÇAR PARA PRÓXIMA RODADA"):
                            dic_rodada = {}
                            for pair in st.session_state.confrontos:
                                if pair[1] == "CHAPÉU (Folga)":
                                    dic_rodada["chapeu"] = {"is_chapeu": True, "j1": pair[0]}
                            
                            for i, pair in enumerate(st.session_state.confrontos):
                                if pair[1] != "CHAPÉU (Folga)":
                                    m_str = str(i+1)
                                    pl = st.session_state.placares_rodada_atual[m_str]
                                    dic_rodada[m_str] = {"is_chapeu": False, "j1": pair[0], "j2": pair[1], "s1": pl[0], "s2": pl[1], "t1": pl[2], "t2": pl[3], "f1": pl[4], "f2": pl[5]}
                                    
                            st.session_state.historico_rodadas[str(st.session_state.rodada_atual)] = dic_rodada
                            reconstruir_classificacao_global()
                            
                            st.session_state.rodada_atual += 1
                            gerar_rodada_com_travas()
                            st.success(f"Rodada concluída. Rodada {st.session_state.rodada_atual} gerada automaticamente.")
                            st.rerun()
                    else:
                        # Processamento do Mata-Mata corrente
                        if st.button("💥 PROCESSAR ELIMINATÓRIA DIRETA E AVANÇAR"):
                            vencedores_fase = []
                            dic_mm_salvar = {}
                            
                            for conf in st.session_state.confrontos_mm:
                                m_id = conf["id_original"]
                                j1, j2 = conf["j1"], conf["j2"]
                                pl = st.session_state.placares_rodada_atual[m_id]
                                
                                dic_mm_salvar[m_id] = {"j1": j1, "j2": j2, "s1": pl[0], "s2": pl[1], "t1": pl[2], "t2": pl[3], "f1": pl[4], "f2": pl[5]}
                                
                                # Acumula flores de mata-mata na classificação
                                if j1 not in st.session_state.flores_acumuladas_matamata: st.session_state.flores_acumuladas_matamata[j1] = 0
                                if j2 not in st.session_state.flores_acumuladas_matamata: st.session_state.flores_acumuladas_matamata[j2] = 0
                                st.session_state.flores_acumuladas_matamata[j1] += int(pl[4])
                                st.session_state.flores_acumuladas_matamata[j2] += int(pl[5])
                                
                                if pl[0] > pl[1]: vencedores_fase.append(j1)
                                else: vencedores_fase.append(j2)
                                
                            st.session_state.historico_matamata[st.session_state.fase_matamata] = dic_mm_salvar
                            reconstruir_classificacao_global()
                            
                            # Condicional de afunilamento de fases
                            if st.session_state.fase_matamata == "Semifinal":
                                st.session_state.confrontos_mm = []
                                f_c1, f_c2 = st.session_state.historico_matamata["Semifinal"]["1"], st.session_state.historico_matamata["Semifinal"]["2"]
                                
                                vencedor_s1 = f_c1["j1"] if f_c1["s1"] > f_c1["s2"] else f_c1["j2"]
                                perdedor_s1 = f_c1["j2"] if f_c1["s1"] > f_c1["s2"] else f_c1["j1"]
                                vencedor_s2 = f_c2["j1"] if f_c2["s1"] > f_c2["s2"] else f_c2["j2"]
                                perdedor_s2 = f_c2["j2"] if f_c2["s1"] > f_c2["s2"] else f_c2["j1"]
                                
                                limpar_placares_memoria()
                                st.session_state.fase_matamata = "Grande Final / 3º Lugar"
                                st.session_state.confrontos_mm.append({"id_original": "1", "tipo": "final", "j1": vencedor_s1, "j2": vencedor_s2})
                                st.session_state.confrontos_mm.append({"id_original": "2", "tipo": "terceiro", "j1": perdedor_s1, "j2": perdedor_s2})
                                st.session_state.placares_rodada_atual["1"] = [0,0,0,0,0,0,False]
                                st.session_state.placares_rodada_atual["2"] = [0,0,0,0,0,0,False]
                                st.session_state.hora_inicio_rodada = None
                                st.session_state.cronometro_ativo = False
                                salvar_estado_no_disco()
                                st.rerun()
                                
                            elif st.session_state.fase_matamata == "Grande Final / 3º Lugar":
                                f_final = st.session_state.placares_rodada_atual["1"]
                                f_3lugar = st.session_state.placares_rodada_atual["2"]
                                conf_f = st.session_state.confrontos_mm[0]
                                conf_3 = st.session_state.confrontos_mm[1]
                                
                                st.session_state.campeao = conf_f["j1"] if f_final[0] > f_final[1] else conf_f["j2"]
                                st.session_state.vice_campeao = conf_f["j2"] if f_final[0] > f_final[1] else conf_f["j1"]
                                st.session_state.terceiro_lugar = conf_3["j1"] if f_3lugar[0] > f_3lugar[1] else conf_3["j2"]
                                st.session_state.quarto_lugar = conf_3["j2"] if f_3lugar[0] > f_3lugar[1] else conf_3["j1"]
                                salvar_estado_no_disco()
                                st.rerun()
                            else:
                                # Redução dinâmica genérica (ex: Quartas para Semifinal)
                                num_vagas_nova = len(vencedores_fase)
                                nova_fase = "Semifinal" if num_vagas_nova == 4 else f"Mata-Mata ({num_vagas_nova} competidores)"
                                iniciar_fase_matamata_manual(num_vagas_nova, nova_fase)
                                st.rerun()
                else:
                    st.info("Preencha os resultados de todas as mesas para abrir o botão de avanço.")
            else:
                st.success("🏆 Torneio concluído com sucesso!")
                
                if st.button("🌟 IMORTALIZAR TORNEIO NA GALERIA DE CAMPEÕES"):
                    df_c = st.session_state.classificacao.sort_values(by='Flores', ascending=False)
                    rei_da_flor = df_c.index[0] if len(df_c) > 0 else "N/A"
                    
                    novo_registro = {
                        "Torneio": st.session_state.nome_torneio,
                        "Data": datetime.now().strftime("%d/%m/%Y"),
                        "Campeao": st.session_state.campeao,
                        "Vice": st.session_state.vice_campeao,
                        "Terceiro": st.session_state.terceiro_lugar,
                        "Quarto": st.session_state.quarto_lugar,
                        "ReiDaFlor": rei_da_flor
                    }
                    
                    galeria_atual = []
                    if os.path.exists(ARQUIVO_GALERIA):
                        try:
                            with open(ARQUIVO_GALERIA, "r", encoding="utf-8") as gf:
                                galeria_atual = json.load(gf)
                        except Exception: pass
                        
                    galeria_atual.append(novo_registro)
                    with open(ARQUIVO_GALERIA, "w", encoding="utf-8") as gf:
                        json.dump(galeria_atual, gf, ensure_ascii=False, indent=4)
                        
                    if os.path.exists(ARQUIVO_BACKUP):
                        try: os.remove(ARQUIVO_BACKUP)
                        except Exception: pass
                        
                    st.session_state.clear()
                    st.success("Torneio imortalizado! Sistema reiniciado com sucesso.")
                    st.rerun()

            # Gatilhos manuais de encerramento para Mata-Mata
            if not st.session_state.em_matamata:
                st.markdown("---")
                st.markdown("### 🎫 Chaveamento Avançado: Transição de Fases")
                cc1, cc2 = st.columns([1, 1])
                with cc1:
                    if st.button("🎯 Migrar Direto para Semifinal (Top 4 Atletas)"):
                        iniciar_fase_matamata_manual(4, "Semifinal")
                        st.rerun()
                with cc2:
                    if st.button("🔥 Migrar Direto para Quartas de Final (Top 8 Atletas)"):
                        iniciar_fase_matamata_manual(8, "Quartas de Final")
                        st.rerun()

            st.markdown("---")
            st.markdown("### ✏️ Edição Retroativa de Resultados Salvos")
            if not st.session_state.historico_rodadas:
                st.info("Nenhuma rodada fechada em histórico para alteração retroativa.")
            else:
                r_alvo_ed = st.selectbox("Selecione a Rodada Gravada:", sorted(list(st.session_state.historico_rodadas.keys())))
                if r_alvo_ed:
                    mesas_alvo = st.session_state.historico_rodadas[r_alvo_ed]
                    for m_id_ed, dados_ed in mesas_alvo.items():
                        if not dados_ed.get("is_chapeu", False):
                            j1, j2 = dados_ed["j1"], dados_ed["j2"]
                            st.markdown(f"**Mesa {m_id_ed}: {j1} VS {j2}**")
                            col_e1, col_e2, col_e3, col_e4, col_e5, col_e6 = st.columns(6)
                            with col_e1: st.number_input(f"Sets {j1}", 0, 2, int(dados_ed["s1"]), key=f"ret_s1_{r_alvo_ed}_{m_id_ed}", on_change=salvar_mudanca_retroativa, args=(r_alvo_ed, m_id_ed, j1, j2))
                            with col_e2: st.number_input(f"Tentos {j1}", 0, 72, int(dados_ed["t1"]), key=f"ret_t1_{r_alvo_ed}_{m_id_ed}", on_change=salvar_mudanca_retroativa, args=(r_alvo_ed, m_id_ed, j1, j2))
                            with col_e3: st.number_input(f"Flores {j1}", 0, 20, int(dados_ed["f1"]), key=f"ret_f1_{r_alvo_ed}_{m_id_ed}", on_change=salvar_mudanca_retroativa, args=(r_alvo_ed, m_id_ed, j1, j2))
                            with col_e4: st.number_input(f"Sets {j2}", 0, 2, int(dados_ed["s2"]), key=f"ret_s2_{r_alvo_ed}_{m_id_ed}", on_change=salvar_mudanca_retroativa, args=(r_alvo_ed, m_id_ed, j1, j2))
                            with col_e5: st.number_input(f"Tentos {j2}", 0, 72, int(dados_ed["t2"]), key=f"ret_t2_{r_alvo_ed}_{m_id_ed}", on_change=salvar_mudanca_retroativa, args=(r_alvo_ed, m_id_ed, j1, j2))
                            with col_e6: st.number_input(f"Flores {j2}", 0, 20, int(dados_ed["f2"]), key=f"ret_f2_{r_alvo_ed}_{m_id_ed}", on_change=salvar_mudanca_retroativa, args=(r_alvo_ed, m_id_ed, j1, j2))

        st.markdown("---")
        st.markdown("<div class='botao-excluir'>", unsafe_allow_html=True)
        if st.button("🚨 LIMPAR TODOS OS DADOS DO TORNEIO ATUAL E RESETAR SISTEMA"):
            if os.path.exists(ARQUIVO_BACKUP):
                try: os.remove(ARQUIVO_BACKUP)
                except Exception: pass
            st.session_state.clear()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 🏆 ABA GALERIA DOS CAMPEÕES
# ==========================================
with aba_galeria:
    if os.path.exists(ARQUIVO_GALERIA):
        try:
            with open(ARQUIVO_GALERIA, "r", encoding="utf-8") as gf:
                dados_galeria = json.load(gf)
            if len(dados_galeria) > 0:
                st.markdown("<h2 style='color: #d4af37; text-align: center;'>HALL DA FAMA TRUQUEIRA</h2>", unsafe_allow_html=True)
                for registro in reversed(dados_galeria):
                    st.markdown(f"""
                        <div class="galeria-card">
                            <div class="galeria-header">
                                <span class="galeria-titulo-evento">🏆 {registro.get('Torneio', 'Torneio sem Nome')}</span>
                                <span class="galeria-data">📅 Data: {registro.get('Data', 'N/A')}</span>
                            </div>
                            <div class="galeria-corpo">
                                <div class="galeria-linha-campeao">🥇 Grande Campeão: <span class="galeria-ouro">{registro.get('Campeao', 'N/A')}</span></div>
                                <div class="galeria-linha-secundaria">🥈 Vice-Campeão: {registro.get('Vice', 'N/A')}</div>
                                <div class="galeria-linha-secundaria">🥉 3º Colocado: {registro.get('Terceiro', 'N/A')} &nbsp;|&nbsp; 🏅 4º Colocado: {registro.get('Quarto', 'N/A')}</div>
                                <div class="galeria-linha-secundaria" style="margin-top: 5px; color: #ff69b4 !important;">🌸 Rei da Flor: {registro.get('ReiDaFlor', 'N/A')}</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else: st.info("A galeria está vazia por enquanto.")
        except Exception: st.info("A galeria está vazia por enquanto.")
    else: st.info("Nenhum torneio foi imortalizado nesta galeria ainda.")

st.markdown(f"<div class='creditos'>Central de Torneios Oficial • Criado e Desenvolvido por {NOME_CRIADOR} © 2026</div>", unsafe_allow_html=True)
