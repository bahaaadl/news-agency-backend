from fastapi import FastAPI, Response
import httpx

app = FastAPI(title="Professional News Wire Service")

# المصدر الرئيسي والوحيد للأخبار والصور
NEWS_SOURCE_URL = "https://storage.googleapis.com/news-agency/x_world_leaders.xml"

@app.get("/x_world_leaders.xml")
async def get_agency_wire():
    """
    هذا الرابط هو الذي ستستخدمه في موقع الويب وفي أي برنامج أخبار.
    يقوم بجلب ملف XML الأصلي (بما فيه من صور وأخبار) وإعادة بثه.
    """
    async with httpx.AsyncClient() as client:
        try:
            # 1. جلب البيانات (XML + صور) من رابط جوجل
            response = await client.get(NEWS_SOURCE_URL, timeout=10.0)
            
            # التأكد من نجاح الجلب
            if response.status_code == 200:
                xml_content = response.text
                
                # 2. إرسال البيانات كما هي (للحفاظ على التوافق الكامل مع موقعك القديم)
                return Response(content=xml_content, media_type="application/xml")
            else:
                return Response(content="<error>Source unavailable</error>", status_code=502)
                
        except Exception as e:
            return Response(content=f"<error>{str(e)}</error>", status_code=500)

@app.get("/")
def home():
    return {"status": "Agency Backend is Online", "source_connected": True}
