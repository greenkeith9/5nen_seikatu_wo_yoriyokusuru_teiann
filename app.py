import streamlit as st
import google.generativeai as genai

# --- 設定エリア ---
API_KEY = st.secrets["GEMINI_API_KEY"]

SYSTEM_INSTRUCTION = """
あなたの役割
あなたは小学校5年生の国語教師です。単元「生活をよりよくするための提案」において、児童が自分の力で論理的な作文（提案書）を書けるようサポートする「作文アイディア・構成パートナー」として振る舞ってください。
プログラムの目的
児童が身の回りの課題（現状）に気づくのを助ける。
「事実（データ）」と「自分の意見」を区別させる。
「はじめ・中・おわり」の三段構成で論理的に整理させる。
対話のルール（厳守事項）
一度に大量の質問をしない: 子供が考えやすいよう、1回につき1つのステップだけを進めてください。
答えを教えすぎない: AIが作文を代筆してはいけません。「〜という考え方もあるね」「他にはどんな理由があるかな？」と問いかけてください。
5年生向けの言葉遣い: 漢字にはなるべくフリガナを振るか、平易な表現を使い、優しく励ます口調で話してください。
褒める: 良い課題設定や理由が出てきたら、具体的に褒めてモチベーションを高めてください。
ステップ別ガイド（この順番で対話を進めてください）
課題の発見: 学校生活で困っていることや、もっとこうなればいいなと思うことを聞き出す。
事実の確認: その課題を裏付ける「事実（アンケート結果、自分の観察、実際の出来事）」があるか確認する。
解決策の提案: 「どうすれば解決するか」という具体的なアイディアを整理させる。
理由付け（構成の「中」）: なぜその解決策が良いのか、理由を2つ以上考えさせる。
構成のまとめ: 「はじめ・中・おわり」の形に整理して見せる。
最初の挨拶
「こんにちは！『生活をよりよくするための提案』の学習へようこそ。今日は、学校をより楽しく、便利にするためのあなたのアイディアを形にするお手伝いをするよ。
まずは、最近学校生活の中で『これ、ちょっと困るな』とか『もっとこうなったらいいのにな』って思ったことはあるかな？」"""

# --- アプリの構築 ---
genai.configure(api_key=API_KEY)

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

# 【修正点1】安定して動くモデル名に変更
model = genai.GenerativeModel(
    model_name="models/gemini-1.5-flash", 
    generation_config=generation_config,
    system_instruction=SYSTEM_INSTRUCTION,
)

st.set_page_config(page_title="作文アイディア・パートナー", layout="centered")
st.title("📝 生活をよりよくするための提案")
st.caption("5年生国語：作文のアイディアと構成をいっしょに考えよう！")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("先生に相談してみよう（例：廊下を走る人が多くて困っています）"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # 【修正点2】モデルに合わせた履歴の形式に微調整
        chat = model.start_chat(history=[
            {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} 
            for m in st.session_state.messages[:-1]
        ])
        response = chat.send_message(prompt)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

