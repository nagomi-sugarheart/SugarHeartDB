"""
CoCo夏夏夏 Holiday / ダンシング・デッド 欠損画像アップロードスクリプト
"""
import json, re, os, ssl, urllib3, time

d = open(r'C:/Users/sawas/.claude.json', encoding='utf-8').read()
os.environ['CLOUDINARY_URL'] = re.search(r'cloudinary://[0-9]+:[^"\']+@dnmzdghoi', d).group(0)
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import cloudinary
import cloudinary.uploader as up
cloudinary.CERT_KWARGS = {"cert_reqs": "CERT_NONE"}
up._http = urllib3.PoolManager(cert_reqs="CERT_NONE")

BASE = r'C:\Users\sawas\OneDrive\Pictures\欠損部分'
EV_COCO = 'Deresute/Event/CoCoNatsuHoliday'
EV_DD = 'Deresute/Event/DancingDead'

# ── CoCo夏夏夏 Holiday ──────────────────────────────
# 章時刻(seconds): OP=124, 1話=645, 2話=1087, 3話=1529, 4話=2040, 5話=2503, ED=2874
# タイトルカード画像時刻(秒)= 直後+数秒: OP=130(00:02:10), 1話=650(00:10:50),
#   2話=1092(00:18:12), 3話=1536(00:25:36), 4話=2045(00:34:05), 5話=2508(00:41:48), ED=2880(00:48:00)
# data-start新値 = タイトル時刻 - 1秒
# OP:129, 1話:649, 2話:1091, 3話:1535, 4話:2044, 5話:2507, ED:2879

coco_uploads = [
    # ── タイトルカード7枚 ──
    (r'CoCo夏夏夏Holiday_00.02.10.png', 'commu/title_OP'),
    (r'CoCo夏夏夏Holiday_00.10.50.png', 'commu/title_1'),
    (r'CoCo夏夏夏Holiday_00.18.12.png', 'commu/title_2'),
    (r'CoCo夏夏夏Holiday_00.25.36.png', 'commu/title_3'),
    (r'CoCo夏夏夏Holiday_00.34.05.png', 'commu/title_4'),
    (r'CoCo夏夏夏Holiday_00.41.48.png', 'commu/title_5'),
    (r'CoCo夏夏夏Holiday_00.48.00.png', 'commu/title_ED'),
    # ── セリフshot ──
    # 予告タブ l.216: 心「みんなやっほー☆...」 直前:commu/0002(title_予告) → 0002a
    (r'CoCo夏夏夏Holiday_00.00.58.png', 'commu/0002a'),
    # OP l.244: 3人「夏だーーーーっ！！！！」 直前:title_OP(=0009) → 0009a
    (r'CoCo夏夏夏Holiday_00.02.19.png', 'commu/0009a'),
    # OP l.245: 心「ヤバ、めっちゃ綺麗ーっ！」 直前:0009a → 0009b
    (r'CoCo夏夏夏Holiday_00.02.31.png', 'commu/0009b'),
    # OP l.248: 愛梨「荘厳で...」 直前:commu/0011(SRT21「荘厳で」=SRT#21 00:02:51) → 0011a
    (r'CoCo夏夏夏Holiday_00.03.03.png', 'commu/0011a'),
    # OP l.267: 心「当事者たち大集合☆」 直前:commu/0024(SRT#39 00:05:36) → 0024a
    (r'CoCo夏夏夏Holiday_00.05.42.png', 'commu/0024a'),
    # OP l.272: 後輩P「えっ？ わ、私が......ですか？」 直前:commu/0026(SRT#45) → 0026a
    (r'CoCo夏夏夏Holiday_00.06.28.png', 'commu/0026a'),
    # OP l.273: P「ああ。申し訳ないが...」 直前:0026a → 0026b
    (r'CoCo夏夏夏Holiday_00.06.39.png', 'commu/0026b'),
    # OP l.279: P「......というわけで...」 直前:commu/0030(SRT#51) → 0030a
    (r'CoCo夏夏夏Holiday_00.07.14.png', 'commu/0030a'),
    # 1話 l.321: 心「人懐っこくてカワイイ～♪」 直前:title_1(=0067) → 0067a
    (r'CoCo夏夏夏Holiday_00.11.11.png', 'commu/0067a'),
    # 2話 l.391: 亜季「では、私からはこれを...！」 直前:commu/0118 → 0118a (0118はtitle_2)
    # ※2話のdss-linesの先頭に場所カード行がないため、直前=0118
    (r'CoCo夏夏夏Holiday_00.19.46.png', 'commu/0118a'),
    # 2話 l.399: 愛梨「まさか、こんなことになるなんて......。」 直前:commu/0118b → 0118b
    (r'CoCo夏夏夏Holiday_00.20.42.png', 'commu/0118b'),
    # 3話 l.450: 鈴帆「ついに、ついに......完成ばい......っ！」 直前:title_3(=0178) → 0178a
    (r'CoCo夏夏夏Holiday_00.25.43.png', 'commu/0178a'),
    # 3話 l.454: 心・愛梨「おっけー☆ わかりました♪」 直前:commu/0180 → 0180a
    (r'CoCo夏夏夏Holiday_00.26.21.png', 'commu/0180a'),
    # 3話 l.459: 現地の人「Hi, cutie！」 直前:commu/0185 → 0185a
    (r'CoCo夏夏夏Holiday_00.26.52.png', 'commu/0185a'),
    # 3話 l.464: 後輩P「えっ！？ ちょ...すとーっぷ！」 直前:commu/0188 → 0188a
    (r'CoCo夏夏夏Holiday_00.27.33.png', 'commu/0188a'),
    # 3話 l.471: 心「な、なんじゃこりゃーー！！！！」 直前:commu/0193 → 0193a
    (r'CoCo夏夏夏Holiday_00.28.41.png', 'commu/0193a'),
    # 3話 l.472: 鈴帆「ふっふっふ...」 直前:0193a → 0193b
    (r'CoCo夏夏夏Holiday_00.28.56.png', 'commu/0193b'),
    # 3話 l.473: 愛梨「これ、私たちも着るの？」 直前:0193b → 0193c
    (r'CoCo夏夏夏Holiday_00.29.01.png', 'commu/0193c'),
    # 3話 l.474: 鈴帆「もちろん！ふたりとも...」 直前:0193c → 0193d
    (r'CoCo夏夏夏Holiday_00.29.16.png', 'commu/0193d'),
    # 3話 l.475: 心「......も、もー。」 直前:0193d → 0193e
    (r'CoCo夏夏夏Holiday_00.29.24.png', 'commu/0193e'),
    # 3話 l.476: 愛梨「はいっ♪ 愛梨、ひと肌...」 直前:0193e → 0193f
    (r'CoCo夏夏夏Holiday_00.29.37.png', 'commu/0193f'),
    # 3話 l.478: 心「オーストラリアへ～、いざ☆」 直前:commu/0202 → 0202a
    (r'CoCo夏夏夏Holiday_00.30.07.png', 'commu/0202a'),
    # 3話 l.479: 愛梨「はあ、ふ......今の私は木！」 直前:0202a → 0202b
    (r'CoCo夏夏夏Holiday_00.30.27.png', 'commu/0202b'),
    # 3話 l.480: 後輩P「あの、これは......？」 直前:0202b → 0202c
    (r'CoCo夏夏夏Holiday_00.30.32.png', 'commu/0202c'),
    # 3話 l.481: 鈴帆「オーストラリアたい！」 直前:0202c → 0202d
    (r'CoCo夏夏夏Holiday_00.30.34.png', 'commu/0202d'),
    # 3話 l.484: 後輩P「......はぁとさんの防水加工は？」 直前:commu/0207 → 0207a
    (r'CoCo夏夏夏Holiday_00.30.57.png', 'commu/0207a'),
    # 3話 l.486: 3人「はぁとしゃーー！！！！」 直前:0207a → 0207b
    (r'CoCo夏夏夏Holiday_00.31.14.png', 'commu/0207b'),
    # 3話 l.487: 後輩P「......すみません、予定を狂わせてしまって。」 直前:0207b → 0207c
    (r'CoCo夏夏夏Holiday_00.31.20.png', 'commu/0207c'),
    # 3話 l.495: 後輩P「......あの、みなさんすいぶん自然体ですけど。」 直前:commu/0212 → 0212a
    (r'CoCo夏夏夏Holiday_00.32.34.png', 'commu/0212a'),
    # 3話 l.501: 後輩P「（笑顔......信頼......。」 直前:0212a → 0212b (3話ラスト行)
    (r'CoCo夏夏夏Holiday_00.33.41.png', 'commu/0212b'),
    # 4話 l.535: 亜季「......っくしゅん！」 直前:title_4(=0213) → 0213a
    (r'CoCo夏夏夏Holiday_00.35.55.png', 'commu/0213a'),
    # 4話 l.536: 梨沙「あら、風邪？」 直前:0213a → 0213b
    (r'CoCo夏夏夏Holiday_00.36.02.png', 'commu/0213b'),
    # 4話 l.539: 梨沙「今頃お土産でも...」 直前:commu/0215 → 0215a
    (r'CoCo夏夏夏Holiday_00.36.33.png', 'commu/0215a'),
    # 4話 l.540: 亜季「いえ、それならば後で......」 直前:0215a → 0215b
    (r'CoCo夏夏夏Holiday_00.36.38.png', 'commu/0215b'),
    # 4話 l.542: 愛梨「ふう、いっぱい買っちゃったぁ。」 直前:commu/0216 → 0216a
    (r'CoCo夏夏夏Holiday_00.36.54.png', 'commu/0216a'),
    # 4話 l.557: 梨沙「プロデューサーも、近況報告しなさいよ。」 直前:commu/0245 → 0245a
    (r'CoCo夏夏夏Holiday_00.39.03.png', 'commu/0245a'),
    # 4話 l.558: P「こっちは順調だよ。」 直前:0245a → 0245b
    (r'CoCo夏夏夏Holiday_00.39.10.png', 'commu/0245b'),
    # 4話 l.561: 亜季「ぶふっ、そう言われると...」 直前:commu/0247 → 0247a
    (r'CoCo夏夏夏Holiday_00.39.37.png', 'commu/0247a'),
    # 5話 l.618: 後輩P「......。」 直前:title_5(=0262) → 0262a
    (r'CoCo夏夏夏Holiday_00.46.01.png', 'commu/0262a'),
    # ED l.669: 後輩P「ええ、先方も期待以上...」 直前:title_ED(=0302) → 0302a
    (r'CoCo夏夏夏Holiday_00.51.14.png', 'commu/0302a'),
    # ED l.672: 鈴帆「......えへへ～、嬉しかぁ♪」 直前:0302a → 0302b
    (r'CoCo夏夏夏Holiday_00.51.45.png', 'commu/0302b'),
    # ED l.684: 梨沙「ええ！ツアーに行ってた連中も...」 直前:commu/0313 → 0313a
    (r'CoCo夏夏夏Holiday_00.53.39.png', 'commu/0313a'),
    # 00.51.40.png は選択肢画面「続く」のため除外
]

# ── ダンシング・デッド ──────────────────────────────
# 章時刻: OP=157, 1話=662, 2話=1218, 3話=1843, 4話=2457, 5話=2909, ED=3616
# 欠損画像を各章時刻+1~10sで照合した結果:
#   OP: 00.02.41(161s) = 157+4s → OPタイトルカード ✓
#   1話~ED: 対応する時刻の画像なし → 撮り漏れ（title_1~title_EDは別途）
# セリフshot直前フレームはHTMLから確認
# 予告タブno-shot:
#   l.200: 心「もうすぐハロウィン...」 直前:commu/0003 → 0003a
#   l.204: 雫「こんにちは...」 直前:commu/0006 → 0006a
# OP no-shot:
#   l.231: 学生たち「うわっ...きゃーーーーーー！？」 直前:commu/0012 → 0012a
#   l.232: ナレーション 直前:0012a → 0012b
#   l.245: 雫「そうですね......。」 直前:commu/0024 → 0024a
# 1話 no-shot:
#   l.264: きらり「雫ちゃん、大丈夫？ 着られた？」 直前:commu/0043 → 0043a
#   l.265: 雫「あ、はいー。...」 直前:0043a → 0043b
#   l.266: 心・きらり「可愛い～～～～～っ☆」 直前:0043b → 0043c
#   l.268: 雫「そ、そうですか......？」 直前:commu/0044 → 0044a
#   l.271: 雫「こうでしょうかー？」 直前:commu/0046 → 0046a
#   l.322: 雫「私、アイドルになるまで...」 直前:commu/0097 → 0097a
#   l.323: 雫「でもはぁとさんも...」 直前:0097a → 0097b
#   l.330: 雫「急なお願いなのに...」 直前:commu/0105 → 0105a
#   l.333: 梨沙「今日はファッションデザイナーの...」 直前:commu/0108 → 0108a
#   l.335: 梨沙「はい！ 先生は...」 直前:commu/0110 → 0110a
#   l.345: 雫「いえー。...」 直前:commu/0119 → 0119a

dd_uploads = [
    # ── OPタイトルカード(1枚のみ) ──
    (r'ダンシング・デッド_00.02.41.png', 'commu/title_OP'),
    # ── セリフshot ──
    # 予告タブ l.200: 心「もうすぐハロウィン...」 直前:commu/0003 → 0003a
    (r'ダンシング・デッド_00.01.27.png', 'commu/0003a'),
    # 予告2 l.204: 雫「こんにちは...」 直前:commu/0006 → 0006a
    (r'ダンシング・デッド_00.02.11.png', 'commu/0006a'),
    # OP l.231: 学生たち「うわっ...きゃーーーーーー！？」 直前:commu/0012 → 0012a
    (r'ダンシング・デッド_00.03.04.png', 'commu/0012a'),
    # OP l.245: 雫「そうですね...できたら...」 直前:commu/0024 → 0024a
    (r'ダンシング・デッド_00.04.51.png', 'commu/0024a'),
    # 1話 l.264: きらり「雫ちゃん、大丈夫？ 着られた？」 直前:commu/0043 → 0043a
    (r'ダンシング・デッド_00.08.01.png', 'commu/0043a'),
    # 1話 l.265: 雫「あ、はいー。...」 直前:0043a → 0043b
    (r'ダンシング・デッド_00.08.11.png', 'commu/0043b'),
    # 1話 l.266: 心・きらり「可愛い～～～～～っ☆」 直前:0043b → 0043c
    (r'ダンシング・デッド_00.08.16.png', 'commu/0043c'),
    # 1話 l.268: 雫「そ、そうですか......？」 直前:commu/0044 → 0044a
    (r'ダンシング・デッド_00.08.31.png', 'commu/0044a'),
    # 1話 l.271: 雫「こうでしょうかー？」 直前:commu/0046 → 0046a
    (r'ダンシング・デッド_00.08.53.png', 'commu/0046a'),
    # 1話 l.322: 雫「私、アイドルになるまで...」 直前:commu/0097 → 0097a
    (r'ダンシング・デッド_00.13.47.png', 'commu/0097a'),
    # 1話 l.323: 雫「でもはぁとさんも...」 直前:0097a → 0097b
    (r'ダンシング・デッド_00.14.03.png', 'commu/0097b'),
    # 1話 l.330: 雫「急なお願いなのに...」 直前:commu/0105 → 0105a
    (r'ダンシング・デッド_00.14.57.png', 'commu/0105a'),
    # 1話 l.333: 梨沙「今日はファッションデザイナーの...」 直前:commu/0108 → 0108a
    (r'ダンシング・デッド_00.15.29.png', 'commu/0108a'),
    # 1話 l.335: 梨沙「はい！ 先生は...」 直前:commu/0110 → 0110a
    (r'ダンシング・デッド_00.15.50.png', 'commu/0110a'),
    # 1話 l.345: 雫「いえー。デザイナーさんの...」 直前:commu/0119 → 0119a
    (r'ダンシング・デッド_00.17.44.png', 'commu/0119a'),
    # 2話 l.389: 女子学生「はい......今まで考えてたテーマ...」 直前:commu/0122 → 0122a
    (r'ダンシング・デッド_00.21.22.png', 'commu/0122a'),
    # 2話 l.407: 雫「ふぅ......。らしくない、かぁ......。」 直前:commu/0144 → 0144a
    (r'ダンシング・デッド_00.24.11.png', 'commu/0144a'),
    # 2話 l.409: 雫「（それに......私たちの衣装も。）」 直前:0144a → 0144b
    (r'ダンシング・デッド_00.24.26.png', 'commu/0144b'),
    # 2話 l.413: 心「さっすがきらりちゃん。やっぱバレるか☆」 直前:commu/0172 → 0172a
    (r'ダンシング・デッド_00.25.09.png', 'commu/0172a'),
    # 2話 l.419: きらり「......。」 直前:commu/0178 → 0178a
    (r'ダンシング・デッド_00.26.02.png', 'commu/0178a'),
    # 2話 l.432: 雫「はぁとさんは悪くないですよー...」 直前:commu/0191 → 0191a
    (r'ダンシング・デッド_00.27.44.png', 'commu/0191a'),
    # 2話 l.447: 心「えっと、明日のスケジュールは......嬉しかった、かあ。」 直前:commu/0206 → 0206a
    (r'ダンシング・デッド_00.30.28.png', 'commu/0206a'),
    # 3話 l.478: 心「んー、あとは......。」 直前:commu/0221 → 0221a (3話dss-lines先頭)
    (r'ダンシング・デッド_00.32.58.png', 'commu/0221a'),
    # 3話 l.485: 心「だってさぁ......。」 直前:commu/0229 → 0229a
    (r'ダンシング・デッド_00.33.52.png', 'commu/0229a'),
    # 3話 l.493: 心「そ、そんなことは......なくもなくもない、かも......。」 直前:commu/0236 → 0236a
    (r'ダンシング・デッド_00.35.12.png', 'commu/0236a'),
    # 3話 l.494: 梨沙「どっちなのよ！？ ......はぁ。」 直前:0236a → 0236b
    (r'ダンシング・デッド_00.35.17.png', 'commu/0236b'),
    # 3話 l.496: 心「それは......もちろん、思わないけど。」 直前:0236b → 0236c
    (r'ダンシング・デッド_00.35.33.png', 'commu/0236c'),
    # 3話 l.498: 梨沙「ユニットは対等なんだから...」 直前:commu/0240 → 0240a
    (r'ダンシング・デッド_00.35.57.png', 'commu/0240a'),
    # 3話 l.501: 雫「うーん......。」 直前:commu/0244 → 0244a
    (r'ダンシング・デッド_00.36.30.png', 'commu/0244a'),
    # 3話 l.507: 雫「あ......はい。でも大丈夫ですよー？」 直前:commu/0250 → 0250a
    (r'ダンシング・デッド_00.37.15.png', 'commu/0250a'),
    # 4話 l.521: P「君たち3人がファッションや...」 直前:commu/0264 → 0264a
    (r'ダンシング・デッド_00.39.40.png', 'commu/0264a'),
    # 4話 l.524: きらり「Pちゃん......。うん、そうだよね。」 直前:0264a → 0264b
    (r'ダンシング・デッド_00.40.08.png', 'commu/0264b'),
    # 4話 l.550: 心「うん、単刀直入に言うね。」 直前:commu/0277 → 0277a
    (r'ダンシング・デッド_00.41.27.png', 'commu/0277a'),
    # 4話 l.572: 心「大丈夫大丈夫☆...はぁとが尻込みしてただけ...」 直前:commu/0299 → 0299a
    (r'ダンシング・デッド_00.44.28.png', 'commu/0299a'),
    # 4話 l.576: 心「そうそう！ てなわけで帰るんだけど...」 直前:commu/0303 → 0303a
    (r'ダンシング・デッド_00.45.06.png', 'commu/0303a'),
    # 5話 l.599: 心「あっ、メンゴメンゴ☆ 今行くー☆」 直前:commu/0294 → 0294a
    (r'ダンシング・デッド_00.48.01.png', 'commu/0294a'),
    # 5話 l.602: 女子学生「......今からでも、できるかな。」 直前:0294a → 0294b
    (r'ダンシング・デッド_00.48.27.png', 'commu/0294b'),
    # 5話 l.647: 心「そっか......。きらりちゃん、カッコいいじゃん。」 直前:commu/0358 → 0358a
    (r'ダンシング・デッド_00.53.08.png', 'commu/0358a'),
    # 5話 l.648: 心「......はぁとは...焦るんだよね。」 直前:0358a → 0358b
    (r'ダンシング・デッド_00.53.16.png', 'commu/0358b'),
    # 5話 l.657: 雫「そうですかー？ ふふ...」 直前:commu/0368 → 0368a
    (r'ダンシング・デッド_00.54.55.png', 'commu/0368a'),
    # 5話 l.668: 雫「や......やりましたぁ～～～！」 直前:commu/0379 → 0379a
    (r'ダンシング・デッド_00.56.28.png', 'commu/0379a'),
    # 5話 l.680: 心「そっかそっか。本番、楽しみにしてるぞ☆」 直前:commu/0396 → 0396a
    (r'ダンシング・デッド_00.59.17.png', 'commu/0396a'),
    # ED l.716: オシャレ好きな学生「そうそう！...」 直前:commu/0375 → 0375a
    (r'ダンシング・デッド_01.01.05.png', 'commu/0375a'),
    # ED l.720: P「はい。...『Fav+rica』に仕事のオファーを...」 直前:commu/0415 → 0415a
    (r'ダンシング・デッド_01.01.28.png', 'commu/0415a'),
    # ED l.722: 梨沙「またあの3人にお仕事？...」 直前:0415a → 0415b
    (r'ダンシング・デッド_01.01.45.png', 'commu/0415b'),
    # ED l.729: P「（3人の尖った個性は...）」 直前:commu/0424 → 0424a
    (r'ダンシング・デッド_01.02.33.png', 'commu/0424a'),
]

results = {}
errors = []

def upload_one(filename, pid, ev_folder):
    path = os.path.join(BASE, filename)
    if not os.path.exists(path):
        print(f"  SKIP (not found): {filename}")
        errors.append(f"NOT FOUND: {filename}")
        return None
    public_id = f'{ev_folder}/{pid}'
    print(f"  {filename} -> {pid} ...", end=' ', flush=True)
    try:
        r = up.upload(path, public_id=public_id, overwrite=True)
        url = r['secure_url']
        results[public_id] = url
        print("OK")
        return url
    except Exception as e:
        print(f"ERROR: {e}")
        errors.append(f"ERROR: {filename} -> {e}")
        return None

print("=== CoCo夏夏夏 Holiday ===")
for fname, pid in coco_uploads:
    upload_one(fname, pid, EV_COCO)
    time.sleep(0.3)

print()
print("=== ダンシング・デッド ===")
for fname, pid in dd_uploads:
    upload_one(fname, pid, EV_DD)
    time.sleep(0.3)

# 結果保存
out_path = r'C:\Users\sawas\Desktop\SugarHeartDB\scripts\_cld_map_CoCo_DancingDead.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=1, ensure_ascii=False)
print(f"\nSaved {len(results)} entries to {out_path}")
if errors:
    print(f"\nErrors ({len(errors)}):")
    for e in errors:
        print(f"  {e}")
