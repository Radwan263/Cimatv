import asyncio
import nest_asyncio
from playwright.async_api import async_playwright
# استدعاء مكتبة التخفي الجديدة
from playwright_stealth import stealth_async

nest_asyncio.apply()

ARABSEED_URLS = [
    {"title": "لا ترد ولا تستبدل", "url": "https://a.asd.homes/?p=828743"},
    {"title": "2 قهوة", "url": "https://a.asd.homes/?p=828618"},
    {"title": "ميدتيرم", "url": "https://a.asd.homes/?p=828728"}
]

async def get_links(url):
    data = {"watch": [], "download": []}
    async with async_playwright() as p:
        # تشغيل المتصفح بخصائص حقيقية
        browser = await p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        
        # تفعيل وضع التخفي للصفحة
        page = await context.new_page()
        await stealth_async(page)
        
        try:
            print(f"🕵️‍♂️ محاولة تخطي الحماية لـ: {url}")
            await page.goto(url, timeout=90000)
            await asyncio.sleep(7) # انتظار أطول عشان لو فيه كابتشا بتتحل لوحدها

            # محاولة الضغط على أي زرار "تخطي" لو ظهر (اختياري)
            try: await page.click("input[value='Verify you are human']", timeout=2000); except: pass
            
            # سحب الروابط
            links = await page.evaluate("""() => {
                return Array.from(document.querySelectorAll('a')).map(a => ({
                    href: a.href,
                    text: a.innerText
                }))
            }""")
            
            print(f"✅ تم العثور على {len(links)} رابط.")

            for link in links:
                href = link['href']
                text = link['text'].strip()
                if not href or "javascript" in href or href == url: continue

                # نفس الفلاتر القديمة
                if "watch" in href or "embed" in href or "مشاهدة" in text:
                    if "1080" in text: data["watch"].append({"q": "1080", "link": href})
                    elif "720" in text: data["watch"].append({"q": "720", "link": href})
                    elif "480" in text: data["watch"].append({"q": "480", "link": href})
                
                elif "download" in href or "uptobox" in href or "mediafire" in href:
                    if "1080" in text: data["download"].append({"q": "1080", "link": href})
                    elif "720" in text: data["download"].append({"q": "720", "link": href})
                    elif "480" in text: data["download"].append({"q": "480", "link": href})

        except Exception as e:
            print(f"❌ Error: {e}")
            
        await browser.close()
    
    # تنظيف التكرار
    seen = set()
    unique_watch = []
    for d in data["watch"]:
        if d['link'] not in seen:
            unique_watch.append(d)
            seen.add(d['link'])
    data["watch"] = unique_watch

    return data

async def main():
    html = """<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>ArabSeed Links</title><style>body{background:#111;color:#fff;font-family:sans-serif;padding:20px}.card{background:#222;margin-bottom:20px;padding:15px;border-radius:10px;border:1px solid #333}h3{color:#e91e63;margin:0 0 10px 0;border-bottom:1px solid #444;padding-bottom:5px}.btn{display:inline-block;padding:8px 15px;margin:5px;background:#333;color:white;text-decoration:none;border-radius:5px;font-size:14px}.watch{background:#4caf50}.dl{background:#2196f3}.no-link{color:#777;font-size:12px}</style></head><body><h1>🎬 آخر الحلقات</h1>"""

    for item in ARABSEED_URLS:
        links = await get_links(item['url'])
        html += f'<div class="card"><h3>{item["title"]}</h3>'
        
        if links["watch"]:
            html += '<div>📺 مشاهدة:<br>'
            for l in links["watch"]: html += f'<a href="{l["link"]}" class="btn watch">{l["q"]}</a>'
            html += '</div>'
            
        if links["download"]:
            html += '<hr><div>⬇️ تحميل:<br>'
            for l in links["download"]: html += f'<a href="{l["link"]}" class="btn dl">{l["q"]}</a>'
            html += '</div>'
            
        if not links["watch"] and not links["download"]:
            html += '<p class="no-link">⚠️ لم يتم تخطي الحماية (Cloudflare Blocking).</p>'
        html += '</div>'

    html += "</body></html>"
    with open("index.html", "w", encoding="utf-8") as f: f.write(html)

if __name__ == "__main__":
    asyncio.run(main())

