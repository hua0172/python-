import PySimpleGUI as sg
import pymongo

sorce_list = []
target_list = []

sorce_not_in_target_collection = []
target_not_in_sorce_collection = []
same_collection = []

sorce_copy_index = []

sg.theme('DarkBrown')   # 设置当前主题
# 界面布局，将会按照列表顺序从上往下依次排列，二级列表中，从左往右依此排列
layout = [  [sg.Text('sorce ip:'), sg.InputText()
                , sg.Text('port:'), sg.InputText("27017",size=(10, 10))
                , sg.Text('user:'), sg.InputText("root",size=(20, 20))
                , sg.Text('password:'), sg.InputText(size=(20, 20))
                , sg.Text('authentication DB:'), sg.InputText("admin",size=(20, 20))
                , sg.Text('database'), sg.InputText(size=(20, 20))
             ],
            [sg.Text('target ip:'), sg.InputText()
                , sg.Text('port:'), sg.InputText("27017", size=(10, 10))
                , sg.Text('user:'), sg.InputText("root",size=(20, 20))
                , sg.Text('password:'), sg.InputText(size=(20, 20))
                , sg.Text('authentication DB:'), sg.InputText("admin", size=(20, 20))
                , sg.Text('database'), sg.InputText(size=(20, 20))
             ],
            [sg.Button('Ok'), sg.Button('Cancel')]
            ,
            [sg.Text('reslut')]
            ,
            [sg.Output(size=(220,30) , key='-OUTPUT-')  ]
            ]

# 创造窗口
window = sg.Window('結構比對', layout)
# 事件循环并获取输入值
while True:
    event, values = window.read()
    if event in (None, 'Cancel'):   # 如果用户关闭窗口或点击`Cancel`
        break

    if len(values[2]) == 0 and len(values[3]) == 0:
        source_user = ""
    else:
        source_user = values[2] + ":" + values[3] + "@"

    if len(values[8]) == 0 and len(values[9]) == 0:
        target_user = ""
    else:
        target_user = values[8] + ":" + values[9] + "@"

    if len(values[4]) == 0:
        source_authentication_db = ""
    else:
        source_authentication_db = "/?authSource=" + values[4]

    if len(values[10]) == 0:
        target_authentication_db = ""
    else:
        target_authentication_db = "/?authSource=" + values[10]

    source_mongodb_server_uri = "mongodb://" + source_user + values[0] + ":" + values[1]
    target_mongodb_server_uri = "mongodb://" + target_user + values[6] + ":" + values[7]

    source_mongo = pymongo.MongoClient(source_mongodb_server_uri)
    target_mongo = pymongo.MongoClient(target_mongodb_server_uri)


    db_sorce = source_mongo[values[5]]
    db_target = target_mongo[values[11]]



    collectionname_sorce = db_sorce.list_collection_names()
    collectionname_target = db_target.list_collection_names()

    for sorce_collection in collectionname_sorce:

        if sorce_collection in str(collectionname_target):
            same_collection.append(sorce_collection)
        else:
            sorce_not_in_target_collection.append(sorce_collection)

    for target_collection in collectionname_target:

        if target_collection not in str(collectionname_sorce):
            target_not_in_sorce_collection.append(target_collection)

    print("===============================")
    print("來源有，目標資料庫沒有的collection")
    # 來源有，目標資料庫沒有的coollection
    for collectionname in sorce_not_in_target_collection:

        index_content = db_sorce[collectionname].index_information()

        for key, value in index_content.items():

            index_key_value = value["key"]

            conditionstr = ""

            for a in value:
                if a in ("expireAfterSeconds", "background", "unique", "sparse"):
                    if len(conditionstr) == 0:
                        conditionstr = "\"" + a + "\"" + ": " + str(value[a]).lower()
                    else:
                        conditionstr = conditionstr + ',' + "\"" + a + "\"" + ": " + str(value[a]).lower()

            if len(conditionstr) == 0:
                conditionstr = ""
            else:
                conditionstr = "{" + conditionstr + "}"

            createstr = ""

            for i in range(len(index_key_value)):

                replacestr = index_key_value[i]
                replacestr = str(replacestr).replace("(", "").replace(")", "").replace(",", ":")

                if len(createstr) == 0:
                    createstr = replacestr
                else:
                    createstr = createstr + ',' + replacestr

            createstr = "{" + createstr + "}"

            if len(conditionstr) > 0:
                createstr = createstr + "," + conditionstr

            print("db." + collectionname + ".createIndex(" + createstr + ")")


    print("===============================")
    print("有相同collection，index有差異")
    # 有相同coollection，index有差異
    for collectionname in same_collection:

        index_content_source = db_sorce[collectionname].index_information()

        index_content_target = db_target[collectionname].index_information()

        index_content_target_str = str(index_content_target)

        if str(index_content_target).find("ns"):
            index_content_target_str = index_content_target_str.replace(", 'ns': '" + str(values[11]) + "." + collectionname + "'","")

        for key, value in index_content_source.items():

            valuestr = str(value)

            if valuestr.find("ns"):
                valuestr = valuestr.replace(", 'ns': '" + str(values[5]) + "." + collectionname + "'", "")

            if valuestr not in index_content_target_str:

                index_key_value = value["key"]

                conditionstr = ""

                for a in value:
                    if a in ("expireAfterSeconds", "background", "unique", "sparse"):
                        if len(conditionstr) == 0:
                            conditionstr = "\"" + a + "\"" + ": " + str(value[a]).lower()
                        else:
                            conditionstr = conditionstr + ',' + "\"" + a + "\"" + ": " + str(value[a]).lower()

                if len(conditionstr) == 0:
                    conditionstr = ""
                else:
                    conditionstr = "{" + conditionstr + "}"

                createstr = ""

                for i in range(len(index_key_value)):

                    replacestr = index_key_value[i]
                    replacestr = str(replacestr).replace("(", "").replace(")", "").replace(",", ":")

                    if len(createstr) == 0:
                        createstr = replacestr
                    else:
                        createstr = createstr + ',' + replacestr

                createstr = "{" + createstr + "}"

                if len(conditionstr) > 0:
                    createstr = createstr + "," + conditionstr

                print("db." + collectionname + ".createIndex(" + createstr + ")")

    print("===============================")
    print("目標有，來源資料庫沒有的collection")
    for collectionname in target_not_in_sorce_collection:
        collectionname

window.close()
