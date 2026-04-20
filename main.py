from fastapi import FastAPI, Response
import httpx

app = FastAPI(title="Professional News Wire Service")

NEWS_SOURCE_URL = "https://storage.googleapis.com/news-agency/x_world_leaders.xml"

@app.get("/x_world_leaders.xml")
async def get_agency_wire():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(NEWS_SOURCE_URL, timeout=10.0)
            if response.status_code == 200:
                return Response(content=response.text, media_type="application/xml")
            else:
                return Response(content="<error>Source unavailable</error>", status_code=502)
        except Exception as e:
            return Response(content=f"<error>{str(e)}</error>", status_code=500)

@app.get("/")
def home():
    return {"status": "Agency Backend is Online", "source_connected": True}
