from flask import Flask, jsonify, request, render_template_string
import urllib.request
import json
import os

app = Flask(__name__)

whitelist_data = {}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="utf-8">
    <title>LetterX Whitelist System</title>
    <style>
        body { font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 40px; background: #050505; color: #f1f1f1; }
        .container { max-width: 600px; margin: 0 auto; background: #0d0d0d; padding: 32px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.8); border: 1px solid #1a1a1a; }
        h2 { margin-top: 0; color: #ffffff; border-bottom: 1px solid #222222; padding-bottom: 12px; font-weight: 700; letter-spacing: 0.5px; }
        input[type="text"] { width: 70%; padding: 12px 14px; background: #141414; border: 1px solid #282828; color: #fff; border-radius: 6px; box-sizing: border-box; outline: none; }
        input[type="text"]:focus { border-color: #444; }
        button { width: 27%; padding: 12px; background: #ffffff; color: #000000; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; transition: 0.2s; }
        button:hover { background: #dcdcdc; }
        ul { list-style: none; padding: 0; margin-top: 24px; }
        li { background: #121212; padding: 14px 18px; margin: 10px 0; border-radius: 6px; display: flex; justify-content: space-between; align-items: center; border-left: 4px solid #ffffff; border-top: 1px solid #1c1c1c; border-right: 1px solid #1c1c1c; border-bottom: 1px solid #1c1c1c; }
        a { color: #ff4d4d; text-decoration: none; font-weight: bold; font-size: 14px; }
        a:hover { text-decoration: underline; }
        .error { color: #ff4d4d; background: rgba(255, 77, 77, 0.08); border: 1px solid rgba(255, 77, 77, 0.2); padding: 12px; border-radius: 6px; font-size: 14px; }
        .success { color: #00ff88; background: rgba(0, 255, 136, 0.08); border: 1px solid rgba(0, 255, 136, 0.2); padding: 12px; border-radius: 6px; font-size: 14px; }
        h3 { color: #aaa; font-size: 16px; margin-top: 28px; font-weight: 600; }
    </style>
</head>
<body>
    <div class="container">
        <h2>LetterX Whitelist System</h2>
        
        {% if msg %}
            <p class="{{ msg_type }}">{{ msg }}</p>
        {% endif %}

        <form method="POST" action="/add">
            <input type="text" name="username" placeholder="Roblox Kullanıcı Adı..." required>
            <button type="submit">Ekle</button>
        </form>
        
        <h3>Whitelistteki Oyuncular</h3>
        <ul>
            {% for uid, uname in whitelist.items() %}
                <li>
                    <span><strong style="color:#fff;">{{ uname }}</strong> <small style="color:#666;">(ID: {{ uid }})</small></span>
                    <a href="/remove/{{ uid }}">Kaldır</a>
                </li>
            {% else %}
                <p style="color:#555; font-size:14px;">Henüz kimse eklenmedi.</p>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
"""

def get_roblox_user_info(username):
    try:
        url = "https://users.roblox.com/v1/usernames/users"
        data = json.dumps({"usernames": [username], "excludeBannedUsers": True}).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            if result.get("data") and len(result["data"]) > 0:
                user_data = result["data"][0]
                return user_data["id"], user_data["name"]
    except Exception as e:
        print("API Hatası:", e)
    return None, None

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, whitelist=whitelist_data, msg=None)

@app.route('/add', methods=['POST'])
def add():
    username = request.form.get('username').strip()
    uid, real_name = get_roblox_user_info(username)
    
    if uid:
        whitelist_data[uid] = real_name
        msg = f"'{real_name}' başarıyla Whitelist'e eklendi!"
        msg_type = "success"
    else:
        msg = f"'{username}' adında bir Roblox oyuncusu bulunamadı!"
        msg_type = "error"
        
    return render_template_string(HTML_TEMPLATE, whitelist=whitelist_data, msg=msg, msg_type=msg_type)

@app.route('/remove/<int:uid>')
def remove(uid):
    if uid in whitelist_data:
        del whitelist_data[uid]
    return render_template_string(HTML_TEMPLATE, whitelist=whitelist_data, msg="Kullanıcı Whitelist'ten kaldırıldı.", msg_type="success")

@app.route('/check')
def check():
    uid_str = request.args.get('userid')
    try:
        uid = int(uid_str)
        if uid in whitelist_data:
            return jsonify({"status": "allowed", "username": whitelist_data[uid]})
    except:
        pass
    return jsonify({"status": "denied"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
