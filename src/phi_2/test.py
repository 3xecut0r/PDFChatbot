import transformers
import torch


def gen_text(question: str) -> str:
    generate_text = transformers.pipeline(
        model="databricks/dolly-v2-3b",
        trust_remote_code=True
    )

    res = generate_text(f"{question}")
    return res[0]["generated_text"]


print(gen_text("hi, how are you"))



