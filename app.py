import streamlit as st
import streamlit.components.v1 as components
import random
import re
import time
from gtts import gTTS
from io import BytesIO

# --- 0. 系統配置 ---
st.set_page_config(
    page_title="第 9 課 - 海 O riyar", 
    page_icon="🦞", 
    layout="centered"
)

# --- 1. 資料庫 (自然環境 第 9 課) ---
VOCAB_MAP = {
    "o": "是/主格", "maan": "什麼", "ko": "主格標記", "paro": "內容物",
    "no": "的", "riyar": "海", "ira": "有", "foting": "魚",
    "cekiw": "貝類", "ato": "和", "'orang": "龍蝦", "i": "在",
    "pina": "多少(數量)", "wa'ay": "腳", "mo^etep": "十",
    "masamaan": "怎麼樣(狀態)", "nanomen": "喝(受事)", "arenim": "鹹"
}

VOCABULARY = [
    {"amis": "riyar", "zh": "海/海洋", "emoji": "🌊", "root": "riyar", "root_zh": "海"},
    {"amis": "paro", "zh": "內容物/裡面", "emoji": "📦", "root": "paro", "root_zh": "裝"},
    {"amis": "cekiw", "zh": "貝類", "emoji": "🐚", "root": "cekiw", "root_zh": "貝"},
    {"amis": "'orang", "zh": "龍蝦/蝦", "emoji": "🦞", "root": "'orang", "root_zh": "蝦"},
    {"amis": "pina", "zh": "多少(問數量)", "emoji": "🔢", "root": "pina", "root_zh": "幾"},
    {"amis": "arenim", "zh": "鹹的", "emoji": "🧂", "root": "arenim", "root_zh": "鹹"},
    {"amis": "masamaan", "zh": "怎麼樣(狀態)", "emoji": "❓", "root": "samaan", "root_zh": "樣"},
]

SENTENCES = [
    {
        "amis": "O maan ko paro no riyar?", 
        "zh": "海裡面有什麼？(海的內容物是什麼？)", 
        "note": """
        <br><b>Paro</b>：內容物 (裝在裡面的東西)。
        <br>💡 <b>比較</b>：
        <br>🔹 <i>I labu</i>：強調「位置」在裡面。
        <br>🔹 <i>O paro</i>：強調「東西」是什麼。"""
    },
    {
        "amis": "Ira ko foting, cekiw ato 'orang i riyar.", 
        "zh": "海裡有魚、貝類和龍蝦。", 
        "note": """
        <br><b>ato</b>：和/與 (連接詞)。
        <br>用來連接名詞：A <i>ato</i> B <i>ato</i> C。
        <br><b>Ira</b>：有 (存在動詞)。"""
    },
    {
        "amis": "Pina ko wa'ay no 'orang?", 
        "zh": "龍蝦有幾隻腳？", 
        "note": """
        <br><b>Pina</b>：多少？(詢問數量專用)。
        <br><b>Wa'ay</b>：腳/腿。
        <br>這是數學課或自然課的標準問句。"""
    },
    {
        "amis": "Mo^etep ko wa'ay no 'orang.", 
        "zh": "龍蝦有十隻腳。", 
        "note": """
        <br><b>Mo^etep</b>：十 (基數詞)。
        <br>回答數量時，直接用數字取代 <i>Pina</i> 即可。"""
    },
    {
        "amis": "Masamaan nanomen ko nanom no riyar?", 
        "zh": "海水的味道喝起來怎麼樣？", 
        "note": """
        <br><b>Masamaan</b>：怎麼樣 (詢問狀態)。
        <br><b>Nanom-en</b>：被喝/去喝 (處置焦點)。
        <br>直譯：海水被喝的時候，狀態是如何？"""
    },
    {
        "amis": "Arenim a nanomen.", 
        "zh": "喝起來是鹹的。", 
        "note": """
        <br><b>Arenim</b>：鹹的。
        <br><b>結構</b>：<i>[形容詞] a [動詞]</i>。
        <br>表示做這個動作時的感覺。"""
    }
]

STORY_DATA = [
    {"amis": "O maan ko paro no riyar?", "zh": "海裡面有什麼？"},
    {"amis": "Ira ko foting, cekiw ato 'orang.", "zh": "有魚、貝類和龍蝦。"},
    {"amis": "Pina ko wa'ay no 'orang?", "zh": "龍蝦有幾隻腳？"},
    {"amis": "Mo^etep ko wa'ay no 'orang.", "zh": "龍蝦有十隻腳。"},
    {"amis": "Masamaan nanomen ko nanom?", "zh": "水喝起來怎麼樣？"},
    {"amis": "Arenim a nanomen.", "zh": "喝起來是鹹的。"}
]

# --- 2. 視覺系統 (CSS 注入 - 風格：清澈淺海 Crystal Shallow Water) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bubblegum+Sans&family=Noto+Sans+TC:wght@400;700&display=swap');

/* 全局背景：明亮的淺藍漸層 */
.stApp { 
    background: linear-gradient(180deg, #E1F5FE 0%, #B3E5FC 100%); 
    color: #0D47A1; /* 深海軍藍，高對比 */
    font-family: 'Noto Sans TC', sans-serif; 
}

/* Tab 樣式：清晰的膠囊 */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: #FFFFFF;
    padding: 8px;
    border-radius: 30px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}
.stTabs [data-baseweb="tab"] {
    height: 45px;
    border-radius: 20px;
    background-color: transparent;
    color: #455A64; /* 深灰色 */
    font-weight: 700;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    background-color: #0288D1 !important;
    color: #FFFFFF !important;
    box-shadow: 0 4px 10px rgba(2, 136, 209, 0.3);
}

/* 按鈕樣式：鮮豔的珊瑚橘 (保持對比) */
.stButton>button { 
    background: linear-gradient(45deg, #FF6F00, #EF6C00) !important; 
    color: white !important; 
    border: none !important; 
    border-radius: 12px !important; 
    font-size: 18px !important; 
    font-weight: 700 !important; 
    box-shadow: 0 4px 10px rgba(239, 108, 0, 0.3) !important;
    transition: all 0.2s ease !important;
}
.stButton>button:hover { 
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(239, 108, 0, 0.4) !important;
}

/* 測驗卡片：純白底色，深色文字 */
.quiz-card { 
    background: #FFFFFF; 
    border: 2px solid #81D4FA; 
    padding: 25px; 
    border-radius: 15px; 
    margin-bottom: 20px; 
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
    color: #01579B;
}
.quiz-tag { 
    background: #0288D1; 
    color: #FFF; 
    padding: 5px 12px; 
    border-radius: 8px; 
    font-weight: bold; 
    font-size: 14px; 
    display: inline-block;
    margin-bottom: 10px;
}

/* 翻譯區塊：淡黃色底，像沙灘，文字清晰 */
.zh-translation-block { 
    background: #FFFDE7; 
    border-left: 5px solid #FFD600;
    border-radius: 8px;
    padding: 20px; 
    color: #37474F; /* 深灰黑色 */
    font-size: 16px; 
    line-height: 1.8; 
    font-family: 'Noto Sans TC', monospace; 
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

# --- 3. 核心技術：沙盒渲染引擎 (修正文字顏色) ---
def get_html_card(item, type="word"):
    pt = "80px" if type == "full_amis_block" else "60px"
    mt = "-20px" if type == "full_amis_block" else "-10px" 

    style_block = f"""<style>
        @import url('https://fonts.googleapis.com/css2?family=Bubblegum+Sans&family=Noto+Sans+TC:wght@400;700&display=swap');
        /* 強制 body 文字顏色為深藍色，確保在任何背景下都清晰 */
        body {{ background-color: transparent; color: #0D47A1; font-family: 'Noto Sans TC', sans-serif; margin: 0; padding: 10px; padding-top: {pt}; overflow-x: hidden; }}
        
        /* 互動單字 */
        .interactive-word {{ 
            position: relative; 
            display: inline-block; 
            border-bottom: 2px dashed #0288D1;
            cursor: pointer; 
            margin: 0 4px; 
            color: #01579B; /* 深藍色 */
            transition: 0.3s; 
            font-size: 20px; 
            font-weight: 700; 
            font-family: 'Bubblegum Sans', sans-serif;
        }}
        .interactive-word:hover {{ color: #EF6C00; border-bottom-color: #EF6C00; transform: translateY(-2px); }}
        
        /* Tooltip */
        .interactive-word .tooltip-text {{ 
            visibility: hidden; 
            min-width: 80px; 
            background-color: #0277BD; 
            color: #FFF; 
            text-align: center; 
            border-radius: 8px; 
            padding: 8px; 
            position: absolute; 
            z-index: 100; 
            bottom: 140%; 
            left: 50%; 
            transform: translateX(-50%); 
            opacity: 0; 
            transition: opacity 0.3s; 
            font-size: 14px; 
            white-space: nowrap; 
            box-shadow: 0 4px 10px rgba(0,0,0,0.3); 
        }}
        .interactive-word:hover .tooltip-text {{ visibility: visible; opacity: 1; }}
        
        /* 播放按鈕 */
        .play-btn-inline {{ background: #0288D1; border: none; color: #FFF; border-radius: 50%; width: 28px; height: 28px; cursor: pointer; margin-left: 8px; display: inline-flex; align-items: center; justify-content: center; font-size: 14px; transition: 0.3s; vertical-align: middle; }}
        .play-btn-inline:hover {{ background: #01579B; transform: scale(1.1); }}
        
        /* 單字卡 - 白底深字 */
        .word-card-static {{ 
            background: #FFFFFF; 
            border-radius: 15px; 
            padding: 15px; 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            margin-top: {mt}; 
            height: 100px; 
            box-sizing: border-box; 
            box-shadow: 0 4px 8px rgba(0,0,0,0.05); 
            border: 1px solid #B3E5FC;
            border-left: 6px solid #0288D1;
        }}
        .wc-root-tag {{ font-size: 12px; background: #E1F5FE; color: #0277BD; padding: 3px 8px; border-radius: 4px; font-weight: bold; margin-right: 5px; }}
        .wc-amis {{ color: #0D47A1; font-size: 26px; font-weight: 700; margin: 2px 0; font-family: 'Bubblegum Sans', sans-serif; }}
        .wc-zh {{ color: #546E7A; font-size: 16px; font-weight: 500; }}
        
        .play-btn-large {{ background: #E1F5FE; border: 2px solid #0288D1; color: #0288D1; border-radius: 50%; width: 42px; height: 42px; cursor: pointer; font-size: 20px; transition: 0.2s; }}
        .play-btn-large:hover {{ background: #0288D1; color: #FFF; }}
        
        .amis-full-block {{ line-height: 2.4; font-size: 18px; margin-top: {mt}; text-align: left; padding: 0 5px; }}
        .sentence-row {{ margin-bottom: 12px; display: block; border-bottom: 1px dashed #B3E5FC; padding-bottom: 8px; }}
        .sentence-row:last-child {{ border-bottom: none; }}
    </style>
    <script>
        function speak(text) {{ window.speechSynthesis.cancel(); var msg = new SpeechSynthesisUtterance(); msg.text = text; msg.lang = 'id-ID'; msg.rate = 0.9; window.speechSynthesis.speak(msg); }}
    </script>"""

    header = f"<!DOCTYPE html><html><head>{style_block}</head><body>"
    body = ""
    
    if type == "word":
        v = item
        body = f"""<div class="word-card-static">
            <div>
                <div style="margin-bottom:5px;"><span class="wc-root-tag">ROOT: {v['root']}</span> <span style="font-size:12px; color:#90A4AE;">({v['root_zh']})</span></div>
                <div class="wc-amis">{v['emoji']} {v['amis']}</div>
                <div class="wc-zh">{v['zh']}</div>
            </div>
            <button class="play-btn-large" onclick="speak('{v['amis'].replace("'", "\\'")}')">🔊</button>
        </div>"""

    elif type == "full_amis_block": 
        all_sentences_html = []
        for sentence_data in item:
            s_amis = sentence_data['amis']
            words = s_amis.split()
            parts = []
            for w in words:
                clean_word = re.sub(r"[^\w']", "", w).lower()
                translation = VOCAB_MAP.get(clean_word, "")
                js_word = clean_word.replace("'", "\\'") 
                
                if translation:
                    chunk = f'<span class="interactive-word" onclick="speak(\'{js_word}\')">{w}<span class="tooltip-text">{translation}</span></span>'
                else:
                    chunk = f'<span class="interactive-word" onclick="speak(\'{js_word}\')">{w}</span>'
                parts.append(chunk)
            
            full_amis_js = s_amis.replace("'", "\\'")
            sentence_html = f"""
            <div class="sentence-row">
                {' '.join(parts)}
                <button class="play-btn-inline" onclick="speak('{full_amis_js}')" title="播放此句">🔊</button>
            </div>
            """
            all_sentences_html.append(sentence_html)
            
        body = f"""<div class="amis-full-block">{''.join(all_sentences_html)}</div>"""
    
    elif type == "sentence": 
        s = item
        words = s['amis'].split()
        parts = []
        for w in words:
            clean_word = re.sub(r"[^\w']", "", w).lower()
            translation = VOCAB_MAP.get(clean_word, "")
            js_word = clean_word.replace("'", "\\'") 
            
            if translation:
                chunk = f'<span class="interactive-word" onclick="speak(\'{js_word}\')">{w}<span class="tooltip-text">{translation}</span></span>'
            else:
                chunk = f'<span class="interactive-word" onclick="speak(\'{js_word}\')">{w}</span>'
            parts.append(chunk)
            
        full_js = s['amis'].replace("'", "\\'")
        body = f'<div style="font-size: 18px; line-height: 1.8; margin-top: {mt};">{" ".join(parts)}</div><button style="margin-top:10px; background:#0288D1; border:none; color:#FFF; padding:6px 15px; border-radius:8px; cursor:pointer; font-family:Bubblegum Sans; font-weight:700; box-shadow: 0 2px 4px rgba(0,0,0,0.2);" onclick="speak(`{full_js}`)">▶ PLAY AUDIO</button>'

    return header + body + "</body></html>"

# --- 4. 測驗生成引擎 ---
def generate_quiz():
    questions = []
    
    # 1. 聽音辨義
    q1 = random.choice(VOCABULARY)
    q1_opts = [q1['amis']] + [v['amis'] for v in random.sample([x for x in VOCABULARY if x != q1], 2)]
    random.shuffle(q1_opts)
    questions.append({"type": "listen", "tag": "🎧 聽音辨義", "text": "請聽語音，選擇正確的單字", "audio": q1['amis'], "correct": q1['amis'], "options": q1_opts})
    
    # 2. 中翻阿
    q2 = random.choice(VOCABULARY)
    q2_opts = [q2['amis']] + [v['amis'] for v in random.sample([x for x in VOCABULARY if x != q2], 2)]
    random.shuffle(q2_opts)
    questions.append({"type": "trans", "tag": "🧩 中翻阿", "text": f"請選擇「<span style='color:#EF6C00'>{q2['zh']}</span>」的阿美語", "correct": q2['amis'], "options": q2_opts})
    
    # 3. 數學題 (Pina)
    q3_data = {"text": "Pina ko wa'ay no 'orang? (龍蝦有幾隻腳？)", "ans": "Mo^etep", "note": "Mo^etep = 10"}
    questions.append({"type": "math", "tag": "🔢 數學時間", "text": f"{q3_data['text']}", "correct": "Mo^etep", "options": ["Mo^etep", "Cecay", "Tosa"], "note": q3_data['note']})

    # 4. 味覺題 (Masamaan)
    q4_data = {"text": "Masamaan nanomen ko nanom no riyar?", "ans": "Arenim", "note": "Arenim = 鹹的"}
    questions.append({"type": "taste", "tag": "👅 味覺測試", "text": f"海水的味道？<br>{q4_data['text']}", "correct": "Arenim", "options": ["Arenim", "Cici'", "Cilemin"], "note": q4_data['note']})

    # 5. 句型翻譯
    q6 = random.choice(STORY_DATA)
    q6_opts = [q6['amis']] + [s['amis'] for s in random.sample([x for x in STORY_DATA if x != q6], 2)]
    random.shuffle(q6_opts)
    questions.append({"type": "sent_trans", "tag": "📝 句型翻譯", "text": f"請選擇中文「<span style='color:#EF6C00'>{q6['zh']}</span>」對應的阿美語", "correct": q6['amis'], "options": q6_opts})

    random.shuffle(questions)
    return questions[:5]

def play_audio_backend(text):
    try:
        tts = gTTS(text=text, lang='id'); fp = BytesIO(); tts.write_to_fp(fp); st.audio(fp, format='audio/mp3')
    except: pass

# --- 5. UI 呈現層 (使用 components.html 隔離渲染標題) ---
# 主題：清澈淺海 (Crystal Shallow Water)
header_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Bubblegum+Sans&family=Noto+Sans+TC:wght@700&display=swap');
        body { margin: 0; padding: 0; background-color: transparent; font-family: 'Noto Sans TC', sans-serif; text-align: center; overflow: hidden; }
        .container {
            background: #FFFFFF;
            border-radius: 20px;
            padding: 20px;
            color: #0D47A1;
            border: 2px solid #81D4FA;
            position: relative;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        }
        /* 氣泡動畫 (淺藍色) */
        .bubble {
            position: absolute;
            background: rgba(129, 212, 250, 0.4);
            border-radius: 50%;
            animation: float 4s infinite ease-in-out;
        }
        .b1 { width: 40px; height: 40px; left: 10%; bottom: -20px; animation-duration: 5s; }
        .b2 { width: 20px; height: 20px; right: 20%; bottom: -10px; animation-duration: 3s; }
        .b3 { width: 60px; height: 60px; left: 80%; bottom: -30px; animation-duration: 6s; }
        
        @keyframes float {
            0% { transform: translateY(0); opacity: 0; }
            50% { opacity: 0.8; }
            100% { transform: translateY(-100px); opacity: 0; }
        }

        h1 {
            font-family: 'Bubblegum Sans', cursive;
            color: #0277BD;
            font-size: 48px;
            margin: 0 0 5px 0;
            letter-spacing: 2px;
        }
        .subtitle {
            color: #01579B;
            background: #E1F5FE;
            border-radius: 20px;
            padding: 5px 20px;
            display: inline-block;
            font-weight: bold;
            font-size: 16px;
        }
        .footer {
            margin-top: 10px;
            font-size: 12px;
            color: #90A4AE;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="bubble b1"></div><div class="bubble b2"></div><div class="bubble b3"></div>
        <h1>O riyar</h1>
        <div class="subtitle">第 9 課：海 (生物與味道)</div>
        <div class="footer">Theme: Crystal Shallow Water 🌊</div>
    </div>
</body>
</html>
"""

components.html(header_html, height=220)

tab1, tab2, tab3, tab4 = st.tabs([
    "🌊 互動課文", 
    "🦞 核心單字", 
    "🧬 句型解析", 
    "🤿 實戰測驗"
])

with tab1:
    st.markdown("### // 文章閱讀")
    st.caption("👆 點擊單字可聽發音並查看翻譯")
    
    # 使用純白背景容器，確保文字清晰
    st.markdown("""<div style="background:#FFFFFF; padding:15px; border-radius:15px; border: 2px solid #B3E5FC; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">""", unsafe_allow_html=True)
    components.html(get_html_card(STORY_DATA, type="full_amis_block"), height=400, scrolling=True)
    st.markdown("</div>", unsafe_allow_html=True)

    zh_content = "<br>".join([item['zh'] for item in STORY_DATA])
    st.markdown(f"""
    <div class="zh-translation-block">
        {zh_content}
    </div>
    """, unsafe_allow_html=True)

with tab2:
    st.markdown("### // 單字與詞根")
    col1, col2 = st.columns(2)
    for i, v in enumerate(VOCABULARY):
        with col1 if i % 2 == 0 else col2:
            components.html(get_html_card(v, type="word"), height=130)

with tab3:
    st.markdown("### // 語法結構分析")
    for s in SENTENCES:
        st.markdown("""<div style="background:#FFFFFF; padding:20px; border-radius: 15px; margin-bottom:20px; box-shadow: 0 5px 15px rgba(0,0,0,0.05); border: 1px solid #E1F5FE;">""", unsafe_allow_html=True)
        components.html(get_html_card(s, type="sentence"), height=160)
        st.markdown(f"""
        <div style="color:#0277BD; font-size:16px; margin-bottom:10px; border-top:2px solid #E1F5FE; padding-top:10px; font-weight:bold;">{s['zh']}</div>
        <div style="color:#546E7A; font-size:14px; line-height:1.8; background:#F1F8E9; padding:10px; border-radius:10px;">
            <span style="color:#2E7D32; font-weight:bold;">💡 NOTE:</span> {s.get('note', '')}
        </div>
        </div>
        """, unsafe_allow_html=True)

with tab4:
    if 'quiz_questions' not in st.session_state:
        st.session_state.quiz_questions = generate_quiz()
        st.session_state.quiz_step = 0; st.session_state.quiz_score = 0
    
    if st.session_state.quiz_step < len(st.session_state.quiz_questions):
        q = st.session_state.quiz_questions[st.session_state.quiz_step]
        st.markdown(f"""<div class="quiz-card">
            <span class="quiz-tag">{q['tag']}</span>
            <div style="font-size:20px; color:#0D47A1; margin-bottom:20px; font-weight:bold;">{q['text']}</div>
        </div>""", unsafe_allow_html=True)
        
        if 'audio' in q: play_audio_backend(q['audio'])
        
        opts = q['options']; cols = st.columns(min(len(opts), 3))
        for i, opt in enumerate(opts):
            with cols[i % 3]:
                if st.button(opt, key=f"q_{st.session_state.quiz_step}_{i}"):
                    if opt.lower() == q['correct'].lower():
                        st.success("✅ Fangcal! (Correct)"); st.session_state.quiz_score += 1
                    else:
                        st.error(f"❌ Caay ka matira... 正解: {q['correct']}"); 
                        if 'note' in q: st.info(q['note'])
                    time.sleep(1.5); st.session_state.quiz_step += 1; st.rerun()
    else:
        st.markdown(f"""<div style="text-align:center; padding:40px; border-radius:20px; background:#FFFFFF; border: 2px solid #81D4FA;">
            <h1 style="color:#EF6C00; font-family:Bubblegum Sans;">Tada Mafana' Kiso!</h1>
            <p style="font-size:22px; color:#0277BD;">得分: {st.session_state.quiz_score} / {len(st.session_state.quiz_questions)}</p>
            <p style="color:#546E7A;">你真厲害！</p>
        </div>""", unsafe_allow_html=True)
        if st.button("🔄 再玩一次 (Replay)"): del st.session_state.quiz_questions; st.rerun()

st.markdown("---")
st.caption("Powered by Code-CRF v7.1 | Theme: Crystal Shallow Water 🌊")
