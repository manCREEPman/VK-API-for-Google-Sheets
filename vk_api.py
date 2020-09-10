<<<<<<< HEAD
#!/usr/bin/env python
# coding: utf-8

# In[1]:


=======
>>>>>>> 1e3aa97e85c1057f4f3d23d9edc7ab2446a1531f
# ----------------------------------------------------------------------
# Бот для сообщества VK
# ----------------------------------------------------------------------
import requests
import json
import random
import re
from pprint import pprint

<<<<<<< HEAD
from Google_Tabs1 import *


# In[2]:


=======
>>>>>>> 1e3aa97e85c1057f4f3d23d9edc7ab2446a1531f
'''
1. Глобальные переменные
    
    api_address - для сокращения строк обращения к методам VK API
    api_version - версия API VK
    group_id - число в ссылке на сообщество, если изменена ссылка, 
               то получить с помощью функции get_group_id, передав ссылку на группу
    token - специальный ключ, который необходимо настроить в сообществе
'''

api_address = 'http://api.vk.com/method/'
api_version = '5.103'
group_id = '195146403'
token = '40a528ce3bfe53f37a917eb0231bd79b2d073dbe026edf775530221432c7a9ffd85e879077d24bfc8dd37'

<<<<<<< HEAD
day = 2


# In[3]:

=======
>>>>>>> 1e3aa97e85c1057f4f3d23d9edc7ab2446a1531f

'''
2. Функции

'''


def get_long_poll_server(api_version, group_id, access_token):
    """
    :param api_version: версия API
    :param group_id: ID сообщества
    :param access_token: токен сообщества
    :return: Структура: сервер, уникальный ключ и счётчик действий.
    """
    return requests.get(
        '%sgroups.getLongPollServer?group_id=%s&access_token=%s&v=%s' %
        (api_address, group_id, access_token, api_version)
    )


def get_dictionary(response):
    """
    :param response: Результат выполения функции get_long_poll_server
    :return: Словарь структуры: сервер, уникальный ключ и счётчик действий.
    """
    string_dictionary = response.content.decode()
    changed_string = string_dictionary.replace("'", "\"")
    return json.loads(changed_string)


def get_message_text(user_action):
    """
    :param user_action: Структура, описывающая действия пользователя и другую информацию
    :return: Текст присланного пользователем сообщения
    """
    message_response = user_action['updates'][len(user_action['updates']) - 2]
    return message_response['object']['message']['text']


def send_message(message, peer_id):
    """
    :param message: Текст сообщения
    :param peer_id: ID получателя
    """
    rand_id = str(random.randint(0, 999999999))
    response = requests.get('{}messages.send?peer_id={}&random_id={}&message={}&access_token={}&v={}'.format
                            (api_address, peer_id, rand_id, message, token, api_version))


def pack_parameters(param):
    """
    :param param: Строка, содержащая слово(-а), разделённые пробелами
    :return: Список параметров
    """
    if param:
<<<<<<< HEAD
        if len(param) > 1:
            params = []
            for item in param[0]:
                params.append(item)
            return params
        return param
=======
        params = []
        params_length = len(param[0])
        for i in range(params_length):
            params.append(param[0][i])
        return params
>>>>>>> 1e3aa97e85c1057f4f3d23d9edc7ab2446a1531f
    else:
        return None


def recognize_action(text):
    """
    Исходя из сообщения пользователя функция сформирует команду и список параметров, если
    они были переданы. Если где-то произошла ошибка, то соответсвующее значение выходной
    тульпы будет равно None.
    user_commands можно дополнять со временем
    :param text: Текст сообщения
    :return: Тульпа - название команды, список параметров
    """
    user_commands = ['добавить аккаунт', 'сменить клуб', 'сменить ник', 'посчитать норму',
                     'начать накоп', 'закончить накоп', 'помощь']
    search_results = re.findall(r'(?i)^({}|{}|{}|{}|{}|{}|{}|\d+)'.format(*user_commands), text)
    if search_results:
        command = search_results[0].lower()
        query_example = r'\d+'
        if command == 'добавить аккаунт' or command == 'сменить клуб':
            query_example = r'(?i){} "([\s,\S]+)" ([1-2])$'
        elif command == 'начать накоп' or command == 'закончить накоп':
            query_example = r'(?i){} "([\s,\S]+)" (\(\d+ \d+ \d+\))$'
        elif command == 'сменить ник':
            query_example = r'(?i){} "([\s,\S]+)" "([\s,\S]+)"$'
        elif command == 'посчитать норму':
            query_example = r'(?i){} "([\s,\S]+)" (\d+)$'
        else:
            command = 'число'
        params = pack_parameters(re.findall(query_example.format(command), text))
        return command, params
    return None, None


def get_user_vk_id(id):
    """
    :param id: Числовой ID пользователя VK
    :return: Ссылка на пользователя
    """
    response = requests.get('{}users.get?user_ids={}&fields=domain&access_token={}&v={}'
                            .format(api_address, id, token, api_version))
    dict = get_dictionary(response)
    return 'https://vk.com/{}'.format(dict['response'][0]['domain'])


def check_preprevious_text_message(text):
    """
    Проверяет текст предыдущего сообщения на наличие корректной команды "посчитать норму"
    :param text: Текст сообщения
    :return: True|False
    """
    result_tuple = recognize_action(text)
    if result_tuple[0] == 'посчитать норму' and result_tuple[1] is not None:
        return True
    return False


def get_preprevious_text_message(current_id):
    """
    Получает текст сообщения, присланного ранее
    :param current_id: ID текущего сообщения
    :return: Текст сообщения, находящегося на 2 позиции в диалоге ранее
    """
    new_id = current_id - 2 if current_id - 2 > 1 else 1
    response = requests.get('{}messages.getById?message_ids={}&group_id={}&access_token={}&v={}'
                            .format(api_address, new_id, group_id, token, api_version))
    dict = get_dictionary(response)
    text = dict['response']['items'][0]['text']
    return text


def get_message_id(message_response):
    """
    Получает ID сообщения от пользователя в рамках диалога
    :param message_response: Структура сообщения
    :return: ID сообщения
    """
    return message_response['object']['message']['id']


def get_group_id(short_name):
    """
    Использовать в случае изменения ссылки на сообщество.
    :param short_name: Ссылка на сообщество
    :return: ID сообщества
    """
    response = requests.get('{}groups.getById?groups_ids={}&access_token={}&v={}'.format
                            (api_address, short_name, token, api_version))
    dict = get_dictionary(response)
    return dict['response'][0]['id']


def get_vk_name(user_id):
    """
    Получает имя пользователя ВК по его ID или по короткой ссылке
    :param user_id: ID пользователя
    :return: Имя пользователя
    """
    fields = ['nickname']
    response = requests.get('{}users.get?user_ids={}&fields={}&access_token={}&v={}'.format
                            (api_address, user_id, *fields, token, api_version))
    return get_dictionary(response)['response'][0]['first_name']


def form_message(result_tuple, vk_address, vk_name, message_id):
    """
    Использовать для дальнейших вызовов функций, работающих с Google Sheets
    Опционально передавать сюда ссылку на страницу пользователя
    :param result_tuple: Тульпа (команда, [параметры])
    :return: Возратит сообщение, которое нужно выдать в зависимости от значений тульпы
    """

    # Здесь нужно помещать функции в зависимости от команды и аргументов
    '''
    пример использования 
    if result_tuple[0] == 'сменить ник' and result_tuple[1] is not None:
        обработка кода
    '''
    if result_tuple[0] is not None and result_tuple[1] is not None:
        message = 'Команда и аргументы корректны'
    elif result_tuple[1] is None and result_tuple[0] is None:
        message = 'Команда и аргументы не корректны'
    elif result_tuple[0] is None:
        message = 'Команда не корректна'
    else:
        message = 'Аргументы не корректны'
<<<<<<< HEAD
        
    
    if result_tuple[0] == 'добавить аккаунт' and result_tuple[1] is not None:
        message = Add_user(user_id = vk_address, user_name = vk_name, nick = result_tuple[1][0][0], club = int(result_tuple[1][0][1]))
    if result_tuple[0] == 'сменить клуб' and result_tuple[1] is not None:
        message = Change_Club(user_id = vk_address, nick = result_tuple[1][0][0], club = int(result_tuple[1][0][1]))
    if result_tuple[0] == 'сменить ник' and result_tuple[1] is not None: 
        message = Change_Nick(user_id = vk_address, old_nick = result_tuple[1][0][0], new_nick = result_tuple[1][0][1])

    if result_tuple[0] == 'начать накоп' and result_tuple[1] is not None:
        message = Collecting_Progress(user_id = vk_address, day = day, type = 1, nick = result_tuple[1][0][0],  res = result_tuple[1][0][1])
    if result_tuple[0] == 'закончить накоп' and result_tuple[1] is not None:
        message = Collecting_Progress(user_id = vk_address, day = day, type = 2, nick = result_tuple[1][0][0],  res = result_tuple[1][0][1])

    if result_tuple[0] == 'посчитать норму' and result_tuple[1] is not None:
        message = Calculate_Norma(user_id = vk_address, day = day, nick = result_tuple[1][0][0],  charm = int(result_tuple[1][0][1]))
  
        
    # Пример обработки сообщения, содержащего лишь число
    if result_tuple[0] == 'число':
        preprevious_text = get_preprevious_text_message(message_id)
        if check_preprevious_text_message(preprevious_text):
            query_example = r'"([\s,\S]+)" (\d+)$'
            old_params = pack_parameters(re.findall(query_example,preprevious_text))
            message = Calculate_Norma(user_id = vk_address, day = day, nick = old_params[0][0],  charm = int(old_params[0][1]), old_point = int(result_tuple[1][0]))
=======

    # Пример обработки сообщения, содержащего лишь число
    if result_tuple[0] == 'число':
        preprevious_text = get_preprevious_text_message(message_id)
        # preprevious_message_parameters содержит команду и параметры из предпредыдущего сообщения
        preprevious_message_parameters = recognize_action(preprevious_text)
        if check_preprevious_text_message(preprevious_text):
            message = 'число засчитано'
>>>>>>> 1e3aa97e85c1057f4f3d23d9edc7ab2446a1531f
        else:
            message = 'число ни к чему не относится'
    return message


def bot_answer(user_action):
    """
    Промежуточная функция для получения нужных параметров:
    message_response - структура, состоящая из информации о сообщении(от кого, прикреплены ли материалы,
    текст сообщения)
    result_tuple - тульпа вида (команда, [параметры]), в случае если сообщение от пользователя было
    неверной структуры, то соответствующие значения тульпы будут None
    user_address_id - ссылка на страницу пользователя
    user_vk_name - имя пользователя ВК
    :param user_action: Действие пользователя (сюда попадают только действия типа "новое сообщение")
    """
    message_response = user_action['updates'][len(user_action['updates']) - 1]
    query_str = message_response['object']['message']['text']
    result_tuple = recognize_action(query_str)
<<<<<<< HEAD
=======
    print(result_tuple)
>>>>>>> 1e3aa97e85c1057f4f3d23d9edc7ab2446a1531f
    user_id = message_response['object']['message']['from_id']
    user_address_id = get_user_vk_id(user_id)
    user_vk_name = get_vk_name(user_id)
    message = form_message(result_tuple, user_address_id, user_vk_name, get_message_id(message_response))
    send_message(message, user_id)


def server_listening(api_version, group_id, access_token):
    """
    Функция будет работать бесконечно, обрабатывая только сообщения от пользователей.
    Сначала она получает адресс Long Poll сервера ВК, затем обращается к нему для прослушки
    действий пользователей
    :param api_version: Версия VK API
    :param group_id: ID сообщества
    :param access_token: токен сообщества
    """
    dictionary = get_dictionary(get_long_poll_server(api_version, group_id, access_token))
    server_address = dictionary['response']['server']
    key = dictionary['response']['key']
    ts = int(dictionary['response']['ts'])
    while True:
        request_string = "{}?act=a_check&key={}&ts={}&wait=25".format(server_address, key, str(ts))
        vk_response = requests.get(request_string)
        user_action = get_dictionary(vk_response)
        new_ts = int(user_action['ts'])
        if len(user_action['updates']) > 0:
            action_type = user_action['updates'][len(user_action['updates']) - 1]['type']
        else:
            action_type = None
        if action_type == 'message_new' and ts != new_ts:
            bot_answer(user_action)
            ts = new_ts


<<<<<<< HEAD
# In[4]:


server_listening(api_version, group_id, token)


# In[ ]:





# In[ ]:




=======
server_listening(api_version, group_id, token)
>>>>>>> 1e3aa97e85c1057f4f3d23d9edc7ab2446a1531f
