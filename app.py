import streamlit as st
import pandas as pd
import time

# --- 1. モックデータの設定 (本来はAPIやDBから取得) ---
def get_external_data():
    """3rd Partyデータ（求人・財務）"""
    return pd.DataFrame({
        "企業名": ["テック未来", "グローバル商事", "スマート製造", "データラボ", "スピード配送"],
        "成長率": [125, 105, 140, 95, 110],  # 前年比%
        "求人増加": [15, 2, 25, -5, 8],      # 先月比件数
        "主要セクター": ["IT", "卸売", "製造", "IT", "物流"]
    })

def get_internal_data():
    """内部データ（名刺・商談履歴）"""
    return pd.DataFrame({
        "企業名": ["テック未来", "グローバル商事", "スマート製造", "新規化学"],
        "接点者": ["田中(営業1課)", "佐藤(部長)", "鈴木(営業2課)", "なし"],
        "最終商談日": ["2024-01-15", "2023-11-20", "2024-03-01", None],
        "ステータス": ["検討中", "停滞", "初回訪問", "未接点"]
    })

# --- 2. 画面構成 ---
st.set_page_config(page_title="Sales Intelligence Demo", layout="wide")
st.title("🚀 ターゲット企業リスト生成デモ")
st.markdown("MCP概念を模した、外部データと内部データの自動突合アプリケーションです。")

# サイドバー：検索条件
st.sidebar.header("検索フィルタ")
min_growth = st.sidebar.slider("最低成長率 (%)", 100, 150, 110)
job_increase = st.sidebar.number_input("求人増加数 (以上)", 0, 50, 5)

if st.button("ターゲットを抽出する"):
    with st.spinner('データを照合中...'):
        time.sleep(1.5)  # 処理をシミュレート
        
        # データのロード
        ext_df = get_external_data()
        int_df = get_internal_data()
        
        # 1. 外部データでフィルタリング
        filtered_ext = ext_df[(ext_df["成長率"] >= min_growth) & (ext_df["求人増加"] >= job_increase)]
        
        # 2. 内部データと結合 (Left Join)
        result = pd.merge(filtered_ext, int_df, on="企業名", how="left")
        
        # 3. AI的な優先度付け（簡易ロジック）
        def scoring(row):
            score = row["成長率"] * 0.5 + row["求人増加"] * 2
            if pd.isna(row["接点者"]): score -= 20  # 接点なしは優先度下げ
            return score
        
        result["スコア"] = result.apply(scoring, axis=1)
        result = result.sort_values("スコア", ascending=False)

    # --- 3. 結果表示 ---
    st.subheader("📊 抽出結果: AI推奨アプローチリスト")
    
    for _, row in result.iterrows():
        with st.expander(f"🏢 {row['企業名']} (スコア: {row['スコア']:.1f})"):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**【外部マーケット状況】**")
                st.write(f"📈 成長率: {row['成長率']}%")
                st.write(f"💼 求人増加: +{row['求人増加']}件")
            with col2:
                st.write("**【社内エンゲージメント】**")
                contact = row['接点者'] if pd.notna(row['接点者']) else "❌ 接点なし"
                st.write(f"👤 担当者: {contact}")
                st.write(f"🗓 最終接触: {row['最終商談日']}")
            
            # AIアドバイス
            if pd.notna(row['接点者']):
                st.info(f"💡 アドバイス: {row['接点者']}経由で、最新の求人動向に基づいた再提案が有効です。")
            else:
                st.warning("💡 アドバイス: 成長が著しいため、新規のアウトバウンド・コンタクトを推奨します。")

else:
    st.info("左側のサイドバーで条件を設定し、ボタンを押してください。")