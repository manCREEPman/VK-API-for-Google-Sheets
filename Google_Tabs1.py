#!/usr/bin/env python
# coding: utf-8

# In[1]:


# ----------------------------------------------------------------------
# Работа с Гугл Табилцами
# ----------------------------------------------------------------------

from pprint import pprint #для красивого вывода штук-дрюк
import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
import re # для регулярных выражений


# In[2]:


'''
===================================== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ==============================================
    
    
'''

CREDENTIALS_FILE = r'creds.json'
spreadsheet_id = '1SuQ5zHzv0ZZ6D_2W7QVf-Jbm2hIrV7A4JZ31YDVwSSg'

#Указываем сервисы, с которыми работаем
credentials = ServiceAccountCredentials.from_json_keyfile_name( CREDENTIALS_FILE,
                                                                ['https://www.googleapis.com/auth/spreadsheets',
                                                                 'https://www.googleapis.com/auth/drive']
                                                              )
#Авторизируемся
httpAuth = credentials.authorize(httplib2.Http()) #Объект, работающий с аутотентификацией.Через него все запросы
service = apiclient.discovery.build('sheets', 'v4', http = httpAuth) #Экзмепляр обёртки апи

#======================= Цвета =======================
color_main = { "red": 1.0,
               "green": 1.0,
               "blue": 1.0,
               "alpha": 1.0
             }

color_sequel = { "red": 0.8117647,
                 "green": 0.8862745,
                 "blue": 0.9529412,
                 "alpha": 1.0
               }

color_minimal  = { "red": 0.85098,
                   "green": 0.917647,
                   "blue": 0.82745,
                   "alpha": 1.0
                 }

color_rest = { "red": 1,
               "green": 0.8509804,
               "blue": 0.4,
               "alpha": 1.0
             }

color_collection = { "red": 0.55686,
                     "green": 0.486274,
                     "blue": 0.76470,
                     "alpha": 1.0
                   }

color_fail = {   "red": 0.87843,
                 "green": 0.4,
                 "blue": 0.4,
                 "alpha": 1.0
               }

transparent = {   "red": 0.0,
                 "green": 0.0,
                 "blue": 0.0,
                 "alpha": 0.0
               }
eps = 0.001
#=======================================================

#======================== Настройка рамок ====================
bottom_border = { "style": "SOLID_MEDIUM",
                  "color": { "red": 0.04313,
                             "green": 0.32549,
                             "blue": 0.580392,
                             "alpha": 1.0
                           }
                }
        
merged_border = { "bottom": bottom_border,
                  "right": {"style": "SOLID_THICK"}
                }
   
unmerged_border = { "bottom": {"style":"SOLID"},
                    "right": {"style": "SOLID_THICK"}
                  }


none_border = { "bottom": {"style":"NONE"},
                "left": { "style": "NONE" },
                "right": {"style": "NONE"}
              }
#=============================================================


table_cell={1:'C', 2:'D', 3:'E', 4:'F', 5:'G', 6:'H', 7:'I'}


# In[7]:


"""
===================================== ФУНКЦИИ ==============================================
"""

def Init():
    """ Инициализации важных переменных """
    # Получаем список листов, их Id и название
    spreadsheet = service.spreadsheets().get(spreadsheetId = spreadsheet_id).execute()
    sheetList = spreadsheet.get('sheets')
   
    sheetUsers = sheetList[0]['properties']['sheetId']
    sheetSW = sheetList[1]['properties']['sheetId']

    #последняя строчка откуда можно присоединять новенького
    last_raw_in_SW = sorted( sheetList[1]['merges'], key = lambda x: x['endRowIndex'], reverse = True)[0]['endRowIndex'] # Узнаём последнюю заполненную строчку в таблице с очками

    return sheetUsers, sheetSW, last_raw_in_SW

def Cell_Format(sri = 0, sci = 1 , eri = 0 ,eci = 1, bg = color_main, border = merged_border, field = "userEnteredFormat" ):
    """
      Возвращает формат ячейки
      :param sri: startRowIndex
      :param sci: startColumnIndex
      :param eri: endRowIndex
      :param eci: endColumnIndex
      :param bg: цвет ячейки
      :param border: стиль рамки
    """
    
    style= {"range": { "sheetId": sheetSW,                                         
                       "startRowIndex": sri,
                       "startColumnIndex" : sci,
                       "endRowIndex" : eri,
                       "endColumnIndex" : eci
                   }, 
            "cell": {"userEnteredFormat": {"numberFormat": {"pattern": "#,##0",
                                                            "type":"NUMBER"
                                                           },                                          
                                           "horizontalAlignment": "CENTER",
                                           "backgroundColor": bg,
                                           "borders": border,
                                         }
                   },
            "fields": field
         }
    
    return style
    
    
    
def Clear_Sheet():
    """ Процедура очищения таблицы"""
  
    #Возвращаем исходное форматирование  
    request=[]
    for i in range(2,last_raw_in_SW,2):  
        request.append([ {"repeatCell": Cell_Format(sri=i-1, sci=2, eri=i, eci=9, bg=color_minimal, border=unmerged_border) },
                         {"repeatCell": Cell_Format(sri=i, sci=2, eri=i+1, eci=9, bg=color_main, border=merged_border)}
                      ])
    results = service.spreadsheets().batchUpdate(spreadsheetId = spreadsheet_id, body = { "requests": request }).execute()
  
    #Очищаем значения
    results = service.spreadsheets().values().clear(spreadsheetId = spreadsheet_id, range = "SW1!C2:I{0}".format(last_raw_in_SW)).execute( )

 
    return

    
def Get_list():
    """ Процедура получения списка участников"""
    # получаем ник и айдишник  
    get = service.spreadsheets().values().batchGet(spreadsheetId = spreadsheet_id, 
                                                   ranges = "SW1!A2:B{0}".format(last_raw_in_SW), 
                                                   valueRenderOption = 'FORMULA',  
                                                   dateTimeRenderOption = 'FORMATTED_STRING').execute() 
    UserList = get['valueRanges'][0]['values']
    return UserList


def Get_green_color(letter='A',number=0):
    """ Процедура для получения зелёного канала из цвета ячейки. Оценка по нему
        :param letter: столбцовый индекс ячейки
        :param number: строковой индекс ячейки
    """  
    values = service.spreadsheets().get(spreadsheetId=spreadsheet_id, ranges ='SW1!{0}{1}'.format(letter,number), includeGridData=True).execute()
    green = values['sheets'][0]['data'][0]['rowData'][0]['values'][0]['effectiveFormat']['backgroundColor']['green']
    #pprint(values['sheets'][0]['data'][0]['rowData'][0]['values'][0]['effectiveFormat']['backgroundColor'])
    return green
        

def Sort():
    """ Процедура для создания соотвествующего списка участников"""
    for i in range(2,last_raw_in_SW+1,2):
        # получаем ник и айдишник
        get = service.spreadsheets().values().batchGet(spreadsheetId = spreadsheet_id, 
                                                       ranges = "SW1!A{0}:B{0}".format(i), 
                                                       valueRenderOption = 'FORMULA',  
                                                       dateTimeRenderOption = 'FORMATTED_STRING').execute()
    
        nick = get['valueRanges'][0]['values'][0][0]
        user_id = get['valueRanges'][0]['values'][0][1]
    
        results = service.spreadsheets().values().batchUpdate(spreadsheetId = spreadsheet_id, body = {
        "valueInputOption": "USER_ENTERED",
        "data": [ {"range": "Список участников!A{0}:B{0}".format(int(i/2+1)),
                   "majorDimension": "ROWS",     # сначала заполнять ряды, затем столбцы (т.е. самые внутренние списки в values - это ряды)
                   "values": [[nick, user_id]]} ] }).execute() 
    
    return  

def Add_user(nick='', user_id='', user_name='', club=0):
    """
      Поменять Ник пользователя
      :param nick: Ник пользователя
      :param user_id: Вк айди пользователя
      :param user_name: имя пользователя
      :param club: клуб. (основа:1)
    """
    global last_raw_in_SW
    
    # Цвет ячейки участника. Из основы - белый, из сиквела - голубой 
    if club == 1 : club_color = color_main
    elif club == 2 : club_color = color_sequel
    else:
        s = "Некорректна цифра клуба. 1 - основа. 2 - сиквел. Повторите попытку"
        return s
    
    
    #Реквест для начального форматирования ячеек
    request = [ #для листа "Список Участников"
                { "repeatCell": {"range": { "sheetId": sheetUsers,
                                           "startRowIndex": int(last_raw_in_SW/2)+1,
                                           "startColumnIndex" : 0,
                                           "endRowIndex" : int(last_raw_in_SW/2)+2,
                                           "endColumnIndex" :3
                                          },
                                "cell": {"userEnteredFormat": {"horizontalAlignment": "CENTER",
                                                               "backgroundColor": club_color,
                                                               "borders": unmerged_border                                                               
                                                              }
                                        },
                                "fields": "userEnteredFormat"
                                }
               },
               #для листа SW        
               { "mergeCells": {"range": { "sheetId": sheetSW,
                                           "startRowIndex": last_raw_in_SW,
                                           "startColumnIndex" : 0,
                                           "endRowIndex" : last_raw_in_SW+2,
                                           "endColumnIndex" :1
                                         },
                                "mergeType": "MERGE_COLUMNS"
                               }
               },
               { "mergeCells": {"range": { "sheetId": sheetSW,
                                           "startRowIndex": last_raw_in_SW,
                                           "startColumnIndex" : 1,
                                           "endRowIndex" : last_raw_in_SW+2,
                                           "endColumnIndex" :2
                                         },
                                "mergeType": "MERGE_COLUMNS"
                               }
               },
               { "repeatCell": {"range": { "sheetId": sheetSW,
                                           "startRowIndex": last_raw_in_SW,
                                           "startColumnIndex" : 0,
                                           "endRowIndex" : last_raw_in_SW+2,
                                           "endColumnIndex" :2
                                          },
                                "cell": {"userEnteredFormat": {"horizontalAlignment": "CENTER",
                                                               "verticalAlignment": "MIDDLE",
                                                               "backgroundColor": club_color,
                                                               "borders": merged_border                                                               
                                                              }
                                        },
                                "fields": "userEnteredFormat"
                                }
               }, 
               { "repeatCell": Cell_Format(sri=last_raw_in_SW, sci=2, eri=last_raw_in_SW+1, eci=9, bg=color_minimal, border=unmerged_border) },
               { "repeatCell": Cell_Format(sri=last_raw_in_SW+1, sci=2, eri=last_raw_in_SW+2, eci=9, bg=color_main, border=merged_border)}
              
    ]
    
    results = service.spreadsheets().batchUpdate(spreadsheetId = spreadsheet_id,body = { "requests": request }).execute()
    
    #Заполнение ячеек информацией о участнике клуба
    user = [[nick, '=HYPERLINK("{0}";"{1}")'.format(user_id, user_name)]]
    
    Body = { "valueInputOption": "USER_ENTERED",
               "data": [ {"range": "Список участников!A{0}:B{0}".format(int(last_raw_in_SW/2+1)+1),
                          "majorDimension": "ROWS",
                          "values": user
                         },
                         {"range": "SW1!A{0}:B{0}".format(last_raw_in_SW+1),
                          "majorDimension": "ROWS",
                          "values": user
                         }
                       ]
             }
           
    results = service.spreadsheets().values().batchUpdate(spreadsheetId = spreadsheet_id, body = Body).execute() 
    last_raw_in_SW +=2
   
    s = "Ваш аккаунт {0} успешно добавлен!". format(nick)
    return s
    

def Delete_user(nick='', user_id=''):
    """
      Удалить пользователя
      :param nick: Ник пользователя
      :param user_id: Вк айди пользователя
    """
    global last_raw_in_SW
    UserList = Get_list()

    for i in range(0,last_raw_in_SW-1,2):  
        if nick == UserList[i][0]: 
            if user_id==re.search(r'https://vk.com/[.,_,\w,\d]+[^"]',UserList[i][1]).group(0):
                #Очищаем значения
                results = service.spreadsheets().values().clear(spreadsheetId = spreadsheet_id, range = "SW1!A{0}:I{1}".format(i+2,i+3)).execute( )  
            
                # Копируем всё, что ниже и вставляем на место юзера
                end_row =1000  if i != last_raw_in_SW-3 else i+6
                print(i, end_row)
                request = [ {"unmergeCells": { "range": { "sheetId": sheetSW,
                                                          "startRowIndex": i+1,
                                                          "startColumnIndex" : 0,
                                                          "endRowIndex" : i+3,
                                                          "endColumnIndex" : 4
                                                       },
                                             }
                            },
                            { "copyPaste" : {"source" : { "sheetId": sheetSW,
                                                          "startRowIndex": i+3,
                                                          "startColumnIndex" : 0,
                                                          "endRowIndex" : end_row,
                                                          "endColumnIndex" :9
                                                       },
                                             "destination": { "sheetId": sheetSW,
                                                              "startRowIndex": i+1,
                                                              "startColumnIndex" : 0,
                                                              "endRowIndex" : i+3,
                                                              "endColumnIndex" :9
                                                            }, 
                                            "pasteType": "PASTE_NORMAL"
                           
                                          }
                           },
                           { "copyPaste" : {"source" : { "sheetId": sheetUsers,
                                                          "startRowIndex": int((i+2)/2+1),
                                                          "startColumnIndex" : 0,
                                                          "endRowIndex" : int(end_row/2+1),
                                                          "endColumnIndex" : 4
                                                        },
                                            "destination": { "sheetId": sheetUsers,
                                                             "startRowIndex": int((i+2)/2),
                                                             "startColumnIndex" : 0,
                                                             "endRowIndex" : int((i+2)/2+1),
                                                             "endColumnIndex" : 4
                                                           }, 
                                            "pasteType": "PASTE_NORMAL"
                                          }
                           },
                         ]
                results = service.spreadsheets().batchUpdate(spreadsheetId = spreadsheet_id,body = { "requests": request }).execute()
   
                last_raw_in_SW -=2
                print("Успешно удалён пользователь! Теперь участников всего: {0}".format(int(last_raw_in_SW/2+1)))
                return
            else: 
                print("Не удалось")
                return
    
def Change_Nick(old_nick='', new_nick='', user_id=''):
    """
     Поменять Ник пользователя
     :param old_nick: Старый Ник пользователя
     :param new_nick: Новый Ник пользователя
     :param user_id: Вк айди пользователя
    """
 
  
    UserList = Get_list()

    for i in range(0,last_raw_in_SW-1,2):
        # сравниваем старые ники и айдишники
        if old_nick== UserList[i][0]: 
            if user_id==re.search(r'https://vk.com/[.,_,\w,\d]+[^"]',UserList[i][1]).group(0):
                Body = { "valueInputOption": "USER_ENTERED",
                         "data": [ {"range": "Список участников!A{0}".format(int((i+2)/2+1)),
                                    "majorDimension": "ROWS",
                                    "values": [[new_nick]]
                                    },
                                    {"range": "SW1!A{0}".format(i+2),
                                     "majorDimension": "ROWS",
                                     "values": [[new_nick]]
                                    }
                                   ]
                         }            
        
                results = service.spreadsheets().values().batchUpdate(spreadsheetId = spreadsheet_id, body = Body).execute() 
                s = "Успешно сменён ник! {0} -> {1}".format(old_nick,new_nick)
                return s
            else: 
                # Если другой чел меняет ник
                s = 'Нельзя сменить чужой ник!'
                return s
    s = 'Ник не удалось сменить. Проверьте правильность написания команд или ника'
    return s



def Change_Club(nick='', user_id='', club=0):
    """
     Сменить клуб для пользователя
     :param nick: Старый Ник пользователя
     :param user_id: Вк айди пользователя
     :param club : Клуб. (основа:1)
    """  
  
    UserList = Get_list()

    if club == 1 : club_color = color_main
    elif club == 2 : club_color = color_sequel
    else:
        s = "Некорректна цифра клуба. 1 - основа. 2 - сиквел. Повторите попытку"
        return s
    


    for i in range(0,last_raw_in_SW-1,2):
        # сравниваем старые ники и айдишники
        if nick ==  UserList[i][0]:
            if user_id==re.search(r'https://vk.com/[.,_,\w,\d]+[^"]',UserList[i][1]).group(0):
                # реквест для обновления ячеек
                request = [ { "repeatCell": {"range": { "sheetId": sheetUsers,
                                                         "startRowIndex": int((i+2)/2),
                                                         "startColumnIndex" : 0,
                                                         "endRowIndex" : int((i+2)/2+1),
                                                         "endColumnIndex" :3
                                                       },
                                             "cell": {"userEnteredFormat": {"backgroundColor": club_color}},
                                             "fields": "userEnteredFormat.backgroundColor"
                                             }
                            },
                            { "repeatCell": {"range": { "sheetId": sheetSW,
                                                         "startRowIndex": i+1,
                                                         "startColumnIndex" : 0,
                                                         "endRowIndex" : i+2,
                                                         "endColumnIndex" :2
                                                       },
                                             "cell": {"userEnteredFormat": {"backgroundColor": club_color}},
                                             "fields": "userEnteredFormat.backgroundColor"
                                             }
                            }
                   ]
            
                change = service.spreadsheets().batchUpdate(spreadsheetId = spreadsheet_id, body = { "requests":request} ).execute()
            
                s = "Клуб успешно сменён!"
                return s
            else:
                s = "Нельзя менять клуб другому пользователю!"
                return s
  
    s = "Не удалось сменить клуб. Проверьте правильность написания команд или ника" 
    return s
        
        
def Calculate_Norma(nick='', user_id='', charm=0, day=1, old_point=0):
    """
     Посчитать норму для пользователя
     :param nick: Старый Ник пользователя
     :param user_id: Вк айди пользователя
     :param charm: чарм пользователя
     :param day: День ивента [1,7]
     :param old_point: очки с предыдущего дня (если за прошлый день их нет в таблице)
    """

    daily_coef= {1:1, 3:1.25, 71: 4, 72: 1.5}
    old_point1=0
  
    if day in [1,2] : coef=daily_coef[1]
    elif day in [3,6]: coef=daily_coef[3]
  

    UserList = Get_list()

    for i in range(0,last_raw_in_SW-1,2):
        # сравниваем старые ники и айдишники
        if nick ==  UserList[i][0]: 
            if user_id==re.search(r'https://vk.com/[.,_,\w,\d]+[^"]',UserList[i][1]).group(0): 
                #Узнаём клуб через цвет ячейки пользователя
                green = Get_green_color(number=i+2)
                trophey = 35 if green==color_sequel['green'] else 50
       
                #Узнаём поинты с прошедшего дня. Если они есть 
                if day==1: old_point=0
                else:
                    #Если финальный день, то узнаём коэфф_дня
                    if green!=color_sequel['green'] and day==7: coef = daily_coef[71]
                    if green==color_sequel['green'] and day==7: coef = daily_coef[72]
        
                    values = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range ='SW1!{0}{1}'.format(table_cell[day-1],i+3), valueRenderOption= 'UNFORMATTED_VALUE').execute()  
                    string = str(values['values'][0][0]) 
                    # Проверяем, может был вчера накоп  
                    if string.isdigit(): old_point1=int(string)
                    elif old_point==0:
                        s = "Невозможно посчитать норму! Неизвестно число за предыдущий день\nОтправьте сообщение с числом(без пробелов), от которого отталкиваться при расчёте нормы"
                        return s
                old_point += old_point1
                new_point = "={0} + 10^5 + {1}*{2}*{3}".format(old_point,trophey,charm,coef)  
                change = service.spreadsheets().values().update(spreadsheetId = spreadsheet_id, range = "SW1!{0}{1}".format(table_cell[day],i+2),
                                                                valueInputOption = "USER_ENTERED",
                                                                body =   { "values": [[new_point]] }  ).execute() 
                values = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range ='SW1!{0}{1}'.format(table_cell[day],i+2), valueRenderOption= 'FORMATTED_VALUE').execute()  
                s = "Норма: {0}".format(values['values'][0][0])
                return s
            else:
                s = "Нельзя считать норму другому пользователю!"
                return s
    #Если не удалось найти нужного пользователя
    s = "Не удалось посчитать норму! Проверьте правильность написания команды, ника или цифр"
    return s

def Collecting_Progress(nick='', user_id='', day=1, type=1, res = '(0 0 0)'):
    """
     Заполнить ресурсы в таблице во время накопа
     :param nick: Старый Ник пользователя
     :param user_id: Вк айди пользователя
     :param day: День ивента [1,7]
     :param type: Тип накопа. (начало:1, конец:2)
     :param res: Ресурсы пользователя
    """
    easy =3 # Поблажка для нормы основы

    UserList = Get_list()  

    for i in range(0,last_raw_in_SW-1,2):
        # сравниваем старые ники и айдишники
        if nick ==  UserList[i][0]: 
            if user_id==re.search(r'https://vk.com/[.,_,\w,\d]+[^"]',UserList[i][1]).group(0):
                #Узнаём клуб через цвет ячейки пользователя
                green = Get_green_color(number=i+2)
                #Норма накопа определяется по бомбам (Основа:20, Сиквел:10)
                bomb_min = 10 if green==color_sequel['green'] else 20-easy
        
                #Если начало накопа
                if type==1: 
                    write_in = service.spreadsheets().values().update(spreadsheetId = spreadsheet_id, range = "SW1!{0}{1}".format(table_cell[day],i+2),
                                                                      valueInputOption = "USER_ENTERED",
                                                                      body =   { "values": [["'"+res]] }  ).execute() 
          
                    #Поставить фиолетовый цвет в ячейку для обозначения накопа  
                    request = { "updateCells": { "range": { "sheetId": sheetSW,
                                                            "startRowIndex": i+2,
                                                            "startColumnIndex" : day+1,
                                                            "endRowIndex" : i+3,
                                                            "endColumnIndex" :day+2,
                                                          },
                                                 "rows": [ { "values": [ { "userEnteredFormat": { "backgroundColor":  color_collection }}]}],
                                                 "fields": "userEnteredFormat.backgroundColor"
                                                }
                             }
                    results = service.spreadsheets().batchUpdate(spreadsheetId = spreadsheet_id,body = { "requests": request }).execute()
    
                    s = "Ваши ресурсы успешно записаны! Удачного накопления!"
                    return s
                else:
                    write_in = service.spreadsheets().values().update(spreadsheetId = spreadsheet_id, range = "SW1!{0}{1}".format(table_cell[day],i+3),
                                                                      valueInputOption = "RAW",
                                                                      body =   { "values": [[res]] }  ).execute() 
                    #Узнаем выполнились ли условия нормы
                    values = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range ='SW1!{0}{1}'.format(table_cell[day],i+2), valueRenderOption= 'UNFORMATTED_VALUE').execute()  

                    #Если начальных ресурсов нет
                    if len(values) <3:
                        s = "Введите начальные ресурсы!"
                        return s
            
                    string = str(values['values'][0][0])
             
                    start_bomb = re.search(r'[\d]+[)]',string).group(0) 
                    start_bomb = int(start_bomb[:len(start_bomb)-1])
                    end_bomb = re.search(r'[\d]+[)]',res).group(0)
                    end_bomb = int(end_bomb[:len(end_bomb)-1])
            
                    #Если у человека ув причина
                    rest = Get_green_color(letter=table_cell[day], number=i+3)
                    if end_bomb - start_bomb >= bomb_min or rest == color_rest['green']:
                        s =  "Ваши ресурсы успешно записаны! Норма выполнена!"
                        return s
            
                    #Поставить красный в ячейку, т.к. норма не выполнена  
                    request = { "updateCells": { "range": { "sheetId": sheetSW,
                                                            "startRowIndex": i+2,
                                                            "startColumnIndex" : day+1,
                                                            "endRowIndex" : i+3,
                                                            "endColumnIndex" : day+2
                                                          },
                                                 "rows": [ { "values": [ { "userEnteredFormat": { "backgroundColor":  color_fail }}]}],
                                                 "fields": "userEnteredFormat.backgroundColor"
                                                }
                             }
                    change = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={"requests": request}).execute()
           
                    s = "Ваши ресурсы успешно записаны! Норма не выполнена!"
                    return s
            else:
                s = "Нельзя записывать ресурсы за другого пользователя!"
                return s
    #Если не удалось найти нужного пользователя
    s = "Не удалось внести ресурсы в таблицу! Проверьте правильность написание команды, ника или цифр"
    return s     
          
        
        


# In[4]:


sheetUsers, sheetSW, last_raw_in_SW = Init()
print(sheetUsers, sheetSW, last_raw_in_SW)

#Add_user(nick='heesdello', user_id='https://www.google.ru', user_name='Google', club=1)
#Change_Nick(old_nick='CodeSeola', new_nick='google', user_id='https://vk.com/femperox')
#Calculate_Norma(nick='Amalthea',user_id='https://vk.com/skazki_vilnusa', charm=12000, day=2)
#Change_Club(nick='Femperox',user_id='https://vk.com/femperox',club=1)
#Collecting_Progress(nick='CodeSeola', user_id='https://vk.com/id156738763', day=1, type=2, res = '(12 34 104)')
#Clear_Sheet()
#Delete_user1(nick='rrrr6', user_id='https://vk.com/id327845711')


# In[5]:


print(last_raw_in_SW)


# In[ ]:




