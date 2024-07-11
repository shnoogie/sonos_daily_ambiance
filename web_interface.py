import cherrypy
import json


class app(object):
    def __init__(self, conn):
        self.conn = conn

        with open('web/template.html', 'r') as file:
            self.template = file.read()

    def generate_page(self, data):
        html = self.template
        html = html.replace('$$data$$', data)
        return html

    @cherrypy.expose
    def index(self):
        self.conn.send('index')
        record_player = self.conn.recv()
        data = "<p class=\"title\"> home </p>"
        data = data + "<a href=\"/start\">start</a> | <a href=\"/stop\">stop</a> | \
            <a href=\"/change_track\">change track</a>"
        if record_player is True:
            data = data + "<p style=\"font-size:24px\"><br><a href=\"/record_player\">Start Record Player</a> </p>"
        html = self.generate_page(data)
        return html

    @cherrypy.expose
    def stop(self):
        self.conn.send('stop')
        raise cherrypy.HTTPRedirect("/")

    @cherrypy.expose
    def start(self):
        self.conn.send('start')
        raise cherrypy.HTTPRedirect("/")

    @cherrypy.expose
    def record_player(self):
        self.conn.send('record_player')
        raise cherrypy.HTTPRedirect("/")

    @cherrypy.expose
    def test(self):
        raise cherrypy.HTTPRedirect("/")

    @cherrypy.expose
    def schedule(self):
        data = "<p class=\"title\"> schedule </p >"
        data = data + "<a href=\"/generate_schedule\">generate new schedule</a><br><br>"
        self.conn.send('schedule')
        schedule = self.conn.recv()
        for event in schedule:
            data = data + event + '<br>'

        html = self.generate_page(data)
        return html

    @cherrypy.expose
    def generate_schedule(self):
        self.conn.send('generate_schedule')
        raise cherrypy.HTTPRedirect("/schedule")

    @cherrypy.expose
    def logs(self):
        data = "<p class=\"title\"> track logs </p >"
        data = data + "<a href=\"/logs\">track logs</a> | <a href=\"/app_logs\"> \
            app logs</a> <br><br>"
        with open('track_log.json', 'r') as file:
            log_info = json.loads(file.read())

        for track in log_info:
            count = str(log_info[track]['count'])
            last_played = log_info[track]['last_played']
            data = data + "<strong>" + track + "</strong>" + "<br> &emsp;&emsp;&emsp;&emsp; Count: " + count \
                   + "<br> &emsp;&emsp;&emsp;&emsp; Last Played: " + last_played + "<br><br>"
        html = self.generate_page(data)
        return html

    @cherrypy.expose
    def app_logs(self):
        data = "<p class=\"title\"> app logs </p >"
        data = data + "<a href=\"/logs\">track logs</a> | <a href=\"/app_logs\"> \
            app logs</a> <br><br>"

        with open('log.txt', 'rt') as file:
            log_data = file.readlines()
            i = len(log_data)
            if i < 51:
                for line in log_data:
                    data = data + line + "<br>"
            else:
                e = i - 50
                for line in log_data[e:]:
                    data = data + line + "<br>"

        html = self.generate_page(data)
        return html

    @cherrypy.expose
    def config(self):
        data = "<p class=\"title\"> config </p >"
        with open('config/config.yaml', 'r') as file:
            config = data + file.read().replace("\n", "<br/>")
        html = self.generate_page(config)
        return html

    @cherrypy.expose
    def change_track(self):
        self.conn.send('change_track')
        raise cherrypy.HTTPRedirect("/")


if __name__ == '__main__':
    print('This script does not run directly.')
