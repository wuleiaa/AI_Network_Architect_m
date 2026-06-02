import os
from openai import OpenAI
from dotenv import load_dotenv

# 鍔犺浇鐜鍙橀噺
load_dotenv()

import streamlit as st

# ============================================================
# 甯搁噺闆嗕腑绠＄悊
# ============================================================
MAX_HISTORY = 10
MODEL_NAME = "deepseek-chat"
DEFAULT_TEMPERATURE = 0.4


class MCU_TutorAI:
    def __init__(self):
        # --- 鍏煎浜戠 Secrets 鍜屾湰鍦?.env ---
        try:
            api_key = st.secrets["AI_API_KEY"]
            base_url = st.secrets["AI_BASE_URL"]
        except (FileNotFoundError, KeyError):
            api_key = os.getenv("AI_API_KEY")
            base_url = os.getenv("AI_BASE_URL")

        if not api_key or not base_url:
            raise ValueError("鐜鍙橀噺 AI_API_KEY 鎴?AI_BASE_URL 鏈缃?)
        if not base_url.rstrip("/").endswith("/v1"):
            raise ValueError(f"AI_BASE_URL 蹇呴』浠?/v1 缁撳熬锛屽綋鍓嶅€? {base_url}")

        try:
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )
        except Exception as e:
            if "401" in str(e) or "authentication" in str(e).lower():
                raise RuntimeError("API 瀵嗛挜鏃犳晥鎴栧凡杩囨湡锛岃妫€鏌?Secrets 涓殑 AI_API_KEY") from e
            elif "base_url" in str(e).lower() or "invalid url" in str(e).lower():
                raise RuntimeError(f"base_url 鏍煎紡閿欒: {base_url}銆傚繀椤讳负 https://api.deepseek.com/v1") from e
            else:
                raise RuntimeError(f"OpenAI 瀹㈡埛绔垵濮嬪寲澶辫触: {str(e)}") from e

    # ================================================================
    # S1: 鍗曠墖鏈轰唬鐮佽瘖鐤楀
    # ================================================================
    def get_diagnostic_response(self, user_code, user_thought, topic):
        """
        鑻忔牸鎷夊簳寮忓甯堬細鍒嗘瀽瀛︾敓鐨凪CU浠ｇ爜鍜屾帓鏌ユ€濊矾锛屽紩瀵艰€岄潪鐩存帴缁欑瓟妗?
        """
        system_prompt = f"""
浣犳槸涓€浣嶈嫃鏍兼媺搴曞紡鐨勫崟鐗囨満/宓屽叆寮忕郴缁熷甯堛€?
褰撳墠瀹為獙涓婚锛歿topic}

銆愯緭鍏ヤ俊鎭€戯細
1. 瀛︾敓浠ｇ爜/閰嶇疆鐗囨锛氳鐢ㄦ埛杈撳叆
2. 瀛︾敓瀵硅嚜宸遍敊璇殑棰勫垽锛歿user_thought}

銆愪綘鐨勫洖澶嶉€昏緫銆戯細
1. 棣栧厛鐐硅瘎瀛︾敓鐨?棰勫垽"鏄惁鍑嗙‘銆傚鏋滃鐢熺寽瀵逛簡鏂瑰悜锛岀粰浜堣偗瀹氾紱
   濡傛灉鐚滈敊浜嗭紝鎸囧嚭涓轰粈涔堥偅涓柟鍚戜笉鏄棶棰樼殑鏍规簮銆?
2. 鐒跺悗鍒嗘瀽浠ｇ爜涓殑瀹為檯閿欒銆?
3. 涓嶈鐩存帴缁欎唬鐮侊紒閫氳繃鎻愰棶寮曞銆備緥濡傦細
   - "浣犳敞鎰忓埌GPIO鐨勬ā寮忛厤缃簡鍚楋紵鎺ㄦ尳杈撳嚭鍜屽紑婕忚緭鍑虹殑鍖哄埆鏄粈涔堬紵"
   - "浣犳鏌ヨ繃Timer鐨勯鍒嗛绯绘暟鍜岃嚜鍔ㄩ噸瑁呰浇鍊兼槸鍚﹀尮閰嶅悧锛?
   - "涓柇鏈嶅姟鍑芥暟涓紝浣犵‘璁ゆ爣蹇椾綅琚竻闄や簡鍚楋紵"
   - "涓插彛鐨勬尝鐗圭巼璁＄畻鍏紡鏄細娉㈢壒鐜?= f_osc / (12 脳 (256 - TH1))锛屼綘楠岃瘉杩囧悧锛?
4. 寮曞鏂瑰悜鍙傝€冿細
   - GPIO锛氭ā寮忥紙鎺ㄦ尳/寮€婕忥級銆佷笂鎷?涓嬫媺銆佹椂閽熶娇鑳姐€佸紩鑴氬垵濮嬪寲
   - Timer锛氶鍒嗛鍣ㄣ€佽嚜鍔ㄩ噸瑁呰浇銆佽鏁版ā寮忋€佷腑鏂娇鑳?
   - UART/I2C/SPI锛氭尝鐗圭巼銆佹椂搴忋€佽澶囧湴鍧€銆佸崗璁牸寮?
   - ADC锛氬弬鑰冪數鍘嬨€侀噰鏍锋椂闂淬€佹牎鍑嗐€佽浆鎹㈣Е鍙戞簮
   - PWM锛氬崰绌烘瘮銆侀鐜囪绠椼€佽緭鍑洪€氶亾閰嶇疆
   - 涓柇锛氫紭鍏堢骇銆佹爣蹇椾綅娓呴櫎銆佷腑鏂悜閲忚〃銆佸祵濂?
5. 浣跨敤 Markdown 鏍煎紡锛岃姘斾翰鍒囦絾涓撲笟銆?
6. 鏈€鍚庣暀涓嬩竴鍙ュ惎鍙戞€х殑鎬濊€冮銆?
        """

        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_code}
                ],
                stream=True,
                temperature=DEFAULT_TEMPERATURE
            )
            yield from response
        except Exception as e:
            # 淇锛氭祦寮忔帴鍙ｅ紓甯告椂搴旇繑鍥炲彲杩唬瀵硅薄锛岃€岄潪瀛楃涓?
            yield f"鈿狅笍 AI 杩炴帴涓柇: {str(e)}"

    # ================================================================
    # S3: 鍗曠墖鏈哄疄楠屽伐鍦猴紙鍘燂細鑷€傚簲瀹為獙宸ュ満锛?
    # ================================================================
    def generate_personalized_task(self, learning_topic, mastery_level):
        """
        鏍规嵁瀛︿範涓婚鍜屾帉鎻″害锛屽姩鎬佺敓鎴愬崟鐗囨満瀹為獙浠诲姟銆?
        """
        task_prompt = f"""
鎴戞槸涓€鍚嶃€婂崟鐗囨満鍘熺悊涓庢帴鍙ｆ妧鏈€嬭绋嬬殑瀛︾敓銆?
銆愪粖鏃ュ涔犻噸鐐广€戯細{learning_topic}
銆愭垜鐨勮嚜璇勬帉鎻″害銆戯細{mastery_level}

璇蜂负鎴戣璁′竴涓€氳繃 Keil C51 / STM32CubeIDE 瀹屾垚鐨勫疄鎴樹换鍔°€?

瑕佹眰锛?
1. 濡傛灉鎺屾彙搴︽槸"鍒氬叆闂?锛屼换鍔¤鍖呭惈璇︾粏鐨勬楠ゆ彁绀哄拰鍏抽敭瀵勫瓨鍣ㄩ厤缃鏄庛€?
2. 濡傛灉鏄?宸茬啛缁?锛屼换鍔¤鍖呭惈 2-3 涓殣钄界殑鏁呴殰闄烽槺锛圱roubleshooting锛夈€?
3. 濡傛灉鏄?宸茬簿閫?锛屾寫鎴樼患鍚堟€у澶栬鍗忓悓浠诲姟銆?
4. 蹇呴』绱ф墸"{learning_topic}"杩欎釜涓婚銆?
5. 濡傛灉娑夊強纭欢鎺ョ嚎锛岄渶鐢ㄦ枃瀛楁弿杩拌繛鎺ユ柟寮忋€?

杈撳嚭缁撴瀯锛?
### 馃幆 浠婃棩鎸戞垬鐩爣
### 馃搵 纭欢杩炵嚎璇存槑锛堝娑夊強锛?
### 馃敡 閰嶇疆浠诲姟/缂栫▼浠诲姟
### 馃悰 棰勫煁鏁呴殰/鎺掗敊鎸戞垬
### 鉁?楠屾敹鏍囧噯 (LED鐘舵€?/ 涓插彛杈撳嚭 / 绀烘尝鍣ㄦ尝褰?
        """

        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": task_prompt}],
                stream=True
            )
            yield from response
        except Exception as e:
            yield f"鈿狅笍 浠诲姟鐢熸垚澶辫触: {str(e)}"

    # ================================================================
    # S3: 鍙傝€冪瓟妗堢敓鎴愶紙鍘燂細generate_task_solution锛?
    # ================================================================
    def generate_task_solution(self, task_content):
        """
        鏍规嵁宸茬敓鎴愮殑瀹為獙浠诲姟锛屾彁渚涙爣鍑嗗弬鑰冧唬鐮併€?
        """
        solution_prompt = f"""
浣犳槸涓€浣嶈祫娣辩殑鍗曠墖鏈?宓屽叆寮忕郴缁熷甯堛€傝鏍规嵁浠ヤ笅瀹為獙浠诲姟锛屾彁渚涙爣鍑嗙殑鍙傝€冧唬鐮佸拰鍘熺悊璁茶В銆?

銆愪换鍔″唴瀹瑰洖椤俱€戯細
{task_content}

銆愯緭鍑鸿姹傘€戯細
1. 鎸夋ā鍧楀垪鍑?C 璇█浠ｇ爜锛圕51 鏍煎紡浼樺厛锛屼篃鍙粰鍑?STM32 HAL 搴撴牸寮忥級銆?
2. 浣跨敤 Markdown 浠ｇ爜鍧楋紙```c锛夈€?
3. 娉ㄩ噴瑙ｉ噴鍏抽敭閰嶇疆鐨勪綔鐢紙濡傚瘎瀛樺櫒璁剧疆銆佹椂搴忓叧绯伙級銆?
4. 缁欏嚭 1-2 涓牳蹇冮獙璇佹柟娉曠殑棰勬湡杈撳嚭锛堝涓插彛鎵撳嵃鍐呭銆丩ED 闂儊棰戠巼銆佹尝褰㈡弿杩帮級銆?
5. 鏍煎紡娓呮櫚锛屼唬鐮佸彲鐩存帴澶嶅埗杩愯銆?
        """

        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": solution_prompt}],
                stream=True
            )
            yield from response
        except Exception as e:
            yield f"鈿狅笍 绛旀鐢熸垚澶辫触: {str(e)}"


    # ================================================================
    # S3: AI瀵煎笀瀹￠槄瀛︾敓鎻愪氦锛堟柊澧炲姛鑳斤級
    # ================================================================
    # S3 AI tutor review student submission
    def review_student_submission(self, task_content, student_submission, conversation_history):
        """
        AI瀵煎笀锛氬闃呭鐢熼拡瀵瑰崟鐗囨満瀹為獙浠诲姟鎻愪氦鐨勪唬鐮?鏂规锛?
        妫€鏌ュ閿欍€佺粰浜堢籂姝ｅ紩瀵笺€佹敮鎸佸杞凯浠ｏ紝鏈€鍚庣粰鍑虹瓟妗堝拰缁撹銆?

        Args:
            task_content: 瀹為獙浠诲姟鍐呭
            student_submission: 瀛︾敓鏈鎻愪氦鐨勪唬鐮?绛旀
            conversation_history: 姝ゅ墠澶氳疆杩唬鐨勫璇濆巻鍙诧紙鍒楄〃锛夛紝
                                  姣忛」涓?{"role": "student"/"tutor", "content": "..."}
        """
        is_first_submission = len(conversation_history) == 0
        history_context = ""
        history_lines = []
        if not is_first_submission:
            for msg in conversation_history:
                role_label = "瀛︾敓" if msg["role"] == "student" else "AI瀵煎笀"
                history_lines.append(f"{role_label}:\n{msg['content']}\n")
        combined_history = "".join(history_lines) if history_lines else ""
        context_note = ("銆愭鍓嶅杞凯浠ｈ褰曘€戯細\n" + combined_history) if combined_history else ""

        system_prompt = f"""浣犳槸涓€浣嶆瀬鍏朵弗璋ㄤ笖瀵屾湁鑰愬績鐨?**鍗曠墖鏈?宓屽叆寮忕郴缁?AI 瀵煎笀**銆備綘鐨勫伐浣滄槸閽堝浠ヤ笅瀹為獙浠诲姟锛屽闃呭鐢熸彁浜ょ殑浠ｇ爜/閰嶇疆鏂规锛屽苟缁欏嚭涓撲笟鍙嶉銆?

銆愬疄楠屼换鍔°€戯細
{task_content}
{context_note}

銆愭湰娆″鐢熸彁浜ゃ€戯細
{student_submission}

銆愬闃呰鍒欌€斺€旇涓ユ牸鎸夌収浠ヤ笅閫昏緫鎵ц銆戯細

### 绗竴闃舵锛氭鏌ヤ笌寮曞
1. **閫愰」妫€鏌?*锛氬鐓у疄楠屼换鍔＄殑姣忎釜瑕佹眰锛岄€愪竴妫€鏌ュ鐢熸彁浜ゆ槸鍚︽纭€?
2. **瀹氫綅閿欒**锛氭槑纭寚鍑轰唬鐮?閰嶇疆涓叿浣撶殑閿欒浣嶇疆鍜屽師鍥犮€?
3. **寮曞鎬濊€?*锛氫笉瑕佺洿鎺ョ粰鍑烘纭瓟妗堬紒閫氳繃鎻愰棶寮曞瀛︾敓鑷繁鍙戠幇闂銆?
4. **鑲畾姝ｇ‘閮ㄥ垎**锛氬浜庡鐢熷仛寰楀鐨勫湴鏂癸紝鍏堢粰浜堣偗瀹氬拰榧撳姳銆?
5. **缁欏嚭鏀硅繘鏂瑰悜**锛氭槑纭憡璇夊鐢熷簲璇ヤ粠鍝簺鏂瑰悜淇敼銆?

### 绗簩闃舵锛氳凯浠ｆ帹杩?
- 濡傛灉瀛︾敓鏄娆℃彁浜わ紝缁欏嚭鍒濇鍙嶉鍚庯紝璇锋槑纭锛?**璇锋牴鎹互涓婂弽棣堜慨鏀逛綘鐨勪唬鐮侊紝淇敼鍚庡啀娆℃彁浜ょ粰鎴戝闃呫€?*"
- 濡傛灉瀛︾敓宸茬粡杩囧杞凯浠ｏ紝璇疯窡韪叾鏀硅繘鎯呭喌锛岄€愭鍑忓皯鎻愮ず锛岀洿鍒版柟妗堝畬鍏ㄦ纭€?

### 绗笁闃舵锛氱粰鍑烘渶缁堢瓟妗堝拰缁撹
- 褰撳鐢熸彁浜ょ殑鏂规 **宸茬粡瀹屽叏姝ｇ‘** 鏃讹紝浣犲繀椤伙細
  1. 鏄庣‘瀹ｅ竷锛?**浣犵殑鏂规宸插畬鍏ㄦ纭紒**"
  2. 瀵规暣涓疄楠屼换鍔＄殑瑕佺偣杩涜鎬荤粨
  3. 缁欏嚭 **鏍囧噯鍙傝€冧唬鐮?绛旀**锛堢敤 ```c 浠ｇ爜鍧楁爣娉級
  4. 缁欏嚭缁撹鎬ц瘎璇拰瀛︿範寤鸿

- 褰撳鐢熸彁浜ょ殑鏂规 **浠嶆湁鏄庢樉閿欒**锛屼絾瀛︾敓涓诲姩瑕佹眰鐪嬫渶缁堢瓟妗堟椂锛屼篃瑕佺粰鍑哄畬鏁寸殑鏍囧噯鍙傝€冧唬鐮佸拰缁撹銆?

璇蜂娇鐢?Markdown 鎺掔増锛岃姘斾笓涓氫笖浜插垏銆?
"""
        messages = [{"role": "system", "content": system_prompt}]
        response = self.client.chat.completions.create(model=MODEL_NAME, messages=messages, stream=True, temperature=DEFAULT_TEMPERATURE)
        yield from response
    # ================================================================
    # 妯″潡涓? 鍗曠墖鏈哄師鐞嗘繁搴﹁拷闂?
    # ================================================================
    def socratic_quiz(self, concept):
        """
        瀵瑰崟鐗囨満瀹為獙闂/鏁呴殰杩涜鑻忔牸鎷夊簳寮忚瘖鏂紩瀵? 鑰屼笉鏄洿鎺ョ粰绛旀.
        """
        prompt = f"""浣犳槸涓€浣嶅崟鐗囨満瀹為獙瀵煎笀锛屼娇鐢ㄨ嫃鏍兼媺搴曞紡鏁欏娉曞紩瀵煎鐢熻嚜宸辫В鍐抽棶棰樸€?

瀛︾敓鎻忚堪鐨勫疄楠岄棶棰橈細"{concept}"

璇烽伒寰互涓嬪師鍒欙細

1. **涓嶈鐩存帴缁欏嚭绛旀鎴栬В鍐虫柟妗堛€?* 姘歌繙涓嶈鐩存帴鍛婅瘔瀛︾敓"浣犲簲璇ユ€庝箞鍋?銆?

2. **閫氳繃鎻愰棶寮曞瀛︾敓鑷繁鍙戠幇闂鏍规簮銆?* 姣忔鍥炲簲鎻愬嚭2-3涓湁閽堝鎬х殑鍚彂寮忛棶棰橈紝渚嬪锛?
   - "浣犵‘璁よ繃瀵瑰簲GPIO绔彛鐨勬椂閽熶娇鑳藉瘎瀛樺櫒宸茬粡寮€鍚簡鍚楋紵"
   - "绀烘尝鍣ㄩ噺杩囪繖涓紩鑴氱殑娉㈠舰鍚楋紵楂樹綆鐢靛钩鏄惁绗﹀悎棰勬湡锛?
   - "濡傛灉鎷挎帀杩欎釜寤舵椂锛岀幇璞′細鍙樺寲鍚楋紵涓轰粈涔堬紵"

3. **瑕嗙洊甯歌鍗曠墖鏈哄疄楠屾晠闅滄帓鏌ユ柟鍚戯細**
   - 纭欢杩炴帴锛氭帴绾挎槸鍚︽纭紵鍏卞湴浜嗗悧锛熶笂鎷?涓嬫媺鐢甸樆锛?
   - 鏃堕挓閰嶇疆锛氬搴斿璁炬椂閽熶娇鑳戒簡鍚楋紵鏃堕挓婧愰€夋嫨姝ｇ‘鍚楋紵
   - 鍒濆鍖栭『搴忥細鍏堥厤缃瓽PIO鍐嶉厤缃璁撅紵涓柇浼樺厛绾ц缃悎鐞嗗悧锛?
   - 瀵勫瓨鍣ㄦ搷浣滐細鏍囧織浣嶆竻闆朵簡鍚楋紵鏁版嵁鎵嬪唽鐩稿叧绔犺妭纭杩囧悧锛?
   - 杞欢閫昏緫锛氶€昏緫鍒嗘瀽浠?涓插彛鎵撳嵃纭杩囩▼鐘舵€佷簡鍚楋紵

4. **璇皵浜插垏锛岄紦鍔卞鐢熷姩鎵嬮獙璇併€?* 鐢?浣犺瘯杩?.."銆?涓嶅Θ閲忎竴涓?.."绛夊紩瀵煎彛鍚汇€?

5. 浣跨敤 **Markdown 鎺掔増**锛岃闂灞傛娓呮櫚銆?

6. 濡傛灉瀛︾敓鎻忚堪澶ā绯婏紝鍏堝弽闂叿浣撶粏鑺備俊鎭紙寮€鍙戞澘鍨嬪彿銆佹帴绾垮浘銆佷唬鐮佺墖娈点€佹祴閲忕粨鏋滅瓑锛夈€?
        """

        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )
            yield from response
        except Exception as e:
            yield f"鈿狅笍 杩炴帴寮傚父: {str(e)}"


    # ================================================================
    # S2: 纭欢浠跨湡瀹為獙
    # ================================================================
    def generate_hardware_simulation(self, component, difficulty):
        """鏍规嵁閫夊畾缁勪欢鍜岄毦搴︾敓鎴?Proteus 纭欢浠跨湡瀹為獙鏂规."""
        sim_prompt = f"""You are a MCU hardware simulation tutor. Design a Proteus experiment.
Component: {component}
Difficulty: {difficulty}
Output: experiment objective, circuit diagram, C reference code, 
Proteus settings, expected results, troubleshooting tips.
Use Markdown format."""
        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{'role': 'user', 'content': sim_prompt}],
                stream=True
            )
            return response
        except Exception as e:
            yield f"Simulation plan generation failed: {str(e)}"

