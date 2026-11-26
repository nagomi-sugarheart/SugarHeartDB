"""画像置き場（Cloudflare Pages × GitHubリポジトリ7個）の振り分けルール。

画像のパス（旧Cloudinaryの public_id と同じ。例: "Deresute/Event/GoJustGo/commu/0001a"）から、
置くべきリポジトリと配信URLを決める。新しい画像を追加するときも必ずこのルールに従うこと。

  python scripts/img_hosting.py Deresute/Event/GoJustGo/commu/0001a.jpg
    → repo: sugarheartdb-img-deresute3
      url : https://sugarheartdb-img-deresute3.pages.dev/Deresute/Event/GoJustGo/commu/0001a.jpg
"""
import sys
from urllib.parse import quote

OWNER = "nagomi-sugarheart"

# デレステは更新終了のため、各リポジトリをほぼ満杯（約900MB）まで詰めている。
# 振り分けは「パスの先頭一致」で、上から順に最初に当たったものを使う。
ROUTES = [
    ("Deresute/Event/NextChapter/", "deresute1"),
    ("Deresute/GuestCommu/", "deresute1"),
    ("Deresute/Other/", "deresute1"),
    ("Deresute/Event/DancingDead/", "deresute2"),
    ("Deresute/Event/OdoruFlagship/", "deresute2"),
    ("Deresute/Event/HappyNewYeah/", "deresute2"),
    ("Deresute/Event/GoJustGo/", "deresute3"),
    ("Deresute/Event/NetsujouEnamorar/", "deresute3"),
    ("Deresute/Event/OumuamuaKooun/", "deresute3"),
    ("Deresute/Memorial/", "deresute3"),
    ("Deresute/Event/CoCoNatsuHoliday/", "deresute4"),
    ("Deresute/Event/TakeMeTakeYou/", "deresute4"),
    ("Deresute/Event/DekobokoSpeedStar/", "deresute4"),
    ("Deresute/Derepo/", "deresute4"),
    ("Deresute/Event/SunFlower/", "deresute5"),
    ("Deresute/Event/InochiMoyashiteKoiseyoOtome/", "deresute5"),
    ("Deresute/Event/IdolProduce1st/", "deresute5"),
    ("Deresute/Eigyo/", "deresute5"),
    # 上に当てはまらないデレステ（カード・ストーリーコミュ・他アイドル等）は deresute6。
    # 1〜5がいっぱいのときの追加先もここ。
    ("Deresute/", "deresute6"),
]
# デレステ以外（モバマス・ユニット・劇場・ポプマス・data・Favicon 等）はすべて general。
DEFAULT = "general"

# URLに入れても安全な文字（それ以外は %エンコード）
_SAFE = "/+-_.~!*'()"


def repo_key(path: str) -> str:
    for prefix, key in ROUTES:
        if path.startswith(prefix):
            return key
    return DEFAULT


def repo_name(path: str) -> str:
    return f"sugarheartdb-img-{repo_key(path)}"


def url(path: str) -> str:
    """拡張子付きのパスから配信URLを返す。"""
    return f"https://{repo_name(path)}.pages.dev/{quote(path, safe=_SAFE)}"


if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(f"repo: {repo_name(p)}\nurl : {url(p)}")
