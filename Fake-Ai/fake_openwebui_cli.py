import sys
import time
import random
import requests
import os
import json
import argparse
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from fake_openwebui_gui import ChatWindow, RESPONSES, KEYWORDS
import logging

def typing_print(text, delay=0.03):
    """打字机效果输出"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

class ChatCLI:
    def __init__(self):
        self.responses = RESPONSES
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "deepseek-coder-r1"
        self.is_processing = False  # 添加处理状态标志
        
    def format_thinking_process(self, prompt):
        """格式化思考过程输出"""
        thinking = (
            "\n↓ 思考过程\n"
            f"• 分析输入: \"{prompt}\"\n"
            "• 处理问题\n"
            "• 生成回复\n"
            "• 格式化输出\n"
        )
        return thinking
        
    def display_response(self, prompt, response_text):
        """显示完整的响应，包括思考过程"""
        # 1. 显示思考过程
        thinking = self.format_thinking_process(prompt)
        typing_print(thinking)
        
        # 2. 显示响应（一次性显示完整响应）
        print("Assistant: ", end='')
        print(response_text)  # 直接打印，不使用打字机效果
        print()
        
    def handle_user_input(self, user_input):
        """处理用户输入"""
        if not user_input.strip():
            return True
            
        if user_input.lower() == 'exit':
            typing_print("正在关闭连接...")
            time.sleep(1)
            return False
            
        # 如果正在处理上一个请求，则忽略新请求
        if self.is_processing:
            print("请等待上一个响应完成...")
            return True
            
        try:
            self.is_processing = True  # 设置处理标志
            
            # 关键词匹配
            response_type = "默认回复"
            for keyword, resp_type in KEYWORDS.items():
                if keyword in user_input.lower():
                    response_type = resp_type
                    break
            
            # 生成响应
            response = random.choice(self.responses[response_type]).strip()
            
            # 显示响应
            self.display_response(user_input, response)
            
        finally:
            self.is_processing = False  # 重置处理标志
            
        return True
        
    def run_cli(self):
        """运行命令行界面"""
        # 清屏
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # 连接过程
        typing_print("正在连接服务器...")
        time.sleep(2)
        typing_print("连接成功！")
        print("\n")
        
        # 模型选择
        typing_print("可用模型:")
        print("1. deepseek-coder-r1")
        print("2. deepseek-coder-v3")
        
        while True:
            model_choice = input("\n请选择模型 (输入数字1或2): ")
            if model_choice in ['1', '2']:
                self.model_name = "deepseek-coder-r1" if model_choice == '1' else "deepseek-coder-v3"
                typing_print(f"\n已选择模型: {self.model_name}")
                break
            else:
                typing_print("无效选择，请重试")
        
        print("\n现在可以开始对话了！输入 'exit' 退出程序\n")
        
        # 对话循环
        try:
            while True:
                user_input = input("You: ")
                if not self.handle_user_input(user_input):
                    break
        except KeyboardInterrupt:
            print("\n\n正在退出程序...")
        except Exception as e:
            logging.error(f"Error: {e}")
            print("\n发生错误，请重试")

def main():
    parser = argparse.ArgumentParser(description='DeepSeek Chat Interface')
    parser.add_argument('--cli', action='store_true', help='使用命令行界面')
    args = parser.parse_args()
    
    try:
        if args.cli:
            chat_cli = ChatCLI()
            chat_cli.run_cli()
        else:
            if hasattr(Qt, 'AA_EnableHighDpiScaling'):
                QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
            if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
                QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
            
            app = QApplication(sys.argv)
            app.setStyle("Fusion")
            app.setApplicationName("OpenWebUI")
            app.setApplicationVersion("1.0")
            
            window = ChatWindow()
            window.show()
            sys.exit(app.exec())
    except Exception as e:
        logging.error(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # 设置环境变量
    os.environ['QT_QUICK_CONTROLS_STYLE'] = 'Default'
    os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    main()