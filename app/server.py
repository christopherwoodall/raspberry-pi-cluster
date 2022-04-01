#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import json
import urllib.parse

from pathlib import Path

import flask
from flask import Flask, request, jsonify, render_template


app = Flask(__name__, static_folder='./www/assets', template_folder='./www')


def render_html(html_file, **kwargs):
    return Path(html_file).read_text(encoding='utf-8')


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        post_data = json.loads(request.data)
        exit(1)
    else:
        return render_html('./www/index.html')


def compile_sass():
    from sass import compile
    scss_build_path = Path('./www/assets/scss/style.scss')
    Path( scss_build_path ).write_text(
        compile(
            filename=scss_build_path,
            output_style='compressed'
        )
    )
    # compile(dirname=('sass', 'css'), output_style='compressed')


if __name__ == '__main__':
    compile_sass()
    # app.run(
    #     debug = True,
    #     host="0.0.0.0",
    #     ssl_context=('./ssl/cert.pem', './ssl/key.pem')
    #     #ssl_context='adhoc'
    # )
    app.run(
        debug = True,
        host="0.0.0.0"
    )
