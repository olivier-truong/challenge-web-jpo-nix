import os
from flask import *
from json import loads, dumps
from random import randbytes
from base64 import b64encode, b64decode

def load_tokens():
    if not os.path.exists("tokens.json"):
        initial_data = {
            "valid_tokens": {},
            "tokens_history": {}
        }
        open("tokens.json", "wb").write(dumps(initial_data).encode())
    return loads(open("tokens.json", "rb").read().decode())

app = Flask(__name__)
app.config["token_prefix"] = "1904_2001"
app.config["tokens"] = load_tokens()
app.config["eventId"] = "JPO Nix 2025"
app.secret_key = os.urandom(24)



def create_token():
    """
    Génère un token :
    - token_id : envoyé au client (cookie)
    - token_value : secret, reste sur le serveur
    """
    token_id = randbytes(3).hex()
    token_value = app.config["token_prefix"] + "_" + randbytes(3).hex()

    return token_id, token_value


def save_tokens():
    open("tokens.json", "wb").write(
        dumps(app.config["tokens"]).encode()
    )


def get_valid_tokens():
    return app.config["tokens"]["valid_tokens"]


def invalidate_token_id(token_id):
    tokens = get_valid_tokens()
    if token_id in tokens:
        app.config["tokens"]["tokens_history"][token_id] = tokens[token_id]
        del tokens[token_id]
        save_tokens()



@app.route('/')
def index():

    user_token_id = request.cookies.get("token_id", None)

    # --- Si utilisateur n’a PAS encore de token ---
    if user_token_id is None:
        token_id, token_value = create_token()
        get_valid_tokens()[token_id] = token_value
        save_tokens()

        r = make_response(
            render_template("index.html",
                            eventId=app.config["eventId"],
                            tokenRandomIci=b64encode(b64encode(b64encode(token_value[10:].encode()))).decode())
        )
        r.set_cookie(
            "token_id",
            token_id,
            max_age=60*60*24*365*2,
            httponly=True,
            secure=True
        )
        return r
    # --- Si utilisateur a déjà un token ---
    else:
        if user_token_id in get_valid_tokens():
            return render_template("index.html",
                eventId=app.config["eventId"],
                tokenRandomIci=b64encode(b64encode(b64encode(get_valid_tokens()[user_token_id][10:].encode()))).decode())
        else:
            token_id, token_value = create_token()
            get_valid_tokens()[token_id] = token_value
            save_tokens()
            r = make_response(
            render_template("index.html",
                eventId=app.config["eventId"],
                tokenRandomIci=b64encode(b64encode(b64encode(token_value[10:].encode()))).decode())
            )
            r.set_cookie(
                "token_id",
                token_id,
                max_age=60*60*24*365*2,
                httponly=True,
                secure=True
            )
            return r


@app.route('/verify')
def verify():
    user_input = request.args.get('token', '')

    for token_id, token_secret in get_valid_tokens().items():

        if user_input == token_secret:
            invalidate_token_id(token_id)
            flash("Bravo ! Votre token est valide. Vous remportez l'épreuve.", "success")
            return redirect(url_for('index'))

    if user_input in app.config["tokens"]["tokens_history"].values():
        flash("Bah alors là c'est vraiment pas bien de réutiliser un token déjà utilisé...", "warning")
    else:
        flash("Ce token n'est pas valide. Merci de réessayer.", "error")

    return redirect(url_for('index'))


@app.route('/favicon.ico')
def favicon():
    return send_file("static/favicon.ico")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
