from flask import Flask
from werkzeug.contrib.fixers import ProxyFix
app = Flask(__name__)


import elastic_web_interface.views

# Use the fixer
app.wsgi_app = ProxyFix(app.wsgi_app)

'''
if __name__ == "__main__":
    app.run()
'''
