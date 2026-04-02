import streamlit as st
import pandas as pd
import time

# --- 1. 拡張モックデータ（場所や従業員数を追加） ---
def get_advanced_data():
    return pd.DataFrame({
        "企業名": ["テック未来", "グローバル商事", "スマート製造", "データラボ", "スピード配送", "渋谷クリエイティブ", "エビスAI"],
        "所在地": ["渋谷区", "中央区", "港区", "渋谷区", "品川区", "渋谷区", "渋谷区"],
        "従業員数": [85, 200, 45, 120, 30, 70, 55],
        "成長率": [140, 105, 110, 130, 95, 150, 120],
        "最終商談日": ["2024-01-15", "2023-11-20", None, "2024-03-01", None, None, "2024-02-10"],
        "接点者": ["田中", "佐藤", "なし", "鈴木", "なし", "なし", "高橋"]
    })

# --- 2. 簡易AIエンジン（自然言語を解析してフィルタを作る） ---
def ai_list_agent(query, data):
    query = query.lower()
    filtered_df = data.copy()
    
    reasons = [] # 抽出理由を格納

    # 「渋谷」というキーワードへの反応
    if "渋谷" in query:
        filtered_df = filtered_df[filtered_df["所在地"] == "渋谷区"]
        reasons.append("所在地が『渋谷区』の企業を抽出しました。")

    # 「200坪」＝ 従業員数 60〜100名程度と解釈するロジック
    if "200坪" in query or "広め" in query:
        # 1人3坪計算で、60人〜100人程度の規模をターゲットにする
        filtered_df = filtered_df[(filtered_df["従業員数"] >= 50) & (filtered_df["従業員数"] <= 100)]
        reasons.append("200坪（約60-100名規模）に最適なサイズの企業を特定しました。")
    
    # 「成長」などのワードがあれば成長率でソート
    if "良い" in query or "成長" in query or "おすすめ" in query:
        filtered_df = filtered_df.sort_values("成長率", ascending=False)
        reasons.append("成長率が高く、オフィス拡張の可能性が高い順に並べ替えました。")

    return filtered_df, reasons

# --- 3. UI構成 ---
st.set_page_config(page_title="AI Target Agent", layout="wide")
st.title("🧠 AIターゲット・エージェント")
st.markdown("### Clay風：自然言語でアタックリストを作成")

# ユーザー入力
user_input = st.text_area(
    "どのようなリストを作成しますか？", 
    placeholder="例：渋谷のオフィスで、200坪くらいの区画を埋めたいんだが、良さそうなリストを作成して",
    height=100
)

if st.button("リストを生成する"):
    if user_input:
        with st.spinner('AIが意図を解釈してデータを統合中...'):
            time.sleep(2) # 思考時間を演出
            
            all_data = get_advanced_data()
            result_df, thoughts = ai_list_agent(user_input, all_data)
            
            # AIの思考プロセスの表示
            st.success("リストの生成が完了しました！")
            with st.expander("AIの抽出ロジックを確認"):
                for t in thoughts:
                    st.write(f"✅ {t}")

            # 結果の表示
            if len(result_df) > 0:
                for _, row in result_df.iterrows():
                    with st.container():
                        st.markdown(f"### {row['企業名']}")
                        c1, c2, c3 = st.columns(3)
                        c1.metric("所在地", row["所在地"])
                        c2.metric("従業員数", f"{row['従業員数']}名")
                        c3.metric("成長率", f"{row['成長率']}%")
                        
                        # 社内接点状況
                        if row["接点者"] != "なし":
                            st.info(f"🔗 社内接点あり: {row['接点者']}（最終商談: {row['最終商談日']}）")
                        else:
                            st.warning("⚠️ 社内接点なし：新規アプローチが必要です")
                        st.divider()
            else:
                st.error("該当する企業が見つかりませんでした。条件を緩めてみてください。")
    else:
        st.warning("プロンプトを入力してください。")
