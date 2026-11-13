import json
import random
import time
import streamlit as st
import themeutils
from pathlib import Path
from collections import deque
from load_css import load_css

load_css()

@st.cache_data
def load_themes() -> dict[str, list[tuple[str, str]]]:
    THEMES_DIR = Path(__file__).parent / "themes"
    themes = {}
    for path in sorted(THEMES_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        themes[data["name"]] = [tuple(p) for p in data["pairs"]]
    return themes


if "configs" not in st.session_state:
    st.session_state.configs = True
    st.session_state.add_theme = False
    st.session_state.min_pairs = 4
    st.session_state.max_pairs = 24
    st.session_state.pair_lines = 4
    st.session_state.all_pairs = load_themes()
    st.session_state.custom_deck = []
    st.session_state.current_custom = None
    st.session_state.txt_deck = ""


@st.cache_data
def get_themes() -> list[str]:
    return sorted(list(st.session_state.all_pairs))


# ---- Setup ----
st.set_page_config(page_title="ニメム", page_icon="🎴", layout="centered")


st.title("メモリーゲーム", width="stretch", text_alignment="center")
st.caption("Jogo da Memória para aprendizado de nihongo.", text_alignment="center")
with st.bottom:
    st.caption("Versão para PC", text_alignment="center")


def get_columns_size(size: int) -> int:
    match size:
        case _ if size < 6:
            return 3
        case _ if size <= 10:
            return 4
        case _ if size <= 15:
            return 5
        case _:
            return 6


def show_found_pairs() -> None:
    for label1, label2 in st.session_state.found:
        st.markdown(f"- {label1.upper()}: **{label2}**", text_alignment="center")


def new_game(pairs: list[tuple[str, str]], theme_name: str) -> None:
    deck = [(p_id, label.upper()) for p_id, pair in enumerate(pairs) for label in pair]
    random.shuffle(deck)
    st.session_state.deck = deck
    st.session_state.size = len(pairs)
    st.session_state.columns = get_columns_size(st.session_state.size)
    st.session_state.pairs = pairs
    st.session_state.theme_name = theme_name
    st.session_state.state = ["down"] * st.session_state.size * 2
    st.session_state.flipped = []
    st.session_state.moves = 0
    st.session_state.matched = 0
    st.session_state.found = deque()
    st.session_state.started_at = time.time()
    st.session_state.finished_at = None
    st.session_state.game_over = False


@st.cache_data
def get_theme_max_pairs(theme: str, max_pairs: int = st.session_state.max_pairs) -> int:
    size = len(st.session_state.all_pairs[theme])
    return size if size <= max_pairs else max_pairs


def validate_custom_deck(deck: list[tuple[str, str]]) -> bool:

    if all(label != "" for pair in deck for label in pair):
        return True
    st.warning(
        f"O conjunto precisa ter no mínimo {st.session_state.min_pairs} pares válidos."
    )
    return False

@st.dialog("Upload de pares", position="right")
def upload_deck():
    uploaded_deck = st.file_uploader(
        "deck_uploader", max_upload_size=1, type="txt", width="stretch", label_visibility="collapsed"
    )

    if uploaded_deck is not None:
        if st.session_state.get("last_uploaded_id") != uploaded_deck.file_id:

            processed_uploaded_deck = themeutils.from_txt(uploaded_deck)

            if processed_uploaded_deck:
                time.sleep(0.5)
                st.toast("Pares importados com sucesso!")
                if st.session_state.current_custom:
                    del st.session_state.all_pairs[st.session_state.current_custom]
                st.session_state.current_custom = processed_uploaded_deck["name"]
                get_themes.clear()
                st.session_state.all_pairs.update(
                    {
                        processed_uploaded_deck["name"]: processed_uploaded_deck[
                            "pairs"
                        ]
                    }
                )
                st.session_state.last_uploaded_id = uploaded_deck.file_id
                st.rerun()
            else:
                st.warning('Por favor, envie um conjunto válido.')
         

def format_filename(deck_name: None | str) -> str:
    if deck_name:
        return deck_name.replace(" ", "_").lower()
    return "meus_pares"

# ---- Custom Pairs ----
if st.session_state.add_theme:

    st.html(  # '+'
        """
        <style>
        button[data-testid="stBaseButton-tertiary"] p,
        button[data-testid="stBaseButton-tertiary"] span {
            font-size: 30px !important;
            line-height: 1 !important;
            color: #7c5ea5 !important;
        }

        button[data-testid="stBaseButton-tertiary"]:hover {
        transform: scale(1.15) !important;
        background-color: transparent !important; 
    }

        </style>
        """
    )
    
    with st.container(horizontal_alignment="center"):
        st.markdown("**Título**", text_alignment="center")
        deck_title = st.text_input(
            label="title",
            value="Meus pares",
            label_visibility="collapsed",
            key="theme",
            width=300,
            max_chars=20,
        )
    st.divider()
    _, col1, col2, _ = st.columns(
        [1, 1.1, 1.1, 1], vertical_alignment="bottom"
    )  
    with col1:
        st.markdown("**Par (A)**", text_alignment="center")
    with col2:
        st.markdown("**Par (B)**", text_alignment="center")

    with st.container(horizontal_alignment="center"):
        for i in range(st.session_state.pair_lines):
            _, col1, col2, _ = st.columns([1, 1.1, 1.1, 1])

            with col1:
                pairA = st.text_input(
                    label=f"pair_{i + 1}",
                    key=f"t1_{i}",
                    label_visibility="collapsed",
                    max_chars=24,
                    width=200,
                )
            with col2:
                pairB = st.text_input(
                    label=f"pair_{i + 1}",
                    key=f"t2_{i}",
                    label_visibility="collapsed",
                    max_chars=24,
                    width=200,
                )

            try:
                st.session_state.custom_deck[i] = pairA, pairB
            except IndexError:
                st.session_state.custom_deck.append((pairA, pairB))

    with st.container(horizontal_alignment="center"):
        if st.button(":material/add:", type="tertiary"):
            if st.session_state.pair_lines < 24:
                st.session_state.pair_lines += 1
                st.rerun()
            else:
                st.warning("Limite máximo de pares atingido.")

        if st.button("Criar", type="primary") and validate_custom_deck(
            st.session_state.custom_deck
        ):
            if st.session_state.current_custom:
                del st.session_state.all_pairs[st.session_state.current_custom]
            get_themes.clear()
            deck_name = f"[{deck_title}]"
            st.session_state.current_custom = deck_name
            st.session_state.custom_deck = {deck_name: st.session_state.custom_deck}
            st.session_state.all_pairs.update(st.session_state.custom_deck)
            st.session_state.txt_deck = themeutils.to_txt(
                {"name": deck_name, "pairs": st.session_state.custom_deck[deck_name]}
            )
            st.session_state.add_theme = False
            st.session_state.custom_deck = []
            st.rerun()

        if st.button("Voltar", type="secondary"):
            st.session_state.add_theme = False
            st.session_state.pair_lines = 4
            st.session_state.custom_deck = []
            st.rerun()     

        st.stop()


# ---- Intro Screen----
if "start" not in st.session_state:
    _, center, _ = st.columns([1, 3, 1])
    with center:
        col_theme, col_pairs = st.columns([2, 1])
        with col_theme:
            initial_theme = st.selectbox(
                label="Temas", options=get_themes(), on_change="rerun"
            )
        with col_pairs:
            initial_pairs = st.number_input(
                label="Pares",
                value=4,
                min_value=4,
                max_value=get_theme_max_pairs(initial_theme),
                width=130,
            )

        _, center_button, _ = st.columns([1, 1.5, 1])
        with center_button:
            if st.button("Começar", type="primary", width=300):
                st.session_state.current_theme = initial_theme
                new_game(
                    random.sample(
                        st.session_state.all_pairs[initial_theme], k=initial_pairs
                    ),
                    st.session_state.current_theme,
                ) 
                st.session_state.start = True
                st.rerun()

            if st.button(
                "Adicionar pares",
                icon=":material/edit_square:",
                type="primary",
                width=300,
            ):
                st.session_state.add_theme = True
                st.rerun()

            st.download_button(
                "Baixar meus pares",
                icon=":material/download:",
                type="primary",
                width=300,
                disabled=not bool(st.session_state.txt_deck),
                data=st.session_state.txt_deck,
                file_name=f"{format_filename(st.session_state.current_custom)}.txt",
                mime="text/plain",
            )

            if st.button("Carregar pares", icon=":material/upload:", type="secondary", width=300):
                upload_deck()

else:
    # ---- Win Screen----
    with st.container(horizontal_alignment="center"):
        if st.session_state.game_over:
            duration = st.session_state.finished_at - st.session_state.started_at
            st.title("Vitória!", text_alignment="center")
            a, b, c = st.columns(3)
            efficiency = duration / st.session_state.size
            a.metric("Tempo", f"{duration:.2f}s")
            b.metric("Jogadas", st.session_state.moves)
            c.metric("Eficiência", f"{efficiency:.2f}s/par")

            show_found_pairs()

            if st.button(f":material/replay: Jogar novamente", type="primary"):
                new_game(
                    random.sample(
                        st.session_state.all_pairs[st.session_state.current_theme],
                        k=st.session_state.size,
                    ),
                    st.session_state.current_theme,
                )
                st.rerun()
            st.stop()

    # ---- In-Game Controls ----
    ctrl_a, ctrl_b = st.columns(2)
    with ctrl_a:
        if st.button(":material/replay: Reiniciar", width="stretch", type="tertiary"):
            new_game(
                random.sample(
                    st.session_state.all_pairs[st.session_state.current_theme],
                    k=st.session_state.size,
                ),
                st.session_state.current_theme,
            )
            st.rerun()
    with ctrl_b:
        if st.button(
            ":material/settings: Configurar novo jogo", width="stretch", type="tertiary"
        ):
            del st.session_state.start
            st.rerun()

    # ---- Status Bar ----
    @st.fragment(run_every=1.0)
    def timer():
        if st.session_state.started_at is None:
            st.metric("Tempo", "—")
            return
        end = st.session_state.finished_at or time.time()
        st.metric("Tempo", f"{int(end - st.session_state.started_at)}s")

    with st.container(
        horizontal=True,
    ):
        c1, c2, c3 = st.columns(3, width="stretch")
        c1.metric("Pares", f"{st.session_state.matched} / {st.session_state.size}")
        c2.metric("Jogadas", st.session_state.moves)
        with c3:
            timer()

    # ---- Board ----
    clicked: int | None = None
    cols = st.columns(st.session_state.columns)
    for i, (_, label) in enumerate(st.session_state.deck):
        s = st.session_state.state[i]
        text, disabled = (
            ("?", False) if s == "down" else (label if s == "up" else "✓", True)
        )
        with cols[i % st.session_state.columns]:
            with st.container(key=f"{s}_{i}"):
                if st.button(
                    text,
                    key=f"card_{i}",
                    disabled=disabled,
                    use_container_width=True,
                ):
                    clicked = i

    # ---- Click Handling ----
    if clicked is not None:
        if len(st.session_state.flipped) == 2:
            a, b = st.session_state.flipped
            st.session_state.state[a] = st.session_state.state[b] = "down"
            st.session_state.flipped = []
        st.session_state.state[clicked] = "up"
        st.session_state.flipped.append(clicked)
        if len(st.session_state.flipped) == 2:
            st.session_state.moves += 1
        st.rerun()

    # ---- Resolve ----
    if len(st.session_state.flipped) == 2:
        a, b = st.session_state.flipped
        if st.session_state.deck[a][0] == st.session_state.deck[b][0]:  # Pair
            st.session_state.state[a] = st.session_state.state[b] = "gone"
            st.session_state.matched += 1
            st.session_state.found.appendleft(
                st.session_state.pairs[st.session_state.deck[a][0]]
            )
            st.session_state.flipped = []
            if st.session_state.matched == st.session_state.size:  # Win condition
                st.session_state.game_over = True
                st.session_state.finished_at = time.time()

            st.rerun()

    # ---- Found Log ----
    st.divider()
    if st.session_state.found:
        st.subheader(f"Pares encontrados")
        show_found_pairs()
