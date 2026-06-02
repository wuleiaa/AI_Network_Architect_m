def sigmoid(x):
    return 1 / (1 + 2.71828 ** (-x))


def sigmoid_derivative(y):
    return y * (1 - y)


# 初始化参数
W1 = 0.2
W2 = 0.3
b = 0.1

params_history = [
    {"轮数": 0, "W1": W1, "W2": W2, "b": b, "误差": None}
]

# 训练数据
X = [[0, 0], [0, 1], [1, 0], [1, 1]]
Y = [0, 0, 0, 1]

# 训练参数
learning_rate = 0.5
epochs = 1000

# 训练过程
for epoch in range(epochs):
    total_error = 0
    for i in range(4):
        x1, x2 = X[i]
        y_true = Y[i]

        # 前向传播
        z = x1 * W1 + x2 * W2 + b
        y_pred = sigmoid(z)

        # 计算误差
        error = y_true - y_pred
        total_error += error ** 2

        # 反向传播更新参数
        delta = error * sigmoid_derivative(y_pred)
        W1 += learning_rate * delta * x1
        W2 += learning_rate * delta * x2
        b += learning_rate * delta

    if (epoch + 1) % 100 == 0:
        avg_error = total_error / 4
        params_history.append({
            "轮数": epoch + 1,
            "W1": round(W1, 4),
            "W2": round(W2, 4),
            "b": round(b, 4),
            "误差": round(avg_error, 6)
        })

# 打印参数变化
print("===== 权重/偏置变化过程 =====")
for item in params_history:
    if item["误差"] is not None:
        print(f"轮数：{item['轮数']} | W1={item['W1']} | W2={item['W2']} | b={item['b']} | 平均误差={item['误差']}")
    else:
        print(f"轮数：{item['轮数']}（初始） | W1={item['W1']} | W2={item['W2']} | b={item['b']}")

# 测试模型
print("\n===== 测试结果 =====")
for i in range(4):
    x1, x2 = X[i]
    y_true = Y[i]
    z = x1 * W1 + x2 * W2 + b
    y_pred = sigmoid(z)
    y_pred_round = round(y_pred)
    print(f"输入({x1},{x2}) → 预测值={round(y_pred, 4)} → 四舍五入={y_pred_round} → 真实值={y_true}")

# 打印最终参数
print("\n===== 最终训练结果 =====")
print(f"最终权重W1：{round(W1, 4)}")
print(f"最终权重W2：{round(W2, 4)}")
print(f"最终偏置b：{round(b, 4)}")