import streamlit as st
import pandas as pd

# --- 1. モックデータの設定（多様なデータを用意） ---
def get_mock_data():
    data = [
        {"企業名": "渋谷AIテック", "所在地": "東京都", "市区町村": "渋谷区", "本社": True, "従業員数": 85, "テナント": "既存", "名刺交換": True, "成長率": 150},
        {"企業名": "クリエイティブ渋谷", "所在地": "東京都", "市区町村": "渋谷区", "本社": True, "従業員数": 120, "テナント": "なし", "名刺交換": False, "成長率": 130},
        {"企業名": "丸の内ビルディング", "所在地": "東京都", "市区町村": "千代田区", "本社": True, "従業員数": 250, "テナント": "既存", "名刺交換": True, "成長率": 110},
        {"企業名": "港区グローバル", "所在地": "東京都", "市区町村": "港区", "本社": True, "従業員数": 180, "テナント": "なし", "名刺交換": False, "成長率": 140},
        {"企業名": "新宿フロント", "所在地": "東京都", "市区町村": "新宿区", "本社": False, "従業員数": 220, "テナント": "既存", "名刺交換": True, "成長率": 105},
        {"企業名": "中央システム", "所在地": "東京都", "市区町村": "中央区", "本社": True, "従業員数": 95, "テナント": "なし", "名刺交換": False, "成長率": 120},
        {"企業名": "横浜みらい", "所在地": "神奈川県", "市区町村": "横浜市", "本社": True, "従業員数": 150, "テナント": "既存", "名刺交換": True, "成長率": 125},
    ]
    return pd.DataFrame(data)

# --- 2. セッション状態（検索条件）の初期化 ---
# デフォルトを「空（未選択）」に設定
if 'filters' not in st.session_state:
    st.session_state.filters = {
        "prefectures": [],
        "cities": [],
        "emp_range": (0, 1000),
        "hq_only": False,
        "tenant": "指定しない",
        "card": "指定しない",
        "attack": "指定しない"
    }
if 'search_triggered' not in st.session_state:
    st.session_state.search_triggered = False

# --- 3. AIによる条件自動生成ロジック ---
def apply_ai_prompt(prompt):
    if not prompt: return
    
    # --- ここで本来はLLM（OpenAI等）を呼び出しますが、デモ用に擬似解釈します ---
    # 初期化（一旦リセット）
    st.session_state.filters["prefectures"] = ["東京都"]
    
    if "渋谷" in prompt:
        st.session_state.filters["cities"] = ["渋谷区"]
    if "200坪" in prompt or "100人" in prompt:
        # 200坪 ≒ 60〜120名程度と解釈
        st.session_state.filters["emp_range"] = (60, 150)
    
    if "本社" in prompt or "埋めたい" in prompt:
        st.session_state.filters["hq_only"] = True
        
    st.session_state.search_triggered = True
    st.toast("AI: 要望に合わせて詳細条件を設定しました！", icon="🧠")

# --- 4. UI全体構成 ---
st.set_page_config(page_title="AI Sales Copilot", layout="wide")

# --- サイドバー：詳細検索条件（ユーザーによる変更用） ---
with st.sidebar:
    st.header("🔍 詳細検索条件")
    st.info("AIの提案結果がここに反映されます。手動での修正も可能です。")
    
    # 拠点設定
    st.subheader("基本情報")
    st.session_state.filters["hq_only"] = st.checkbox("本社に限定", value=st.session_state.filters["hq_only"])
    
    st.session_state.filters["prefectures"] = st.multiselect(
        "都道府県", ["東京都", "神奈川県", "千葉県", "埼玉県"], 
        default=st.session_state.filters["prefectures"]
    )
    st.session_state.filters["cities"] = st.multiselect(
        "市区町村", ["千代田区", "中央区", "港区", "新宿区", "渋谷区", "品川区", "横浜市"],
        default=st.session_state.filters["cities"]
    )
    
    # 従業員数
    st.session_state.filters["emp_range"] = st.slider(
        "従業員数 (人)", 0, 1000, st.session_state.filters["emp_range"]
    )
    
    st.divider()
    
    # ステータス設定
    st.session_state.filters["tenant"] = st.radio(
        "テナント状況", ["指定しない", "既存テナントのみ", "既存テナント除外"], 
        index=["指定しない", "既存テナントのみ", "既存テナント除外"].index(st.session_state.filters["tenant"])
    )
    st.session_state.filters["card"] = st.radio(
        "名刺交換", ["指定しない", "名刺交換済みのみ", "名刺交換済みを除外"],
        index=["指定しない", "名刺交換済みのみ", "名刺交換済みを除外"].index(st.session_state.filters["card"])
    )

    st.divider()
    # 手動再検索ボタン
    if st.button("🚨 この条件で再検索", use_container_width=True, type="primary"):
        st.session_state.search_triggered = True

# --- メインエリア ---
st.title("🚀 不動産アタックリスト・エージェント")

# 1. AIプロンプト入力セクション
with st.container(border=True):
    st.markdown("### 🪄 AIに条件作成を依頼する")
    col_input, col_btn = st.columns([8, 2])
    with col_input:
        user_prompt = st.text_input(
            "プロンプト入力", 
            placeholder="例：渋谷のオフィスで、200坪（100人程度）の区画を埋めたい",
            label_visibility="collapsed"
        )
    with col_btn:
        if st.button("条件を生成", use_container_width=True):
            apply_ai_prompt(user_prompt)
            st.rerun()

# 2. 結果表示セクション
st.subheader("📋 抽出ターゲットリスト")

if st.session_state.search_triggered:
    # フィルタリング処理の実行
    df = get_mock_data()
    f = st.session_state.filters

    # 厳格なフィルタリング（都道府県・市区町村が空ならヒットさせない）
    if not f["prefectures"] and not f["cities"]:
        st.info("条件が設定されていません。AIに指示を出すか、サイドバーで条件を選択してください。")
    else:
        mask = pd.Series([True] * len(df))
        if f["prefectures"]: mask &= df["所在地"].isin(f["prefectures"])
        if f["cities"]: mask &= df["市区町村"].isin(f["cities"])
        mask &= (df["従業員数"] >= f["emp_range"][0]) & (df["従業員数"] <= f["emp_range"][1])
        if f["hq_only"]: mask &= (df["本社"] == True)
        if f["tenant"] == "既存テナントのみ": mask &= (df["テナント"] == "既存")
        if f["card"] == "名刺交換済みのみ": mask &= (df["名刺交換"] == True)

        result_df = df[mask]

        if not result_df.empty:
            st.success(f"条件に合致する企業が {len(result_df)} 件見つかりました。")
            st.dataframe(
                result_df, 
                use_container_width=True,
                column_config={
                    "成長率": st.column_config.ProgressColumn("成長スコア", min_value=0, max_value=200, format="%d%%")
                }
            )
        else:
            st.warning("条件に合致する企業が見つかりませんでした。条件を広げてみてください。")
else:
    # 初期状態の表示
    st.write("👆 上記のボックスにやりたいことを入力するか、左側の「詳細検索条件」を設定してください。")
    
    # 参考：Clay風のプレースホルダー表示
    st.image("https://via.placeholder.com/1000x300.png?text=Waiting+for+Search+Criteria...", use_container_width=True)
