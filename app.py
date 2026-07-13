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
CORS(app) 

# ==========================================
# AI-এর মেমোরি বা স্মৃতিশক্তি (ম্যাজিক এখানেই!)
# ==========================================
ai_memory = {}

def ai_brain(user_message, chat_id):
    message = user_message.lower().strip()
    
    # ১. মেমোরি সেভ করা (যেমন: আমার নাম পুস্পেন্দু)
    if "amar nam" in message or "my name is" in message:
        # নামটা বের করার লজিক
        name_parts = message.split("nam") if "nam" in message else message.split("is")
        if len(name_parts) > 1:
            name = name_parts[-1].strip()
            
            # মেমোরিতে চ্যাট আইডি অনুযায়ী নাম সেভ করা
            if chat_id not in ai_memory:
                ai_memory[chat_id] = {}
            ai_memory[chat_id]['user_name'] = name
            
            return f"ঠিক আছে স্যার, আমি মনে রাখব যে আপনার নাম {name}!"

    # ২. মেমোরি থেকে মনে করা (যেমন: আমার নাম কী?)
    if "amar nam ki" in message or "what is my name" in message or "amar name ki" in message:
        if chat_id in ai_memory and 'user_name' in ai_memory[chat_id]:
            saved_name = ai_memory[chat_id]['user_name']
            return f"আপনার নাম হলো {saved_name}! আমি কি আমার স্যারের নাম ভুলতে পারি?"
        else:
            return "স্যার, আপনি তো এখনও আমাকে আপনার নাম বলেননি! আপনার নাম কী?"

    # ৩. সাধারণ নলেজ বেস
    qa_dict = {
        "hello": ["নমস্কার স্যার! ক্লাসে আপনাকে স্বাগত।", "হ্যালো! বলুন, আজ কী নিয়ে আলোচনা করব?"],
        "hi": ["হ্যালো স্যার! আমি প্রস্তুত।", "হাই! বলুন কীভাবে সাহায্য করতে পারি?"],
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
            
    # ৪. সময় বলা
    if any(word in message for word in ["time", "somoy", "কয়টা", "সময়", "baje"]):
        tz = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(tz).strftime('%I:%M %p')
        return f"স্যার, এখন ঘড়িতে সময় {current_time}।"
        
    # ৫. অঙ্ক করা
    if re.match(r'^[0-9\s\+\-\*\/\(\)\.]+$', message):
        try:
            result = eval(message)
            return f"খুব সহজ! এর উত্তর হবে: {result}"
        except:
            pass
            
    # ৬. উইকিপিডিয়া সার্চ
    try:
        summary = wikipedia.summary(message, sentences=2)
        return f"আমি উইকিপিডিয়া থেকে আপনার জন্য এই তথ্যটি পেলাম:<br><br>{summary}"
    except:
        pass
            
    # ৭. কিছু না বুঝলে
    fallback_responses = [
        f"আপনি বলেছেন: '{user_message}'। স্যার, এই বিষয়টি আমার জানা নেই। আমাকে কি একটু বুঝিয়ে বলবেন?",
        f"দুঃখিত স্যার, '{user_message}' সম্পর্কে আমার কাছে কোনো তথ্য নেই।"
    ]
    return random.choice(fallback_responses)

@app.route('/api', methods=['POST'])
def chat_api():
    user_message = request.form.get('message', '')
    
    # PHP থেকে আসা Chat ID ধরা হচ্ছে, যাতে সে আলাদা আলাদা চ্যাটের কথা আলাদাভাবে মনে রাখে
    chat_id = request.form.get('chat_id', 'default_chat') 
    
    # ব্রেনকে মেসেজ এবং চ্যাট আইডি দুটোই পাঠানো হলো
    ai_response = ai_brain(user_message, chat_id)
    
    return jsonify({
        'status': 'success',
        'reply': ai_response
    })

@app.route('/', methods=['GET'])
def home():
    return "Smart AI Tutor Server is Running Perfectly!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
