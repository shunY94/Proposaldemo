import streamlit as st
import pandas as pd
import time

# --- 1. モックデータ ---
def get_mock_data():
    data = [
        {"企業名": "渋谷テックAI", "所在地": "東京都", "市区町村": "渋谷区", "本社": True, "従業員数": 85, "テナント": "既存", "名刺交換": True, "成長スコア": 92},
        {"企業名": "クリエイティブ・シブヤ", "所在地": "東京都", "市区町村": "渋谷区", "本社": True, "従業員数": 120, "テナント": "なし", "名刺交換": False, "成長スコア": 78},
        {"企業名": "丸の内フロンティア", "所在地": "東京都", "市区町村": "千代田区", "本社": True, "従業員数": 250, "テナント": "既存", "名刺交換": True, "成長スコア": 65},
        {"企業名": "港区グローバル・リンク", "所在地": "東京都", "市区町村": "港区", "本社": True, "従業員数": 180, "テナント": "なし", "名刺交換": False, "成長スコア": 88},
        {"企業名": "新宿デジタル本社", "所在地": "東京都", "市区町村": "新宿区", "本社": True, "従業員数": 220, "テナント": "既存", "名刺交換": True, "成長スコア": 72},
    ]
    return pd.DataFrame(data)

# --- 2. セッション状態の初期化 ---
if 'filters' not in st.session_state:
    st.session_state.filters = {
        "prefectures": [],
        "cities": [],
        "emp_range": (0, 1000),
        "hq_only": False,
        "tenant": "指定しない",
        "card": "指定しない" # 初期値を合わせる
    }

if 'has_searched' not in st.session_state:
    st.session_state.has_searched = False

# --- 3. AIによる検索条件の自動生成ロジック ---
def apply_ai_prompt(prompt):
    if not prompt: return
    
    # 条件リセット
    st.session_state.filters["prefectures"] = ["東京都"]
    
    if "渋谷" in prompt:
        st.session_state.filters["cities"] = ["渋谷区"]
    if "200坪" in prompt or "100人" in prompt:
        st.session_state.filters["emp_range"] = (80, 160)
    if "本社" in prompt:
        st.session_state.filters["hq_only"] = True
    
    # 🌟 ここが重要：AIがセットする言葉を選択肢と完全に一致させる
    if "名刺" in prompt:
        st.session_state.filters["card"] = "名刺交換済みのみ"
    
    st.session_state.has_searched = True
    st.toast("AI: 条件をセットしました", icon="🧠")

# --- 4. メイン画面のUI ---
st.set_page_config(page_title="Sales AI Copilot", layout="wide")
st.title("🎯 AIターゲット・エージェント")

with st.container(border=True):
    st.subheader("🪄 AIに要望を伝える")
    col_input, col_btn = st.columns([8, 2])
    with col_input:
        user_prompt = st.text_input("検索条件の生成", placeholder="例：渋谷のオフィスで、100人規模の本社ビルを探している...", label_visibility="collapsed")
    with col_btn:
        if st.button("条件を生成", use_container_width=True, type="secondary"):
            apply_ai_prompt(user_prompt)
            st.rerun()

# --- 5. サイドバー：詳細検索条件 ---
with st.sidebar:
    st.header("🔍 詳細検索条件")
    
    st.session_state.filters["hq_only"] = st.checkbox("本社に限定", value=st.session_state.filters["hq_only"])
    st.session_state.filters["prefectures"] = st.multiselect("都道府県", ["東京都", "神奈川県", "千葉県", "埼玉県"], default=st.session_state.filters["prefectures"])
    st.session_state.filters["cities"] = st.multiselect("市区町村", ["千代田区", "中央区", "港区", "新宿区", "渋谷区", "品川区", "横浜市"], default=st.session_state.filters["cities"])
    st.session_state.filters["emp_range"] = st.slider("従業員数 (人)", 0, 1000, st.session_state.filters["emp_range"])
    
    st.divider()

    # 🌟 エラー対策：安全にラジオボタンのインデックスを取得する関数
    def get_index(options, target):
        try:
            return options.index(target)
        except ValueError:
            return 0 # 見つからない場合は「指定しない」に戻す

    # ラジオボタンの選択肢（ここをAIロジックと完全に一致させる）
    tenant_options = ["指定しない", "既存テナントのみ", "既存テナント除外"]
    card_options = ["指定しない", "名刺交換済みのみ", "名刺交換済みを除外"]

    st.session_state.filters["tenant"] = st.radio(
        "テナント状況", tenant_options, 
        index=get_index(tenant_options, st.session_state.filters["tenant"])
    )
    
    st.session_state.filters["card"] = st.radio(
        "名刺交換状況", card_options,
        index=get_index(card_options, st.session_state.filters["card"])
    )

    st.divider()
    
    # 再検索ボタン
    if st.button("🚨 この条件で再検索", use_container_width=True, type="primary"):
        st.session_state.has_searched = True
        st.rerun()

# --- 6. 検索結果表示 ---
st.subheader("📋 抽出ターゲットリスト")

if st.session_state.has_searched:
    df = get_mock_data()
    f = st.session_state.filters

    mask = pd.Series([True] * len(df))
    if f["prefectures"]: mask &= df["所在地"].isin(f["prefectures"])
    if f["cities"]: mask &= df["市区町村"].isin(f["cities"])
    mask &= (df["従業員数"] >= f["emp_range"][0]) & (df["従業員数"] <= f["emp_range"][1])
    if f["hq_only"]: mask &= (df["本社"] == True)
    if f["tenant"] == "既存テナントのみ": mask &= (df["テナント"] == "既存")
    if f["card"] == "名刺交換済みのみ": mask &= (df["名刺交換"] == True)

    result_df = df[mask]
    st.success(f"{len(result_df)} 件ヒットしました。")
    st.dataframe(result_df, use_container_width=True)
else:
    st.info("AIに指示を出すか、条件を設定して検索を開始してください。")
