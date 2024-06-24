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


app = Flask(__name__)



if __name__ == '__main__':
    app.run()
