import streamlit as st
import pandas as pd
import random
import json
import os
import qrcode
from io import BytesIO
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Torneio de Truco de Mano - Sicredi & Cusco",
    page_icon="🏆",
    layout="centered"
)

NOME_CRIADOR = "Eduardo Luis Ferreira"
ARQUIVO_BACKUP = "torneio_demo.json"
ARQUIVO_GALERIA = "galeria_demo.json"

CHAVE_ADMINISTRADOR = "truco123"

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
        "nome_torneio": st.session_state.get("nome_torneio", "I Copa de Truco de Mano Sicredi/Cusco"),
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
            st.session_state.nome_torneio = estado.get("nome_torneio", "I Copa de Truco de Mano Sicredi/Cusco")
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

# --- INICIALIZAÇÃO DE MEMÓRIA ---
valores_padrao = {
    "jogadores": [],
    "torneio_iniciado": False,
    "rodada_atual": 1,
    "classificacao": None,
    "confrontos": [],
    "jogadores_no_chapeu": set(),
    "hora_inicio_rodada": None,
    "cronometro_ativo": False,
    "historico_rodadas": {},
    "em_matamata": False,
    "fase_matamata": "",
    "confrontos_mm": [],
    "campeao": None,
    "vice_campeao": None,
    "terceiro_lugar": None,
    "quarto_lugar": None,
    "perdedores_semi": [],
    "salvo_na_galeria": False
}

for chave, valor in valores_padrao.items():
    if chave not in st.session_state:
        st.session_state[chave] = valor

if os.path.exists(ARQUIVO_BACKUP):
    carregar_estado_do_disco()

# --- ESTILIZAÇÃO CSS CUSTOMIZADA ---
st.markdown("""
    <style>
    .stApp { background-color: #1b4d3e; }
    h1, h2, h3, h4, p, label, .stMarkdown { color: #ffffff !important; }
    .stButton>button {
        background-color: #d4af37 !important; color: #111111 !important;
        font-weight: bold !important; border-radius: 8px !important; width: 100%;
    }
    .card-mesa { background-color: #2c6b56; padding: 15px; border-radius: 10px; margin-bottom: 15px; border: 1px solid #d4af37; }
    .cronometro-box { background-color: #11221a; border: 2px solid #d4af37; padding: 10px; border-radius: 8px; text-align: center; font-family: 'Courier New', Courier, monospace; margin-bottom: 15px; }
    
    /* Pódio e Destaques dos Campeões */
    .box-campeao { background-color: #d4af37; padding: 25px; border-radius: 15px; text-align: center; color: #111111 !important; border: 3px solid #ffffff; margin-bottom: 20px; }
    .box-campeao h1, .box-campeao h2 { color: #111111 !important; margin: 5px 0; }
    .podio-posicao { padding: 15px; border-radius: 10px; text-align: center; font-weight: bold; margin-bottom: 12px; color: #ffffff !important; font-size: 1.1rem; }
    .podio-vice { background-color: #a0a0a0; border: 2px solid #d1d1d1; }
    .podio-terceiro { background-color: #cd7f32; border: 2px solid #e5a65d; }
    .podio-quarto { background-color: #2c6b56; border: 2px solid #d4af37; }
    .box-flores { background-color: #4a1525; padding: 15px; border-radius: 10px; text-align: center; color: #ffffff !important; border: 2px solid #ff4b4b; margin-top: 15px; margin-bottom: 20px; }
    
    /* Estilos dos Patrocinadores */
    .banner-patrocinio-side { background-color: #ffffff; padding: 12px; border-radius: 8px; text-align: center; color: #333333 !important; border-left: 6px solid #34a853; margin-bottom: 20px; }
    .logo-patrocinio { font-size: 1.1rem; font-weight: bold; margin: 2px 0; }
    .marca-sicredi { color: #34a853 !important; }
    .marca-cusco { color: #8b5a2b !important; font-family: 'Georgia', serif; }
    
    .creditos { text-align: center; color: #a0c0b5 !important; font-size: 0.8rem; margin-top: 50px; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR COM PAINEL DE PATROCÍNIO ---
st.sidebar.markdown("""
    <div class="banner-patrocinio-side">
        <p style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; margin: 0; color: #666666 !important;">Apoio Oficial</p>
        <div class="logo-patrocinio marca-sicredi">🌲 Sicredi</div>
        <div class="logo-patrocinio marca-cusco">🐾 Cusco</div>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown("### 🔐 Controle de Acesso")
senha_inserida = st.sidebar.text_input("Chave do Operador:", type="password")
is_admin = (senha_inserida == CHAVE_ADMINISTRADOR)

if is_admin:
    st.sidebar.success("⚡ Modo Administrador Ativo")
else:
    st.sidebar.info("👁️ Modo Visualizador Público")

# --- TRAVA MATEMÁTICA DEFINITIVA ---
def conferir_e_ajustar_valores(s1, s2, t1, t2, n1, n2, mesa_id):
    if (s1 == 2 and s2 == 2) or (s1 < 2 and s2 < 2):
        return True, s1, s2, t1, t2, f"Mesa {mesa_id}: Placar de Sets inválido ({s1}x{s2}). Alguém precisa fechar com exatamente 2 sets."

    if s1 == 2 and s2 == 0:
        t1 = 72
        if t2 > 46:
            return True, s1, s2, t1, t2, f"Mesa {mesa_id}: Inconsistência! No 2x0, o perdedor ({n2}) não pode somar mais do que 46 tentos."

    elif s2 == 2 and s1 == 0:
        t2 = 72
        if t1 > 46:
            return True, s1, s2, t1, t2, f"Mesa {mesa_id}: Inconsistência! No 2x0, o perdedor ({n1}) não pode somar mais do que 46 tentos."

    elif s1 == 2 and s2 == 1:
        if t1 < 48:
            return True, s1, s2, t1, t2, f"Mesa {mesa_id}: Inconsistência! Como {n1} fez 2 sets, ele precisa ter no mínimo 48 tentos."
        if t2 < 24:
            return True, s1, s2, t1, t2, f"Mesa {mesa_id}: Inconsistência! Como {n2} fez 1 set, ele precisa ter no mínimo 24 tentos."

    elif s2 == 2 and s1 == 1:
        if t2 < 48:
            return True, s1, s2, t1, t2, f"Mesa {mesa_id}: Inconsistência! Como {n2} fez 2 sets, ele precisa ter no mínimo 48 tentos."
        if t1 < 24:
            return True, s1, s2, t1, t2, f"Mesa {mesa_id}: Inconsistência! Como {n1} fez 1 set, ele precisa ter no mínimo 24 tentos."

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
    salvar_estado_no_disco()

def iniciar_fase_matamata(lista_jogadores, nome_fase):
    st.session_state.em_matamata = True
    st.session_state.fase_matamata = nome_fase
    st.session_state.confrontos_mm = []
    n = len(lista_jogadores)
    for i in range(n // 2):
        st.session_state.confrontos_mm.append({"tipo": "normal", "j1": lista_jogadores[i], "j2": lista_jogadores[n - 1 - i]})
    salvar_estado_no_disco()

# --- CONTEÚDO PRINCIPAL ---
st.title("🏆 Circuito de Truco de Mano")

# === TELA 1: CADASTRO / CONFIGURAÇÃO DO TORNEIO ===
if not st.session_state.torneio_iniciado:
    aba1, aba2 = st.tabs(["🎮 Painel de Inscrições", "📜 Galeria de Campeões"])
    
    with aba1:
        st.markdown("### 🎪 Identificação do Evento")
        if is_admin:
            nome_torneio = st.text_input("Nome do Torneio ou CTG:", value=st.session_state.get("nome_torneio", "I Copa de Truco de Mano Sicredi/Cusco"))
        else:
            st.markdown(f"**{st.session_state.get('nome_torneio', 'I Copa de Truco de Mano Sicredi/Cusco')}**")
        
        st.markdown("---")
        st.markdown("### 👤 Cadastro Prático de Competidores")
        
        if is_admin:
            with st.form(key="form_cadastro", clear_on_submit=True):
                novo_jogador = st.text_input("Nome do Jogador:")
                if st.form_submit_button("➕ Registrar") and novo_jogador:
                    name_clean = novo_jogador.strip()
                    if name_clean not in st.session_state.jogadores and name_clean != "":
                        st.session_state.jogadores.append(name_clean)
                        salvar_estado_no_disco()
                        st.rerun()
            
            if st.button("🃏 Carregar Lista de Demonstração (8 Jogadores)"):
                st.session_state.jogadores = ["Gaudêncio", "Pedro Ortaça", "Neto Fagundes", "Borghettinho", "Telmo de Lima", "Jayme Caetano", "Noel Guarany", "Cenair Maicá"]
                salvar_estado_no_disco()
                st.rerun()

        total_inscritos = len(st.session_state.jogadores)
        st.markdown(f"**Inscritos atuais: {total_inscritos}**")
        st.write(", ".join(st.session_state.jogadores) if st.session_state.jogadores else "Nenhum jogador cadastrado.")
        
        if is_admin and total_inscritos >= 4:
            if st.button("🃏 INICIAR ETAPA CLASSIFICATÓRIA 🃏"):
                st.session_state.nome_torneio = nome_torneio
                st.session_state.classificacao = pd.DataFrame({
                    'Jogador': st.session_state.jogadores,
                    'Vitorias': 0, 'Sets_Ganhos': 0, 'Tentos_Pro': 0, 'Tentos_Contra': 0, 'Saldo_Tentos': 0, 'Flores': 0
                }).set_index('Jogador')
                st.session_state.torneio_iniciado = True
                st.session_state.em_matamata = False
                st.session_state.campeao = None
                gerar_rodada_web()
                st.rerun()
                
    with aba2:
        st.info("A galeria exibirá o histórico das copas anteriores organizadas.")

# === TELA 2: ANDAMENTO DO TORNEIO ===
else:
    st.markdown(f"### 🏟️ {st.session_state.nome_torneio}")
    
    # 1. CASO TENHA UM CAMPEÃO DEFINIDO -> EXIBE O PÓDIO FINAL EM DESTAQUE
    if st.session_state.campeao:
        st.markdown("<h2 style='text-align: center; color: #d4af37 !important;'>✨ CERIMÔNIA DE PREMIAÇÃO ✨</h2>", unsafe_allow_html=True)
        
        rei_das_flores = st.session_state.classificacao.sort_values(by='Flores', ascending=False).index[0]
        max_flores = int(st.session_state.classificacao.loc[rei_das_flores, 'Flores'])
        
        st.markdown(f'<div class="box-campeao"><h1>🥇 1º LUGAR - CAMPEÃO 🥇</h1><h2>🌟 {st.session_state.campeao} 🌟</h2></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="podio-posicao podio-vice">🥈 2º LUGAR: {st.session_state.vice_campeao}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="podio-posicao podio-terceiro">🥉 3º LUGAR: {st.session_state.terceiro_lugar}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="podio-posicao podio-quarto">🎖️ 4º LUGAR: {st.session_state.quarto_lugar}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="box-flores">🌸 REI DAS FLORES: {rei_das_flores} ({max_flores} fl.)</div>', unsafe_allow_html=True)
        
        # --- TRAVA DE RESET NA TELA FINAL ---
        if is_admin:
            st.markdown("---")
            if st.button("🏁 LIMPAR HISTÓRICO E REINICIAR (NOVO TORNEIO)"):
                if os.path.exists(ARQUIVO_BACKUP): os.remove(ARQUIVO_BACKUP)
                st.session_state.clear()
                st.rerun()

    # 2. CASO ESTEJA NO MATA-MATA (EXIBE AS MESAS DE CONFRONTO DA FASE ATUAL)
    elif st.session_state.em_matamata:
        st.markdown(f"#### ⚡ Fase Atual: {st.session_state.fase_matamata}")
        
        if is_admin:
            with st.form(key=f"mm_form_exec_{st.session_state.fase_matamata}"):
                resultados_fase = []
                for idx, confronto in enumerate(st.session_state.confrontos_mm):
                    j1, j2 = confronto["j1"], confronto["j2"]
                    label_mesa = "🏆 GRANDE FINAL" if confronto.get("tipo") == "normal" and st.session_state.fase_matamata == "FINAIS" else (
                        "🥉 DISPUTA DE 3º LUGAR" if confronto.get("tipo") == "bronze" else f"Mesa {idx+1}"
                    )
                    
                    st.markdown(f'<div class="card-mesa"><b>{label_mesa}</b></div>', unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"**{j1}**")
                        s1 = st.number_input("Sets:", min_value=0, max_value=2, step=1, key=f"mm_s1_{idx}")
                        t1 = st.number_input("Tentos:", min_value=0, max_value=72, step=1, key=f"mm_t1_{idx}")
                        f1 = st.number_input("Flores:", min_value=0, max_value=20, step=1, key=f"mm_f1_{idx}")
                    with c2:
                        st.markdown(f"**{j2}**")
                        s2 = st.number_input("Sets:", min_value=0, max_value=2, step=1, key=f"mm_s2_{idx}")
                        t2 = st.number_input("Tentos:", min_value=0, max_value=72, step=1, key=f"mm_t2_{idx}")
                        f2 = st.number_input("Flores:", min_value=0, max_value=20, step=1, key=f"mm_f2_{idx}")
                    resultados_fase.append({"j1": j1, "j2": j2, "s1": s1, "s2": s2, "t1": t1, "t2": t2, "f1": f1, "f2": f2, "is_bronze": confronto.get("tipo") == "bronze", "mesa": idx+1})
                
                if st.form_submit_button("💾 COMPUTAR RESULTADOS DESTA FASE"):
                    sucesso_validacao = True
                    dados_ajustados = []
                    
                    for r in resultados_fase:
                        bloqueia, ns1, ns2, nt1, nt2, msg = conferir_e_ajustar_valores(r["s1"], r["s2"], r["t1"], r["t2"], r["j1"], r["j2"], r["mesa"])
                        if bloqueia:
                            st.error(msg)
                            sucesso_validacao = False
                        else:
                            dados_ajustados.append({"j1": r["j1"], "j2": r["j2"], "s1": ns1, "s2": ns2, "t1": nt1, "t2": nt2, "f1": r["f1"], "f2": r["f2"], "is_bronze": r["is_bronze"]})
                    
                    if技术_sucesso := sucesso_validacao:
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
                            st.session_state.confrontos_mm = [
                                {"tipo": "normal", "j1": vencedores[0], "j2": vencedores[1]},
                                {"tipo": "bronze", "j1": perdedores[0], "j2": perdedores[1]}
                            ]
                        elif st.session_state.fase_matamata == "FINAIS":
                            st.session_state.campeao = vencedores[0]
                            st.session_state.vice_campeao = perdedores[0]
                            
                        salvar_estado_no_disco()
                        st.rerun()
            
            # --- TRAVA DE RESET NO MEIO DO MATA-MATA ---
            st.markdown("---")
            if st.button("🚨 FORÇAR CANCELAMENTO E RESETAR TORNEIO"):
                if os.path.exists(ARQUIVO_BACKUP): os.remove(ARQUIVO_BACKUP)
                st.session_state.clear()
                st.rerun()
        else:
            for idx, c in enumerate(st.session_state.confrontos_mm):
                label_mesa = "🏆 GRANDE FINAL" if c.get("tipo") == "normal" and st.session_state.fase_matamata == "FINAIS" else (
                    "🥉 DISPUTA DE 3º LUGAR" if c.get("tipo") == "bronze" else f"Mesa {idx+1}"
                )
                st.markdown(f"<div class='card-mesa'><b>{label_mesa}:</b> {c['j1']} ⚔️ {c['j2']}</div>", unsafe_allow_html=True)

    # 3. CASO ESTEJA NA FASE CLASSIFICATÓRIA
    else:
        tab_mesas, tab_tabela, tab_hist = st.tabs(["⚔️ Mesas da Rodada", "📊 Tabela Geral", "📜 Histórico de Jogos"])
        
        with tab_mesas:
            st.markdown(f"#### 📅 Rodada {st.session_state.rodada_atual} (Modelo Demo)")
            
            if is_admin:
                with st.form(key=f"form_rodada_exec_{st.session_state.rodada_atual}"):
                    placares = []
                    for idx, (j1, j2) in enumerate(st.session_state.confrontos):
                        st.markdown(f'<div class="card-mesa"><b>Mesa {idx+1}</b></div>', unsafe_allow_html=True)
                        if j2 == "CHAPÉU (Folga)":
                            st.markdown(f"🤠 **{j1}** está no CHAPÉU")
                            placares.append(None)
                        else:
                            c1, c2 = st.columns(2)
                            with c1:
                                st.markdown(f"**{j1}**")
                                s1 = st.number_input("Sets:", 0, 2, 0, key=f"s1_{idx}")
                                t1 = st.number_input("Tentos:", 0, 72, 0, key=f"t1_{idx}")
                                f1 = st.number_input("Flores:", 0, 20, 0, key=f"f1_{idx}")
                            with c2:
                                st.markdown(f"**{j2}**")
                                s2 = st.number_input("Sets:", 0, 2, 0, key=f"s2_{idx}")
                                t2 = st.number_input("Tentos:", 0, 72, 0, key=f"t2_{idx}")
                                f2 = st.number_input("Flores:", 0, 20, 0, key=f"f2_{idx}")
                            placares.append((s1, s2, t1, t2, f1, f2))
                    
                    if st.form_submit_button("💾 COMPUTAR RESULTADOS"):
                        sucesso_validacao = True
                        dados_ajustados = []
                        
                        for idx, c in enumerate(placares):
                            j1, j2 = st.session_state.confrontos[idx]
                            if j2 != "CHAPÉU (Folga)":
                                s1, s2, t1, t2, f1, f2 = c
                                bloqueia, ns1, ns2, nt1, nt2, msg = conferir_e_ajustar_valores(s1, s2, t1, t2, j1, j2, idx+1)
                                if bloqueia:
                                    st.error(msg)
                                    sucesso_validacao = False
                                else:
                                    dados_ajustados.append((ns1, ns2, nt1, nt2, f1, f2))
                            else:
                                dados_ajustados.append(None)
                                    
                        if技术_sucesso := sucesso_validacao:
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
                            if st.session_state.rodada_atual <= 3:
                                gerar_rodada_web()
                            else:
                                salvar_estado_no_disco()
                            st.rerun()
                            
                # --- TRAVA DE RESET NA FASE CLASSIFICATÓRIA ---
                st.markdown("---")
                if st.button("🚨 REINICIAR TODO O TORNEIO (LIMPAR HISTÓRICO)"):
                    if os.path.exists(ARQUIVO_BACKUP): os.remove(ARQUIVO_BACKUP)
                    st.session_state.clear()
                    st.rerun()
            else:
                for idx, (j1, j2) in enumerate(st.session_state.confrontos):
                    st.markdown(f"<div class='card-mesa'><b>Mesa {idx+1}:</b> {j1} ⚔️ {j2}</div>", unsafe_allow_html=True)
            
            if st.session_state.rodada_atual > 3:
                st.success("🎉 Classificatória de Demonstração Concluída!")
                if is_admin:
                    if st.button("🏆 GERAR CHAVE MATA-MATA (Top 4)"):
                        df_v = st.session_state.classificacao.sort_values(by=['Vitorias', 'Sets_Ganhos', 'Saldo_Tentos'], ascending=False)
                        iniciar_fase_matamata(list(df_v.index[:4]), "SEMIFINAL")
                        st.rerun()

        with tab_tabela:
            st.markdown("#### 📊 Tabela Geral Classificatória")
            df_exibir = st.session_state.classificacao.sort_values(by=['Vitorias', 'Sets_Ganhos', 'Saldo_Tentos'], ascending=False)
            st.dataframe(df_exibir[['Vitorias', 'Sets_Ganhos', 'Saldo_Tentos', 'Flores']], use_container_width=True)

        with tab_hist:
            st.markdown("#### 🔍 Histórico de Partidas")
            for r_nome in sorted(st.session_state.historico_rodadas.keys(), reverse=True):
                with st.expander(r_nome):
                    for jogo in st.session_state.historico_rodadas[r_nome]:
                        st.write(f"Mesa {jogo['Mesa']}: {jogo['Jogador 1']} {jogo['Placar']} {jogo['Jogador 2']}")

st.markdown(f"""
    <div class="creditos">
        <hr style="border-color: #2c6b56;">
        <b>{st.session_state.get("nome_torneio", "I Copa de Truco de Mano Sicredi/Cusco")}</b><br>
        Parceiros Comerciais: <b>Sicredi</b> & <b>Cusco</b><br>
        <span style="font-size:0.7rem;">Desenvolvido por {NOME_CRIADOR} | © 2026</span>
    </div>
""", unsafe_allow_html=True)
