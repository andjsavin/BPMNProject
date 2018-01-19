import requests
from tkinter import *
import json
import base64
import os
import jenkins


trello_key = "da55a084a94eed5f8193a3a8d4a69899"
trello_token = "fd3ac0253f7e4f97a9bc43b729578bd8f97caa79954a519bfa1f0313cd659980"
board_id = "5a60b855b9260853af5fb472"
activiti_url = "http://kermit:kermit@80.211.255.185:32771/activiti-rest/service"
proc_id = "process:1:86"
git_token = "ad0044c6d9bc2db41b28eb9df675494d8996c524"
sonar_token = "63a1848a89a0eb7266651f5d68d1ccec92f45c26"


root = Tk()
lists = {}


def check():
    global lists
    url = "https://api.trello.com/1/boards/5a60b855b9260853af5fb472/lists"
    querystring = {"key": "da55a084a94eed5f8193a3a8d4a69899", "token": "fd3ac0253f7e4f97a9bc43b729578bd8f97caa79954a519bfa1f0313cd659980"}
    response = requests.request("GET", url, params=querystring)
    print(response.text)
    if len(response.text) > 10:
        lists = json.loads(response.text[1:-1])
        if lists.get("cards") is None:
            url = activiti_url + "/runtime/process-instances"
            headers = {'content-type': 'application/json'}
            data = {
                "processDefinitionId":"process:1:86",
            }
            d = json.dumps(data)
            response = requests.request("POST", url, data=d, headers=headers)
            print(response.text)

            url = "https://api.trello.com/1/cards"
            querystring = {"name": "Developing", "idList": lists['id'], "key": trello_key, "token": trello_token}
            requests.request("POST", url, params=querystring)


def development():
    global lists
    dev = Toplevel(root)
    devframe = Frame(dev, width=260, height=200, bg='lightblue')
    devframe.pack()

    def push_to_github():
        url = "https://api.github.com/repos/" + "Milaketta/Pamparam" + "/contents/" + "foo.txt"

        base64content = base64.b64encode(open("foo.txt", "rb").read())

        data = requests.get(url + '?ref=' + "master", headers={"Authorization": "token " + git_token}).json()
        print(data)
        sha = data['sha']

        if base64content.decode('utf-8') + "\n" != data['content']:
            message = json.dumps({"message": "update",
                                  "branch": "master",
                                  "content": base64content.decode("utf-8"),
                                  "sha": sha
                                  })

            resp = requests.put(url, data=message,
                                headers={"Content-Type": "application/json", "Authorization": "token " + git_token})
            print(resp)
        else:
            print("nothing to update")

        url = "http://Developer:12345@80.211.255.185:32771/activiti-rest/service/runtime/tasks"
        headers = {'content-type': 'application/json'}
        response = requests.request("GET", url, headers=headers)
        task = json.loads(response.text)
        id = task["data"][0]["id"]

        url = "http://Developer:12345@80.211.255.185:32771/activiti-rest/service/runtime/tasks/" + str(id)
        headers = {'content-type': 'application/json'}
        data = {
  "action" : "complete",
  "variables" : []
}
        d = json.dumps(data)
        response = requests.request("POST", url, data=d, headers=headers)
        print(response.text)

        url = "https://api.trello.com/1/cards"
        querystring = {"name": "Reviewing", "idList": lists['id'], "key": trello_key, "token": trello_token}
        requests.request("POST", url, params=querystring)




    commit = Button(devframe, text='Commit', command=push_to_github)
    commit.pack()
    commit.place(x=60, y=90)


def review():
    global lists
    rev = Toplevel(root)
    revframe = Frame(rev, width=260, height=200, bg='lightblue')
    revframe.pack()
    def sonar():
        os.system('sonar-scanner.bat -Dsonar.projectKey=hi -Dsonar.sources=Foo')

    review = Button(revframe, text="Review")
    review.pack()
    review.place(x=20, y=20)

    son = Button(revframe, text="Sonar", command=sonar)
    son.pack()
    son.place(x=20, y=60)



    revp = IntVar()
    revm = IntVar()
    sonp = IntVar()
    sonm = IntVar()
    utp = IntVar()
    utm = IntVar()
    c1 = Checkbutton(revframe, text="+", variable=revp)
    c2 = Checkbutton(revframe, text="-", variable=revm)
    c3 = Checkbutton(revframe, text="+", variable=sonp)
    c4 = Checkbutton(revframe, text="-", variable=sonm)
    c5 = Checkbutton(revframe, text="+", variable=utp)
    c6 = Checkbutton(revframe, text="-", variable=utm)

    c1.pack()
    c1.place(x=100, y=20)
    c2.pack()
    c2.place(x=140, y=20)
    c3.pack()
    c3.place(x=100, y=60)
    c4.pack()
    c4.place(x=140, y=60)
    c5.pack()
    c5.place(x=100, y=100)
    c6.pack()
    c6.place(x=140, y=100)

    def tests():
        server = jenkins.Jenkins('http://localhost:8080', username='andj', password='112233')
        server.build_job('hello')

    ut = Button(revframe, text="Unit tests", command=tests)
    ut.pack()
    ut.place(x=20, y=100)

    def submit():
        err = 0
        if revm.get() == 1:
            err += 1
        if sonm.get() == 1:
            err += 1
        if utm.get() == 1:
            err += 1
        if err != 0:
            url = "https://api.trello.com/1/cards"
            querystring = {"name": "Development", "idList": lists['id'], "key": trello_key, "token": trello_token}
            requests.request("POST", url, params=querystring)
        else:
            url = "https://api.trello.com/1/cards"
            querystring = {"name": "Testing", "idList": lists['id'], "key": trello_key, "token": trello_token}
            requests.request("POST", url, params=querystring)

            url = "http://Reviewer:12345@80.211.255.185:32771/activiti-rest/service/runtime/tasks"
            headers = {'content-type': 'application/json'}
            response = requests.request("GET", url, headers=headers)
            task = json.loads(response.text)
            id = task["data"][0]["id"]

            url = "http://Reviewer:12345@80.211.255.185:32771/activiti-rest/service/runtime/tasks/" + str(id)
            headers = {'content-type': 'application/json'}
            data = {
                "action": "complete",
                "variables": []
            }
            d = json.dumps(data)
            response = requests.request("POST", url, data=d, headers=headers)
            print(response.text)



    sub = Button(revframe, text="Submit", command=submit)
    sub.pack()
    sub.place(x=20, y=140)

def testing():
    global lists
    rev = Toplevel(root)
    revframe = Frame(rev, width=260, height=200, bg='lightblue')
    revframe.pack()

    def complete():
        url = "http://Tester:12345@80.211.255.185:32771/activiti-rest/service/runtime/tasks"
        headers = {'content-type': 'application/json'}
        response = requests.request("GET", url, headers=headers)
        task = json.loads(response.text)
        id = task["data"][0]["id"]

        url = "http://Tester:12345@80.211.255.185:32771/activiti-rest/service/runtime/tasks/" + str(id)
        headers = {'content-type': 'application/json'}
        data = {
            "action": "complete",
            "variables": []
        }
        d = json.dumps(data)
        response = requests.request("POST", url, data=d, headers=headers)
        print(response.text)

        url = "https://api.trello.com/1/cards"
        querystring = {"name": "Implementing", "idList": lists['id'], "key": trello_key, "token": trello_token}
        requests.request("POST", url, params=querystring)

    comp = Button(revframe, text='Complete', command=complete)
    comp.pack()
    comp.place(x=60, y=90)


def impl():
    global lists
    rev = Toplevel(root)
    revframe = Frame(rev, width=260, height=200, bg='lightblue')
    revframe.pack()

    def complete():
        url = "http://System:12345@80.211.255.185:32771/activiti-rest/service/runtime/tasks"
        headers = {'content-type': 'application/json'}
        response = requests.request("GET", url, headers=headers)
        task = json.loads(response.text)
        id = task["data"][0]["id"]

        url = "http://System:12345@80.211.255.185:32771/activiti-rest/service/runtime/tasks/" + str(id)
        headers = {'content-type': 'application/json'}
        data = {
            "action": "complete",
            "variables": []
        }
        d = json.dumps(data)
        response = requests.request("POST", url, data=d, headers=headers)
        print(response.text)

        url = "https://api.trello.com/1/lists/" + lists['id'] + "/closed"
        querystring = {"value": "true", "key": trello_key, "token": trello_token}
        requests.request("PUT", url, params=querystring)

    comp = Button(revframe, text='Complete', command=complete)
    comp.pack()
    comp.place(x=60, y=90)


mainframe = Frame(root, width=260, height=200, bg='lightblue')
mainframe.pack()

menubar = Menu(mainframe)
root.config(menu=menubar)
windowswitch = Menu(menubar)
windowswitch.add_command(label="Development", command=development)
windowswitch.add_command(label="Review", command=review)
windowswitch.add_command(label="Test", command=testing)
windowswitch.add_command(label="Implement", command=impl)
windowswitch.add_command(label="Exit", command=root.destroy)
menubar.add_cascade(label="File", menu=windowswitch)

but_check = Button(root, text='Check', command=check)
but_check.pack()
but_check.place(x=60, y=90)


root.mainloop()