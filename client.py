import sys
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QTableWidgetItem, QMessageBox
from requests import get, post, put, delete
from werkzeug.security import generate_password_hash, check_password_hash
import time


def set_password(password):
    hashed_password = generate_password_hash(password)
    return hashed_password


def check_password(self, password):
    return check_password_hash(self.hashed_password, password)


USER = ''
task_diff = {'A': 10, 'B': 15, 'C': 20, 'D': 25, 'E': 30, 'F': 35}


class RegisterWindow(QWidget):
    """Форма регистрации нового пользователя"""
    def __init__(self):
        super().__init__()
        uic.loadUi('data/ui/Register.ui', self)

        self.RegButton.clicked.connect(self.reg)
        self.return_home_Button.clicked.connect(self.go_back)

    def reg(self):
        """Функция регистрации. Она проверят чтоб все строчки в форме были заполнены,
           чтоб совпадали пароли и чтоб был уникальный логин. Если все условия соблюдены,
           то создаёт нового пользователя, иначе звполняет error_label."""
        global USER
        if self.create_Password_lineEdit.text() == self.prove_Password_lineEdit.text():
            if self.create_Nickname_lineEdit.text() and self.create_Email_lineEdit.text() and \
                    self.create_Password_lineEdit.text():
                if self.create_Email_lineEdit.text() != "'":
                    if not get(f'http://127.0.0.1:5000/api/users/{self.create_Email_lineEdit.text()}'):
                        user = dict()
                        user['nickname'] = self.create_Nickname_lineEdit.text()
                        user['login'] = self.create_Email_lineEdit.text()
                        user['hashed_password'] = set_password(self.create_Password_lineEdit.text())
                        user['birthday'] = str(self.dateEdit.text())
                        user['status'] = 'student'
                        post('http://127.0.0.1:5000/api/user', json=user)
                        USER = get(f'http://127.0.0.1:5000/api/users/{self.create_Email_lineEdit.text()}').json()

                        self.open_form = MainWindow()
                        self.open_form.show()
                        self.hide()
                    else:
                        self.error_label.setText('Данный логин уже занят')
                else:
                    self.error_label.setText('Данные некорректны')

            else:
                self.error_label.setText('Обязательное поле не заполнено')
        else:
            self.error_label.setText('Пароли не совпадают')
        pass

    def go_back(self):
        """Возвращает на PreviewWindow"""
        self.preview_win = PreviewWindow()
        self.preview_win.show()
        self.hide()


class LoginWindow(QWidget):
    def __init__(self):
        """Форма авторизации уже существующего пользователя"""
        super().__init__()

        uic.loadUi('data/ui/Login.ui', self)

        self.remembrMe_checkBox.stateChanged.connect(self.rememberMe)
        self.LoginButton.clicked.connect(self.login)
        self.return_home_Button.clicked.connect(self.go_back)
        self.remember = False

    def login(self):
        """Функция входа в программу. Она получает пользователя из get-запроса и проверяет
           хешированный пароль с тем, который ввёл пользователь. Если пользователь с таким
           логином существует и пароль правильный, то входим в развилку. Если пользователь
           выбрал 'Запомнить меня', то в settings.txt записывается его логин.
           Далее открывается нужная форма в связи со статусом пользователя."""
        global USER
        try:
            USER = get(f'http://127.0.0.1:5000/api/users/{self.login_lineEdit.text()}').json()
            if check_password_hash(USER['hashed_password'], self.password_lineEdit.text()):
                if self.remember:
                    txt = open('data/settings.txt', 'r').read().split('\n')
                    txt.remove("'")
                    txt.insert(0, USER['login'])

                    self.settings = open('data/settings.txt', 'w')
                    self.settings.write('\n'.join(txt))
                    self.settings.close()

                self.main_form = MainWindow() if USER['status'] != 'developer' else DeveloperClient()
                self.main_form.show()
                self.close()
            else:
                raise ValueError()
        except:
            self.error_label.setText('Ошибка: данные некорректны')

    def rememberMe(self, state):
        if state == Qt.Checked:
            self.remember = True

    def go_back(self):
        """Возвращает на PreviewWindow"""
        self.preview_win = PreviewWindow()
        self.preview_win.show()
        self.hide()


class PreviewWindow(QWidget):
    """Форма приветственного окна"""
    def __init__(self):
        """Если логин указан в settings.txt, то сразу по нажатию на
           кнопку 'Войти' откроет либо MainWindow(), либо DeveloperClient()"""
        global USER
        super().__init__()
        uic.loadUi('data/ui/PreviewRegisterWindow.ui', self)
        self.RegButton.clicked.connect(self.open_reg_form)
        self.LoginButton.clicked.connect(self.open_login_form)

        txt = open('data/settings.txt', 'r').read().split('\n')
        if str(txt[0]) != "'":
            USER = get(f'http://127.0.0.1:5000/api/users/{txt[0]}').json()
            print(USER['status'])
            print(1)
            self.open_form = MainWindow() if USER['status'] != 'developer' else DeveloperClient()
        else:
            self.open_form = LoginWindow()

    def open_reg_form(self):
        self.reg_form = RegisterWindow()
        self.reg_form.show()
        self.hide()

    def open_login_form(self):
        self.open_form.show()
        self.hide()


class MainWindow(QMainWindow):
    """Форма главного окна"""
    def __init__(self):
        """current_task - id текушей задачи; task_id - id будущей задачи;
           Если задача с tsk_id существует, то обновляется current_task"""
        global current_task, task_id
        super().__init__()

        self.settings = open('data/settings.txt', 'r').read().split('\n')
        uic.loadUi('data/ui/client.ui', self)
        task_id = int(self.settings[-1])

        current_task = get(f'http://127.0.0.1:5000/api/task/{self.settings[-1]}')

        if current_task:
            current_task = current_task.json()
            self.post_task()
        else:
            current_task = current_task.json()
            self.get_next_task()

        """Заполняется таблица решённых задач"""
        n_tasks = USER['decided_tasks'].split('%')[2:]
        i = 0
        for j in n_tasks:
            task = get(f'http://127.0.0.1:5000/api/task/{j}')
            if task:
                self.decidedTasks.setRowCount(i + 1)
                task = task.json()
                self.update_decidedTasks(i, task)
                i += 1

        """Обработка кнопок"""
        self.ButtonNextTask.clicked.connect(self.get_next_task)
        self.ButtonPrevTask.clicked.connect(self.get_prev_task)
        self.ButtonSendAnswer.clicked.connect(self.check_answer)
        self.ButtonFindTask.clicked.connect(self.search)
        self.reportButton.clicked.connect(self.report)

        self.OneCalcButton.clicked.connect(self.num_operation)
        self.TwoCalcButton.clicked.connect(self.num_operation)
        self.ThreeCalcButton.clicked.connect(self.num_operation)
        self.FourCalcButton.clicked.connect(self.num_operation)
        self.FiveCalcButton.clicked.connect(self.num_operation)
        self.SixCalcButton.clicked.connect(self.num_operation)
        self.SevenCalcButton.clicked.connect(self.num_operation)
        self.EightCalcButton.clicked.connect(self.num_operation)
        self.NineCalcButton.clicked.connect(self.num_operation)
        self.ZeroCalcButton.clicked.connect(self.num_operation)

        self.PlusCalcButton.clicked.connect(self.arithmetic_operation)
        self.MinusCalcButton.clicked.connect(self.arithmetic_operation)
        self.MultiplyCalcButton.clicked.connect(self.arithmetic_operation)
        self.DivideCalcButton.clicked.connect(self.arithmetic_operation)
        self.DotCalcButton.clicked.connect(self.arithmetic_operation)

        self.DelCalcButton.clicked.connect(self.special_operation)
        self.EqualCalcButton.clicked.connect(self.special_operation)

        self.expr_board = ''
        self.number_board = ''

        self.labelCalcNums.setText(self.nice_view(self.number_board))
        self.update_profile()

        self.ButtonExit.clicked.connect(self.exit_from_account)
        self.add_task_pushButton.clicked.connect(self.add_task)

    """-----Функции калькулятора и боковой панели-----"""

    def num_operation(self, button=''):
        """Функция записывает введённые цифры в number_board.
           Число добавляетя в строку, потом преобразуется в нужный формат."""
        button = self.sender().text() if not button else button
        self.number_board += button
        self.number_board = str(int(self.number_board)) \
            if '.' not in self.number_board else str(float(self.number_board))
        self.labelCalcNums.setText(self.nice_view(self.number_board))

    def arithmetic_operation(self, button=''):
        """Функция обрабатывает арифметические знаки и точку.
           Если точка, то программа пробует преобразовать полученную строку в число.
           Если будет 2 точки, то вылетит ошибка и вторая точка не поставится.
           Если вводятся другие знаки, то соответствующий знак ставится в expr_board, либо
           меняет последний знак. Старый number_board становится частью expr_board
           и зануляется."""
        button = self.sender().text() if not button else button
        if button == '.':
            try:
                eval(self.number_board + '.')
                self.number_board += button
                self.labelCalcNums.setText(self.nice_view(self.number_board))
            except:
                pass
        else:
            self.expr_board += self.number_board
            if self.expr_board:
                if self.expr_board[-1] in ['+', '-', '*', '/']:
                    self.expr_board = self.expr_board[:-1] + button
                else:
                    self.expr_board += button
            else:
                self.expr_board += '0' + button

            self.number_board = ''
            self.labelExprCalc.setText(self.expr_board)
            self.labelCalcNums.setText(self.nice_view(self.number_board))

    def special_operation(self, button=''):
        """Функция обрабатывает знаки типа 'удалить символ' и 'посчитать'.
           Если нажата кнопка 'удалить символ', то удаляется последняя цифра числа.
           Если нажата кнопка 'посчитать', то возвращается результат expr_board (если
           его можно посчитать, иначе обрабатывается ошибка)"""
        button = self.sender().text() if not button else button
        if button == '⌫':
            self.number_board = self.number_board[:-1] if len(self.number_board) != 0 else ''
            self.labelCalcNums.setText(self.nice_view(self.number_board))
        if button == '=':
            try:
                self.expr_board += self.number_board
                self.number_board = str(eval(self.expr_board))
                self.labelCalcNums.setText(self.number_board)
                self.labelExprCalc.setText(self.expr_board + '=')
                self.expr_board = ''
            except:
                self.labelCalcNums.setText('Error')
                self.number_board, self.expr_board = '', ''

    def nice_view(self, string):
        return '0' if string == '' else string

    def search(self):
        """Функция ищет задачу по id, который ввёл пользователь."""
        global current_task
        text = self.lineSearch.text()
        try:
            current_task = get(f'http://127.0.0.1:5000/api/task/{int(text)}').json()
            self.post_task()
        except:
            pass

    def exit_from_account(self):
        """Функция обрабатывает кнопку выхода из аккаунта.
           В settings.txt затерается догин пользователя, окно закрывается
           и открывается PreviewWindow()"""
        valid = QMessageBox.question(self, 'Предупреждение',
                                     "Вы действительно хотите выйти из аккаунта?",
                                     QMessageBox.Yes, QMessageBox.No)
        if valid == QMessageBox.Yes:
            if self.settings[-2] == USER['login']:
                self.settings.clear()
                self.settings.append("'")
                self.settings.append(str(current_task['id']))

                self.write_settings = open("data/settings.txt", "w")
                self.write_settings.write('\n'.join(self.settings))
                self.write_settings.close()

            self.preview = PreviewWindow()
            self.preview.show()
            self.hide()

    """-----Работа с сервером-----"""

    def update_decidedTasks(self, last_section, current_task):
        global USER

        self.decidedTasks.setRowCount(last_section + 1)

        self.decidedTasks.setItem(last_section, 0, QTableWidgetItem(str(current_task['id'])))
        self.decidedTasks.item(last_section, 0).setFlags(self.decidedTasks.item(last_section, 0).flags() ^ Qt.ItemIsEditable)

        self.decidedTasks.setItem(last_section, 1, QTableWidgetItem(current_task['name']))
        self.decidedTasks.item(last_section, 1).setFlags(self.decidedTasks.item(last_section, 1).flags() ^ Qt.ItemIsEditable)

        self.decidedTasks.setItem(last_section, 2, QTableWidgetItem("+" + str(current_task['points'])))
        self.decidedTasks.item(last_section, 2).setFlags(self.decidedTasks.item(last_section, 2).flags() ^ Qt.ItemIsEditable)
        USER = get(f'http://127.0.0.1:5000/api/users/{self.create_Email_lineEdit.text()}').json()

    def update_profile(self):
        """Функция обновления профиля"""
        global USER

        USER = get(f'http://127.0.0.1:5000/api/users/{USER["login"]}').json()
        self.labelCalcNums.setText(self.nice_view(self.number_board))
        self.Nickname.setText(USER['nickname'])
        self.Nickname_small.setText(USER['nickname'])
        self.Status.setText(USER['status'])
        self.Points.setText(str(USER['points']))
        self.Email.setText(USER["login"])
        self.labelBD.setText(USER['birthday'])

        if USER['points'] < 150:
            self.AddTaskPage.setEnabled(False)
            self.permission_label.setText('Для доступа к добавлению задач необходимо набрать 150 баллов')
        else:
            self.AddTaskPage.setEnabled(True)
            self.permission_label.clear()

    def get_next_task(self):
        """Фунуция получает следующую по id задачу. Если id существует,
           то обновляется current_task, иначе происходит рекурсия."""
        global current_task, task_id
        print(1)
        max_id = get("http://127.0.0.1:5000/api/task/0").json()['count']
        print(2)
        decided_tasks = USER['decided_tasks'].split('%')
        if (len(set(decided_tasks)) - 2) != max_id:
            if task_id == max_id:
                task_id = 1
            else:
                task_id += 1
            print(1)
            possible_task = get(f'http://127.0.0.1:5000/api/task/{task_id}')
            print(2)
            if possible_task:
                current_task = possible_task.json()
                self.post_task()
            else:
                self.get_next_task()

    def get_prev_task(self):
        """Фунуция получает предыдущую по id задачу. Если id существует,
           то обновляется current_task, иначе происходит рекурсия."""
        global current_task, task_id
        decided_tasks = USER['decided_tasks'].split('%')
        max_id = get('http://127.0.0.1:5000/api/task/0').json()['count']

        if (len(set(decided_tasks)) - 2) != max_id:
            if task_id == 1:
                task_id = max_id
            else:
                task_id -= 1
            possible_task = get(f'http://127.0.0.1:5000/api/task/{task_id}')
            if possible_task:
                current_task = possible_task.json()
                self.post_task()
            else:
                self.get_prev_task()

    def report(self):
        global USER, current_task
        valid = QMessageBox.question(self, 'Предупреждение',
                                     "Вы действительно хотите пожаловаться на задачу?",
                                     QMessageBox.Yes, QMessageBox.No)
        if valid == QMessageBox.Yes:
            if str(current_task['id']) not in get(f'http://127.0.0.1:5000/api/users/{USER["login"]}').json()['reports'].split('%'):
                put(f'http://127.0.0.1:5000/api/users/{USER["login"]}', data={'decided': 0, 'reported': current_task["id"], 'points': 0})
                put(f'http://127.0.0.1:5000/api/task/{current_task["id"]}')
            else:
                valid = QMessageBox.warning(self, 'Предупреждение',
                                             "Вы уже отправили жалобу на задачу!",
                                             QMessageBox.Cancel)
        USER = get(f'http://127.0.0.1:5000/api/users/{self.create_Email_lineEdit.text()}').json()

    def check_answer(self):
        """Функция проверяет ответ пользователя с правильным ответом. Если ответ правильный,
           то запольняютя вспомогательные объекты, изменяется список решённых пользователем задач и
           начисляются баллы."""
        global task_id, current_task

        decided_tasks = get(f'http://127.0.0.1:5000/api/users/{USER["login"]}').json()['decided_tasks'].split('%')[2:]
        if str(current_task["user_login"]) != USER["login"]:
            if str(current_task["id"]) not in decided_tasks:
                try:
                    print(float(self.lineAnswer.text()), current_task['answer'])
                    if float(self.lineAnswer.text()) == float(current_task['answer']):
                        self.labelAnswStatus.setText('✓')
                        self.labelAnswStatus.setToolTip('Статус: зачтено')
                        put(f"http://127.0.0.1:5000/api/users/{USER['login']}",
                            data={'decided': current_task['id'], 'reported': 0, 'points': current_task['points']})
                        self.update_profile()
                        self.update_decidedTasks(len(USER['decided_tasks'].split('%')) - 3, current_task)
                        self.warningLabel.setText("")
                    else:
                        self.labelAnswStatus.setText('✕')
                        self.labelAnswStatus.setToolTip('Статус: неправельное решение')
                except:
                    self.warningLabel.setText("Ответ должен быть представлен числом")
            else:
                self.warningLabel.setText("Вы уже решили эту задачу")
        else:
            self.warningLabel.setText("Вы не можете решить свою же задачу")

    def post_task(self):
        """Задача отображается в форме."""
        global current_task
        current_task = current_task
        txt = open('data/settings.txt', 'r').read().split('\n')
        txt.remove(txt[-1])
        txt.append(str(current_task["id"]))

        new_settings = open('data/settings.txt', 'w')
        new_settings.write('\n'.join(txt))
        new_settings.close()

        self.TextTask.setPlainText(current_task['content'])
        self.labelTitle.setText(current_task['name'])
        self.labelID.setText(f'ID: {current_task["id"]}')
        self.ScoreLabel.setText(f'{current_task["points"]} баллов')
        self.warningLabel.setText('')
        self.labelAuthor.setText('Автор: ' + get(f'http://127.0.0.1:5000/api/users/{current_task["user_login"]}').json()["nickname"])
        if str(current_task["id"]) in str(USER['decided_tasks']):
            self.lineAnswer.setText(current_task['answer'])
            self.labelAnswStatus.setText('✓')
            self.labelAnswStatus.setToolTip('Статус: зачтено')
        else:
            self.lineAnswer.setText('')
            self.labelAnswStatus.setText('')
            self.labelAnswStatus.setToolTip('Статус')

    def add_task(self):
        """Если у пользователя уже наборалось 150 баллов, то он может добавлять задачи.
           Если дан числовой ответ и все строки заполненны, то задача добавляется в базу данных."""
        dct = {'name': self.title_lineEdit.text(), 'user_login': USER['login'],
               'points': int(task_diff[self.difficult_lvl_comboBox.currentText()]),
               'content': self.task_text_TextEdit.toPlainText(), 'answer': self.answer_lineEdit.text()}
        try:
            if not (self.title_lineEdit.text() and
                    self.task_text_TextEdit.toPlainText() and self.answer_lineEdit.text()):
                raise NameError()
            dct['answer'] = float(dct['answer'])
        except ValueError:
            self.error_label.setStyleSheet('color: rgb(255, 154, 0);')
            self.error_label.setText('Некорректный ответ (ответ должен быть представлен числом)')
            return
        except NameError:
            self.error_label.setStyleSheet('color: rgb(255, 154, 0);')
            self.error_label.setText('Все поля должны быть заполнены')
            return

        post(f'http://127.0.0.1:5000/api/tasks/{USER["login"]}', json=dct)
        lst_tasks = get(f'http://127.0.0.1:5000/api/tasks/{USER["login"]}').json()['tasks']
        self.error_label.setStyleSheet('color: rgb(0, 200, 0);')
        self.error_label.setText(f'Задача успешно добавлена! ID задачи: {max([task["id"] for task in lst_tasks])}')

    # обработка кнопок клавиатуры

    def keyPressEvent(self, event):
        if event.text() in map(str, range(0, 10)):
            self.num_operation(event.text())

        if event.text() in ['+', '-', '*', '/']:
            self.arithmetic_operation(event.text())

        if event.key() == Qt.Key_Enter:
            self.special_operation('=')

        if event.key() == Qt.Key_Backspace:
            self.special_operation('⌫')


class DeveloperClient(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('data/ui/developer_client.ui', self)
        self.settings = open('data/settings.txt', 'r').read().split('\n')
        self.tasks_list = get("http://127.0.0.1:5000/api/tasks/'").json()['tasks']
        self.Nickname_small.setText(USER['nickname'])

        self.del_task_button.clicked.connect(self.del_task)
        self.open_user_tasks_button.clicked.connect(self.open_user_tasks)
        self.del_user_button.clicked.connect(self.del_user)
        self.update_tasks_button.clicked.connect(self.get_reported_tasks)
        self.ButtonExit.clicked.connect(self.exit_from_account)

        self.add_task_pushButton.clicked.connect(self.add_task)

        self.get_reported_tasks()

    def get_reported_tasks(self):
        self.tasks_list = get("http://127.0.0.1:5000/api/tasks/'").json()['tasks']
        self.update_tasks()
        self.labelStatus.setText("Все задачи")

    def del_task(self):
        rows = list(set([i.row() for i in self.tableWidget.selectedItems()]))
        if rows:
            valid = QMessageBox.question(self, 'Предупреждение',
                                         "Вы действительно удалить выбранные задачи?\n" +
                                         f"ID задач: {list(map(lambda i: int(self.tableWidget.item(i, 0).text()), rows))}",
                                         QMessageBox.Yes, QMessageBox.No)
            if valid == QMessageBox.Yes:
                for i in rows:
                    delete(f"http://127.0.0.1:5000/api/task/{int(self.tableWidget.item(i, 0).text())}")
                if len(self.labelStatus.text()) > 10:
                    self.tasks_list = get(f"http://127.0.0.1:5000/api/tasks/{self.labelStatus.text().split()[-1]}").json()['tasks']
                    self.update_tasks()
                else:
                    self.get_reported_tasks()
        else:
            warWindow = QMessageBox.warning(self, 'Предупреждение',
                                            'Отметьте задачи для удаления!')

    def open_user_tasks(self):
        row = list(set([i.row() for i in self.tableWidget.selectedItems()]))
        if len(row) == 1:
            self.tasks_list = get(f"http://127.0.0.1:5000/api/tasks/{str(self.tableWidget.item(row[0], 4).text())}").json()['tasks']
            self.labelStatus.setText(f"Все задачи пользователя {str(self.tableWidget.item(row[0], 4).text())}")
            self.update_tasks()
        else:
            warWindow = QMessageBox.warning(self, 'Предупреждение',
                                            'Отметьте только одного пользователя!')

    def del_user(self):
        row = list(set([i.row() for i in self.tableWidget.selectedItems()]))
        if len(row) == 1:
            valid = QMessageBox.question(self, 'Предупреждение',
                                         f"Вы действительно хотите удалить пользователя {str(self.tableWidget.item(row[0], 4).text())}?",
                                         QMessageBox.Yes, QMessageBox.No)
            if valid == QMessageBox.Yes:
                delete(f"http://127.0.0.1:5000/api/tasks/{str(self.tableWidget.item(row[0], 4).text())}")
                delete(f"http://127.0.0.1:5000/api/users/{str(self.tableWidget.item(row[0], 4).text())}")
                self.get_reported_tasks()
        else:
            warWindow = QMessageBox.warning(self, 'Предупреждение',
                                            'Отметьте только одного пользователя!')

    def update_tasks(self):
        for j in range(len(self.tasks_list)):
            self.tableWidget.setRowCount(j + 1)
            task = self.tasks_list[j]
            self.tableWidget.setItem(j, 0, QTableWidgetItem(str(task['id'])))
            self.tableWidget.item(j, 0).setFlags(self.tableWidget.item(j, 0).flags() ^ Qt.ItemIsEditable)

            self.tableWidget.setItem(j, 1, QTableWidgetItem(str(task['name'])))
            self.tableWidget.item(j, 1).setFlags(self.tableWidget.item(j, 1).flags() ^ Qt.ItemIsEditable)

            self.tableWidget.setItem(j, 2, QTableWidgetItem(str(task['content'])))
            self.tableWidget.item(j, 2).setFlags(self.tableWidget.item(j, 2).flags() ^ Qt.ItemIsEditable)

            self.tableWidget.setItem(j, 3, QTableWidgetItem(str(task['answer'])))
            self.tableWidget.item(j, 3).setFlags(self.tableWidget.item(j, 3).flags() ^ Qt.ItemIsEditable)

            self.tableWidget.setItem(j, 4, QTableWidgetItem(str(task['user_login'])))
            self.tableWidget.item(j, 4).setFlags(self.tableWidget.item(j, 4).flags() ^ Qt.ItemIsEditable)

            self.tableWidget.setItem(j, 5, QTableWidgetItem(str(task['reports'])))
            self.tableWidget.item(j, 5).setFlags(self.tableWidget.item(j, 5).flags() ^ Qt.ItemIsEditable)

        self.tableWidget.resizeColumnsToContents()

    def add_task(self):
        """Разработчик может добавлять задачи.
           Если дан числовой ответ и все строки заполненны, то задача добавляется в базу данных."""
        dct = {'name': self.title_lineEdit.text(), 'user_login': USER['login'],
               'points': int(task_diff[self.difficult_lvl_comboBox.currentText()]),
               'content': self.task_text_TextEdit.toPlainText(), 'answer': self.answer_lineEdit.text()}
        try:
            if not (self.title_lineEdit.text() and
                    self.task_text_TextEdit.toPlainText() and self.answer_lineEdit.text()):
                raise NameError()
            dct['answer'] = float(dct['answer'])
        except ValueError:
            self.error_label.setStyleSheet('color: rgb(255, 154, 0);')
            self.error_label.setText('Некорректный ответ (ответ должен быть представлен числом)')
            return
        except NameError:
            self.error_label.setStyleSheet('color: rgb(255, 154, 0);')
            self.error_label.setText('Все поля должны быть заполнены')
            return

        post(f'http://127.0.0.1:5000/api/tasks/{USER["login"]}', json=dct)
        lst_tasks = get(f'http://127.0.0.1:5000/api/tasks/{USER["login"]}').json()['tasks']
        self.error_label.setStyleSheet('color: rgb(0, 200, 0);')
        self.error_label.setText(f'Задача успешно добавлена! ID задачи: {max([task["id"] for task in lst_tasks])}')

    def exit_from_account(self):
        valid = QMessageBox.question(self, 'Предупреждение',
                                     "Вы действительно хотите выйти из аккаунта?",
                                     QMessageBox.Yes, QMessageBox.No)
        if valid == QMessageBox.Yes:
            if self.settings[-2] != "'":
                self.settings.remove(self.settings[-2])
                self.settings.insert(0, "'")

                self.write_settings = open("data/settings.txt", "w")
                self.write_settings.write('\n'.join(self.settings))
                self.write_settings.close()

            self.close()


app = QApplication(sys.argv)
ex = PreviewWindow()
ex.show()
sys.exit(app.exec_())
