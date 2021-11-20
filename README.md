CIS 524: Small Parser Cloud Service Project
===

Name: Bradley Dowling
CSUID: 2657649
Grail ID: brdowlin

Time Log Parser
---

Description and Testing
---

This project was made challenging by restricting the use of the regular expression standard library module `re`. Using regular expressions, I could have easily written this program in a handful of lines. I instead tried to take an approach where I treated each part of the line as a type of token. A significant part of the code is validating the format of what I expect to be tokens, and the main function that performs the essential function of tallying the time, `parse_log()` is longer than it otherwise might be because I am keeping track of the time taken by each activity.

Validation
---

I treat dates, times, and then all other characters as the three primary token types in a correctly formatted time log. To validate dates and times, I use the following functions:

```python
def valid_date(d: str) -> bool:
    if not d[0].isdigit():
        return False
    if d.startswith("0"):
        return False
    if "/" not in d:
        return False
    if not d.endswith(":"):
        return False
    dt = tuple(map(lambda x: int(x), d[:-1].split("/")))
    if dt[0] < 1 or dt[0] > 12:
        return False
    if dt[1] < 1 or dt[1] > 31:
        return False
    if dt[2] < 1 or dt[2] > 99:
        return False
    return True

def valid_time(t: str) -> bool:
    if not t[0].isdigit():
        return False
    if t.startswith("0"):
        return False
    if ":" not in t:
        return False
    if not t.endswith("am") and not t.endswith("pm"):
        return False
    if len(t) > 7:
        return False
    hour, rest = t.split(":")
    minute, _ = int(rest[:2]), rest[2:]
    hour = int(hour)
    if hour < 1 or hour > 12:
        return False
    if minute < 0 or minute > 59:
        return False
    return True
```

Dealing with Time Values
---

I convert times to minutes through the day when calculating the difference. The code should be robust against rolling over into the next day. I also convert dates into days into the current century for getting a difference in the number of days in the time log.

```python
def to_minutes(t: str) -> int:
    """
    to_minutes(t: str) -> int

    input:
        - t: A string representing a validated timestamp

    output:
        - int: minutes into the current day
    """
    hour, rest = t.split(":")
    minute, meridiem = int(rest[:2]), rest[2:].lower()
    hour = int(hour)
    if meridiem == "am":
        if hour == 12:
            hour = 0
    if meridiem == "pm":
        if hour < 12:
            hour += 12
    return hour*60 + minute


def time_delta(t1: str, t2: str) -> int:
    """
    time_delta(t1: str, t2: str) -> int

    input:
        - t1: a string representing a timestamp of the form HH:MM[am|pm]
        - t2: a string representing a timestamp of the form HH:MM[am|pm], strictly greater than t1
    output:
        - int: the strictly positive difference between t2 - t1, modulo 1440
    """
    t1 = to_minutes(t1)
    t2 = to_minutes(t2)
    return (t2 - t1) % 1440


def to_days(d: str) -> int:
    """
    to_days(d: str) -> int:

    input:
        - d: a string representing a validated date
    output: 
        - int: days into the current century

    Days = (total days of n-1 months) + days + (total days of n-1 years) + leap years
    """
    mm, dd, yy = map(lambda n: int(n), d.split('/'))
    months = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    days = dd + yy*365 + (yy // 4)
    if mm > 1:
        days += sum(months[:(mm-1)])
    return days


def date_delta(d1: str, d2: str) -> int:
    """
    date_delta(d1: str, d2: str) -> int:

    input:
        - d1: a valid date of the form MM/DD/YY
        - d2: a valid date monotonically larger than d1
    output:
        - int: the difference d2-d1 of elapsed days
    """
    d1 = to_days(d1)
    d2 = to_days(d2)
    return (d2 - d1) % (100 * 365 + 100 // 4)  # days in a century + leap days
```

Tokenizing a Line
---

The __parse_line()__ stores the different token types in a dictionary. A single hyphen character is passed over if encountered, and anything not a valid time or date will be appended to the "comment" key. The timestamp uses a dynamic key name beginning with 't' indicating the position in the line, and the number of time keys in a line. Should there be an odd number of times in a line, there is an error.

```python
def parse_line(line: str) -> dict:
    """
    parse_line(line: str) -> dict

    input:
        - line: a line as a string from the time log file under scrutiny
    output:
        - data: a dictionary containing the different types of tokens in the line

    Tokenizes each line into a date, an even number of timestamps, and a comment string
    """
    tokens = line.split()
    data = {"comment": ""}
    for i, tok in enumerate(tokens):
        if valid_date(tok):
            data["date"] = tok[:-1]
            continue
        if valid_time(tok):
            data[f"t{i}"] = tok
            continue
        if tok == "-":
            continue
        else:
            data["comment"] += f" {tok}"
    return data
```

Extra Functionality
---

There are some additional functions that go beyond the minimum requirements of the project. There is an argument parser for a slightly nicer command line interface, the mean and median time taken per task (the aggregated comments following one time stamp), and maintaining the maximum time taken by any one task in the list. The inclusion of these features made the single pass over the file slightly more complicated. When to decide that a new record was complete was the most involved part of the testing.

```python
def longest_task(records: list) -> tuple:
    """
    longest_task(records: list[tuple]) -> tuple[int, str]

    input:
        - records: a list of time_record tuples (date, duration, task)
    output:
        - (): the maximum duration and the corresponding task or comments
    """
    maxtime = 0
    maxrecord = None
    for r in records:
        if r[1] > maxtime:
            maxtime = r[1]
            maxrecord = r
    return maxrecord


def working_days(records: list) -> tuple:
    """
    working_days(records: list[tuple]) -> tuple[int, int]

    input:
        - records: a list of tuples (date, duration, task)
    output:
        - (int, int): Total number of days worked, total number of days elapsed
    """
    worked = {r[0] for r in records}
    elapsed = date_delta(records[0][0], records[-1][0])
    return worked, elapsed


def record_stats(records: list, total: int, filename: str) -> dict:
    """
    record_stats(filename: str) -> dict:

    input:
        - filename: path to log file
    output:
        - dict: Organized dictionary of statistics and data
    """
    stats = {'filename': filename, 'total': total}
    stats['dates'], stats['elapsed'] = working_days(records)
    stats['durations'] = map(lambda r: r[1], records)
    stats['mean'] = stats['total'] / len(stats['dates'])
    ts = sorted(stats['durations'])
    if len(ts) % 2 == 0:
        stats['median'] = (ts[len(ts) // 2] + ts[len(ts) // 2 + 1]) / 2
    else:
        stats['median'] = ts[len(ts) // 2 + 1]
    stats['longest'] = longest_task(records)
    return stats


def format_output(stats: dict) -> list:
    """
    format_output(stats: dict) -> str:

    input:
        - stats: dictionary of statistics collected from time log
    output:
        - list: formatted output for terminal or template rendering
    """
    output = [f"Statistics for {stats['filename']}:"]
    output.append(f"{'-'*(len(stats['filename'])+16)}")

    h, m = divmod(stats['total'], 60)
    output.append(f"Total time spent: {h} hours, {m} minutes")
    output.append(f"Total days worked: {len(stats['dates'])}")
    output.append(f"Total days elapsed: {stats['elapsed']}\n")

    h, m = divmod(stats['mean'], 60)
    output.append(f"Mean time spent per working day: {h:.2f} hours, {m:.2f} minutes")
    h, m = divmod(stats['median'], 60)
    output.append(f"Median time spent: {h:.2f} hours, {m:.2f} minutes\n")

    date, maxtime, task = stats['longest']
    h, m = divmod(maxtime, 60)
    output.append("Longest working session:")
    output.append(f"{date}: {task}")
    output.append(f"Time spent: {h} hours, {m} minutes\n")

    return output


def argparser():
    """Set up argument parser."""
    ap = argparse.ArgumentParser(prog="Time Log Parser")
    ap.add_argument("files",
                    type=str,
                    metavar="FILE",
                    nargs='+',
                    help="Log files to parse")
    return ap
```

Main Function
---

```python
def parse_log(filename: str) -> tuple:
    """
    parse_log(filename: str) -> tuple

    input:
        - filename: a path to a time log file
    output:
        - (time_records, total_time): a tuple of time_records, and the total accumulated time

    time_record -> (date, time spent, accumulated comments)

    Parses the time log file by checking the number of valid tokens in each line.
    Accumulates total time, and saves individual times for each date/task.
    Multiline comments are accumulated together, blank dates are assumed to be the same.
    """
    with open(filename) as f:
        lines = f.readlines()
    if lines[0].lower().strip() != "time log:":
        return -1
    time_record = []
    cur_comment = []
    cur_date = ""
    cur_total = 0
    total_time = 0
    for i, line in enumerate(lines[1:]):
        try:
            parsed = parse_line(line)
            nkeys = len(parsed.keys())
            ts = tuple(filter(lambda k: k.startswith('t'), sorted(parsed.keys())))
            if nkeys == 1:
                comment = parsed['comment'].strip()
                if comment:
                    cur_comment.append(comment)
            if nkeys == 2:
                td = time_delta(parsed[ts[0]], parsed[ts[1]])
                cur_total += td
                total_time += td
                cur_comment = []
            if nkeys == 3:
                td = time_delta(parsed[ts[0]], parsed[ts[1]])
                cur_total += td
                total_time += td
                comment = parsed['comment'].strip()
                if comment:
                    cur_comment.append(comment)
            if nkeys == 4:
                if i == 0:
                    cur_date = parsed['date']
                    comment = parsed['comment'].strip()
                    if comment:
                        cur_comment.append(f"{comment}")
                    td = time_delta(parsed[ts[0]], parsed[ts[1]])
                    cur_total += td
                    total_time += td
                else:
                    if cur_date != parsed['date']:
                        time_record.append((cur_date, cur_total, f"\n{' '*(len(cur_date)+2)}".join(cur_comment)))
                        cur_date = parsed['date']
                        cur_total = 0
                        cur_comment = []
                    td = time_delta(parsed[ts[0]], parsed[ts[1]])
                    cur_total += td
                    total_time += td
                    comment = parsed['comment'].strip()
                    if comment:
                        cur_comment.append(comment)
        except Exception:
            print(f"error on line {i}")
            continue
    return time_record, total_time
```

### Update

Earlier on in the semester when I originally submitted the SmallParser project, there was erroneous logic in the time calculations, where hours and minutes were calculated fully independently of one another, and thus resulted in incorrect times sometimes much larger than the actual time recorded.

During the development of the Flask web service, I identified the bug and made a change so that times were converted directly into "minutes through the day" rather than a 24-hour time clock. The same logic used to convert to a 24-hour clock is used, but instead of returning the hours and minutes discretely in a tuple, the minutes are totaled immediately and then the difference is taken.

Additionally, formatting of the additional outputs has been improved, and the inefficient string concatenations for the comment tokens have been replaced with considerably more efficient list joins. The date is also provided for the most time consuming task(s). Additional statistics are provided in a nicely formatted response. The command line can accept any number of files as arguments, and detailed docstrings have been provided for each function.

Results (CORRECTED)
---

### Carbon

![Carbon](images/carbon.png)

### Water

![Water](images/water.png)

### Watershed

![Watershed](images/watershed.png)

### Nitrogen

![Nitrogen](images/nitrogen.png)

### Energy

![Energy](images/energy.png)

Development Experience
---

Development of the initial program logic was tricky to get started, since we were not to use the __re__ standard library module. In previous versions of this project written in Rust and Julia, using regular expressions could make the code extremely short, but effectively bypass many concepts of simple parsers, like tokenizing the text, lookahead, or other strategies that could be used. I approached the problem using a very simplified Pratt parser.

Testing the initial code quickly became difficult without the use of a debugger, and I used __pydb__ and __ddd__ to trace the path through the code.

Overall, the configuration of the flask server was a very simple part of the project, but the bulk of the work ended up being in building the web service out fully. I decided to use more than the simple development server, and hosted the application on Google Cloud Platform, configured Ubuntu to automate the server so that it would always stay up, added high performance components to the application like Gunicorn WSGI and NGINX high performance web server, and also tried containerizing the application with docker for easy replication.

Web Service
---

I was able to run a Flask service on Google Cloud Platform using an Ubuntu Linux image. Additionally, I automated the server to maintain uptime by using `supervisord` and by making configuration files for `systemd` to automatically launch the app and keep it alive.

![ubuntu](images/gcp_ubuntu.png)

I experimented with several approaches during development of the web service:

Simply using the Flask Development Web Server
---

- This worked well at first, and was definitely the easiest way to get started working on the local machine.
- For an application with very little traffic, it worked fine both on the cloud machine and locally.
  - Flask's development server is not intended for production use, however, and I wanted to try to move into a production web server.

Using uWSGI and Apache:
---

- uWSGI is a WSGI module written especially for python. It is very simple and easy to use, and integrates very well into both Django and Flask applications.
- It is often the go-to WSGI module to connect to a better server than the flask server.
- Apache Web Server is ubiquitous, has good performance, and is easier to set up than Nginx.
- I made sure to automate the process in order to maintain uptime.
- The `systemd` configuration for uWSGI follows:

#### systemd Config

```conf
[uwsgi]
module = wsgi:app
master = true
processes = 5
socket = smallparser.sock
chmod-socket = 660
vacuum = true
die-on-term = true
```

Using Gunicorn and Nginx
---

- Gunicorn is a WSGI module for many languages that I used to connect the Flask application to the NGINX web server.
  - Gunicorn is a very high quality WSGI module with a very consistent and usable API.
    - I had previously used uWSGI for this part, and I found Gunicorn to be superior to it in performance and usability.
    - Instead of using `systemd` I used `supervisord` to control Gunicorn. The configuration file is much simpler than for systemd.

#### Supervisor Config

```conf
[program:SmallParserService]
command = gunicorn SmallParserService:app
directory = /home/bradd/SmallParserService
user = bradd
```
  
- NGINX is a high performance web server intended for production web services and can be very complex and cumbersome to set up.
- I attempted to set up TLS 1.3 to enable secure communication with HTTPS.
- Lacking certificates other than self-signed, it is ultimately not much better than regular HTTP.
- SSL Configuration was very complex.

NGINX Basic Configuration
---

- Sets up a basic reverse proxy for WSGI

```conf
worker_processes 1;
user www-data;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
        worker_connections 1024;
        accept_mutex off;
        use epoll;
}

http {
        include mime.types;
        default_type application/octet-stream;
        access_log /var/log/nginx/access.log combined;
        sendfile on;

        upstream app_server {
                server unix:/tmp/gunicorn.sock fail_timeout=0;
        }

        server {
                listen 80 default_server;
                return 443;
        }

        server {
                listen 80 deferred;
                client_max_body_size 4G;
                server_name scientician.systems www.scientician.systems;
                keepalive_timeout 5;
                root /home/bradd/app/SmallParserService/static;
                location / {
                        try_files $uri @proxy_to_app;
                }

                location @proxy_to_app {
                        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                        proxy_set_header X-Forwarded-Proto $scheme;
                        proxy_set_header Host $http_host;
                        proxy_redirect off;
                        proxy_pass http://app_server;
                }

                error_page 500 502 503 504 /500.html;
                location = /500.html {
                        root /home/bradd/app/SmallParserService/static;
                }
        }

        server {
                listen 443 ssl default_server;

                ssl_protocols SSLv3 TLSv1;

                ssl_ciphers ALL:!aNULL:!ADH:!eNULL:!LOW:!EXP:RC4+RSA:+HIGH:+MEDIUM;

                access_log /var/log/nginx/access.log;
                error_log  /var/log/nginx/error.log info;

                keepalive_timeout 75 75;

                ssl on;
                ssl_certificate /etc/ssl/certs/smallparser_selfsigned.crt;
                ssl_certificate_key /etc/ssl/private/smallparser_selfsigned.key;
                ssl_session_timeout  5m;

                root /home/bradd/app/SmallParserService/static;
                index index.html;
        }
}
```

Dockerizing the Application
---

- Finally, I experimented with containerizing the application in order to simplify redeployment.
- The Docker configuration was kept very simple because I have had limited experience in actually creating my own containers.

#### Dockerfile

```docker
FROM python:alpine3.7
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 80
ENTRYPOINT [ "python" ]
CMD [ "app.py" ]
```

Flask App
---

- The actual Flask web service code was very simple compared to all the configuration that was required around it in the operating system and with the many different services required to actually host and keep the service alive.
- Here is the primary endpoint used to upload the file, which automatically displays the results after upload.
- Uploaded files are kept in a directory on the server.

File Upload Endpoint
---

```python
@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    """Upload a file to the server."""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
            file.save(filepath)
            results = parse_timelog(filepath)
            return render_template("display_results.html", results=results)
    return render_template("file_upload.html")


def allowed_file(f: str) -> bool:
    """Check if file type is allowed."""
    return '.' in f and f.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
```

![file_upload_page](images/upload_file_button.png)

![file_upload_response](images/time_log_upload_results.png)

REST Service
---

- I also set up an endpoint to function as a REST service.
- You can send the timelog as a JSON array of strings.
- It will respond with the statistics output.
- The `request.py` script can be used to test.

```python
@app.route('/parse_timelog', methods=['GET', 'POST'])
def parse_timelog():
    """Parse timelog as JSON"""
    if request.method == 'POST':
        timelog = json.loads(request.json)
        records, total = tlp.parse_log(timelog['timelog'])
        stats = tlp.record_stats(records, total, timelog['filename'])
        results = {'output': tlp.format_output(stats)}
        return make_response(jsonify(results), 200)
    return render_template("index.html")
```

![rest_service](images/rest_service_response.png)

![flask_response](images/flask_rest_response.png)

On the Cloud
---

- I am running my app on Google Cloud Platform

![gcp](images/gcp_dashboard.png)

- I have a static IP address reserved for the time being at 34.70.131.103
- Port 80 is open
- There is an unresolved bug in file uploads.
- The REST service is working well
- Using Gunicorn and running a proxy through NGINX

![gcp](images/gunicorn_proxy.png)

![gcp](images/nginx_reverse_proxy.png)

- The REST service is accessible at http://34.70.131.103/parse_timelog
- The `request.py` script will allow you to test it easily.
- The command is `python request.py -f ./logs/TimeLogCarbon.txt -u 34.70.131.103 -p 80 -e parse_timelog`

![gcp](images/rest_service_gcp.png)