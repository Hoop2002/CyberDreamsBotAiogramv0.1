import time
import datetime


def load_txt(name, phone_number, visit_time, lesson_type):
    with open("log.txt", "a", encoding="utf-8") as logfile:
        logfile.write("ФИО - {0}\n"
                      "Номер телефона - {1}\n"
                      "Время визита - {2}\n"
                      "Тип занятий - {3}\n"
                      "Дата сохранения -- {4}\n"
                      "_____________________________\n".format(name,
                                                               phone_number,
                                                               visit_time,
                                                               lesson_type,
                                                               datetime.date.today()))
