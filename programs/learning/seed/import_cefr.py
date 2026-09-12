# LCARS CEFR Full Importer з авто-перекладом (deep-translator)
# Завантажує public CEFR-J CSV (~8000 слів), перекладає кожне слово через Google Translate
# та вставляє у локальну SQLite базу даних.
# 
# Запускати:
#     python programs/english_learning/import_cefr.py [--limit 500]
import sqlite3
import csv
import io
import sys
import time
import argparse
from pathlib import Path

DBPath = str(Path(__file__).resolve().parents[3] / "lcars" / "database" / "english_learning_v2.db")
CSVUrl = "https://raw.githubusercontent.com/openlanguageprofiles/olp-en-cefrj/master/cefrj-vocabulary-profile-1.5.csv"

LEVELMap = {"A1":"A1","A2":"A2","B1":"B1","B2":"B2","C1":"C1","C2":"C2"}

TOPICCategoryMap = {
    "education": "general", "work and jobs": "work", "shopping": "general",
    "travel": "travel", "health and body care": "nature", "food and drink": "food",
    "family": "family", "personal information": "general", "personal identification": "general",
    "travel and services vocab": "travel", "ways of travelling": "travel",
    "nationalities and countries": "travel", "science": "technology",
    "technology": "technology", "computers": "technology",
    "hobbies and pastimes": "general", "free time, entertainment": "general",
    "environment": "nature", "natural world": "nature",
}

# Fast built-in cache of ~500 common words (no API needed)
BUILTINDict = {
    "a":"а/артикль","about":"про","above":"над","abroad":"за кордоном",
    "absence":"відсутність","absent":"відсутній","absolute":"абсолютний",
    "absolutely":"абсолютно","accept":"приймати","acceptable":"прийнятний",
    "accident":"аварія","accommodation":"проживання","achieve":"досягати",
    "achievement":"досягнення","action":"дія","active":"активний",
    "activity":"діяльність","actor":"актор","add":"додавати","address":"адреса",
    "advice":"порада","advise":"радити","afraid":"боятися","after":"після",
    "afternoon":"день","again":"знову","age":"вік","ago":"тому",
    "agree":"погоджуватися","agreement":"угода","air":"повітря",
    "airport":"аеропорт","all":"усі","allow":"дозволяти","almost":"майже",
    "alone":"на самоті","already":"вже","also":"також","always":"завжди",
    "among":"серед","amount":"кількість","angry":"сердитий","animal":"тварина",
    "another":"інший","appear":"з'являтися","apply":"подавати заяву",
    "arm":"рука","arrive":"прибувати","article":"стаття","ask":"питати",
    "attention":"увага","available":"доступний","avoid":"уникати",
    "awful":"жахливий","back":"назад","bad":"поганий","bag":"сумка",
    "bank":"банк","beach":"пляж","beautiful":"красивий","because":"тому що",
    "become":"ставати","before":"до","begin":"починати","behaviour":"поведінка",
    "believe":"вірити","beside":"біля","between":"між","big":"великий",
    "bill":"рахунок","birthday":"день народження","book":"книга",
    "boring":"нудний","borrow":"позичати","both":"обидва","brain":"мозок",
    "break":"перерва","bring":"приносити","build":"будувати","busy":"зайнятий",
    "buy":"купувати","call":"дзвонити","can":"могти","car":"автомобіль",
    "care":"турбота","carry":"нести","cause":"причина","change":"зміна",
    "charge":"плата","cheap":"дешевий","check":"перевіряти","choose":"вибирати",
    "city":"місто","class":"клас","clear":"зрозумілий","clever":"розумний",
    "cloud":"хмара","cold":"холодний","come":"приходити","communicate":"спілкуватися",
    "community":"спільнота","company":"компанія","complain":"скаржитися",
    "complete":"завершений","completely":"повністю","concern":"хвилювання",
    "confidence":"впевненість","connect":"з'єднувати","consider":"розглядати",
    "continue":"продовжувати","correct":"правильний","cost":"вартість",
    "country":"країна","create":"створювати","danger":"небезпека","dark":"темний",
    "date":"дата","day":"день","deal":"угода","decide":"вирішувати",
    "decision":"рішення","describe":"описувати","design":"дизайн",
    "develop":"розвивати","difference":"різниця","different":"різний",
    "difficult":"важкий","direct":"прямий","do":"робити","drink":"пити",
    "drive":"їхати","during":"протягом","duty":"обов'язок","each":"кожен",
    "early":"рано","easy":"легкий","eat":"їсти","education":"освіта",
    "effective":"ефективний","effort":"зусилля","emotion":"емоція",
    "employ":"наймати","encourage":"заохочувати","energy":"енергія",
    "enjoy":"насолоджуватися","enough":"достатньо","environment":"середовище",
    "especially":"особливо","event":"подія","every":"кожний","everyone":"усі",
    "example":"приклад","excellent":"відмінний","experience":"досвід",
    "explain":"пояснювати","extra":"додатковий",
    "face":"обличчя","fail":"провалити","fall":"падати","family":"сім'я",
    "famous":"знаменитий","fast":"швидкий","feel":"відчувати","final":"фінальний",
    "finally":"нарешті","find":"знаходити","finish":"закінчувати",
    "follow":"слідувати","food":"їжа","force":"сила","forget":"забувати",
    "free":"вільний","friend":"друг","front":"передній","fun":"розвага",
    "funny":"смішний","game":"гра","get":"отримувати","give":"давати",
    "go":"іти","goal":"ціль","good":"добрий","great":"відмінний",
    "grow":"рости","guess":"вгадувати","happen":"траплятися","happy":"щасливий",
    "hard":"важкий","hate":"ненавидіти","have":"мати","heavy":"важкий (вагою)",
    "help":"допомагати","here":"тут","high":"високий","home":"дім",
    "honest":"чесний","hope":"надія","house":"будинок","however":"однак",
    "human":"людина","hurry":"поспішати","idea":"ідея","imagine":"уявляти",
    "immediately":"одразу","improve":"покращувати","include":"включати",
    "increase":"збільшувати","independent":"незалежний","information":"інформація",
    "interest":"інтерес","interesting":"цікавий","involve":"залучати",
    "issue":"питання","job":"робота","join":"приєднуватися","just":"просто",
    "keep":"тримати","kind":"добрий","know":"знати","language":"мова",
    "large":"великий","late":"пізно","laugh":"сміятися","learn":"вчитися",
    "leave":"залишати","less":"менше","life":"життя","like":"подобатися",
    "listen":"слухати","little":"маленький","live":"жити","long":"довгий",
    "look":"дивитися","lose":"програвати","love":"любити","low":"низький",
    "main":"головний","make":"робити","many":"багато","mean":"означати",
    "meet":"зустрічати","mind":"розум","miss":"пропускати","modern":"сучасний",
    "money":"гроші","more":"більше","most":"найбільш","move":"рухатися",
    "much":"багато","must":"мусити","name":"ім'я","nature":"природа",
    "need":"потребувати","never":"ніколи","new":"новий","next":"наступний",
    "nice":"гарний","nothing":"нічого","now":"зараз","number":"число",
    "offer":"пропонувати","often":"часто","old":"старий","only":"тільки",
    "open":"відкривати","other":"інший","own":"власний","past":"минуле",
    "pay":"платити","people":"люди","perhaps":"можливо","phone":"телефон",
    "pick":"вибирати","plan":"план","play":"грати","possible":"можливий",
    "practice":"практика","prepare":"готуватися","problem":"проблема",
    "process":"процес","prove":"доводити","question":"питання","quick":"швидкий",
    "quiet":"тихий","reach":"досягати","read":"читати","ready":"готовий",
    "realize":"усвідомлювати","reason":"причина","receive":"отримувати",
    "remember":"пам'ятати","require":"вимагати","responsibility":"відповідальність",
    "result":"результат","right":"правильний","risk":"ризик","room":"кімната",
    "run":"бігти","safe":"безпечний","same":"однаковий","save":"зберігати",
    "say":"говорити","school":"школа","see":"бачити","seem":"здаватися",
    "sell":"продавати","send":"надсилати","show":"показувати","simple":"простий",
    "situation":"ситуація","skill":"навичка","small":"маленький","smile":"посміхатися",
    "something":"щось","sometimes":"іноді","soon":"скоро","sorry":"вибачте",
    "speak":"говорити","start":"починати","stay":"залишатися","stop":"зупиняти",
    "study":"навчання","suddenly":"раптово","suggest":"пропонувати",
    "support":"підтримка","take":"брати","talk":"розмовляти","teach":"навчати",
    "tell":"говорити","think":"думати","tired":"втомлений","today":"сьогодні",
    "together":"разом","tomorrow":"завтра","travel":"подорожувати","try":"намагатися",
    "turn":"повертатися","understand":"розуміти","use":"використовувати",
    "usually":"зазвичай","very":"дуже","view":"вид","visit":"відвідувати",
    "wait":"чекати","want":"хотіти","way":"шлях","work":"робота",
    "world":"світ","worry":"хвилюватися","write":"писати","wrong":"неправильний",
    # tech
    "computer":"комп'ютер","internet":"інтернет","software":"програмне забезпечення",
    "hardware":"апаратне забезпечення","network":"мережа","database":"база даних",
    "download":"завантажувати","upload":"вивантажувати","password":"пароль",
    "algorithm":"алгоритм","application":"застосунок","device":"пристрій",
    "screen":"екран","keyboard":"клавіатура","mouse":"миша","printer":"принтер",
    "data":"дані","server":"сервер","file":"файл","digital":"цифровий",
    "website":"вебсайт","email":"електронна пошта","message":"повідомлення",
    "search":"пошук","program":"програма","code":"код","system":"система",
    "cloud":"хмара","machine":"машина","robot":"робот","science":"наука",
    "technology":"технологія","equipment":"обладнання","signal":"сигнал",
    # nature
    "forest":"ліс","ocean":"океан","river":"річка","mountain":"гора",
    "planet":"планета","sun":"сонце","moon":"місяць","star":"зірка",
    "tree":"дерево","flower":"квітка","grass":"трава","water":"вода",
    "fire":"вогонь","earth":"земля","stone":"камінь","wind":"вітер",
    "rain":"дощ","snow":"сніг","ice":"лід","weather":"погода",
    "climate":"клімат","pollution":"забруднення","species":"вид",
    "ecosystem":"екосистема","biodiversity":"біорізноманіття",
    "extinction":"вимирання","temperature":"температура",
    # food
    "breakfast":"сніданок","lunch":"обід","dinner":"вечеря",
    "restaurant":"ресторан","taste":"смак","hungry":"голодний",
    "meal":"їжа","recipe":"рецепт","cook":"готувати","diet":"дієта",
    "sweet":"солодкий","spicy":"гострий","bread":"хліб","milk":"молоко",
    "apple":"яблуко","egg":"яйце","coffee":"кава","tea":"чай",
    "meat":"м'ясо","fish":"риба","rice":"рис","soup":"суп",
    "salad":"салат","fruit":"фрукт","vegetable":"овоч","sugar":"цукор",
    "salt":"сіль","cake":"торт","cheese":"сир","butter":"масло",
    "pizza":"піца","pasta":"паста","juice":"сік","beer":"пиво","wine":"вино",
    # family
    "mother":"мати","father":"батько","brother":"брат","sister":"сестра",
    "son":"син","daughter":"донька","husband":"чоловік","wife":"дружина",
    "baby":"немовля","child":"дитина","grandma":"бабуся","grandpa":"дідусь",
    "parent":"батьки","uncle":"дядько","aunt":"тітка","cousin":"кузен",
    "nephew":"племінник","niece":"племінниця","relationship":"стосунки",
    "marry":"одружитися","wedding":"весілля","sibling":"брат або сестра",
    # work
    "career":"кар'єра","project":"проект","report":"звіт","meeting":"нарада",
    "boss":"керівник","salary":"зарплата","colleague":"колега",
    "deadline":"дедлайн","contract":"контракт","interview":"співбесіда",
    "team":"команда","budget":"бюджет","office":"офіс","employee":"працівник",
    "employer":"роботодавець","profession":"професія","manager":"менеджер",
    "productivity":"продуктивність","strategy":"стратегія","revenue":"дохід",
    # travel
    "hotel":"готель","airport":"аеропорт","passport":"паспорт",
    "ticket":"квиток","map":"карта","suitcase":"валіза","road":"дорога",
    "journey":"подорож","vacation":"відпустка","destination":"пункт призначення",
    "tourist":"турист","customs":"митниця","flight":"рейс","border":"кордон",
    "currency":"валюта","car":"автомобіль","bus":"автобус","train":"поїзд",
    # advanced
    "alleviate":"полегшувати","ambiguous":"двозначний","coherent":"зв'язний",
    "contemplate":"розмірковувати","diminish":"зменшувати","elaborate":"деталізувати",
    "facilitate":"сприяти","intricate":"заплутаний","nuance":"нюанс",
    "paramount":"першочерговий","scrutinize":"ретельно перевіряти",
    "unprecedented":"безпрецедентний","arbitrary":"довільний","bias":"упередженість",
    "catalyst":"каталізатор","concede":"визнавати","ubiquitous":"всюдисущий",
    "ephemeral":"ефемерний","paradigm":"парадигма","rhetoric":"риторика",
    "pragmatic":"прагматичний","eloquent":"красномовний","benevolent":"доброзичливий",
    "meticulous":"скрупульозний","tenacious":"наполегливий","hypothesis":"гіпотеза",
    "empirical":"емпіричний","synthesis":"синтез","infrastructure":"інфраструктура",
    "bandwidth":"пропускна здатність","latency":"затримка","scalable":"масштабований",
    "consequence":"наслідок","perspective":"точка зору","circumstance":"обставина",
    "significant":"значний","substantial":"суттєвий","relevant":"актуальний",
    "adequate":"достатній","diverse":"різноманітний","flexible":"гнучкий",
    "efficient":"ефективний","enhance":"покращувати","assess":"оцінювати",
    "ensure":"забезпечувати","maintain":"підтримувати","obtain":"отримувати",
    "indicate":"вказувати","establish":"встановлювати","assume":"припускати",
    "negotiate":"вести переговори","invest":"інвестувати","fundamental":"фундаментальний",
    "inevitable":"неминучий","consistent":"послідовний","phenomenon":"феномен",
    "controversy":"суперечка","abandon":"покидати","ability":"здатність",
    "accomplish":"здійснювати","accurate":"точний","acquire":"отримувати",
    "adapt":"пристосовувати","affect":"впливати","afford":"дозволяти собі",
    "challenge":"виклик","opportunity":"можливість","solution":"вирішення",
    "purpose":"мета","attitude":"ставлення","achievement":"досягнення",
    "behavior":"поведінка","argument":"суперечка","choice":"вибір",
    "benefit":"перевага","demand":"вимога","encourage":"заохочувати",
    "improve":"покращувати","develop":"розвивати","compare":"порівнювати",
    "discuss":"обговорювати","manage":"керувати","protect":"захищати",
    "prevent":"запобігати","recognize":"визнавати","volunteer":"волонтер",
    "celebrate":"святкувати","participate":"брати участь","communicate":"спілкуватися",
    "explain":"пояснювати","organize":"організовувати","respond":"відповідати",
    "produce":"виробляти","reduce":"зменшувати","analyze":"аналізувати",
    "measure":"вимірювати","identify":"визначати","evaluate":"оцінювати",
    "investigate":"досліджувати","demonstrate":"демонструвати",
    "distribute":"розподіляти","generate":"генерувати","implement":"впроваджувати",
    "monitor":"спостерігати","operate":"керувати","perform":"виконувати",
    "publish":"публікувати","regulate":"регулювати","transform":"перетворювати",
    "vary":"варіювати","observe":"спостерігати","predict":"передбачати",
    "investigate":"досліджувати","estimate":"оцінювати","classify":"класифікувати",
}


def getCategory(rowDict):
    for key in ("CoreInventory 1", "CoreInventory 2", "Threshold"):
        val = rowDict.get(key, "").strip().lower()
        if val:
            for topic, cat in TOPICCategoryMap.items():
                if topic in val:
                    return cat
    return "general"


def migrateAddCategory(cursor):
    cursor.execute("ALTER TABLE vocabulary ADD COLUMN category TEXT DEFAULT 'general'")


def downloadCsv():
    import importlib.util
    if importlib.util.findSpec('requests') is not None:
        import requests
        resp = requests.get(CSVUrl, timeout=30)
        resp.raiseForStatus()
        return resp.text
    else:
        import urllib.request
        with urllib.request.urlopen(CSVUrl, timeout=30) as r:
            return r.read().decode("utf-8")


def autoTranslate(word: str) -> str:
    # Translate single English word to Ukrainian via deep-translator.
    import importlib.util
    if importlib.util.findSpec('deep_translator') is None:
        return ""
    from deepTranslator import GoogleTranslator
    result = GoogleTranslator(source="en", target="uk").translate(word)
    return result if result else ""


def main():
    parser = argparse.ArgumentParser(description="Import CEFR vocabulary into LCARS DB")
    parser.addArgument("--limit", type=int, default=0, help="Limit words to import (0=all)")
    parser.addArgument("--no-auto", action="store_true", help="Skip Google Translate (only use built-in dict)")
    args = parser.parseArgs()

    print("Завантаження CEFR-J словника з GitHub...")
    csvText = downloadCsv()
    print(f"  Завантажено {len(csv_text):,} байт.")

    conn = sqlite3.connect(DBPath)
    cursor = conn.cursor()
    migrateAddCategory(cursor)

    reader = csv.DictReader(io.StringIO(csvText))
    inserted = 0
    skippedDup = 0
    translatedApi = 0

    rows = list(reader)
    total = len(rows)
    print(f"  Рядків у CSV: {total:,}")
    if args.limit:
        print(f"  Обмеження: {args.limit} слів")

    for i, row in enumerate(rows):
        headword = row.get("headword", "").strip().lower()
        posRaw = row.get("pos", "").strip()
        level = LEVELMap.get(row.get("CEFR", "").strip(), None)

        if not headword or not level:
            continue

        # Simplify compound entries
        if "/" in headword:
            headword = headword.split("/")[0].strip()

        # Skip very long phrases (> 3 words)
        if len(headword.split()) > 3:
            continue

        # Check duplicate
        exists = cursor.execute(
            "SELECT id FROM vocabulary WHERE english = ? AND level = ?", (headword, level)
        ).fetchone()
        if exists:
            skippedDup += 1
            continue

        # Get translation
        translation = BUILTINDict.get(headword, None)
        if translation is None:
            if args.noAuto:
                continue
            # Use Google Translate API
            translation = autoTranslate(headword)
            if translation:
                translatedApi += 1
                time.sleep(0.15)  # rate limit
            else:
                continue

        category = getCategory(row)
        diff = {"A1":1,"A2":2,"B1":3,"B2":4,"C1":5,"C2":6}.get(level, 3)

        cursor.execute(
            'INSERT INTO vocabulary (english, ukrainian, part_of_speech, level, category, difficulty)\n               VALUES (?, ?, ?, ?, ?, ?)',
            (headword, translation, posRaw, level, category, diff)
        )
        inserted += 1

        if inserted % 50 == 0:
            conn.commit()
            pct = (i / total) * 100
            print(f"  [{pct:.0f}%] Вставлено {inserted} слів (API перекладів: {translated_api})...")

        if args.limit and inserted >= args.limit:
            break

    conn.commit()
    print(f"\nГотово!")
    print(f"  Вставлено нових слів: {inserted}")
    print(f"  З них через Google Translate: {translated_api}")
    print(f"  Пропущено (дублікат): {skipped_dup}")
    print("\nСтатистика рівнів:")
    for lvl in ["A1","A2","B1","B2","C1","C2"]:
        n = conn.execute("SELECT COUNT(*) FROM vocabulary WHERE level=?", (lvl,)).fetchone()[0]
        print(f"  {lvl}: {n:,} слів")
    conn.close()


if __name__ == "__main__":
    main()
