from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "হ্যালো! আমার পাইথন অ্যাপ সাকসেসফুলি হোস্ট হয়েছে!"

if __name__ == '__main__':
    app.run()
