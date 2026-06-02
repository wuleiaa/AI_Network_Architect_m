def sigmoid(x):
    return 1 / (1 + 2.71828 ** (-x))


def sigmoid_derivative(y):
    return y * (1 - y)


# 鍒濆鍖栧弬鏁?
W1 = 0.2
W2 = 0.3
b = 0.1

params_history = [
    {"杞暟": 0, "W1": W1, "W2": W2, "b": b, "璇樊": None}
]

# 璁粌鏁版嵁
X = [[0, 0], [0, 1], [1, 0], [1, 1]]
Y = [0, 0, 0, 1]

# 璁粌鍙傛暟
learning_rate = 0.5
epochs = 1000

# 璁粌杩囩▼
for epoch in range(epochs):
    total_error = 0
    for i in range(4):
        x1, x2 = X[i]
        y_true = Y[i]

        # 鍓嶅悜浼犳挱
        z = x1 * W1 + x2 * W2 + b
        y_pred = sigmoid(z)

        # 璁＄畻璇樊
        error = y_true - y_pred
        total_error += error ** 2

        # 鍙嶅悜浼犳挱鏇存柊鍙傛暟
        delta = error * sigmoid_derivative(y_pred)
        W1 += learning_rate * delta * x1
        W2 += learning_rate * delta * x2
        b += learning_rate * delta

    if (epoch + 1) % 100 == 0:
        avg_error = total_error / 4
        params_history.append({
            "杞暟": epoch + 1,
            "W1": round(W1, 4),
            "W2": round(W2, 4),
            "b": round(b, 4),
            "璇樊": round(avg_error, 6)
        })

# 鎵撳嵃鍙傛暟鍙樺寲
print("===== 鏉冮噸/鍋忕疆鍙樺寲杩囩▼ =====")
for item in params_history:
    if item["璇樊"] is not None:
        print(f"杞暟锛歿item['杞暟']} | W1={item['W1']} | W2={item['W2']} | b={item['b']} | 骞冲潎璇樊={item['璇樊']}")
    else:
        print(f"杞暟锛歿item['杞暟']}锛堝垵濮嬶級 | W1={item['W1']} | W2={item['W2']} | b={item['b']}")

# 娴嬭瘯妯″瀷
print("\n===== 娴嬭瘯缁撴灉 =====")
for i in range(4):
    x1, x2 = X[i]
    y_true = Y[i]
    z = x1 * W1 + x2 * W2 + b
    y_pred = sigmoid(z)
    y_pred_round = round(y_pred)
    print(f"杈撳叆({x1},{x2}) 鈫?棰勬祴鍊?{round(y_pred, 4)} 鈫?鍥涜垗浜斿叆={y_pred_round} 鈫?鐪熷疄鍊?{y_true}")

# 鎵撳嵃鏈€缁堝弬鏁?
print("\n===== 鏈€缁堣缁冪粨鏋?=====")
print(f"鏈€缁堟潈閲峎1锛歿round(W1, 4)}")
print(f"鏈€缁堟潈閲峎2锛歿round(W2, 4)}")
print(f"鏈€缁堝亸缃産锛歿round(b, 4)}")