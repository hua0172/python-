import PySimpleGUI as sg
import pymongo

sg.theme('DarkBrown')   # 设置当前主题
# 界面布局，将会按照列表顺序从上往下依次排列，二级列表中，从左往右依此排列
layout = [  [sg.Text('sorce ip:'), sg.InputText()
                , sg.Text('port:'), sg.InputText("27017",size=(10, 10))
                , sg.Text('user:'), sg.InputText("root",size=(20, 20))
                , sg.Text('password:'), sg.InputText(size=(20, 20))

             ],
            [sg.Text('target ip:'), sg.InputText()
                , sg.Text('port:'), sg.InputText("27017", size=(10, 10))
                , sg.Text('user:'), sg.InputText("root",size=(20, 20))
                , sg.Text('password:'), sg.InputText(size=(20, 20))
             ],
            [sg.Button('Ok'), sg.Button('Cancel')]
            ,
            [sg.Text('reslut')]
            ,
            [sg.Output(size=(220,30) , key='-OUTPUT-')  ]
            ]

# 创造窗口
window = sg.Window('使用者比對', layout)
# 事件循环并获取输入值
while True:
    event, values = window.read()
    if event in (None, 'Cancel'):   # 如果用户关闭窗口或点击`Cancel`
        break

    if len(values[2]) == 0 and len(values[3]) == 0:
        source_user = ""
    else:
        source_user = values[2] + ":" + values[3] + "@"

    if len(values[6]) == 0 and len(values[7]) == 0:
        target_user = ""
    else:
        target_user = values[6] + ":" + values[7] + "@"


    source_mongodb_server_uri = "mongodb://" + source_user + values[0] + ":" + values[1]
    target_mongodb_server_uri = "mongodb://" + target_user + values[4] + ":" + values[5]

    source_mongo = pymongo.MongoClient(source_mongodb_server_uri)
    target_mongo = pymongo.MongoClient(target_mongodb_server_uri)

    db_sorce = source_mongo["admin"]
    db_target = target_mongo["admin"]

    source_list = db_sorce.command('usersInfo')
    target_list = db_target.command('usersInfo')

    source_user_list = []
    source_role_list = []
    target_user_list = []
    target_role_list = []

    same_list = []
    diff_list = []

    for a in source_list['users']:
        source_user_list.append(a["user"])
        source_role_list.append(a["roles"])

    for b in target_list['users']:
        target_user_list.append(b["user"])
        target_role_list.append(b["roles"])

    for user in source_user_list:

        if user in target_user_list:
            same_list.append(user)
        elif user not in target_user_list:
            diff_list.append(user)

    print("============================")
    print("來源有，目標沒有")

    for user in diff_list:
        print("user:" + user + " , roles:" + str(source_role_list[source_user_list.index(user)]))

    print("============================")
    print("相同user，權限不同")
    for user in same_list:

        source_role_str = str(source_role_list[source_user_list.index(user)]).replace("[", "").replace("]", "")
        target_role_str = str(target_role_list[target_user_list.index(user)]).replace("[", "").replace("]", "")

        if source_role_str != target_role_str:
            print("source: user = " + user + " , roles=" + source_role_str)
            print("target: user = " + user + " , roles=" + target_role_str + "\n")

    print("============================")
    print("目標有，來源沒有")

    for user in target_user_list:

        if user not in same_list:
            print(user)

window.close()
