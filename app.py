import os
from flask import Flask, request, render_template_string, render_template
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
    return render_template('index.html')

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
          "text": "この問題を解いてください。問題文を再び出力しないでください。問題でなければ画像について解説してください"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": str(image_data2)
          }
        }
      ]
    }
  ] ,           max_tokens=3000,
        )
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_ACCOUNT, GMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        response = response.choices[0].message.content
        result=str(response)
        return render_template_string("""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        
    </head>
    <body>
        <h1>結果:</h1>
        <p>{{ result }}</p>
        <form action="{{ url_for('index') }}" method="get">
            <button type="submit">トップページに戻る</button>
        </form>
    </body>
    </html>
    """, result=result)


    except Exception as e:
        return f"エラー: {str(e)}"

@app.route('/<path:subpath>')
def show_text(subpath):
    try:
        with open(f'texts/{subpath}.txt', 'r', encoding='utf-8') as file:
            content = file.read()
        return render_template('text_display.html', content=content)
    except FileNotFoundError:
        return render_template('error.html', message="ファイルが見つかりません"), 404
if __name__ == '__main__':
    aport = int(os.environ.get('PORT', 80))  # PORT環境変数からポートを取得。デフォルトは80。
    app.run(host='0.0.0.0', port=port)
