#from transformers import TFGPT2LMHeadModel, GPT2Tokenizer
from transformers import TFAutoModelForQuestionAnswering, AutoTokenizer
import tensorflow as tf

# If you want to run tensorflow using your gpu you have to install cuda toolkit (3gb) then cudnn (600mb) and zlib have fun #
#devices = tf.config.list_physical_devices()
#print(devices)
class Chatbot:
    def __init__(self, model_name):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = TFAutoModelForQuestionAnswering.from_pretrained(model_name)
        #self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        #self.model = TFGPT2LMHeadModel.from_pretrained(model_name)

    # If you want to generate answers only and no text like chatgpt, use this function #
    # It will give direct answers which is boring #
    # And use this model 'bert-large-uncased-whole-word-masking-finetuned-squad' the others don't work #
    def GenerateAnswer(self, question, context):
        if tf.config.list_physical_devices('GPU'):
            device = '/GPU:0'
        else:
            device = '/CPU:0'

        with tf.device(device):
            inputs = self.tokenizer.encode_plus(question, context, add_special_tokens=True, return_tensors="tf")

            input_ids = inputs["input_ids"].numpy().tolist()[0]

            outputs = self.model(inputs['input_ids'], attention_mask=inputs['attention_mask'])

            answer_start_scores = outputs.start_logits
            answer_end_scores = outputs.end_logits

            answer_start = tf.argmax(answer_start_scores, axis=1).numpy()[0]
            answer_end = tf.argmax(answer_end_scores, axis=1).numpy()[0] + 1

            if answer_start == 0 or answer_end == 0 or answer_start >= len(input_ids) or answer_end > len(input_ids):
                return "Sorry, I couldn't find an answer to your question in the provided context."

            answer = self.tokenizer.convert_tokens_to_string(self.tokenizer.convert_ids_to_tokens(input_ids[answer_start:answer_end]))

            if answer in ["[CLS]", "[SEP]", ""]:
                return "Sorry, I couldn't find an answer to your question in the provided context."
            
            return answer

    # this text generator doesn't even work right #
    # GPT2 has repitition issues, and i can't find a way to make it generate text based off of the context and the prompt #
    # If you concatenate the context with the prompt, it will just give out the entire context most of the time #
    # Also if you do that the max_length has to be massive to fit the context aswell so it will take ages to generate the text #
    # Rather use the direct answering model since that one is almost instant and it works lol #
    # Model name for this is just 'gpt2' #
    def GenerateText(self, prompt, context, max_length=100, temperature=0.8, top_k=50, top_p=0.9):
        if tf.config.list_physical_devices('GPU'):
            device = '/GPU:0'
        else:
            device = '/CPU:0'

        with tf.device(device):
            inputs = self.tokenizer.encode(prompt, return_tensors='tf')
            outputs = self.model.generate(
                inputs,
                max_length=max_length,
                temperature=temperature,
                top_k=top_k,
                top_p=top_p,
                do_sample=True,
            )
            text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return text