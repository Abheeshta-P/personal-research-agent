from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

model = ChatGoogleGenerativeAI(
    # model="gemini-3.6-flash"
    # model="gemini-3.5-flash-lite",
    model="gemini-3.1-flash-lite",
    thinking_level="minimal",
)