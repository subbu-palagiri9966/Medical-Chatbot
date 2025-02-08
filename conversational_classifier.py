import spacy
import random
class ConversationalClassifier:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            import subprocess
            subprocess.run(['python', '-m', 'spacy', 'download', 'en_core_web_sm'])

        self.greeting_response = ['Hi! how may I help you', 'Hey! Hope everything is fine. What can I assist you with today?']
        self.thankyou_response = ['See you soon with your better health.', "Thanks for having a chat with me"]
    def classify_text(self, text):
        doc = self.nlp(text)
        
        if any(token.text.lower() in ['hello', "hi", "hey"] for token in doc):
            return random.choice(self.greeting_response)
        if any(token.text.lower() in ['thank', "thanks", "appreciate"] for token in doc):
            return random.choice(self.thankyou_response)
        else:
            return "Unknown"
