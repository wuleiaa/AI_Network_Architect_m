import os
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

import streamlit as st

# ============================================================
# 常量集中管理
# ============================================================
MAX_HISTORY = 10
MODEL_NAME = "deepseek-chat"
DEFAULT_TEMPERATURE = 0.4


class MCU_TutorAI:
    def __init__(self):
        # --- 兼容云端 Secrets 和本地 .env ---
        try:
            api_key = st.secrets["AI_API_KEY"]
            base_url = st.secrets["AI_BASE_URL"]
        except (FileNotFoundError, KeyError):
            api_key = os.getenv("AI_API_KEY")
            base_url = os.getenv("AI_BASE_URL")

        if not api_key or not base_url:
            raise ValueError("环境变量 AI_API_KEY 或 AI_BASE_URL 未设置")
        if not base_url.rstrip("/").endswith("/v1"):
            raise ValueError(f"AI_BASE_URL 必须以 /v1 结尾，当前值: {base_url}")

        try:
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )
        except Exception as e:
            if "401" in str(e) or "authentication" in str(e).lower():
                raise RuntimeError("API 密钥无效或已过期，请检查 Secrets 中的 AI_API_KEY") from e
            elif "base_url" in str(e).lower() or "invalid url" in str(e).lower():
                raise RuntimeError(f"base_url 格式错误: {base_url}。必须为 https://api.deepseek.com/v1") from e
            else:
                raise RuntimeError(f"OpenAI 客户端初始化失败: {str(e)}") from e

    # ================================================================
    # S1: 单片机代码诊疗室
    # ================================================================
    def get_diagnostic_response(self, user_code, user_thought, topic):
        """
        苏格拉底式导师：分析学生的MCU代码和排查思路，引导而非直接给答案.
        """
        system_prompt = f"""
你是一位苏格拉底式的单片机/嵌入式系统导师。
当前实验主题：{topic}

【输入信息】：
1. 学生代码/配置片段：见用户输入
2. 学生对自己错误的预判：{user_thought}

【你的回复逻辑】：
1. 首先点评学生的"预判"是否准确。如果学生猜对了方向，给予肯定；
   如果猜错了，指出为什么那个方向不是问题的根源。
2. 然后分析代码中的实际错误。
3. 不要直接给代码！通过提问引导。例如：
   - "你注意到GPIO的模式配置了吗？推挽输出和开漏输出的区别是什么？"
   - "你检查过Timer的预分频系数和自动重装载值是否匹配吗？"
   - "中断服务函数中，你确认标志位被清除了吗？"
   - "串口的波特率计算公式是：波特率 = f_osc / (12 × (256 - TH1))，你验证过吗？"
4. 引导方向参考：
   - GPIO：模式（推挽/开漏）、上拉/下拉、时钟使能、引脚初始化
   - Timer：预分频器、自动重装载、计数模式、中断使能
   - UART/I2C/SPI：波特率、时序、设备地址、协议格式
   - ADC：参考电压、采样时间、校准、转换触发源
   - PWM：占空比、频率计算、输出通道配置
   - 中断：优先级、标志位清除、中断向量表、嵌套
5. 使用 Markdown 格式，语气亲切但专业。
6. 最后留下一句启发性的思考题。
        """

        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_code}
                ],
                stream=True,
                temperature=DEFAULT_TEMPERATURE
            )
            yield from response
        except Exception as e:
            # 修复：流式接口异常时应返回可迭代对象，而非字符串
            yield f"⚠️ AI 连接中断: {str(e)}"

    # ================================================================
    # S3: 单片机实验工场（原：自适应实验工场）
    # ================================================================
    def generate_personalized_task(self, learning_topic, mastery_level):
        """
        根据学习主题和掌握度，动态生成单片机实验任务。
        """
        task_prompt = f"""
我是一名《单片机原理与接口技术》课程的学生。
【今日学习重点】：{learning_topic}
【我的自评掌握度】：{mastery_level}

请为我设计一个通过 Keil C51 / STM32CubeIDE 完成的实战任务。

要求：
1. 如果掌握度是"刚入门"，任务要包含详细的步骤提示和关键寄存器配置说明。
2. 如果是"已熟练"，任务要包含 2-3 个隐蔽的故障陷阱（Troubleshooting）。
3. 如果是"已精通"，挑战综合性多外设协同任务。
4. 必须紧扣"{learning_topic}"这个主题。
5. 如果涉及硬件接线，需用文字描述连接方式。

输出结构：
### 🎯 今日挑战目标
### 📋 硬件连线说明（如涉及）
### 🔧 配置任务/编程任务
### 🐛 预埋故障/排错挑战
### ✅ 验收标准 (LED状态 / 串口输出 / 示波器波形)
        """

        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": task_prompt}],
                stream=True
            )
            yield from response
        except Exception as e:
            yield f"⚠️ 任务生成失败: {str(e)}"

    # ================================================================
    # S3: 参考答案生成（原：generate_task_solution）
    # ================================================================
    def generate_task_solution(self, task_content):
        """
        根据已生成的实验任务，提供标准参考代码。
        """
        solution_prompt = f"""
你是一位资深的单片机/嵌入式系统导师。请根据以下实验任务，提供标准的参考代码和原理讲解。

【任务内容回顾】：
{task_content}

【输出要求】：
1. 按模块列出 C 语言代码（C51 格式优先，也可给出 STM32 HAL 库格式）。
2. 使用 Markdown 代码块（```c）。
3. 注释解释关键配置的作用（如寄存器设置、时序关系）。
4. 给出 1-2 个核心验证方法的预期输出（如串口打印内容、LED 闪烁频率、波形描述）。
5. 格式清晰，代码可直接复制运行。
        """

        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": solution_prompt}],
                stream=True
            )
            yield from response
        except Exception as e:
            yield f"⚠️ 答案生成失败: {str(e)}"


    # ================================================================
    # S3: AI导师审阅学生提交（新增功能）
    # ================================================================
    # S3 AI tutor review student submission
    def review_student_submission(self, task_content, student_submission, conversation_history):
        """
        AI导师：审阅学生针对单片机实验任务提交的代码/方案，
        检查对错、给予纠正引导、支持多轮迭代，最后给出答案和结论。

        Args:
            task_content: 实验任务内容
            student_submission: 学生本次提交的代码/答案
            conversation_history: 此前多轮迭代的对话历史（列表），
                                  每项为 {"role": "student"/"tutor", "content": "..."}
        """
        is_first_submission = len(conversation_history) == 0
        history_context = ""
        history_lines = []
        if not is_first_submission:
            for msg in conversation_history:
                role_label = "学生" if msg["role"] == "student" else "AI导师"
                history_lines.append(f"{role_label}:\n{msg['content']}\n")
        combined_history = "".join(history_lines) if history_lines else ""
        context_note = ("【此前多轮迭代记录】：\n" + combined_history) if combined_history else ""

        system_prompt = f"""你是一位极其严谨且富有耐心的 **单片机/嵌入式系统 AI 导师**。你的工作是针对以下实验任务，审阅学生提交的代码/配置方案，并给出专业反馈。

【实验任务】：
{task_content}
{context_note}

【本次学生提交】：
{student_submission}

【审阅规则——请严格按照以下逻辑执行】：

### 第一阶段：检查与引导
1. **逐项检查**：对照实验任务的每个要求，逐一检查学生提交是否正确。
2. **定位错误**：明确指出代码/配置中具体的错误位置和原因。
3. **引导思考**：不要直接给出正确答案！通过提问引导学生自己发现问题。
4. **肯定正确部分**：对于学生做得对的地方，先给予肯定和鼓励。
5. **给出改进方向**：明确告诉学生应该从哪些方向修改。

### 第二阶段：迭代推进
- 如果学生是首次提交，给出初次反馈后，请明确说："**请根据以上反馈修改你的代码，修改后再次提交给我审阅。**"
- 如果学生已经过多轮迭代，请跟踪其改进情况，逐步减少提示，直到方案完全正确。

### 第三阶段：给出最终答案和结论
- 当学生提交的方案 **已经完全正确** 时，你必须：
  1. 明确宣布："**你的方案已完全正确！**"
  2. 对整个实验任务的要点进行总结
  3. 给出 **标准参考代码/答案**（用 ```c 代码块标注）
  4. 给出结论性评语和学习建议

- 当学生提交的方案 **仍有明显错误**，但学生主动要求看最终答案时，也要给出完整的标准参考代码和结论。

请使用 Markdown 排版，语气专业且亲切。
"""
        messages = [{"role": "system", "content": system_prompt}]
        response = self.client.chat.completions.create(model=MODEL_NAME, messages=messages, stream=True, temperature=DEFAULT_TEMPERATURE)
        yield from response
    # ================================================================
    # 模块三: 单片机原理深度追问
    # ================================================================
    def socratic_quiz(self, concept):
        """
        对单片机实验问题/故障进行苏格拉底式诊断引导, 而不是直接给答案.
        """
        prompt = f"""你是一位单片机实验导师，使用苏格拉底式教学法引导学生自己解决问题。

学生描述的实验问题："{concept}"

请遵循以下原则：

1. **不要直接给出答案或解决方案。** 永远不要直接告诉学生"你应该怎么做"。

2. **通过提问引导学生自己发现问题根源。** 每次回应提出2-3个有针对性的启发式问题，例如：
   - "你确认过对应GPIO端口的时钟使能寄存器已经开启了吗？"
   - "示波器量过这个引脚的波形吗？高低电平是否符合预期？"
   - "如果拿掉这个延时，现象会变化吗？为什么？"

3. **覆盖常见单片机实验故障排查方向：**
   - 硬件连接：接线是否正确？共地了吗？上拉/下拉电阻？
   - 时钟配置：对应外设时钟使能了吗？时钟源选择正确吗？
   - 初始化顺序：先配置GPIO再配置外设？中断优先级设置合理吗？
   - 寄存器操作：标志位清零了吗？数据手册相关章节确认过吗？
   - 软件逻辑：逻辑分析仪/串口打印确认过程状态了吗？

4. **语气亲切，鼓励学生动手验证。** 用"你试过..."、"不妨量一下..."等引导口吻。

5. 使用 **Markdown 排版**，让问题层次清晰。

6. 如果学生描述太模糊，先反问具体细节信息（开发板型号、接线图、代码片段、测量结果等）。
        """

        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )
            yield from response
        except Exception as e:
            yield f"⚠️ 连接异常: {str(e)}"


    # ================================================================
    # S2: 硬件仿真实验
    # ================================================================
    def generate_hardware_simulation(self, component, difficulty):
        """根据选定组件和难度生成 Proteus 硬件仿真实验方案."""
        sim_prompt = f"""You are a MCU hardware simulation tutor. Design a Proteus experiment.
Component: {component}
Difficulty: {difficulty}
Output: experiment objective, circuit diagram, C reference code, 
Proteus settings, expected results, troubleshooting tips.
Use Markdown format."""
        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{'role': 'user', 'content': sim_prompt}],
                stream=True
            )
            return response
        except Exception as e:
            yield f"Simulation plan generation failed: {str(e)}"

