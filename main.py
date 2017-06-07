import os
import json, requests
import hashlib
import time
import modules.cms as cms
import modules.database as dbase

# Список расширений, которые будут сканироваться
permitted_extensions = (".php", ".js", ".htm", ".html", "pl")

# Список зараженных файлов
anamnesis_list = []


class TheKadeshi:
    """
    Основной класс
    """
    
    # Список файлов для сканирования
    files_list = []
    
    # Суммарный размер файлов в байтах
    total_files_size = 0
    
    # База сигнатур
    signatures_database = {'h': [], 'r': []}
    
    def get_files_list(self):
        """
        Функция получения списка файлов
        
        :return: Ничего, просто заполняет список файлов
        """
        
        for root, dirs, files in os.walk('./'):
            for name in files:
                if name.endswith(permitted_extensions):
                    file_path = os.path.join(root, name)
                    file_size = os.path.getsize(file_path)
                    self.total_files_size = self.total_files_size + file_size
                    self.files_list.append({'path': file_path, 'size': file_size})
        pass
    
    def load_signatures(self):
        """
        Функция загрузки сигнатур
        """
        db = dbase.Database()
        self.signatures_database['h'] = db.get_hash_signatures()
    
    def scan_files(self):
        """
        Функция сканирования файлов
        
        :return: Ничего
        """
        
        global signatures_database
        
        global total_files_size
        
        # Флаг, нужно ли продолжать сканирование
        need_to_scan = True
        
        # Таймер
        timer_start = time.time()
        
        # Сколько просканировано в байтах, необходимо для вычисления скорости
        total_scanned = 0
        
        # Расчетная скорость сканирования
        scan_speed = 0
        
        # Счетчик проверенных файлов
        scanner_counter = 0
        
        # Берем файл из списка
        for file_item in self.files_list:
            anamnesis_element = []
            current_progress = (total_scanned + file_item['size']) * 100 / self.total_files_size
            
            is_file_clean = True
            
            is_file_error = False
            
            # with open(file_item['path'], encoding="latin-1", mode='rb') as f:
            with open(file_item['path'], mode='rb') as f:
                
                # Тут у нас обработчик ошибок.
                try:
                    content = f.read()
                
                # Это если в коде внезапно нашелся недопустимый символ.
                except UnicodeDecodeError as e:
                    is_file_error = True
                    print("Incorrect char in ", file_item['path'], e)
                
                # Если нет ошибок чтения, то сканируем
                if len(content) > 0:
                    # Хеш сумма файла
                    file_hash = hashlib.sha256(content).hexdigest()
                    
                    for signature in self.signatures_database['h']:
                        if file_hash == signature['expression']:
                            
                            is_file_clean = False
                            
                            anamnesis_element = {
                                'path': file_item['path'],
                                'title': signature['title'],
                                'action': signature['action']
                            }
                            
                            if signature['action'] == 'delete':
                                need_to_scan = False
                                
                                # print(file_hash)
                                # todo тут будет сканирование по регуляркам
                                # Если сканирование по хэщ ничего не выявило, то ищем по сигнатурам
                                # if need_to_scan == True:
                                
                                # Берем сигнатуру из списка
                                # for signature in signatures_database['r']:
                                # pass
                                # print(signature)
            
            total_scanned = total_scanned + file_item['size']
            current_time = time.time()
            time_delta = current_time - timer_start
            if time_delta != 0:
                scan_speed = total_scanned // time_delta // 1024
            scanner_counter = scanner_counter + 1
            
            file_message = "\x1b[92m" + "Clean" + "\x1b[39m"
            if is_file_error:
                file_message = "Error"
            else:
                if not is_file_clean:
                    file_message = "\x1b[31m" + "Infected" + "\x1b[39m" + ": " + "\x1b[93m" + anamnesis_element[
                        'title'] + "\x1b[39m"
            
            print('[{0:.2f}% | {1!s}kB/s] {2!s} ({3!s})'.format(current_progress, scan_speed, file_item['path'],
                                                                file_message, sep=" ", end="", flush=True))
            
            # print(len(anamnesis_element))
            if len(anamnesis_element) > 0:
                anamnesis_list.append(anamnesis_element)


print("Ready")
kdsh = TheKadeshi()
kdsh.get_files_list()
print("Found", len(kdsh.files_list), "files, ~", kdsh.total_files_size, "bytes")

kdsh.load_signatures()

kdsh.scan_files()

for element in anamnesis_list:
    print(element)
