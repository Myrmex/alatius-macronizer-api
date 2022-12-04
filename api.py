import sys
import os
from flask import Flask, request
# TODO: comment out the mock Macronizer
from macronizer import Macronizer

# macronizer
MACRONIZER_LIB = "/usr/local/latin-macronizer"
sys.path.append(MACRONIZER_LIB)
# TODO: enable this
# from macronizer import Macronizer

app = Flask(__name__)

# GET /test:
# input: nothing
# output: { result: string }


@app.route("/test", methods=["GET"])
def test():
    print("test invoked")
    return {"result": "test works!"}


def getSwitch(dct, key):
    if (key not in dct):
        return False
    if (dct[key] == True or dct[key] == "true" or dct[key] == "1" or dct[key] == 1):
        return True
    else:
        return False

# POST /macronize:
# input: { text: string, maius?: boolean, utov?: boolean, itoj?: boolean, ambigs?: boolean}
# output: { result: string, error?: string }


@app.route("/macronize", methods=["POST"])
def macronize():
    content_type = request.headers.get("Content-Type")
    if (content_type != "application/json"):
        return "Content-Type not supported", 400

    dct = request.json
    if ("text" not in dct or not dct["text"]):
        return {"result": ""}

    text = dct["text"]
    maius = getSwitch(dct, "maius")
    utov = getSwitch(dct, "utov")
    itoj = getSwitch(dct, "itoj")
    ambigs = getSwitch(dct, "ambigs")
    try:
        macronizer = Macronizer()
        macronizer.settext(text)
        result = macronizer.gettext(True, maius, utov, itoj, markambigs=ambigs)
    except Exception as ex:
        return {"error": ex.args[0], "result": ""}
    return {"result": result, "maius": maius, "utov": utov, "itoj": itoj, "ambigs": ambigs}


# ----------------------------------

if __name__ == "__main__":
    mode = os.environ.get("MACRONIZER_API_MODE", "production")
    print("starting macronizer API in " + mode)

    # production mode (requires pip install waitress)
    if mode == "production":
        from waitress import serve
        serve(app, host="0.0.0.0", port=105)
    else:
        app.run(host="0.0.0.0", port=105)
