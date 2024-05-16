from fastapi import FastAPI
from wikipediaapi import Wikipedia
import openai
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("SECRET_KEY")

wiki_wiki = Wikipedia(language="en", user_agent="my_application")
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/sections/{page_name}")
async def get_sections(page_name: str):
    page_py = wiki_wiki.page(page_name)
    return {"sections": [s.title for s in page_py.sections]}


@app.get("/summary/{page_name}/{section_name}")
async def get_summary(page_name: str, section_name: str):
    page_py = wiki_wiki.page(page_name)
    for section in page_py.sections:
        if section.title == section_name:
            content = section.text[:4096]  # Limit to first 4096 characters for GPT-3.5 Turbo
            break
    else:
        return {"error": "Section not found"}
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": content},
            {"role": "user", "content": "Please summarize the above text."},
        ],
    )
    return {"original": content, "summary": response["choices"][0]["message"]["content"].strip()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
