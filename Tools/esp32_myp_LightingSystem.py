import os, json
import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import serial
import time
import struct
import serial.tools.list_ports

# 全局變量
box_data_sent = False  # 在全局變量區域初始化
rectangles = []
capturing = False
output_file = None
frame = None
original_frame = None
num_rectangles = 0
rect_start = None
paused = False
stopped = False
cap = None
recording = False
video_file = None
total_frames = 0
fps = 0
frame_width = 0
frame_height = 0
ser = None  # Serial port

program_path = os.path.abspath(os.path.dirname(__file__))

output_Name = None

# 固定方框大小 (8mm x 8mm，假設DPI為96)
dpi = 96
mm_per_inch = 25.4
rect_width = int(8 / mm_per_inch * dpi)
rect_height = rect_width  # 正方形

# 波特率選項
baudrate_options = [9600, 57600, 115200, 256000, 460800, 512000, 921600, 1500000, 3000000]
selected_baudrate = None


def read_config_info():
    global box_data_sent, rectangles, capturing, output_file, frame, original_frame
    global num_rectangles, rect_start, paused, stopped, cap, recording, video_file, total_frames
    global fps, frame_width, frame_height, ser, program_path,output_Name

    program_path = os.path.abspath(os.path.dirname(__file__))
    config_path = program_path+ '\\config.json'

    if not os.path.exists(config_path) :
        with open(config_path, "w+") as outfile:
            outfile.write()
        print('not config ')
    else:
        with open(config_path, 'r') as openfile:
            config = json.load(openfile)

        box_data_sent = config.get('box_data_sent',None) if config.get('box_data_sent',None) != None else box_data_sent
        rectangles = config.get('rectangles',None) if config.get('rectangles',None) != None else rectangles
        capturing = config.get('capturing',None) if config.get('capturing',None) != None else capturing
        output_file = config.get('output_file',None) if config.get('output_file',None) != None else output_file
        # frame = config.get('frame',None) if config.get('frame',None) != None else frame
        # original_frame = config.get('original_frame',None) if config.get('original_frame',None) != None else original_frame


        num_rectangles = config.get('num_rectangles',None) if config.get('num_rectangles',None) != None else num_rectangles
        rect_start = config.get('rect_start',None) if config.get('rect_start',None) != None else rect_start
        paused = config.get('paused',None) if config.get('paused',None) != None else paused
        stopped = config.get('stopped',None) if config.get('stopped',None) != None else stopped
        # cap = config.get('cap',None) if config.get('cap',None) != None else cap
        recording = config.get('recording',None) if config.get('recording',None) != None else recording
        video_file = config.get('video_file',None) if config.get('video_file',None) != None else video_file
        total_frames = config.get('total_frames',None) if config.get('total_frames',None) != None else total_frames


        fps = config.get('fps',None) if config.get('fps',None) != None else fps
        frame_width = config.get('frame_width',None) if config.get('frame_width',None) != None else frame_width
        frame_height = config.get('frame_height',None) if config.get('frame_height',None) != None else frame_height
        ser = config.get('ser',None) if config.get('ser',None) != None else ser

        output_Name = config.get('output_Name',None) if config.get('output_Name',None) != None else output_Name
        
        try:

            if num_rectangles:
                light_quantity_label.config(text=str(num_rectangles))

            if output_file:
                output_label.config(text=output_file)
                with open(output_file, "wb") as f:
                    pass


            if video_file:
                video_label.config(text=video_file)
                cap = cv2.VideoCapture(video_file)
                if cap.isOpened():
                    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    video_length = total_frames / fps if fps else 0
                    minutes = int(video_length // 60)
                    seconds = int(video_length % 60)
                    total_frames_label.config(text=f"總幀數: {total_frames}")
                    progress_slider.config(to=total_frames-1)
                    ret, original_frame = cap.read()
                    if ret:
                        frame = original_frame.copy()
                        update_video_canvas(video_canvas, frame)
                        video_info_label.config(text=f"解析度: {frame_width}x{frame_height}, FPS: {fps}, 時長: {minutes}分{seconds}秒")
                    cap.release()

            if rectangles:
                for idx,i in enumerate(rectangles) :
                    cv2.rectangle(frame, i[0], i[1], (0, 255, 0), 2)
                    cv2.putText(frame, f'{idx+1}', (i[0][0], i[0][1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                    update_video_canvas(video_canvas, frame)
                    if len(rectangles) == num_rectangles:
                        capturing = True


        except Exception as e:
            print(e)
            messagebox.showerror("錯誤", str(e))        
        print('read config')



    print(program_path)

def save_config_info():
    global box_data_sent, rectangles, capturing, output_file, frame, original_frame
    global num_rectangles, rect_start, paused, stopped, cap, recording, video_file, total_frames
    global fps, frame_width, frame_height, ser, program_path , output_Name

    program_path = os.path.abspath(os.path.dirname(__file__))
    config_path = program_path+ '\\config.json'

    if not os.path.exists(config_path) :
        with open(config_path, "w+") as outfile:
            outfile.write()
        print('not config ')
    else:

        config = {
            'box_data_sent':box_data_sent, 'rectangles':rectangles, 'capturing':capturing, 'output_file':output_file, 
            ##
            # 'frame':frame.tolist(), 
            # 'original_frame':original_frame.tolist(),

            'num_rectangles':num_rectangles, 'rect_start':rect_start, 'paused':paused, 'stopped':stopped, 
            ##
            # 'cap':cap, 

            'recording':recording, 'video_file': video_file, 'total_frames':total_frames,

            'fps':fps, 'frame_width':frame_width, 'frame_height':frame_height ,'ser':ser,'output_Name':output_Name

        }
        print(type(frame))
        print(config)

        with open(config_path, "w+") as outfile:
            running_config = json.dumps(config,indent=4)
            outfile.write(running_config)

        
        print('read config')



    print(program_path)


def get_all_buf():
    global rectangles , video_file ,output_Name,program_path ,total_frames
    global frame, original_frame, capturing, paused, stopped, output_file, cap, recording, ser
    global box_data_sent  # 添加全局變量來跟踪是否已發送方框坐標


    if video_file  :
        cap = cv2.VideoCapture(video_file)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) -1

        if output_Name != None:
            output_file = program_path+f'//{output_Name}_grbBuf_{len(rectangles)}_{total_frames}.bin'

        if output_file:
            with open(output_file, 'wb') as f:
                pass

    
        while(cap.isOpened()):
            ret, frame = cap.read()
            if not ret:
                return
            avg_rgb_values = calculate_average_rgb(frame, rectangles)
            color_data = []
            with open(output_file, 'ab') as f:
                for i in avg_rgb_values:
                    r,g,b = list( reversed(i) )
                    packed_data = struct.pack('BBB', g,r,b)
                    f.write(packed_data)
                    
            
            # with open(video_file, 'ab') as f:
            #     f.write(packed_data)


def save_to_buffer():
    global  frame, original_frame,cap

    # print(len(frame))
    # print(len(frame[0]))
    # print(len(frame[0][0]))
    # print(len(frame.tolist()))

    # print(len(original_frame))
    # print(len(original_frame[0]))
    # print(len(original_frame[0][0]))
    # print(original_frame[0][0])
    # print(type(original_frame))
    # print(len(original_frame.tolist()))

    print('*'*30)

    get_all_buf()
    print('*'*15)


    return


def init_serial(port, baudrate):
    global ser
    if ser and ser.is_open:
        ser.close()
    try:
        ser = serial.Serial(port, baudrate)
        time.sleep(2)  # 等待串口初始化
        if ser.is_open:
            print(f"串行端口 {port} 打開成功，波特率為 {baudrate}。")
        else:
            print(f"串行端口 {port} 打開失敗。")
    except Exception as e:
        print(f"初始化串口失敗: {e}")

def select_video_file():
    global video_file, cap, total_frames, fps, frame, original_frame, frame_width, frame_height
    video_file = filedialog.askopenfilename(filetypes=[("視頻文件", "*.mp4;*.avi;*.mov")])
    if video_file:
        video_label.config(text=video_file)
        cap = cv2.VideoCapture(video_file)
        if cap.isOpened():
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) -1
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            video_length = total_frames / fps if fps else 0
            minutes = int(video_length // 60)
            seconds = int(video_length % 60)
            total_frames_label.config(text=f"總幀數: {total_frames}")
            progress_slider.config(to=total_frames-1)
            ret, original_frame = cap.read()
            if ret:
                frame = original_frame.copy()
                update_video_canvas(video_canvas, frame)
                video_info_label.config(text=f"解析度: {frame_width}x{frame_height}, FPS: {fps}, 時長: {minutes}分{seconds}秒")
            cap.release()

def save_output_file():
    global output_file,program_pathm,output_Name
    # output_file = filedialog.asksaveasfilename(defaultextension=".bin", filetypes=[("二進制文件", "*.bin")])
    # if output_file:
    #     output_label.config(text=output_file)
    #     output_file = os.path.abspath(output_file)  # 获取绝对路径
    #     with open(output_file, 'wb') as f:
    #         pass  # 初始化文件但不寫入任何內容

    try:
        result = simpledialog.askstring("燈效名稱", "請輸入燈效名稱:")
        print(result)
        if result is not None and result !='':
            output_Name = result
            output_file = program_path+f'\{output_Name}.bin'
            output_label.config(text=str(output_file))
            with open(output_file, 'wb') as f:
                pass  # 初始化文件但不寫入任何內容

        else:
            messagebox.showerror("錯誤", "請輸入有效的燈效名稱。")
    except Exception as e:
        messagebox.showerror("錯誤", str(e))

def draw_rectangles(event):
    global rectangles, capturing, rect_start, frame

    if frame is None:
        return

    canvas_width = video_canvas.winfo_width()
    canvas_height = video_canvas.winfo_height()
    frame_height, frame_width, _ = frame.shape

    # 計算縮放比例
    scale_x = frame_width / canvas_width
    scale_y = frame_height / canvas_height

    # 轉換鼠標點擊的坐標
    x = int(event.x * scale_x)
    y = int(event.y * scale_y)

    if event.type == tk.EventType.ButtonPress and len(rectangles) < num_rectangles:
        rect_start = (x, y)
    elif event.type == tk.EventType.ButtonRelease and len(rectangles) < num_rectangles:
        rect_end = (x + rect_width, y + rect_height)
        rectangles.append((rect_start, rect_end))
        cv2.rectangle(frame, rect_start, rect_end, (0, 255, 0), 2)
        cv2.putText(frame, f'{len(rectangles)}', (rect_start[0], rect_start[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        update_video_canvas(video_canvas, frame)
        if len(rectangles) == num_rectangles:
            capturing = True

def calculate_average_rgb(frame, rectangles):
    avg_rgb_values = []
    for rect_start, rect_end in rectangles:
        roi = frame[rect_start[1]:rect_end[1], rect_start[0]:rect_end[0]]
        avg_color_per_row = np.average(roi, axis=0)
        avg_color = np.average(avg_color_per_row, axis=0)
        avg_rgb_values.append([int(c) for c in avg_color])  # 轉換為整數
    return avg_rgb_values

def update_video_canvas(canvas, frame):
    frame_resized = cv2.resize(frame, (canvas.winfo_width(), canvas.winfo_height()))
    image = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(image)
    image_tk = ImageTk.PhotoImage(image)
    canvas.create_image(0, 0, anchor=tk.NW, image=image_tk)
    canvas.image_tk = image_tk

def update_color_canvas(canvas, rectangles, avg_rgb_values):
    canvas.delete("all")  # 清空畫布
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    frame_resized = np.zeros((canvas_height, canvas_width, 3), dtype=np.uint8)

    # 計算縮放比例，以確保右邊窗口的方框與左邊窗口的方框保持1:1比例
    scale_x = canvas_width / frame_width
    scale_y = canvas_height / frame_height

    for i, ((rect_start, rect_end), rgb) in enumerate(zip(rectangles, avg_rgb_values)):
        # 確保方框位置比例一致
        rect_start_scaled = (int(rect_start[0] * scale_x), int(rect_start[1] * scale_y))
        rect_end_scaled = (int(rect_end[0] * scale_x), int(rect_end[1] * scale_y))
        color = tuple(rgb)
        cv2.rectangle(frame_resized, rect_start_scaled, rect_end_scaled, color, -1)
        cv2.putText(frame_resized, str(i + 1), (rect_start_scaled[0], rect_start_scaled[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

    image = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(image)
    image_tk = ImageTk.PhotoImage(image)
    canvas.create_image(0, 0, anchor=tk.NW, image=image_tk)
    canvas.image_tk = image_tk

def update_frame():
    global rectangles
    global frame, original_frame, capturing, paused, stopped, output_file, cap, recording, ser
    global box_data_sent  # 添加全局變量來跟踪是否已發送方框坐標

    if stopped:
        return

    if not paused and cap and cap.isOpened():
        ret, original_frame = cap.read()
        
        # print(original_frame)
        if not ret:
            # 重置全局變量
            rectangles = []
            capturing = False

            cap.release()
            messagebox.showinfo("信息", "視頻處理完成。數據已保存到文件。")
            clear_inputs()  # 清除輸入框和標籤內容
            return

        # 在原始幀上畫出已選擇的矩形和編號
        frame = original_frame.copy()
        for i, (rect_start, rect_end) in enumerate(rectangles):
            cv2.rectangle(frame, rect_start, rect_end, (0, 255, 0), 2)
            cv2.putText(frame, f'{i + 1}', (rect_start[0], rect_start[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        update_video_canvas(video_canvas, frame)


        if capturing and recording:
            avg_rgb_values = calculate_average_rgb(original_frame, rectangles)
            print(avg_rgb_values)
            update_color_canvas(color_canvas, rectangles, avg_rgb_values)

            # 將所有 255 值替換為 254
            avg_rgb_values = [[254 if c == 255 else c for c in rgb] for rgb in avg_rgb_values]
            print(avg_rgb_values)

            # 創建方框坐標數據，i 需要倒序
            if not box_data_sent:  # 只有在第一次時發送方框坐標
                box_data = b''.join(
                    struct.pack('BBBBB', 255, len(rectangles) - 1 - i, 255,
                                int(rect_start[0] / 80), int(rect_start[1] / 45))  # 1280/16 = 80, 720/16 = 45
                    for i, (rect_start, rect_end) in enumerate(reversed(rectangles))
                )

                print(f"Sending box data to serial: {box_data}")  # 添加日志输出

                if ser and ser.is_open:
                    try:
                        # 先發送方框坐標數據
                        ser.write(box_data)
                    except Exception as e:
                        print(f"串口寫入失敗: {e}")

                box_data_sent = True  # 設置標誌為已發送

                # 將方框坐標數據寫入文件
                with open(output_file, 'ab') as f:
                    f.write(box_data)  # 寫入方框坐標數據

            # 創建顏色數據
            color_data = b''.join(
                struct.pack('BBBBB', 255, i, b, g, r) 
                for i, (r, g, b) in reversed(list(enumerate(avg_rgb_values)))
            )

#            print(f"Sending color data to serial: {color_data}")  # 添加日志输出

            if ser and ser.is_open:
                try:
                    # 然後發送顏色數據
                    ser.write(color_data)
                except Exception as e:
                    print(f"串口寫入失敗: {e}")

            with open(output_file, 'ab') as f:
                f.write(color_data)  # 只寫入顏色數據

        # 更新滑塊位置
        progress_slider.set(int(cap.get(cv2.CAP_PROP_POS_FRAMES)))

    video_canvas.after(30, update_frame)

def start_processing():
    global output_file, cap, stopped, recording, rectangles, capturing, paused, frame, original_frame, video_file

    try:
        # 檢查是否選擇了串口
        # if not selected_port.get():
        #     messagebox.showerror("錯誤", "請選擇串口。")
        #     return

        if num_rectangles <= 0:
            messagebox.showerror("錯誤", "請輸入有效的擷取數量。")
            return

        if not video_file:
            messagebox.showerror("錯誤", "請選擇視頻文件。")
            return

        if not output_file:
            messagebox.showerror("錯誤", "請選擇輸出文件。")
            return


        # 打開視頻文件
        cap = cv2.VideoCapture(video_file)
        if not cap.isOpened():
            messagebox.showerror("錯誤", "無法打開視頻。")
            return

        # 重置全局變量
        # rectangles = []
        # capturing = False
        paused = False
        frame = None
        original_frame = None

        # 初始化串口
        # init_serial(selected_port.get(), selected_baudrate.get())  # 使用選擇的串口

        stopped = False
        recording = True
        update_frame()

    except Exception as e:
        print(e)
        messagebox.showerror("錯誤", str(e))

def on_slider_change(event):
    global cap, paused

    if cap and cap.isOpened():
        slider_value = int(progress_slider.get())
        cap.set(cv2.CAP_PROP_POS_FRAMES, slider_value)
        if paused:
            ret, frame = cap.read()
            if ret:
                update_video_canvas(video_canvas, frame)

def toggle_pause():
    global paused, recording
    paused = not paused
    if paused:
        recording = False
    else:
        recording = True

def stop_video():
    global stopped, cap

    stopped = True
    if cap:
        cap.release()
    video_canvas.delete("all")
    color_canvas.delete("all")

def undo_last_rectangle():
    global rectangles, frame, original_frame
    if original_frame is None:
        return  # 如果 original_frame 為 None 則退出
    if rectangles:
        rectangles.pop()
        frame = original_frame.copy()
        for i, (rect_start, rect_end) in enumerate(rectangles):
            cv2.rectangle(frame, rect_start, rect_end, (0, 255, 0), 2)
            cv2.putText(frame, f'{i + 1}', (rect_start[0], rect_start[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        update_video_canvas(video_canvas, frame)

def clear_inputs():
    video_label.config(text="未選擇視頻文件")
    output_label.config(text="未選擇輸出文件")

def fast_forward():
    global cap, fps
    if cap and cap.isOpened():
        current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        new_frame = min(current_frame + int(fps * 10), total_frames - 1)
        cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)
        if paused:
            ret, frame = cap.read()
            if ret:
                update_video_canvas(video_canvas, frame)
            progress_slider.set(new_frame)

def rewind():
    global cap, fps
    if cap and cap.isOpened():
        current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        new_frame = max(current_frame - int(fps * 10), 0)
        cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)
        if paused:
            ret, frame = cap.read()
            if ret:
                update_video_canvas(video_canvas, frame)
            progress_slider.set(new_frame)

def set_light_quantity():
    global num_rectangles
    try:
        result = simpledialog.askinteger("燈光數量", "請輸入燈光數量:")
        if result is not None and result > 0:
            num_rectangles = result
            light_quantity_label.config(text=str(num_rectangles))
        else:
            messagebox.showerror("錯誤", "請輸入有效的燈光數量。")
    except Exception as e:
        messagebox.showerror("錯誤", str(e))

def select_serial_port():
    global ser
    try:
        port = selected_port.get()  # 使用下拉菜單的選擇
        if port:
            if ser and ser.is_open:
                ser.close()
            init_serial(port, selected_baudrate.get())  # 使用選擇的波特率
    except Exception as e:
        messagebox.showerror("錯誤", str(e))
        
def update_serial_ports():
    # 清空舊的串口選項
    port_menu.delete(0, tk.END)
    
    # 獲取可用的串口並添加到下拉菜單
    for port in serial.tools.list_ports.comports():
        port_menu.add_radiobutton(label=port.device, variable=selected_port, value=port.device)

    # 每隔1秒再次檢查
    root.after(1000, update_serial_ports)        

def main():
    global video_canvas, color_canvas, video_label, output_label, progress_slider, total_frames_label, video_info_label, light_quantity_label, frame_width, frame_height, selected_baudrate, selected_port, port_menu, root

    # 創建Tkinter界面
    root = tk.Tk()  # 確保在這裡創建root
    root.title("視頻處理介面")

    # 初始化波特率選項變量
    selected_baudrate = tk.IntVar(value=1000000)

    # 初始化串行端口
    selected_port = tk.StringVar()  # 新增這行以存儲選擇的串口
 
    # 創建菜單欄
    menubar = tk.Menu(root)
    root.config(menu=menubar)

    # 添加文件菜單
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="文件", menu=file_menu)
    file_menu.add_command(label="讀取配置信息", command=read_config_info)
    file_menu.add_command(label="儲存配置信息", command=save_config_info)

    file_menu.add_command(label="儲存RGB緩存", command=save_to_buffer)

    file_menu.add_command(label="選擇視頻文件", command=select_video_file)
    file_menu.add_command(label="選擇輸出文件", command=save_output_file)
    file_menu.add_separator()
    file_menu.add_command(label="退出", command=root.quit)

    # 添加控制菜單
    control_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="控制", menu=control_menu)
    control_menu.add_command(label="播放", command=play_video)
    control_menu.add_command(label="暫停", command=toggle_pause)
    control_menu.add_command(label="停止", command=stop_video)
    control_menu.add_command(label="快進10秒", command=fast_forward)
    control_menu.add_command(label="倒退10秒", command=rewind)
    control_menu.add_separator()
    control_menu.add_command(label="開始", command=start_processing)
    control_menu.add_command(label="燈光數量", command=set_light_quantity)
    control_menu.add_command(label="重選", command=undo_last_rectangle)

    # 添加串口選擇的下拉菜單
    port_menu = tk.Menu(control_menu, tearoff=0)
    control_menu.add_cascade(label="串口選擇", menu=port_menu)

    # 初始化串口選項
    update_serial_ports()  # 開始定時更新串口

    # 添加波特率選擇
    baudrate_menu = tk.Menu(control_menu, tearoff=0)
    control_menu.add_cascade(label="波特率選擇", menu=baudrate_menu)
    for rate in baudrate_options:
        baudrate_menu.add_radiobutton(label=str(rate), variable=selected_baudrate, value=rate)

    # 將尺寸從厘米轉換為像素
    width_cm = 50
    height_cm = 28
    width_px = int((width_cm / 2.54) * dpi)
    height_px = int((height_cm / 2.54) * dpi)

    root.geometry(f"{width_px}x{height_px}")

    # 設置介面底色
    root.configure(bg='#4B4B4B')

    # 創建主框架
    top_frame = tk.Frame(root, bg='#4B4B4B')
    top_frame.pack(padx=10, pady=5, side=tk.TOP)

    bottom_frame = tk.Frame(root, bg='#4B4B4B')
    bottom_frame.pack(padx=10, pady=5, side=tk.TOP)

    # 左右視頻視窗框架
    video_frame = tk.Frame(top_frame, bg='#4B4B4B')
    video_frame.pack(side=tk.LEFT, padx=10)

    # 左邊的播放視頻視窗
    video_canvas = tk.Canvas(video_frame, width=int(20 * dpi / 2.54), height=int(11.2 * dpi / 2.54), bg="black")
    video_canvas.pack(side=tk.LEFT)

    # 右邊的顏色顯示視窗
    color_canvas = tk.Canvas(video_frame, width=int(20 * dpi / 2.54), height=int(11.2 * dpi / 2.54), bg="white")
    color_canvas.pack(side=tk.LEFT, padx=20)

    # 綁定滑鼠事件
    video_canvas.bind("<ButtonPress-1>", draw_rectangles)
    video_canvas.bind("<ButtonRelease-1>", draw_rectangles)
    
    # 視頻信息標籤
    video_info_label = tk.Label(bottom_frame, text="解析度: N/A, FPS: N/A, 時長: N/A", bg='#4B4B4B', fg='white', font=("Helvetica", 12))
    video_info_label.pack(pady=5)

    # 滑塊控件框架
    slider_frame = tk.Frame(bottom_frame, bg='#4B4B4B')
    slider_frame.pack(pady=5)

    # 滑塊描述標籤
    slider_label = tk.Label(slider_frame, text="視頻進度", bg='#4B4B4B', fg='white', font=("Helvetica", 12))
    slider_label.grid(row=0, column=0, padx=5)

    # 滑塊控件
    progress_slider = tk.Scale(slider_frame, from_=0, to=100, orient=tk.HORIZONTAL, length=900, command=on_slider_change)
    progress_slider.grid(row=0, column=1, padx=5)

    # 總幀數標籤
    total_frames_label = tk.Label(slider_frame, text="視頻總幀數: 0", bg='#4B4B4B', fg='white', font=("Helvetica", 12))
    total_frames_label.grid(row=0, column=2, padx=5)

    # 按鈕框架
    button_frame = tk.Frame(bottom_frame, bg='#4B4B4B')
    button_frame.pack(pady=5)

    # 開始按鈕
    start_button = tk.Button(button_frame, text="開始", command=start_processing, width=13, height=3, font=("Helvetica", 12))
    start_button.grid(row=0, column=0, padx=5)

    # 播放按鈕
    play_button = tk.Button(button_frame, text="播放", command=play_video, width=13, height=3, font=("Helvetica", 12))
    play_button.grid(row=0, column=1, padx=5)

    # 倒退按鈕
    rewind_button = tk.Button(button_frame, text="倒退10秒", command=rewind, width=13, height=3, font=("Helvetica", 12))
    rewind_button.grid(row=0, column=2, padx=5)

    # 暫停按鈕
    pause_button = tk.Button(button_frame, text="暫停", command=toggle_pause, width=13, height=3, font=("Helvetica", 12))
    pause_button.grid(row=0, column=3, padx=5)

    # 快進按鈕
    fast_forward_button = tk.Button(button_frame, text="快進10秒", command=fast_forward, width=13, height=3, font=("Helvetica", 12))
    fast_forward_button.grid(row=0, column=4, padx=5)

    # 停止按鈕
    stop_button = tk.Button(button_frame, text="停止", command=stop_video, width=13, height=3, font=("Helvetica", 12))
    stop_button.grid(row=0, column=5, padx=5)

    # 重選按鈕
    undo_button = tk.Button(button_frame, text="重選", command=undo_last_rectangle, width=13, height=3, font=("Helvetica", 12))
    undo_button.grid(row=0, column=6, padx=5)

    # 輸入框架
    input_frame = tk.Frame(bottom_frame, bg='#4B4B4B')
    input_frame.pack(side=tk.LEFT, padx=5)

    # 燈光數量按鈕
    light_button = tk.Button(input_frame, text="燈光數量", width=19, height=2, font=("Helvetica", 12), command=set_light_quantity)
    light_button.grid(row=0, column=0, padx=5, pady=5, sticky="w")

    # 顯示燈光數量的標籤
    light_quantity_label = tk.Label(input_frame, text="未設置", bg='#4B4B4B', fg='white', font=("Helvetica", 12))
    light_quantity_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    # 選擇視頻文件按鈕
    select_video_button = tk.Button(input_frame, text="選擇視頻文件", command=select_video_file, width=19, height=2, font=("Helvetica", 12))
    select_video_button.grid(row=1, column=0, padx=5, pady=5, sticky="w")

    # 顯示所選視頻文件路徑的標籤
    video_label = tk.Label(input_frame, text="未選擇視頻文件", bg='#4B4B4B', fg='white', font=("Helvetica", 12))
    video_label.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    # 選擇輸出文件按鈕
    select_output_button = tk.Button(input_frame, text="選擇輸出文件", command=save_output_file, width=19, height=2, font=("Helvetica", 12))
    select_output_button.grid(row=2, column=0, padx=5, pady=5, sticky="w")

    # 顯示所選輸出文件路徑的標籤
    output_label = tk.Label(input_frame, text="未選擇輸出文件", bg='#4B4B4B', fg='white', font=("Helvetica", 12))
    output_label.grid(row=2, column=1, padx=5, pady=5, sticky="w")

    # 綁定鍵盤事件
    root.bind("<space>", lambda event: toggle_pause())

    root.mainloop()

def play_video():
    global paused, recording
    paused = False
    recording = True

if __name__ == "__main__":
    main()





