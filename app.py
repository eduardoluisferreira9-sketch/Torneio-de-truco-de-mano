import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import random
import json
import os
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
# 🎨 IDENTIDADE VISUAL E GRADE DE TRANSMISSÃO (CSS)
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;900&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Montserrat', sans-serif;
        background-color: #06150f;
    }
    .stApp { background-color: #06150f; } 
    
    /* Customização da Barra Lateral */
    section[data-testid="stSidebar"] {
        background-color: #030a07;
        border-right: 2px solid #b89742;
    }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 { 
        color: #e5c158 !important;
        font-weight: 900;
    }
    
    /* Textos Gerais */
    h1, h2, h3, h4, h5, p, label, .stText, [data-testid="stMarkdownContainer"] p { 
        color: #ffffff !important; 
    }
    
    .titulo-passo-admin {
        color: #e5c158 !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 10px 0 5px 0 !important;
    }

    /* Inputs Customizados */
    div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input {
        color: #ffffff !important;
        background-color: #0c241b !important;
        border: 2px solid #b89742 !important;
        border-radius: 6px !important;
        text-align: center !important;
        font-weight: bold !important;
        font-size: 1.05rem !important;
    }
    div[data-testid="stNumberInput"] label, div[data-testid="stTextInput"] label {
        color: #a4c2b7 !important;
        font-size: 0.85rem !important;
        font-weight: 700 !important;
    }
    
    /* Abas Superiores */
    button[data-baseweb="tab"] { 
        color: #a4c2b7 !important; 
        font-size: 1.1rem !important;
        padding: 12px 24px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] { 
        color: #e5c158 !important; 
        font-weight: 900 !important; 
        border-bottom-color: #e5c158 !important;
    }
    
    /* Botões Ouro */
    .stButton>button {
        background: linear-gradient(135deg, #e5c158, #b89742) !important; 
        color: #030a07 !important;
        font-weight: 900 !important; 
        border-radius: 8px !important; 
        width: 100%;
        border: none !important;
        font-size: 0.95rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    
    div.botao-excluir > button {
        background: linear-gradient(135deg, #961717, #5c0f0f) !important;
        color: #ffffff !important;
    }
    div.botao-editar > button {
        background: #0c241b !important;
        color: #e5c158 !important;
        border: 1px solid #b89742 !important;
    }
    
    /* Cronômetro Moderno e Fixo */
    .cronometro-box { 
        background: linear-gradient(135deg, #091f16, #030a07);
        border: 2px solid #b89742; 
        padding: 12px 25px; 
        border-radius: 8px; 
        margin-bottom: 25px;
        text-align: center;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 8px 20px rgba(0,0,0,0.4);
    }
    .cronometro-tempo {
        font-size: 2.5rem !important;
        font-weight: 900 !important;
        color: #ffffff !important;
        font-family: monospace;
        letter-spacing: 2px;
    }
    
    /* SISTEMA DE HISTÓRICO E GALERIA */
    .galeria-card {
        background: linear-gradient(135deg, #091f16, #0c241b);
        border: 1px solid #b89742;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0px 6px 15px rgba(0,0,0,0.4);
    }
    
    /* Tabelas Oficiais */
    div[data-testid="stTable"] table { 
        border-collapse: collapse !important;
        background-color: #091f16 !important; 
        border-radius: 8px !important;
        overflow: hidden;
        width: 100%; 
    }
    div[data-testid="stTable"] th { 
        background-color: #030a07 !important; 
        color: #e5c158 !important; 
        font-weight: 900 !important;
        text-transform: uppercase;
        padding: 12px !important;
        border: 1px solid #143d2c !important;
    }
    div[data-testid="stTable"] td { 
        color: #ffffff !important; 
        padding: 10px !important;
        font-weight: 700;
        border: 1px solid #143d2c !important;
    }
    
    .chapeu-container-novo {
        background: linear-gradient(135deg, #091f16, #143d2c);
        border: 2px dashed #e5c158;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        text-align: center;
    }
    
    .creditos { text-align: center; color: #a4c2b7 !important; font-size: 0.75rem; margin-top: 50px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 💾 PERSISTÊNCIA COMPLETA DE DADOS (JSON)
# ==========================================
def limpar_placares_memoria():
    st.session_state.placares_rodada_atual = {}
    if "semente_reset" not in st.session_state:
        st.session_state.semente_reset = 1
    else:
        st.session_state.semente_reset += 1
    chaves_para_remover = [k for k in st.session_state.keys() if k.startswith("dir_s") or k.startswith("dir_t") or k.startswith("dir_f")]
    for k in chaves_para_remover:
        del st.session_state[k]

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
            if estado.get("nome_torneio"): st.session_state.nome_torneio = estado.get("nome_torneio")
            if estado.get("classificacao") is not None:
                st.session_state.classificacao = pd.DataFrame.from_dict(estado["classificacao"], orient="index")
            if estado.get("hora_inicio_rodada"):
                st.session_state.hora_inicio_rodada = datetime.fromisoformat(estado["hora_inicio_rodada"])
        except Exception: pass

# Inicialização de chaves essenciais na memória
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

# ==========================================
# ⚙️ MOTOR DE RECALCULO E AUDITORIA RETROATIVA
# ==========================================
def reconstruir_classificacao_global():
    st.session_state.classificacao = pd.DataFrame({
        'Jogador': st.session_state.jogadores, 'Vitorias': 0, 'Sets_Ganhos': 0, 
        'Tentos_Pro': 0, 'Tentos_Contra': 0, 'Saldo_Tentos': 0, 'Flores': 0
    }).set_index('Jogador')
    
    # Recalcula rodadas de pontos corridos
    for r_num, mesas in list(st.session_state.historico_rodadas.items()):
        for m_id, dados in mesas.items():
            if dados.get("is_chapeu", False):
                if dados["j1"] in st.session_state.classificacao.index:
                    st.session_state.classificacao.loc[dados["j1"], ['Vitorias', 'Sets_Ganhos', 'Tentos_Pro']] += [1, 3, 72]
            else:
                j1, j2 = dados["j1"], dados["j2"]
                if j1 in st.session_state.classificacao.index and j2 in st.session_state.classificacao.index:
                    s1, s2 = int(dados.get("s1", 0)), int(dados.get("s2", 0))
                    t1, t2 = int(dados.get("t1", 0)), int(dados.get("t2", 0))
                    f1, f2 = int(dados.get("f1", 0)), int(dados.get("f2", 0))
                    
                    s1_c = 3 if (s1 == 2 and s2 == 0) else s1
                    s2_c = 3 if (s2 == 2 and s1 == 0) else s2
                    v1 = 1 if s1 > s2 else 0
                    v2 = 1 if s2 > s1 else 0
                    
                    st.session_state.classificacao.loc[j1, ['Vitorias','Sets_Ganhos','Tentos_Pro','Tentos_Contra','Flores']] += [v1, s1_c, t1, t2, f1]
                    st.session_state.classificacao.loc[j2, ['Vitorias','Sets_Ganhos','Tentos_Pro','Tentos_Contra','Flores']] += [v2, s2_c, t2, t1, f2]
                
    # Soma as flores acumuladas do Mata-Mata para manter prêmio individual atualizado
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
                if (dados["j1"] == j1 and dados["j2"] == j2) or (dados["j1"] == j2 and dados["j2"] == j1): return True
    return False

# ==========================================
# 🎲 ALGORITMOS DE EMPARELHAMENTO
# ==========================================
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
        if par_encontrado: pares_definidos.append((j1, par_encontrado))
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
    if not st.session_state.em_matamata or not st.session_state.confrontos_mm: return
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
        j1, j2 = vivos[i], vivos[n-1-i]
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
    while len(lista_vivos) < vagas: lista_vivos.append("CHAPÉU (Folga)")
        
    n = len(lista_vivos)
    idx_mesa = 1
    for i in range(n // 2):
        id_m = str(idx_mesa)
        j1, j2 = lista_vivos[i], lista_vivos[n-1-i]
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

# ==========================================
# 📺 MONITOR DO TRANSMISSÃO: GRADE COMPACTA (SEM ROLAGEM)
# ==========================================
def renderizar_grade_computada_html():
    """Gera o layout unificado montando os cards compactos horizontais em Grid para TVs"""
    html_cards = ""
    mesas_ativas = []
    
    if not st.session_state.em_matamata:
        cont = 1
        for j1, j2 in st.session_state.confrontos:
            if j2 != "CHAPÉU (Folga)":
                p = st.session_state.placares_rodada_atual.get(str(cont), [0,0,0,0,0,0,False])
                mesas_ativas.append({"id": str(cont), "j1": j1, "j2": j2, "s1": p[0], "s2": p[1], "t1": p[2], "t2": p[3], "f1": p[4], "f2": p[5]})
                cont += 1
    else:
        for c in st.session_state.confrontos_mm:
            if c["j2"] != "CHAPÉU (Folga)":
                p = st.session_state.placares_rodada_atual.get(c["id_original"], [0,0,0,0,0,0,False])
                
                # Tag amigável para identificar se é Final ou 3º Lugar
                prefixo_mesa = f"MESA {c['id_original']}"
                if c["tipo"] == "final": prefixo_mesa = "🏆 GRANDE FINAL"
                elif c["tipo"] == "3place": prefixo_mesa = "🥉 DISPUTA 3º LUGAR"
                
                mesas_ativas.append({"id": prefixo_mesa, "j1": c["j1"], "j2": c["j2"], "s1": p[0], "s2": p[1], "t1": p[2], "t2": p[3], "f1": p[4], "f2": p[5]})

    for m in mesas_ativas:
        is_finalizada = (int(m["s1"]) == 2 or int(m["s2"]) == 2)
        
        if is_finalizada:
            status_badge = '<span style="background-color: #3a1616; color: #ff8888; border: 1px solid #ff4444; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 900; letter-spacing: 1px;">🛑 FINALIZADA</span>'
            card_border = "1px solid #233d32"
            bg_card = "linear-gradient(135deg, #05140e, #091f16)"
            opacity_perdedor = "opacity: 0.4;"
        else:
            status_badge = '<span style="background-color: #11361c; color: #6eff89; border: 1px solid #2ecc71; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 900; letter-spacing: 1px; animation: pulse 2s infinite;">🟢 EM ANDAMENTO</span>'
            card_border = "2px solid #b89742"
            bg_card = "linear-gradient(135deg, #091f16, #123325)"
            opacity_perdedor = "opacity: 1;"

        venceu_j1 = "color: #e5c158; font-weight: 900;" if (is_finalizada and m["s1"] > m["s2"]) else "color: #ffffff;"
        venceu_j2 = "color: #e5c158; font-weight: 900;" if (is_finalizada and m["s2"] > m["s1"]) else "color: #ffffff;"
        
        style_j1 = venceu_j1 + (opacity_perdedor if (is_finalizada and m["s1"] < m["s2"]) else "")
        style_j2 = venceu_j2 + (opacity_perdedor if (is_finalizada and m["s2"] < m["s1"]) else "")

        # Verificação para evitar printar string inteira de final na id
        label_mesa = m["id"] if "🏆" in m["id"] or "🥉" in m["id"] else f"🎰 MESA {m['id']}"

        html_cards += f"""
        <div style="background: {bg_card}; border: {card_border}; border-radius: 10px; padding: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.4); font-family: 'Montserrat', sans-serif; box-sizing: border-box;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; border-bottom: 1px solid rgba(184,151,66,0.2); padding-bottom: 6px;">
                <span style="color: #e5c158; font-weight: 900; font-size: 0.85rem; letter-spacing: 1px;">{label_mesa}</span>
                {status_badge}
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; {style_j1}">
                <span style="font-size: 0.95rem; text-transform: uppercase; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 160px;">{m["j1"]}</span>
                <div style="display: flex; gap: 8px; font-weight: 900; font-size: 1.15rem;">
                    <span style="color: #e5c158;">{int(m["s1"])}<span style="font-size: 0.65rem; font-weight:400; color: #a4c2b7;">S</span></span>
                    <span>{int(m["t1"])}<span style="font-size: 0.65rem; font-weight:400; color: #a4c2b7;">T</span></span>
                </div>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; {style_j2}">
                <span style="font-size: 0.95rem; text-transform: uppercase; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 160px;">{m["j2"]}</span>
                <div style="display: flex; gap: 8px; font-weight: 900; font-size: 1.15rem;">
                    <span style="color: #e5c158;">{int(m["s2"])}<span style="font-size: 0.65rem; font-weight:400; color: #a4c2b7;">S</span></span>
                    <span>{int(m["t2"])}<span style="font-size: 0.65rem; font-weight:400; color: #a4c2b7;">T</span></span>
                </div>
            </div>
            <div style="margin-top: 8px; padding-top: 4px; border-top: 1px dashed rgba(20,61,44,0.3); font-size: 0.7rem; color: #ff69b4; text-align: right; font-weight: bold;">
                🌸 Flores: {int(m["f1"])} vs {int(m["f2"])}
            </div>
        </div>
        """

    html_completo = f"""
    <style> @keyframes pulse {{ 0% {{ opacity: 0.6; }} 50% {{ opacity: 1; }} 100% {{ opacity: 0.6; }} }} </style>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 10px; width: 100%;">
        {html_cards}
    </div>
    """
    components.html(html_completo, height=650, scrolling=True)

# ==========================================
# 🏎️ ENGINE FRAGMENTADA DE OPERAÇÃO DE MESA
# ==========================================
@st.fragment
def renderizar_bloco_mesa_isolado(m, j1, j2, sem_id):
    p = st.session_state.placares_rodada_atual.get(m, [0,0,0,0,0,0,False])
    s1, s2, t1, t2, f1, f2 = p[0], p[1], p[2], p[3], p[4], p[5]
    
    is_f = (int(s1) == 2 or int(s2) == 2)
    cor_borda = "#ff4444" if is_f else "#e5c158"
    texto_st = "🛑 FINALIZADA" if is_f else "🟢 EM ANDAMENTO"
    
    st.markdown(f"""
        <div style='background:#091f16; border-left:5px solid {cor_borda}; padding:12px; margin-top:15px; border-radius:4px;'>
            <span style='color:#e5c158; font-weight:900;'>🎰 MESA {m}</span> &nbsp;|&nbsp; {texto_st}<br>
            <span style='font-size:1.1rem; text-transform:uppercase;'><b>{j1}</b> ({s1}S) vs <b>{j2}</b> ({s2}S)</span>
        </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([2, 2, 1.2])
    with c1:
        s1_in = st.number_input(f"Sets {j1}", 0, 2, int(s1), key=f"dir_s1_{m}_{sem_id}")
        s2_in = st.number_input(f"Sets {j2}", 0, 2, int(s2), key=f"dir_s2_{m}_{sem_id}")
    
    jogo_encerrado = (s1_in == 2 or s2_in == 2)
    with c2:
        if not jogo_encerrado:
            st.caption("Aguardando definição de Sets")
            t1_final, t2_final = 0, 0
        else:
            # TRAVAS DE SEGURANÇA ANTIFRAUDE PRESERVADAS
            if s1_in == 2 and s2_in == 0:
                t1_final = 72
                t2_final = st.number_input(f"Tentos {j2} (Máx: 46)", 0, 46, min(int(t2), 46), key=f"dir_t2_{m}_{sem_id}_2x0")
            elif s2_in == 2 and s1_in == 0:
                t1_final = st.number_input(f"Tentos {j1} (Máx: 46)", 0, 46, min(int(t1), 46), key=f"dir_t1_{m}_{sem_id}_2x0")
                t2_final = 72
            else:
                t1_raw = st.text_input(f"Tentos {j1} (Min 48 se ganhou)", value="" if t1==72 or t1==0 else str(t1), key=f"dir_t1_{m}_{sem_id}_2x1")
                t2_raw = st.text_input(f"Tentos {j2} (Min 48 se ganhou)", value="" if t2==72 or t2==0 else str(t2), key=f"dir_t2_{m}_{sem_id}_2x1")
                try: t1_final = int(t1_raw) if t1_raw.strip() != "" else 0
                except: t1_final = 0
                try: t2_final = int(t2_raw) if t2_raw.strip() != "" else 0
                except: t2_final = 0
    with c3:
        f1_final = st.number_input(f"Flores {j1}", 0, 20, int(f1), key=f"dir_f1_{m}_{sem_id}")
        f2_final = st.number_input(f"Flores {j2}", 0, 20, int(f2), key=f"dir_f2_{m}_{sem_id}")
        
    if st.button(f"💾 Confirmar Mesa {m}", key=f"btn_s_m_{m}"):
        # Validações estruturais do placar de 2x1
        if jogo_encerrado and s1_in == 1 and s2_in == 2 and (t2_final < 48 or t1_final < 24):
            st.error("Erro: No placar de 2x1, o vencedor precisa de pelo menos 48 tentos e o perdedor de 24.")
        elif jogo_encerrado and s1_in == 2 and s2_in == 1 and (t1_final < 48 or t2_final < 24):
            st.error("Erro: No placar de 2x1, o vencedor precisa de pelo menos 48 tentos e o perdedor de 24.")
        else:
            st.session_state.placares_rodada_atual[m] = [s1_in, s2_in, t1_final, t2_final, f1_final, f2_final, True]
            salvar_estado_no_disco()
            st.rerun()

# ==========================================
# ⚙️ SIDEBAR ADMIN CONTROL
# ==========================================
modo_tela = st.selectbox("📺 INTERFACE SELECIONADA:", ["💻 Painel do Operador (Modo Completo)", "📺 Painel Digital (Salão / TV)"], index=0)
is_modo_tv = (modo_tela == "📺 Painel Digital (Salão / TV)")

if is_modo_tv:
    st.markdown("<style>section[data-testid='stSidebar'] { display: none !important; }</style>", unsafe_allow_html=True)
    is_admin = False
else:
    with st.sidebar:
        st.markdown("## ⚙️ CONTROLE DO ADMINISTRADOR")
        senha = st.text_input("Chave Master:", type="password")
        is_admin = (senha == CHAVE_ADMINISTRADOR)
        
        if is_admin and st.session_state.torneio_iniciado and not st.session_state.campeao:
            st.markdown("### ⏱️ Relógio Regulamentar")
            minutos_escolhidos = st.number_input("Duração total (min):", 5, 120, int(st.session_state.get("duracao_rodada_minutos", 45)), 5)
            st.session_state.duracao_rodada_minutos = minutos_escolhidos
            
            if st.button("▶️ Disparar Cronômetro"):
                st.session_state.hora_inicio_rodada = datetime.now()
                st.session_state.cronometro_ativo = True
                salvar_estado_no_disco(); st.rerun()
            if st.button("⏹️ Pausar Cronômetro"):
                st.session_state.cronometro_ativo = False
                salvar_estado_no_disco(); st.rerun()
                
            st.markdown("---")
            st.markdown("🎲 **Mesa de Ajustes**")
            if st.button("🔄 Forçar Re-sorteio desta Fase"):
                if not st.session_state.em_matamata: gerar_rodada_com_travas()
                else: re_sortear_mata_mata_manual()
                st.rerun()

            st.markdown("---")
            st.markdown("⚠️ **Reset e Segurança**")
            confirma_reset_geral = st.checkbox("Desejo apagar os dados do torneio atual", key="check_reset_geral")
            if st.button("🚨 LIMPAR COMPLETO", disabled=not confirma_reset_geral):
                if os.path.exists(ARQUIVO_BACKUP): os.remove(ARQUIVO_BACKUP)
                st.session_state.clear(); st.rerun()

# --- HEADER PRINCIPAL ---
st.markdown(f"<h1 style='text-align:center; font-weight:900; color:#e5c158 !important;'>🃏 {st.session_state.get('nome_torneio', 'Torneio de Truco')}</h1>", unsafe_allow_html=True)

# ==========================================
# 📺 FLUXO 1: INTERFACE EXCLUSIVA DA TV (SALÃO)
# ==========================================
if is_modo_tv:
    if st.session_state.cronometro_ativo and st.session_state.hora_inicio_rodada:
        duracao_min = st.session_state.get("duracao_rodada_minutos", 45)
        tl = st.session_state.hora_inicio_rodada + timedelta(minutes=duracao_min)
        tr = tl - datetime.now()
        if tr.total_seconds() > 0:
            st.markdown(f'<div class="cronometro-box"><span style="color:#e5c158; font-weight:900; letter-spacing:1px;">⏱️ CRONÔMETRO DE TRANSMISSÃO</span><div class="cronometro-tempo">{int(tr.total_seconds()//60):02d}:{int(tr.total_seconds()%60):02d}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="cronometro-box"><div class="cronometro-tempo" style="color:#ff3333 !important; width:100%;">⏰ TEMPO REGULAMENTAR ESGOTADO</div></div>', unsafe_allow_html=True)
            
    col_tv_m, col_tv_t = st.columns([7, 5])
    with col_tv_m:
        st.markdown("<h3 style='color:#e5c158 !important; margin:0 0 10px 0; font-weight:900;'>⚔️ MONITOR DE PARTIDAS EM ANDAMENTO</h3>", unsafe_allow_html=True)
        if st.session_state.torneio_iniciado and not st.session_state.campeao:
            renderizar_grade_computada_html()
        elif st.session_state.campeao:
            st.markdown(f"""
                <div style='background: linear-gradient(135deg, #b89742, #e5c158); color:#030a07; padding:30px; border-radius:12px; text-align:center;'>
                    <h1 style='color:#030a07 !important; font-weight:900; margin:0;'>🏆 TORNEIO CONCLUÍDO</h1>
                    <p style='color:#030a07 !important; font-size:1.5rem; font-weight:700; margin:10px 0 0 0;'>🥇 CAMPEÃO: {st.session_state.campeao}</p>
                </div>
            """, unsafe_allow_html=True)
            
    with col_tv_t:
        st.markdown("<h3 style='color:#e5c158 !important; margin:0 0 10px 0; font-weight:900;'>📊 CLASSIFICAÇÃO ATUALIZADA</h3>", unsafe_allow_html=True)
        if st.session_state.classificacao is not None:
            st.table(st.session_state.classificacao.sort_values(by=['Vitorias','Sets_Ganhos','Saldo_Tentos'], ascending=False))

# ==========================================
# 💻 FLUXO 2: PAINEL DO OPERADOR COMPLETÍSSIMO
# ==========================================
else:
    aba_arena, aba_tabela, aba_historico = st.tabs(["⚔️ Arena de Confrontos", "📊 Classificação & Auditoria", "📜 Galeria de Campeões"])
    
    with aba_arena:
        if not st.session_state.torneio_iniciado:
            st.markdown("### 🎮 Configurações Iniciais do Torneio")
            nome_t = st.text_input("Nome Oficial da Edição:", value="Torneio de Truco do CTG")
            
            if is_admin:
                if st.session_state.get("jogador_sendo_editado") is not None:
                    idx_edit = st.session_state.jogador_sendo_editado
                    nome_antigo = st.session_state.jogadores[idx_edit]
                    st.warning(f"✍️ Corrigindo nome do competidor: **{nome_antigo}**")
                    with st.form("form_edicao"):
                        novo_nome = st.text_input("Novo Nome:", value=nome_antigo)
                        c_b1, c_b2 = st.columns(2)
                        with c_b1:
                            if st.form_submit_button("💾 Atualizar"):
                                st.session_state.jogadores[idx_edit] = novo_nome.strip()
                                st.session_state.jogador_sendo_editado = None
                                salvar_estado_no_disco(); st.rerun()
                        with c_b2:
                            if st.form_submit_button("❌ Cancelar"):
                                st.session_state.jogador_sendo_editado = None; st.rerun()
                else:
                    with st.form("cad_jogadores", clear_on_submit=True):
                        nj = st.text_input("Nome do Competidor:")
                        if st.form_submit_button("➕ Adicionar Competidor") and nj:
                            st.session_state.jogadores.append(nj.strip())
                            salvar_estado_no_disco(); st.rerun()
                            
            st.write(f"**Competidores Registrados ({len(st.session_state.jogadores)}):**")
            if st.session_state.jogadores:
                if is_admin:
                    for idx, player in enumerate(st.session_state.jogadores):
                        c_nome, c_edit, c_excluir = st.columns([6, 1.5, 1.5])
                        with c_nome: st.markdown(f"🔹 **{player}**")
                        with c_edit:
                            st.markdown('<div class="botao-editar">', unsafe_allow_html=True)
                            if st.button(f"✏️ Editar", key=f"btn_edit_{idx}"):
                                st.session_state.jogador_sendo_editado = idx; st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
                        with c_excluir:
                            st.markdown('<div class="botao-excluir">', unsafe_allow_html=True)
                            if st.button(f"🗑️ Excluir", key=f"btn_del_{idx}"):
                                st.session_state.jogadores.pop(idx)
                                salvar_estado_no_disco(); st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.info(", ".join(st.session_state.jogadores))
            
            if is_admin and len(st.session_state.jogadores) >= 4:
                st.markdown("---")
                if st.button("🃏 INICIAR E DISTRIBUIR PRIMEIRA RODADA", type="primary"):
                    st.session_state.nome_torneio = nome_t
                    reconstruir_classificacao_global()
                    st.session_state.torneio_iniciado = True
                    gerar_rodada_com_travas(); st.rerun()
        else:
            if st.session_state.campeao:
                st.balloons()
                st.success(f"🥇 Campeão: {st.session_state.campeao} | 🥈 Vice: {st.session_state.vice_campeao}")
                
                if is_admin and st.button("💾 Eternizar Resultados na Galeria Histórica"):
                    novo_registro = {
                        "Data": datetime.now().strftime("%d/%m/%Y"),
                        "Torneio": st.session_state.get("nome_torneio"),
                        "Campeao": st.session_state.campeao,
                        "Vice": st.session_state.vice_campeao,
                        "Terceiro": st.session_state.terceiro_lugar if st.session_state.terceiro_lugar else "N/A",
                        "Quarto": st.session_state.quarto_lugar if st.session_state.quarto_lugar else "N/A"
                    }
                    lista_g = []
                    if os.path.exists(ARQUIVO_GALERIA):
                        try:
                            with open(ARQUIVO_GALERIA, "r", encoding="utf-8") as f: lista_g = json.load(f)
                        except: pass
                    lista_g.append(novo_registro)
                    with open(ARQUIVO_GALERIA, "w", encoding="utf-8") as f: json.dump(lista_g, f, ensure_ascii=False, indent=4)
                    st.success("Salvo com sucesso na história do clube!")
            
            elif st.session_state.get("aguardando_escolha_mm", False):
                st.markdown("## 🏁 Fase de Grupos Concluída! Defina a Chave Automática do Mata-Mata:")
                if is_admin:
                    c_o, c_q, c_s = st.columns(3)
                    with c_o:
                        if st.button("🏅 Oitavas de Final (Top 16)"): iniciar_fase_matamata_manual(16, "OITAVAS DE FINAL"); st.rerun()
                    with c_q:
                        if st.button("🏆 Quartas de Final (Top 8)"): iniciar_fase_matamata_manual(8, "QUARTAS DE FINAL"); st.rerun()
                    with c_s:
                        if st.button("⚡ Semifinal Direta (Top 4)"): iniciar_fase_matamata_manual(4, "SEMIFINAL"); st.rerun()

            else:
                sem_id = st.session_state.get("semente_reset", 1)
                
                for j1, j2 in st.session_state.confrontos:
                    if j2 == "CHAPÉU (Folga)":
                        st.markdown(f'<div class="chapeu-container-novo"><div style="background-color:#e5c158; color:#030a07; padding:2px 10px; border-radius:10px; font-size:0.75rem; font-weight:900; display:inline-block;">🎩 CHAPÉU (FOLGA REGULAMENTAR)</div><h3 style="margin:5px 0 0 0; font-weight:900;">{j1} (+1V / +3S / +72T)</h3></div>', unsafe_allow_html=True)

                if not st.session_state.em_matamata:
                    st.markdown(f"### 📅 Fase de Pontos Corridos: Rodada {st.session_state.rodada_atual} de 5")
                    cont = 1
                    for j1, j2 in st.session_state.confrontos:
                        if j2 != "CHAPÉU (Folga)":
                            renderizar_bloco_mesa_isolado(str(cont), j1, j2, sem_id)
                            cont += 1
                            
                    if is_admin:
                        st.markdown("---")
                        if st.button("🏁 VALIDAR E FECHAR RODADA", type="primary"):
                            erro = False
                            mc = 1
                            for j1, j2 in st.session_state.confrontos:
                                if j2 != "CHAPÉU (Folga)":
                                    p = st.session_state.placares_rodada_atual.get(str(mc), [0,0,0,0,0,0,False])
                                    if not (p[0] == 2 or p[1] == 2):
                                        st.error(f"A Mesa {mc} ainda possui partida em andamento!"); erro = True
                                    mc += 1
                            if not erro:
                                id_r = str(st.session_state.rodada_atual)
                                st.session_state.historico_rodadas[id_r] = {}
                                mc = 1
                                for j1, j2 in st.session_state.confrontos:
                                    if j2 == "CHAPÉU (Folga)":
                                        st.session_state.historico_rodadas[id_r][f"chapeu_{j1}"] = {"is_chapeu": True, "j1": j1, "j2": "Folga", "s1": 3, "s2": 0, "t1": 72, "t2": 0, "f1": 0, "f2": 0}
                                    else:
                                        p = st.session_state.placares_rodada_atual.get(str(mc), [0,0,0,0,0,0,False])
                                        st.session_state.historico_rodadas[id_r][str(mc)] = {"is_chapeu": False, "j1": j1, "j2": j2, "s1": p[0], "s2": p[1], "t1": p[2], "t2": p[3], "f1": p[4], "f2": p[5]}
                                        mc += 1
                                reconstruir_classificacao_global()
                                st.session_state.rodada_atual += 1
                                if st.session_state.rodada_atual <= 5: gerar_rodada_com_travas()
                                else: st.session_state.aguardando_escolha_mm = True
                                salvar_estado_no_disco(); st.rerun()
                else:
                    st.markdown(f"### ⚡ Chave de Eliminatórias: {st.session_state.fase_matamata}")
                    for c in st.session_state.confrontos_mm:
                        if c["j2"] != "CHAPÉU (Folga)":
                            renderizar_bloco_mesa_isolado(c["id_original"], c["j1"], c["j2"], sem_id)
                        else:
                            st.info(f"🏅 {c['j1']} avançou diretamente pelo Chapéu do chaveamento.")
                        
                    if is_admin and st.button("Avançar Fase do Mata-Mata", type="primary"):
                        venc, perd = [], []
                        for c in st.session_state.confrontos_mm:
                            p = st.session_state.placares_rodada_atual.get(c["id_original"], [0,0,0,0,0,0,False])
                            # Computa flores para a premiação individual
                            st.session_state.flores_acumuladas_matamata[c["j1"]] = st.session_state.flores_acumuladas_matamata.get(c["j1"], 0) + p[4]
                            st.session_state.flores_acumuladas_matamata[c["j2"]] = st.session_state.flores_acumuladas_matamata.get(c["j2"], 0) + p[5]
                            
                            w, l = (c["j1"], c["j2"]) if p[0] >= p[1] else (c["j2"], c["j1"])
                            if c["tipo"] == "normal": venc.append(w); perd.append(l)
                            elif c["tipo"] == "final": st.session_state.campeao = w; st.session_state.vice_campeao = l
                            elif c["tipo"] == "3place": st.session_state.terceiro_lugar = w; st.session_state.quarto_lugar = l
                        
                        f_at = st.session_state.fase_matamata
                        if f_at == "OITAVAS DE FINAL":
                            st.session_state.fase_matamata = "QUARTAS DE FINAL"
                            st.session_state.confrontos_mm = [{"id_original": str(i+1), "tipo": "normal", "j1": venc[i], "j2": venc[len(venc)-1-i]} for i in range(len(venc)//2)]
                            st.session_state.placares_rodada_atual = {str(i+1): [0,0,0,0,0,0,False] for i in range(len(venc)//2)}
                        elif f_at == "QUARTAS DE FINAL":
                            st.session_state.fase_matamata = "SEMIFINAL"
                            st.session_state.confrontos_mm = [{"id_original": str(i+1), "tipo": "normal", "j1": venc[i], "j2": venc[len(venc)-1-i]} for i in range(len(venc)//2)]
                            st.session_state.placares_rodada_atual = {str(i+1): [0,0,0,0,0,0,False] for i in range(len(venc)//2)}
                        elif f_at == "SEMIFINAL":
                            st.session_state.fase_matamata = "FINAIS"
                            st.session_state.confrontos_mm = [
                                {"id_original": "1", "tipo": "final", "j1": venc[0], "j2": venc[1]},
                                {"id_original": "2", "tipo": "3place", "j1": perd[0], "j2": perd[1]}
                            ]
                            st.session_state.placares_rodada_atual = {"1": [0,0,0,0,0,0,False], "2": [0,0,0,0,0,0,False]}
                        else:
                            reconstruir_classificacao_global()
                        salvar_estado_no_disco(); st.rerun()

    with aba_tabela:
        if st.session_state.classificacao is not None:
            st.markdown("### 📊 Tabela Geral Classificatória")
            st.table(st.session_state.classificacao.sort_values(by=['Vitorias','Sets_Ganhos','Saldo_Tentos'], ascending=False))
            
            # AUDITORIA RETROATIVA PRESERVADA 
            if is_admin and st.session_state.historico_rodadas:
                st.markdown("---")
                st.markdown("### 🔍 Painel de Auditoria e Edições Retroativas")
                r_alvo = st.selectbox("Selecione a Rodada Passada:", list(st.session_state.historico_rodadas.keys()))
                if r_alvo:
                    mesas_auditoria = st.session_state.historico_rodadas[r_alvo]
                    for m_id, dados in list(mesas_auditoria.items()):
                        if not dados.get("is_chapeu", False):
                            st.write(f"**Mesa {m_id}: {dados['j1']} vs {dados['j2']}**")
                            c_au1, c_au2, c_au3 = st.columns(3)
                            with c_au1:
                                ns1 = st.number_input(f"Sets {dados['j1']}", 0, 2, int(dados['s1']), key=f"ret_s1_{r_alvo}_{m_id}")
                                ns2 = st.number_input(f"Sets {dados['j2']}", 0, 2, int(dados['s2']), key=f"ret_s2_{r_alvo}_{m_id}")
                            with c_au2:
                                nt1 = st.number_input(f"Tentos {dados['j1']}", 0, 72, int(dados['t1']), key=f"ret_t1_{r_alvo}_{m_id}")
                                nt2 = st.number_input(f"Tentos {dados['j2']}", 0, 72, int(dados['t2']), key=f"ret_t2_{r_alvo}_{m_id}")
                            with c_au3:
                                nf1 = st.number_input(f"Flores {dados['j1']}", 0, 20, int(dados['f1']), key=f"ret_f1_{r_alvo}_{m_id}")
                                nf2 = st.number_input(f"Flores {dados['j2']}", 0, 20, int(dados['f2']), key=f"ret_f2_{r_alvo}_{m_id}")
                            
                            if st.button(f"💾 Atualizar Histórico Mesa {m_id}", key=f"btn_ret_{r_alvo}_{m_id}"):
                                st.session_state.historico_rodadas[r_alvo][m_id].update({"s1": ns1, "s2": ns2, "t1": nt1, "t2": nt2, "f1": nf1, "f2": nf2})
                                reconstruir_classificacao_global()
                                st.success("Placar recalculado retroativamente!")
                                st.rerun()

    with aba_historico:
        st.markdown("### 📜 Registros Históricos e Campeões")
        if os.path.exists(ARQUIVO_GALERIA):
            try:
                with open(ARQUIVO_GALERIA, "r", encoding="utf-8") as f: dg_check = json.load(f)
                if dg_check:
                    for idx, t in enumerate(dg_check):
                        st.markdown(f"""
                            <div class="galeria-card">
                                <div style="color:#e5c158; font-weight:900; font-size:1.1rem;">🏆 {t.get('Torneio')}</div>
                                <div style="font-size:0.8rem; color:#a4c2b7; margin-bottom:8px;">📅 Data de Conclusão: {t.get('Data')}</div>
                                🥇 Campeão: <b>{t.get('Campeao')}</b> | 🥈 Vice: {t.get('Vice')}<br>
                                🥉 Terceiro: {t.get('Terceiro')} | 🏅 Quarto: {t.get('Quarto')}
                            </div>
                        """, unsafe_allow_html=True)
                    
                    if is_admin:
                        st.markdown("---")
                        opcoes_torneios = [f"{idx} - {t.get('Torneio')} ({t.get('Data')})" for idx, t in enumerate(dg_check)]
                        torneio_para_deletar = st.selectbox("Deletar registro específico da galeria:", opcoes_torneios)
                        c_confirma = st.checkbox("Confirmo a remoção permanente deste item do histórico", key="check_del_seletivo")
                        if st.button("🗑️ Remover Registro do Histórico", disabled=not c_confirma):
                            idx_alvo = int(torneio_para_deletar.split(" - ")[0])
                            dg_check.pop(idx_alvo)
                            with open(ARQUIVO_GALERIA, "w", encoding="utf-8") as f: json.dump(dg_check, f, indent=4)
                            st.success("Item removido!"); st.rerun()
                else: st.info("Nenhum torneio arquivado até o momento.")
            except: st.info("Nenhum torneio arquivado até o momento.")
        else: st.info("Nenhum torneio arquivado até o momento.")

st.markdown(f'<div class="creditos">💻 {NOME_CRIADOR} © 2026</div>', unsafe_allow_html=True)
