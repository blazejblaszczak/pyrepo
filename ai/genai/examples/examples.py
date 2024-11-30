import google.generativeai as genai

"""
This code is used to configure the Google Generative AI module, with a set configuration and a specific model for text generation.
It then prompts the model with several pairs of input-output where input is a word and output is a corresponding color.
The script finally uses this to generate text based on the given input and print out the result.
"""

genai.configure(api_key="your_api_key")

# Set up the model
generation_config = {
  "temperature": 0.9,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 2048,
}
safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]

model = genai.GenerativeModel(model_name="gemini-pro",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

prompt_parts = [
  "I will say a word and you tell me the color that describes best your emotional state",
  "input: cat",
  "output: orange",
  "input: ocean",
  "output: blue",
  "input: hugging",
  "output: pink",
  "input: work",
  "output: turquoise",
  "input: coffee",
  "output: red",
  "input: tenis",
  "output: light green",
  "input: ",
  "output: ",
]

response = model.generate_content(prompt_parts)
print(response.text)
