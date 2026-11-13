import streamlit as st

def load_css():
    st.markdown(
        """
        <style>
        /* ---- Toast ---- */
        div[data-testid="stToast"] {
            background-color: #7c5ea5 !important;
            color: white !important;
        }

        /* ---- Caption ---- */
                [data-testid="stCaptionContainer"] p, 
                .stCaptionContainer {
                    color: #7E7249 !important;
                }

        /* ---- Metric ---- */
        [data-testid="stMetric"],
        [data-testid="stMetric"] > div {
            text-align: center !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            width: 100% !important;
        }

        [data-testid="stMetricValue"] {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            width: 100% !important;
            font-size: 18px !important;
            font-weight: bold;
            color: #A4976D !important;
        }

        [data-testid="stMetricLabel"] p {
            font-size: 14px !important;
            text-align: center !important;
            color: #7E7249 !important;
        }

        /* ---- Cards ---- */
        div[data-testid="stColumn"],
        div[data-testid="column"] {
            container-type: inline-size;
        }

        div[class*="st-key-down_"] button,
        div[class*="st-key-up_"] button,
        div[class*="st-key-gone_"] button {
            aspect-ratio: 1 / 1;
            height: auto;
            border-radius: 14px;
            border: none !important;
            box-shadow: none;
            transition: all 0.18s ease;
            opacity: 1 !important;
        }

        div[class*="st-key-down_"] button p,
        div[class*="st-key-up_"] button p,
        div[class*="st-key-gone_"] button p {
            font-size: clamp(0.6rem, 12cqw, 2.2rem) !important;
            white-space: normal !important;
            line-height: 1.1 !important;
            overflow-wrap: anywhere !important;
            text-align: center !important;
            margin: 0 !important;
        }

        div[class*="st-key-down_"] button,
        div[class*="st-key-down_"] button:disabled {
            background-color: #7c5ea5 !important;
            color: #e9d5ff !important;
        }

        div[class*="st-key-down_"] button:hover:not(:disabled) {
            transform: scale(1.04);
            background-color: #634B85 !important;
        }

        div[class*="st-key-up_"] button,
        div[class*="st-key-up_"] button:disabled {
            background-color: #e7dfc7 !important;
            color: #512888 !important;
        }

        div[class*="st-key-gone_"] button,
        div[class*="st-key-gone_"] button:disabled {
            background-color: transparent !important;
            border: 1.5px dashed #b57edc !important;
            color: #b57edc !important;
            box-shadow: none !important;
        }

        div[class*="st-key-down_"] button:disabled,
        div[class*="st-key-up_"] button:disabled,
        div[class*="st-key-gone_"] button:disabled {
            cursor: default !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )