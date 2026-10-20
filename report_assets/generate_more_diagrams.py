import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

os.makedirs("report_assets", exist_ok=True)
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Tahoma']
plt.rcParams['axes.unicode_minus'] = False

def create_act_diagram(filename, title, swimlanes, steps, connections):
    fig, ax = plt.subplots(figsize=(9, 6), dpi=200)
    ax.axis('off')
    n_lanes = len(swimlanes)
    lane_w = 1.0 / n_lanes
    for i, lane in enumerate(swimlanes):
        cx = (i + 0.5) * lane_w
        ax.text(cx, 0.96, lane, ha='center', va='center', fontsize=10.5, fontweight='bold', color="#1E3A8A")
        if i > 0:
            ax.plot([i * lane_w, i * lane_w], [0.05, 0.95], color="#CBD5E1", lw=1.2, ls="--")
            
    pos_map = {}
    for name, lane_idx, y, stype in steps:
        x = (lane_idx + 0.5) * lane_w
        pos_map[name] = (x, y)
        if stype == "start":
            circle = plt.Circle((x, y), 0.025, color="#10B981")
            ax.add_patch(circle)
        elif stype == "end":
            c1 = plt.Circle((x, y), 0.028, color="#EF4444", fill=False, lw=1.5)
            c2 = plt.Circle((x, y), 0.020, color="#EF4444")
            ax.add_patch(c1); ax.add_patch(c2)
        elif stype == "decision":
            diamond = patches.Polygon([[x, y+0.04], [x+0.08, y], [x, y-0.04], [x-0.08, y]], closed=True, ec="#D97706", fc="#FEF3C7", lw=1.2)
            ax.add_patch(diamond)
            ax.text(x, y, name, ha='center', va='center', fontsize=7.5, fontweight='bold', color="#92400E")
        else:
            box = patches.FancyBboxPatch((x-0.12, y-0.035), 0.24, 0.07, boxstyle="round,pad=0.015", ec="#0284C7", fc="#F0F9FF", lw=1.2)
            ax.add_patch(box)
            ax.text(x, y, name, ha='center', va='center', fontsize=8, fontweight='bold', color="#0F172A")
            
    for s, t, label in connections:
        sx, sy = pos_map[s]
        tx, ty = pos_map[t]
        ax.annotate("", xy=(tx, ty+0.035 if ty < sy else ty), xytext=(sx, sy-0.035 if ty < sy else sy),
                    arrowprops=dict(arrowstyle="->", color="#334155", lw=1.2))
        if label:
            mx, my = (sx + tx)/2, (sy + ty)/2
            ax.text(mx+0.02, my, label, fontsize=7.5, color="#D97706", fontweight='bold')
            
    ax.set_title(title, fontsize=11, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig(f"report_assets/{filename}")
    plt.close()

# Activity Login
create_act_diagram(
    "fig_4_1_act_login.png",
    "Biểu đồ hoạt động (Activity Diagram) - Chức năng Đăng nhập hệ thống",
    ["Người dùng (Client)", "Backend API (FastAPI)", "Cơ sở dữ liệu (MySQL)"],
    [
        ("Bắt đầu", 0, 0.90, "start"),
        ("Nhập Email & Mật khẩu", 0, 0.78, "action"),
        ("Gửi POST /auth/login", 0, 0.65, "action"),
        ("Xác thực & So khớp Bcrypt", 1, 0.65, "action"),
        ("Kiểm tra User & Active", 2, 0.52, "action"),
        ("Hợp lệ?", 1, 0.38, "decision"),
        ("Tạo JWT Access Token", 1, 0.25, "action"),
        ("Báo lỗi 401 Unauthorized", 1, 0.25, "action"),
        ("Lưu UserSession & Vào Dashboard", 0, 0.12, "action"),
        ("Kết thúc", 0, 0.02, "end")
    ],
    [
        ("Bắt đầu", "Nhập Email & Mật khẩu", ""),
        ("Nhập Email & Mật khẩu", "Gửi POST /auth/login", ""),
        ("Gửi POST /auth/login", "Xác thực & So khớp Bcrypt", ""),
        ("Xác thực & So khớp Bcrypt", "Kiểm tra User & Active", ""),
        ("Kiểm tra User & Active", "Hợp lệ?", ""),
        ("Hợp lệ?", "Tạo JWT Access Token", "Đúng"),
        ("Hợp lệ?", "Báo lỗi 401 Unauthorized", "Sai"),
        ("Tạo JWT Access Token", "Lưu UserSession & Vào Dashboard", ""),
        ("Lưu UserSession & Vào Dashboard", "Kết thúc", "")
    ]
)

# Activity Report
create_act_diagram(
    "fig_4_3_act_report.png",
    "Biểu đồ hoạt động (Activity Diagram) - Tạo và Xem Báo cáo Kinh doanh",
    ["Người dùng (Manager/Admin)", "Report Engine (Backend)", "Cơ sở dữ liệu"],
    [
        ("Bắt đầu", 0, 0.90, "start"),
        ("Chọn Kỳ (Tháng/Quý/Năm)", 0, 0.78, "action"),
        ("Bấm 'Tạo báo cáo'", 0, 0.65, "action"),
        ("Tính Summary & Tăng trưởng %", 1, 0.65, "action"),
        ("Top sản phẩm & Phân rã chi nhánh", 1, 0.52, "action"),
        ("Tính Moving Average dự báo", 1, 0.39, "action"),
        ("Lưu JSON kết quả vào bảng Reports", 2, 0.39, "action"),
        ("Render Dashboard & TableView", 0, 0.25, "action"),
        ("Kết thúc", 0, 0.12, "end")
    ],
    [
        ("Bắt đầu", "Chọn Kỳ (Tháng/Quý/Năm)", ""),
        ("Chọn Kỳ (Tháng/Quý/Năm)", "Bấm 'Tạo báo cáo'", ""),
        ("Bấm 'Tạo báo cáo'", "Tính Summary & Tăng trưởng %", ""),
        ("Tính Summary & Tăng trưởng %", "Top sản phẩm & Phân rã chi nhánh", ""),
        ("Top sản phẩm & Phân rã chi nhánh", "Tính Moving Average dự báo", ""),
        ("Tính Moving Average dự báo", "Lưu JSON kết quả vào bảng Reports", ""),
        ("Lưu JSON kết quả vào bảng Reports", "Render Dashboard & TableView", ""),
        ("Render Dashboard & TableView", "Kết thúc", "")
    ]
)

# Sequence Login
def create_seq_login():
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=200)
    ax.axis('off')
    lifelines = [("User (Desktop/App)", 0.15), ("LoginController", 0.40), ("FastAPI /auth/login", 0.65), ("MySQL Database", 0.88)]
    for name, x in lifelines:
        box = patches.FancyBboxPatch((x-0.10, 0.88), 0.20, 0.06, boxstyle="round,pad=0.01", ec="#1E3A8A", fc="#EFF6FF", lw=1.2)
        ax.add_patch(box)
        ax.text(x, 0.91, name, ha='center', va='center', fontsize=8.5, fontweight='bold', color="#1E3A8A")
        ax.plot([x, x], [0.08, 0.88], color="#CBD5E1", lw=1.2, ls="--")
    messages = [
        (0.15, 0.40, 0.78, "1: Điền email, password & Click Đăng nhập", False),
        (0.40, 0.65, 0.66, "2: POST /api/v1/auth/login (form-urlencoded)", False),
        (0.65, 0.88, 0.54, "3: SELECT * FROM users WHERE email = :email", False),
        (0.88, 0.65, 0.44, "4: Trả về User Entity & Hashed Password", True),
        (0.65, 0.65, 0.35, "5: So khớp bcrypt & Verify is_active", False),
        (0.65, 0.40, 0.25, "6: HTTP 200 OK + access_token (JWT)", True),
        (0.40, 0.15, 0.15, "7: Lưu UserSession, hiển thị Dashboard chính", True)
    ]
    for sx, tx, y, text, is_ret in messages:
        ls = "--" if is_ret else "-"
        col = "#047857" if is_ret else "#1E293B"
        if sx == tx:
            # Self call
            ax.annotate("", xy=(sx+0.08, y-0.04), xytext=(sx, y),
                        arrowprops=dict(arrowstyle="->", color=col, lw=1.2))
            ax.text(sx+0.09, y-0.02, text, fontsize=7.5, color=col)
        else:
            ax.annotate("", xy=(tx, y), xytext=(sx, y),
                        arrowprops=dict(arrowstyle="->", color=col, lw=1.2, ls=ls))
            ax.text((sx+tx)/2, y+0.015, text, ha='center', va='bottom', fontsize=7.5, color=col)
    ax.set_title("Biểu đồ tuần tự (Sequence Diagram) - Đăng nhập và Xác thực JWT Token", fontsize=11, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig("report_assets/fig_5_1_seq_login.png")
    plt.close()

create_seq_login()
print("Extended diagrams created!")
