import streamlit as st
import streamlit.components.v1 as components
import random
import re
import time
from gtts import gTTS
from io import BytesIO

# --- 0. 系統配置 (System Configuration) ---
st.set_page_config(
    page_title="O Hekal - 大自然", 
    page_icon="🏞️", 
    layout="centered"
)

# --- 1. 資料庫 (第 9 課：O Hekal - 修訂版) ---
VOCAB_MAP = {
    "ira": "有", "ko": "主格標記", "lotok": "山", "i": "在", 
    "hekal": "外面/大自然", "'alo": "河流", "sasi'ayaw": "正前方/對面", 
    "no": "的(屬格)", "fangcal": "漂亮/好", "ayam": "鳥", 
    "a": "連接詞", "ma'efer": "飛", "tada": "非常/真正", 
    "maso'so'": "清澈/乾淨", "nanom": "水", "cidal": "太陽"
}

VOCABULARY = [
    {"amis": "hekal", "zh": "外面/大自然", "emoji": "🏞️", "root": "hekal", "root_zh": "外"},
    {"amis": "lotok", "zh": "山", "emoji": "⛰️", "root": "lotok", "root_zh": "山"},
    {"amis": "'alo", "zh": "河流", "emoji": "🌊", "root": "'alo", "root_zh": "河"},
    {"amis": "fangcal", "zh": "漂亮/好", "emoji": "✨", "root": "fangcal", "root_zh": "善/美"},
    {"amis": "ayam", "zh": "鳥", "emoji": "🐦", "root": "ayam", "root_zh": "鳥"},
    {"amis": "ma'efer", "zh": "飛", "emoji": "🦅", "root": "'efer", "root_zh": "飛"},
    {"amis": "maso'so'", "zh": "清澈/乾淨", "emoji": "💧", "root": "so'so'", "root_zh": "洗"},
    {"amis": "tada", "zh": "非常/真正", "emoji": "❗", "root": "tada", "root_zh": "真"},
    {"amis": "sasi'ayaw", "zh": "正前方", "emoji": "👀", "root": "'ayaw", "root_zh": "前"},
    {"amis": "nanom", "zh": "水", "emoji": "🚰", "root": "nanom", "root_zh": "水"},
]

SENTENCES = [
    {
        "amis": "Ira ko lotok i hekal.", 
        "zh": "外面有山。", 
        "note": """
        <br><b>Ira</b>：有 (存在動詞)。
        <br><b>hekal</b>：外面/戶外/大自然。
        <br><b>句型</b>：Ira ko [物品] i [地點]。"""
    },
    {
        "amis": "Ira ko 'alo i sasi'ayaw no lotok.", 
        "zh": "山的前面有河流。", 
        "note": """
        <br><b>sasi'ayaw</b>：正前方/對面 (比 <i>'ayaw</i> 更具體)。
        <br><b>no lotok</b>：山的 (屬格)。
        <br><b>畫面</b>：河在山的正前方流過。"""
    },
    {
        "amis": "Fangcal ko hekal.", 
        "zh": "風景很漂亮。", 
        "note": """
        <br><b>Fangcal</b>：漂亮/美好。
        <br><b>hekal</b>：這裡指風景/景色。
        <br><b>注意</b>：通用詞，也可用於形容人好、天氣好。"""
    },
    {
        "amis": "Ira ko ayam a ma'efer.", 
        "zh": "有鳥在飛。", 
        "note": """
        <br><b>ayam</b>：鳥。
        <br><b>ma'efer</b>：飛 (動作)。
        <br><b>結構</b>：Ira... a [動作] (有...在做某事)。"""
    },
    {
        "amis": "Tada maso'so' ko nanom no 'alo.", 
        "zh": "河水非常清澈。", 
        "note": """
        <br><b>Tada</b>：非常 (程度副詞，置於形容詞前)。
        <br><b>maso'so'</b>：清澈 (原意為被洗淨的)。
        <br><b>nanom no 'alo</b>：河水。"""
    }
]

STORY_DATA = [
    {"amis": "Ira ko lotok i hekal.", "zh": "外面有山。"},
    {"amis": "Ira ko 'alo i sasi'ayaw no lotok.", "zh": "山的前面有河流。"},
    {"amis": "Fangcal ko hekal.", "zh": "風景很漂亮。"},
    {"amis": "Ira ko ayam a ma'efer.", "zh": "有鳥在飛。"},
    {"amis": "Tada maso'so' ko nanom no 'alo.", "zh": "河水非常清澈。"}
]

# --- 2. 視覺系統 (CSS 注入 - 強制高對比版) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;900&family=Noto+Sans+TC:wght@300;500;700&display=swap');
    
    /* 背景 */
    .stApp { background-color: #F1F8E9; color: #1B5E20; font-family: 'Noto Sans TC', sans-serif; }
    
    /* Tab 樣式 */
    .stTabs [data-baseweb="tab"] { 
        color: #33691E !important; 
        font-family: 'Nunito', 'Noto Sans TC', sans-serif;
        font-size: 18px;
        font-weight: 700;
    }
    .stTabs [aria-selected="true"] { 
        border-bottom: 4px solid #2E7D32 !important; 
        color: #1B5E20 !important; 
    }
    
    /* 按鈕 */
    .stButton>button { 
        border: 2px solid #2E7D32 !important; 
        background: #FFFFFF !important; 
        color: #1B5E20 !important; 
        font-family: 'Nunito', 'Noto Sans TC', sans-serif !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        width: 100%; 
        border-radius: 12px; 
    }
    .stButton>button:hover { 
        background: #2E7D32 !important; 
        color: #FFFFFF !important; 
    }
    
    /* 測驗卡片 */
    .quiz-card { 
        background: #FFFFFF; 
        border: 2px solid #81C784; 
        padding: 25px; 
        border-radius: 12px; 
        margin-bottom: 20px; 
    }
    .quiz-tag { 
        background: #5D4037; 
        color: #FFF; 
        padding: 4px 12px; 
        border-radius: 4px; 
        font-weight: bold; 
        font-size: 14px; 
        margin-right: 10px; 
        font-family: 'Nunito', 'Noto Sans TC', sans-serif;
    }
    
    /* 翻譯區塊 */
    .zh-translation-block {
        background: #E8F5E9;
        border-left: 5px solid #2E7D32;
        padding: 20px;
        color: #1B5E20; 
        font-size: 16px;
        line-height: 2.0;
        font-family: 'Noto Sans TC', monospace;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 核心技術：沙盒渲染引擎 ---
def get_html_card(item, type="word"):
    pt = "100px" if type == "full_amis_block" else "80px"
    mt = "-40px" if type == "full_amis_block" else "-30px" 

    style_block = f"""<style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;900&family=Noto+Sans+TC:wght@300;500;700&display=swap');
        body {{ background-color: transparent; color: #1B5E20; font-family: 'Noto Sans TC', sans-serif; margin: 0; padding: 5px; padding-top: {pt}; overflow-x: hidden; }}
        
        .interactive-word {{ position: relative; display: inline-block; border-bottom: 2px solid #2E7D32; cursor: pointer; margin: 0 3px; color: #1B5E20; transition: 0.3s; font-size: 19px; font-weight: 600; }}
        .interactive-word:hover {{ color: #E65100; border-bottom-color: #E65100; }}
        
        .interactive-word .tooltip-text {{ visibility: hidden; min-width: 80px; background-color: #1B5E20; color: #FFF; text-align: center; border-radius: 8px; padding: 8px; position: absolute; z-index: 100; bottom: 145%; left: 50%; transform: translateX(-50%); opacity: 0; transition: opacity 0.3s; font-size: 14px; white-space: nowrap; box-shadow: 0 4px 10px rgba(0,0,0,0.3); font-family: 'Nunito', 'Noto Sans TC', sans-serif; font-weight: 700; }}
        .interactive-word:hover .tooltip-text {{ visibility: visible; opacity: 1; }}
        
        .play-btn-inline {{ background: #2E7D32; border: none; color: #FFF; border-radius: 50%; width: 28px; height: 28px; cursor: pointer; margin-left: 8px; display: inline-flex; align-items: center; justify-content: center; font-size: 14px; transition: 0.3s; vertical-align: middle; }}
        .play-btn-inline:hover {{ background: #E65100; transform: scale(1.1); }}
        
        .word-card-static {{ background: #FFFFFF; border: 1px solid #A5D6A7; border-left: 6px solid #1B5E20; padding: 15px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; margin-top: {mt}; height: 100px; box-sizing: border-box; box-shadow: 0 3px 6px rgba(0,0,0,0.05); }}
        .wc-root-tag {{ font-size: 12px; background: #E8F5E9; color: #1B5E20; padding: 3px 8px; border-radius: 4px; font-weight: bold; margin-right: 5px; font-family: 'Nunito', 'Noto Sans TC', sans-serif; }}
        .wc-amis {{ color: #1B5E20; font-size: 26px; font-weight: 900; margin: 2px 0; font-family: 'Nunito', sans-serif; }}
        .wc-zh {{ color: #5D4037; font-size: 16px; font-weight: 500; }}
        .play-btn-large {{ background: #F1F8E9; border: 2px solid #1B5E20; color: #1B5E20; border-radius: 50%; width: 42px; height: 42px; cursor: pointer; font-size: 20px; transition: 0.2s; }}
        .play-btn-large:hover {{ background: #1B5E20; color: #FFF; }}
        
        .amis-full-block {{ line-height: 2.2; font-size: 18px; margin-top: {mt}; }}
        .sentence-row {{ margin-bottom: 12px; display: block; }}
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
                <div style="margin-bottom:5px;"><span class="wc-root-tag">ROOT: {v['root']}</span> <span style="font-size:12px; color:#757575;">({v['root_zh']})</span></div>
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
        body = f'<div style="font-size: 18px; line-height: 1.6; margin-top: {mt};">{" ".join(parts)}</div><button style="margin-top:10px; background:#1B5E20; border:none; color:#FFF; padding:6px 15px; border-radius:8px; cursor:pointer; font-family:Nunito; font-weight:700; box-shadow: 0 2px 4px rgba(0,0,0,0.2);" onclick="speak(`{full_js}`)">▶ PLAY AUDIO</button>'

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
    questions.append({"type": "trans", "tag": "🧩 中翻阿", "text": f"請選擇「<span style='color:#2E7D32'>{q2['zh']}</span>」的阿美語", "correct": q2['amis'], "options": q2_opts})
    
    # 3. 阿翻中
    q3 = random.choice(VOCABULARY)
    q3_opts = [q3['zh']] + [v['zh'] for v in random.sample([x for x in VOCABULARY if x != q3], 2)]
    random.shuffle(q3_opts)
    questions.append({"type": "trans_a2z", "tag": "🔄 阿翻中", "text": f"單字 <span style='color:#2E7D32'>{q3['amis']}</span> 的意思是？", "correct": q3['zh'], "options": q3_opts})

    # 4. 詞根偵探
    q4 = random.choice(VOCABULARY)
    other_roots = list(set([v['root'] for v in VOCABULARY if v['root'] != q4['root']]))
    if len(other_roots) < 2: other_roots += ["roma", "lalan", "cidal"]
    q4_opts = [q4['root']] + random.sample(other_roots, 2)
    random.shuffle(q4_opts)
    questions.append({"type": "root", "tag": "🧬 詞根偵探", "text": f"單字 <span style='color:#2E7D32'>{q4['amis']}</span> 的詞根是？", "correct": q4['root'], "options": q4_opts, "note": f"詞根意思：{q4['root_zh']}"})
    
    # 5. 語感聽解
    q5 = random.choice(STORY_DATA)
    questions.append({"type": "listen_sent", "tag": "🔊 語感聽解", "text": "請聽句子，選擇正確的中文翻譯", "audio": q5['amis'], "correct": q5['zh'], "options": [q5['zh']] + [s['zh'] for s in random.sample([x for x in STORY_DATA if x != q5], 2)]})

    # 6. 句型翻譯
    q6 = random.choice(STORY_DATA)
    q6_opts = [q6['amis']] + [s['amis'] for s in random.sample([x for x in STORY_DATA if x != q6], 2)]
    random.shuffle(q6_opts)
    questions.append({"type": "sent_trans", "tag": "📝 句型翻譯", "text": f"請選擇中文「<span style='color:#2E7D32'>{q6['zh']}</span>」對應的阿美語", "correct": q6['amis'], "options": q6_opts})

    # 7. 克漏字
    q7 = random.choice(STORY_DATA)
    words = q7['amis'].split()
    valid_indices = []
    for i, w in enumerate(words):
        clean_w = re.sub(r"[^\w']", "", w).lower()
        if clean_w in VOCAB_MAP:
            valid_indices.append(i)
    
    if valid_indices:
        target_idx = random.choice(valid_indices)
        target_raw = words[target_idx]
        target_clean = re.sub(r"[^\w']", "", target_raw).lower()
        
        words_display = words[:]
        words_display[target_idx] = "______"
        q_text = " ".join(words_display)
        
        correct_ans = target_clean
        distractors = [k for k in VOCAB_MAP.keys() if k != correct_ans and len(k) > 2]
        if len(distractors) < 2: distractors += ["kako", "ira"]
        opts = [correct_ans] + random.sample(distractors, 2)
        random.shuffle(opts)
        
        questions.append({"type": "cloze", "tag": "🕳️ 文法克漏字", "text": f"請填空：<br><span style='color:#1B5E20; font-size:18px;'>{q_text}</span><br><span style='color:#5D4037; font-size:14px;'>{q7['zh']}</span>", "correct": correct_ans, "options": opts})
    else:
        questions.append(questions[0]) 

    questions.append(random.choice(questions[:4])) 
    random.shuffle(questions)
    return questions

def play_audio_backend(text):
    try:
        tts = gTTS(text=text, lang='id'); fp = BytesIO(); tts.write_to_fp(fp); st.audio(fp, format='audio/mp3')
    except: pass

# --- 5. UI 呈現層 (修正重點：字體支援與正確渲染) ---
st.markdown("""
<div style="
    background: linear-gradient(180deg, #1B5E20 0%, #0D3310 100%); 
    border-bottom: 6px solid #5D4037; 
    border-radius: 15px; 
    padding: 30px; 
    text-align: center; 
    margin-bottom: 30px; 
    box-shadow: 0 6px 15px rgba(0, 0, 0, 0.4);
    position: relative;">
    
    <h1 style="
        font-family: 'Nunito', 'Noto Sans TC', 'Microsoft JhengHei', sans-serif; 
        color: #FFFFFF !important; 
        font-size: 50px; 
        font-weight: 900; 
        margin-bottom: 10px; 
        text-shadow: 3px 3px 0 #000000; 
        letter-spacing: 2px;">
        O Hekal
    </h1>
    
    <div style="
        color: #FFD54F !important; 
        font-size: 18px; 
        font-family: 'Nunito', 'Noto Sans TC', 'Microsoft JhengHei', sans-serif;
        font-weight: 700;
        background: rgba(0, 0, 0, 0.3); 
        padding: 5px 20px;
        border-radius: 20px;
        display: inline-block;
        border: 1px solid #FFD54F;">
        第 9 課：大自然
    </div>
    
    <div style="font-size: 12px; margin-top:10px; color:#C8E6C9; font-family: 'Nunito', sans-serif;">
        Code-CRF v6.4 | Theme: Wilderness High Contrast
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "🏞️ 互動課文", 
    "⛰️ 核心單字", 
    "🧬 句型解析", 
    "⚔️ 實戰測驗"
])

with tab1:
    st.markdown("### // 文章閱讀")
    st.caption("👆 點擊單字可聽發音並查看翻譯")
    
    st.markdown("""<div style="background:#FFFFFF; padding:10px; border: 2px solid #A5D6A7; border-radius:12px;">""", unsafe_allow_html=True)
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
    for v in VOCABULARY:
        components.html(get_html_card(v, type="word"), height=150)

with tab3:
    st.markdown("### // 語法結構分析")
    for s in SENTENCES:
        st.markdown("""<div style="background:#FFFFFF; padding:15px; border:1px dashed #2E7D32; border-radius: 12px; margin-bottom:15px;">""", unsafe_allow_html=True)
        components.html(get_html_card(s, type="sentence"), height=160)
        st.markdown(f"""
        <div style="color:#1B5E20; font-size:16px; margin-bottom:10px; border-top:1px solid #C8E6C9; padding-top:10px;">{s['zh']}</div>
        <div style="color:#2E7D32; font-size:14px; line-height:1.8; border-top:1px dashed #C8E6C9; padding-top:5px;"><span style="color:#1B5E20; font-family:Nunito; font-weight:bold;">ANALYSIS:</span> {s.get('note', '')}</div>
        </div>
        """, unsafe_allow_html=True)

with tab4:
    if 'quiz_questions' not in st.session_state:
        st.session_state.quiz_questions = generate_quiz()
        st.session_state.quiz_step = 0; st.session_state.quiz_score = 0
    
    if st.session_state.quiz_step < len(st.session_state.quiz_questions):
        q = st.session_state.quiz_questions[st.session_state.quiz_step]
        st.markdown(f"""<div class="quiz-card"><div style="margin-bottom:10px;"><span class="quiz-tag">{q['tag']}</span> <span style="color:#5D4037;">Q{st.session_state.quiz_step + 1}</span></div><div style="font-size:18px; color:#1B5E20; margin-bottom:10px;">{q['text']}</div></div>""", unsafe_allow_html=True)
        if 'audio' in q: play_audio_backend(q['audio'])
        opts = q['options']; cols = st.columns(min(len(opts), 3))
        for i, opt in enumerate(opts):
            with cols[i % 3]:
                if st.button(opt, key=f"q_{st.session_state.quiz_step}_{i}"):
                    if opt.lower() == q['correct'].lower():
                        st.success("✅ 正確 (Correct)"); st.session_state.quiz_score += 1
                    else:
                        st.error(f"❌ 錯誤 - 正解: {q['correct']}"); 
                        if 'note' in q: st.info(q['note'])
                    time.sleep(1.5); st.session_state.quiz_step += 1; st.rerun()
    else:
        st.markdown(f"""<div style="text-align:center; padding:30px; border:4px solid #1B5E20; border-radius:15px; background:#FFFFFF;"><h2 style="color:#1B5E20; font-family:Nunito;">MISSION COMPLETE</h2><p style="font-size:20px; color:#2E7D32;">得分: {st.session_state.quiz_score} / {len(st.session_state.quiz_questions)}</p></div>""", unsafe_allow_html=True)
        if st.button("🔄 重新挑戰 (Reboot)"): del st.session_state.quiz_questions; st.rerun()

st.markdown("---")
st.caption("Powered by Code-CRF v6.4 | Architecture: Chief Architect")
