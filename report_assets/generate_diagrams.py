import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

os.makedirs("report_assets", exist_ok=True)
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Tahoma']
plt.rcParams['axes.unicode_minus'] = False

def draw_partners():
    fig, ax = plt.subplots(figsize=(8, 2.5), dpi=200)
    ax.axis('off')
    partners = [("ABB", "#E0001B"), ("Bumhan", "#004B87"), ("UAC Aerospace", "#005DAA"), ("EVN", "#D62828"), ("Makitech", "#1D3557")]
    for i, (name, col) in enumerate(partners):
        box = patches.FancyBboxPatch((0.05 + i*0.19, 0.25), 0.15, 0.5, boxstyle="round,pad=0.03", ec="#CBD5E1", fc="#F8FAFC", lw=1.5)
        ax.add_patch(box)
        ax.text(0.125 + i*0.19, 0.5, name, ha='center', va='center', fontsize=12, fontweight='bold', color=col)
    ax.set_title("Đối tác tiêu biểu của Công ty TNHH Tự Động Hóa Nhật Tri", fontsize=11, pad=10, color="#334155")
    plt.tight_layout()
    plt.savefig("report_assets/fig_1_1_partners.png")
    plt.close()

def draw_projects():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 4), dpi=200)
    for ax, title, desc, col in [(ax1, "Dự án Cải tạo máy quấn dây", "Nâng cao hiệu quả sản xuất\nNhà máy Relats Việt Nam", "#1E3A8A"),
                                  (ax2, "Tủ điều khiển xử lý nước thải", "Giám sát thông minh qua Internet\nNhà máy Toyota Trang Lê", "#047857")]:
        ax.axis('off')
        box = patches.FancyBboxPatch((0.05, 0.05), 0.9, 0.9, boxstyle="round,pad=0.04", ec=col, fc="#F0FDF4" if "nước" in title else "#EFF6FF", lw=2)
        ax.add_patch(box)
        ax.text(0.5, 0.65, title, ha='center', va='center', fontsize=12, fontweight='bold', color=col)
        ax.text(0.5, 0.35, desc, ha='center', va='center', fontsize=10, color="#475569")
    plt.tight_layout()
    plt.savefig("report_assets/fig_1_2_projects.png")
    plt.close()

def draw_prediction_chart():
    np.random.seed(42)
    days = 90
    x = np.linspace(1, days, days)
    x_norm = x / days
    # True trend (degree 4 poly)
    trend = 15000000 + 8000000*x_norm - 25000000*(x_norm**2) + 40000000*(x_norm**3) - 18000000*(x_norm**4)
    noise = np.random.normal(0, 1200000, days)
    actual = trend + noise
    
    # Introduce 3 artificial outliers
    actual[25] += 5000000  # spike
    actual[55] -= 5500000  # sudden drop
    actual[78] += 4800000  # spike
    
    poly_coefs = np.polyfit(x_norm, actual, 4)
    pred = np.polyval(poly_coefs, x_norm)
    std = np.std(actual - pred)
    upper = pred + 2 * std
    lower = np.maximum(0, pred - 2 * std)
    
    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=200)
    ax.plot(x, actual / 1e6, label='Doanh thu thực tế (Actual)', color='#10B981', lw=1.5, marker='o', markersize=3, alpha=0.8)
    ax.plot(x, pred / 1e6, label='Đường xu hướng (Poly Degree 4)', color='#0284C7', lw=2.5)
    ax.plot(x, upper / 1e6, label='Cận trên (+2σ, Dải tin cậy 95%)', color='#94A3B8', ls='--', lw=1.5)
    ax.plot(x, lower / 1e6, label='Cận dưới (-2σ, Dải tin cậy 95%)', color='#94A3B8', ls='--', lw=1.5)
    ax.fill_between(x, lower / 1e6, upper / 1e6, color='#E2E8F0', alpha=0.4)
    
    # Highlight outliers
    outliers = (actual > upper) | (actual < lower)
    ax.scatter(x[outliers], actual[outliers] / 1e6, color='#EF4444', s=80, zorder=5, label='Ngoại lai bất thường (Outlier)')
    for ox, oy in zip(x[outliers], actual[outliers] / 1e6):
        ax.annotate(f'Ngày {int(ox)}: {oy:.1f}M', (ox, oy), textcoords="offset points", xytext=(0,10), ha='center', fontsize=8, fontweight='bold', color='#B91C1C')
        
    ax.set_title("Mô hình Hồi quy Đa thức Bậc 4 & Phát hiện Ngoại lai Doanh thu (90 ngày)", fontsize=12, fontweight='bold', pad=12, color="#1E293B")
    ax.set_xlabel("Thời gian (Ngày trong kỳ quan sát)", fontsize=10, labelpad=6)
    ax.set_ylabel("Doanh thu (Triệu VNĐ)", fontsize=10, labelpad=6)
    ax.legend(loc='upper left', frameon=True, fontsize=9)
    ax.grid(True, ls=':', color='#CBD5E1', alpha=0.7)
    plt.tight_layout()
    plt.savefig("report_assets/fig_2_3_prediction_math.png")
    plt.close()

draw_partners()
draw_projects()
draw_prediction_chart()
print("Base diagrams created successfully!")
