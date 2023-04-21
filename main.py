# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
from urllib.parse import urlparse, parse_qs
import openai
from dotenv import load_dotenv
import os
import base64
from gradio_client import Client

global fullttsaudiofilename
fullttsaudiofilename=""
resumeFile = "resume.txt"
with open(resumeFile) as f:
    resumeText = f.read()

gptLimit = "Limit responses to 2 sentences."

load_dotenv()  # you need to set OPENAI_API_KEY in .env
openai.api_key = os.getenv("OPENAI_API_KEY")  # print os.env for debug
huggingfacekey = os.getenv("HUGGINGFACE_API_KEY")  # print os.env for debug

hostName = "localhost"
serverPort = 3000
client = Client("daw1882/tortoise", hf_token=huggingfacekey)

filename = "index.html"
with open(filename) as f:
    content = f.readlines()


def batch(fullText, question):
    # declare a byte array
    fullmp3Data = bytearray()
    # give the mp3s random filenames
    audioname = question+"_"+fullText+".mp3"

    # str(int(time.time() % 10000))+".mp3"
    # open file in write byte mode
    wav_file = open(audioname, "wb")
    batches = fullText.split(".")  # split by sentence

    # print(client.view_api())

    for batch in batches:
        # call TTS on individual sentences, append to byte array
        fullmp3Data.extend(TTS(batch))

    # write the byte array to a file
    wav_file.write(fullmp3Data)
    wav_file.close()
    
    return audioname

# ask nicely for text to be converted into voice cloned speech
# wait a while for the response
def TTS(text):
    # ttsaudioPath=client.predict(["dade-sample1.wav", "dade-sample2.wav"], False, "Hello", "ultra_fast", api_name="/custom")
    # print(ttsaudioPath)
    ttsaudioPath="./dade-sample1.wav"
    ttsaudio = open(ttsaudioPath, "rb").read()
    return ttsaudio  # response


# ChatGPT, verb. Definition: To do anything involving GPT-3. Example sentence: "I'm going to chatGPT with my friends tonight." "What are you going to chatGPT about?" "I'm going to chatGPT about how I'm going to chatGPT with my friends tonight."
# *example sentence was chatGPTed by GPT-3


def chatGpt(message):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user",
                "content": resumeText},  # basically, paste your resume here, might need "This is my resume:" in front
            {"role": "user", "content": "I want you to answer questions as if you were me, using the information in my resume."+gptLimit},
            {"role": "user",
                "content": message},
        ]
    )
    print(response)
    print(response.choices[0].message.content)
    return response.choices[0].message.content


class MyServer(BaseHTTPRequestHandler):
    # def do_POST(self):
    #     self.send_response(200)
    #     # parsed_url = urlparse(self.path)
    #     print("POST request received")
    #     print(self)

    # render a page :)
    def renderHTML(self, file):
        with open("./"+file) as f:
            content = f.readlines()

        # headers
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        # page content
        for line in content:
            self.wfile.write(bytes(line, "utf-8"))

        # /html
        self.wfile.write(bytes("</body></html>", "utf-8"))

    def do_GET(self):
        global fullttsaudiofilename
        if self.path.find("question=") != -1:  # "submit" button adds to query string
            print("Button clicked")
            # grab the question from the url
            parsed_url = urlparse(self.path)
            # print(parsed_url.query)
            question = parsed_url.query.split("question=")[1].split(
                " ")[0].replace("%20", " ").replace("+", " ")
            print(question)

            # input text -> chatbot response text
            # chatGpt(question)
            res = "Sample chatgpt response. This is what the chatbot said."
            # chatbot response text -> cloned voice audio
            fullttsaudiofilename = batch(res, question)  # batch the TTS calls

            # give some info about the file
            # f = open(fullttsaudiofilename, 'rb')
            # st = os.fstat(f.fileno())
            # length = st.st_size

            self.send_response(200)
            self.send_header('Content-type', 'text/html')

            self.end_headers()
            for line in content:
                self.wfile.write(bytes(line, "utf-8"))

            self.wfile.write(bytes("<div class=\"question\">Question: %s</div>" %
                             question.replace("%3F", "?"), "utf-8"))
            self.wfile.write(bytes("<br><div class=\"response\"> %s</div>" %
                             res.replace("%3F", "?"), "utf-8"))
            self.wfile.write(bytes(
                '<audio autoplay controls><source src="temp.mp3" type="audio/mpeg"><source src="', "utf-8"))
            self.wfile.write(bytes('temp.mp3', "utf-8"))  # audio filename
            self.wfile.write(bytes(
                '" type="audio/mpeg">Your browser does not support the audio element.</audio>', "utf-8"))
            self.wfile.write(bytes("</div", "utf-8"))
            self.wfile.write(bytes("</body></html>", "utf-8"))
            # # self.send_response(200)

        elif self.path == "/":
            print("index"+".html")
            print('test')
            self.renderHTML("index.html")

        elif self.path == "/temp.mp3":
            f = open(fullttsaudiofilename, 'rb')
            st = os.fstat(f.fileno())
            length = st.st_size
            data = f.read()
            self.send_response(200)
            self.send_header('Content-type', 'audio/mpeg')
            self.send_header('Content-Length', length)
            # self.send_header('ETag', '"{0}"'.format(md5.hexdigest()))
            self.send_header('Accept-Ranges', 'bytes')
            # self.send_header('Last-Modified', time.strftime(
            #     "%a %d %b %Y %H:%M:%S GMT", time.localtime(os.path.getmtime('temp.mp3'))))
            self.end_headers()
            # self.wfile.open()
            self.wfile.write(data)
            
        elif self.path == "/styles.css":
            self.send_response(200)
            stylesheet=open("styles.css", "rb")
            self.wfile.write(stylesheet.read())                
            
        elif os.path.exists(self.path.replace("/", "").replace(".html", "")+".html"):
            self.renderHTML(self.path.replace(
                "/", "").replace(".html", "")+".html")

        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(
                bytes("<html><head><title>404</title></head>", "utf-8"))
            self.wfile.write(bytes("<body><p>404 Not Found</p>", "utf-8"))
            self.wfile.write(
                bytes("<p>The resource could not be found.</p></body></html>", "utf-8"))


if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))
    fullttsaudiofilename="temp.mp3"
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
