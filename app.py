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

ai_memory = {}

def ai_brain(user_message, chat_id):
    message = user_message.lower().strip()
    
    # ==========================================
    # স্মার্ট RAG (পড়ে নির্দিষ্ট অংশ বের করা)
    # ==========================================
    if "protista" in message or "protasta" in message:
        try:
            with open('protista.txt', 'r', encoding='utf-8') as file:
                notes = file.read()
            
            # যদি শুধু 'বৈশিষ্ট্য' জানতে চায়
            if "বৈশিষ্ট্য" in message or "boisisto" in message or "characteristics" in message:
                start = notes.find("প্রধান বৈশিষ্ট্যসমূহ:")
                end = notes.find("উদাহরণ:")
                if start != -1 and end != -1:
                    specific_answer = notes[start:end].strip().replace('\n', '<br>')
                    return f"স্যার, আপনার নোটস অনুযায়ী কিংডম প্রোটিস্টার বৈশিষ্ট্যগুলো হলো:<br><br>{specific_answer}"
            
            # যদি শুধু 'উদাহরণ' জানতে চায়
            elif "উদাহরণ" in message or "example" in message or "udahar" in message:
                start = notes.find("উদাহরণ:")
                if start != -1:
                    specific_answer = notes[start:].strip().replace('\n', '<br>')
                    return f"স্যার, আপনার নোটস অনুযায়ী এর কিছু উদাহরণ হলো:<br><br>{specific_answer}"
            
            # যদি শুধু 'কাকে বলে' বা সাধারণ কিছু জানতে চায়
            else:
                end = notes.find("প্রধান বৈশিষ্ট্যসমূহ:")
                specific_answer = notes[:end].strip().replace('\n', '<br>') if end != -1 else notes.replace('\n', '<br>')
                return f"স্যার, প্রোটিস্টা সম্পর্কে সাধারণ ধারণা হলো:<br><br>{specific_answer}"

        except:
            return "স্যার, 'protista.txt' ফাইলটি খুঁজে পাচ্ছি না।"
            
    # নাম মনে করা (Memory Recall)
    if any(phrase in message for phrase in ["amar nam ki", "amar name ki", "what is my name", "amar nam ki?"]):
        if chat_id in ai_memory and 'user_name' in ai_memory[chat_id]:
            return f"আপনার নাম হলো {ai_memory[chat_id]['user_name']}! আমি কি আমার স্যারের নাম ভুলতে পারি?"
        return "স্যার, আপনি তো এখনও আমাকে আপনার নাম বলেননি! আপনার নাম কী?"

    # নাম সেভ করা (Memory Save)
    elif any(phrase in message for phrase in ["amar nam", "amar name", "my name is"]):
        name = ""
        for keyword in ["is ", "name ", "nam "]:
            if keyword in message:
                name = message.split(keyword)[-1].strip()
                break
        if name:
            if chat_id not in ai_memory: ai_memory[chat_id] = {}
            ai_memory[chat_id]['user_name'] = name
            return f"ঠিক আছে স্যার, আমি মনে রাখব যে আপনার নাম {name}!"

    # সাধারণ নলেজ
    qa_dict = {
        "hello": ["নমস্কার স্যার! ক্লাসে আপনাকে স্বাগত।", "হ্যালো! বলুন, আজ কী নিয়ে আলোচনা করব?"],
        "hi": ["হ্যালো স্যার! আমি প্রস্তুত।", "হাই! বলুন কীভাবে সাহায্য করতে পারি?"],
        "student": ["আবু সাইদ, শাকিল এবং শান্তনু—ওরা সবাই ক্লাসের বেঞ্চে বসে আপনার লেকচারের জন্য অপেক্ষা করছে!"]
    }
    
    words_in_message = message.split()
    for key, responses in qa_dict.items():
        if key in message or difflib.get_close_matches(key, words_in_message, n=1, cutoff=0.7):
            return random.choice(responses)
            
    # সময় বলা
    if any(word in message for word in ["time", "somoy"]):
        tz = pytz.timezone('Asia/Kolkata')
        return f"স্যার, এখন ঘড়িতে সময় {datetime.now(tz).strftime('%I:%M %p')}।"
        
    # অঙ্ক করা
    if re.match(r'^[0-9\s\+\-\*\/\(\)\.]+$', message):
        try: return f"খুব সহজ! এর উত্তর হবে: {eval(message)}"
        except: pass
            
    # উইকিপিডিয়া সার্চ
    try:
        return f"আমি উইকিপিডিয়া থেকে আপনার জন্য এই তথ্যটি পেলাম:<br><br>{wikipedia.summary(message, sentences=2)}"
    except:
        pass
            
    return random.choice([
        f"আপনি বলেছেন: '{user_message}'। স্যার, এই বিষয়টি আমার জানা নেই। আমাকে কি একটু বুঝিয়ে বলবেন?",
        f"দুঃখিত স্যার, '{user_message}' সম্পর্কে আমার কাছে কোনো তথ্য নেই।"
    ])

@app.route('/api', methods=['POST'])
def chat_api():
    return jsonify({
        'status': 'success',
        'reply': ai_brain(request.form.get('message', ''), request.form.get('chat_id', 'default_chat'))
    })

@app.route('/', methods=['GET'])
def home():
    return "Smart AI Tutor Server is Running Perfectly!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
