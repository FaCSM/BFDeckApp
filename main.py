from tkinter import *
import serial
import threading
import pyautogui
import sqlite3
from tkinter import ttk
from serial.tools import list_ports
backlight = 0
wireless = 0
lenght = 0
wight = 0
clicked_button = 0
conBaudRate=9600
timeout_time = 5
serial_thread
started = 0
stop_flag = 0
buttons = {0:"Null"}
def connect_db():
    conn = sqlite3.connect('sqlite.sql')
    cursor = conn.cursor()
    return conn, cursor

def readProfile():
    global lenght,wight
    conn, cursor = connect_db()
    for i in range(1,lenght*wight+1):
        cursor.execute("SELECT func FROM main WHERE button = ?", (i,))
        result = cursor.fetchone()
        if result:
            buttons[i] = result[0]  # Результат - это кортеж, и func находится в первом элементе
        else:
            buttons[i] = ""

def writeProfile(button,func):
    global lenght,wight
    conn, cursor = connect_db()
    cursor.execute("INSERT OR REPLACE INTO main (button, func) VALUES (?, ?)", (button, func))
    conn.commit()
    conn.close()

def scan():
    ports = serial.tools.list_ports.comports()
    for port in ports:
            try:
                if port.manufacturer == 'Microsoft':
                    continue
                ser = serial.Serial(port.device, baudrate=conBaudRate,timeout=timeout_time)
                ser.write("10,0".encode())
                response = ser.readline().decode().strip().split(",")
                if len(response) == 4:
                     return port.device
                ser.close()
            except serial.SerialException:
                pass

    return None

def button_grid_click(num):
    global clicked_button, root, buttons
    clicked_button = num

    if clicked_button in buttons:
        root.Entry.delete(0, END)
        root.Entry.insert(0, f"{buttons[clicked_button]}")
    print(f"button_grid_click:{num}")

def reConnect():
    global lenght,wireless,wight,backlight,root
    con = scan()
    if con != None:
        ser = serial.Serial(con, baudrate=conBaudRate,timeout=timeout_time)
        ser.write("10,0".encode())
        response = ser.readline().decode().strip().split(",")
        lenght = int(response[0])
        wight = int(response[1])
        backlight = int(response[2])
        wireless = int(response[3])
        root.Label1.configure(text='''Connected''')
        print(f"Connected {con}")
        for widget in frame.winfo_children():
            widget.destroy()
        frame.pack()
        # Создаем кнопки и размещаем их в сетке
        for y in range(wight):
          for x in range(lenght):
            button = ttk.Button(frame, text=f"{lenght*y+x+1}",command=lambda num=lenght*y+x+1: button_grid_click(num))
            button.grid(row=y, column=x, padx=5, pady=5)
        root.Button3.configure(state=NORMAL)
        readProfile()
    else:
        root.Label1.configure(text='''Not connected''')
        print(f"Not connected")
        root.Button3.configure(state=DISABLED)

def saveButton():
    global root
    print(f"saveButton1: {root.Entry.get()}")
    if int(clicked_button) != 0:
        writeProfile(clicked_button,root.Entry.get().lower())
        readProfile()
        print(f"saveButton2: {buttons[clicked_button]}")

def Working():
    global stop_flag
    ser = serial.Serial(scan(), baudrate=conBaudRate,timeout=1)
    while stop_flag == 0:
        response = ser.readline().decode().strip()
        try:
            num = int(response[3:])
            if num in buttons:
                keys = buttons[num].split('+')
                pyautogui.hotkey(*keys)
        except:
            pass
        print(f"Working: {response}")
    ser.close()

def startStop():
    global root, serial_thread,started,stop_flag
    if started == 0:
        started = 1
        stop_flag = 0
        root.Button3.configure(text='''Stop''')
        serial_thread = threading.Thread(target=Working)
        serial_thread.start()
        print("startStop1: запущен")
    elif started == 1:
        started = 0
        root.Button3.configure(text='''Start''')
        stop_flag = 1
        serial_thread.join()
        print("startStop2: остановлен")

def window_close():
    global stop_flag
    if (started == 1):
        stop_flag = 1
        serial_thread.join()
    root.destroy()  # ручное закрытие окна и всего приложения
    print("window_close: Закрытие приложения")

root = Tk()     # создаем корневой объект - окно
root.title("BFDeck APP")     # устанавливаем заголовок окна
root.geometry("900x600")    # устанавливаем размеры окна
root.minsize(900,600)
frame = ttk.Frame(root)
root.configure(background="black")
root.configure(highlightbackground="black")
root.configure(highlightcolor="white")
root.Button1 = ttk.Button(root, command=reConnect)
root.Button1.place(relx=0.0, rely=0.0, height=30, width=48)
root.Button1.configure(text='''Recon''')
root.Entry = ttk.Entry(root)
root.Entry.place(relx=0.833, rely=0.0, height=21, relwidth=0.104)
root.Button2= ttk.Button(root, command=saveButton)
root.Button2.configure(text='''Save''')
root.Button2.place(relx=0.944, rely=0.0, height=30, width=48)
root.Button3= ttk.Button(root,command=startStop,state=DISABLED)
root.Button3.configure(text='''Start''')
root.Button3.place(relx=0.0, rely=0.1, height=30, width=48)
root.Label1 = ttk.Label(root)
root.Label1.place(relx=0.056, rely=0.0, height=23, width=117)
root.Label1.configure(anchor='w')
root.Label1.configure(compound='left')
root.Label1.configure(text='''Not connected''')
root.iconbitmap(default="BFDeck.ico")
root.protocol("WM_DELETE_WINDOW", window_close)
reConnect()
root.mainloop()
