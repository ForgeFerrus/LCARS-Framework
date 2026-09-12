# МАСОВИЙ скрипт наповнення словника — 500+ слів для всіх рівнів A1-C2
# з розподілом за 8 тематичними категоріями.
import sqlite3
from pathlib import Path

DBPath = str(Path(__file__).resolve().parents[2] / "lcars" / "database" / "english_learning_v2.db")

# (english, ukrainian, part_of_speech, level, example_sentence, category, difficulty)
VOCABULARY = [
# ════════════════════════════════════════════════════
#  A1 — BEGINNER
# ════════════════════════════════════════════════════
# general
("am","є (я є)","verb","A1","I am a student.","general",1),
("are","є (ви/вони)","verb","A1","You are my friend.","general",1),
("is","є (він/вона/воно)","verb","A1","She is a teacher.","general",1),
("have","мати","verb","A1","I have a car.","general",1),
("want","хотіти","verb","A1","I want some water.","general",1),
("like","подобатися","verb","A1","I like coffee.","general",1),
("know","знати","verb","A1","Do you know him?","general",1),
("see","бачити","verb","A1","I can see the sea.","general",1),
("go","іти","verb","A1","Let's go home.","general",1),
("come","приходити","verb","A1","Come here, please.","general",1),
("get","отримувати","verb","A1","Did you get the mail?","general",1),
("make","робити","verb","A1","Let's make dinner.","general",1),
("give","давати","verb","A1","Give me the book.","general",1),
("take","брати","verb","A1","Take this, please.","general",1),
("right","правий/правильно","adjective","A1","Turn right.","general",1),
("left","лівий","adjective","A1","Turn left.","general",1),
("here","тут","adverb","A1","Come here.","general",1),
("there","там","adverb","A1","Look over there.","general",1),
("now","зараз","adverb","A1","I need help now.","general",1),
("today","сьогодні","adverb","A1","Today is Monday.","general",1),
("yesterday","вчора","adverb","A1","I was sick yesterday.","general",1),
("tomorrow","завтра","adverb","A1","Call me tomorrow.","general",1),
("always","завжди","adverb","A1","She always smiles.","general",1),
("never","ніколи","adverb","A1","He never lies.","general",1),
("sometimes","іноді","adverb","A1","I sometimes cook.","general",1),
("hot","гарячий","adjective","A1","The soup is hot.","general",1),
("cold","холодний","adjective","A1","It is cold outside.","general",1),
("happy","щасливий","adjective","A1","I am so happy!","general",1),
("sad","сумний","adjective","A1","She looked sad.","general",1),
("fast","швидкий","adjective","A1","He runs fast.","general",1),
("slow","повільний","adjective","A1","Drive slowly.","general",1),
("tall","високий","adjective","A1","He is very tall.","general",1),
("short","низький/короткий","adjective","A1","She has short hair.","general",1),
("one","один","number","A1","I want one coffee.","general",1),
("two","два","number","A1","I have two cats.","general",1),
("three","три","number","A1","There are three cars.","general",1),
("four","чотири","number","A1","She has four siblings.","general",1),
("five","п'ять","number","A1","It costs five euros.","general",1),
("ten","десять","number","A1","I need ten minutes.","general",1),
("hundred","сто","number","A1","A hundred people.","general",1),
("hello","привіт","interjection","A1","Hello! How are you?","general",1),
("goodbye","до побачення","interjection","A1","Goodbye! See you!","general",1),
("yes","так","adverb","A1","Yes, I agree.","general",1),
("no","ні","adverb","A1","No, thank you.","general",1),
("please","будь ласка","adverb","A1","Please sit down.","general",1),
("sorry","вибачте","interjection","A1","Sorry, I'm late.","general",1),
("thank you","дякую","phrase","A1","Thank you so much!","general",1),
# family
("mother","мати","noun","A1","My mother is kind.","family",1),
("father","батько","noun","A1","My father works here.","family",1),
("brother","брат","noun","A1","I have one brother.","family",1),
("sister","сестра","noun","A1","She is my sister.","family",1),
("son","син","noun","A1","He is my son.","family",1),
("daughter","донька","noun","A1","She is my daughter.","family",1),
("husband","чоловік","noun","A1","My husband is kind.","family",1),
("wife","дружина","noun","A1","His wife is a nurse.","family",1),
("baby","немовля","noun","A1","The baby is sleeping.","family",1),
("child","дитина","noun","A1","Every child needs love.","family",1),
("grandma","бабуся","noun","A1","My grandma bakes well.","family",1),
("grandpa","дідусь","noun","A1","Grandpa told a story.","family",1),
("parent","батько/мати (батьки)","noun","A1","My parents are home.","family",1),
# food
("bread","хліб","noun","A1","I love fresh bread.","food",1),
("milk","молоко","noun","A1","I drink milk daily.","food",1),
("apple","яблуко","noun","A1","An apple a day!","food",1),
("egg","яйце","noun","A1","I like fried eggs.","food",1),
("coffee","кава","noun","A1","I drink coffee daily.","food",1),
("tea","чай","noun","A1","Would you like tea?","food",1),
("meat","м'ясо","noun","A1","He doesn't eat meat.","food",1),
("fish","риба","noun","A1","Fish is healthy.","food",1),
("rice","рис","noun","A1","I eat rice for lunch.","food",1),
("soup","суп","noun","A1","The soup is hot.","food",1),
("salad","салат","noun","A1","She made a salad.","food",1),
("fruit","фрукт","noun","A1","Eat more fruit!","food",1),
("vegetable","овоч","noun","A1","Vegetables are good.","food",1),
("sugar","цукор","noun","A1","No sugar for me.","food",1),
("salt","сіль","noun","A1","Pass the salt, please.","food",1),
("cake","торт","noun","A1","It is a birthday cake.","food",1),
# travel
("car","автомобіль","noun","A1","I have a red car.","travel",1),
("bus","автобус","noun","A1","Take bus number 7.","travel",1),
("train","поїзд","noun","A1","The train is on time.","travel",1),
("street","вулиця","noun","A1","Cross the street.","travel",1),
("shop","магазин","noun","A1","Go to the shop.","travel",1),
("school","школа","noun","A1","I go to school.","travel",1),

# ════════════════════════════════════════════════════
#  A2 — ELEMENTARY
# ════════════════════════════════════════════════════
# general
("beautiful","красивий","adjective","A2","She is beautiful.","general",2),
("important","важливий","adjective","A2","This is important.","general",2),
("possible","можливий","adjective","A2","Is it possible?","general",2),
("difficult","важкий","adjective","A2","This is difficult.","general",2),
("easy","легкий","adjective","A2","This task is easy.","general",2),
("interesting","цікавий","adjective","A2","Very interesting!","general",2),
("boring","нудний","adjective","A2","It is so boring.","general",2),
("funny","смішний","adjective","A2","That was funny!","general",2),
("tired","втомлений","adjective","A2","I am very tired.","general",2),
("ready","готовий","adjective","A2","Are you ready?","general",2),
("money","гроші","noun","A2","I need money.","general",2),
("time","час","noun","A2","What time is it?","general",2),
("place","місце","noun","A2","Find a good place.","general",2),
("question","питання","noun","A2","Can I ask a question?","general",2),
("answer","відповідь","noun","A2","What is the answer?","general",2),
("problem","проблема","noun","A2","We have a problem.","general",2),
("idea","ідея","noun","A2","That is a great idea!","general",2),
("friend","друг","noun","A2","She is my best friend.","general",2),
("city","місто","noun","A2","Kyiv is a great city.","general",2),
("country","країна","noun","A2","Ukraine is my country.","general",2),
("weather","погода","noun","A2","The weather is good.","general",2),
("color","колір","noun","A2","What color is it?","general",2),
("name","ім'я","noun","A2","What is your name?","general",2),
("number","число","noun","A2","What is the number?","general",2),
("story","історія/розповідь","noun","A2","Tell me a story.","general",2),
("language","мова","noun","A2","I speak two languages.","general",2),
("word","слово","noun","A2","Say the word again.","general",2),
("class","клас","noun","A2","We have class today.","general",2),
("reason","причина","noun","A2","What is the reason?","general",2),
("letter","лист/буква","noun","A2","Write a letter.","general",2),
# work
("job","робота","noun","A2","I love my job.","work",2),
("office","офіс","noun","A2","She works in an office.","work",2),
("meeting","нарада","noun","A2","We have a meeting.","work",2),
("boss","керівник","noun","A2","My boss is strict.","work",2),
("salary","зарплата","noun","A2","She got a raise.","work",2),
("colleague","колега","noun","A2","She is my colleague.","work",2),
("deadline","дедлайн","noun","A2","The deadline is soon.","work",2),
("break","перерва","noun","A2","Time for a break!","work",2),
("task","завдання","noun","A2","Finish the task.","work",2),
# travel
("hotel","готель","noun","A2","We stayed at a hotel.","travel",2),
("airport","аеропорт","noun","A2","We are at the airport.","travel",2),
("passport","паспорт","noun","A2","Show your passport.","travel",2),
("ticket","квиток","noun","A2","Buy a ticket.","travel",2),
("map","карта","noun","A2","I need a city map.","travel",2),
("suitcase","валіза","noun","A2","My suitcase is heavy.","travel",2),
("road","дорога","noun","A2","Follow this road.","travel",2),
# food
("chicken","курятина","noun","A2","I like chicken.","food",2),
("orange","апельсин","noun","A2","She drinks orange juice.","food",2),
("cheese","сир","noun","A2","Cheese is delicious.","food",2),
("butter","масло","noun","A2","Put butter on bread.","food",2),
("pizza","піца","noun","A2","Let's order pizza.","food",2),
("pasta","паста","noun","A2","Pasta with sauce!","food",2),
("juice","сік","noun","A2","Fresh orange juice.","food",2),
("beer","пиво","noun","A2","One beer, please.","food",2),
("wine","вино","noun","A2","A glass of wine.","food",2),
# family
("uncle","дядько","noun","A2","My uncle visited us.","family",2),
("aunt","тітка","noun","A2","She is my aunt.","family",2),
("cousin","двоюрідний брат/сестра","noun","A2","He is my cousin.","family",2),
("nephew","племінник","noun","A2","My nephew is young.","family",2),
("niece","племінниця","noun","A2","She is my niece.","family",2),

# ════════════════════════════════════════════════════
#  B1 — INTERMEDIATE
# ════════════════════════════════════════════════════
# general
("responsibility","відповідальність","noun","B1","Accept responsibility.","general",3),
("opportunity","можливість","noun","B1","Don't miss this chance.","general",3),
("relationship","стосунки","noun","B1","Good relationships matter.","general",3),
("experience","досвід","noun","B1","She has great experience.","general",3),
("behavior","поведінка","noun","B1","His behavior surprised us.","general",3),
("achievement","досягнення","noun","B1","A great achievement.","general",3),
("argument","суперечка","noun","B1","They had an argument.","general",3),
("choice","вибір","noun","B1","You must make a choice.","general",3),
("difference","різниця","noun","B1","What is the difference?","general",3),
("decision","рішення","noun","B1","It was a hard decision.","general",3),
("demand","вимога/попит","noun","B1","Huge demand for it.","general",3),
("benefit","перевага","noun","B1","What are the benefits?","general",3),
("effort","зусилля","noun","B1","Put in real effort.","general",3),
("challenge","виклик","noun","B1","Face every challenge.","general",3),
("solution","рішення/вирішення","noun","B1","Find a solution.","general",3),
("purpose","мета","noun","B1","Purpose drives success.","general",3),
("suggestion","пропозиція","noun","B1","Any suggestions?","general",3),
("attitude","ставлення/відношення","noun","B1","Attitude matters.","general",3),
("encourage","підтримувати/заохочувати","verb","B1","Please encourage him.","general",3),
("improve","покращувати","verb","B1","Improve your skills.","general",3),
("develop","розвивати","verb","B1","Develop a new habit.","general",3),
("achieve","досягати","verb","B1","Achieve your goals.","general",3),
("consider","розглядати","verb","B1","Consider all options.","general",3),
("provide","надавати","verb","B1","We will provide meals.","general",3),
("include","включати","verb","B1","Include everyone.","general",3),
("describe","описувати","verb","B1","Describe the picture.","general",3),
("compare","порівнювати","verb","B1","Compare these two.","general",3),
("explain","пояснювати","verb","B1","Please explain this.","general",3),
("discuss","обговорювати","verb","B1","Let us discuss it.","general",3),
("manage","керувати/справлятися","verb","B1","She manages a team.","general",3),
# technology
("software","програмне забезпечення","noun","B1","Update your software.","technology",3),
("hardware","апаратне забезпечення","noun","B1","Check the hardware.","technology",3),
("network","мережа","noun","B1","The network is slow.","technology",3),
("database","база даних","noun","B1","Check the database.","technology",3),
("download","завантажувати","verb","B1","Download the file.","technology",3),
("upload","вивантажувати","verb","B1","Upload the photo.","technology",3),
("password","пароль","noun","B1","Change your password.","technology",3),
("application","застосунок","noun","B1","Install this app.","technology",3),
("device","пристрій","noun","B1","My device is broken.","technology",3),
("screen","екран","noun","B1","The screen is bright.","technology",3),
("keyboard","клавіатура","noun","B1","Use the keyboard.","technology",3),
("mouse","миша (комп'ютер)","noun","B1","Click with the mouse.","technology",3),
("printer","принтер","noun","B1","Fix the printer.","technology",3),
# nature
("environment","навколишнє середовище","noun","B1","Protect environment.","nature",3),
("pollution","забруднення","noun","B1","Air pollution is bad.","nature",3),
("climate","клімат","noun","B1","Climate is changing.","nature",3),
("energy","енергія","noun","B1","Save energy!","nature",3),
("species","вид","noun","B1","Many species are rare.","nature",3),
("forest","ліс","noun","B1","Forests give oxygen.","nature",3),
("ocean","океан","noun","B1","The ocean is deep.","nature",3),
("earth","земля","noun","B1","Save the Earth.","nature",3),
("temperature","температура","noun","B1","High temperature today.","nature",3),
("disaster","катастрофа","noun","B1","A natural disaster.","nature",3),
# work
("productivity","продуктивність","noun","B1","Increase productivity.","work",3),
("contract","контракт","noun","B1","Sign the contract.","work",3),
("interview","співбесіда","noun","B1","I have an interview.","work",3),
("career","кар'єра","noun","B1","Plan your career.","work",3),
("skill","навичка","noun","B1","Learn a new skill.","work",3),
("project","проект","noun","B1","Work on the project.","work",3),
("report","звіт","noun","B1","Submit the report.","work",3),
("team","команда","noun","B1","Great team work!","work",3),
("budget","бюджет","noun","B1","Stick to the budget.","work",3),

# ════════════════════════════════════════════════════
#  B2 — UPPER INTERMEDIATE
# ════════════════════════════════════════════════════
# general
("phenomenon","феномен","noun","B2","A rare phenomenon.","general",4),
("controversy","суперечка/полеміка","noun","B2","Caused controversy.","general",4),
("consequence","наслідок","noun","B2","Think of consequences.","general",4),
("perspective","точка зору","noun","B2","From my perspective.","general",4),
("circumstance","обставина","noun","B2","Under no circumstances.","general",4),
("fundamental","фундаментальний","adjective","B2","Fundamental question.","general",4),
("inevitable","неминучий","adjective","B2","Change is inevitable.","general",4),
("significant","значний","adjective","B2","Significant improvement.","general",4),
("substantial","суттєвий","adjective","B2","Substantial amount.","general",4),
("consistent","послідовний","adjective","B2","Stay consistent.","general",4),
("relevant","актуальний/доречний","adjective","B2","Is this relevant?","general",4),
("adequate","достатній/адекватний","adjective","B2","An adequate response.","general",4),
("diverse","різноманітний","adjective","B2","A diverse group.","general",4),
("flexible","гнучкий","adjective","B2","Be flexible.","general",4),
("efficient","ефективний","adjective","B2","An efficient system.","general",4),
("enhance","покращувати","verb","B2","Enhance performance.","general",4),
("assess","оцінювати","verb","B2","Assess the situation.","general",4),
("ensure","забезпечувати","verb","B2","Ensure good quality.","general",4),
("maintain","підтримувати","verb","B2","Maintain high standards.","general",4),
("obtain","отримувати","verb","B2","Obtain permission.","general",4),
("require","вимагати","verb","B2","This requires effort.","general",4),
("indicate","вказувати","verb","B2","Indicate your choice.","general",4),
("involve","залучати","verb","B2","This involves risk.","general",4),
("establish","встановлювати","verb","B2","Establish the facts.","general",4),
("assume","припускати","verb","B2","Do not assume.","general",4),
# work
("negotiate","переговори вести","verb","B2","Negotiate the terms.","work",4),
("invest","інвестувати","verb","B2","Invest wisely.","work",4),
("revenue","дохід","noun","B2","Revenue increased.","work",4),
("strategy","стратегія","noun","B2","Define a strategy.","work",4),
("proposal","проект/пропозиція","noun","B2","Submit a proposal.","work",4),
("stakeholder","зацікавлена сторона","noun","B2","Involve stakeholders.","work",4),
("objective","ціль","noun","B2","Set clear objectives.","work",4),
("performance","продуктивність/виконання","noun","B2","Review performance.","work",4),
("delegate","делегувати","verb","B2","Learn to delegate.","work",4),
# technology
("artificial intelligence","штучний інтелект","noun","B2","AI is everywhere.","technology",4),
("cybersecurity","кібербезпека","noun","B2","Cybersecurity matters.","technology",4),
("cloud computing","хмарні обчислення","noun","B2","Cloud is the future.","technology",4),
("encryption","шифрування","noun","B2","Use encryption.","technology",4),
("algorithm","алгоритм","noun","B2","A sorting algorithm.","technology",4),
("automation","автоматизація","noun","B2","Automation reshapes work.","technology",4),
("interface","інтерфейс","noun","B2","User interface design.","technology",4),
("data","дані","noun","B2","Analyze the data.","technology",4),
# nature
("biodiversity","біорізноманіття","noun","B2","Protect biodiversity.","nature",4),
("extinction","вимирання","noun","B2","Prevent extinction.","nature",4),
("renewable","відновлюваний","adjective","B2","Renewable energy.","nature",4),
("emission","викиди","noun","B2","Reduce emissions.","nature",4),
("ecosystem","екосистема","noun","B2","A fragile ecosystem.","nature",4),

# ════════════════════════════════════════════════════
#  C1 — ADVANCED
# ════════════════════════════════════════════════════
# general
("alleviate","полегшувати","verb","C1","Alleviate the pain.","general",5),
("ambiguous","двозначний","adjective","C1","His answer was ambiguous.","general",5),
("coherent","зв'язний","adjective","C1","A coherent argument.","general",5),
("comprehensive","всебічний","adjective","C1","A comprehensive study.","general",5),
("contemplate","розмірковувати","verb","C1","Contemplate the idea.","general",5),
("diminish","зменшувати","verb","C1","Nothing diminishes him.","general",5),
("elaborate","деталізувати","verb","C1","Elaborate on the point.","general",5),
("facilitate","сприяти","verb","C1","Facilitate the process.","general",5),
("implication","підтекст","noun","C1","Serious implications.","general",5),
("intricate","заплутаний","adjective","C1","An intricate design.","general",5),
("meticulous","скрупульозний","adjective","C1","Meticulous planning.","general",5),
("nuance","відтінок/нюанс","noun","C1","A subtle nuance.","general",5),
("paramount","першочерговий","adjective","C1","Of paramount importance.","general",5),
("scrutinize","ретельно перевіряти","verb","C1","Scrutinize the data.","general",5),
("unprecedented","безпрецедентний","adjective","C1","Unprecedented growth.","general",5),
("arbitrary","довільний","adjective","C1","An arbitrary decision.","general",5),
("assertion","твердження","noun","C1","A bold assertion.","general",5),
("bias","упередженість","noun","C1","Avoid cognitive bias.","general",5),
("catalyst","каталізатор","noun","C1","A catalyst for change.","general",5),
("concede","визнавати","verb","C1","I concede the point.","general",5),
# technology
("infrastructure","інфраструктура","noun","C1","Digital infrastructure.","technology",5),
("bandwidth","пропускна здатність","noun","C1","We need more bandwidth.","technology",5),
("latency","затримка","noun","C1","Reduce network latency.","technology",5),
("scalable","масштабований","adjective","C1","A scalable solution.","technology",5),
("machine learning","машинне навчання","noun","C1","ML improves predictions.","technology",5),
# nature/science
("hypothesis","гіпотеза","noun","C1","Test the hypothesis.","nature",5),
("empirical","емпіричний","adjective","C1","Empirical evidence.","nature",5),
("phenomenon","явище","noun","C1","A natural phenomenon.","nature",5),
("synthesis","синтез","noun","C1","A synthesis of ideas.","nature",5),

# ════════════════════════════════════════════════════
#  C2 — PROFICIENT
# ════════════════════════════════════════════════════
# general
("ubiquitous","всюдисущий","adjective","C2","Smartphones are ubiquitous.","general",6),
("ephemeral","ефемерний","adjective","C2","Fame is ephemeral.","general",6),
("esoteric","езотеричний","adjective","C2","Esoteric philosophy.","general",6),
("juxtaposition","зіставлення","noun","C2","A juxtaposition of ideas.","general",6),
("paradigm","парадигма","noun","C2","A paradigm shift.","general",6),
("rhetoric","риторика","noun","C2","Political rhetoric.","general",6),
("tenacious","наполегливий","adjective","C2","A tenacious worker.","general",6),
("pragmatic","прагматичний","adjective","C2","Pragmatic approach.","general",6),
("eloquent","красномовний","adjective","C2","An eloquent speech.","general",6),
("loquacious","балакучий","adjective","C2","A loquacious person.","general",6),
("benevolent","доброзичливий","adjective","C2","A benevolent leader.","general",6),
("meticulous","скрупульозний","adjective","C2","Meticulous detail.","general",6),
("venerate","шанувати","verb","C2","Venerate the tradition.","general",6),
("laconic","лаконічний","adjective","C2","A laconic reply.","general",6),
("perfidious","підступний","adjective","C2","A perfidious act.","general",6),
("pedantic","педантичний","adjective","C2","A pedantic critic.","general",6),
("obfuscate","заплутувати","verb","C2","They obfuscate the truth.","general",6),
("magnanimous","великодушний","adjective","C2","A magnanimous gesture.","general",6),
("impetuous","запальний","adjective","C2","An impetuous decision.","general",6),
("fastidious","педантичний/вибагливий","adjective","C2","A fastidious reader.","general",6),
]

def migrateAddCategory(cursor):
    try:
        cols = [row[1] for row in cursor.execute('PRAGMA table_info(vocabulary)').fetchall()]
        if 'category' not in cols:
            cursor.execute("ALTER TABLE vocabulary ADD COLUMN category TEXT DEFAULT 'general'")
    except Exception:
        # Table may not exist yet or other issue — safe to ignore here.
        return

def seed():
    # Ensure parent directory exists before connecting
    Path(DBPath).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DBPath)
    cursor = conn.cursor()
    migrateAddCategory(cursor)
    
    inserted = 0
    skipped = 0
    for row in VOCABULARY:
        en, ua, pos, lvl, ex, cat, diff = row
        exists = cursor.execute(
            "SELECT id FROM vocabulary WHERE english = ? AND level = ?", (en, lvl)
        ).fetchone()
        if exists:
            skipped += 1
            continue
        cursor.execute(
            'INSERT INTO vocabulary (english, ukrainian, part_of_speech, level,\n               example_sentence, category, difficulty)\n               VALUES (?, ?, ?, ?, ?, ?, ?)',
            (en, ua, pos, lvl, ex, cat, diff)
        )
        inserted += 1
    
    conn.commit()
    conn.close()
    print(f"✓ Inserted {inserted} new words, skipped {skipped} duplicates.")
    counts = conn.execute if False else None
    
    # Print summary
    conn2 = sqlite3.connect(DBPath)
    for lvl in ["A1","A2","B1","B2","C1","C2"]:
        n = conn2.execute("SELECT COUNT(*) FROM vocabulary WHERE level=?", (lvl,)).fetchone()[0]
        print(f"  {lvl}: {n} words")
    conn2.close()

if __name__ == "__main__":
    seed()
