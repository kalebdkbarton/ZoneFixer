from flask import Flask
app = Flask(__name__)
@app.route("/output")
def output():
        return "Hello World!"
if __name__ == "__main__":
        app.run("142.93.86.122",5010)