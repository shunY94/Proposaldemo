import streamlit as st
import pandas as pd

# --- 1. モックデータの拡張 ---
def get_mock_data():
    data = [
        {"企業名": "テック渋谷", "所在地": "東京都", "市区町村": "渋谷区", "本社": True, "従業員数": 150, "テナント": "既存", "名刺交換": True, "アタックリスト": True},
        {"企業名": "千代田エナジー", "所在地": "東京都", "市区町村": "千代田区", "本社": True, "従業員数": 250, "テナント": "なし", "名刺交換": False, "アタックリスト": False},
        {"企業名": "港区トレード", "所在地": "東京都", "市区町村": "港区", "本社": True, "従業員数": 120, "テナント": "既存", "名刺交換": True, "アタックリスト": False},
        {"企業名": "新宿フロント", "所在地": "東京都", "市区町村": "新宿区", "本社": False, "従業員数": 280, "テナント": "なし", "名刺交換": False, "アタックリスト": True},
        {"企業名": "中央システム", "所在地": "東京都", "市区町村": "中央区", "本社": True, "従業員数": 180, "テナント": "既存", "名刺交換": False, "アタックリスト": False},
        {"企業名": "横浜商事", "所在地": "神奈川県", "市区町村": "横浜市", "本社": True, "従業員数": 200, "テナント": "なし", "名刺交換": True, "アタックリスト": True},
    ]
    return pd.DataFrame(data)

# --- 2. セッション状態の初期化 ---
if 'filters' not in st.session_state:
    st.session_state.filters = {
        "prefectures": ["東京都"],
        "cities": ["千代田区", "中央区", "港区", "新宿区", "渋谷区"],
        "emp_range": (100, 300),
        "hq_only": True,
        "tenant": "指定しない",
        "card": "指定しない",
        "attack": "指定しない"
    }

# --- 3. AI解釈ロジック（簡易版） ---
def ai_interpret(prompt):
    # 本来はLLMで解析しますが、デモ用に特定のワードでセッション状態を書き換えます
    if "渋谷" in prompt and "200坪" in prompt:
        st.session_state.filters["cities"] = ["渋谷区"]
        st.session_state.filters["emp_range"] = (60, 150) # 200坪想定の規模
        st.session_state.filters["hq_only"] = True
        return "✅ 渋谷区、本社限定、従業員数60-150名の条件をセットしました。"
    return "⚠️ 汎用的な条件を維持します。"

# --- 4. UI 構築 ---
st.set_page_config(layout="wide")
st.title("🏢 不動産アタックリスト・エージェント")

# プロンプト入力エリア
with st.container():
    query = st.text_input("AIに条件を指示（例：渋谷で200坪くらいの区画を埋めたい）")
    if st.button("AIで条件設定"):
        msg = ai_interpret(query)
        st.info(msg)

st.divider()

# --- 5. 詳細検索パネル (添付画像のUI再現) ---
with st.expander("🔍 詳細検索条件を確認・変更する", expanded=True):
    # 上段：都道府県、従業員数など
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        st.session_state.filters["prefectures"] = st.multiselect(
            "都道府県", ["東京都", "神奈川県", "千葉県", "埼玉県"], 
            default=st.session_state.filters["prefectures"]
        )
    with col2:
        st.session_state.filters["emp_range"] = st.slider(
            "従業員数 (人)", 0, 1000, st.session_state.filters["emp_range"]
        )
    with col3:
        st.write("拠点住所オプション")
        st.session_state.filters["hq_only"] = st.checkbox(
            "本社に限定", value=st.session_state.filters["hq_only"]
        )

    # 中段：市区町村（マルチセレクト）
    st.session_state.filters["cities"] = st.multiselect(
        "市区町村", ["千代田区", "中央区", "港区", "新宿区", "渋谷区", "品川区", "横浜市"],
        default=st.session_state.filters["cities"]
    )

    # 下段：ラジオボタン系
    r_col1, r_col2, r_col3 = st.columns(3)
    with r_col1:
        st.session_state.filters["tenant"] = st.radio(
            "テナント", ["指定しない", "既存テナントのみ", "既存テナント除外"], 
            index=["指定しない", "既存テナントのみ", "既存テナント除外"].index(st.session_state.filters["tenant"]),
            horizontal=True
        )
    with r_col2:
        st.session_state.filters["card"] = st.radio(
            "名刺交換", ["指定しない", "名刺交換済みのみ", "名刺交換済みを除外"],
            index=["指定しない", "名刺交換済みのみ", "名刺交換済みを除外"].index(st.session_state.filters["card"]),
            horizontal=True
        )
    with r_col3:
        st.session_state.filters["attack"] = st.radio(
            "アタックリスト条件", ["指定しない", "対象アタックリストのみ", "対象アタックリスト除外"],
            index=["指定しない", "対象アタックリストのみ", "対象アタックリスト除外"].index(st.session_state.filters["attack"]),
            horizontal=True
        )

# --- 6. フィルタリング実行 ---
df = get_mock_data()

# フィルタ適用
f = st.session_state.filters
mask = (
    df["所在地"].isin(f["prefectures"]) &
    df["市区町村"].isin(f["cities"]) &
    (df["従業員数"] >= f["emp_range"][0]) &
    (df["従業員数"] <= f["emp_range"][1])
)
if f["hq_only"]:
    mask &= (df["本社"] == True)

# ラジオボタンの条件適用（デモ用簡易ロジック）
if f["tenant"] == "既存テナントのみ": mask &= (df["テナント"] == "既存")
if f["card"] == "名刺交換済みのみ": mask &= (df["名刺交換"] == True)

result_df = df[mask]

# --- 7. 結果表示 ---
st.subheader(f"📊 抽出結果: {len(result_df)} 社")
st.dataframe(result_df, use_container_width=True)

if len(result_df) == 0:
    st.warning("条件に合致する企業がありません。条件を緩めてください。")
