from flask import *
from hashlib import sha3_512
from subprocess import Popen, PIPE
import json

def check_user_query(query: str, username: str) -> str:
    p = Popen(["/bin/sh"], stderr=PIPE, stdout=PIPE, stdin=PIPE)
    stdout, stderr = p.communicate(f"echo user {username} {query}".encode())
    return stdout.decode()

app = Flask(__name__)
app.config["DB"] = {}

app.secret_key = "hrifhidhgirfdhwgifdgrfdhwbvhjfbdwhgjvbfdhbgvkfbfhbshgrhesgfhrjefqfkrh"

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template("index.html")
    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        flash("Username or password is empty", "error")
        return redirect(url_for("index"))

    if len(password) < 5:
        flash("Password length must be at least 5 characters", "warning")
        return redirect(url_for("index"))
    
    if username in app.config["DB"]:
        if password == app.config["DB"][username]["password"]:
            resp = Response(render_template_string('<meta http-equiv="refresh" content="0; url=/dashboard" />'))
            sess = sha3_512(username.encode("utf-16") + password.encode("utf-32") + b"SAlT63696663").hexdigest()
            app.config["DB"][username]["token"] = sess
            resp.set_cookie("token", sess)
            return make_response(resp)
        
        flash("Invalid credentials !", "error")
        return redirect(url_for("index"))
    else:
        resp = Response(render_template_string('<meta http-equiv="refresh" content="0; url=/dashboard" />'))
        sess = sha3_512(username.encode("utf-16") + password.encode("utf-32") + b"SAlT63696663").hexdigest()
        app.config["DB"][username] = {
            "password": password,
            "token": sess,
            "profile_infos": {
                "username": username,
                "token": sess,
                "age": None,
                "pin": "1111-1111-6892",
                "is_pinned_on_admin_pannel": False,
                "is_banned": False,
                "is_leader": False,
                "is_muted": False,
                "is_authentificated_with_sso": False,
                "group": {
                    "user_basic": True,
                    "is_online": True,
                    "have_backup": None,
                    "friends": [],
                    "is_behind_proxy": False
                }
            }
        }
        resp.set_cookie("token", sess)
        return make_response(resp)
    flash("Registration OK", "success")
    return redirect(url_for("index"))

@app.route('/dashboard')
def dashboard():
    if request.cookies.get("token") == None:
        return redirect(url_for("register"))
    for (user, vals) in app.config["DB"].items():
        if request.cookies.get("token") == vals.get("token"):
            if vals.get("profile_infos", {}).get("is_leader", False):
                return render_template("dashboard.html", pathTo = "/usersList", titleTo = "Users List", hidden = "")
            return render_template("dashboard.html", hidden = "hidden")
    return render_template("index.html")

@app.route('/profil', methods=["GET", "POST"])
def profil():
    if request.cookies.get("token") == None:
        return redirect(url_for("register"))
    for (user, vals) in app.config["DB"].items():
        if request.cookies.get("token") == vals.get("token"):
            if request.method == 'GET':
                return render_template_string(open("./templates/profil.html", 'rb').read().decode().replace("===dictJson===", json.dumps(vals.get("profile_infos", {}))), username = vals.get("profile_infos", {}).get("username", user), age = vals.get("profile_infos", {}).get("age"))
            else:
                newProfileInfos = request.json
                app.config["DB"][user]["profile_infos"] = newProfileInfos

    return render_template("index.html")

@app.route('/profil.js')
def profile_js():
    return send_file("./static/profile.js")


@app.route("/logout")
def logout():
    if request.cookies.get("token") == None:
        return redirect(url_for("register"))
    for (user, vals) in app.config["DB"].items():
        if request.cookies.get("token") == vals.get("token"):
            resp = Response(render_template("index.html"))
            resp.delete_cookie("token")
            app.config["DB"].pop(user)
            return make_response(resp)
    return render_template("index.html")

@app.route('/usersList', methods=["GET", "POST"])
def usersList():
    if request.cookies.get("token") == None:
        return redirect(url_for("register"))
    for (user, vals) in app.config["DB"].items():
        if request.cookies.get("token") == vals.get("token"):
            if vals.get("profile_infos", {}).get("is_leader", False):
                if request.method == "GET":
                    resp = Response(render_template("usersList.html"))
                    return make_response(resp)
                elif request.is_json:
                    return json.dumps({"query_response": check_user_query(request.json.get("query_user"), user)})
            resp = Response(render_template("index.html"))
            return make_response(resp)
    return render_template("index.html")

if __name__== '__main__':
    app.run(host="0.0.0.0", port=38081)
