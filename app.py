import streamlit as st
import pandas as pd
import time

# --- 1. モックデータ（データベースの代わり） ---
def get_mock_data():
    data = [
        {"企業名": "渋谷テックAI", "所在地": "東京都", "市区町村": "渋谷区", "本社": True, "従業員数": 85, "テナント": "既存", "名刺交換": True, "成長スコア": 92},
        {"企業名": "クリエイティブ・シブヤ", "所在地": "東京都", "市区町村": "渋谷区", "本社": True, "従業員数": 120, "テナント": "なし", "名刺交換": False, "成長スコア": 78},
        {"企業名": "丸の内フロンティア", "所在地": "東京都", "市区町村": "千代田区", "本社": True, "従業員数": 250, "テナント": "既存", "名刺交換": True, "成長スコア": 65},
        {"企業名": "港区グローバル・リンク", "所在地": "東京都", "市区町村": "港区", "本社": True, "従業員数": 180, "テナント": "なし", "名刺交換": False, "成長スコア": 88},
        {"企業名": "新宿デジタル本社", "所在地": "東京都", "市区町村": "新宿区", "本社": True, "従業員数": 220, "テナント": "既存", "名刺交換": True, "成長スコア": 72},
        {"企業名": "中央システム研究所", "所在地": "東京都", "市区町村": "中央区", "本社": True, "従業員数": 95, "テナント": "なし", "名刺交換": False, "成長スコア": 81},
        {"企業名": "横浜みなとAI", "所在地": "神奈川県", "市区町村": "横浜市", "本社": True, "従業員数": 150, "テナント": "既存", "名刺交換": True, "成長スコア": 85},
    ]
    return pd.DataFrame(data)

# --- 2. セッション状態（検索条件と検索実行フラグ）の管理 ---
if 'filters' not in st.session_state:
    st.session_state.filters = {
        "prefectures": [],
        "cities": [],
        "emp_range": (0, 1000),
        "hq_only": False,
        "tenant": "指定しない",
        "card": "指定しない"
    }

# 検索が一度でも実行されたかを管理するフラグ
if 'has_searched' not in st.session_state:
    st.session_state.has_searched = False

# --- 3. AIによる検索条件の自動生成ロジック ---
def apply_ai_prompt(prompt):
    if not prompt: return
    
    # 既存条件をリセット
    st.session_state.filters["prefectures"] = ["東京都"]
    
    # プロンプトの単語から簡易的に条件を推定（デモ用）
    if "渋谷" in prompt:
        st.session_state.filters["cities"] = ["渋谷区"]
    if "200坪" in prompt or "100人" in prompt:
        st.session_state.filters["emp_range"] = (80, 160)
    if "本社" in prompt or "埋めたい" in prompt:
        st.session_state.filters["hq_only"] = True
    
    # AIが条件をセットしたら、自動的に検索を実行状態にする
    st.session_state.has_searched = True
    st.toast("AI: 最適な検索パラメータをセットしました", icon="🧠")

# --- 4. メイン画面のUI構成 ---
st.set_page_config(page_title="Sales AI Copilot", layout="wide")
st.title("🎯 AIターゲット・エージェント")

# AIプロンプト入力（Clay風）
with st.container(border=True):
    st.subheader("🪄 AIに要望を伝える")
    col_input, col_btn = st.columns([8, 2])
    with col_input:
        user_prompt = st.text_input(
            "検索条件の生成", 
            placeholder="例：渋谷のオフィスで、100人規模の本社ビルを探している...",
            label_visibility="collapsed"
        )
    with col_btn:
        if st.button("条件を生成", use_container_width=True, type="secondary"):
            apply_ai_prompt(user_prompt)
            st.rerun()

# --- 5. サイドバー：詳細検索条件の管理 ---
with st.sidebar:
    st.header("🔍 詳細検索条件")
    st.write("AIが提案した条件をここで微調整してください。")
    
    # 各種入力項目（セッション状態を直接反映・更新）
    st.session_state.filters["hq_only"] = st.checkbox(
        "本社に限定", value=st.session_state.filters["hq_only"]
    )
    st.session_state.filters["prefectures"] = st.multiselect(
        "都道府県", ["東京都", "神奈川県", "千葉県", "埼玉県"], 
        default=st.session_state.filters["prefectures"]
    )
    st.session_state.filters["cities"] = st.multiselect(
        "市区町村", ["千代田区", "中央区", "港区", "新宿区", "渋谷区", "品川区", "横浜市"],
        default=st.session_state.filters["cities"]
    )
    st.session_state.filters["emp_range"] = st.slider(
        "従業員数 (人)", 0, 1000, st.session_state.filters["emp_range"]
    )
    
    st.divider()
    st.session_state.filters["tenant"] = st.radio(
        "テナント状況", ["指定しない", "既存テナントのみ", "既存テナント除外"], 
        index=["指定しない", "既存テナントのみ", "既存テナント除外"].index(st.session_state.filters["tenant"])
    )
    st.session_state.filters["card"] = st.radio(
        "名刺交換状況", ["指定しない", "名刺済みのみ", "名刺済みを除外"],
        index=["指定しない", "名刺済みのみ", "名刺済みを除外"].index(st.session_state.filters["card"])
    )

    st.divider()
    
    # 🚨 ここが肝：更新ボタン
    if st.button("🚨 この条件で再検索", use_container_width=True, type="primary"):
        st.session_state.has_searched = True
        st.rerun()

# --- 6. 検索結果の表示ロジック ---
st.subheader("📋 抽出ターゲットリスト")

if st.session_state.has_searched:
    with st.spinner('データベースを照合中...'):
        time.sleep(0.5) # 処理感を演出
        
        df = get_mock_data()
        f = st.session_state.filters

        # フィルタリング適用
        mask = pd.Series([True] * len(df))
        if f["prefectures"]: mask &= df["所在地"].isin(f["prefectures"])
        if f["cities"]: mask &= df["市区町村"].isin(f["cities"])
        mask &= (df["従業員数"] >= f["emp_range"][0]) & (df["従業員数"] <= f["emp_range"][1])
        if f["hq_only"]: mask &= (df["本社"] == True)
        if f["tenant"] == "既存テナントのみ": mask &= (df["テナント"] == "既存")
        if f["card"] == "名刺済みのみ": mask &= (df["名刺交換"] == True)

        result_df = df[mask]

        if not result_df.empty:
            st.success(f"{len(result_df)} 件の企業がヒットしました。")
            st.dataframe(
                result_df, 
                use_container_width=True,
                column_config={
                    "成長スコア": st.column_config.ProgressColumn("成長スコア", min_value=0, max_value=100, format="%d")
                }
            )
        else:
            st.warning("条件に一致する企業が見つかりませんでした。条件を広げてください。")
else:
    # 検索前の初期状態
    st.info("AIにプロンプトを入力するか、左側の詳細条件を設定して検索を開始してください。")
