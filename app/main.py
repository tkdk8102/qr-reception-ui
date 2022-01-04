from flask import Flask, abort, render_template, request, redirect, url_for
import hashlib, uuid
import MySQLdb
import os
import secrets

app = Flask(__name__, static_folder='static', static_url_path='')

@app.route('/')
def favicon():
    return '<html><body>Hello</body></html>'
