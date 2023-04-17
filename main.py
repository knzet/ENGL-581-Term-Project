# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
from urllib.parse import urlparse, parse_qs
import openai
from dotenv import load_dotenv
import os

load_dotenv() # you need to set OPENAI_API_KEY in .env

hostName = "localhost"
serverPort = 3000
# link to test mp3 download and play
# https://drive.google.com/file/d/1cgwNhWnP-vaHDR10mLdFBRcLVvuedG5o/view?usp=share_link

filename = "index.html"
with open(filename) as f:
    content = f.readlines()

# Show the file contents line by line.
# We added the comma to print single newlines and not double newlines.
# This is because the lines contain the newline character '\n'.
# for line in content:
#     print(line),


# ChatGPT, verb. Definition: To do anything involving GPT-3. Example sentence: "I'm going to chatGPT with my friends tonight." "What are you going to chatGPT about?" "I'm going to chatGPT about how I'm going to chatGPT with my friends tonight."
# *example sentence was chatGPTed by GPT-3
def chatGpt(message):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user",
                "content": "I am a CS major at RIT"},  # basically, paste your resume here, might need "This is my resume:" in front
            {"role": "user", "content": "I want you to answer questions as if you were me, using the information in my resume."},
            {"role": "user",
                "content": "Why should I hire you to work on AI language models?"},
        ]
    )
    print(response)
    print(response.choices[0].message.content)
    return response.choices[0].message.content


class MyServer(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        # parsed_url = urlparse(self.path)
        print(self)

    def do_GET(self):
        if self.path.find("question=") != -1: # "submit" button adds to query string
            print("Button clicked")
            # grab the question from the url
            parsed_url = urlparse(self.path)
            # print(parsed_url.query)
            question = parsed_url.query.split("question=")[1].split(
                " ")[0].replace("%20", " ").replace("+", " ")
            print(question)
            res = chatGpt(question)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')

            self.end_headers()

            for line in content:
                self.wfile.write(bytes(line, "utf-8"))

            self.wfile.write(bytes("<p>Question: %s</p>" % question, "utf-8"))
            self.wfile.write(bytes("<br>Response: %s" % res, "utf-8"))
            self.wfile.write(bytes("</div", "utf-8"))
            self.wfile.write(bytes("</body></html>", "utf-8"))
        elif self.path == "/":

            self.send_response(200)
            self.send_header('Content-type', 'text/html')

            # use this to return link to mp3 file
            # self.send_header('Content-type', 'application/json')

            self.end_headers()

            for line in content:
                self.wfile.write(bytes(line, "utf-8"))
            self.wfile.write(bytes("</body></html>", "utf-8"))
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            for line in content:
                self.wfile.write(bytes(line, "utf-8"))
                self.wfile.write(bytes("</body></html>", "utf-8"))


if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
