import json
import re

import torch

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
)


MODEL_NAME = (
    "Qwen/Qwen2.5-1.5B-Instruct"
)


class LegalAnswerGenerator:

    def __init__(self):

        print(
            "Loading legal answer model:",
            MODEL_NAME
        )


        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )


        self.tokenizer = (
            AutoTokenizer.from_pretrained(
                MODEL_NAME
            )
        )


        self.model = (
            AutoModelForCausalLM.from_pretrained(
                MODEL_NAME,
                torch_dtype="auto",
                device_map="auto"
            )
        )


        self.model.eval()


        print(
            "Legal answer model ready."
        )


    # ==============================================
    # Build evidence context
    # ==============================================

    def build_context(
        self,
        results: list[dict]
    ) -> str:

        blocks = []


        for result in results:

            section = str(
                result.get(
                    "section"
                )
            )


            payload = result.get(
                "payload",
                {}
            )


            text = payload.get(
                "text",
                ""
            ).strip()


            source = result.get(
                "legal_source",
                {}
            )


            block = (
                f"SECTION {section}\n"
                f"Legal text:\n{text}\n\n"
                f"Source: "
                f"{source.get('source_url')}\n"
                f"Version: "
                f"{source.get('version')}\n"
                f"Verified: "
                f"{source.get('verified')}\n"
            )


            blocks.append(
                block
            )


        return (
            "\n============================\n"
            .join(
                blocks
            )
        )


    # ==============================================
    # Parse JSON from model
    # ==============================================

    def parse_json(
        self,
        text: str
    ) -> dict | None:

        text = text.strip()


        # Remove markdown fences if model adds them
        text = re.sub(
            r"^```(?:json)?",
            "",
            text,
            flags=re.IGNORECASE
        )


        text = re.sub(
            r"```$",
            "",
            text
        ).strip()


        try:

            return json.loads(
                text
            )

        except json.JSONDecodeError:

            pass


        # ------------------------------------------
        # Fallback: extract first JSON object
        # ------------------------------------------

        start = text.find(
            "{"
        )

        end = text.rfind(
            "}"
        )


        if (
            start == -1
            or end == -1
            or end <= start
        ):

            return None


        try:

            return json.loads(
                text[
                    start:end + 1
                ]
            )

        except json.JSONDecodeError:

            return None


    # ==============================================
    # Validate model citations
    # ==============================================

    def validate_sections(
        self,
        cited_sections: list,
        results: list[dict]
    ) -> bool:

        allowed = {

            str(
                result.get(
                    "section"
                )
            )

            for result in results
        }


        for section in cited_sections:

            if str(
                section
            ) not in allowed:

                return False


        return True


    # ==============================================
    # Generate answer
    # ==============================================

    def generate(
        self,
        query: str,
        results: list[dict]
    ) -> dict:

        if not results:

            return {

                "answer":
                    None,

                "cited_sections":
                    [],

                "needs_human_review":
                    True,

                "reason":
                    "No legal evidence was retrieved."
            }


        context = (
            self.build_context(
                results
            )
        )


        prompt = f"""
You are a legal information assistant for an Indian legal-help platform.

You are given VERIFIED provisions from the Bharatiya Nyaya Sanhita, 2023.

USER QUESTION:
{query}

VERIFIED LEGAL EVIDENCE:
{context}


STRICT RULES:

1. Answer ONLY using the supplied legal evidence.

2. Never invent:
   - a section,
   - punishment,
   - legal requirement,
   - exception,
   - procedure,
   - court interpretation,
   - or legal conclusion
   that is not supported by the supplied evidence.

3. Do NOT rely on your internal knowledge of Indian law.

4. If the supplied provisions are not sufficient to answer the question,
   set "needs_human_review" to true.

5. Cite only section numbers appearing in the supplied evidence.

6. Keep the answer concise and understandable to a normal person.

7. Clearly distinguish legal information from advice.

8. Do not say that the user is definitely guilty, innocent, liable,
   or entitled to win a case.

9. Do not provide procedural advice unless that procedure is explicitly
   contained in the supplied evidence.

10. Return ONLY valid JSON.

Required format:

{{
  "answer": "Concise source-grounded answer",
  "cited_sections": ["103"],
  "needs_human_review": false,
  "reason": "Evidence sufficiently answers the statutory question."
}}
""".strip()


        messages = [

            {
                "role":
                    "system",

                "content":
                    (
                        "Answer legal questions strictly "
                        "from supplied verified statutory "
                        "evidence. Never use unsupported "
                        "legal knowledge."
                    )
            },

            {
                "role":
                    "user",

                "content":
                    prompt
            }
        ]


        formatted = (
            self.tokenizer.apply_chat_template(

                messages,

                tokenize=False,

                add_generation_prompt=True
            )
        )


        inputs = self.tokenizer(

            formatted,

            return_tensors="pt"
        ).to(
            self.model.device
        )


        with torch.inference_mode():

            outputs = self.model.generate(

                **inputs,

                max_new_tokens=300,

                do_sample=False,

                pad_token_id=(
                    self.tokenizer.eos_token_id
                )
            )


        generated_tokens = outputs[
            0,
            inputs[
                "input_ids"
            ].shape[1]:
        ]


        generated = (
            self.tokenizer.decode(

                generated_tokens,

                skip_special_tokens=True
            )
        )


        parsed = (
            self.parse_json(
                generated
            )
        )


        # ==========================================
        # Invalid model output
        # ==========================================

        if parsed is None:

            return {

                "answer":
                    None,

                "cited_sections":
                    [],

                "needs_human_review":
                    True,

                "reason":
                    (
                        "Answer model returned an "
                        "invalid structured response."
                    )
            }


        answer = parsed.get(
            "answer"
        )


        cited_sections = (
            parsed.get(
                "cited_sections",
                []
            )
        )


        needs_human_review = bool(

            parsed.get(
                "needs_human_review",
                False
            )

        )


        reason = parsed.get(
            "reason",
            ""
        )


        # ==========================================
        # Validate citation structure
        # ==========================================

        if not isinstance(
            cited_sections,
            list
        ):

            return {

                "answer":
                    None,

                "cited_sections":
                    [],

                "needs_human_review":
                    True,

                "reason":
                    "Invalid citation structure."
            }


        # ==========================================
        # Hallucinated section protection
        # ==========================================

        if not self.validate_sections(

            cited_sections,

            results
        ):

            return {

                "answer":
                    None,

                "cited_sections":
                    [],

                "needs_human_review":
                    True,

                "reason":
                    (
                        "Answer model cited a section "
                        "that was not retrieved."
                    )
            }


        # ==========================================
        # Empty answer protection
        # ==========================================

        if (
            not answer
            and
            not needs_human_review
        ):

            return {

                "answer":
                    None,

                "cited_sections":
                    cited_sections,

                "needs_human_review":
                    True,

                "reason":
                    "Answer generation failed."
            }


        return {

            "answer":
                answer,

            "cited_sections": [
                str(
                    section
                )
                for section
                in cited_sections
            ],

            "needs_human_review":
                needs_human_review,

            "reason":
                reason
        }