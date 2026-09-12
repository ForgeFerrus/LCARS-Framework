from groq import Groq
from lcars.system.environment import Runtime


def Main():
    Key = Runtime.get("GROQ_API_KEY")

    if not Key:
        print("GROQ_API_KEY: MISSING")
        return

    Client = Groq(api_key=Key)

    Tools = [
        {
            "type": "function",
            "function": {
                "name": "project_status",
                "description": (
                    "Return a fixed test status. "
                    "Do not inspect files or execute commands."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        }
    ]

    Response = Client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are testing the LCARS agent backend. "
                    "Use the project_status tool exactly once, "
                    "then answer briefly."
                ),
            },
            {
                "role": "user",
                "content": "Check the project agent connection.",
            },
        ],
        tools=Tools,
        tool_choice="required",
        reasoning_effort="low",
    )

    Message = Response.choices[0].message

    print("MODEL:", Response.model)
    print("CONTENT:", Message.content)
    print("TOOL_CALLS:", Message.tool_calls)

    if Message.tool_calls:
        for Call in Message.tool_calls:
            print("TOOL:", Call.function.name)
            print("ARGS:", Call.function.arguments)


if __name__ == "__main__":
    Main()