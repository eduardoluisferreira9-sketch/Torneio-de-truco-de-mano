import streamlit as st
import pandas as pd
import random
import json
import os
import qrcode
import socket
from io import BytesIO
from datetime import datetime, timedelta

# 🃏 CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Sistema de Torneios de Truco de Mano",
    page_icon="🃏",
    layout="wide"
)

NOME_CRIADOR = "Eduardo Luis Ferreira"
ARQUIVO_BACKUP = "torneio_atual.json"
ARQUIVO_GALERIA = "galeria_campeoes.json"
CHAVE_ADMINISTRADOR = "truco123"

# ==========================================
# 🖼️ BANCO DE DADOS DE IMAGENS VIA INTERNET
# ==========================================
URL_BASE_IMAGENS = "https://raw.githubusercontent.com/seu-usuario/seu-repositorio/main/imagens"

PATROCINADORES = {
    "master": {"nome": "Sicredi", "logo": f"{URL_BASE_IMAGENS}/sicredi.png"},
    "secundario": {"nome": "Copag", "logo": f"{URL_BASE_IMAGENS}/copag.png"},
    "mesas": [
        {"nome": "Sicredi", "logo": f"{URL_BASE_IMAGENS}/sicredi.png"},
        {"nome": "Copag", "logo": f"{URL_BASE_IMAGENS}/copag.png"},
        {"nome": "O Chimarrão", "logo": f"{URL_BASE_IMAGENS}/o_chimarrao.png"},
        {"nome": "Pampa", "logo": f"{URL_BASE_IMAGENS}/pampa.png"},
        {"nome": "Rio Grande", "logo": f"{URL_BASE_IMAGENS}/rio_grande.png"}
    ]
}

# --- FUNÇÕES DE SALVAMENTO E RECUPERAÇÃO ---
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
        "salvo_na_galeria": st.session_state.get("salvo_na_galeria", False)
    }
    if st.session_state.classificacao is not None:
        estado["classificacao"] = st.session_state.classificacao.to_dict(orient="index")
    else:
        estado["classificacao"] = None
        
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
            
            if estado.get("hora_inicio_rodada"):
                st.session_state.hora_inicio_rodada = datetime.fromisoformat(estado["hora_inicio_rodada"])
            else:
                st.session_state.hora_inicio_rodada = None
                
            if estado.get("classificacao") is not None:
                st.session_state.classificacao = pd.DataFrame.from_dict(estado["classificacao"], orient="index")
            else:
                st.session_state.classificacao = None
        except Exception:
            pass

def salvar_na_galeria(torneio, campeao, vice, terceiro, quarto, rei_flores, qtd_flores):
    registros = []
    if os.path.exists(ARQUIVO_GALERIA):
        try:
            with open(ARQUIVO_GALERIA, "r", encoding="utf-8") as f:
                registros = json.load(f)
        except Exception:
            registros = []
            
    novo_registro = {
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "torneio": torneio,
        "campeao": campeao,
        "vice": vice,
        "terceiro": terceiro,
        "quarto": quarto,
        "rei_flores": f"{rei_flores} ({qtd_flores} fl.)"
    }
    registros.insert(0, novo_registro)
    with open(ARQUIVO_GALERIA, "w", encoding="utf-8") as f:
        json.dump(registros, f, ensure_ascii=False, indent=4)

# --- INICIALIZAÇÃO DE MEMÓRIA ---
valores_padrao = {
    "jogadores": [], "torneio_iniciado": False, "rodada_atual": 1, "classificacao": None,
    "confrontos": [], "jogadores_no_chapeu": set(), "hora_inicio_rodada": None, "cronometro_ativo": False,
    "historico_rodadas": {}, "em_matamata": False, "fase_matamata": "", "confrontos_mm": [],
    "campeao": None, "vice_campeao": None, "terceiro_lugar": None, "quarto_lugar": None, "perdedores_semi": [], "salvo_na_galeria": False
}

for chave, valor in valores_padrao.items():
    if chave not in st.session_state:
        st.session_state[chave] = valor

if os.path.exists(ARQUIVO_BACKUP):
    carregar_estado_do_disco()

# --- ESTILIZAÇÃO CSS DE ALTO CONTRASTE + PLANTA BAIXA DA MESA ---
st.markdown("""
    <style>
    .stApp { background-color: #1b4d3e; }
    h1, h2, h3, h4, p, label, .stMarkdown { color: #ffffff !important; }
    .stButton>button {
        background-color: #d4af37 !important; color: #111111 !important;
        font-weight: bold !important; border-radius: 8px !important; width: 100%;
    }
    
    .card-lateral {
        background-color: #11221a;
        padding: 20px; border-radius: 12px; border: 2px solid #2c6b56; margin-bottom: 20px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
    }
    
    /* 🎰 CONTAINER DA PLANTA BAIXA DA MESA */
    .planta-mesa {
        background-color: #143525; /* Feltro Verde de Jogo */
        border: 6px solid #5a3825; /* Borda de Madeira */
        border-radius: 45px;
        padding: 24px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: space-between;
        position: relative;
        box-shadow: inset 0px 0px 40px rgba(0,0,0,0.8), 0px 10px 20px rgba(0,0,0,0.6);
        margin-bottom: 30px;
    }
    
    /* 👤 CADEIRA / CABECEIRA DO JOGADOR */
    .cabeceira-player {
        color: #111111 !important;
        padding: 10px 30px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 1.15rem;
        box-shadow: 0px 5px 10px rgba(0,0,0,0.4);
        text-align: center;
        min-width: 240px;
        letter-spacing: 0.5px;
    }
    .p1-cor { background: linear-gradient(135deg, #d4af37, #aa8312); border: 2px solid #ffffff; }
    .p2-cor { background: linear-gradient(135deg, #ffffff, #dcdcdc); border: 2px solid #aaaaaa; }
    
    /* 🎛️ CENTRO OPERACIONAL DE INPUTS DE DADOS */
    .centro-operacional {
        background-color: rgba(14, 25, 20, 0.95);
        border: 2px solid #d4af37;
        border-radius: 14px;
        padding: 16px;
        width: 100%;
        margin: 15px 0;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.5);
    }
    
    .vs-text {
        text-align: center; color: #d4af37 !important; font-weight: bold; font-size: 0.85rem; margin: 8px 0; letter-spacing: 2px;
    }
    
    div[data-baseweb="input"] {
        background-color: #22312c !important; border: 1px solid #d4af37 !important; border-radius: 6px !important;
    }
    input { color: #ffffff !important; font-weight: bold !important; text-align: center; }
    label { color: #a0c0b5 !important; font-size: 0.8rem !important; text-align: center; width: 100%; }
    
    .texto-confronto { font-size: 1.25rem !important; font-weight: bold !important; color: #ffffff !important; }
    .cronometro-box { 
        background-color: #11221a; border: 3px solid #d4af37; padding: 15px; border-radius: 12px; margin-bottom: 25px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.4);
    }
    
    .box-campeao { background-color: #d4af37; padding: 25px; border-radius: 15px; text-align: center; color: #111111 !important; border: 3px solid #ffffff; margin-bottom: 15px; }
    .podio-posicao { padding: 15px; border-radius: 10px; text-align: center; font-weight: bold; margin-bottom: 10px; color: #ffffff !important; }
    .podio-vice { background-color: #a0a0a0; border: 2px solid #d1d1d1; }
    .podio-terceiro { background-color: #cd7f32; border: 2px solid #e5a65d; }
    .podio-quarto { background-color: #2c6b56; border: 2px solid #d4af37; }
    .box-flores { background-color: #4a1525; padding: 15px; border-radius: 10px; text-align: center; color: #ffffff !important; border: 2px solid #ff4b4b; margin-top: 15px; margin-bottom: 20px; }
    .creditos { text-align: center; color: #a0c0b5 !important; font-size: 0.8rem; margin-top: 50px; }
    </style>
""", unsafe_allow_html=True)

def obter_ip_da_rede():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return f"http://{ip}:8501"
    except Exception:
        return "http://localhost:8501"

url_oficial = obter_ip_da_rede()

# --- TRAVA MATEMÁTICA ---
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
        if t1 < 48: return True, s1, s2, t1, t2, f"Mesa {mesa_id}: Inconsistência! Como {n1} fez 2 sets, ele precisa ter no mínimo 48 tentos."
        if t2 < 24: return True, s1, s2, t1, t2, f"Mesa {mesa_id}: Inconsistência! Como {n2} fez 1 set, ele precisa ter no mínimo 24 tentos."
    elif s2 == 2 and s1 == 1:
        if t2 < 48: return True, s1, s2, t1, t2, f"Mesa {mesa_id}: Inconsistência! Como {n2} fez 2 sets, ele precisa ter no mínimo 48 tentos."
        if t1 < 24: return True, s1, s2, t1, t2, f"Mesa {mesa_id}: Inconsistência! Como {n1} fez 1 set, ele precisa ter no mínimo 24 tentos."
    return False, s1, s2, t1, t2, ""

def gerar_rodada_web():
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

    for i in range(0, len(lista_rodada), 2):
        st.session_state.confrontos.append((lista_rodada[i], lista_rodada[i+1]))
    st.session_state.hora_inicio_rodada = None
    st.session_state.cronometro_ativo = False
    salvar_estado_no_disco()

def iniciar_fase_matamata(lista_jogadores, nome_fase):
    st.session_state.em_matamata = True
    st.session_state.fase_matamata = nome_fase
    st.session_state.confrontos_mm = []
    n = len(lista_jogadores)
    for i in range(n // 2):
        st.session_state.confrontos_mm.append({"tipo": "normal", "j1": lista_jogadores[i], "j2": lista_jogadores[n - 1 - i]})
    st.session_state.hora_inicio_rodada = None
    st.session_state.cronometro_ativo = False
    salvar_estado_no_disco()

# =========================================================================
# 🏛️ MONTAGEM DA PAISAGEM DE TRÊS COLUNAS
# =========================================================================
col_esquerda, col_centro, col_direita = st.columns([1, 2, 1])

# -------------------------------------------------------------------------
# 🔐 COLUNA DA ESQUERDA: Painel do Operador + Patrocínios Principais
# -------------------------------------------------------------------------
with col_esquerda:
    st.markdown("### ⚙️ Gestão Técnico-Operacional")
    
    with st.expander("🛠️ Abrir Painel de Controle", expanded=False):
        senha_inserida = st.text_input("Chave do Operador:", type="password")
        is_admin = (senha_inserida == CHAVE_ADMINISTRADOR)
        
        if is_admin:
            st.success("⚡ Administrador Conectado")
            st.markdown("**⏱️ Tempo de Jogo:**")
            c_c1, c_c2 = st.columns(2)
            with c_c1:
                if st.button("▶️ Iniciar 45m"):
                    st.session_state.hora_inicio_rodada = datetime.now()
                    st.session_state.cronometro_ativo = True
                    salvar_estado_no_disco()
                    st.rerun()
            with c_c2:
                if st.button("⏹️ Pausar"):
                    st.session_state.hora_inicio_rodada = None
                    st.session_state.cronometro_ativo = False
                    salvar_estado_no_disco()
                    st.rerun()
            
            st.markdown("---")
            st.markdown("🌐 **Acesso Mobile:**")
            url_torneio = st.text_input("Link da Rede Local:", value=st.session_state.get("url_override", url_oficial))
            st.session_state["url_override"] = url_torneio
            
            qr = qrcode.QRCode(version=1, box_size=6, border=2)
            qr.add_data(url_torneio)
            qr.make(fit=True)
            img_qr = qr.make_image(fill_color="black", back_color="white")
            buf = BytesIO()
            img_qr.save(buf, format="PNG")
            st.image(buf.getvalue(), caption="QR Code de Consulta", use_container_width=True)
            
            st.markdown("---")
            if st.button("🚨 LIMPAR E REINICIAR TORNEIO"):
                if os.path.exists(ARQUIVO_BACKUP): os.remove(ARQUIVO_BACKUP)
                st.session_state.clear()
                st.rerun()
        else:
            st.info("Insira a chave para liberar os controles.")

    # 🌟 ESPAÇO DE PATROCÍNIOS PRINCIPAIS
    st.markdown("---")
    st.markdown("<p style='text-align: center; font-size: 0.95rem; font-weight: bold; color: #d4af37 !important; margin-bottom: 15px;'>⭐️ PATROCÍNIO PRINCIPAL ⭐️</p>", unsafe_allow_html=True)
    
    col_patro1, col_patro2 = st.columns(2)
    with col_patro1:
        if PATROCINADORES["master"]["logo"]: st.image(PATROCINADORES["master"]["logo"], use_container_width=True, caption="Master")
        else: st.caption(PATROCINADORES["master"]["nome"])
    with col_patro2:
        if PATROCINADORES["secundario"]["logo"]: st.image(PATROCINADORES["secundario"]["logo"], use_container_width=True, caption="Parceiro Oficial")
        else: st.caption(PATROCINADORES["secundario"]["nome"])

# -------------------------------------------------------------------------
# ⚔️ COLUNA CENTRAL: O Campo de Jogo (Layout Arquitetônico de Planta Baixa)
# -------------------------------------------------------------------------
with col_centro:
    st.markdown(f"<h1 style='text-align:center;'>🏆 {st.session_state.get('nome_torneio', 'Torneio de Truco do CTG')}</h1>", unsafe_allow_html=True)
    
    if not st.session_state.torneio_iniciado:
        aba1, aba2 = st.tabs(["🎮 Painel de Inscrições", "📜 Galeria de Campeões"])
        with aba1:
            st.markdown("### 🎪 Identificação do Evento")
            nome_torneio = st.text_input("Nome do Torneio ou CTG:", value=st.session_state.get("nome_torneio", "Torneio de Truco do CTG"))
            st.markdown("---")
            st.markdown("### 👤 Cadastro de Jogadores")
            
            with st.form(key="form_cadastro", clear_on_submit=True):
                novo_jogador = st.text_input("Nome do Jogador:")
                submit_add = st.form_submit_button("➕ Adicionar Jogador")
                if submit_add and novo_jogador:
                    name_clean = novo_jogador.strip()
                    if name_clean in st.session_state.jogadores: st.warning(f"⚠️ O jogador '{name_clean}' já está inscrito!")
                    elif name_clean != "":
                        st.session_state.jogadores.append(name_clean)
                        salvar_estado_no_disco()
                        st.rerun()

            total_inscritos = len(st.session_state.jogadores)
            st.markdown(f"**Inscritos atuais: {total_inscritos} / 64**")
            st.write(", ".join(st.session_state.jogadores))
            
            if total_inscritos > 0:
                jogador_remover = st.selectbox("Selecione para remover:", [""] + st.session_state.jogadores)
                if st.button("❌ Remover Jogador Selecionado") and jogador_remover:
                    st.session_state.jogadores.remove(jogador_remover)
                    salvar_estado_no_disco()
                    st.rerun()
                        
            st.markdown("---")
            if total_inscritos >= 4:
                if st.button("🃏 INICIAR CLASSIFICATÓRIA (5 RODADAS) 🃏"):
                    st.session_state.nome_torneio = nome_torneio
                    st.session_state.classificacao = pd.DataFrame({
                        'Jogador': st.session_state.jogadores, 'Vitorias': 0, 'Sets_Ganhos': 0, 'Tentos_Pro': 0, 'Tentos_Contra': 0, 'Saldo_Tentos': 0, 'Flores': 0
                    }).set_index('Jogador')
                    st.session_state.torneio_iniciado = True
                    st.session_state.em_matamata = False
                    st.session_state.campeao = None
                    gerar_rodada_web()
                    st.rerun()
                    
        with aba2:
            st.markdown("### 🏛️ Registro de Campeões")
            if os.path.exists(ARQUIVO_GALERIA):
                if st.button("🗑️ Limpar Todo o Histórico da Galeria", type="primary"):
                    try: os.remove(ARQUIVO_GALERIA); st.success("Galeria apagada!"); st.rerun()
                    except Exception: pass

            if os.path.exists(ARQUIVO_GALERIA):
                with open(ARQUIVO_GALERIA, "r", encoding="utf-8") as f: dados_galeria = json.load(f)
                if dados_galeria:
                    df_galeria = pd.DataFrame(dados_galeria)
                    df_galeria.columns = ["📅 Data/Hora", "🏟️ Torneio", "🥇 Campeão", "🥈 Vice", "🥉 3º Lugar", "🎖️ 4º Lugar", "🌸 Rei das Flores"]
                    st.dataframe(df_galeria, use_container_width=True, hide_index=True)
                else: st.info("Nenhum registro na galeria ainda.")
            else: st.info("A galeria de honra está limpa.")

    else:
        # ⏱️ CRONÔMETRO CENTRAL
        if not st.session_state.campeao:
            st.markdown('<div class="cronometro-box">', unsafe_allow_html=True)
            col_crono_txt, col_crono_img = st.columns([3, 1])
            with col_crono_txt:
                if st.session_state.cronometro_ativo and st.session_state.hora_inicio_rodada:
                    tempo_limite = st.session_state.hora_inicio_rodada + timedelta(minutes=45)
                    tempo_atual = datetime.now()
                    if tempo_atual < tempo_limite:
                        tempo_restante = tempo_limite - tempo_atual
                        minutos, segundos = int(tempo_restante.total_seconds() // 60), int(tempo_restante.total_seconds() % 60)
                        st.markdown(f'<h2 style="margin:0; font-family:\'Courier New\', Courier, monospace; color:#d4af37 !important; font-weight:bold;">⏱️ TEMPO RESTANTE: {minutos:02d}:{segundos:02d}</h2>', unsafe_allow_html=True)
                    else: st.markdown('<h2 style="margin:0; font-family:\'Courier New\', Courier, monospace; color:#ff4b4b !important; font-weight:bold;">⏰ TEMPO ESGOTADO!</h2>', unsafe_allow_html=True)
                else: st.markdown('<h2 style="margin:0; font-family:\'Courier New\', Courier, monospace; color:#a0a0a0 !important; font-weight:bold;">⏱️ CRONÔMETRO PAUSADO</h2>', unsafe_allow_html=True)
            with col_crono_img:
                if PATROCINADORES["master"]["logo"]: st.image(PATROCINADORES["master"]["logo"], use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # 🏆 EXIBIÇÃO DO CAMPEÃO
        if st.session_state.campeao:
            st.markdown("<h2 style='text-align: center; color: #d4af37 !important;'>✨ CERIMÔNIA DE PREMIAÇÃO FINAL ✨</h2>", unsafe_allow_html=True)
            rei_das_flores = st.session_state.classificacao.sort_values(by='Flores', ascending=False).index[0]
            max_flores = int(st.session_state.classificacao.loc[rei_das_flores, 'Flores'])
            if not st.session_state.get("salvo_na_galeria", False):
                salvar_na_galeria(st.session_state.nome_torneio, st.session_state.campeao, st.session_state.vice_campeao, st.session_state.terceiro_lugar, st.session_state.quarto_lugar, rei_das_flores, max_flores)
                st.session_state.salvo_na_galeria = True
                salvar_estado_no_disco()
            st.markdown(f'<div class="box-campeao"><h1>🥇 1º LUGAR - CAMPEÃO 🥇</h1><h2>🌟 {st.session_state.campeao} 🌟</h2></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="podio-posicao podio-vice">🥈 2º LUGAR: {st.session_state.vice_campeao}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="podio-posicao podio-terceiro">🥉 3º LUGAR: {st.session_state.terceiro_lugar}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="podio-posicao podio-quarto">🎖️ 4º LUGAR: {st.session_state.quarto_lugar}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="box-flores">🌸 REI DAS FLORES: {rei_das_flores} ({max_flores} fl.)</div>', unsafe_allow_html=True)

        # ⚡ MATA-MATA COM PLANTA BAIXA DA MESA
        elif st.session_state.em_matamata:
            st.markdown(f"#### ⚡ Fase Eliminatória: {st.session_state.fase_matamata}")
            with st.form(key=f"mm_form_{st.session_state.fase_matamata}"):
                resultados_fase = []
                for idx, confronto in enumerate(st.session_state.confrontos_mm):
                    j1, j2 = confronto["j1"], confronto["j2"]
                    texto_mesa = "🏆 GRANDE FINAL" if st.session_state.fase_matamata == "FINAIS" and not confronto.get("tipo") == "bronze" else ("🥉 DISPUTA DO 3º LUGAR" if confronto.get("tipo") == "bronze" else f"MESA {idx+1}")
                    patro_atual = PATROCINADORES["mesas"][idx % len(PATROCINADORES["mesas"])]
                    
                    # Abertura da Mesa de Jogo (Feltro e Madeira)
                    st.markdown(f"""
                    <div class="planta-mesa">
                        <div class="cabeceira-player p1-cor">🧔 {j1} (J1)</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Bloco do Meio: Central de Operações
                    with st.container():
                        st.markdown('<div class="centro-operacional">', unsafe_allow_html=True)
                        col_m_txt, col_m_img = st.columns([5, 1])
                        with col_m_txt: st.markdown(f"**🎰 CONTRATO DA {texto_mesa}** ({patro_atual['nome']})")
                        with col_m_img:
                            if patro_atual["logo"]: st.image(patro_atual["logo"], width=35)
                        
                        st.markdown("<hr style='margin:10px 0; border-color:#2c6b56;'>", unsafe_allow_html=True)
                        
                        # Painel de Inputs de Performance do J1
                        c1_s1, c1_t1, c1_f1 = st.columns(3)
                        with c1_s1: s1 = st.number_input("Sets Feitos (J1):", 0, 2, 0, key=f"mm_s1_m_{idx}")
                        with c1_t1: t1 = st.number_input("Tentos Ganhos (J1):", 0, 72, 0, key=f"mm_t1_m_{idx}")
                        with c1_f1: f1 = st.number_input("Flores Cantadas (J1):", 0, 20, 0, key=f"mm_f1_m_{idx}")
                        
                        st.markdown('<div class="vs-text">⚡ DISPUTA CENTRAL DE TENTOS ⚡</div>', unsafe_allow_html=True)
                        
                        # Painel de Inputs de Performance do J2
                        c2_s2, c2_t2, c2_f2 = st.columns(3)
                        with c2_s2: s2 = st.number_input("Sets Feitos (J2):", 0, 2, 0, key=f"mm_s2_m_{idx}")
                        with c2_t2: t2 = st.number_input("Tentos Ganhos (J2):", 0, 72, 0, key=f"mm_t2_m_{idx}")
                        with c2_f2: f2 = st.number_input("Flores Cantadas (J2):", 0, 20, 0, key=f"mm_f2_m_{idx}")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Fechamento da Base da Mesa de Jogo
                    st.markdown(f"""
                    <div class="planta-mesa" style="min-height:auto; border:none; background:none; box-shadow:none; padding:0; margin-bottom:40px;">
                        <div class="cabeceira-player p2-cor">🧔 {j2} (J2)</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    resultados_fase.append({"j1": j1, "j2": j2, "s1": s1, "s2": s2, "t1": t1, "t2": t2, "f1": f1, "f2": f2, "is_bronze": confronto.get("tipo") == "bronze", "mesa": idx+1})
                
                if st.form_submit_button("💾 COMPUTAR RESULTADOS ELIMINATÓRIOS"):
                    algoritmo_valido = True
                    dados_ajustados = []
                    for r in resultados_fase:
                        bloqueia, ns1, ns2, nt1, nt2, msg = conferir_e_ajustar_valores(r["s1"], r["s2"], r["t1"], r["t2"], r["j1"], r["j2"], r["mesa"])
                        if bloqueia: st.error(msg); algoritmo_valido = False
                        else: dados_ajustados.append({"j1": r["j1"], "j2": r["j2"], "s1": ns1, "s2": ns2, "t1": nt1, "t2": nt2, "f1": r["f1"], "f2": r["f2"], "is_bronze": r["is_bronze"]})
                    
                    if algoritmo_valido:
                        vencedores, perdedores = [], []
                        for r in dados_ajustados:
                            j1, j2, s1, s2 = r["j1"], r["j2"], r["s1"], r["s2"]
                            s1_computado = 3 if (s1 == 2 and s2 == 0) else s1
                            s2_computado = 3 if (s2 == 2 and s1 == 0) else s2
                            st.session_state.classificacao.loc[j1, ['Sets_Ganhos', 'Tentos_Pro', 'Tentos_Contra', 'Flores']] += [s1_computado, r["t1"], r["t2"], r["f1"]]
                            st.session_state.classificacao.loc[j2, ['Sets_Ganhos', 'Tentos_Pro', 'Tentos_Contra', 'Flores']] += [s2_computado, r["t2"], r["t1"], r["f2"]]
                            
                            if r["is_bronze"]:
                                if s1 > s2: st.session_state.terceiro_lugar, st.session_state.quarto_lugar = j1, j2
                                else: st.session_state.terceiro_lugar, st.session_state.quarto_lugar = j2, j1
                            else:
                                if s1 > s2: vencedores.append(j1); perdedores.append(j2)
                                else: vencedores.append(j2); perdedores.append(j1)
                                    
                        if st.session_state.fase_matamata == "OITAVAS DE FINAL": iniciar_fase_matamata(vencedores, "QUARTAS DE FINAL")
                        elif st.session_state.fase_matamata == "QUARTAS DE FINAL": iniciar_fase_matamata(vencedores, "SEMIFINAL")
                        elif st.session_state.fase_matamata == "SEMIFINAL":
                            st.session_state.fase_matamata = "FINAIS"
                            st.session_state.confrontos_mm = [{"tipo": "normal", "j1": vencedores[0], "j2": vencedores[1]}, {"tipo": "bronze", "j1": perdedores[0], "j2": perdedores[1]}]
                        elif st.session_state.fase_matamata == "FINAIS":
                            st.session_state.campeao = vencedores[0]; st.session_state.vice_campeao = perdedores[0]
                        salvar_estado_no_disco(); st.rerun()

        # 📊 CLASSIFICATÓRIA COM PLANTA BAIXA DA MESA
        else:
            tab_mesas, tab_hist = st.tabs(["⚔️ Mesas em Campo", "📜 Histórico de Jogos"])
            with tab_mesas:
                if st.session_state.rodada_atual <= 5:
                    st.markdown(f"#### 📅 Rodada {st.session_state.rodada_atual} de 5")
                    with st.form(key=f"form_rodada_exec_{st.session_state.rodada_atual}"):
                        placares = []
                        for idx, (j1, j2) in enumerate(st.session_state.confrontos):
                            patro_atual = PATROCINADORES["mesas"][idx % len(PATROCINADORES["mesas"])]
                            
                            if j2 == "CHAPÉU (Folga)":
                                st.markdown('<div class="card-mesa">', unsafe_allow_html=True)
                                st.markdown(f"🤠 <span class='texto-confronto'><b>{j1}</b> está no CHAPÉU (Folga da Rodada)</span>", unsafe_allow_html=True)
                                st.markdown('</div>', unsafe_allow_html=True)
                                placares.append(None)
                            else:
                                # Abertura da Mesa de Jogo (Feltro e Madeira)
                                st.markdown(f"""
                                <div class="planta-mesa">
                                    <div class="cabeceira-player p1-cor">🧔 {j1} (J1)</div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Bloco do Meio: Central de Operações
                                with st.container():
                                    st.markdown('<div class="centro-operacional">', unsafe_allow_html=True)
                                    col_m_txt, col_m_img = st.columns([5, 1])
                                    with col_m_txt: st.markdown(f"**🎰 CONTRATO DA MESA {idx+1}** ({patro_atual['nome']})")
                                    with col_m_img:
                                        if patro_atual["logo"]: st.image(patro_atual["logo"], width=35)
                                    
                                    st.markdown("<hr style='margin:10px 0; border-color:#2c6b56;'>", unsafe_allow_html=True)
                                    
                                    # Painel de Inputs de Performance do J1
                                    c1_s1, c1_t1, c1_f1 = st.columns(3)
                                    with c1_s1: s1 = st.number_input("Sets Feitos (J1):", 0, 2, 0, key=f"cl_s1_m_{idx}")
                                    with c1_t1: t1 = st.number_input("Tentos Ganhos (J1):", 0, 72, 0, key=f"cl_t1_m_{idx}")
                                    with c1_f1: f1 = st.number_input("Flores Cantadas (J1):", 0, 20, 0, key=f"cl_f1_m_{idx}")
                                    
                                    st.markdown('<div class="vs-text">⚡ DISPUTA CENTRAL DE TENTOS ⚡</div>', unsafe_allow_html=True)
                                    
                                    # Painel de Inputs de Performance do J2
                                    c2_s2, c2_t2, c2_f2 = st.columns(3)
                                    with c2_s2: s2 = st.number_input("Sets Feitos (J2):", 0, 2, 0, key=f"cl_s2_m_{idx}")
                                    with c2_t2: t2 = st.number_input("Tentos Ganhos (J2):", 0, 72, 0, key=f"cl_t2_m_{idx}")
                                    with c2_f2: f2 = st.number_input("Flores Cantadas (J2):", 0, 20, 0, key=f"cl_f2_m_{idx}")
                                    
                                    st.markdown('</div>', unsafe_allow_html=True)
                                
                                # Fechamento da Base da Mesa de Jogo
                                st.markdown(f"""
                                <div class="planta-mesa" style="min-height:auto; border:none; background:none; box-shadow:none; padding:0; margin-bottom:40px;">
                                    <div class="cabeceira-player p2-cor">🧔 {j2} (J2)</div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                placares.append((s1, s2, t1, t2, f1, f2))
                        
                        if st.form_submit_button("💾 COMPUTAR PAINEL DE MESAS"):
                            sucesso_validacao = True
                            dados_ajustados = []
                            for idx, c in enumerate(placares):
                                j1, j2 = st.session_state.confrontos[idx]
                                if j2 != "CHAPÉU (Folga)":
                                    s1, s2, t1, t2, f1, f2 = c
                                    bloqueia, ns1, ns2, nt1, nt2, msg = conferir_e_ajustar_valores(s1, s2, t1, t2, j1, j2, idx+1)
                                    if bloqueia: st.error(msg); sucesso_validacao = False
                                    else: dados_ajustados.append((ns1, ns2, nt1, nt2, f1, f2))
                                else: dados_ajustados.append(None)
                                        
                            if sucesso_validacao:
                                dados_hist = []
                                for idx, c in enumerate(dados_ajustados):
                                    j1, j2 = st.session_state.confrontos[idx]
                                    if j2 == "CHAPÉU (Folga)":
                                        st.session_state.classificacao.loc[j1, ['Vitorias', 'Sets_Ganhos', 'Tentos_Pro']] += [1, 3, 72]
                                        dados_hist.append({"Mesa": idx+1, "Jogador 1": j1, "Placar": "CHAPÉU", "Jogador 2": "Folga"})
                                    else:
                                        s1, s2, t1, t2, f1, f2 = c
                                        s1_computado = 3 if (s1 == 2 and s2 == 0) else s1
                                        s2_computado = 3 if (s2 == 2 and s1 == 0) else s2
                                        st.session_state.classificacao.loc[j1, ['Vitorias', 'Sets_Ganhos', 'Tentos_Pro', 'Tentos_Contra', 'Flores']] += [(1 if s1 > s2 else 0), s1_computado, t1, t2, f1]
                                        st.session_state.classificacao.loc[j2, ['Vitorias', 'Sets_Ganhos', 'Tentos_Pro', 'Tentos_Contra', 'Flores']] += [(1 if s2 > s1 else 0), s2_computado, t2, t1, f2]
                                        dados_hist.append({"Mesa": idx+1, "Jogador 1": j1, "Placar": f"({s1}s | {t1}t) ✖ ({s2}s | {t2}t)", "Jogador 2": j2})
                                
                                st.session_state.historico_rodadas[f"Rodada {st.session_state.rodada_atual}"] = dados_hist
                                st.session_state.classificacao['Saldo_Tentos'] = st.session_state.classificacao['Tentos_Pro'] - st.session_state.classificacao['Tentos_Contra']
                                st.session_state.rodada_atual += 1
                                if st.session_state.rodada_atual <= 5: gerar_rodada_web()
                                salvar_estado_no_disco(); st.rerun()
				else:
                    st.success("🎉 Classificatória Encerrada!")
                    n_insc = len(st.session_state.jogadores)
                    f_nome = "OITAVAS DE FINAL" if n_insc > 16 else ("QUARTAS DE FINAL" if n_insc >= 8 else "SEMIFINAL")
                    qtd_c = 16 if n_insc > 16 else (8 if n_insc >= 8 else 4)
                    if st.button(f"🏆 GERAR CHAVE DE {f_nome}"):
                        df_v = st.session_state.classificacao.sort_values(by=['Vitorias', 'Sets_Ganhos', 'Saldo_Tentos'], ascending=False)
                        iniciar_fase_matamata(list(df_v.index[:qtd_c]), f_nome)
                        st.rerun()

            with tab_hist:
                st.markdown("#### 🔍 Histórico de Partidas Concluídas")
                for r_nome in sorted(st.session_state.historico_rodadas.keys(), reverse=True):
                    with st.expander(r_nome):
                        for jogo in st.session_state.historico_rodadas[r_nome]:
                            st.write(f"Mesa {jogo['Mesa']}: {jogo['Jogador 1']} {jogo['Placar']} {jogo['Jogador 2']}")

# -------------------------------------------------------------------------
# 📊 COLUNA DA DIREITA: Classificação Permanente no Telão
# -------------------------------------------------------------------------
with col_direita:
    st.markdown("### 📊 Classificação Atual")
    st.markdown('<div class="card-lateral">', unsafe_allow_html=True)
    if st.session_state.classificacao is not None:
        df_rank = st.session_state.classificacao.sort_values(by=['Vitorias', 'Sets_Ganhos', 'Saldo_Tentos'], ascending=False)
        for i, (competidor, linha) in enumerate(df_rank.iterrows()):
            icone = "🥇" if i == 0 else ("🥈" if i == 1 else ("🥉" if i == 2 else "🔹"))
            st.markdown(f"{icone} **{competidor}** <br> `{int(linha['Vitorias'])} Vitórias` | `S: {int(linha['Sets_Ganhos'])}` | `Fl: {int(linha['Flores'])}`", unsafe_allow_html=True)
            st.markdown('<hr style="border-color: #1a3327; margin: 6px 0;">', unsafe_allow_html=True)
    else: st.info("Aguardando o início do torneio.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- RODAPÉ COM OS PARCEIROS ---
st.markdown('<hr style="border-color: #2c6b56; margin-top: 40px;">', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-weight: bold;'>🤝 PARCEIROS OFICIAIS DA TRADIÇÃO</p>", unsafe_allow_html=True)

col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns(5)
for i, col in enumerate([col_f1, col_f2, col_f3, col_f4, col_f5]):
    with col:
        patro = PATROCINADORES["mesas"][i]
        if patro["logo"]: st.image(patro["logo"], use_container_width=True, caption=patro["nome"])
        else: st.caption(patro["nome"])

st.markdown(f"""
    <div class="creditos">
        💻 Criado por <b>{NOME_CRIADOR}</b> | Todos os direitos reservados © 2026
    </div>
""", unsafe_allow_html=True)
