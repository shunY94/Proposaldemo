import streamlit as st
import pandas as pd

# --- 1. モックデータ ---
def get_mock_data():
    data = [
        {"企業名": "渋谷テックAI", "所在地": "東京都", "市区町村": "渋谷区", "本社": True, "従業員数": 85, "テナント": "既存", "名刺交換": True},
        {"企業名": "クリエイティブ・シブヤ", "所在地": "東京都", "市区町村": "渋谷区", "本社": True, "従業員数": 120, "テナント": "なし", "名刺交換": False},
        {"企業名": "丸の内フロンティア", "所在地": "東京都", "市区町村": "千代田区", "本社": True, "従業員数": 250, "テナント": "既存", "名刺交換": True},
        {"企業名": "港区グローバル・リンク", "所在地": "東京都", "市区町村": "港区", "本社": True, "従業員数": 180, "テナント": "なし", "名刺交換": False},
        {"企業名": "新宿デジタル本社", "所在地": "東京都", "市区町村": "新宿区", "本社": True, "従業員数": 220, "テナント": "既存", "名刺交換": True},
        {"企業名": "中央システム研究所", "所在地": "東京都", "市区町村": "中央区", "本社": True, "従業員数": 95, "テナント": "なし", "名刺交換": False},
    ]
    return pd.DataFrame(data)

# --- 2. セッション状態の初期化 ---
# 「編集中の条件」と「検索実行時の確定条件」を分けるのがコツです
if 'edit_filters' not in st.session_state:
    st.session_state.edit_filters = {
        "prefectures": [],
        "cities": [],
        "emp_range": (0, 1000),
        "hq_only": False,
        "tenant": "指定しない",
        "card": "指定しない"
    }

if 'active_filters' not in st.session_state:
    st.session_state.active_filters = None # 最初は何も検索していない状態

# --- 3. AIによる条件生成ロジック ---
def apply_ai_prompt(prompt):
    if not prompt: return
    
    # AIがサイドバーの「編集中の条件」を書き換える
    st.session_state.edit_filters["prefectures"] = ["東京都"]
    if "渋谷" in prompt:
        st.session_state.edit_filters["cities"] = ["渋谷区"]
    if "200坪" in prompt or "100人" in prompt:
        st.session_state.edit_filters["emp_range"] = (80, 160)
    if "本社" in prompt:
        st.session_state.edit_filters["hq_only"] = True
    
    # AI生成時はそのまま検索を実行状態にする
    st.session_state.active_filters = st.session_state.edit_filters.copy()
    st.toast("AIが最適な条件をセットしました。左側の条件で微調整も可能です。", icon="🧠")

# --- 4. メイン画面のUI ---
st.set_page_config(page_title="AI Sales Copilot", layout="wide")
st.title("🎯 AIターゲット・エージェント")

# AI入力エリア
with st.container(border=True):
    st.subheader("🪄 AIに要望を伝えて企業を検索")
    col_input, col_btn = st.columns([8, 2])
    with col_input:
        user_prompt = st.text_input("例：渋谷で100人規模の本社を探して", placeholder="港区の300坪の区画に入る企業を教えて", label_visibility="collapsed")
    with col_btn:
        if st.button("条件を生成", use_container_width=True, type="primary"):
            apply_ai_prompt(user_prompt)
            st.rerun()

# --- 5. サイドバー：詳細検索条件 ---
with st.sidebar:
    st.header("🔍 詳細検索条件")
    st.write("ここで条件を自由に変更し、下のボタンで再検索してください。")
    
    # セッション状態と連動した入力フォーム
    st.session_state.edit_filters["hq_only"] = st.checkbox("本社に限定", value=st.session_state.edit_filters["hq_only"])
    st.session_state.edit_filters["prefectures"] = st.multiselect("都道府県", ["東京都", "神奈川県", "千葉県", "埼玉県"], default=st.session_state.edit_filters["prefectures"])
    st.session_state.edit_filters["cities"] = st.multiselect("市区町村", ["千代田区", "中央区", "港区", "新宿区", "渋谷区", "品川区"], default=st.session_state.edit_filters["cities"])
    st.session_state.edit_filters["emp_range"] = st.slider("従業員数 (人)", 0, 1000, st.session_state.edit_filters["emp_range"])
    
    st.divider()
    
    tenant_opts = ["指定しない", "既存テナントのみ", "既存テナント除外"]
    st.session_state.edit_filters["tenant"] = st.radio("テナント状況", tenant_opts, index=tenant_opts.index(st.session_state.edit_filters["tenant"]))
    
    card_opts = ["指定しない", "名刺交換済みのみ", "名刺交換済みを除外"]
    st.session_state.edit_filters["card"] = st.radio("名刺交換状況", card_opts, index=card_opts.index(st.session_state.edit_filters["card"]))

    st.divider()
    
    # 🚨 再検索ボタン：これを押すと「確定条件」が更新される
    if st.button("🚨 この条件で再検索を実行", use_container_width=True, type="primary"):
        st.session_state.active_filters = st.session_state.edit_filters.copy()
        st.rerun()

# --- 6. 検索結果表示 ---
st.subheader("📋 抽出ターゲットリスト")

if st.session_state.active_filters is not None:
    # 確定された条件（active_filters）でデータを抽出
    df = get_mock_data()
    f = st.session_state.active_filters

    mask = pd.Series([True] * len(df))
    if f["prefectures"]: mask &= df["所在地"].isin(f["prefectures"])
    if f["cities"]: mask &= df["市区町村"].isin(f["cities"])
    mask &= (df["従業員数"] >= f["emp_range"][0]) & (df["従業員数"] <= f["emp_range"][1])
    if f["hq_only"]: mask &= (df["本社"] == True)
    if f["tenant"] == "既存テナントのみ": mask &= (df["テナント"] == "既存")
    if f["card"] == "名刺交換済みのみ": mask &= (df["名刺交換"] == True)

    result_df = df[mask]
    
    if len(result_df) > 0:
        st.success(f"検索条件を適用しました： {len(result_df)} 件ヒット")
        st.dataframe(result_df, use_container_width=True)
    else:
        st.warning("条件に一致する企業が見つかりませんでした。サイドバーで条件を緩めて再検索してください。")
else:
    # 初期状態（何も検索していない時）
    st.info("AIにプロンプトを入力するか、左側の詳細条件を設定して「再検索を実行」を押してください。")
    st.image("https://via.placeholder.com/800x200.png?text=Waiting+for+Search+Command...", use_container_width=True)
