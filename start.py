
from google import genai

client = genai.Client()
interaction  = client.interaction(
    model ="gemini-3.8-flash",
    input = "Please analyze my program code and provide a brief summary of the following code snippets and their purpose.",
    )
print(interaction.output_text)