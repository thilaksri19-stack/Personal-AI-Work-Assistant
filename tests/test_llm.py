from src.generation.llm import generate_answer

prompt = """
Explain logistic regression in simple terms
for a beginner.
"""


answer = generate_answer(prompt)

print("\nANSWER:")
print(answer)