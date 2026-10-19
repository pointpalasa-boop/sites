"""Собирает index.html (страница) и checklist.pdf из одних и тех же данных.
Запуск: python3 build.py   (нужен playwright + chromium)
Свой контакт поменяйте в CONTACT ниже и запустите заново."""
import html, pathlib
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).parent
CONTACT = "@Dim4ik0"
CONTACT_URL = "https://t.me/Dim4ik0"
PAGE_URL = "https://pointpalasa-boop.github.io/sites/proverka-sayta/"

GROUPS = [
    ("Первый экран: 5 секунд", [
        ("Понятно, чем вы занимаетесь", "Заголовок отвечает на вопрос «что это?» без прокрутки и без общих слов вроде «лучшие решения»."),
        ("Видно, для кого сайт", "Есть уточнение: для кого, в каком городе, для какой задачи."),
        ("Есть одна главная кнопка", "Одно заметное действие: «Записаться», «Заказать», «Позвонить». Не пять равных кнопок."),
    ]),
    ("Телефон", [
        ("Текст читается без увеличения", "Основной текст не мельче 16 px. Если приходится щуриться или растягивать пальцами, это провал."),
        ("Кнопки удобно нажимать", "Нажимаемая область не меньше 44 на 44 px, между кнопками есть воздух."),
        ("Телефон и почта кликабельны", "Номер оформлен как ссылка (tel:), по нажатию открывается набор номера."),
    ]),
    ("Читаемость", [
        ("Контраст текста не меньше 4,5\u00a0:\u00a01", "Серый на бежевом выглядит стильно и не читается. Проверьте в WebAIM Contrast Checker."),
        ("Заголовки отличаются от текста", "Размером и весом. Абзацы короткие, не больше 3–4 строк на телефоне."),
        ("Нет горизонтальной прокрутки", "На телефоне страница не уезжает вбок и ничего не обрезано по краю."),
    ]),
    ("Доверие", [
        ("Есть доказательство", "Цифра, отзыв с именем, примеры работ или логотипы клиентов. Что-то, что можно проверить."),
        ("Видна цена или хотя бы «от»", "Если цены нет совсем, часть людей уйдёт, не спросив. Достаточно диапазона или примера расчёта."),
        ("В подвале есть реквизиты", "Название, ИНН или ОГРНИП, адрес или город, способ связи. Это признак живой компании."),
    ]),
    ("Заявка", [
        ("Форма короткая", "Имя и телефон или мессенджер. Каждое лишнее поле снижает число заявок."),
        ("Есть подтверждение после отправки", "Человек видит «Заявка принята, отвечу в течение ...». Иначе нажмёт второй раз или уйдёт."),
        ("Связаться можно не только формой", "Мессенджер или телефон рядом с формой. Не все любят заполнять поля."),
    ]),
]
TOTAL = sum(len(g[1]) for g in GROUPS)
LEVELS = [
    ("13–15", "Хорошая база", "Сайт делает свою работу. Дальше помогают тесты заголовка и кнопки."),
    ("8–12", "Есть что исправить", "Заявки теряются на мелочах. Начните с пунктов первого экрана и телефона: они дают больше всего."),
    ("0–7", "Сайт теряет заявки", "Большинство посетителей уходит, не поняв предложение. Проще пересобрать первый экран, чем латать."),
]

CSS_COMMON = """
:root{--paper:#f0f4fa;--ink:#0e1628;--blue:#2e50ff;--lime:#ffe25c;--mut:#586482;--line:#d5dcec;--card:#fff}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Inter,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;color:var(--ink);background:var(--paper);line-height:1.5}
h1,h2,h3{font-family:"Inter Display",Inter,system-ui,sans-serif;line-height:1.08;letter-spacing:-.02em}
"""


def items_html(interactive):
    out, n = [], 0
    for gi, (gname, items) in enumerate(GROUPS):
        out.append(f'<section class="grp"><h2>{html.escape(gname)}</h2>')
        for title, hint in items:
            n += 1
            if interactive:
                out.append(f'<label class="it"><input type="checkbox" class="chk"><span class="box"></span>'
                           f'<span class="tx"><b>{n}. {html.escape(title)}</b><small>{html.escape(hint)}</small></span></label>')
            else:
                out.append(f'<div class="it"><span class="box"></span>'
                           f'<span class="tx"><b>{n}. {html.escape(title)}</b><small>{html.escape(hint)}</small></span></div>')
        out.append('</section>')
    return "\n".join(out)


def levels_html():
    return "".join(f'<div class="lv"><div class="rg">{r}</div><div><b>{html.escape(t)}</b><p>{html.escape(d)}</p></div></div>'
                   for r, t, d in LEVELS)


# ---------- PDF ----------
PDF_CSS = CSS_COMMON + """
@page{size:A4;margin:0}
.pg{width:210mm;height:297mm;padding:18mm 17mm;position:relative;page-break-after:always;overflow:hidden;background:var(--paper)}
.pg:last-child{page-break-after:auto}
.cover{background:var(--ink);color:#fff;display:flex;flex-direction:column;justify-content:space-between}
.cover h1{font-size:64px;font-weight:900;margin-top:40mm}
.cover h1 span{color:var(--lime)}
.cover p.sub{font-size:18px;color:#b8c2de;margin-top:8mm;max-width:130mm}
.cover .meta{font-size:13px;color:#8e9ac0}
.pill{display:inline-block;background:var(--lime);color:var(--ink);font-weight:800;padding:6px 14px;border-radius:99px;font-size:13px}
h2{font-size:21px;font-weight:800;margin-bottom:8px;color:var(--blue)}
.grp{margin-bottom:14px}
.it{display:flex;gap:12px;align-items:flex-start;padding:9px 12px;background:var(--card);border:1.5px solid var(--line);border-radius:12px;margin-bottom:7px}
.box{flex:none;width:18px;height:18px;border:2px solid var(--ink);border-radius:5px;margin-top:2px}
.tx b{display:block;font-size:13.5px}
.tx small{display:block;font-size:11.5px;color:var(--mut);margin-top:1px}
.ph{font-size:26px;font-weight:900;margin-bottom:12px}
.lv{display:flex;gap:14px;background:var(--card);border:1.5px solid var(--line);border-radius:14px;padding:14px;margin-bottom:10px;align-items:center}
.rg{flex:none;width:74px;text-align:center;font-weight:900;font-size:20px;color:#fff;background:var(--blue);border-radius:10px;padding:10px 0}
.lv p{font-size:12.5px;color:var(--mut)}
.how{background:var(--card);border-radius:14px;border:1.5px solid var(--line);padding:16px;margin:14px 0}
.how ol{padding-left:18px;font-size:12.5px}.how li{margin-bottom:5px}
.cta{background:var(--blue);color:#fff;border-radius:18px;padding:22px;margin-top:14px}
.cta h3{font-size:24px;font-weight:900}.cta p{font-size:13px;margin-top:6px;color:#dde3ff}
.cta .ct{display:inline-block;margin-top:12px;background:var(--lime);color:var(--ink);font-weight:800;padding:8px 16px;border-radius:10px;font-size:15px}
.foot{position:absolute;left:17mm;right:17mm;bottom:10mm;font-size:10px;color:var(--mut);display:flex;justify-content:space-between}
"""

def pdf_html():
    mid = len(GROUPS) // 2 + 1
    def part(a, b):
        sub = GROUPS[a:b]
        out, n = [], sum(len(g[1]) for g in GROUPS[:a])
        for gname, items in sub:
            out.append(f'<section class="grp"><h2>{html.escape(gname)}</h2>')
            for title, hint in items:
                n += 1
                out.append(f'<div class="it"><span class="box"></span><span class="tx"><b>{n}. {html.escape(title)}</b><small>{html.escape(hint)}</small></span></div>')
            out.append('</section>')
        return "\n".join(out)
    return f"""<!doctype html><html lang="ru"><head><meta charset="utf-8"><style>{PDF_CSS}</style></head><body>
<div class="pg cover"><div><span class="pill">Чек-лист · {TOTAL} пунктов</span>
<h1>Проверь свой сайт<br><span>за 10 минут</span></h1>
<p class="sub">Откройте свой сайт на телефоне и отметьте пункты. По итогам станет ясно, где теряются заявки и что чинить первым.</p></div>
<div class="meta">Разработка сайтов · {html.escape(CONTACT)} · pointpalasa-boop.github.io/sites/proverka-sayta</div></div>
<div class="pg"><div class="ph">Отмечайте то, что у вас уже есть</div>{part(0, 3)}<div class="foot"><span>Проверь свой сайт за 10 минут</span><span>2</span></div></div>
<div class="pg"><div class="ph">Продолжаем</div>{part(3, 5)}
<div class="how"><b>Как проверять</b><ol><li>Откройте сайт на телефоне, не на компьютере: так на него приходит большинство людей.</li><li>Первые три пункта проверьте за 5 секунд, не листая.</li><li>Контраст проверьте на webaim.org/resources/contrastchecker (вставьте цвет текста и фона).</li><li>Отмечайте пункт, только если уверены на «да». Сомневаетесь — не отмечайте.</li></ol></div>
<div class="foot"><span>Проверь свой сайт за 10 минут</span><span>3</span></div></div>
<div class="pg"><div class="ph">Ваш результат: сколько пунктов отмечено из {TOTAL}</div>{levels_html()}
<div class="how"><b>С чего начать исправлять</b><ol><li>Сначала первый экран (пункты 1–3): он влияет на все остальные.</li><li>Потом телефон (4–6): большая часть посетителей именно там.</li><li>Контраст и читаемость (7–9) обычно правятся за час.</li><li>Доверие и заявка (10–15) дают рост, когда база уже в порядке.</li></ol></div>
<div class="cta"><h3>Хотите, разберу ваш сайт?</h3><p>Пришлите ссылку и результат чек-листа. Скажу, какие 2–3 правки дадут больше всего.</p><span class="ct">{html.escape(CONTACT)}</span><p style="margin-top:12px">Онлайн-версия: {PAGE_URL}</p></div>
<div class="foot"><span>Проверь свой сайт за 10 минут</span><span>4</span></div></div>
</body></html>"""


# ---------- Страница ----------
PAGE_CSS = CSS_COMMON + """
a{color:inherit}
.wrap{max-width:760px;margin:0 auto;padding:0 20px}
.hero{background:var(--ink);color:#fff;padding:64px 0 56px}
.hero h1{font-size:clamp(40px,9vw,72px);font-weight:900}
.hero h1 span{color:var(--lime)}
.hero p{font-size:19px;color:#b8c2de;margin:18px 0 28px;max-width:560px}
.btn{display:inline-block;background:var(--lime);color:var(--ink);font-weight:800;padding:16px 26px;border-radius:14px;text-decoration:none;font-size:17px;min-height:48px}
.btn:focus-visible,.it:focus-within{outline:3px solid var(--blue);outline-offset:3px}
.tool{padding:48px 0}
.tool>.wrap>h2{font-size:clamp(28px,6vw,40px);font-weight:900;margin-bottom:6px}
.lead{color:var(--mut);margin-bottom:24px}
.grp h2{font-size:18px;font-weight:800;color:var(--blue);margin:22px 0 8px}
.it{display:flex;gap:14px;align-items:flex-start;padding:14px;background:var(--card);border:1.5px solid var(--line);border-radius:14px;margin-bottom:8px;cursor:pointer;min-height:56px}
.chk{position:absolute;opacity:0;pointer-events:none}
.box{flex:none;width:26px;height:26px;border:2.5px solid var(--ink);border-radius:8px;margin-top:1px;display:grid;place-items:center;transition:background .15s}
.chk:checked+.box{background:var(--blue);border-color:var(--blue)}
.chk:checked+.box::after{content:"";width:7px;height:13px;border:solid #fff;border-width:0 3px 3px 0;transform:rotate(45deg) translate(-1px,-1px)}
.tx b{display:block;font-size:16px}.tx small{display:block;color:var(--mut);font-size:14px;margin-top:2px}
.score{position:sticky;bottom:0;background:var(--ink);color:#fff;padding:14px 0;margin-top:24px;z-index:5}
.score .wrap{display:flex;gap:16px;align-items:center}
.n{font-size:32px;font-weight:900;color:var(--lime);white-space:nowrap}
.verdict b{display:block}.verdict span{font-size:14px;color:#b8c2de}
.levels{padding:40px 0}.lv{display:flex;gap:14px;background:var(--card);border:1.5px solid var(--line);border-radius:14px;padding:14px;margin-bottom:10px;align-items:center}
.rg{flex:none;width:76px;text-align:center;font-weight:900;color:#fff;background:var(--blue);border-radius:10px;padding:10px 0}
.lv p{color:var(--mut);font-size:15px}
.cta{background:var(--blue);color:#fff;padding:48px 0 56px}
.cta h2{font-size:clamp(28px,6vw,40px);font-weight:900}.cta p{margin:10px 0 22px;color:#dde3ff}
.note{font-size:13px;color:var(--mut);padding:20px 0 40px}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
"""

def page_html():
    return f"""<!doctype html><html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Проверь свой сайт за 10 минут</title>
<link rel="canonical" href="{PAGE_URL}">
<meta name="description" content="Бесплатный чек-лист из {TOTAL} пунктов: где ваш сайт теряет заявки. Проверка онлайн или PDF.">
<style>{PAGE_CSS}</style></head><body>
<header class="hero"><div class="wrap"><h1>Проверь свой сайт <span>за 10 минут</span></h1>
<p>{TOTAL} вопросов о первом экране, телефоне, читаемости, доверии и заявке. Отметьте, что у вас уже есть, и увидите, где сайт теряет клиентов.</p>
<a class="btn" href="checklist.pdf" download>Скачать PDF</a></div></header>
<main>
<section class="tool"><div class="wrap"><h2>Проверка онлайн</h2>
<p class="lead">Откройте свой сайт на телефоне в соседней вкладке и отмечайте пункты. Ничего не отправляется: подсчёт идёт в вашем браузере.</p>
{items_html(True)}
</div>
<div class="score" role="status" aria-live="polite"><div class="wrap"><div class="n" id="n">0 / {TOTAL}</div>
<div class="verdict"><b id="vt">Начните отмечать пункты</b><span id="vd">Результат появится здесь</span></div></div></div></section>
<section class="levels"><div class="wrap"><h2 style="font-size:26px;font-weight:900;margin-bottom:14px">Что значит результат</h2>{levels_html()}</div></section>
<section class="cta"><div class="wrap"><h2>Хотите, разберу ваш сайт?</h2>
<p>Пришлите ссылку и результат. Скажу, какие 2–3 правки дадут больше всего.</p>
<a class="btn" href="{CONTACT_URL}">{html.escape(CONTACT)}</a></div></section>
<div class="wrap note">Обратная связь и вопросы: <a href="{CONTACT_URL}">{html.escape(CONTACT)}</a>. Пороги (16 px, 44 px, контраст 4,5\u00a0:\u00a01) — общепринятые ориентиры для удобства чтения и нажатий на телефоне. Чек-лист не заменяет полного аудита.</div>
</main>
<script>
var LV={[{"min":13,"t":"Хорошая база","d":"Сайт делает свою работу."},{"min":8,"t":"Есть что исправить","d":"Начните с первого экрана и телефона."},{"min":0,"t":"Сайт теряет заявки","d":"Проще пересобрать первый экран, чем латать."}]!r};
var cs=document.querySelectorAll('.chk'),n=document.getElementById('n'),vt=document.getElementById('vt'),vd=document.getElementById('vd');
function upd(){{var c=0;cs.forEach(function(x){{if(x.checked)c++}});n.textContent=c+' / {TOTAL}';
if(c===0){{vt.textContent='Начните отмечать пункты';vd.textContent='Результат появится здесь';return}}
for(var i=0;i<LV.length;i++){{if(c>=LV[i].min){{vt.textContent=LV[i].t;vd.textContent=LV[i].d;break}}}}}}
cs.forEach(function(x){{x.addEventListener('change',upd)}});
</script></body></html>"""


def main():
    page = page_html()
    (HERE / "index.html").write_text(page, encoding="utf-8")
    (HERE / "_pdf.html").write_text(pdf_html(), encoding="utf-8")
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.goto((HERE / "_pdf.html").as_uri())
        pg.pdf(path=str(HERE / "checklist.pdf"), format="A4", print_background=True, prefer_css_page_size=True)
        b.close()
    (HERE / "_pdf.html").unlink()
    print("ok")


if __name__ == "__main__":
    main()
