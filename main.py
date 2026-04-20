from fastapi import FastAPI, Response, HTTPException, Query
import httpx
import time

app = FastAPI(title="Digital News Wire Service")

# قاعدة بيانات المشتركين: (المفتاح عبارة عن رقم : اسم المشترك)
# يمكنك تغيير الأرقام كما تحب لتكون هي "أكواد التفعيل"
SUBSCRIBERS = {
    "11223344": "قناة العربية",
    "55667788": "شبكة الجزيرة",
    "12345678": "مستخدم تجريبي"
}

# ذاكرة الجلسات (لمنع التكرار)
active_sessions = {}
SESSION_TIMEOUT = 300 # 5 دقائق خمول للسماح بتبديل الجهاز

NEWS_SOURCE_URL = "https://storage.googleapis.com/news-agency/x_world_leaders.xml"

@app.get("/api/v1/wire")
async def get_secure_wire(
    api_key: str = Query(..., description="كود التفعيل الرقمي"),
    device_id: int = Query(..., description="رقم معرف الجهاز")
):
    current_time = time.time()

    # 1. التحقق من كود التفعيل الرقمي
    if api_key not in SUBSCRIBERS:
        raise HTTPException(status_code=403, detail="Activation Code Error")

    # 2. منطق "الجهاز الواحد" باستخدام الـ IDs الرقمية
    if api_key in active_sessions:
        session = active_sessions[api_key]
        
        # إذا كان المعرف الرقمي للجهاز مختلف
        if session["device_id"] != device_id:
            # هل الجهاز الأول لا يزال نشطاً؟
            if current_time - session["last_seen"] < SESSION_TIMEOUT:
                raise HTTPException(
                    status_code=429, 
                    detail=f"Subscription active on another device"
                )
            else:
                # تحديث للجهاز الجديد بعد خمول القديم
                active_sessions[api_key] = {"device_id": device_id, "last_seen": current_time}
        else:
            # تحديث وقت النشاط لنفس الجهاز
            session["last_seen"] = current_time
    else:
        # أول تسجيل دخول لهذا الكود الرقمي
        active_sessions[api_key] = {"device_id": device_id, "last_seen": current_time}

    # 3. جلب ملف الـ XML والصور
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(NEWS_SOURCE_URL)
            return Response(content=response.text, media_type="application/xml")
        except:
            raise HTTPException(status_code=500, detail="Source Connection Error")
