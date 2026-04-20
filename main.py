from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, Field
from typing import List, Optional
import datetime
import uuid

# ==========================================
# 1. نظام الحماية والتصاريح (Authentication)
# ==========================================
API_KEY_NAME = "X-NewsWire-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

# قاعدة بيانات وهمية للمشتركين (القنوات الفضائية المشتركة في وكالتك)
VALID_CLIENTS = {
    "key_aljazeera_8923": "Al Jazeera Network",
    "key_alarabiya_4412": "Al Arabiya",
    "key_bbc_arabic_9910": "BBC Arabic"
}

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key not in VALID_CLIENTS:
        raise HTTPException(status_code=403, detail="غير مصرح لك بسحب الأخبار. يرجى تجديد الاشتراك.")
    return VALID_CLIENTS[api_key]

# ==========================================
# 2. الهيكلة القياسية للخبر (Data Models)
# ==========================================
class WireStory(BaseModel):
    story_id: str = Field(default_factory=lambda: f"urn:newsml:youragency.com:20260420:{uuid.uuid4().hex[:8]}")
    slugline: str = Field(..., description="الكلمة المفتاحية للخبر للبحث السريع في iNews")
    urgency: int = Field(..., ge=1, le=6, description="1: Flash (عاجل جدا), 2: Bulletin, 4: Regular")
    headline: str
    body_text: str
    category_code: str = Field(..., description="مثال: POL للسياسة, ECO للاقتصاد")
    published_at: datetime.datetime
    embargo_time: Optional[datetime.datetime] = None # وقت فك حظر النشر إن وجد

# ==========================================
# 3. إعداد السيرفر (FastAPI App)
# ==========================================
app = FastAPI(
    title="نظام الواير الاحترافي للوكالة",
    description="واجهة برمجة التطبيقات (API) لتوزيع الأخبار على أنظمة Newsrooms",
    version="2.0.0"
)

# قاعدة بيانات وهمية للأخبار الموجودة حالياً
db_news_wire = [
    WireStory(
        slugline="BC-USA-ELECTION-FLASH",
        urgency=1, # عاجل جداً يطلق صافرة في غرف الأخبار
        headline="عاجل | إعلان نتائج التصويت الأولية في ولاية حاسمة",
        body_text="أظهرت النتائج الأولية تقدم المرشح...",
        category_code="POL",
        published_at=datetime.datetime.now(datetime.timezone.utc)
    ),
    WireStory(
        slugline="BC-MARKETS-OIL-UPDATE",
        urgency=4, # خبر عادي
        headline="استقرار أسعار النفط عالمياً بعد قرارات أوبك",
        body_text="شهدت أسواق النفط استقراراً ملحوظاً اليوم...",
        category_code="ECO",
        published_at=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=15)
    )
]

# ==========================================
# 4. مسارات سحب الأخبار (Endpoints)
# ==========================================

@app.get("/api/v1/wire/latest", response_model=List[WireStory])
async def get_latest_news(limit: int = 50, client_name: str = Depends(verify_api_key)):
    """
    هذا الرابط الذي ستضعه القنوات في برامجها لسحب أحدث الأخبار بصيغة JSON السريعة.
    يتم تسجيل اسم القناة التي سحبت الخبر لأغراض الفوترة.
    """
    # هنا يتم ترتيب الأخبار وعرض أحدثها (بحد أقصى يحدده المتغير limit)
    # ملاحظة: في العمل الحقيقي، نقوم بسحبها من قاعدة بيانات حقيقية مثل PostgreSQL
    return db_news_wire[:limit]

@app.get("/api/v1/wire/newsml")
async def get_newsml_g2(client_name: str = Depends(verify_api_key)):
    """
    المعيار الذهبي (NewsML-G2): صيغة XML المعقدة التي تفهمها أنظمة (ENPS و iNews) القديمة والحديثة.
    """
    # توليد كود XML متوافق مع معايير الصحافة العالمية
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n<newsMessage xmlns="http://iptc.org/std/nar/2006-10-01/">\n'
    for news in db_news_wire:
        xml_content += f"""
        <itemSet>
            <newsItem guid="{news.story_id}">
                <itemMeta>
                    <urgency>{news.urgency}</urgency>
                </itemMeta>
                <contentMeta>
                    <headline>{news.headline}</headline>
                    <slugline>{news.slugline}</slugline>
                </contentMeta>
                <contentSet>
                    <inlineXML>
                        <body>{news.body_text}</body>
                    </inlineXML>
                </contentSet>
            </newsItem>
        </itemSet>
        """
    xml_content += "</newsMessage>"
    
    from fastapi.responses import Response
    return Response(content=xml_content, media_type="application/xml")