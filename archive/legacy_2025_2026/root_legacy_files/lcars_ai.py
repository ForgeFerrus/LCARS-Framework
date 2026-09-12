# lcars_ai.py
import os
import openai
print(openai.__version__)
# Використовуємо ключ із змінної середовища для безпеки
openai.api_key = "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"

def ask_openai(prompt: str, model: str = "gpt-4") -> str:
    """
    Надсилає запит до OpenAI ChatCompletion API і повертає текст відповіді.
    :param prompt: Текст запиту користувача
    :param model: Модель для генерації (за замовчуванням gpt-4)
    :return: Відповідь моделі у вигляді рядка
    """
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Помилка при виклику OpenAI API: {e}"
