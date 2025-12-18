import asyncio
import nest_asyncio
from playwright.async_api import async_playwright

nest_asyncio.apply()

# ==========================================
# 1️⃣ قائمة المسلسلات
# ==========================================
ARABSEED_URLS = [
    {"title": "لا ترد ولا تستبدل", "url": "https://a.asd.homes/?p=828743"},
    {"title": "2 قهوة", "url": "https://a.asd.homes/?p=828618"},
    {"title": "ميدتيرم", "url": "https://a.asd.homes/?p=828728"}
]

# ==========================================
# 2️⃣ كود الشبح (Stealth Scraper) 👻
# ==========================================
async def get_links(url):
    data = {"watch": [], "download": []}
    async with async_playwright() as p:
        # تشغيل المتصفح بخصائص تخفي (عشان يبان حقيقي)
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled', # إخفاء علامة التحكم الآلي
                '--no-sandbox',
                '--disable-setuid-sandbox'
            ]
        )
        # تغيير مواصفات المتصفح ليبدو كـ Chrome عادي
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = await context.new_page()
        
        try:
            print(f"جاري الدخول: {url}")
            await page.goto(url, timeout=90000, wait_until="domcontentloaded")
            await asyncio.sleep(5) # انتظار إضافي للتحميل
            
            # --- محاولة 1: البحث المباشر عن الروابط ---
            # تجميع كل الروابط في الصفحة وفلترتها
            all_links = await page.evaluate('''() => {
                const links = Array.from(document.querySelectorAll('a'));
                return links.map(a => ({
                    text: a.innerText,
                    href: a.href,
                    parentClass: a.parentElement.className
                }));
            }''')

            # فلترة روابط المشاهدة
            for link in all_links:
                href = link['href']
                text = link['text']
                if not href or "javascript" in href: continue

                # منطق المشاهدة (Watch)
                if "1080" in text and "مشاهدة" in text: data["watch"].append({"q": "1080", "link": href})
                elif "720" in text and "مشاهدة" in text: data["watch"].append({"q": "720", "link": href})
                elif "480" in text and "مشاهدة" in text: data["watch"].append({"q": "480", "link": href})
                
                # منطق التحميل (Download)
                elif "1080" in text and ("تحميل" in text or "Download" in text): data["download"].append({"q": "1080", "link": href})
                elif "720" in text and ("تحميل" in text or "Download" in text): data["download"].append({"q": "720", "link": href})
                elif "480" in text and ("تحميل" in text or "Download" in text): data["download"].append({"q": "480", "link": href})

            # --- محاولة 2: لو القوائم فاضية، نستخدم الضغط على الأزرار ---
            if not data["watch"]:
                try:
                    await page.click("text='المشاهدة الآن'", timeout=3000)
                    await asyncio.sleep(2)
                    # (هنا ممكن نضيف كود سحب إضافي لو احتجنا)
                except: pass

        except Exception as e:
            print(f"Error fetching {url}: {e}")
            
        await browser.close()
    return data

# ==========================================
# 3️⃣ تصميم الصفحة
# ==========================================
async def main():
    html = """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>تطبيق المسلسلات</title>
        <style>
            body { background-color: #121212; color: #e0e0e0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 10px; }
            .card { background: #1e1e1e; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); border: 1px solid #333; }
            .title { color: #ff3d00; font-size: 20px; font-weight: bold; margin-bottom: 15px; text-align: center; border-bottom: 2px solid #333; padding-bottom: 10px; }
            .section-label { font-size: 14px; color: #888; margin: 15px 0 5px; font-weight: bold; }
            .btn-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 10px; }
            .btn { display: block; padding: 12px; border-radius: 8px; text-align: center; text-decoration: none; font-weight: bold; color: white; transition: transform 0.2s; font-size: 14px; }
            .btn:active { transform: scale(0.95); }
            .watch { background: linear-gradient(45deg, #d32f2f, #b71c1c); }
            .download { background: linear-gradient(45deg, #1976d2, #0d47a1); }
            .empty-msg { text-align: center; color: #666; font-style: italic; padding: 10px; }
        </style>
    </head>
    <body>
    """

    for item in ARABSEED_URLS:
        print(f"Working on: {item['title']}...")
        links = await get_links(item['url'])
        
        html += f'<div class="card"><div class="title">{item["title"]}</div>'
        
        # عرض روابط المشاهدة
        if links["watch"]:
            html += '<div class="section-label">📺 مشاهدة مباشرة</div><div class="btn-grid">'
            for link in links["watch"]:
                html += f'<a href="{link["link"]}" class="btn watch">{link["q"]}p</a>'
            html += '</div>'
        
        # عرض روابط التحميل
        if links["download"]:
            html += '<div class="section-label">⬇️ تحميل</div><div class="btn-grid">'
            for link in links["download"]:
                html += f'<a href="{link["link"]}" class="btn download">{link["q"]}p</a>'
            html += '</div>'

        # لو مفيش روابط خالص
        if not links["watch"] and not links["download"]:
            html += '<div class="empty-msg">⚠️ جاري تحديث الروابط... حاول لاحقاً</div>'
        
        html += '</div>'

    html += "</body></html>"
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ Done!")

if __name__ == "__main__":
    asyncio.run(main())
