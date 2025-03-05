from config import *
from typing import List

if USE_LANGCHAIN:
    from .workflow import WorkFlow
else:
    from transformers import AutoTokenizer, TFAutoModelForQuestionAnswering, AutoModelForSeq2SeqLM
    import tensorflow as tf

class Chatbot:
    def __init__(self):
        if USE_LANGCHAIN:
            # Note: The Memory for the chatbot is stored per session
            # This way we don't create multiple instances of the model
            self.workflow = WorkFlow()
        else:
            model_name = "bert-large-uncased-whole-word-masking-finetuned-squad"
            self.AnswerModel = {
                "tokenizer": AutoTokenizer.from_pretrained(model_name),
                "model": TFAutoModelForQuestionAnswering.from_pretrained(model_name),
            }

            model_name = "google/flan-t5-large"
            self.QuestionsModel = {
                "tokenizer": AutoTokenizer.from_pretrained(model_name),
                "model": AutoModelForSeq2SeqLM.from_pretrained(model_name),
            }


    def GenerateAnswer(self, session, context, question) -> str:
        if USE_LANGCHAIN:
            result = self.workflow.Run(session, context, question)
            return result
        else:
            tokenizer = self.AnswerModel["tokenizer"]
            model = self.AnswerModel["model"]

            inputs = tokenizer(question, context, return_tensors="tf", padding=True, truncation=True)
            
            outputs = model(**inputs)

            start_logits = outputs.start_logits
            end_logits = outputs.end_logits

            start_index = tf.argmax(start_logits, axis=-1).numpy()[0]
            end_index = tf.argmax(end_logits, axis=-1).numpy()[0]

            answer_tokens = inputs.input_ids[0][start_index:end_index + 1]
            
            answer = tokenizer.decode(answer_tokens, skip_special_tokens=True)

            if answer in ["[CLS]", "[SEP]", ""]:
                return "Sorry, I couldn't find an answer to your question in the provided context."

            return answer
    
    def GenerateQuestions(self, session, context) -> List[str]:
        if USE_LANGCHAIN:
            result = self.workflow.Run(session, context, "Generate 3 questions about this document without enums.")
            cleaned_result = [line for line in result.splitlines() if line.strip()]
            return cleaned_result
        else:
            tokenizer = self.QuestionsModel["tokenizer"]
            model = self.QuestionsModel["model"]

            inputs = tokenizer("Generate 3 questions based on the following context: " + context, return_tensors="pt", padding=True, truncation=True)

            outputs = model.generate(
                inputs['input_ids'],
                min_length=6,
                max_length=20,
                num_return_sequences=3,
                do_sample=True,
                temperature=1.2,
            )

            generated_questions = tokenizer.batch_decode(outputs, skip_special_tokens=True)

            return generated_questions