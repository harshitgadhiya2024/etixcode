from flask import (flash, Flask, redirect, render_template, request,
                   session, url_for, send_file, jsonify, send_from_directory)

from werkzeug.utils import secure_filename
import os
import requests, logging
import time
import json
import random
import asyncio
from playwright.async_api import async_playwright
import pandas as pd

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = set(['csv', 'xlsx'])

# SqlAlchemy Database Configuration With Mysql
app.config["SECRET_KEY"] = "sdfsf65416534sdfsdf4653"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
secure_type = "http"
app.config["already"] = []
app.config["unique_user"] = []

# server_file_name = "server.log"
# logging.basicConfig(filename=server_file_name, level=logging.DEBUG)

proxy_config = {
    "server": "http://geo.iproyal.com:12321",
    "username": "plural2356",
    "password": "dorbu7r62t9k"
}

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.48",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-A505FN) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 12_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Mobile/15E148 Safari/605.1"
]

app.config["all_outputs"] = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

async def capture_network_requests(url, loop_value, value_min, unique_name):
    async with async_playwright() as p:
        random_user_agent = random.choice(user_agents)
        print(f"Using User-Agent: {random_user_agent}")
        browser = await p.chromium.launch(headless=True, proxy=proxy_config)
        context = await browser.new_context(user_agent=random_user_agent)
        page = await context.new_page()
        all_requests = []
        async def log_response(response):
            if "https://etix.com/ticket/api/online/search" == response.url:
                try:
                    json_response = await response.json()
                    # get_data = json.dumps(json_response, indent=2)
                    a = json_response.get("events")
                    all_requests.extend(a)
                    print(f"Captured response for {response.url}: {json.dumps(json_response, indent=2)}")
                except Exception as e:
                    print(f"Failed to decode JSON response for {response.url}: {e}")

        page.on("response", log_response)

        # Open the website
        await page.goto(url, wait_until="networkidle", timeout=9000000)
        print("load site")
        time.sleep(50)

        for var in range(1, loop_value):
            await page.get_by_role("button", name="Show More").click()
            time.sleep(15)

        # Wait for some time to let all requests complete (adjust as needed)
        await asyncio.sleep(10)

        seen = set()
        unique_data = []

        for event in all_requests:
            if event["eventId"] not in seen:
                unique_data.append(event)
                seen.add(event["eventId"])
        
        flag = True
        while flag:
            output_number = random.randint(1111, 9999)
            filename = f"requests_log{output_number}.json"
            if filename not in app.config["already"]:
                flag = False

        app.config["output_files"]= "static/output_files/"
        filepath = f"static/output_files/{filename}"
        with open(filepath, "w") as f:
            json.dump(unique_data[:value_min], f, indent=4)

        # download_file_path = f"http://127.0.0.1:5000/download/{filename}"
        app.config["all_outputs"][unique_name].append({"url": url, "output_link": unique_data[:value_min]})

        await browser.close()

@app.route('/download/<filename>')
def download_image_path(filename):
    return send_from_directory(app.config['output_files'], filename, as_attachment=True)


@app.route("/", methods=["GET", "POST"])
def getdata():
    try:
        start_time = time.time()
        if request.method=="POST":
            flag = True
            while flag:
                name_number = random.randint(11111, 99999)
                unique_name = f"new_number_{name_number}"
                if unique_name not in app.config["unique_user"]:
                    flag = False

            input_data = request.files['uploadfile']
            app.config["all_outputs"][unique_name] = []
            path = app.config["UPLOAD_FOLDER"]

            if 'file' not in request.files:
                flash('No file part', "danger")
                redirect(url_for('getdata', _external=True, _scheme=secure_type))

            if input_data.filename == '':
                flash('No resume selected for uploading', "danger")
                redirect(url_for('getdata', _external=True, _scheme=secure_type))

            exten = ""
            if input_data and allowed_file(input_data.filename):
                filename = secure_filename(input_data.filename)
                exten = filename.split(".")[-1]
                input_data.save(os.path.join(path, filename))
                input_data_path = os.path.join(path, filename)
            else:
                flash('This file format is not supported.....', "danger")
                redirect(url_for('getdata', _external=True, _scheme=secure_type))


            if exten=="xlsx":
                df = pd.read_excel(input_data_path)
            else:
                df = pd.read_csv(input_data_path)

            all_list = list(df["urls"])
            all_counts = list(df["counts"])

            for url, value_min in zip(all_list, all_counts):
                loop_value = int(value_min / 12) + 1
                value_min = 12*loop_value
                asyncio.run(capture_network_requests(url=url, loop_value=loop_value, value_min=value_min, unique_name=unique_name))


            all_output_data = app.config["all_outputs"][unique_name]
            # df_main = pd.DataFrame(all_output_data)
            # df_name = f"{app.config['output_files']}{unique_name}.csv"
            # df_main.to_csv(df_name, index=False)
            # download_file_path = f"http://127.0.0.1:5000/download/{unique_name}.csv"

            flash("Please download your report", "success")
            # return render_template('index.html', output_filename = download_file_path)
            return {"output_data": all_output_data}
        else:
            return {"message": "Get method not allowed"}
        

    except Exception as e:
        message = "Server Not Responding"
        print(e)
        app.logger.debug(f"Error in main route: {e}")
        return jsonify(message=message)

@app.route("/download_logs", methods=['GET'])
def download_logs():
    file = os.path.abspath("result.json")
    return send_file(file, as_attachment=True)

@app.route("/view_logs", methods=['GET'])
def view_logs():
    try:
        server_file_name = "server.log"
        file = os.path.abspath(server_file_name)
        lines = []
        with open(file, "r") as f:
            lines += f.readlines()
        return render_template("logs.html", lines=lines)

    except Exception as e:
        app.logger.debug(f"Error in show log api route : {e}")
        return render_template("index.html")

if __name__ == "__main__":
    app.run()
