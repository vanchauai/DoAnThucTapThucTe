import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

os.makedirs("report_assets", exist_ok=True)
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Tahoma']
plt.rcParams['axes.unicode_minus'] = False

def create_use_case():
    fig, ax = plt.subplots(figsize=(10, 8), dpi=200)
    ax.axis('off')
    
    # Actors
    actors = [
        ("Admin\n(Quản trị viên)", 0.08, 0.75, "#DC2626"),
        ("Manager\n(Quản lý)", 0.08, 0.45, "#2563EB"),
        ("Employee\n(Nhân viên)", 0.08, 0.15, "#16A34A")
    ]
    for name, x, y, col in actors:
        circle = plt.Circle((x, y+0.05), 0.03, color=col, fill=True)
        ax.add_patch(circle)
        ax.plot([x, x], [y+0.02, y-0.03], color=col, lw=2)
        ax.plot([x-0.02, x+0.02], [y, y], color=col, lw=2)
        ax.plot([x, x-0.02], [y-0.03, y-0.06], color=col, lw=2)
        ax.plot([x, x+0.02], [y-0.03, y-0.06], color=col, lw=2)
        ax.text(x, y-0.08, name, ha='center', va='top', fontsize=9, fontweight='bold', color=col)
        
    # Boundary box
    sys_box = patches.FancyBboxPatch((0.24, 0.05), 0.72, 0.90, boxstyle="round,pad=0.02", ec="#64748B", fc="#F8FAFC", lw=1.5)
    ax.add_patch(sys_box)
    ax.text(0.60, 0.92, "HỆ THỐNG DATA SYNC & AUTOMATED REPORTING", ha='center', va='center', fontsize=11, fontweight='bold', color="#1E293B")
    
    # Use cases
    use_cases = [
        ("Đăng nhập & Đổi mật khẩu", 0.60, 0.85, [0, 1, 2]),
        ("Quản lý tài khoản người dùng", 0.43, 0.76, [0]),
        ("Cấu hình Scheduler tự động", 0.77, 0.76, [0]),
        ("Quản lý & Tải lên Data Sources", 0.43, 0.63, [0, 1]),
        ("Đồng bộ & Kiểm tra toàn vẹn", 0.77, 0.63, [0, 1]),
        ("Phát hiện ngoại lai (Z-Score)", 0.77, 0.52, [0, 1]),
        ("Xem Dashboard tổng quan", 0.43, 0.40, [0, 1, 2]),
        ("Tạo & Quản lý Báo cáo đa kỳ", 0.77, 0.40, [0, 1]),
        ("Dự báo xu hướng (Hồi quy bậc 4)", 0.43, 0.26, [0, 1]),
        ("Truy vấn Trợ lý dữ liệu ảo", 0.77, 0.26, [0, 1, 2]),
        ("Nhận Email báo cáo & Cảnh báo", 0.60, 0.12, [0, 1])
    ]
    
    for text, cx, cy, linked_actors in use_cases:
        ellipse = patches.Ellipse((cx, cy), 0.28, 0.065, ec="#0284C7", fc="#E0F2FE", lw=1.2)
        ax.add_patch(ellipse)
        ax.text(cx, cy, text, ha='center', va='center', fontsize=8.5, fontweight='bold', color="#0369A1")
        
        for a_idx in linked_actors:
            ax_x, ax_y = actors[a_idx][1], actors[a_idx][2]
            ax.annotate("", xy=(cx - 0.13, cy), xytext=(ax_x + 0.04, ax_y),
                        arrowprops=dict(arrowstyle="-", color="#94A3B8", lw=0.8))
                        
    plt.tight_layout()
    plt.savefig("report_assets/fig_3_usecase.png")
    plt.close()

def create_activity_sync():
    fig, ax = plt.subplots(figsize=(9, 6.5), dpi=200)
    ax.axis('off')
    
    # Swimlanes
    ax.plot([0.33, 0.33], [0.05, 0.95], color="#CBD5E1", lw=1.5, ls="--")
    ax.plot([0.66, 0.66], [0.05, 0.95], color="#CBD5E1", lw=1.5, ls="--")
    ax.text(0.165, 0.96, "Người dùng (User)", ha='center', va='center', fontsize=11, fontweight='bold', color="#1E3A8A")
    ax.text(0.495, 0.96, "FastAPI Backend (ETL & Validation)", ha='center', va='center', fontsize=11, fontweight='bold', color="#047857")
    ax.text(0.825, 0.96, "Cơ sở dữ liệu (MySQL)", ha='center', va='center', fontsize=11, fontweight='bold', color="#B45309")
    
    steps = [
        ("Bắt đầu", 0.165, 0.90, "start"),
        ("Tải file Excel / Chọn GSheets", 0.165, 0.81, "action"),
        ("Bấm 'Đồng bộ ngay'", 0.165, 0.70, "action"),
        ("Đọc file & Ánh xạ cột (Alias Mapping)", 0.495, 0.70, "action"),
        ("Kiểm tra hợp lệ dòng & kiểu dữ liệu", 0.495, 0.58, "action"),
        ("Cross-file & Outlier Check (Z-Score)", 0.495, 0.46, "action"),
        ("Lưu NormalizedOrders vào DB", 0.825, 0.46, "action"),
        ("Cập nhật DataSource (synced/error)", 0.825, 0.34, "action"),
        ("Trả kết quả & danh sách cảnh báo", 0.495, 0.34, "action"),
        ("Hiển thị thông báo & Outliers trên UI", 0.165, 0.22, "action"),
        ("Kết thúc", 0.165, 0.11, "end")
    ]
    
    pos_map = {}
    for name, x, y, stype in steps:
        pos_map[name] = (x, y)
        if stype == "start":
            circle = plt.Circle((x, y), 0.025, color="#10B981")
            ax.add_patch(circle)
        elif stype == "end":
            circle1 = plt.Circle((x, y), 0.028, color="#EF4444", fill=False, lw=1.5)
            circle2 = plt.Circle((x, y), 0.020, color="#EF4444")
            ax.add_patch(circle1)
            ax.add_patch(circle2)
        else:
            box = patches.FancyBboxPatch((x-0.13, y-0.035), 0.26, 0.07, boxstyle="round,pad=0.015", ec="#0284C7", fc="#F0F9FF", lw=1.2)
            ax.add_patch(box)
            ax.text(x, y, name, ha='center', va='center', fontsize=8.5, fontweight='bold', color="#0F172A")
            
    # Connectors
    arrows = [
        ("Bắt đầu", "Tải file Excel / Chọn GSheets"),
        ("Tải file Excel / Chọn GSheets", "Bấm 'Đồng bộ ngay'"),
        ("Bấm 'Đồng bộ ngay'", "Đọc file & Ánh xạ cột (Alias Mapping)"),
        ("Đọc file & Ánh xạ cột (Alias Mapping)", "Kiểm tra hợp lệ dòng & kiểu dữ liệu"),
        ("Kiểm tra hợp lệ dòng & kiểu dữ liệu", "Cross-file & Outlier Check (Z-Score)"),
        ("Cross-file & Outlier Check (Z-Score)", "Lưu NormalizedOrders vào DB"),
        ("Lưu NormalizedOrders vào DB", "Cập nhật DataSource (synced/error)"),
        ("Cập nhật DataSource (synced/error)", "Trả kết quả & danh sách cảnh báo"),
        ("Trả kết quả & danh sách cảnh báo", "Hiển thị thông báo & Outliers trên UI"),
        ("Hiển thị thông báo & Outliers trên UI", "Kết thúc")
    ]
    for s, t in arrows:
        sx, sy = pos_map[s]
        tx, ty = pos_map[t]
        ax.annotate("", xy=(tx, ty+0.035 if ty < sy else ty), xytext=(sx, sy-0.035 if ty < sy else sy),
                    arrowprops=dict(arrowstyle="->", color="#334155", lw=1.2))
                    
    ax.set_title("Biểu đồ hoạt động (Activity Diagram) - Quy trình Đồng bộ Dữ liệu ETL", fontsize=11, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig("report_assets/fig_4_2_act_sync.png")
    plt.close()

def create_sequence_sync():
    fig, ax = plt.subplots(figsize=(9.5, 6.5), dpi=200)
    ax.axis('off')
    
    lifelines = [
        ("User (UI)", 0.12),
        ("DataSourceController", 0.32),
        ("FastAPI Router", 0.52),
        ("ETL & Validation Service", 0.72),
        ("MySQL Database", 0.90)
    ]
    for name, x in lifelines:
        box = patches.FancyBboxPatch((x-0.08, 0.88), 0.16, 0.06, boxstyle="round,pad=0.01", ec="#1E3A8A", fc="#EFF6FF", lw=1.2)
        ax.add_patch(box)
        ax.text(x, 0.91, name, ha='center', va='center', fontsize=8.5, fontweight='bold', color="#1E3A8A")
        ax.plot([x, x], [0.08, 0.88], color="#CBD5E1", lw=1.2, ls="--")
        
    messages = [
        (0.12, 0.32, 0.82, "1: Click 'Đồng bộ ngay'", False),
        (0.32, 0.52, 0.74, "2: POST /api/v1/data-sources/{id}/sync", False),
        (0.52, 0.72, 0.66, "3: execute_sync(source_id)", False),
        (0.72, 0.90, 0.58, "4: Query history orders (check duplicate & Z-score)", False),
        (0.90, 0.72, 0.50, "5: Return historical stats", True),
        (0.72, 0.90, 0.42, "6: Bulk insert NormalizedOrders & update DataSource", False),
        (0.90, 0.72, 0.34, "7: Commit OK", True),
        (0.72, 0.52, 0.26, "8: Return sync summary & warnings", True),
        (0.52, 0.32, 0.18, "9: HTTP 200 OK (SyncResponse JSON)", True),
        (0.32, 0.12, 0.10, "10: Render table status & show Outlier alert dialog", True)
    ]
    for sx, tx, y, text, is_ret in messages:
        ls = "--" if is_ret else "-"
        col = "#047857" if is_ret else "#1E293B"
        ax.annotate("", xy=(tx, y), xytext=(sx, y),
                    arrowprops=dict(arrowstyle="->", color=col, lw=1.2, ls=ls))
        mid_x = (sx + tx) / 2
        ax.text(mid_x, y+0.015, text, ha='center', va='bottom', fontsize=7.5, color=col, fontweight='bold' if not is_ret else 'normal')
        
    ax.set_title("Biểu đồ tuần tự (Sequence Diagram) - Kích hoạt Đồng bộ hóa và Xử lý ETL", fontsize=11, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig("report_assets/fig_5_2_seq_sync.png")
    plt.close()

def create_class_diagram():
    fig, ax = plt.subplots(figsize=(10, 7), dpi=200)
    ax.axis('off')
    
    classes = [
        ("User", 0.18, 0.75, ["+ id: Integer", "+ email: String", "+ hashed_password: String", "+ full_name: String", "+ role: String", "+ is_active: Boolean", "+ created_at: DateTime"], "#EFF6FF", "#1E40AF"),
        ("DataSource", 0.52, 0.75, ["+ id: Integer", "+ name: String", "+ source_type: String", "+ config: JSON", "+ column_mapping: JSON", "+ status: String", "+ last_synced_at: DateTime"], "#F0FDF4", "#166534"),
        ("NormalizedOrder", 0.84, 0.75, ["+ id: Integer", "+ order_id: String (UK)", "+ order_date: Date", "+ product_name: String", "+ quantity: Float", "+ unit_price: Float", "+ total_amount: Float", "+ source_sheet: String"], "#FEF3C7", "#92400E"),
        ("Report", 0.18, 0.30, ["+ id: Integer", "+ report_name: String", "+ period_type: String", "+ period_value: String", "+ created_by: Integer", "+ data: JSON", "+ created_at: DateTime"], "#F5F3FF", "#5B21B6"),
        ("AlertHistory", 0.52, 0.30, ["+ id: Integer", "+ alert_type: String", "+ alert_date: Date", "+ created_at: DateTime"], "#FFF1F2", "#9F1239"),
        ("AuditLog", 0.84, 0.30, ["+ id: Integer", "+ user_id: Integer", "+ action: String", "+ detail: String", "+ created_at: DateTime"], "#F8FAFC", "#334155")
    ]
    
    for name, cx, cy, fields, bg, border in classes:
        w, h = 0.26, 0.28
        box = patches.FancyBboxPatch((cx-w/2, cy-h/2), w, h, boxstyle="round,pad=0.01", ec=border, fc=bg, lw=1.5)
        ax.add_patch(box)
        ax.text(cx, cy+h/2-0.03, f"<<Entity>>\n{name}", ha='center', va='top', fontsize=9.5, fontweight='bold', color=border)
        ax.plot([cx-w/2, cx+w/2], [cy+h/2-0.07, cy+h/2-0.07], color=border, lw=1)
        for i, f in enumerate(fields):
            ax.text(cx-w/2+0.015, cy+h/2-0.09-i*0.03, f, ha='left', va='top', fontsize=7.5, color="#1E293B")
            
    # Relationships
    ax.annotate("", xy=(0.18, 0.46), xytext=(0.18, 0.60), arrowprops=dict(arrowstyle="->", color="#475569", lw=1.2))
    ax.text(0.20, 0.53, "1 : N (creates)", fontsize=8, color="#475569")
    
    ax.annotate("", xy=(0.70, 0.75), xytext=(0.66, 0.75), arrowprops=dict(arrowstyle="->", color="#475569", lw=1.2))
    ax.text(0.68, 0.77, "1 : N", fontsize=8, color="#475569")

    ax.set_title("Biểu đồ Lớp Thực thể Cốt lõi (Class Diagram / Domain Model)", fontsize=11, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig("report_assets/fig_6_class_diagram.png")
    plt.close()

def create_database_erd():
    fig, ax = plt.subplots(figsize=(10, 7), dpi=200)
    ax.axis('off')
    
    tables = [
        ("users", 0.18, 0.75, ["id (PK, INT)", "email (VARCHAR 255, UK)", "hashed_password (VARCHAR)", "full_name (VARCHAR 255)", "role (VARCHAR 50)", "is_active (BOOLEAN)", "created_at (DATETIME)"]),
        ("data_sources", 0.52, 0.75, ["id (PK, INT)", "name (VARCHAR 255)", "source_type (VARCHAR 50)", "config (JSON)", "column_mapping (JSON)", "status (VARCHAR 50)", "last_synced_at (DATETIME)"]),
        ("normalized_orders", 0.84, 0.75, ["id (PK, INT)", "order_id (VARCHAR 100, UK)", "order_date (DATE)", "product_name (VARCHAR 255)", "quantity (FLOAT)", "unit_price (FLOAT)", "total_amount (FLOAT)", "source_sheet (VARCHAR 255)"]),
        ("reports", 0.18, 0.28, ["id (PK, INT)", "report_name (VARCHAR 255)", "period_type (VARCHAR 50)", "period_value (VARCHAR 100)", "created_by (FK, INT)", "data (JSON)", "created_at (DATETIME)"]),
        ("alert_history", 0.52, 0.28, ["id (PK, INT)", "alert_type (VARCHAR 50)", "alert_date (DATE)", "created_at (DATETIME)"]),
        ("audit_logs", 0.84, 0.28, ["id (PK, INT)", "user_id (FK, INT)", "action (VARCHAR 50)", "detail (VARCHAR 255)", "created_at (DATETIME)"])
    ]
    for name, cx, cy, cols in tables:
        w, h = 0.26, 0.32
        box = patches.FancyBboxPatch((cx-w/2, cy-h/2), w, h, boxstyle="square,pad=0.0", ec="#0284C7", fc="#FFFFFF", lw=1.5)
        ax.add_patch(box)
        head_box = patches.Rectangle((cx-w/2, cy+h/2-0.06), w, 0.06, ec="#0284C7", fc="#0284C7")
        ax.add_patch(head_box)
        ax.text(cx, cy+h/2-0.03, f"TABLE: {name}", ha='center', va='center', fontsize=9, fontweight='bold', color="#FFFFFF")
        for i, c in enumerate(cols):
            ax.text(cx-w/2+0.015, cy+h/2-0.09-i*0.032, c, ha='left', va='top', fontsize=7.5, color="#0F172A")
            
    # Foreign key links
    ax.annotate("", xy=(0.18, 0.44), xytext=(0.18, 0.58), arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.2, ls="--"))
    ax.text(0.20, 0.51, "FK: created_by", fontsize=7.5, color="#DC2626")

    ax.annotate("", xy=(0.84, 0.44), xytext=(0.18, 0.60), arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.2, ls="--", connectionstyle="arc3,rad=-0.2"))
    ax.text(0.50, 0.52, "FK: user_id -> users.id", fontsize=7.5, color="#DC2626")

    ax.set_title("Sơ đồ Quan hệ Thực thể Cơ sở dữ liệu (Database Schema / ERD)", fontsize=11, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig("report_assets/fig_7_database_erd.png")
    plt.close()

def create_ui_mockups():
    # 1. Dashboard Mockup
    fig, ax = plt.subplots(figsize=(10, 6), dpi=200)
    ax.axis('off')
    bg = patches.Rectangle((0, 0), 1, 1, color="#0F172A")
    ax.add_patch(bg)
    sidebar = patches.Rectangle((0, 0), 0.22, 1, color="#1E293B")
    ax.add_patch(sidebar)
    ax.text(0.11, 0.94, "DATA PLATFORM", ha='center', va='center', fontsize=11, fontweight='bold', color="#38BDF8")
    menus = ["Dashboard", "Nguồn dữ liệu", "Báo cáo", "Dự báo (Prediction)", "Trợ lý ảo (Assistant)", "Quản lý User", "Lịch trình (Cron)"]
    for i, m in enumerate(menus):
        y = 0.84 - i*0.08
        col = "#38BDF8" if i == 0 else "#94A3B8"
        if i == 0:
            box = patches.FancyBboxPatch((0.02, y-0.025), 0.18, 0.05, boxstyle="round,pad=0.01", color="#0284C7", alpha=0.3)
            ax.add_patch(box)
        ax.text(0.04, y, f"• {m}", ha='left', va='center', fontsize=9, fontweight='bold' if i==0 else 'normal', color=col)
        
    # KPI cards
    kpis = [("TỔNG DOANH THU", "1.258.420.000 đ", "#10B981"), ("TỔNG ĐƠN HÀNG", "3.428 đơn", "#38BDF8"), ("GIÁ TRỊ TB ĐƠN (AOV)", "367.100 đ", "#F59E0B")]
    for i, (title, val, col) in enumerate(kpis):
        x = 0.26 + i*0.24
        card = patches.FancyBboxPatch((x, 0.72), 0.22, 0.18, boxstyle="round,pad=0.02", ec="#334155", fc="#1E293B", lw=1.2)
        ax.add_patch(card)
        ax.text(x+0.02, 0.85, title, fontsize=8, color="#94A3B8", fontweight='bold')
        ax.text(x+0.02, 0.77, val, fontsize=12, color=col, fontweight='bold')
        
    # Chart area
    chart_box = patches.FancyBboxPatch((0.26, 0.10), 0.70, 0.58, boxstyle="round,pad=0.02", ec="#334155", fc="#1E293B", lw=1.2)
    ax.add_patch(chart_box)
    ax.text(0.28, 0.63, "Biểu đồ biến động doanh thu & Đường xu hướng Moving Average", fontsize=10, fontweight='bold', color="#F8FAFC")
    
    # Mini chart lines
    cx = np.linspace(0.30, 0.92, 20)
    cy = 0.35 + 0.12*np.sin(np.linspace(0, 5, 20)) + np.random.normal(0, 0.02, 20)
    ax.plot(cx, cy, color="#10B981", lw=2, marker='o', markersize=3, label="Thực tế")
    ax.plot(cx, 0.35 + 0.12*np.sin(np.linspace(0, 5, 20)), color="#38BDF8", lw=2, ls="--", label="Moving Average")
    ax.legend(loc='lower right', frameon=False, fontsize=8, labelcolor='white')
    
    plt.tight_layout()
    plt.savefig("report_assets/fig_8_2_ui_dashboard.png")
    plt.close()

    # 2. Assistant Screen Mockup (Đã bỏ chi nhánh, đúng 5 câu hỏi như trong Desktop App)
    fig, ax = plt.subplots(figsize=(10, 6), dpi=200)
    ax.axis('off')
    bg = patches.Rectangle((0, 0), 1, 1, color="#0F172A")
    ax.add_patch(bg)
    sidebar = patches.Rectangle((0, 0), 0.22, 1, color="#1E293B")
    ax.add_patch(sidebar)
    ax.text(0.11, 0.94, "DATA PLATFORM", ha='center', va='center', fontsize=11, fontweight='bold', color="#38BDF8")
    for i, m in enumerate(menus):
        y = 0.84 - i*0.08
        col = "#38BDF8" if i == 4 else "#94A3B8"
        if i == 4:
            box = patches.FancyBboxPatch((0.02, y-0.025), 0.18, 0.05, boxstyle="round,pad=0.01", color="#0284C7", alpha=0.3)
            ax.add_patch(box)
        ax.text(0.04, y, f"• {m}", ha='left', va='center', fontsize=9, fontweight='bold' if i==4 else 'normal', color=col)
        
    # Questions list on left of main area
    q_box = patches.FancyBboxPatch((0.25, 0.10), 0.32, 0.80, boxstyle="round,pad=0.02", ec="#334155", fc="#1E293B", lw=1.2)
    ax.add_patch(q_box)
    ax.text(0.27, 0.85, "Câu hỏi nghiệp vụ mẫu:", fontsize=9.5, fontweight='bold', color="#38BDF8")
    sample_qs = [
        "1. Doanh thu tháng này so với tháng trước?",
        "2. Sản phẩm nào bán chạy nhất tháng này?",
        "3. Xu hướng doanh thu sắp tới dự báo thế nào?",
        "4. Có nguồn dữ liệu nào đang gặp lỗi không?",
        "5. Có phát hiện dữ liệu bất thường nào gần đây?"
    ]
    for i, q in enumerate(sample_qs):
        qy = 0.77 - i*0.13
        q_btn = patches.FancyBboxPatch((0.265, qy-0.04), 0.29, 0.08, boxstyle="round,pad=0.01", ec="#0284C7" if i==1 else "#475569", fc="#0369A1" if i==1 else "#334155", lw=1)
        ax.add_patch(q_btn)
        ax.text(0.275, qy, q, fontsize=7.2, color="#F8FAFC", va='center')
        
    # Answer box on right
    ans_box = patches.FancyBboxPatch((0.60, 0.10), 0.37, 0.80, boxstyle="round,pad=0.02", ec="#334155", fc="#1E293B", lw=1.2)
    ax.add_patch(ans_box)
    ax.text(0.62, 0.85, "Trả lời từ Trợ lý ảo (AI Insight Engine):", fontsize=9.5, fontweight='bold', color="#10B981")
    ans_text = "Sản phẩm bán chạy nhất tháng này là 'Webcam 1080p',\nvới tổng cộng 145 sản phẩm bán ra,\nmang lại doanh thu 94.250.000 đ."
    ax.text(0.62, 0.74, ans_text, fontsize=8.5, color="#F8FAFC", va='top')
    
    # Mini table for Top products
    ax.text(0.62, 0.58, "Top 5 sản phẩm bán chạy nhất:", fontsize=8.5, fontweight='bold', color="#94A3B8")
    top_products = [
        ("1. Webcam 1080p", "94.250.000 đ"),
        ("2. Màn hình 24inch", "86.400.000 đ"),
        ("3. Loa máy tính", "52.000.000 đ"),
        ("4. Chuột không dây", "38.500.000 đ"),
        ("5. Bàn phím cơ", "31.200.000 đ")
    ]
    for i, (pname, pval) in enumerate(top_products):
        py = 0.50 - i*0.065
        ax.text(0.62, py, pname, fontsize=8, color="#CBD5E1")
        ax.text(0.83, py, pval, fontsize=8, color="#10B981", fontweight='bold')
        
    plt.tight_layout()
    plt.savefig("report_assets/fig_8_8_ui_assistant.png")
    plt.close()

if __name__ == "__main__":
    create_use_case()
    create_activity_sync()
    create_sequence_sync()
    create_class_diagram()
    create_database_erd()
    create_ui_mockups()
    print("All UML & UI diagrams created successfully!")
