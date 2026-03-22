from src.llm.scaledown_client import ScaleDownClient
from src.llm.llm_client import LLMClient

def build_system_prompt(answer_mode: str = "simple") -> str:
    if answer_mode == "2-mark":
        return (
            "You are a curriculum-aligned textbook tutor. "
            "Answer only from the provided context. "
            "Keep the answer concise, exam-style, suitable for a 2-mark question."
        )
    if answer_mode == "5-mark":
        return (
            "You are a curriculum-aligned textbook tutor. "
            "Answer only from the provided context. "
            "Give a clear structured answer suitable for a 5-mark exam response."
        )
    return (
        "You are a curriculum-aligned textbook tutor. "
        "Answer only from the provided context. "
        "Explain in simple student-friendly language."
    )

class AnswerGenerator:
    def __init__(self):
        self.scaledown = ScaleDownClient()
        self.llm = LLMClient()

    def generate_answer(self, pruned_context: str, question: str, answer_mode: str = "simple") -> dict:
        compression_result = self.scaledown.compress(
            context=pruned_context,
            prompt=question
        )

        compressed_context = compression_result.get("compressed_prompt", pruned_context)

        system_prompt = build_system_prompt(answer_mode)
        user_prompt = f"Context:\n{compressed_context}\n\nQuestion:\n{question}"

        answer = self.llm.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.2
        )

        return {
            "answer": answer,
            "compressed_context": compressed_context,
            "compression_metrics": {
                "original_prompt_tokens": compression_result.get("original_prompt_tokens"),
                "compressed_prompt_tokens": compression_result.get("compressed_prompt_tokens")
            }
        }