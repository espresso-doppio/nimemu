import copy
import json
import random
import time
from collections import deque
from pathlib import Path
import streamlit as st
import themeutils
from load_css import load_css

load_css()


@st.cache_data
def load_themes() -> dict[str, list[tuple[str, str]]]:
    themes_dir = Path(__file__).parent / "themes"
    themes: dict[str, list[tuple[str, str]]] = {}
    for path in sorted(themes_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        themes[data["name"]] = [tuple(p) for p in data["pairs"]]
    return themes


if "configs" not in st.session_state:
    st.session_state.configs = True
    st.session_state.add_theme = False
    st.session_state.min_pairs = 4
    st.session_state.max_pairs = 24
    st.session_state.pair_lines = 4
    st.session_state.all_pairs = copy.deepcopy(load_themes())
    st.session_state.custom_deck = []
    st.session_state.current_custom = None
    st.session_state.txt_deck = ""


# ---- Setup ----
st.set_page_config(page_title="ニメム", page_icon="🎴", layout="centered")

st.title("ニメム", width="stretch", text_alignment="center")
st.caption("メモリーゲーム para aprendizado de japonês.", text_alignment="center")
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


def sample_pairs(theme: str, k: int) -> list[tuple[str, str]]:
    pairs = st.session_state.all_pairs[theme]
    return random.sample(pairs, k=min(k, len(pairs)))


def new_game(pairs: list[tuple[str, str]]) -> None:
    deck = [(p_id, label.upper()) for p_id, pair in enumerate(pairs) for label in pair]
    random.shuffle(deck)
    st.session_state.deck = deck
    st.session_state.size = len(pairs)
    st.session_state.columns = get_columns_size(st.session_state.size)
    st.session_state.pairs = pairs
    st.session_state.state = ["down"] * (st.session_state.size * 2)
    st.session_state.flipped = []
    st.session_state.moves = 0
    st.session_state.matched = 0
    st.session_state.found = deque()
    st.session_state.started_at = time.time()
    st.session_state.finished_at = None
    st.session_state.game_over = False


def handle_card_click(i: int) -> None:
    if st.session_state.game_over or st.session_state.state[i] != "down":
        return

    flipped = st.session_state.flipped

    if len(flipped) == 2:
        st.session_state.state[flipped[0]] = "down"
        st.session_state.state[flipped[1]] = "down"
        flipped.clear()

    st.session_state.state[i] = "up"
    flipped.append(i)

    if len(flipped) == 2:
        st.session_state.moves += 1
        a, b = flipped

        if st.session_state.deck[a][0] == st.session_state.deck[b][0]:  # Pair
            st.session_state.state[a] = "gone"
            st.session_state.state[b] = "gone"
            st.session_state.matched += 1
            st.session_state.found.appendleft(
                st.session_state.pairs[st.session_state.deck[a][0]]
            )
            flipped.clear()

            if st.session_state.matched == st.session_state.size:  # Win
                st.session_state.finished_at = time.time()
                st.session_state.game_over = True


@st.dialog("Upload de pares", position="right")
def upload_deck():
    uploaded_deck = st.file_uploader(
        "deck_uploader",
        max_upload_size=1,
        type="txt",
        width="stretch",
        label_visibility="collapsed",
    )

    if uploaded_deck is not None:
        if st.session_state.get("last_uploaded_id") != uploaded_deck.file_id:
            processed_uploaded_deck = themeutils.from_txt(uploaded_deck)

            if processed_uploaded_deck:
                st.toast("Pares importados com sucesso!")
                if st.session_state.current_custom:
                    del st.session_state.all_pairs[st.session_state.current_custom]
                st.session_state.current_custom = processed_uploaded_deck["name"]
                st.session_state.all_pairs.update(
                    {processed_uploaded_deck["name"]: processed_uploaded_deck["pairs"]}
                )
                st.session_state.last_uploaded_id = uploaded_deck.file_id
                st.rerun()
            else:
                st.warning("Por favor, envie um conjunto válido.")


def format_filename(deck_name: None | str) -> str:
    if deck_name:
        return deck_name.replace(" ", "_").lower()
    return "meus_pares"


def clean_custom_deck(deck: list[tuple[str, str]]) -> list[tuple[str, str]]:
    cleaned = [(a.strip(), b.strip()) for a, b in deck]
    return [pair for pair in cleaned if any(pair)]


def validate_custom_deck(deck: list[tuple[str, str]]) -> bool:
    if len(deck) >= st.session_state.min_pairs and all(all(pair) for pair in deck):
        return True
    st.warning(
        f"O conjunto precisa ter no mínimo {st.session_state.min_pairs} pares válidos."
    )
    return False


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
    _, col1, col2, _ = st.columns([1, 1.1, 1.1, 1], vertical_alignment="bottom")
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

        if st.button("Criar", type="primary"):
            deck = clean_custom_deck(st.session_state.custom_deck)
            if validate_custom_deck(deck):
                if st.session_state.current_custom:
                    del st.session_state.all_pairs[st.session_state.current_custom]
                deck_name = f"[{deck_title.strip() or 'Meus pares'}]"
                st.session_state.current_custom = deck_name
                st.session_state.all_pairs[deck_name] = deck
                st.session_state.txt_deck = themeutils.to_txt(
                    {"name": deck_name, "pairs": deck}
                )
                st.session_state.pair_lines = 4
                st.session_state.add_theme = False
                st.session_state.custom_deck = []
                st.rerun()

        if st.button("Voltar", type="secondary"):
            st.session_state.add_theme = False
            st.session_state.pair_lines = 4
            st.session_state.custom_deck = []
            st.rerun()

        st.stop()


# ---- Intro Screen ----
if "start" not in st.session_state:
    _, center, _ = st.columns([1, 3, 1])
    with center:
        col_theme, col_pairs = st.columns([2, 1])
        with col_theme:
            initial_theme = st.selectbox(
                label="Temas", options=sorted(st.session_state.all_pairs), on_change="rerun"
            )
        with col_pairs:
            initial_pairs = st.number_input(
                label="Pares",
                value=4,
                min_value=4,
                max_value=max(
                    4,
                    min(
                        len(st.session_state.all_pairs[initial_theme]),
                        st.session_state.max_pairs,
                    ),
                ),
                width=130,
            )

        _, center_button, _ = st.columns([1, 1.5, 1])
        with center_button:
            if st.button("Começar", type="primary", width=300):
                st.session_state.current_theme = initial_theme
                new_game(sample_pairs(initial_theme, initial_pairs))
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

            if st.button(
                "Carregar pares", icon=":material/upload:", type="secondary", width=300
            ):
                upload_deck()

else:
    # ---- Win Screen ----
    if st.session_state.game_over:
        duration = st.session_state.finished_at - st.session_state.started_at
        st.title("クリア！", text_alignment="center")
        a, b, c = st.columns(3)
        efficiency = duration / st.session_state.size
        a.metric("Tempo", f"{duration:.2f}s")
        b.metric("Jogadas", st.session_state.moves)
        c.metric("Eficiência", f"{efficiency:.2f}s/par")

        show_found_pairs()

        if st.button(":material/replay: Jogar novamente", type="primary"):
            new_game(
                sample_pairs(
                    st.session_state.current_theme, st.session_state.size
                )
            )
            st.rerun()
        st.stop()

    # ---- In-Game Controls ----
    ctrl_a, ctrl_b = st.columns(2)
    with ctrl_a:
        if st.button(":material/replay: Reiniciar", width="stretch", type="tertiary"):
            new_game(sample_pairs(st.session_state.current_theme, st.session_state.size))
            st.rerun()
    with ctrl_b:
        if st.button(
            ":material/settings: Configurar novo jogo",
            width="stretch",
            type="tertiary",
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

    with st.container(horizontal=True):
        c1, c2, c3 = st.columns(3, width="stretch")
        c1.metric("Pares", f"{st.session_state.matched} / {st.session_state.size}")
        c2.metric("Jogadas", st.session_state.moves)
        with c3:
            timer()

    # ---- Board ----
    cols = st.columns(st.session_state.columns)
    for i, (_, label) in enumerate(st.session_state.deck):
        s = st.session_state.state[i]
        text, disabled = (
            ("?", False) if s == "down" else (label if s == "up" else "✓", True)
        )
        with cols[i % st.session_state.columns]:
            with st.container(key=f"{s}_{i}"):
                st.button(
                    text,
                    key=f"card_{i}",
                    disabled=disabled,
                    use_container_width=True,
                    on_click=handle_card_click,
                    args=(i,),
                )

    # ---- Found Log ----
    st.divider()
    if st.session_state.found:
        st.subheader("Pares encontrados")
        show_found_pairs()
