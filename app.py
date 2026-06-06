import streamlit as st
import pandas as pd
import random
import json
import os
import qrcode
from io import BytesIO
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Sistema de Torneios de Truco de Mano",
    page_icon="🏆",
    layout="centered"
)

NOME_CRIADOR = "Eduardo Luis Ferreira"
ARQUIVO_BACKUP = "torneio_atual.json"
ARQUIVO_GALERIA = "galeria_campeoes.json"

# CHAVE DE ACESSO PARA MODIFICAR O TORNEIO (Troque por uma de sua preferência)
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

# --- INICIALIZAÇÃO DE MEMÓRIA (BLINDADA CONTRA ERROS) ---
valores_padrao = {
    "jogadores": [],
    "torneio_iniciado": False,
    "rodada_atual": 1,
    "classificacao": None,
    "confrontos": [],
    "jogadores_no_chapeu": set(),
    "hora_inicio_rodada": None,
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

# --- ESTILIZAÇÃO CSS COMPLETA ---
st.markdown("""
    <style>
    .stApp { background-color: #1b4d3e; }
    h1, h2, h3, h4, p, label, .stMarkdown { color: #ffffff !important; }
    .stButton>button {
        background-color: #d4af37 !important; color: #111111 !important;
        font-weight: bold !important; border-radius: 8px !important; width: 100%;
    }
    .card-mesa { background-color: #2c6b56; padding: 15px; border-radius: 10px; margin-bottom: 15px; border: 1px solid #d4af37; }
    
    /* Mesa Especial da Final */
    .card-mesa-final { 
        background-color: #11221a; 
        padding: 20px; 
        border-radius: 12px; 
        margin-bottom: 20px; 
        border: 3px solid #d4af37;
        box-shadow: 0px 0px 15px #d4af37;
        text-align: center;
    }
    
    .card-historico { background-color: #14382d; padding: 10px; border-radius: 8px; margin-bottom: 10px; border-left: 5px solid #d4af37; }
    .cronometro-box { background-color: #11221a; border: 2px solid #d4af37; padding: 10px; border-radius: 8px; text-align: center; font-family: 'Courier New', Courier, monospace; margin-bottom: 15px; }
    
    /* Design Estilizado da Tela de Premiação */
    .box-campeao { background-color: #d4af37; padding: 25px; border-radius: 15px; text-align: center; color: #111111 !important; border: 3px solid #ffffff; margin-bottom: 15px; }
    .podio-posicao { padding: 15px; border-radius: 10px; text-align: center; font-weight: bold; margin-bottom: 10px; color: #ffffff !important; }
    .podio-vice { background-color: #a0a0a0; border: 2px solid #d1d1d1; }
    .podio-terceiro { background-color: #cd7f32; border: 2px solid #e5a65d; }
    .podio-quarto { background-color: #2c6b56; border: 2px solid #d4af37; }
    .box-flores { background-color: #4a1525; padding: 15px; border-radius: 10px; text-align: center; color: #ffffff !important; border: 2px solid #ff4b4b; margin-top: 15px; margin-bottom: 20px; }
    
    .creditos { text-align: center; color: #a0c0b5 !important; font-size: 0.8rem; margin-top: 50px; }
    </style>
""", unsafe_allow_html=True)

# --- CONTROLE DE ACESSO E QR CODE (SIDEBAR) ---
st.sidebar.markdown("### 🔐 Controle de Acesso")
senha_inserida = st.sidebar.text_input("Chave do Operador:", type="password", help="Insira a senha secreta para liberar o lançamento de resultados.")

# Validação do status de admin
is_admin = (senha_inserida == CHAVE_ADMINISTRADOR)

if is_admin:
    st.sidebar.success("⚡ Modo Administrador Ativo")
    
    # --- GERADOR DE QR CODE PARA O PÚBLICO ---
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📱 Compartilhar Torneio")
    
    # Caso queira fixar o link definitivo na internet, pode substituir a string abaixo:
    url_torneio = "https://truco-ctg.streamlit.app" 
    
    if st.sidebar.button("🍏 Gerar QR Code de Visualização"):
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(url_torneio)
        qr.make(fit=True)
        img_qr = qr.make_image(fill_color="black", back_color="white")
        
        buf = BytesIO()
        img_qr.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        st.sidebar.image(byte_im, caption="Aponte a câmera do celular para acompanhar!", use_container_width=True)
else:
    st.sidebar.info("👁️ Modo Visualizador Público")

# --- FUNÇÕES DE LOGICA ---
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
    st.session_state.hora_inicio_rodada = datetime.now()
    salvar_estado_no_disco()

def iniciar_fase_matamata(lista_jogadores, nome_fase):
    st.session_state.em_matamata = True
    st.session_state.fase_matamata = nome_fase
    st.session_state.confrontos_mm = []
    
    n = len(lista_jogadores)
    for i in range(n // 2):
        st.session_state.confrontos_mm.append({"tipo": "normal", "j1": lista_jogadores[i], "j2": lista_jogadores[n - 1 - i]})
    
    st.session_state.hora_inicio_rodada = datetime.now()
    salvar_estado_no_disco()

# --- CONTEÚDO PRINCIPAL ---
st.title("🏆 Truco de Mano")

# === TELA 1: CADASTRO / CONFIGURAÇÃO DO TORNEIO ===
if not st.session_state.torneio_iniciado:
    opcoes_menu = ["🎮 Novo Torneio" if is_admin else "🎯 Inscrições Atuais", "📜 Galeria de Campeões"]
    aba_inicial = st.radio("Selecione:", opcoes_menu, horizontal=True)
    
    if aba_inicial in ["🎮 Novo Torneio", "🎯 Inscrições Atuais"]:
        st.markdown("### 🎪 Identificação do Evento")
        if is_admin:
            nome_torneio = st.text_input("Nome do Torneio ou CTG:", value=st.session_state.get("nome_torneio", "Torneio de Truco do CTG"))
        else:
            st.markdown(f"**{st.session_state.get('nome_torneio', 'Torneio de Truco do CTG')}**")
        
        st.markdown("---")
        st.markdown("### 👤 Cadastro de Jogadores")
        
        if is_admin:
            with st.form(key="form_cadastro", clear_on_submit=True):
                novo_jogador = st.text_input("Nome do Jogador:")
                botao_add = st.form_submit_button(label="➕ Adicionar Jogador")
                if botao_add and novo_jogador:
                    nome_limpo = novo_jogador.strip()
                    if nome_limpo in st.session_state.jogadores:
                        st.warning(f"⚠️ O jogador '{nome_limpo}' já está inscrito!")
                    elif nome_limpo != "":
                        st.session_state.jogadores.append(nome_limpo)
                        salvar_estado_no_disco()
                        st.success(f"🃏 {nome_limpo} adicionado com sucesso!")
        else:
            st.info("🔒 O cadastro de jogadores está fechado para o público. Aguarde o início do organizador.")

        total_inscritos = len(st.session_state.jogadores)
        st.markdown(f"**Inscritos atuais: {total_inscritos} / 64**")
        
        if not is_admin and total_inscritos > 0:
            st.write(", ".join(st.session_state.jogadores))
        
        if is_admin and total_inscritos > 0:
            jogador_remover = st.selectbox("Selecione para remover:", [""] + st.session_state.jogadores)
            if st.button("❌ Remover Jogador Selecionado") and jogador_remover:
                st.session_state.jogadores.remove(jogador_remover)
                salvar_estado_no_disco()
                st.rerun()
                    
        st.markdown("---")
        if is_admin:
            if st.button("🃏 INICIAR CLASSIFICATÓRIA (5 RODADAS) 🃏"):
                if total_inscritos < 4:
                    st.error("❌ É necessário pelo menos 4 jogadores!")
                else:
                    st.session_state.nome_torneio = nome_torneio
                    st.session_state.classificacao = pd.DataFrame({
                        'Jogador': st.session_state.jogadores,
                        'Vitorias': 0, 'Sets_Ganhos': 0, 'Tentos_Pro': 0, 'Tentos_Contra': 0, 'Saldo_Tentos': 0, 'Flores': 0
                    }).set_index('Jogador')
                    st.session_state.torneio_iniciado = True
                    st.session_state.em_matamata = False
                    st.session_state.campeao = None
                    st.session_state.vice_campeao = None
                    st.session_state.terceiro_lugar = None
                    st.session_state.quarto_lugar = None
                    st.session_state.perdedores_semi = []
                    st.session_state.salvo_na_galeria = False
                    gerar_rodada_web()
                    st.rerun()
                
    elif aba_inicial == "📜 Galeria de Campeões":
        st.markdown("### 🏛️ Registro de Campeões e Histórico do Torneio")
        if os.path.exists(ARQUIVO_GALERIA):
            with open(ARQUIVO_GALERIA, "r", encoding="utf-8") as f:
                dados_galeria = json.load(f)
            if dados_galeria:
                df_galeria = pd.DataFrame(dados_galeria)
                df_galeria.columns = ["📅 Data/Hora", "🏟️ Torneio", "🥇 Campeão", "🥈 Vice", "🥉 3º Lugar", "🎖️ 4º Lugar", "🌸 Rei das Flores"]
                st.dataframe(df_galeria, use_container_width=True, hide_index=True)
                
                if is_admin:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🗑️ APAGAR HISTÓRICO DA GALERIA (Modo Teste)"):
                        if os.path.exists(ARQUIVO_GALERIA):
                            os.remove(ARQUIVO_GALERIA)
                        st.success("💥 Histórico de testes apagado com sucesso!")
                        st.rerun()
            else:
                st.info("Nenhum registro encontrado na galeria ainda.")
        else:
            st.info("A galeria de honra está limpa. Os campeões aparecerão aqui assim que fechar o primeiro torneio!")

# === TELA 2: ANDAMENTO / ENCERRAMENTO ===
else:
    st.markdown(f"### 🏟️ {st.session_state.nome_torneio}")
    
    # --- ENCERRAMENTO COM ÊNFASE NOS 4 MELHORES ---
    if st.session_state.campeao:
        st.markdown("<h2 style='text-align: center; color: #d4af37 !important;'>✨ CERIMÔNIA DE PREMIAÇÃO FINAL ✨</h2>", unsafe_allow_html=True)
        
        rei_das_flores = "Ninguém"
        max_flores = 0
        if st.session_state.classificacao is not None:
            rei_das_flores = st.session_state.classificacao.sort_values(by='Flores', ascending=False).index[0]
            max_flores = int(st.session_state.classificacao.loc[rei_das_flores, 'Flores'])
            
        if not st.session_state.get("salvo_na_galeria", False):
            salvar_na_galeria(
                st.session_state.nome_torneio,
                st.session_state.campeao,
                st.session_state.vice_campeao,
                st.session_state.terceiro_lugar,
                st.session_state.quarto_lugar,
                rei_das_flores,
                max_flores
            )
            st.session_state.salvo_na_galeria = True
            salvar_estado_no_disco()
        
        st.markdown(f"""
            <div class="box-campeao">
                <h1 style="margin:0; font-size:2.8rem; letter-spacing: 2px;">🥇 1º LUGAR - CAMPEÃO 🥇</h1>
                <h2 style="color:#111111 !important; margin:12px 0; font-size:2.2rem;">🌟 {st.session_state.campeao} 🌟</h2>
                <p style="color:#222222 !important; font-weight:bold; margin:0; font-size:1.1rem;">O padrão absoluto das mesas de truco!</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
            <div class="podio-posicao podio-vice">
                <span style="font-size:1.4rem;">🥈 2º LUGAR (VICE-CAMPEÃO): {st.session_state.vice_campeao}</span>
            </div>
            <div class="podio-posicao podio-terceiro">
                <span style="font-size:1.3rem;">🥉 3º LUGAR (MEDALHA DE BRONZE): {st.session_state.terceiro_lugar}</span>
            </div>
            <div class="podio-posicao podio-quarto">
                <span style="font-size:1.2rem;">🎖️ 4º LUGAR: {st.session_state.quarto_lugar}</span>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
            <div class="box-flores">
                <h2 style="margin:0; color:#ff4b4b; font-size:1.6rem; letter-spacing:1px;">🌸 MAIOR CANTADOR DE FLORES 🌸</h2>
                <h3 style="margin:8px 0; font-size:1.5rem;"><b>{rei_das_flores}</b></h3>
                <p style="margin:0; font-style:italic;">Floriu o galpão inteiro cantando um total de <b>{max_flores} flores</b>!</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📊 Tabela Estatística de Fechamento")
        st.dataframe(st.session_state.classificacao.sort_values(by=['Vitorias', 'Sets_Ganhos', 'Saldo_Tentos'], ascending=False), use_container_width=True)
        
        if is_admin and st.button("🏁 Voltar para o Início / Novo Torneio"):
            if os.path.exists(ARQUIVO_BACKUP): os.remove(ARQUIVO_BACKUP)
            
            jogadores_salvos = list(st.session_state.jogadores)
            st.session_state.clear()
            st.session_state.jogadores = jogadores_salvos
            st.rerun()

    # --- FLUXO DO MATA-MATA ---
    elif st.session_state.em_matamata:
        st.markdown(f"#### ⚡ Fase: {st.session_state.fase_matamata}")
        
        if st.session_state.hora_inicio_rodada:
            tempo_limite = st.session_state.hora_inicio_rodada + timedelta(minutes=45)
            tempo_atual = datetime.now()
            if tempo_atual < tempo_limite:
                tempo_restante = tempo_limite - tempo_atual
                minutos, segundos = int(tempo_restante.total_seconds() // 60), int(tempo_restante.total_seconds() % 60)
                st.markdown(f'<div class="cronometro-box"><h3 style="margin:0; color:#d4af37 !important;">⏱️ TEMPO RESTANTE DO MATA-MATA: {minutos:02d}:{segundos:02d}</h3></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="cronometro-box"><h3 style="margin:0; color:#ff4b4b !important;">⏰ TEMPO ESGOTADO NESTA FASE!</h3></div>', unsafe_allow_html=True)

        if is_admin:
            with st.form(key=f"matamata_{st.session_state.fase_matamata}"):
                resultados_fase = []
                
                for idx, confronto in enumerate(st.session_state.confrontos_mm):
                    j1, j2 = confronto["j1"], confronto["j2"]
                    is_bronze = confronto.get("tipo") == "bronze"
                    is_final = (st.session_state.fase_matamata == "FINAIS" and not is_bronze)
                    
                    if is_final:
                        st.markdown(f"""
                            <div class="card-mesa-final">
                                <h2 style="margin:0; color:#d4af37 !important; letter-spacing:1px;">🔥 MESA DA GRANDE FINAL 🔥</h2>
                                <p style="margin:5px 0 0 0; color:#ffffff; font-weight:bold;">DISPUTA DO TÍTULO MÁXIMO DO TORNEIO</p>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        tipo = "👉 " if not is_bronze else "🥉 [DISPUTA DE 3º E 4º LUGAR] "
                        st.markdown(f'<div class="card-mesa"><b>Mesa {idx+1} - {tipo}</b></div>', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**{j1}**")
                        s1 = st.number_input("Sets:", min_value=0, max_value=2, step=1, key=f"mm_s1_{idx}")
                        t1 = st.number_input("Tentos Pró:", min_value=0, max_value=72, step=1, key=f"t1_{idx}")
                        f1 = st.number_input("🌸 Flores:", min_value=0, max_value=20, step=1, key=f"f1_{idx}")
                    with col2:
                        st.markdown(f"**{j2}**")
                        s2 = st.number_input("Sets:", min_value=0, max_value=2, step=1, key=f"s2_{idx}")
                        t2 = st.number_input("Tentos Pró:", min_value=0, max_value=72, step=1, key=f"t2_{idx}")
                        f2 = st.number_input("🌸 Flores:", min_value=0, max_value=20, step=1, key=f"f2_{idx}")
                    
                    resultados_fase.append({"j1": j1, "j2": j2, "s1": s1, "s2": s2, "t1": t1, "t2": t2, "f1": f1, "f2": f2, "is_bronze": is_bronze})
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                if st.form_submit_button("💾 COMPUTAR RESULTADOS DA ETAPA"):
                    vencedores = []
                    perdedores = []
                    
                    for r in resultados_fase:
                        j1, j2, s1, s2, t1, t2, f1, f2 = r["j1"], r["j2"], r["s1"], r["s2"], r["t1"], r["t2"], r["f1"], r["f2"]
                        
                        st.session_state.classificacao.loc[j1, 'Vitorias'] += (1 if s1 > s2 else 0)
                        st.session_state.classificacao.loc[j1, 'Sets_Ganhos'] += s1
                        st.session_state.classificacao.loc[j1, 'Tentos_Pro'] += t1
                        st.session_state.classificacao.loc[j1, 'Tentos_Contra'] += t2
                        st.session_state.classificacao.loc[j1, 'Flores'] += f1
                        
                        st.session_state.classificacao.loc[j2, 'Vitorias'] += (1 if s2 > s1 else 0)
                        st.session_state.classificacao.loc[j2, 'Sets_Ganhos'] += s2
                        st.session_state.classificacao.loc[j2, 'Tentos_Pro'] += t2
                        st.session_state.classificacao.loc[j2, 'Tentos_Contra'] += t1
                        st.session_state.classificacao.loc[j2, 'Flores'] += f2
                        
                        if r["is_bronze"]:
                            if s1 > s2:
                                st.session_state.terceiro_lugar = j1
                                st.session_state.quarto_lugar = j2
                            else:
                                st.session_state.terceiro_lugar = j2
                                st.session_state.quarto_lugar = j1
                        else:
                            if s1 > s2:
                                vencedores.append(j1)
                                perdedores.append(j2)
                            else:
                                vencedores.append(j2)
                                perdedores.append(j1)
                    
                    st.session_state.classificacao['Saldo_Tentos'] = st.session_state.classificacao['Tentos_Pro'] - st.session_state.classificacao['Tentos_Contra']
                    
                    if st.session_state.fase_matamata == "OITAVAS DE FINAL":
                        iniciar_fase_matamata(vencedores, "QUARTAS DE FINAL")
                    elif st.session_state.fase_matamata == "QUARTAS DE FINAL":
                        st.session_state.perdedores_semi = []
                        iniciar_fase_matamata(vencedores, "SEMIFINAL")
                    elif st.session_state.fase_matamata == "SEMIFINAL":
                        st.session_state.perdedores_semi = perdedores
                        st.session_state.fase_matamata = "FINAIS"
                        st.session_state.confrontos_mm = [
                            {"tipo": "normal", "j1": vencedores[0], "j2": vencedores[1]}, 
                            {"tipo": "bronze", "j1": perdedores[0], "j2": perdedores[1]}   
                        ]
                        st.session_state.hora_inicio_rodada = datetime.now()
                    elif st.session_state.fase_matamata == "FINAIS":
                        st.session_state.campeao = vencedores[0]
                        finalistas = [resultados_fase[0]["j1"], resultados_fase[0]["j2"]] if not resultados_fase[0]["is_bronze"] else [resultados_fase[1]["j1"], resultados_fase[1]["j2"]]
                        if st.session_state.campeao in finalistas:
                            finalistas.remove(st.session_state.campeao)
                        st.session_state.vice_campeao = finalistas[0]
                        
                    salvar_estado_no_disco()
                    st.rerun()
        else:
            for idx, confronto in enumerate(st.session_state.confrontos_mm):
                j1, j2 = confronto["j1"], confronto["j2"]
                is_bronze = confronto.get("tipo") == "bronze"
                tipo = "🏆 [GRANDE FINAL] " if (st.session_state.fase_matamata == "FINAIS" and not is_bronze) else ("🥉 [3º LUGAR] " if is_bronze else f"Mesa {idx+1}: ")
                st.markdown(f"""
                <div class="card-historico">
                    <b>{tipo}</b> {j1} ⚔️ {j2}
                </div>
                """, unsafe_allow_html=True)
            st.info("🔒 Resultados e chaves sendo atualizados pelo organizador do torneio.")

# === FLUXO DA CLASSIFICATÓRIA SUIÇA ===
else:
    abas = ["⚔️ Mesas da Rodada", "📊 Tabela Geral", "📜 Histórico de Jogos"]
    aba_selecionada = st.radio("Navegar para:", abas, horizontal=True)

    if aba_selecionada == "⚔️ Mesas da Rodada":
        if st.session_state.rodada_atual <= 5:
            st.markdown(f"#### 📅 Rodada {st.session_state.rodada_atual} de 5")
            
            if st.session_state.hora_inicio_rodada:
                tempo_limite = st.session_state.hora_inicio_rodada + timedelta(minutes=45)
                tempo_atual = datetime.now()
                if tempo_atual < tempo_limite:
                    tempo_restante = tempo_limite - tempo_atual
                    minutos, segundos = int(tempo_restante.total_seconds() // 60), int(tempo_restante.total_seconds() % 60)
                    st.markdown(f'<div class="cronometro-box"><h3 style="margin:0; color:#d4af37 !important;">⏱️ TEMPO RESTANTE: {minutos:02d}:{segundos:02d}</h3></div>', unsafe_allow_html=True)
            
            if is_admin:
                with st.form(key=f"rodada_{st.session_state.rodada_atual}"):
                    placares_coletados = []
                    for idx, (j1, j2) in enumerate(st.session_state.confrontos):
                        st.markdown(f'<div class="card-mesa"><b>Mesa {idx+1}</b></div>', unsafe_allow_html=True)
                        if j2 == "CHAPÉU (Folga)":
                            st.markdown(f"🤠 **{j1}** caiu no CHAPÉU (+1 Vit | +3 Sets | +72 Tentos)")
                            placares_coletados.append(None)
                        else:
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown(f"**{j1}**")
                                s1 = st.number_input("Sets:", min_value=0, max_value=2, step=1, key=f"s1_{idx}")
                                t1 = st.number_input("Tentos Pró:", min_value=0, max_value=72, step=1, key=f"t1_{idx}")
                                f1 = st.number_input("🌸 Flores:", min_value=0, max_value=20, step=1, key=f"f1_{idx}")
                            with col2:
                                st.markdown(f"**{j2}**")
                                s2 = st.number_input("Sets:", min_value=0, max_value=2, step=1, key=f"s2_{idx}")
                                t2 = st.number_input("Tentos Pró:", min_value=0, max_value=72, step=1, key=f"t2_{idx}")
                                f2 = st.number_input("🌸 Flores:", min_value=0, max_value=20, step=1, key=f"f2_{idx}")
                            placares_coletados.append((s1, s2, t1, t2, f1, f2))
                        st.markdown("<br>", unsafe_allow_html=True)
                    
                    if st.form_submit_button("💾 COMPUTAR RESULTADOS DA RODADA"):
                        dados_da_rodada_atual = []
                        for idx, c in enumerate(placares_coletados):
                            j1, j2 = st.session_state.confrontos[idx]
                            if j2 == "CHAPÉU (Folga)":
                                st.session_state.classificacao.loc[j1, ['Vitorias', 'Sets_Ganhos', 'Tentos_Pro']] += [1, 3, 72]
                                dados_da_rodada_atual.append({"Mesa": idx+1, "Jogador 1": j1, "Placar": "CHAPÉU", "Jogador 2": "Folga"})
                            else:
                                s1, s2, t1, t2, f1, f2 = c
                                st.session_state.classificacao.loc[j1, 'Vitorias'] += (1 if s1 > s2 else 0)
                                st.session_state.classificacao.loc[j1, 'Sets_Ganhos'] += s1
                                st.session_state.classificacao.loc[j1, 'Tentos_Pro'] += t1
                                st.session_state.classificacao.loc[j1, 'Tentos_Contra'] += t2
                                st.session_state.classificacao.loc[j1, 'Flores'] += f1
                                
                                st.session_state.classificacao.loc[j2, 'Vitorias'] += (1 if s2 > s1 else 0)
                                st.session_state.classificacao.loc[j2, 'Sets_Ganhos'] += s2
                                st.session_state.classificacao.loc[j2, 'Tentos_Pro'] += t2
                                st.session_state.classificacao.loc[j2, 'Tentos_Contra'] += t1
                                st.session_state.classificacao.loc[j2, 'Flores'] += f2
                                
                                dados_da_rodada_atual.append({
                                    "Mesa": idx+1, "Jogador 1": j1,
                                    "Placar": f"({s1}s | {t1}t | {f1}f)  ✖  ({s2}s | {t2}t | {f2}f)", "Jogador 2": j2
                                })
                        
                        st.session_state.historico_rodadas[f"Rodada {st.session_state.rodada_atual}"] = dados_da_rodada_atual
                        st.session_state.classificacao['Saldo_Tentos'] = st.session_state.classificacao['Tentos_Pro'] - st.session_state.classificacao['Tentos_Contra']
                        st.session_state.rodada_atual += 1
                        if st.session_state.rodada_atual <= 5:
                            gerar_rodada_web()
                        else:
                            salvar_estado_no_disco()
                        st.rerun()
            else:
                for idx, (j1, j2) in enumerate(st.session_state.confrontos):
                    st.markdown(f'<div class="card-mesa"><b>Mesa {idx+1}</b></div>', unsafe_allow_html=True)
                    if j2 == "CHAPÉU (Folga)":
                        st.markdown(f"🤠 **{j1}** está no CHAPÉU (Folga da Rodada)")
                    else:
                        st.markdown(f"🤠 **{j1}** ⚔️ 🤠 **{j2}**")
                    st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.success("🎉 Fase de grupos encerrada!")
            total_insc = len(st.session_state.jogadores)
            if total_insc > 16:
                qtd_classificados = 16
                nome_fase_inicial = "OITAVAS DE FINAL"
            elif total_insc >= 8:
                qtd_classificados = 8
                nome_fase_inicial = "QUARTAS DE FINAL"
            else:
                qtd_classificados = 4
                nome_fase_inicial = "SEMIFINAL"
            
            st.markdown(f"### ⚔️ Próxima Etapa: Mata-Mata ({qtd_classificados} melhores)")
            if is_admin:
                if st.button(f"🏆 INICIAR {nome_fase_inicial} ELIMINATÓRIA"):
                    df_venc = st.session_state.classificacao.sort_values(by=['Vitorias', 'Sets_Ganhos', 'Saldo_Tentos'], ascending=False)
                    lista_elite = list(df_venc.index[:qtd_classificados])
                    iniciar_fase_matamata(lista_elite, nome_fase_inicial)
                    st.rerun()
            else:
                st.info("Aguardando o administrador chavear as eliminatórias do Mata-Mata.")

    elif aba_selecionada == "📊 Tabela Geral":
        st.markdown("#### 📊 Classificação Geral ao Vivo")
        df_exibir = st.session_state.classificacao.sort_values(by=['Vitorias', 'Sets_Ganhos', 'Saldo_Tentos'], ascending=False)
        st.dataframe(df_exibir[['Vitorias', 'Sets_Ganhos', 'Saldo_Tentos', 'Flores']], use_container_width=True)

    elif aba_selecionada == "📜 Histórico de Jogos":
        st.markdown("#### 🔍 Auditoria de Rodadas Computadas")
        if not st.session_state.historico_rodadas:
            st.info("Nenhuma rodada finalizada ainda.")
        else:
            for nome_da_rodada in sorted(st.session_state.historico_rodadas.keys(), reverse=True):
                with st.expander(f"👁️ Verificar {nome_da_rodada}", expanded=True):
                    for jogo in st.session_state.historico_rodadas[nome_da_rodada]:
                        st.markdown(f"""
                        <div class="card-historico">
                            <b>Mesa {jogo['Mesa']}:</b><br>
                            🤠 {jogo['Jogador 1']} <span style='color:#d4af37;'>{jogo['Placar']}</span> {jogo['Jogador 2']}
                        </div>
                        """, unsafe_allow_html=True)

    if is_admin:
        st.markdown("---")
        if st.button("🚨 Reiniciar Todo o Torneio"):
            if os.path.exists(ARQUIVO_BACKUP): os.remove(ARQUIVO_BACKUP)
            st.session_state.clear()
            st.rerun()

st.markdown(f"""
    <div class="creditos">
        <hr style="border-color: #2c6b56;">
        💻 Criado e Desenvolvido por <b>{NOME_CRIADOR}</b><br>
        Todos os direitos reservados à {NOME_CRIADOR} © 2026
    </div>
""", unsafe_allow_html=True)
