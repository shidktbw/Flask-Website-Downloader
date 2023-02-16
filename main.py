import os
import zipfile
import requests
from flask import Flask, request, send_file, render_template
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    if not url.startswith('http'):
        url = 'https://' + url

    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        url = urlunparse(('https',) + parsed_url[1:])
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract CSS and JS file URLs
    css_urls = [link['href'] for link in soup.find_all('link') if link.get('href') and link.get('rel') == ['stylesheet']]
    js_urls = [script['src'] for script in soup.find_all('script') if script.get('src')]

    # Download HTML, CSS, and JS files
    html_content = response.text
    css_content = ''
    js_content = ''
    for css_url in css_urls:
        if not css_url.startswith('http'):
            css_url = urlunparse(('https', parsed_url.netloc, css_url, '', '', ''))
        css_response = requests.get(css_url)
        css_content += css_response.text
    for js_url in js_urls:
        if not js_url.startswith('http'):
            js_url = urlunparse(('https', parsed_url.netloc, js_url, '', '', ''))
        js_response = requests.get(js_url)
        js_content += js_response.text


    # Create ZIP archive
    archive_name = 'source.zip'
    with zipfile.ZipFile(archive_name, 'w') as archive:
        archive.writestr('index.html', html_content)
        for i, css_url in enumerate(css_urls):
            archive.writestr(f'style{i}.css', css_content)
        for i, js_url in enumerate(js_urls):
            archive.writestr(f'script{i}.js', js_content)

    # Send ZIP archive as a file download
    return send_file(archive_name, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
