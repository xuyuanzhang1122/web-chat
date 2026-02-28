import sys
import time
import random
import requests
import os
import json
import re
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QTextEdit, QLineEdit, QPushButton, 
                            QComboBox, QLabel, QStackedWidget, QMessageBox, QToolButton)
from PyQt6.QtCore import (Qt, QTimer, pyqtSignal, QThread, QByteArray, 
                         QSize)
from PyQt6.QtGui import QIcon, QPixmap, QFont, QTextCursor
import resources  # 这将是我们的资源文件
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 添加预设问答字典
RESPONSES = {
    "通用问候": [
        "你好！很高兴见到你。",
        "你好啊！有什么我可以帮你的吗？",
        "嗨！今天过得怎么样？",
        "你好！让我们开始愉快的对话吧。"
    ],
    
    "身份询问": [
        "我是DeepSeek AI助手，一个由DeepSeek开发的大型语言模型。",
        "我是一个AI助手，可以帮助你解决各种问题。",
        "你可以叫我DeepSeek，我是一个智能对话助手。",
        "我是你的AI助手，随时准备为你提供帮助。"
    ],
    
    "能力介绍": [
        "我可以帮你编程、写作、回答问题，以及进行各种有趣的对话。",
        "我擅长处理文本、代码和各类知识问题，让我知道你需要什么帮助。",
        "作为AI助手，我可以协助你完成多种任务，包括但不限于编程、写作和问答。",
        "我的知识库涵盖多个领域，可以为你提供专业的建议和帮助。"
    ],
    
    "感谢回应": [
        "不用谢！很高兴能帮到你。",
        "这是我的荣幸，随时都可以找我聊天。",
        "能帮助你我很开心，有需要随时说。",
        "不客气，这就是我的工作。"
    ],
    
    "道别": [
        "再见！希望今天的对话对你有帮助。",
        "下次见！如果还有问题随时来问我。",
        "再会！祝你有愉快的一天。",
        "拜拜！期待下次与你交流。"
    ],
    
    "默认回复": [
        "抱歉，服务器当前负载过高，请稍后重试。",
        "对不起，我现在有点忙，请稍后再试。",
        "系统正在处理其他请求，请稍候。",
        "当前用户较多，请稍后重新尝试。"
    ]
}

# 关键词匹配字典
KEYWORDS = {
    "你好": "通用问候",
    "嗨": "通用问候",
    "在吗": "通用问候",
    "hi": "通用问候",
    "hello": "通用问候",
    
    "你是谁": "身份询问",
    "你叫什么": "身份询问",
    "介绍一下": "身份询问",
    "你是什么": "身份询问",
    
    "你能做什么": "能力介绍",
    "你会什么": "能力介绍",
    "能干什么": "能力介绍",
    "有什么功能": "能力介绍",
    
    "谢谢": "感谢回应",
    "感谢": "感谢回应",
    "多谢": "感谢回应",
    "thank": "感谢回应",
    
    "再见": "道别",
    "拜拜": "道别",
    "bye": "道别",
    "goodbye": "道别"
}

# 修改全局样式表
STYLE_SHEET = """
QMainWindow {
    background-color: #121212;  /* 更深的背景色 */
}

QTextEdit {
    background-color: #121212;
    border: none;
    border-radius: 8px;
    padding: 20px;
    font-size: 14px;
    line-height: 1.6;
    color: #ffffff;
    selection-background-color: #264F78;
}

QLineEdit {
    background-color: #1a1a1a;  /* 输入框深色背景 */
    border: 1px solid #333333;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 14px;
    color: #ffffff;
    min-height: 24px;
}

QPushButton#sendButton {
    background-color: #2b5eb3;  /* 更鲜艳的蓝色 */
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 14px;
}

QPushButton#sendButton:hover {
    background-color: #3373d6;
}

QPushButton#sendButton:pressed {
    background-color: #0055FF;
}

QToolButton {
    background-color: #007AFF;
    color: white;
    border: none;
    border-radius: 12px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 500;
    min-width: 150px;
}

QToolButton:hover {
    background-color: #0066FF;
}

QComboBox {
    background-color: #f7f8fa;
    border: none;
    border-radius: 12px;
    padding: 10px 16px;
    min-width: 200px;
    font-size: 14px;
}

QLabel {
    color: #1c1c1e;
    font-size: 14px;
    font-weight: 500;
}

QWidget#inputContainer {
    background-color: #1a1a1a;
    border: 1px solid #333333;
    border-radius: 8px;
    padding: 8px;
}

/* 滚动条样式 */
QScrollBar:vertical {
    border: none;
    background: #f7f8fa;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #c7c7cc;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #a8a8ad;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}
"""

# 修改思考过程模板
THINKING_TEMPLATE = """
<div style="
    margin: 8px 16px;
    background-color: #1a1a1a;
    border-radius: 8px;
    overflow: hidden;
">
    <div style="
        padding: 8px 12px;
        background-color: #2d2d2d;
        font-size: 12px;
        opacity: 0.7;
    ">思考过程</div>
    <div style="
        padding: 12px;
        opacity: 0.8;
        font-size: 13px;
        line-height: 1.5;
    ">{content}</div>
</div>
"""

# 修改加载动画
LOADING_ANIMATION = """
<div style="text-align: center; margin: 15px 0;">
    <div style="
        display: inline-block;
        width: 24px;
        height: 24px;
        border: 2px solid #007AFF;
        border-radius: 50%;
        border-top-color: transparent;
        animation: spin 1s linear infinite;
        margin-bottom: 8px;
    "></div>
    <div style="
        color: #007AFF;
        font-size: 13px;
        font-weight: 500;
    ">思考中...</div>
    <style>
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</div>
"""

# 添加请求处理线程类
class RequestThread(QThread):
    # 修改信号定义
    response_received = pyqtSignal(str)  # 用于发送完整响应
    response_complete = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self, url, model, prompt):
        super().__init__()
        self.url = url
        self.model = model
        self.prompt = prompt
    
    def run(self):
        try:
            response = requests.post(
                self.url,
                json={
                    "model": self.model,
                    "prompt": self.prompt,
                    "stream": False  # 改为非流式请求
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                if "response" in data:
                    self.response_received.emit(data["response"])
                self.response_complete.emit()
            else:
                self.error_occurred.emit(f"请求失败（状态码：{response.status_code}）")
        except Exception as e:
            self.error_occurred.emit(f"请求错误：{str(e)}")

class LoadingThread(QThread):
    finished = pyqtSignal()
    
    def run(self):
        # 减少加载时间到1秒
        time.sleep(1)
        self.finished.emit()

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenWebUI")
        self.setMinimumSize(1000, 600)
        
        # 预加载资源
        self.preload_resources()
        
        # 创建堆叠窗口部件用于切换不同页面
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # 初始化变量
        self.current_message = ""
        self.message_count = 0
        self.thinking_timer = None
        self.response_timer = None
        self.chat_display = None  # 将在create_chat_page中初始化
        self.input_field = None   # 将在create_chat_page中初始化
        
        # 添加Ollama连接状态和模型信息
        self.ollama_connected = False
        self.ollama_url = "http://12.nat0.cn:15012/api/generate"
        self.model_name = None  # 将在连接时设置
        
        # 添加声明内容
        self.disclaimer = """本程序由作者超级牛逼的徐院长制作。仅供娱乐，没有接入任何的API以及大模型。
如果需要大模型服务请去各大模型官网使用！

问题及反馈：QQ：1571032052"""
        
        # 修改连接按钮文本
        self.connect_button = QToolButton(self)
        self.connect_button.setText("连接真实AI(体验版)")
        self.connect_button.setStyleSheet("""
            QToolButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 12px;
            }
            QToolButton:hover {
                background-color: #45a049;
            }
        """)
        self.connect_button.hide()
        self.connect_button.clicked.connect(self.toggle_ollama_connection)
        
        # 创建页面
        self.create_loading_page()
        self.create_chat_page()
        
        # 显示加载页面
        self.stacked_widget.setCurrentIndex(0)
        
        # 启动加载线程
        self.loading_thread = LoadingThread()
        self.loading_thread.finished.connect(self.show_chat_page)
        self.loading_thread.start()
        
        # 直接设置样式表，避免运行时解析
        self.setStyleSheet(STYLE_SHEET)
        
        # 添加思考过程模板作为实例属性
        self.thinking_template = """
        <div style="
            margin: 8px 0;
            background-color: #2D2D2D;
            border-radius: 8px;
        ">
            <div style="
                padding: 8px 12px;
                display: flex;
                align-items: center;
                border-bottom: 1px solid #363636;
            ">
                <span style="
                    color: #A0A0A0;
                    font-size: 12px;
                ">思考过程</span>
            </div>
            <div style="
                padding: 12px;
                color: #A0A0A0;
                font-size: 13px;
            ">
                {content}
            </div>
        </div>
        """
        
        # 添加用于存储当前响应的变量
        self.current_response = ""
        self.current_message_cursor = None
        self.is_processing = False  # 新增处理状态标志
        
    def preload_resources(self):
        """预加载资源，避免运行时加载"""
        try:
            # 预加载图标
            self.app_icon = QIcon()
            icon_data = resources.get_icon_data()
            icon_pixmap = QPixmap()
            if icon_pixmap.loadFromData(icon_data):
                self.app_icon = QIcon(icon_pixmap)
                self.setWindowIcon(self.app_icon)
            
            # 预加载样式表
            self.ollama_style = """
            QMainWindow {
                background-color: #f8f9fa;
            }
            
            QTextEdit {
                background-color: white;
                border: 1px solid #e1e4e8;
                border-radius: 12px;
                padding: 15px;
                font-size: 14px;
                line-height: 1.6;
                selection-background-color: #cce5ff;
            }
            
            QLineEdit {
                background-color: white;
                border: 1px solid #e1e4e8;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                min-height: 24px;
            }
            
            QPushButton#sendButton {
                background-color: #1a73e8;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 14px;
                font-weight: bold;
                min-width: 80px;
                min-height: 36px;
            }
            
            QPushButton#sendButton:hover {
                background-color: #1557b0;
            }
            
            QComboBox {
                background-color: white;
                border: 1px solid #e1e4e8;
                border-radius: 8px;
                padding: 8px 12px;
                min-width: 200px;
                font-size: 14px;
            }
            
            QWidget#inputContainer {
                background-color: white;
                border: 1px solid #e1e4e8;
                border-radius: 12px;
                padding: 5px;
            }
            """
            
            # 预加载模型信息
            self.available_models = {
                "Llama3.2-1b": "huihui_ai/llama3.2-abliterate:1b",
                "DeepSeek-1.5b": "deepseek-r1:1.5b"
            }
        except Exception as e:
            print(f"Error preloading resources: {e}")
    
    def create_loading_page(self):
        """优化加载页面"""
        loading_page = QWidget()
        layout = QVBoxLayout()
        
        # 使用预加载的图标
        logo_label = QLabel()
        if hasattr(self, 'app_icon'):
            scaled_pixmap = self.app_icon.pixmap(100, 100)
            logo_label.setPixmap(scaled_pixmap)
        else:
            logo_label.setText("DeepSeek")
            logo_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 添加进度提示
        self.progress_label = QLabel("正在初始化...")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_label.setStyleSheet("""
            font-size: 14px;
            color: #666666;
            margin-top: 10px;
        """)
        
        layout.addStretch()
        layout.addWidget(logo_label)
        layout.addWidget(self.progress_label)
        layout.addStretch()
        
        loading_page.setLayout(layout)
        self.stacked_widget.addWidget(loading_page)
        
    def create_chat_page(self):
        chat_page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 顶部工具栏
        toolbar = QHBoxLayout()
        self.model_label = QLabel("当前模型:")
        self.model_selector = QComboBox()
        # 初始显示假模型
        self.model_selector.addItems(["deepseek-coder-r1", "deepseek-coder-v3"])
        self.model_selector.setEnabled(False)  # 初始禁用
        
        toolbar.addWidget(self.model_label)
        toolbar.addWidget(self.model_selector)
        toolbar.addWidget(self.connect_button)
        toolbar.addStretch()
        
        # 聊天显示区域
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setMinimumHeight(400)
        
        # 自定义聊天气泡样式
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
        """)
        
        # 输入区域容器
        input_container = QWidget()
        input_container.setObjectName("inputContainer")
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(15, 10, 15, 10)
        input_layout.setSpacing(10)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("输入消息...")
        
        send_button = QPushButton("发送")  # 添加文字
        send_button.setObjectName("sendButton")
        # send_button.setIcon(QIcon(":/icons/send.png"))  # 注释掉图标，因为我们现在用文字
        # send_button.setIconSize(QSize(20, 20))
        send_button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(send_button)
        
        layout.addLayout(toolbar)
        layout.addWidget(self.chat_display)
        layout.addWidget(input_container)
        
        chat_page.setLayout(layout)
        self.stacked_widget.addWidget(chat_page)
        
        # 连接信号
        send_button.clicked.connect(self.send_message)
        self.input_field.returnPressed.connect(self.send_message)
        
    def show_chat_page(self):
        self.chat_display.append("连接成功！\n系统已就绪，请开始对话。")
        self.stacked_widget.setCurrentIndex(1)
        
    def format_message(self, sender, message):
        if sender == "System":
            return f'''
                <div style="
                    margin: 16px 0;
                    padding: 12px;
                    background-color: rgba(0, 122, 255, 0.1);
                    border-radius: 8px;
                    text-align: center;
                ">
                    <div style="color: #007AFF;">
                        <span style="margin-right: 8px;">🎉</span>
                        <span>{message}</span>
                    </div>
                </div>
            '''
        elif sender == "You":
            return f'''
                <div style="
                    margin: 16px 0;
                    padding: 0 16px;
                    display: flex;
                    justify-content: flex-end;
                ">
                    <div style="
                        max-width: 80%;
                        background-color: #2b5eb3;
                        padding: 12px 16px;
                        border-radius: 12px 2px 12px 12px;
                        color: #ffffff;
                    ">{message}</div>
                </div>
            '''
        else:  # Assistant 消息
            return f'''
                <div style="
                    margin: 16px 0;
                    padding: 0 16px;
                    display: flex;
                    justify-content: flex-start;
                ">
                    <div style="
                        max-width: 80%;
                        background-color: #2d2d2d;
                        padding: 12px 16px;
                        border-radius: 2px 12px 12px 12px;
                        color: #ffffff;
                    ">{self.format_markdown(message)}</div>
                </div>
            '''

    def get_thinking_process(self, message):
        """生成思考过程的文本"""
        # 分析输入并生成思考过程
        thinking_content = f"""• 分析输入: "{message}" • 处理问题 • 生成回复 • 格式化输出"""
        return thinking_content

    def show_disclaimer(self):
        msg = QMessageBox()
        msg.setWindowTitle("声明")
        msg.setText(self.disclaimer)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
        
        # 显示连接按钮
        self.connect_button.show()
    
    def show_model_selection(self):
        msg = QMessageBox()
        msg.setWindowTitle("选择模型")
        msg.setText("请选择要使用的模型：")
        msg.setIcon(QMessageBox.Icon.Question)
        
        # 添加模型选择按钮
        llama_button = msg.addButton("Llama3.2-1b", QMessageBox.ButtonRole.ActionRole)
        deepseek_button = msg.addButton("DeepSeek-1.5b", QMessageBox.ButtonRole.ActionRole)
        cancel_button = msg.addButton("取消", QMessageBox.ButtonRole.RejectRole)
        
        msg.exec()
        
        clicked_button = msg.clickedButton()
        if clicked_button == llama_button:
            self.model_name = self.available_models["Llama3.2-1b"]
            self.attempt_connection("Llama3.2-1b")
        elif clicked_button == deepseek_button:
            self.model_name = self.available_models["DeepSeek-1.5b"]
            self.attempt_connection("DeepSeek-1.5b")
    
    def attempt_connection(self, model_display_name):
        try:
            self.progress_label.setText(f"正在连接到{model_display_name}模型...")
            # 使用更短的超时时间
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model_name,
                    "prompt": "你好",
                    "stream": False
                },
                timeout=3  # 减少超时时间
            )
            if response.status_code == 200:
                self.ollama_connected = True
                self.apply_ollama_theme()
                
                # 更新模型选择器
                self.model_selector.clear()
                self.model_selector.addItems(list(self.available_models.keys()))
                self.model_selector.setCurrentText(model_display_name)
                self.model_selector.setEnabled(True)
                
                self.connect_button.setStyleSheet("""
                    QToolButton {
                        background-color: #1a73e8;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 5px 10px;
                        font-size: 12px;
                        min-width: 150px;
                    }
                    QToolButton:hover {
                        background-color: #1557b0;
                    }
                """)
                self.connect_button.setText(f"已连接 {model_display_name}")
                self.chat_display.clear()
                self.chat_display.append(self.format_message("System", f"🎉 成功连接到{model_display_name}模型！\n现在可以开始对话了。"))
            else:
                raise Exception("连接失败，服务器返回错误")
        except Exception as e:
            self.chat_display.append(self.format_message("System", f"❌ 连接失败：{str(e)}"))
            self.model_name = None
    
    def toggle_ollama_connection(self):
        if not self.ollama_connected:
            self.show_model_selection()
        else:
            self.ollama_connected = False
            self.model_name = None
            self.restore_original_theme()
            
            # 恢复模型选择器
            self.model_selector.clear()
            self.model_selector.addItems(["deepseek-coder-r1", "deepseek-coder-v3"])
            self.model_selector.setEnabled(False)
            
            self.connect_button.setStyleSheet("""
                QToolButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 10px;
                    font-size: 12px;
                    min-width: 150px;
                }
                QToolButton:hover {
                    background-color: #45a049;
                }
            """)
            self.connect_button.setText("连接真实AI(体验版)")
            self.chat_display.append(self.format_message("System", "已断开与模型的连接"))

    def apply_ollama_theme(self):
        self.setStyleSheet(self.ollama_style)

    def restore_original_theme(self):
        self.setStyleSheet(STYLE_SHEET)

    def send_message(self):
        if self.is_processing:
            QMessageBox.warning(self, "提示", "请等待当前响应完成")
            return
        
        message = self.input_field.text().strip()
        if not message:
            return
            
        try:
            self.is_processing = True
            self.input_field.setEnabled(False)
            self.input_field.clear()
            
            # 显示用户消息
            self.chat_display.append(self.format_message("You", message))
            
            # 如果已连接到Ollama，使用Ollama处理消息
            if self.ollama_connected:
                # 显示思考过程
                thinking_content = self.get_thinking_process(message)
                self.chat_display.append(self.thinking_template.format(content=thinking_content))
                
                # 创建并启动请求线程
                self.request_thread = RequestThread(self.ollama_url, self.model_name, message)
                self.request_thread.response_received.connect(self.handle_response)
                self.request_thread.response_complete.connect(self.handle_response_complete)
                self.request_thread.error_occurred.connect(self.handle_error)
                self.request_thread.start()
                return
            
            # 未连接Ollama时的本地响应逻辑
            self.message_count += 1
            
            # 检查是否需要显示声明
            if self.message_count == 3:
                self.show_disclaimer()
            
            # 检查特殊问题
            if "说真话你是谁" in message.lower():
                self.chat_display.append(self.format_message("Assistant", "Thinking..."))
                QTimer.singleShot(1500, lambda: self.show_truth_response())
                return
            
            # 关键词匹配
            response_type = "默认回复"
            for keyword, resp_type in KEYWORDS.items():
                if keyword in message.lower():
                    response_type = resp_type
                    break
            
            # 显示思考过程
            self.chat_display.append(self.format_message("Assistant", "Thinking..."))
            
            # 延迟显示响应
            QTimer.singleShot(1500, lambda: self.show_local_response(response_type))
            
        except Exception as e:
            logging.error(f"发送消息错误: {e}")
            self.handle_error(f"发送消息时发生错误：{str(e)}")
    
    def handle_response(self, response_text):
        """处理收到的响应"""
        self.chat_display.append(self.format_message("Assistant", response_text))
    
    def handle_response_complete(self):
        """响应完成后的清理"""
        self.is_processing = False
        self.input_field.setEnabled(True)
        self.input_field.setFocus()
    
    def handle_error(self, error_message):
        """处理错误"""
        self.chat_display.append(self.format_message("System", error_message))
        self.is_processing = False
        self.input_field.setEnabled(True)
        self.input_field.setFocus()

    def show_local_response(self, response_type):
        """显示本地响应"""
        try:
            response = random.choice(RESPONSES[response_type])
            self.chat_display.append(self.format_message("Assistant", response))
        finally:
            self.is_processing = False
            self.input_field.setEnabled(True)
            self.input_field.setFocus()
    
    def show_truth_response(self):
        """显示真实身份响应"""
        try:
            self.chat_display.append(self.format_message("Assistant", self.disclaimer))
            self.connect_button.show()
        finally:
            self.is_processing = False
            self.input_field.setEnabled(True)
            self.input_field.setFocus()

    def format_code_blocks(self, text):
        """处理代码块"""
        def replace_code_block(match):
            code = match.group(2)
            language = match.group(1) if match.group(1) else ""
            
            return f'''
                <div style="
                    background-color: #1a1a1a;
                    border-radius: 8px;
                    margin: 8px 0;
                    overflow: hidden;
                ">
                    <div style="
                        background-color: #2d2d2d;
                        padding: 8px 12px;
                        font-size: 12px;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        border-bottom: 1px solid #363636;
                    ">
                        <span>{language}</span>
                        <span style="opacity: 0.6;">复制</span>
                    </div>
                    <pre style="
                        margin: 0;
                        padding: 12px;
                        color: #e1e1e1;
                        font-family: monospace;
                        font-size: 13px;
                        line-height: 1.5;
                        overflow-x: auto;
                        background-color: #1a1a1a;
                    "><code>{code}</code></pre>
                </div>
            '''
        
        pattern = r'```(\w*)\n([\s\S]*?)```'
        return re.sub(pattern, replace_code_block, text)

    def format_markdown(self, text):
        """处理 Markdown 格式文本"""
        # 处理代码块
        text = self.format_code_blocks(text)
        
        # 处理行内代码
        text = re.sub(
            r'`([^`]+)`',
            r'<code style="background-color: rgba(0,0,0,0.3); padding: 2px 6px; border-radius: 4px; font-family: monospace;">\1</code>',
            text
        )
        
        # 处理列表
        text = re.sub(
            r'^\s*(\d+\.|\-|\*)\s+(.+)$',
            r'<div style="display: flex; padding: 2px 0;"><span style="opacity: 0.7; margin-right: 8px;">\1</span><span>\2</span></div>',
            text,
            flags=re.MULTILINE
        )
        
        return text

def main():
    # 设置高DPI支持
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    
    # 预加载Fusion样式
    app.setStyle("Fusion")
    
    # 设置应用程序信息
    app.setApplicationName("OpenWebUI")
    app.setApplicationVersion("1.0")
    
    # 创建并显示窗口
    window = ChatWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    # 设置环境变量以优化性能
    os.environ['QT_QUICK_CONTROLS_STYLE'] = 'Default'
    os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
    
    # 启动应用
    main() 