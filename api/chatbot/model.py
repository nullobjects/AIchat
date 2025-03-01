from transformers import TFAutoModelForQuestionAnswering, AutoTokenizer
import tensorflow as tf

class Chatbot:
    def __init__(self, model_name):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = TFAutoModelForQuestionAnswering.from_pretrained(model_name)

    def GenerateAnswer(self, question, context):
        inputs = self.tokenizer(question, context, return_tensors="tf", padding=True, truncation=True)
        
        outputs = self.model(**inputs)

        start_logits = outputs.start_logits
        end_logits = outputs.end_logits

        start_index = tf.argmax(start_logits, axis=-1).numpy()[0]
        end_index = tf.argmax(end_logits, axis=-1).numpy()[0]

        answer_tokens = inputs.input_ids[0][start_index:end_index + 1]
        
        answer = self.tokenizer.decode(answer_tokens, skip_special_tokens=True)
    
        if answer in ["[CLS]", "[SEP]", ""]:
            return "Sorry, I couldn't find an answer to your question in the provided context."

        return answer