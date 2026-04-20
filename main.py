from fastapi import FastAPI, Response
from email.utils import formatdate
import time

app = FastAPI(title="وكالة الأنباء الاحترافية - RSS Feed")

# قاعدة بيانات الأخبار (تخيل أن الصحفيين أدخلوها عبر لوحة التحكم)
# وضعت لك صوراً حقيقية لروابط مشابهة لما كان في الملف القديم
db_news = [
    {
        "id": "1001",
        "title": "Javier Milei",
        "desc": "الرئيس ميلي في إسرائيل 🇦🇷🇮🇱 | لقاء تاريخي لتعزيز العلاقات.",
        "link": "https://x.com/JMilei/status/123456",
        # توليد الوقت بالصيغة العالمية RFC 822 التي يقرأها feedparser
        "date": formatdate(timeval=time.time(), localtime=False, usegmt=True), 
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Javier_Milei_en_el_Foro_Econ%C3%B3mico_Mundial_2024_%28cropped%29.jpg/800px-Javier_Milei_en_el_Foro_Econ%C3%B3mico_Mundial_2024_%28cropped%29.jpg"
    },
    {
        "id": "1002",
        "title": "التلفزيون العربي",
        "desc": "عاجل | الرئاسة الإيرانية تؤكد استمرار المحادثات الدبلوماسية لوقف إطلاق النار.",
        "link": "https://alaraby.com/news/789",
        "date": formatdate(timeval=time.time() - 3600, localtime=False, usegmt=True), # خبر قبل ساعة
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Alaraby_TV_logo.svg/800px-Alaraby_TV_logo.svg.png"
    },
    {
        "id": "1003",
        "title": "خبر عاجل - بدون صورة",
        "desc": "بيان رسمي يوضح تفاصيل القرارات الاقتصادية الجديدة.",
        "link": "https://news.com/urgent",
        "date": formatdate(timeval=time.time() - 7200, localtime=False, usegmt=True),
        "image": None # اختبار لخبر بدون صورة
    }
]

@app.get("/x_world_leaders.xml") # جعلنا الرابط بنفس اسم الملف القديم تقريباً!
def generate_rss_feed():
    """
    هذه الدالة تصنع ملف XML يطابق تماماً الملف الذي كان يقرأه موقعك
    """
    # ترويسة ملف RSS القياسية مع دعم الصور (media)
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/">\n'
    xml += '  <channel>\n'
    xml += '    <title>وكالة الأنباء الاحترافية (الواير الخاص)</title>\n'
    xml += '    <link>https://your-agency-domain.com</link>\n'
    xml += '    <description>تغذية إخبارية حية لغرف الأخبار</description>\n'

    # تحويل قاعدة البيانات إلى أسطر XML
    for item in db_news:
        xml += '    <item>\n'
        xml += f'      <title><![CDATA[{item["title"]}]]></title>\n'
        xml += f'      <link>{item["link"]}</link>\n'
        xml += f'      <description><![CDATA[{item["desc"]}]]></description>\n'
        xml += f'      <pubDate>{item["date"]}</pubDate>\n'
        xml += f'      <guid isPermaLink="false">{item["id"]}</guid>\n'
        
        # السر هنا: هذا الكود هو الذي سيجعل موقعك (وأنظمة الأخبار الأخرى) تسحب الصور!
        if item["image"]:
            # Enclosure هو المعيار القديم
            xml += f'      <enclosure url="{item["image"]}" type="image/jpeg" length="1024" />\n'
            # Media:content هو المعيار الحديث الذي يبحث عنه الكود الخاص بك
            xml += f'      <media:content url="{item["image"]}" medium="image" />\n'
            
        xml += '    </item>\n'

    xml += '  </channel>\n'
    xml += '</rss>'
    
    # إرسال الملف للمتصفح على أنه ملف XML وليس نصاً عادياً
    return Response(content=xml, media_type="application/xml")
