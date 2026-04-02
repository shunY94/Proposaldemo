import streamlit as st
import pandas as pd

# --- 1. モックデータの設定 ---
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
# AIとマニュアル操作で共有する検索条件の器
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

# --- 3. AI解釈ロジック ---
def apply_ai_prompt(prompt):
    if not prompt: return
    # デモ用の簡易判定。実際はここでLLM APIを叩き、JSONでフィルタを受け取る
    if "渋谷" in prompt:
        st.session_state.filters["cities"] = ["渋谷区"]
        if "200坪" in prompt or "100人" in prompt:
            st.session_state.filters["emp_range"] = (80, 150)
        st.session_state.filters["hq_only"] = True
        st.toast("AI: 渋谷区・本社限定・100名前後の条件をセットしました！", icon="🧠")

# --- 4. UI全体構成 ---
st.set_page_config(page_title="AI Sales Copilot", layout="wide")

# --- サイドバー：詳細検索条件 ---
with st.sidebar:
    st.header("🔍 詳細検索条件")
    st.write("AIの提案をここで微調整できます")
    
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
    
    # ステータス設定（ラジオボタン）
    st.session_state.filters["tenant"] = st.radio(
        "テナント状況", ["指定しない", "既存テナントのみ", "既存テナント除外"], 
        index=["指定しない", "既存テナントのみ", "既存テナント除外"].index(st.session_state.filters["tenant"])
    )
    st.session_state.filters["card"] = st.radio(
        "名刺交換", ["指定しない", "名刺交換済みのみ", "名刺交換済みを除外"],
        index=["指定しない", "名刺交換済みのみ", "名刺交換済みを除外"].index(st.session_state.filters["card"])
    )
    st.session_state.filters["attack"] = st.radio(
        "アタックリスト", ["指定しない", "対象のみ", "対象除外"],
        index=["指定しない", "対象のみ", "対象除外"].index(st.session_state.filters["attack"])
    )

    st.divider()
    # 検索実行ボタン
    search_clicked = st.button("🚨 この条件で再検索", use_container_width=True, type="primary")

# --- メインエリア ---
st.title("🧠 AIターゲット・エージェント")

# 1. 自然言語入力セクション
with st.container(border=True):
    st.subheader("AIに指示を出す")
    col_input, col_btn = st.columns([8, 2])
    with col_input:
        prompt = st.text_input("プロンプト入力", placeholder="例：渋谷のオフィスで、200坪くらいの区画を埋めたいんだが...")
    with col_btn:
        st.write("") # スペース調整
        if st.button("条件を生成", use_container_width=True):
            apply_ai_prompt(prompt)
            st.rerun() # サイドバーの値を更新するために再描画

# 2. 結果表示セクション
st.subheader("📋 抽出ターゲットリスト")

# フィルタリング処理
df = get_mock_data()
f = st.session_state.filters

mask = (
    df["所在地"].isin(f["prefectures"]) &
    df["市区町村"].isin(f["cities"]) &
    (df["従業員数"] >= f["emp_range"][0]) &
    (df["従業員数"] <= f["emp_range"][1])
)
if f["hq_only"]: mask &= (df["本社"] == True)
if f["tenant"] == "既存テナントのみ": mask &= (df["テナント"] == "既存")
if f["card"] == "名刺交換済みのみ": mask &= (df["名刺交換"] == True)
if f["attack"] == "対象のみ": mask &= (df["アタックリスト"] == True)

result_df = df[mask]

# リストの表示
if not result_df.empty:
    st.dataframe(
        result_df, 
        use_container_width=True, 
        column_config={
            "企業名": st.column_config.TextColumn("企業名", width="medium"),
            "成長率": st.column_config.ProgressColumn("成長率", format="%d%%", min_value=0, max_value=200),
        }
    )
    st.caption(f"抽出件数: {len(result_df)}件")
else:
    st.warning("現在の条件に合致するデータがありません。サイドバーで条件を調整してください。")

# 3. 補足：現在の適用条件の可視化
with st.expander("現在適用中の検索パラメータ（デバッグ用）"):
    st.write(st.session_state.filters)
