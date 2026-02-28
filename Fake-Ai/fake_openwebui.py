import time
import sys
import os

def typing_print(text, delay=0.03):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def main():
    # 清空控制台
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # 连接服务器阶段
    typing_print("正在连接服务器...")
    time.sleep(4)
    typing_print("连接成功！")
    print("\n")
    
    # 选择模型阶段
    typing_print("可用模型:")
    print("1. deepseek-coder-r1")
    print("2. deepseek-coder-v3")
    
    while True:
        model_choice = input("\n请选择模型 (输入数字1或2): ")
        if model_choice in ['1', '2']:
            selected_model = "deepseek-coder-r1" if model_choice == '1' else "deepseek-coder-v3"
            typing_print(f"\n已选择模型: {selected_model}")
            break
        else:
            typing_print("无效选择，请重试")
    
    print("\n现在可以开始对话了！输入 'exit' 退出程序\n")
    
    # 对话循环
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            typing_print("正在关闭连接...")
            time.sleep(1)
            break
            
        print("\nAssistant: Thinking......")
        time.sleep(4)
        typing_print("抱歉，服务器当前负载过高，请稍后重试。", delay=0.05)
        print()

if __name__ == "__main__":
    main() 