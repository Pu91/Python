from flask import Flask, request, jsonify
from datetime import datetime
import pytz
import re
import wikipedia
import random
import difflib
from flask_cors import CORS

wikipedia.set_lang("bn")
app = Flask(__name__)
CORS(app) # CORS সমস্যা সমাধানের জন্য

def ai_brain(user_message):
    message = user_message.lower().strip()
    
    qa_dict = {
        "hello": ["নমস্কার স্যার! ক্লাসে আপনাকে স্বাগত।", "হ্যালো! বলুন, আজ কী নিয়ে আলোচনা করব?", "হাই! আপনার 3D ভিডিও প্রজেক্টের কাজ কতদূর?"],
        "kemon acho": ["আমি দারুণ আছি! আপনি কেমন আছেন?", "খুব ভালো স্যার! আপনার ক্লাস করার জন্য অপেক্ষা করছিলাম।"],
        "cricket": ["ক্রিকেট তো আমারও খুব প্রিয়! বিরাট কোহলি বা শুভমান গিলের কোনো নতুন আপডেট আছে?", "ক্রিকেট নিয়ে কথা বলতে ভালোই লাগে।"],
        "student": ["আবু সাইদ, শাকিল এবং শান্তনু—ওরা সবাই ক্লাসের বেঞ্চে বসে আপনার লেকচারের জন্য অপেক্ষা করছে!"]
    }
    
    words_in_message = message.split()
    
    for key, responses in qa_dict.items():
        if key in message:
            return random.choice(responses)
        close_matches = difflib.get_close_matches(key, words_in_message, n=1, cutoff=0.7)
        if close_matches:
            return random.choice(responses)
            
    if any(word in message for word in ["time", "somoy", "কয়টা", "সময়", "baje"]):
        tz = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(tz).strftime('%I:%M %p')
        return f"স্যার, এখন ঘড়িতে সময় {current_time}।"
        
    if re.match(r'^[0-9\s\+\-\*\/\(\)\.]+$', message):
        try:
            result = eval(message)
            return f"খুব সহজ! এর উত্তর হবে: {result}"
        except:
            pass
            
    try:
        summary = wikipedia.summary(message, sentences=2)
        return f"আমি উইকিপিডিয়া থেকে আপনার জন্য এই তথ্যটি পেলাম:\n\n{summary}"
    except:
        pass
            
    fallback_responses = [
        f"আপনি বলেছেন: '{user_message}'। স্যার, এই বিষয়টি আমার জানা নেই। আমাকে কি একটু বুঝিয়ে বলবেন?",
        f"দুঃখিত স্যার, '{user_message}' সম্পর্কে আমার কাছে কোনো তথ্য নেই।"
    ]
    return random.choice(fallback_responses)

# এই অংশটিই আপনার সার্ভারে মিসিং ছিল (404 Error এর কারণ)
@app.route('/api', methods=['POST'])
def chat_api():
    user_message = request.form.get('message', '')
    ai_response = ai_brain(user_message)
    return jsonify({
        'status': 'success',
        'reply': ai_response
    })

# Render-এ সার্ভার লাইভ আছে কি না চেক করার জন্য
@app.route('/', methods=['GET'])
def home():
    return "Smart AI Tutor Server is Running Perfectly!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
