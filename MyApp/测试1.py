import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import os
import requests
import time
# 基础配置
# lastLoginUser=shentianxiong; orgId=10513; roleId=974828; crm_prod_position_id=974827; login_type=0; beta_device_uuid=VjJfbWlzdWNuXzEwMDAwMzlfTENSM1BEUkFDTU1OVDhQQjlSR1AzSkhDQVU;
# beta_user_token=admin_user_1837253_web_d6f80b090085e7e60e57069bb59108de; PRO_CASTGC=ldap
url = "https://opw.yunshanmeicai.com/opw-api/common/getCompanySsuPrice"
headers = {
    'Content-Type': 'application/json',
    'cookie': ''

        }
data = {
    'companyId': '82267790',
    'ssuId': '',
    'adjustRecordId': ''
        }
token_header='beta_user_token='
file_path = None
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
file_path = os.path.join(desktop_path, "tk.txt")

class DataProcessingApp:

    def __init__(self, root):
        self.root = root
        self.root.title("批量查询3.0")

        # 存储中间结果的数组
        self.input_c_array = []
        self.output_array = []

        # 创建界面
        self.create_widgets()

    def create_widgets(self):
        # 输入框A
        frame_a = ttk.Frame(self.root)
        frame_a.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(frame_a, text="输入门店:").pack(side=tk.LEFT)
        self.entry_a = ttk.Entry(frame_a)
        self.entry_a.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        # 输入框B
        frame_b = ttk.Frame(self.root)
        frame_b.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(frame_b, text="输入tk:").pack(side=tk.LEFT)
        self.entry_b = ttk.Entry(frame_b)
        self.entry_b.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        # 输入框C（多行）
        frame_c = ttk.Frame(self.root)
        frame_c.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)

        ttk.Label(frame_c, text="输入SSU（每行一个）:").pack(anchor=tk.W)
        self.text_c = scrolledtext.ScrolledText(frame_c, height=10)
        self.text_c.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        # 按钮区域
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        self.process_button = ttk.Button(button_frame, text="查询", command=self.start_processing)
        self.process_button.pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(button_frame, text="清空所有", command=self.clear_all).pack(side=tk.LEFT, padx=5)

        # 输出框D
        frame_d = ttk.LabelFrame(self.root, text="输出结果")
        frame_d.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)

        self.text_d = scrolledtext.ScrolledText(frame_d, height=10)
        self.text_d.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.text_d.config(state=tk.DISABLED)

    def validate_inputs(self):
        """验证输入A和C是否为空"""
        a_value = self.entry_a.get().strip()
        c_value = self.text_c.get("1.0", tk.END).strip()

        # if not a_value:
        #     messagebox.showerror("错误", "门店不能为空")
        #     return False

        if not c_value:
            messagebox.showerror("错误", "SSU不能为空")
            return False

        return True

    def read_inputs(self):
        """读取所有输入值"""
        # 读取A和B
        a_value = self.entry_a.get().strip()
        b_value = self.entry_b.get().strip()

        # 读取C并转换为数组（跳过空行）
        c_text = self.text_c.get("1.0", tk.END)
        c_array = [line.strip() for line in c_text.splitlines() if line.strip()]

        print(a_value)
        print(b_value)
        print(c_array)

        return a_value, b_value, c_array

    def process_data(self, a_value, b_value, c_array):
        # 清空之前的输出数组
        self.output_array = []

        if a_value:
            data['companyId'] = a_value                # 是否使用默认ID
        headers['cookie'] = token_header+b_value       # 拼接tk
        headers['cookie'] = headers['cookie'].strip()  # 去除头尾空白（包括换行）
        print(headers)
        # 循环处理C数组中的每个元素
        for i, item in enumerate(c_array):
            data['ssuId']=item
            try:
                response =requests.post(url,headers=headers,json=data)
                output_value =response.json()['data'][0]['price']
                # 将结果添加到输出数组
                self.output_array.append(output_value)
                time.sleep(1.5)
            except Exception as e:
                self.output_array.append(0)
        # 处理完成后显示结果
        self.display_results(a_value,b_value)

    def display_results(self,a_value,b_value):
        """将结果输出到文本框D"""
        self.text_d.config(state=tk.NORMAL)
        self.text_d.delete(1.0, tk.END)

        for result in self.output_array:
            self.text_d.insert(tk.END, str(result) + "\n")

        self.text_d.config(state=tk.DISABLED)

        # 清空数组，为下次运行做准备
        self.input_c_array = []
        self.output_array = []
        data['companyId'] = '82267790'  # 修改回默认ID

    def start_processing(self):
        """开始处理数据"""
        if not self.validate_inputs():
            return

        # 禁用按钮，防止重复点击
        self.process_button.config(state=tk.DISABLED)

        # 读取输入值
        a_value, b_value, c_array = self.read_inputs()

        # 在新线程中处理数据，避免界面卡顿
        thread = threading.Thread(
            target=self.process_data,
            args=(a_value, b_value, c_array)
        )
        thread.daemon = True
        thread.start()

        # 重新启用按钮（在线程完成后）
        self.root.after(100, self.check_thread, thread)

    def check_thread(self, thread):
        """检查线程是否完成，完成后重新启用按钮"""
        if thread.is_alive():
            self.root.after(100, self.check_thread, thread)
        else:
            self.process_button.config(state=tk.NORMAL)

    def clear_all(self):
        """清空所有输入框和输出框"""
        self.entry_a.delete(0, tk.END)
        self.text_c.delete(1.0, tk.END)

        self.text_d.config(state=tk.NORMAL)
        self.text_d.delete(1.0, tk.END)
        self.text_d.config(state=tk.DISABLED)

        # 清空数组
        self.input_c_array = []
        self.output_array = []

def main():
    root = tk.Tk()
    root.geometry("600x700")
    app = DataProcessingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()