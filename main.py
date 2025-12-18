import asyncio
import nest_asyncio
from playwright.async_api import async_playwright

nest_asyncio.apply()

# ==========================================
# 1️⃣ قائمة المسلسلات (عدل هنا براحتك)
# ==========================================
ARABSEED_URLS = [
    {"title": "لا ترد ولا تستبدل", "url": "https://a.asd.homes/?p=828743"},
    {"title": "2 قهوة", "url": "https://a.asd.homes/?p=828618"},
    {"title": "ميدتيرم", "url": "https://a.asd.homes/?p=828728"}
]

# ==========================================
# 2️⃣ كود السحب (مفصول مشاهدة / تحميل)
# ==========================================
async def get_links(url):
    data = {"watch": [], "download": []}
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
        page = await context.new_page()
        
        try:
            await page.goto(url, timeout=60000)
            
            # --- أ) سحب روابط المشاهدة (1080, 720, 480) ---
            try:
                # محاولة فتح تبويب المشاهدة
                await page.click("li:has-text('المشاهدة الآن'), span:has-text('المشاهدة الآن')", timeout=2000)
                await asyncio.sleep(1)
            except: pass

            watch_qualities = ["1080", "720", "480"]
            for q in watch_qualities:
                try:
                    # البحث عن الجودة
                    elem = page.locator(f".WatchServersContainer a:has-text('{q}'), ul.WatchServers li:has-text('{q}') a").first
                    if await elem.count() > 0:
                        href = await elem.get_attribute("href")
                        if href: data["watch"].append({"q": q, "link": href})
                except: pass

            # --- ب) سحب روابط التحميل (1080, 720, 480, 360) ---
            try:
                # محاولة فتح تبويب التحميل
                await page.click("li:has-text('التحميل الآن'), span:has-text('التحميل الآن')", timeout=2000)
                await asyncio.sleep(1)
            except: pass

            dl_qualities = ["1080", "720", "480", "360"]
            for q in dl_qualities:
                try:
                    elem = page.locator(f".DownloadServersContainer a:has-text('{q}'), ul.DownloadServers li:has-text('{q}') a").first
                    if await elem.count() > 0:
                        href = await elem.get_attribute("href")
                        if href: data["download"].append({"q": q, "link": href})
                except: pass
                
        except Exception as e:
            print(f"Error: {e}")
            
        await browser.close()
    return data

# ==========================================
# 3️⃣ تصميم الصفحة (HTML Generator)
# ==========================================
async def main():
    html = """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ArabSeed App</title>
        <style>
            body { background-color: #1a1a1a; color: white; font-family: sans-serif; margin: 0; padding: 10px; }
            .card { background: #2d2d2d; border-radius: 10px; padding: 15px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
            .title { color: #e50914; font-size: 18px; font-weight: bold; margin-bottom: 10px; text-align: center;}
            .section-title { font-size: 14px; color: #aaa; margin: 10px 0 5px; border-bottom: 1px solid #444; padding-bottom: 5px; }
            .btn { display: block; width: 100%; padding: 10px; margin: 5px 0; border-radius: 5px; text-align: center; text-decoration: none; font-weight: bold; color: white; box-sizing: border-box; }
            /* ألوان الزراير */
            .w-1080 { background: #4caf50; } .w-720 { background: #8bc34a; } .w-480 { background: #cddc39; color: black; }
            .d-1080 { background: #2196f3; } .d-720 { background: #03a9f4; } .d-480 { background: #00bcd4; } .d-360 { background: #009688; }
        </style>
    </head>
    <body>
    """

    for item in ARABSEED_URLS:
        print(f"جاري العمل على: {item['title']}...")
        links = await get_links(item['url'])
        
        html += f'<div class="card"><div class="title">{item["title"]}</div>'
        
        # إضافة أزرار المشاهدة
        if links["watch"]:
            html += '<div class="section-title">📺 مشاهدة مباشرة</div>'
            for link in links["watch"]:
                html += f'<a href="{link["link"]}" class="btn w-{link["q"]}">مشاهدة {link["q"]}p</a>'
        
        # إضافة أزرار التحميل
        if links["download"]:
            html += '<div class="section-title">⬇️ تحميل</div>'
            for link in links["download"]:
                html += f'<a href="{link["link"]}" class="btn d-{link["q"]}">تحميل {link["q"]}p</a>'
        
        html += '</div>'

    html += "</body></html>"
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ تم إنشاء الصفحة بنجاح!")

if __name__ == "__main__":
    asyncio.run(main())
