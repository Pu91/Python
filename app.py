from flask import Flask, request, jsonify
import os
from datetime import datetime
import pytz
import google.generativeai as genai
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ==========================================
# চাবি এখন রেন্ডারের গোপন লকার থেকে আসবে!
# ==========================================
GOOGLE_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash')

ai_memory = {}

def ai_brain(user_message, chat_id):
    message = user_message.lower().strip()
    
    if any(phrase in message for phrase in ["amar nam", "amar name", "my name is"]):
        name = ""
        for keyword in ["is ", "name ", "nam "]:
            if keyword in message:
                name = message.split(keyword)[-1].strip()
                break
        if name:
            if chat_id not in ai_memory: ai_memory[chat_id] = {}
            ai_memory[chat_id]['user_name'] = name
            return f"ঠিক আছে স্যার, আমি মনে রাখব যে আপনার নাম {name}!"

    if any(phrase in message for phrase in ["amar nam ki", "amar name ki"]):
        if chat_id in ai_memory and 'user_name' in ai_memory[chat_id]:
            return f"আপনার নাম হলো {ai_memory[chat_id]['user_name']}! আমি কি আমার স্যারের নাম ভুলতে পারি?"
        return "স্যার, আপনি তো এখনও আমাকে আপনার নাম বলেননি!"

    notes_content = ""
    try:
        with open('protista.txt', 'r', encoding='utf-8') as file:
            notes_content = file.read()
    except:
        pass

    prompt = f"""
    তুমি একজন অত্যন্ত স্মার্ট এবং বন্ধুসুলভ AI শিক্ষক। তুমি ক্লাসের ছাত্রদের সাহায্য করার জন্য তৈরি হয়েছো।
    সব প্রশ্নের উত্তর তুমি বাংলায়, খুব সহজে এবং গল্পের মতো করে বুঝিয়ে দেবে।

    নিচে 'কিংডম প্রোটিস্টা' সম্পর্কে একটি নোটস দেওয়া হলো:
    {notes_content}

    ছাত্রের বর্তমান প্রশ্ন: "{user_message}"

    নির্দেশনা:
    ১. যদি ছাত্রের প্রশ্ন প্রোটিস্টা সম্পর্কে হয়, তবে অবশ্যই ওপরের নোটস থেকে তথ্য নিয়ে খুব সুন্দর করে গুছিয়ে উত্তর দেবে। হুবহু কপি না করে মানুষের মতো বুঝিয়ে বলবে।
    ২. যদি প্রশ্নটি অঙ্কের, বিজ্ঞানের বা অন্য কোনো শিক্ষামূলক বিষয়ের হয়, তবে তুমি তোমার নিজের বিশাল জ্ঞান ব্যবহার করে উত্তর দেবে।
    """

    try:
        response = model.generate_content(prompt)
        return response.text.replace('\n', '<br>')
    except Exception as e:
        return "দুঃখিত স্যার, এই মুহূর্তে আমার ব্রেনের সার্ভারে একটু সমস্যা হচ্ছে। দয়া করে একটু পর আবার চেষ্টা করুন।"

@app.route('/api', methods=['POST'])
def chat_api():
    return jsonify({
        'status': 'success',
        'reply': ai_brain(request.form.get('message', ''), request.form.get('chat_id', 'default_chat'))
    })

@app.route('/', methods=['GET'])
def home():
    return "Smart AI Tutor Server is Running Perfectly with Gemini Brain!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
