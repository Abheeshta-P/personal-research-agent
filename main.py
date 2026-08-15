import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage

load_dotenv()

@tool
def calculator(a:float, b:float) -> float:
    """Add two numbers together."""
    return a+b

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is not set")

model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=api_key,
)

# add calculator to the model as tool 
        #          Gemini
        #             │
        #      ┌──────┴──────┐
        #      │             │
        #   Knowledge    Calculator
model_with_tools = model.bind_tools([calculator])

# response = model.invoke("Explain what an AI agent in one sentence.")

# print(response.text)

question = input("Ask me anything: ")

# response = model.invoke(question)
# response = model.invoke([
# response = model_with_tools.invoke([
#     ("system", "You are a helpful AI research assistant. Explain things clearly and accurately"),
#     ("human", question)
# ])

messages = [
    ("system", "You are a helpful AI research assistant. Use the calculator when you need to calculate numbers."),
    ("human", question),
]

response = model_with_tools.invoke(messages)

# response has everything text, tool call token everything differnt when tool called and text is generated
# print(response) 

if response.tool_calls:
    tool_call = response.tool_calls[0]
    result = calculator.invoke(tool_call["args"])

    # Gemini → Calculator → Result
    # print("Calculator result:",result)

    # Gemini → Calculator → Gemini → Final answer
    messages.append(response)
    
    # messages.append({
    #     "role": "tool",
    #     "content": str(result),
    #     "tool_call_id": tool_call["id"]
    # })
    messages.append(
        ToolMessage(
            content=str(result),
            tool_call_id=tool_call["id"]
        )
    )

    # print("\n--- MESSAGE HISTORY ---")

    # for message in messages:
    #     print(type(message).__name__, ":", message)

    # print("--- END MESSAGE HISTORY ---\n")

    final_response = model_with_tools.invoke(messages)

    print(final_response.text)
else:
    print(response.text)


# messages
# │
# ├── SystemMessage
# │     "You are a helpful assistant"
# │
# ├── HumanMessage
# │     "What is 29 + 9?"
# │
# ├── AIMessage
# │     "I want to call calculator"
# │     tool_call_id = "call_123"
# │
# └── ToolMessage
#       "38"
#       tool_call_id = "call_123"

    #                 YOUR CODE
    #                    │
    #                    ▼
    #               LANGCHAIN
    #       ┌────────────┼────────────┐
    #       │            │            │
    #    Messages     Tools       Model API
    #       │            │            │
    #       └────────────┼────────────┘
    #                    ▼
    #                  GEMINI

# --- MESSAGE HISTORY WITHOUT ToolMessage---
# tuple : ('system', 'You are a helpful AI research assistant. Use the calculator when you need to calculate numbers.')
# tuple : ('human', 'what is 25 + 9')
# AIMessage : content=[] additional_kwargs={'function_call': {'name': 'calculator', 'arguments': '{"b": 9, "a": 25}'}, '__gemini_function_call_thought_signatures__': {'call_1266642': 'EqICCp8CARFNMg8cFO16sWLCQvikKU5N+iirqHsc5bB5lB9/qaX9wu53Xq9csZgaZtLLi0z2c2C/Q6xHaWWbvCupzHjt/7Is8kYVPYrFqxZJJaZucVesMBhffZVWNBaEIK17zq29vTaggy6k7Ho4bji6t2mwbp4v89Htm23mI3eUkQB3zfBofyKHM0+Uvso2368YNyaQfP0GKHfap6ceCuiG0e4bpXyF2c+UoOymyaPy5p2DO+C7UiT8jLAS3qRr7YO5IgLWAfathgHp4DNQ697Or0ikLFmbVgkfyle+fpFfu3T/Fr7xIw6QLM9SRwagNdVfvIafCDwK9tnnyBQHcw1/EI2vgKZkuL2RD/sApeOwM52q7D0Wq/xq2f7gQ+Ukkkb9yjU='}} response_metadata={'finish_reason': 'STOP', 'model_name': 'gemini-3.6-flash', 'safety_ratings': [], 'model_provider': 'google_genai'} id='lc_run--019fff67-60c8-77f0-b510-3c10ccfbfdf3-0' tool_calls=[{'name': 'calculator', 'args': {'b': 9, 'a': 25}, 'id': 'call_1266642', 'type': 'tool_call'}] invalid_tool_calls=[] usage_metadata={'input_tokens': 79, 'output_tokens': 76, 'total_tokens': 155, 'input_token_details': {'cache_read': 0}, 'output_token_details': {'reasoning': 59}}
# dict : {'role': 'tool', 'content': '34.0', 'tool_call_id': 'call_1266642'}
# --- END MESSAGE HISTORY ---

# --- MESSAGE HISTORY ---
# tuple : ('system', 'You are a helpful AI research assistant. Use the calculator when you need to calculate numbers.')
# tuple : ('human', 'what is 25 + 9')
# AIMessage : content=[] additional_kwargs={'function_call': {'name': 'calculator', 'arguments': '{"b": 9, "a": 25}'}, '__gemini_function_call_thought_signatures__': {'call_214551': 'EpICCo8CARFNMg85yoceT+JWdhTeV0mZXMY0k9a0Cte7ws5EGC5F6hRqwH3IWeAntoZO8Ygmo2ENXc+0j/ElcQV612o8cUykUg7WcEeKrrd3XlNJNHWFG2z3fV3OnOIqk3AaWPgZjrjCKnvG5ojBhIESnXZ5psEWde3uf67dmDw4MxmGA0vTOU0k63IajxM9RrVTOnNAYJB1E6zkP6GeaunwzBVWMIG2khGTggwoC9OTJruT/3qaHFBr3zDJYVpEDcM9X1C5UCIA/ZNnLXKYX5NWPPqgZsCMSMp8WJ2wSBpXeQLNspsfjjMb6WK4Pwo1CRNUFPlGSvAUZnhrGYFAeRfce//tBLWy3S6Kz0Xss4UHW/v5ag=='}} response_metadata={'finish_reason': 'STOP', 'model_name': 'gemini-3.6-flash', 'safety_ratings': [], 'model_provider': 'google_genai'} id='lc_run--019fff65-6421-7d93-97eb-72be85847454-0' tool_calls=[{'name': 'calculator', 'args': {'b': 9, 'a': 25}, 'id': 'call_214551', 'type': 'tool_call'}] invalid_tool_calls=[] usage_metadata={'input_tokens': 79, 'output_tokens': 74, 'total_tokens': 153, 'input_token_details': {'cache_read': 0}, 'output_token_details': {'reasoning': 57}}
# ToolMessage : content='34.0' tool_call_id='call_214551'
# --- END MESSAGE HISTORY ---