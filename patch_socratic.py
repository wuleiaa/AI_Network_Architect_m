import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

filepath = r"F:\porj_AI_NetWork_Project\AI_Network_Architect\AI_NetWork_Project\utils\ai_engine.py"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

old_method = """    def socratic_quiz(self, concept):
        \"\"\"
        对单片机概念进行通俗比喻解释 + 抛出深度思考题.
        \"\"\"
        prompt = f\"\"\"
对\"{concept}\"这个单片机/嵌入式概念，请做两件事：

    1. 用最通俗易懂的生活比喻解释它是什么（就像用\"水龙头开关\"解释\"GPIO高低电平控制\"那样）。
   比喻要贴切到位的，能让人秒懂。

2. 然后向我抛出2-3个有深度的思考题，测试我是否真正理解了，例如：
   - 在场景X下，如果Y发生了会怎样？
   - 为什么Z不是最优方案？
   - 你如何用这个知识优化某段代码？
   
请用 Markdown 排版。
        \"\"\"

        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{\"role\": \"user\", \"content\": prompt}],
                stream=True
            )
            yield from response
        except Exception as e:
            yield f\"\u26a0\ufe0f 连接异常: {str(e)}\""""

new_method = """    def socratic_quiz(self, concept):
        \"\"\"
        对单片机实验问题/故障进行苏格拉底式诊断引导, 而不是直接给答案.
        \"\"\"
        prompt = f\"\"\"你是一位单片机实验导师，使用苏格拉底式教学法引导学生自己解决问题。

学生描述的实验问题："{concept}"

请遵循以下原则：

1. **不要直接给出答案或解决方案。** 永远不要直接告诉学生\"你应该怎么做\"。

2. **通过提问引导学生自己发现问题根源。** 每次回应提出2-3个有针对性的启发式问题，例如：
   - \"你确认过对应GPIO端口的时钟使能寄存器已经开启了吗？\"
   - \"示波器量过这个引脚的波形吗？高低电平是否符合预期？\"
   - \"如果拿掉这个延时，现象会变化吗？为什么？\"

3. **覆盖常见单片机实验故障排查方向：**
   - 硬件连接：接线是否正确？共地了吗？上拉/下拉电阻？
   - 时钟配置：对应外设时钟使能了吗？时钟源选择正确吗？
   - 初始化顺序：先配置GPIO再配置外设？中断优先级设置合理吗？
   - 寄存器操作：标志位清零了吗？数据手册相关章节确认过吗？
   - 软件逻辑：逻辑分析仪/串口打印确认过程状态了吗？

4. **语气亲切，鼓励学生动手验证。** 用"你试过..."、"不妨量一下..."等引导口吻。

5. 使用 **Markdown 排版**，让问题层次清晰。

6. 如果学生描述太模糊，先反问具体细节信息（开发板型号、接线图、代码片段、测量结果等）。
        \"\"\"

        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{\"role\": \"user\", \"content\": prompt}],
                stream=True
            )
            yield from response
        except Exception as e:
            yield f\"\u26a0\ufe0f 连接异常: {str(e)}\""""

if old_method in content:
    content = content.replace(old_method, new_method)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print("socratic_quiz method updated successfully!")
else:
    print("ERROR: Could not find the old method exactly. Trying to locate...")
    if "def socratic_quiz" in content:
        print("Method found but exact text differs.")
        idx = content.find("def socratic_quiz")
        print(repr(content[idx:idx+500]))
    else:
        print("Method not found at all!")
