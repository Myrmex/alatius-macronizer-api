import sys
from flask import Flask, request
# TODO: comment out the mock Macronizer
from macronizer import Macronizer

# macronizer
MACRONIZER_LIB = '/usr/local/latin-macronizer'
sys.path.append(MACRONIZER_LIB)
# TODO: enable this
# from macronizer import Macronizer

app = Flask(__name__)

# GET /test:
# input: nothing
# output: { result: string }
@app.route('/test', methods=['GET'])
def test():
    return {"result": "test works!"}


def argToBool(arg):
    if (arg == "1" or arg == 1):
        return True
    else:
        return False

# POST /macronize:
# input: { text: string, maius?: boolean, utov?: boolean, itoj?: boolean}
# output: { result: string, error?: string }
@app.route('/macronize', methods=['POST'])
def macronize():
    content_type = request.headers.get('Content-Type')
    if (content_type != "application/json"):
        return 'Content-Type not supported', 400

    r = request.json
    maius = argToBool(r['maius'])
    utov = argToBool(r['utov'])
    itoj = argToBool(r['itoj'])
    text = r['text']
    if not text:
        return {result: ""}
    try:
        macronizer = Macronizer()
        macronizer.settext(text)
        result = macronizer.gettext(True, maius, utov, itoj, markambigs=False)
    except Exception as ex:
        return {"error": ex.args[0], "result": ""}
    return {"result": result}


# ----------------------------------
# development mode
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=105)

# production mode (requires pip install waitress)
if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=105)
