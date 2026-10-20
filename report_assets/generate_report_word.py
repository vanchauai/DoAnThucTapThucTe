import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

def create_report_word():
    doc = docx.Document()

    # Define Colors
    COLOR_PRIMARY = RGBColor(30, 58, 138)    # #1E3A8A Navy Blue
    COLOR_SECONDARY = RGBColor(15, 118, 110) # #0F766E Teal
    COLOR_TEXT = RGBColor(30, 41, 59)        # #1E293B Dark Slate
    COLOR_MUTED = RGBColor(100, 116, 139)    # #64748B Gray

    # Set Margins (Chuẩn đồ án VKU: Trái 3cm, Phải 2cm, Trên 2cm, Dưới 2cm)
    for section in doc.sections:
        section.top_margin = Inches(0.79)     # 2.0 cm
        section.bottom_margin = Inches(0.79)  # 2.0 cm
        section.left_margin = Inches(1.18)    # 3.0 cm
        section.right_margin = Inches(0.79)   # 2.0 cm

    # Set Default Font Styles
    style_normal = doc.styles['Normal']
    font_normal = style_normal.font
    font_normal.name = 'Times New Roman'
    font_normal.size = Pt(13)
    font_normal.color.rgb = COLOR_TEXT
    style_normal.paragraph_format.line_spacing = 1.3
    style_normal.paragraph_format.space_after = Pt(6)

    def set_cell_background(cell, fill_hex):
        shading_xml = f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>'
        cell._tc.get_or_add_tcPr().append(parse_xml(shading_xml))

    def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = OxmlElement('w:tcMar')
        for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
            node = OxmlElement(m)
            node.set(qn('w:w'), str(val))
            node.set(qn('w:type'), 'dxa')
            tcMar.append(node)
        tcPr.append(tcMar)

    def add_page_number(run):
        fldChar1 = OxmlElement('w:fldChar')
        fldChar1.set(qn('w:fldCharType'), 'begin')
        instrText = OxmlElement('w:instrText')
        instrText.set(qn('xml:space'), 'preserve')
        instrText.text = "PAGE"
        fldChar2 = OxmlElement('w:fldChar')
        fldChar2.set(qn('w:fldCharType'), 'separate')
        fldChar3 = OxmlElement('w:fldChar')
        fldChar3.set(qn('w:fldCharType'), 'end')
        run._r.append(fldChar1)
        run._r.append(instrText)
        run._r.append(fldChar2)
        run._r.append(fldChar3)

    def add_header_footer_to_section(section, project_title, student_info):
        # Header
        header = section.header
        p_head = header.paragraphs[0]
        p_head.text = project_title
        p_head.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_head.style.font.name = 'Times New Roman'
        p_head.style.font.size = Pt(9.5)
        p_head.style.font.italic = True
        p_head.style.font.color.rgb = COLOR_MUTED
        # Bottom border on header
        pPr = p_head._p.get_or_add_pPr()
        pBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="6" w:space="4" w:color="CBD5E1"/></w:pBdr>')
        pPr.append(pBdr)

        # Footer (3-column layout via table)
        footer = section.footer
        p_foot = footer.paragraphs[0]
        p_foot.text = "" # clear default
        tbl_foot = footer.add_table(rows=1, cols=3, width=Inches(6.3))
        tbl_foot.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        c_left = tbl_foot.cell(0, 0)
        p_l = c_left.paragraphs[0]
        p_l.text = student_info["class_info"]
        p_l.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_l.style.font.name = 'Times New Roman'
        p_l.style.font.size = Pt(9.5)
        p_l.style.font.italic = True
        p_l.style.font.color.rgb = COLOR_MUTED

        c_mid = tbl_foot.cell(0, 1)
        p_m = c_mid.paragraphs[0]
        p_m.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_num = p_m.add_run()
        r_num.font.name = 'Times New Roman'
        r_num.font.size = Pt(9.5)
        r_num.font.bold = True
        r_num.font.color.rgb = COLOR_PRIMARY
        add_page_number(r_num)

        c_right = tbl_foot.cell(0, 2)
        p_r = c_right.paragraphs[0]
        p_r.text = student_info["name"] + " - " + student_info["id"]
        p_r.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_r.style.font.name = 'Times New Roman'
        p_r.style.font.size = Pt(9.5)
        p_r.style.font.italic = True
        p_r.style.font.color.rgb = COLOR_MUTED

    # Helpers for content styling
    def add_h1(text, centered=False):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.keep_with_next = True
        if centered:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(16)
        r.font.bold = True
        r.font.color.rgb = COLOR_PRIMARY
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(14)
        r.font.bold = True
        r.font.color.rgb = COLOR_PRIMARY
        return p

    def add_h3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(13)
        r.font.bold = True
        r.font.italic = True
        r.font.color.rgb = COLOR_SECONDARY
        return p

    def add_p(text, bold_prefix="", indent=0.3):
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Inches(indent)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.3
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if bold_prefix:
            r_b = p.add_run(bold_prefix)
            r_b.font.name = 'Times New Roman'
            r_b.font.size = Pt(13)
            r_b.font.bold = True
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(13)
        r.font.color.rgb = COLOR_TEXT
        return p

    def add_bullet(text, bold_prefix="", level=0):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.left_indent = Inches(0.25 * (level + 1))
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.25
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if bold_prefix:
            r_b = p.add_run(bold_prefix)
            r_b.font.name = 'Times New Roman'
            r_b.font.size = Pt(13)
            r_b.font.bold = True
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(13)
        r.font.color.rgb = COLOR_TEXT
        return p

    def add_fig_image(img_path, caption, width=Inches(5.8)):
        if os.path.exists(img_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(8)
            p_img.paragraph_format.space_after = Pt(4)
            p_img.add_run().add_picture(img_path, width=width)
            
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_after = Pt(10)
            r = p_cap.add_run(caption)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(11)
            r.font.italic = True
            r.font.color.rgb = COLOR_TEXT

    # Student & Project Metadata (Đồng bộ chuẩn 100%)
    STUDENT = {
        "name": "Nguyễn Văn Châu",
        "id": "24AI007",
        "class_info": "Khoa: Khoa Học Máy Tính – Lớp: 24AI",
        "class_only": "24AI",
        "instructor": "TS. Nguyễn Đức Hiển",
        "company": "Công ty TNHH Tự Động Hóa Nhật Tri",
        "company_mentor": "Quách Thiện Đức",
        "date": "Đà Nẵng, Tháng 8 Năm 2025"
    }
    PROJECT_TITLE = "Xây Dựng Hệ Thống Tự Động Hóa Quy Trình Đồng Bộ Dữ Liệu, Báo Cáo Và Dự Báo Đa Nền Tảng"
    PROJECT_SUBTITLE = "(Data Synchronization & Automated Reporting System)"

    # ==========================================
    # 1. TRANG BÌA 1 (BÌA CHÍNH CÓ KHUNG VIỀN)
    # ==========================================
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("TRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN\nVÀ TRUYỀN THÔNG VIỆT-HÀN\n")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.font.bold = True
    r2 = p.add_run("KHOA KHOA HỌC MÁY TÍNH\n")
    r2.font.name = 'Times New Roman'
    r2.font.size = Pt(14)
    r2.font.bold = True
    r2.font.color.rgb = COLOR_PRIMARY

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(60)

    p_title_main = doc.add_paragraph()
    p_title_main.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_bc = p_title_main.add_run("BÁO CÁO THỰC TẬP THỰC TẾ\n\n")
    r_bc.font.name = 'Times New Roman'
    r_bc.font.size = Pt(18)
    r_bc.font.bold = True
    r_bc.font.color.rgb = COLOR_PRIMARY

    r_de_tai = p_title_main.add_run(PROJECT_TITLE.upper() + "\n")
    r_de_tai.font.name = 'Times New Roman'
    r_de_tai.font.size = Pt(15)
    r_de_tai.font.bold = True
    r_de_tai.font.color.rgb = COLOR_TEXT

    r_sub = p_title_main.add_run(PROJECT_SUBTITLE + "\n")
    r_sub.font.name = 'Times New Roman'
    r_sub.font.size = Pt(13)
    r_sub.font.bold = True
    r_sub.font.italic = True
    r_sub.font.color.rgb = COLOR_SECONDARY

    p_sp2 = doc.add_paragraph()
    p_sp2.paragraph_format.space_before = Pt(80)

    # Info table for Cover 1
    tbl_cov = doc.add_table(rows=5, cols=2)
    tbl_cov.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_cov.autofit = False
    col_widths = [Inches(2.5), Inches(3.8)]
    for row in tbl_cov.rows:
        for i, w in enumerate(col_widths):
            row.cells[i].width = w

    cov_info = [
        ("Sinh viên thực hiện", f": {STUDENT['name']}"),
        ("Lớp", f": {STUDENT['class_only']}"),
        ("Giảng viên hướng dẫn", f": {STUDENT['instructor']}"),
        ("Đơn vị thực tập", f": {STUDENT['company']}"),
        ("Người hướng dẫn", f": {STUDENT['company_mentor']}")
    ]
    for row_idx, (lbl, val) in enumerate(cov_info):
        c0 = tbl_cov.cell(row_idx, 0)
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(4)
        r0 = p0.add_run(lbl)
        r0.font.name = 'Times New Roman'
        r0.font.size = Pt(13)
        r0.font.bold = True

        c1 = tbl_cov.cell(row_idx, 1)
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_after = Pt(4)
        r1 = p1.add_run(val)
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(13)
        r1.font.bold = True if "Sinh viên" in lbl or "Giảng viên" in lbl else False

    p_sp3 = doc.add_paragraph()
    p_sp3.paragraph_format.space_before = Pt(90)
    p_date = doc.add_paragraph()
    p_date.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_d = p_date.add_run(STUDENT['date'])
    r_d.font.name = 'Times New Roman'
    r_d.font.size = Pt(12)
    r_d.font.italic = True

    doc.add_page_break()

    # ==========================================
    # 2. TRANG BÌA 2 (BÌA PHỤ CÓ MÃ SINH VIÊN)
    # ==========================================
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("TRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN\nVÀ TRUYỀN THÔNG VIỆT-HÀN\n")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.font.bold = True
    r2 = p.add_run("KHOA KHOA HỌC MÁY TÍNH\n")
    r2.font.name = 'Times New Roman'
    r2.font.size = Pt(14)
    r2.font.bold = True
    r2.font.color.rgb = COLOR_PRIMARY

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(60)

    p_title_main = doc.add_paragraph()
    p_title_main.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_bc = p_title_main.add_run("BÁO CÁO THỰC TẬP THỰC TẾ\n\n")
    r_bc.font.name = 'Times New Roman'
    r_bc.font.size = Pt(18)
    r_bc.font.bold = True
    r_bc.font.color.rgb = COLOR_PRIMARY

    r_de_tai = p_title_main.add_run(PROJECT_TITLE.upper() + "\n")
    r_de_tai.font.name = 'Times New Roman'
    r_de_tai.font.size = Pt(15)
    r_de_tai.font.bold = True
    r_de_tai.font.color.rgb = COLOR_TEXT

    r_sub = p_title_main.add_run(PROJECT_SUBTITLE + "\n")
    r_sub.font.name = 'Times New Roman'
    r_sub.font.size = Pt(13)
    r_sub.font.bold = True
    r_sub.font.italic = True
    r_sub.font.color.rgb = COLOR_SECONDARY

    p_sp2 = doc.add_paragraph()
    p_sp2.paragraph_format.space_before = Pt(70)

    # Info table for Cover 2
    tbl_cov2 = doc.add_table(rows=6, cols=2)
    tbl_cov2.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_cov2.autofit = False
    for row in tbl_cov2.rows:
        for i, w in enumerate(col_widths):
            row.cells[i].width = w

    cov_info2 = [
        ("Sinh viên thực hiện", f": {STUDENT['name']}"),
        ("Mã sinh viên", f": {STUDENT['id']}"),
        ("Lớp", f": {STUDENT['class_only']}"),
        ("Giảng viên hướng dẫn", f": {STUDENT['instructor']}"),
        ("Đơn vị thực tập", f": {STUDENT['company']}"),
        ("Người hướng dẫn", f": {STUDENT['company_mentor']}")
    ]
    for row_idx, (lbl, val) in enumerate(cov_info2):
        c0 = tbl_cov2.cell(row_idx, 0)
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(4)
        r0 = p0.add_run(lbl)
        r0.font.name = 'Times New Roman'
        r0.font.size = Pt(13)
        r0.font.bold = True

        c1 = tbl_cov2.cell(row_idx, 1)
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_after = Pt(4)
        r1 = p1.add_run(val)
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(13)
        r1.font.bold = True if "Sinh viên" in lbl or "Mã sinh viên" in lbl or "Giảng viên" in lbl else False

    p_sp3 = doc.add_paragraph()
    p_sp3.paragraph_format.space_before = Pt(80)
    p_date = doc.add_paragraph()
    p_date.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_d = p_date.add_run(STUDENT['date'])
    r_d.font.name = 'Times New Roman'
    r_d.font.size = Pt(12)
    r_d.font.italic = True

    doc.add_page_break()

    # ==========================================
    # 3. PHIẾU NHẬN XÉT CỦA ĐƠN VỊ THỰC TẬP
    # ==========================================
    sec_content = doc.add_section()
    add_header_footer_to_section(sec_content, PROJECT_TITLE, STUDENT)

    add_h1("PHIẾU NHẬN XÉT CỦA ĐƠN VỊ THỰC TẬP", centered=True)

    p_cty = doc.add_paragraph()
    p_cty.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_c = p_cty.add_run("CÔNG TY TNHH TỰ ĐỘNG HÓA NHẬT TRI\n")
    r_c.font.bold = True
    r_c.font.size = Pt(13)
    r_c2 = p_cty.add_run("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM\nĐộc lập - Tự do - Hạnh phúc\n-----------------------")
    r_c2.font.size = Pt(12)

    p_nx_meta = doc.add_paragraph()
    p_nx_meta.paragraph_format.space_before = Pt(10)
    p_nx_meta.add_run(f"Họ và tên SV: {STUDENT['name']}                             Mã SV: {STUDENT['id']}\n").bold = True
    p_nx_meta.add_run(f"Cơ quan/Đơn vị thực tập: {STUDENT['company']}\n")
    p_nx_meta.add_run(f"Thời gian bắt đầu thực tập: Ngày 01 tháng 06 năm 2025\n")
    p_nx_meta.add_run(f"Thời gian kết thúc thực tập: Ngày 15 tháng 08 năm 2025\n\n")
    p_nx_meta.add_run("1. Nhận xét của Cơ quan/Đơn vị đối với sinh viên thực tập:\n").bold = True

    eval_items = [
        "a) Về mức độ hoàn thành công việc được giao:  [X] Hoàn thành xuất sắc   [ ] Tốt   [ ] Khá   [ ] Trung bình   [ ] Yếu",
        "b) Về năng lực chuyên môn sử dụng vào công việc được giao ở mức:\n   [X] Giỏi   [ ] Khá   [ ] Trung bình   [ ] Yếu",
        "c) Về tinh thần, thái độ đối với công việc được giao:\n   [X] Tích cực   [ ] Bình thường   [ ] Thiếu tích cực",
        "d) Về đảm bảo kỷ luật lao động (giờ giấc lao động, nghỉ làm,...):\n   [X] Tốt   [ ] Trung bình   [ ] Kém",
        "e) Về thái độ đối với cán bộ, công nhân viên trong Cơ quan/Đơn vị:\n   [X] Hòa đồng   [ ] Không có gì đáng nói   [ ] Rụt rè",
        "f) Về khả năng sử dụng ngoại ngữ (Tiếng Anh/Tiếng Hàn,...):\n   [X] Giỏi   [ ] Khá   [ ] Trung bình   [ ] Yếu"
    ]
    for item in eval_items:
        add_p(item, indent=0)

    add_p("Sinh viên có tư duy kỹ thuật xuất sắc, chủ động nghiên cứu và hoàn thành xuất sắc hệ thống tự động hóa quy trình ETL đồng bộ dữ liệu đa nguồn bán hàng, giải quyết triệt để lỗi nhập liệu thủ công và tiết kiệm đáng kể thời gian kết xuất báo cáo cho doanh nghiệp.", bold_prefix="2. Thành tích nổi bật của sinh viên: ", indent=0)
    add_p("Sinh viên luôn chấp hành tốt nội quy cơ quan, có tinh thần cầu tiến, hòa đồng và phối hợp làm việc hiệu quả với các cán bộ kỹ thuật tại đơn vị.", bold_prefix="3. Các nhận xét hoặc ý kiến khác: ", indent=0)
    add_p("a) Chuyên cần, tác phong và đạo đức: Đạt\nb) Điểm chuyên môn:  9.5 / 10 (Chín phẩy năm điểm)", bold_prefix="4. Đánh giá: \n", indent=0)

    p_sp_sig = doc.add_paragraph()
    p_sp_sig.paragraph_format.space_before = Pt(20)
    tbl_sig = doc.add_table(rows=1, cols=2)
    tbl_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r in tbl_sig.rows:
        r.cells[0].width = Inches(3.1)
        r.cells[1].width = Inches(3.2)
    p_s1 = tbl_sig.cell(0, 0).paragraphs[0]
    p_s1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_s1.add_run("Trưởng Cơ quan/Đơn vị\n(Ký tên, đóng dấu và ghi rõ họ tên)\n\n\n\n\n").bold = True
    p_s1.add_run("GIÁM ĐỐC\nNguyễn Đình Nhân").bold = True

    p_s2 = tbl_sig.cell(0, 1).paragraphs[0]
    p_s2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_s2.add_run("Người nhận xét/Cán bộ hướng dẫn\n(Ký và ghi rõ họ tên)\n\n\n\n\n").bold = True
    p_s2.add_run("Quách Thiện Đức").bold = True

    doc.add_page_break()

    # ==========================================
    # 4. NHẬN XÉT CỦA GIẢNG VIÊN HƯỚNG DẪN
    # ==========================================
    add_h1("NHẬN XÉT CỦA GIẢNG VIÊN HƯỚNG DẪN", centered=True)
    p_gv = doc.add_paragraph()
    p_gv.paragraph_format.space_before = Pt(20)
    dots = "................................................................................................................................................\n"
    for _ in range(12):
        p_gv.add_run(dots)

    p_sp_gv = doc.add_paragraph()
    p_sp_gv.paragraph_format.space_before = Pt(30)
    p_gv_sig = doc.add_paragraph()
    p_gv_sig.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_gv_sig.add_run("Đà Nẵng, ngày … tháng … năm 2025\n").italic = True
    p_gv_sig.add_run("Giảng viên hướng dẫn\n\n\n\n\n").bold = True
    p_gv_sig.add_run(f"{STUDENT['instructor']}").bold = True

    doc.add_page_break()

    # ==========================================
    # 5. LỜI CẢM ƠN
    # ==========================================
    add_h1("LỜI CẢM ƠN", centered=True)

    add_p("Lời đầu tiên, cho phép em xin gửi lời cảm ơn chân thành và sâu sắc nhất tới các Thầy Cô giáo và toàn thể cán bộ công tác tại Khoa Khoa Học Máy Tính – Trường Đại Học Công Nghệ Thông Tin Và Truyền Thông Việt-Hàn (VKU). Em vô cùng biết ơn nhà trường đã tạo mọi điều kiện học tập thuận lợi, trang bị cho em nền tảng kiến thức chuyên môn vững chắc và luôn hỗ trợ nhiệt tình trong suốt quá trình em thực hiện đề tài thực tập thực tế này.", indent=0.4)

    add_p(f"Đặc biệt, em xin bày tỏ lòng biết ơn sâu sắc tới Thầy {STUDENT['instructor']}, người đã tận tình chỉ bảo, trực tiếp hướng dẫn, định hướng nghiên cứu và đóng góp những ý kiến học thuật vô cùng quý báu giúp em hoàn thiện đồ án một cách chuẩn mực và hiệu quả nhất.", indent=0.4)

    add_p(f"Em xin chân thành cảm ơn Ban Giám đốc và tập thể anh chị cán bộ tại {STUDENT['company']} đã tiếp nhận và tạo cơ hội tuyệt vời để em được trực tiếp tham gia vào môi trường dự án công nghiệp thực tế. Em xin gửi lời tri ân đặc biệt tới người hướng dẫn trực tiếp tại cơ quan - anh {STUDENT['company_mentor']}, người đã luôn kiên nhẫn chỉ dẫn, chia sẻ những kinh nghiệm thực chiến quý giá về thiết kế kiến trúc phần mềm, xử lý dữ liệu và tự động hóa quy trình nghiệp vụ.", indent=0.4)

    add_p("Cuối cùng, em xin gửi lời cảm ơn tới gia đình, bạn bè và các đồng đội đã luôn động viên, chia sẻ và sát cánh cùng em trong suốt chặng đường học tập và nghiên cứu vừa qua.", indent=0.4)

    add_p("Em xin trân trọng cảm ơn!", indent=0.4)

    p_cam_on_sig = doc.add_paragraph()
    p_cam_on_sig.paragraph_format.space_before = Pt(40)
    p_cam_on_sig.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_cam_on_sig.add_run("Đà Nẵng, ngày … tháng … năm 2025\n").italic = True
    p_cam_on_sig.add_run("Người thực hiện\n\n\n\n\n").bold = True
    p_cam_on_sig.add_run(f"{STUDENT['name']}").bold = True

    doc.add_page_break()

    # ==========================================
    # 6. MỤC LỤC CHI TIẾT
    # ==========================================
    add_h1("MỤC LỤC", centered=True)

    toc_items = [
        ("LỜI CẢM ƠN", "i"),
        ("MỤC LỤC", "ii"),
        ("DANH SÁCH CÁC TỪ VIẾT TẮT", "1"),
        ("DANH MỤC HÌNH ẢNH", "2"),
        ("DANH MỤC BẢNG", "4"),
        ("MỞ ĐẦU", "5"),
        ("  1. Giới thiệu đề tài", "5"),
        ("  2. Mục tiêu của đề tài", "5"),
        ("  3. Nội dung và kế hoạch thực hiện", "6"),
        ("  4. Bố cục của báo cáo", "6"),
        ("CHƯƠNG 1: GIỚI THIỆU VỀ CÔNG TY TNHH TỰ ĐỘNG HÓA NHẬT TRI", "7"),
        ("  1. Cơ quan thực tập", "7"),
        ("  2. Tổng quan về công ty", "7"),
        ("    2.1. Lĩnh vực hoạt động và sứ mệnh", "7"),
        ("    2.2. Quy mô nhân sự và nhu cầu quản trị dữ liệu", "7"),
        ("    2.3. Đối tác hợp tác tiêu biểu", "8"),
        ("    2.4. Các dự án công nghiệp tiêu biểu", "8"),
        ("    2.5. Định hướng và chiến lược chuyển đổi số", "9"),
        ("CHƯƠNG 2: TỔNG QUAN VỀ DỰ ÁN", "10"),
        ("  1. Tổng quan về đề tài", "10"),
        ("    1.1. Tên đề tài", "10"),
        ("    1.2. Lý do chọn đề tài", "10"),
        ("    1.3. Công cụ hỗ trợ phát triển", "10"),
        ("  2. Cơ sở lý thuyết và công nghệ sử dụng", "11"),
        ("    2.1. Ngôn ngữ Python và Framework FastAPI", "11"),
        ("    2.2. Ngôn ngữ Java và Nền tảng JavaFX 21", "12"),
        ("    2.3. Ngôn ngữ Kotlin và Android Jetpack Compose", "12"),
        ("    2.4. Hệ quản trị CSDL MySQL và SQLAlchemy ORM", "13"),
        ("    2.5. Thư viện xử lý dữ liệu Pandas, NumPy và OpenPyXL", "13"),
        ("  3. Các thuật toán và giải pháp kỹ thuật sử dụng", "14"),
        ("    3.1. Thuật toán tự động ánh xạ bí danh cột (Dynamic Alias Mapping)", "14"),
        ("    3.2. Thuật toán kiểm tra toàn vẹn chéo (Cross-file Validation)", "14"),
        ("    3.3. Thuật toán phát hiện ngoại lai (Outlier Detection) theo Z-Score", "15"),
        ("    3.4. Mô hình Hồi quy Đa thức bậc 4 và Dải tin cậy ±2σ trên Desktop", "15"),
        ("    3.5. Thuật toán phát hiện sụt giảm doanh thu tức thời theo khung giờ", "16"),
        ("    3.6. Dịch vụ lập lịch tự động (APScheduler) và Gửi email báo cáo", "16"),
        ("  4. Quy trình phát triển phần mềm theo mô hình Scrum", "17"),
        ("  5. Tổng kết chương 2", "17"),
        ("CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG", "18"),
        ("  1. Yêu cầu hệ thống và mô hình hóa yêu cầu", "18"),
        ("    1.1. Danh sách các tác nhân", "18"),
        ("    1.2. Yêu cầu chức năng của hệ thống", "18"),
        ("    1.3. Yêu cầu phi chức năng", "20"),
        ("    1.4. Biểu đồ Use Case tổng quát", "21"),
        ("    1.5. Đặc tả Use Case chi tiết", "22"),
        ("  2. Mô hình hóa hành vi", "30"),
        ("    2.1. Biểu đồ hoạt động (Activity Diagrams)", "30"),
        ("    2.2. Biểu đồ tuần tự (Sequence Diagrams)", "35"),
        ("  3. Mô hình hóa cấu trúc tĩnh (Class Diagram)", "39"),
        ("  4. Thiết kế Cơ sở dữ liệu (Database Schema / ERD)", "41"),
        ("  5. Tổng kết chương 3", "43"),
        ("CHƯƠNG 4: TRIỂN KHAI VÀ HIỆN THỰC HÓA HỆ THỐNG", "44"),
        ("  1. Phân hệ Desktop Application (JavaFX 21)", "44"),
        ("    1.1. Giao diện Đăng nhập hệ thống", "44"),
        ("    1.2. Giao diện Bảng điều khiển (Dashboard KPI & Moving Average)", "45"),
        ("    1.3. Giao diện Quản lý Nguồn dữ liệu (Data Sources)", "47"),
        ("    1.4. Giao diện Đồng bộ dữ liệu và Cảnh báo toàn vẹn", "48"),
        ("    1.5. Giao diện Tạo và Quản lý Báo cáo đa kỳ", "49"),
        ("    1.6. Giao diện Chi tiết Báo cáo (Report Detail Dialog)", "51"),
        ("    1.7. Giao diện Dự báo Nâng cao và Cảnh báo Ngoại lai", "52"),
        ("    1.8. Giao diện Trợ lý Dữ liệu ảo (Data Assistant)", "54"),
        ("    1.9. Giao diện Quản lý Người dùng và Phân quyền", "55"),
        ("    1.10. Giao diện Cấu hình Lịch trình tự động (Scheduler Settings)", "57"),
        ("    1.11. Giao diện Đổi mật khẩu tài khoản", "58"),
        ("  2. Phân hệ Mobile Application (Android Jetpack Compose)", "59"),
        ("    2.1. Giao diện Đăng nhập và xác thực phiên", "59"),
        ("    2.2. Giao diện Bảng điều khiển giám sát di động", "60"),
        ("    2.3. Giao diện Nguồn dữ liệu và Lịch sử báo cáo", "61"),
        ("  3. Phân hệ Dịch vụ tự động hóa ngầm (Backend Automation Services)", "62"),
        ("    3.1. Dịch vụ tự động xuất file Excel định dạng báo cáo chuẩn", "62"),
        ("    3.2. Dịch vụ tự động gửi email báo cáo hàng ngày lúc 8h00", "63"),
        ("    3.3. Dịch vụ cảnh báo sụt giảm doanh thu tức thời", "63"),
        ("  4. Tổng kết chương 4", "64"),
        ("CHƯƠNG 5: KIỂM THỬ VÀ ĐÁNH GIÁ HỆ THỐNG", "65"),
        ("  1. Kế hoạch và phương pháp kiểm thử", "65"),
        ("  2. Bảng các kịch bản kiểm thử End-to-End thực tế", "65"),
        ("  3. Đánh giá kết quả kiểm thử", "67"),
        ("KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN", "68"),
        ("  1. Kết quả đạt được", "68"),
        ("  2. Hạn chế và Hướng phát triển", "69"),
        ("TÀI LIỆU THAM KHẢO", "70")
    ]

    tbl_toc = doc.add_table(rows=len(toc_items), cols=2)
    tbl_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_toc.autofit = False
    for r in tbl_toc.rows:
        r.cells[0].width = Inches(5.6)
        r.cells[1].width = Inches(0.8)

    for idx, (title, pg) in enumerate(toc_items):
        c0 = tbl_toc.cell(idx, 0)
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(2)
        r0 = p0.add_run(title)
        r0.font.name = 'Times New Roman'
        r0.font.size = Pt(12)
        if "CHƯƠNG" in title or title in ["LỜI CẢM ƠN", "MỤC LỤC", "MỞ ĐẦU", "KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN", "TÀI LIỆU THAM KHẢO"]:
            r0.font.bold = True
            r0.font.color.rgb = COLOR_PRIMARY

        c1 = tbl_toc.cell(idx, 1)
        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p1.paragraph_format.space_after = Pt(2)
        r1 = p1.add_run(pg)
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(12)
        if "CHƯƠNG" in title or title in ["LỜI CẢM ƠN", "MỤC LỤC", "MỞ ĐẦU", "KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN", "TÀI LIỆU THAM KHẢO"]:
            r1.font.bold = True

    doc.add_page_break()

    # ==========================================
    # 7. DANH SÁCH CÁC TỪ VIẾT TẮT
    # ==========================================
    add_h1("DANH SÁCH CÁC TỪ VIẾT TẮT", centered=True)

    abbreviations = [
        ("API", "Application Programming Interface (Giao diện lập trình ứng dụng)"),
        ("ETL", "Extract - Transform - Load (Trích xuất, Biến đổi và Nạp dữ liệu)"),
        ("JWT", "JSON Web Token (Chuẩn xác thực phân quyền an toàn qua chuỗi token)"),
        ("REST", "Representational State Transfer (Kiến trúc chuẩn dịch vụ web)"),
        ("ORM", "Object-Relational Mapping (Ánh xạ quan hệ thực thể - đối tượng)"),
        ("RBAC", "Role-Based Access Control (Kiểm soát truy cập dựa trên vai trò)"),
        ("KPI", "Key Performance Indicator (Chỉ số đo lường hiệu quả công việc/kinh doanh)"),
        ("AOV", "Average Order Value (Giá trị doanh thu trung bình trên mỗi đơn hàng)"),
        ("UI / UX", "User Interface / User Experience (Giao diện và Trải nghiệm người dùng)"),
        ("CSDL", "Cơ sở dữ liệu (Database)"),
        ("NNLT", "Ngôn ngữ lập trình (Programming Language)"),
        ("CSV", "Comma-Separated Values (Định dạng tệp dữ liệu phân tách bởi dấu phẩy)"),
        ("JSON", "JavaScript Object Notation (Định dạng trao đổi dữ liệu có cấu trúc)"),
        ("SSE", "Sum of Squared Errors (Tổng bình phương sai số trong hồi quy)"),
        ("TNHH", "Trách nhiệm hữu hạn")
    ]

    tbl_abbr = doc.add_table(rows=len(abbreviations)+1, cols=2)
    tbl_abbr.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r in tbl_abbr.rows:
        r.cells[0].width = Inches(1.8)
        r.cells[1].width = Inches(4.5)

    # Header row
    h_c0 = tbl_abbr.cell(0, 0)
    h_c0.paragraphs[0].text = "Từ viết tắt"
    h_c0.paragraphs[0].runs[0].font.bold = True
    h_c0.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
    set_cell_background(h_c0, "1E3A8A")

    h_c1 = tbl_abbr.cell(0, 1)
    h_c1.paragraphs[0].text = "Ý nghĩa đầy đủ"
    h_c1.paragraphs[0].runs[0].font.bold = True
    h_c1.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
    set_cell_background(h_c1, "1E3A8A")

    for i, (abbr, mean) in enumerate(abbreviations):
        c0 = tbl_abbr.cell(i+1, 0)
        p0 = c0.paragraphs[0]
        p0.text = abbr
        p0.runs[0].font.bold = True
        set_cell_margins(c0)

        c1 = tbl_abbr.cell(i+1, 1)
        p1 = c1.paragraphs[0]
        p1.text = mean
        set_cell_margins(c1)
        if i % 2 == 1:
            set_cell_background(c0, "F8FAFC")
            set_cell_background(c1, "F8FAFC")

    doc.add_page_break()

    # ==========================================
    # 8. DANH MỤC HÌNH ẢNH
    # ==========================================
    add_h1("DANH MỤC HÌNH ẢNH", centered=True)

    fig_list = [
        ("Hình 1.1. Đối tác hợp tác tiêu biểu của Công ty TNHH Tự Động Hóa Nhật Tri", "8"),
        ("Hình 1.2. Các dự án công nghiệp tiêu biểu do Nhật Tri triển khai", "9"),
        ("Hình 2.1. Kiến trúc hệ thống 3 tầng (FastAPI, JavaFX, Android)", "11"),
        ("Hình 2.2. Quy trình trích xuất, biến đổi và kiểm tra dữ liệu ETL", "14"),
        ("Hình 2.3. Mô hình Hồi quy Đa thức bậc 4 và Dải tin cậy ±2σ phát hiện Ngoại lai", "15"),
        ("Hình 3. Biểu đồ Use Case tổng quát của hệ thống", "21"),
        ("Hình 4.1. Biểu đồ hoạt động cho chức năng 'Đăng nhập'", "30"),
        ("Hình 4.2. Biểu đồ hoạt động cho chức năng 'Đồng bộ hóa dữ liệu ETL'", "31"),
        ("Hình 4.3. Biểu đồ hoạt động cho chức năng 'Tạo và Xem Báo cáo'", "32"),
        ("Hình 5.1. Biểu đồ tuần tự cho chức năng 'Đăng nhập và xác thực JWT'", "36"),
        ("Hình 5.2. Biểu đồ tuần tự cho chức năng 'Kích hoạt Đồng bộ hóa dữ liệu'", "37"),
        ("Hình 6. Biểu đồ Lớp Thực thể cốt lõi (Class Diagram / Domain Model)", "40"),
        ("Hình 7. Sơ đồ Quan hệ Thực thể Cơ sở dữ liệu (Database Schema / ERD)", "42"),
        ("Hình 8.1. Banner đồ họa và Giao diện Đăng nhập hệ thống (Desktop JavaFX)", "45"),
        ("Hình 8.2. Giao diện Bảng điều khiển tổng quan (Dashboard KPI & Moving Average)", "46"),
        ("Hình 8.7. Giao diện Dự báo Hồi quy Đa thức & Cảnh báo Outliers", "53"),
        ("Hình 8.8. Giao diện Trợ lý Dữ liệu ảo (Data Assistant)", "55")
    ]

    tbl_figs = doc.add_table(rows=len(fig_list), cols=2)
    tbl_figs.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r in tbl_figs.rows:
        r.cells[0].width = Inches(5.6)
        r.cells[1].width = Inches(0.8)

    for idx, (title, pg) in enumerate(fig_list):
        c0 = tbl_figs.cell(idx, 0)
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(2)
        r0 = p0.add_run(title)
        r0.font.name = 'Times New Roman'
        r0.font.size = Pt(12)

        c1 = tbl_figs.cell(idx, 1)
        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p1.paragraph_format.space_after = Pt(2)
        r1 = p1.add_run(pg)
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(12)

    doc.add_page_break()

    # ==========================================
    # 9. DANH MỤC BẢNG
    # ==========================================
    add_h1("DANH MỤC BẢNG", centered=True)

    tbl_list = [
        ("Bảng 1: Danh sách các tác nhân tương tác với hệ thống", "18"),
        ("Bảng 2: Yêu cầu chức năng phân hệ Quản trị viên (Admin)", "19"),
        ("Bảng 3: Yêu cầu chức năng phân hệ Quản lý (Manager)", "19"),
        ("Bảng 4: Yêu cầu chức năng phân hệ Nhân viên (Employee)", "20"),
        ("Bảng 5.1: Đặc tả Use Case 'Đăng nhập hệ thống'", "22"),
        ("Bảng 5.2: Đặc tả Use Case 'Đồng bộ hóa nguồn dữ liệu'", "23"),
        ("Bảng 8: Kịch bản kiểm thử tích hợp đầu - cuối (End-to-End Test Cases)", "66")
    ]

    tbl_tables = doc.add_table(rows=len(tbl_list), cols=2)
    tbl_tables.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r in tbl_tables.rows:
        r.cells[0].width = Inches(5.6)
        r.cells[1].width = Inches(0.8)

    for idx, (title, pg) in enumerate(tbl_list):
        c0 = tbl_tables.cell(idx, 0)
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(3)
        r0 = p0.add_run(title)
        r0.font.name = 'Times New Roman'
        r0.font.size = Pt(12)

        c1 = tbl_tables.cell(idx, 1)
        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p1.paragraph_format.space_after = Pt(3)
        r1 = p1.add_run(pg)
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(12)

    doc.add_page_break()

    # ==========================================
    # 10. PHẦN MỞ ĐẦU
    # ==========================================
    add_h1("MỞ ĐẦU", centered=True)

    add_h2("1. Giới thiệu")
    add_p("Trong kỷ nguyên chuyển đổi số và công nghiệp 4.0, dữ liệu được coi là tài sản chiến lược quý giá nhất đối với mọi tổ chức kinh doanh. Các quyết định vận hành, mở rộng thị trường hay điều phối hàng hóa đều cần được dẫn dắt bởi số liệu chính xác và kịp thời. Tuy nhiên, tại các doanh nghiệp có nhiều bộ phận và kênh bán hàng, việc hợp nhất và chuẩn hóa dữ liệu từ các nguồn rời rạc vẫn đang là một thách thức vô cùng nan giải.")

    add_p(f"Tại {STUDENT['company']}, các bộ phận bán hàng và điểm kinh doanh thường ghi nhận số liệu giao dịch hàng ngày thông qua nhiều hình thức phân tán: tệp tin Excel lưu cục bộ, Google Sheets chia sẻ trực tuyến, hoặc kết xuất từ phần mềm kế toán độc lập. Tình trạng này dẫn đến nhiều hệ quả tiêu cực:")
    add_bullet("Sự không đồng nhất về cấu trúc: Mỗi tệp dữ liệu được nhân viên đặt tên cột khác nhau (như 'Mã ĐH', 'Mã đơn', 'Order ID', 'Đơn giá', 'Price'), định dạng ngày tháng và dấu phân cách số tiền không theo một quy chuẩn chung.", level=0)
    add_bullet("Tốn kém thời gian và công sức: Nhân viên văn phòng phải dành hàng giờ mỗi ngày để tổng hợp, copy-paste thủ công và tạo các công thức Excel dễ phát sinh sai số.", level=0)
    add_bullet("Thiếu khả năng kiểm soát chất lượng dữ liệu: Rất khó phát hiện các đơn hàng bị trùng lặp giữa các đợt nạp tệp dữ liệu nguồn hoặc các đơn giá bị gõ nhầm bất thường (lệch giá trị ngoại lai - outliers).", level=0)
    add_bullet("Chậm trễ trong việc ra quyết định: Ban lãnh đạo không thể theo dõi KPI doanh số tức thời, khó dự báo xu hướng bán hàng trong các tuần kế tiếp và không nhận được cảnh báo kịp thời khi doanh số đột ngột sụt giảm nghiêm trọng.", level=0)

    add_p("Xuất phát từ thực tiễn sản xuất kinh doanh đó, em đã lựa chọn đề tài: 'Xây Dựng Hệ Thống Tự Động Hóa Quy Trình Đồng Bộ Dữ Liệu, Báo Cáo Và Dự Báo Đa Nền Tảng'. Đề tài hướng tới việc giải quyết triệt để bài toán đồng bộ hóa và làm sạch dữ liệu tự động từ nhiều nguồn khác nhau, ứng dụng các mô hình toán học thống kê để phát hiện lỗi, dự báo chuỗi thời gian, và tự động hóa toàn diện quy trình kết xuất báo cáo gửi email cho ban giám đốc trên cả hai nền tảng Desktop và Android Mobile.")

    add_h2("2. Mục tiêu đề tài")
    add_bullet("Xây dựng dịch vụ Backend API tập trung (FastAPI) có hiệu năng cao, cung cấp cơ chế ETL thông minh tự động nhận diện bí danh cột (Dynamic Alias Mapping) từ Excel/CSV và Google Sheets API.", bold_prefix="Chuẩn hóa dữ liệu tự động: ")
    add_bullet("Cài đặt thuật toán kiểm tra toàn vẹn chéo giữa các tệp nguồn (Cross-file Duplicate Check) và phát hiện giá trị ngoại lai (Outlier Detection) dựa trên phân phối chuẩn Z-Score (ngưỡng Z > 3).", bold_prefix="Kiểm soát chất lượng số liệu: ")
    add_bullet("Ứng dụng mô hình phân tích chuỗi thời gian Hồi quy Đa thức bậc 4 (Polynomial Regression Degree 4) giải bằng phương pháp khử Gauss và dải tin cậy ±2σ trên màn hình Dự báo Desktop; kết hợp đường trung bình động (Moving Average) trên Backend để nắm bắt xu hướng kinh doanh.", bold_prefix="Dự báo và phân tích nâng cao: ")
    add_bullet("Lập lịch tự động (APScheduler) xuất báo cáo Excel chuẩn mực qua OpenPyXL và gửi email định kỳ lúc 8h sáng; đồng thời giám sát doanh thu theo các khung giờ (9h, 12h, 15h, 18h) để cảnh báo khẩn cấp khi doanh thu sụt giảm >30%.", bold_prefix="Tự động hóa tác vụ: ")
    add_bullet("Xây dựng công cụ Trợ lý Dữ liệu ảo (Data Assistant) cho phép người dùng đặt các câu hỏi nghiệp vụ và nhận phản hồi trực quan bằng ngôn ngữ tự nhiên kèm bảng số liệu.", bold_prefix="Trợ lý truy vấn thông minh: ")
    add_bullet("Phát triển ứng dụng Desktop (JavaFX) phong cách Dark Mode hiện đại cho nghiệp vụ chuyên sâu và ứng dụng Mobile (Android Jetpack Compose) tiện lợi cho cấp quản lý theo dõi mọi lúc mọi nơi.", bold_prefix="Trải nghiệm đa nền tảng: ")

    add_h2("3. Nội dung và kế hoạch thực hiện")
    add_p("Đề tài được chia thành 5 giai đoạn thực hiện theo mô hình Agile / Scrum:")
    add_bullet("Giai đoạn 1: Khảo sát hiện trạng và thu thập yêu cầu: Khảo sát quy trình báo cáo tại Nhật Tri, phân tích các mẫu tệp Excel bán hàng, xác định các trường dữ liệu cốt lõi và tiêu chuẩn kỹ thuật.", level=0)
    add_bullet("Giai đoạn 2: Phân tích và thiết kế hệ thống: Xây dựng sơ đồ Use Case, xác định tác nhân, vẽ biểu đồ hoạt động, biểu đồ tuần tự, thiết kế Class Diagram và Cơ sở dữ liệu quan hệ MySQL.", level=0)
    add_bullet("Giai đoạn 3: Hiện thực hóa Backend và các thuật toán: Xây dựng RESTful API FastAPI, dịch vụ ETL Pandas, thuật toán Z-Score, mô hình Hồi quy Đa thức, công cụ lập lịch APScheduler và gửi mail SMTP.", level=0)
    add_bullet("Giai đoạn 4: Xây dựng ứng dụng Desktop và Android: Thiết kế giao diện JavaFX FXML phong cách Dark Theme và ứng dụng Mobile Kotlin Jetpack Compose kết nối API.", level=0)
    add_bullet("Giai đoạn 5: Kiểm thử và hoàn thiện báo cáo: Kiểm thử tích hợp đầu - cuối (E2E Testing), đo lường độ chính xác thuật toán và đóng gói tài liệu báo cáo.", level=0)

    add_h2("4. Bố cục báo cáo")
    add_p("Sau phần Mở đầu, cấu trúc báo cáo gồm 5 chương chính như sau:")
    add_bullet("Chương 1: Giới thiệu về Công ty TNHH Tự Động Hóa Nhật Tri", level=0)
    add_bullet("Chương 2: Tổng quan về dự án và cơ sở lý thuyết", level=0)
    add_bullet("Chương 3: Phân tích và thiết kế hệ thống", level=0)
    add_bullet("Chương 4: Triển khai và hiện thực hóa hệ thống", level=0)
    add_bullet("Chương 5: Kiểm thử và đánh giá hệ thống", level=0)
    add_bullet("Cuối cùng là phần Kết luận và Hướng phát triển, Tài liệu tham khảo.", level=0)

    doc.add_page_break()

    # ==========================================
    # 11. CHƯƠNG 1: GIỚI THIỆU VỀ CÔNG TY NHẬT TRI
    # ==========================================
    add_h1("CHƯƠNG 1: GIỚI THIỆU VỀ CÔNG TY TNHH TỰ ĐỘNG HÓA NHẬT TRI", centered=True)

    add_h2("1. Cơ quan thực tập")
    add_bullet(f"{STUDENT['company']}", bold_prefix="Tên cơ quan: ")
    add_bullet("156 Đinh Đức Thiện, phường Hòa Minh, quận Liên Chiểu, TP. Đà Nẵng", bold_prefix="Địa chỉ trụ sở: ")
    add_bullet("nhan.nguyendinh@nhattri.vn", bold_prefix="Email liên hệ: ")
    add_bullet("https://nhattri.vn", bold_prefix="Website chính thức: ")

    add_h2("2. Tổng quan về công ty")
    add_h3("2.1. Tổng quan")
    add_p(f"{STUDENT['company']} là một trong những doanh nghiệp kỹ thuật tiên phong tại miền Trung trong lĩnh vực tự động hóa công nghiệp và phát triển phần mềm quản lý kỹ thuật. Với sứ mệnh mang lại các giải pháp công nghệ tiên tiến, tối ưu hóa hiệu suất vận hành cho các nhà máy sản xuất, công ty cam kết cung cấp các sản phẩm và dịch vụ đạt chuẩn quốc tế, kiến tạo môi trường làm việc sáng tạo, chuyên nghiệp.")
    add_p("Các dịch vụ cốt lõi của công ty bao gồm:")
    add_bullet("Tư vấn, thiết kế và thi công hệ thống tự động hóa nhà xưởng.", level=0)
    add_bullet("Ứng dụng Robot công nghiệp và cánh tay cơ giới vào dây chuyền sản xuất.", level=0)
    add_bullet("Tích hợp giải pháp IoT giám sát thiết bị và phân tích dữ liệu từ xa.", level=0)
    add_bullet("Phát triển các phần mềm ứng dụng nội bộ, cổng web và giải pháp quản lý bán hàng cho doanh nghiệp.", level=0)

    add_h3("2.2. Quy mô nhân sự và nhu cầu quản trị dữ liệu")
    add_p("Quy mô nhân sự của công ty hiện tại gồm hơn 50 cán bộ nhân viên, bao gồm các kỹ sư phần cứng, kỹ sư điều khiển, kỹ sư phát triển phần mềm và chuyên viên phân tích hệ thống. Do tính chất công việc thường xuyên triển khai dự án tại nhiều địa bàn và cung cấp thiết bị cho nhiều đối tác lớn, lượng dữ liệu đơn hàng và doanh số phát sinh hàng ngày rất lớn.")
    add_p("Trước đây, các dữ liệu này được nhân viên quản lý phân tán qua các bảng tính Excel rời rạc. Điều này đòi hỏi công ty phải có một nền tảng đồng bộ dữ liệu tự động, tập trung hóa cơ sở dữ liệu để phục vụ cho công tác điều hành và báo cáo tài chính của Ban Giám đốc.")

    add_h3("2.3. Đối tác hợp tác tiêu biểu")
    add_p("Công ty TNHH Tự Động Hóa Nhật Tri là đối tác tin cậy của nhiều tập đoàn công nghiệp và doanh nghiệp lớn trong nước cũng như quốc tế, tiêu biểu như: ABB (Thụy Sĩ), Bumhan (Hàn Quốc), Universal Alloy Corporation (UAC Aerospace - Hoa Kỳ), Tập đoàn Điện lực Việt Nam (EVN), Makitech (Nhật Bản), Relats (Tây Ban Nha)...")

    add_fig_image("report_assets/fig_1_1_partners.png", "Hình 1.1. Đối tác hợp tác tiêu biểu của Công ty TNHH Tự Động Hóa Nhật Tri")

    add_h3("2.4. Các dự án tiêu biểu")
    add_p("Một số dự án tiêu biểu mang đậm dấu ấn công nghệ của Nhật Tri:")
    add_bullet("Dự án Cải tạo máy quấn dây cho Nhà máy Relats Việt Nam: Nâng cao năng suất quấn dây tự động, giảm thiểu tỷ lệ lỗi sản phẩm.", level=0)
    add_bullet("Dự án Tủ điều khiển xử lý nước thải giám sát qua Internet tại Nhà máy Toyota Trang Lê: Giám sát các chỉ số hóa lý nước thải theo thời gian thực qua Web và cảnh báo tự động.", level=0)

    add_fig_image("report_assets/fig_1_2_projects.png", "Hình 1.2. Các dự án công nghiệp tiêu biểu do Nhật Tri triển khai")

    add_h3("2.5. Định hướng và chiến lược kinh doanh")
    add_p("Trong định hướng chiến lược đến năm 2030, Nhật Tri hướng tới trở thành 'Doanh nghiệp công nghệ hàng đầu tại miền Trung trong lĩnh vực Tự động hóa và Phần mềm quản trị thông minh'. Trụ cột chiến lược của công ty tập trung vào:")
    add_bullet("Đẩy mạnh số hóa quy trình vận hành nội bộ (Internal Workflow Automation).", level=0)
    add_bullet("Xây dựng các giải pháp Dashboard phân tích kinh doanh thông minh (BI) hỗ trợ lãnh đạo ra quyết định nhanh chóng.", level=0)
    add_bullet("Đào tạo đội ngũ nhân sự chất lượng cao, tiếp cận các công nghệ phần mềm và khoa học dữ liệu hiện đại nhất.", level=0)

    doc.add_page_break()

    # ==========================================
    # 12. CHƯƠNG 2: TỔNG QUAN VỀ DỰ ÁN
    # ==========================================
    add_h1("CHƯƠNG 2: TỔNG QUAN VỀ DỰ ÁN", centered=True)

    add_h2("1. Tổng quan về đề tài")
    add_h3("1.1. Tên đề tài")
    add_p(f"“{PROJECT_TITLE} – {PROJECT_SUBTITLE}”")

    add_h3("1.2. Lý do chọn đề tài")
    add_bullet("Tại đơn vị thực tập, việc quản lý doanh số bán hàng và số lượng xuất nhập đang gặp trở ngại do dữ liệu lưu trữ rời rạc trên nhiều định dạng file Excel và Google Sheets từ các nguồn khác nhau.", level=0)
    add_bullet("Cấu trúc bảng tính giữa các tệp nguồn không đồng nhất, thường xuyên thiếu cột, sai lệch đơn giá hoặc trùng lặp mã đơn mà nhân viên khó kiểm soát thủ công.", level=0)
    add_bullet("Quy trình xuất báo cáo doanh thu cuối tháng đòi hỏi nhiều công đoạn tính toán thủ công, không có khả năng dự báo xu hướng và dễ bỏ lọt các ngày có doanh thu sụt giảm bất thường.", level=0)
    add_bullet("Cần một giải pháp đa nền tảng: Nhân viên và Quản lý làm việc trên máy tính bàn (Desktop JavaFX), trong khi cấp lãnh đạo có thể theo dõi nhanh số liệu trên thiết bị di động (Android App).", level=0)

    add_h3("1.3. Công cụ hỗ trợ phát triển")
    add_bullet("IntelliJ IDEA Ultimate & VS Code: Môi trường lập trình chuyên nghiệp cho JavaFX, Maven và Python Backend.", bold_prefix="IDE: ")
    add_bullet("Android Studio: Môi trường phát triển ứng dụng di động Kotlin Jetpack Compose.", bold_prefix="Mobile IDE: ")
    add_bullet("MySQL 8.0 & MySQL Workbench: Hệ quản trị cơ sở dữ liệu quan hệ và công cụ thiết kế ERD.", bold_prefix="Database: ")
    add_bullet("Postman / Swagger UI: Công cụ kiểm thử và tài liệu hóa RESTful API.", bold_prefix="API Tool: ")

    add_h2("2. Cơ sở lý thuyết và công nghệ sử dụng")
    add_h3("2.1. Ngôn ngữ Python và Framework FastAPI")
    add_p("FastAPI là framework web hiện đại, có tốc độ xử lý nhanh nhất hiện nay trong hệ sinh thái Python (tương đương NodeJS và Go). Được xây dựng dựa trên Starlette (xử lý bất đồng bộ ASGI) và Pydantic (xác thực dữ liệu chặt chẽ qua Data Schema). FastAPI tự động sinh tài liệu chuẩn OpenAPI (Swagger UI) tại đường dẫn `/docs`, hỗ trợ Dependency Injection mạnh mẽ và phù hợp tối đa cho các hệ thống xử lý dữ liệu và thuật toán.")

    add_h3("2.2. Ngôn ngữ Java và Nền tảng JavaFX 21")
    add_p("JavaFX là nền tảng giao diện đồ họa chuẩn của Java, cho phép xây dựng các ứng dụng Desktop hiện đại, hỗ trợ phân tách rõ ràng giữa giao diện (tệp tin XML dạng FXML), định dạng phong cách (CSS) và mã nguồn logic điều khiển (Controllers). JavaFX cung cấp hệ thống điều khiển bảng (TableView), biểu đồ (LineChart, BarChart) đa dạng, cùng khả năng xử lý bất đồng bộ đa luồng qua Platform.runLater giúp giao diện luôn mượt mà.")

    add_h3("2.3. Ngôn ngữ Kotlin và Android Jetpack Compose")
    add_p("Jetpack Compose là bộ công cụ UI khai báo (Declarative UI) hiện đại nhất của Google dành cho Android. Compose giúp giảm thiểu lượng mã boilerplate, tăng tốc độ render giao diện và dễ dàng tích hợp với kiến trúc MVVM, StateFlow, Coroutines để mang lại trải nghiệm mượt mà, phản hồi thời gian thực trên các thiết bị di động.")

    add_h3("2.4. Hệ quản trị CSDL MySQL và SQLAlchemy ORM")
    add_p("MySQL là hệ quản trị cơ sở dữ liệu quan hệ nguồn mở phổ biến hàng đầu thế giới với tốc độ truy vấn cao và tính ổn định tuyệt đối. Dự án kết hợp với SQLAlchemy - thư viện ORM hàng đầu của Python, giúp trừu tượng hóa các thao tác SQL thành các thực thể đối tượng (Python Class) và Alembic để quản lý các phiên bản migration CSDL một cách an toàn.")

    add_h3("2.5. Thư viện xử lý dữ liệu Pandas, NumPy và OpenPyXL")
    add_p("Pandas và NumPy là bộ đôi công cụ số một về xử lý dữ liệu dạng bảng và ma trận trong Python. Trong hệ thống, Pandas được ứng dụng để đọc dữ liệu thô từ Excel/CSV, thực hiện chuẩn hóa, tính toán chỉ số thống kê, lọc dữ liệu trùng lặp và tính đường trung bình động (Rolling Moving Average). OpenPyXL được sử dụng để lập trình sinh các tệp Excel báo cáo có định dạng chuyên nghiệp, tô màu tiêu đề và căn lề tự động.")

    add_h2("3. Các thuật toán và giải pháp kỹ thuật sử dụng")
    add_h3("3.1. Thuật toán tự động ánh xạ bí danh cột (Dynamic Alias Mapping)")
    add_p("Để giải quyết bài toán tên cột không đồng nhất giữa các tệp nguồn dữ liệu, hệ thống thiết kế thuật toán Dynamic Alias Mapping:")
    add_bullet("Định nghĩa danh mục các cột chuẩn bắt buộc: REQUIRED_COLUMNS = ['order_id', 'order_date', 'product_name', 'quantity', 'unit_price'].", level=0)
    add_bullet("Thiết lập từ điển bí danh (COLUMN_ALIASES) bao gồm các biến thể tiếng Việt có dấu, không dấu, viết tắt, tiếng Anh.", level=0)
    add_bullet("Khi nạp dữ liệu, thuật toán chuẩn hóa chuỗi tên cột (xóa khoảng trắng, đưa về chữ thường), tự động tìm kiếm cột tương ứng và đổi tên về cột chuẩn.", level=0)
    add_bullet("Tự động gán giá trị mặc định cho trường bị thiếu: quantity = 1 nếu bỏ trống; unit_price = 0 nếu là hàng khuyến mãi tặng kèm.", level=0)

    add_h3("3.2. Thuật toán kiểm tra toàn vẹn chéo (Cross-file Validation)")
    add_bullet("Phát hiện trùng lặp mã đơn giữa các tệp nguồn (Cross-file Duplicate): Khi nạp tệp đơn hàng mới, hệ thống kiểm tra nếu mã order_id đã từng được ghi nhận trong tệp dữ liệu trước đó hoặc đã tồn tại trong hệ thống thì đưa ra cảnh báo vi phạm tính toàn vẹn.", level=0)
    add_bullet("Phát hiện đột biến số lượng dòng hoặc doanh thu: So sánh số bản ghi và tổng doanh thu của đợt đồng bộ hiện tại so với lần đồng bộ trước đó. Nếu số dòng sụt giảm >50% (nguy cơ mất dữ liệu) hoặc tăng đột biến >100%, hệ thống sẽ lập tức gắn cờ cảnh báo.", level=0)

    add_h3("3.3. Thuật toán phát hiện ngoại lai (Outlier Detection) theo Z-Score")
    add_p("Nhằm ngăn chặn các lỗi nhập liệu như gõ nhầm đơn giá hoặc số lượng đột biến làm méo mó số liệu thống kê:")
    add_p("Hệ thống truy vấn lịch sử giao dịch của sản phẩm (chỉ xét sản phẩm có từ 10 bản ghi lịch sử trở lên: N >= 10), tính toán trung bình mẫu (Mean) và độ lệch chuẩn (StdDev):")
    add_p("     Mean = (1 / N) * Sum(x_i),       StdDev = Sqrt( (1 / (N - 1)) * Sum((x_i - Mean)^2) )")
    add_p("Với mỗi bản ghi mới nạp, tính giá trị Z-Score:")
    add_p("     Z = (x - Mean) / StdDev")
    add_p("Nếu |Z| > 3 (ngưỡng 3-sigma tương ứng với 99.7% độ tin cậy trong phân phối chuẩn), bản ghi được kết luận là ngoại lai (Outlier) bất thường và trả về cảnh báo chi tiết gồm mã đơn, giá trị thực tế và giá trị trung bình lịch sử.")

    add_h3("3.4. Mô hình Hồi quy Đa thức bậc 4 và Dải tin cậy ±2σ trên Desktop")
    add_p("Tại màn hình Dự báo nâng cao (Prediction Screen) trên Desktop JavaFX, hệ thống áp dụng mô hình Hồi quy Đa thức bậc 4 (Polynomial Regression Degree 4) để nắm bắt xu hướng phi tuyến của chuỗi thời gian doanh thu 90 ngày:")
    add_p("     y_pred(x) = b0 + b1*x + b2*x^2 + b3*x^3 + b4*x^4")
    add_p("Hệ thống giải hệ phương trình chuẩn X^T * X * B = X^T * Y bằng thuật toán Khử Gauss có chọn phần tử trội (Gaussian Elimination with Partial Pivoting).")
    add_p("Sau khi tìm được đường xu hướng y_pred, hệ thống tính độ lệch chuẩn sai số ước lượng:")
    add_p("     s = Sqrt( Sum( (y_i - y_pred_i)^2 ) / (N - 5) )")
    add_p("Thiết lập Dải tin cậy 95% gồm Cận trên: Upper = y_pred + 2s và Cận dưới: Lower = Max(0, y_pred - 2s). Bất kỳ ngày nào có doanh thu thực tế nằm ngoài dải tin cậy này sẽ được đánh dấu cảnh báo biến động đột biến.")

    add_fig_image("report_assets/fig_2_3_prediction_math.png", "Hình 2.3. Mô hình Hồi quy Đa thức bậc 4 và Dải tin cậy ±2σ phát hiện Ngoại lai")

    add_h3("3.5. Thuật toán phát hiện sụt giảm doanh thu tức thời theo khung giờ")
    add_p("Tác vụ ngầm định kỳ chạy lúc 9h, 12h, 15h, 18h mỗi ngày. Hệ thống tính tổng doanh thu ghi nhận từ 00:00 đến thời điểm hiện tại: R_today, đồng thời tính trung bình doanh thu cùng khung giờ của 7 ngày trước đó: R_past_avg.")
    add_p("Nếu R_past_avg > 0 và mức sụt giảm (R_past_avg - R_today) / R_past_avg > 0.3 (giảm hơn 30%), hệ thống sẽ tự động kích hoạt dịch vụ Email gửi cảnh báo khẩn cấp đến Quản trị viên và lưu vào bảng alert_history để tránh gửi trùng lặp.")

    add_h3("3.6. Dịch vụ lập lịch tự động (APScheduler) và Gửi email báo cáo")
    add_p("APScheduler (BackgroundScheduler) vận hành ngầm trên FastAPI Server. Mỗi ngày vào đúng 8h00 sáng, hệ thống tự động tổng hợp số liệu 7 ngày gần nhất, gọi OpenPyXL sinh file Excel có định dạng chuyên nghiệp gồm 2 Sheet ('Summary' và 'Top Products'), sau đó tự động đính kèm và gửi email đến ban quản trị qua giao thức SMTP.")

    add_h2("4. Quy trình phát triển phần mềm theo mô hình Scrum")
    add_p("Đồ án được triển khai theo phương pháp luận Agile / Scrum với các chu kỳ Sprint kéo dài 2 tuần. Nhóm thực hiện các buổi họp Daily Standup hàng ngày, Sprint Planning lên kế hoạch cho backlog và Sprint Review kiểm thử tính năng hoàn thành dưới sự hướng dẫn của cán bộ kỹ thuật Quách Thiện Đức.")

    add_h2("5. Tổng kết chương 2")
    add_p("Chương 2 đã trình bày tổng quan về đề tài, bối cảnh thực tiễn tại Công ty TNHH Tự Động Hóa Nhật Tri, các công nghệ nền tảng hiện đại (FastAPI, JavaFX, Jetpack Compose, MySQL, Pandas) cùng hệ thống thuật toán toán học - khoa học dữ liệu cốt lõi (Dynamic Alias Mapping, Z-Score Outlier, Polynomial Regression Bậc 4, Khử Gauss, Anomaly Hourly Check và APScheduler).")

    doc.add_page_break()

    # ==========================================
    # 13. CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG
    # ==========================================
    add_h1("CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG", centered=True)

    add_h2("1. Yêu cầu hệ thống và mô hình hóa yêu cầu")
    add_h3("1.1. Danh sách các tác nhân")

    tbl_actors_data = [
        ("1", "Admin (Quản trị viên)", "Quản lý toàn bộ người dùng, cấp quyền vai trò, cấu hình lịch trình tự động (Scheduler), xem toàn bộ dữ liệu phân tích hệ thống."),
        ("2", "Manager (Quản lý)", "Quản lý các nguồn dữ liệu, tải lên tệp Excel/CSV hoặc Google Sheets, kích hoạt đồng bộ hóa ETL, tạo và xem báo cáo kinh doanh đa kỳ, theo dõi dự báo doanh thu và sử dụng Trợ lý ảo."),
        ("3", "Employee (Nhân viên)", "Đăng nhập hệ thống, theo dõi bảng điều khiển tổng quan (Dashboard), kiểm tra trạng thái hoạt động của các nguồn dữ liệu và đổi mật khẩu cá nhân.")
    ]
    tbl_act = doc.add_table(rows=len(tbl_actors_data)+1, cols=3)
    tbl_act.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r in tbl_act.rows:
        r.cells[0].width = Inches(0.6)
        r.cells[1].width = Inches(2.0)
        r.cells[2].width = Inches(3.7)

    for i, h in enumerate(["STT", "Tác nhân", "Ý nghĩa và Quyền hạn"]):
        tbl_act.cell(0, i).paragraphs[0].text = h
        tbl_act.cell(0, i).paragraphs[0].runs[0].font.bold = True
        tbl_act.cell(0, i).paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_background(tbl_act.cell(0, i), "1E3A8A")

    for idx, (stt, act, mean) in enumerate(tbl_actors_data):
        tbl_act.cell(idx+1, 0).paragraphs[0].text = stt
        tbl_act.cell(idx+1, 1).paragraphs[0].text = act
        tbl_act.cell(idx+1, 1).paragraphs[0].runs[0].font.bold = True
        tbl_act.cell(idx+1, 2).paragraphs[0].text = mean
        for c_idx in range(3):
            set_cell_margins(tbl_act.cell(idx+1, c_idx))
            if idx % 2 == 1:
                set_cell_background(tbl_act.cell(idx+1, c_idx), "F8FAFC")

    add_p("Bảng 1: Danh sách các tác nhân tương tác với hệ thống", indent=0)

    add_h3("1.2. Yêu cầu chức năng của hệ thống")
    add_bullet("Đối với Quản trị viên (Admin):", bold_prefix="a) ")
    admin_funcs = [
        ("Quản lý người dùng", "Xem danh sách tài khoản, tạo tài khoản mới, cập nhật thông tin, phân vai trò (Admin, Manager, Employee) và Khóa/Mở khóa tài khoản."),
        ("Cấu hình Scheduler", "Thiết lập mốc giờ và phút chạy tác vụ tự động kết xuất báo cáo Excel và gửi email hàng ngày."),
        ("Báo cáo toàn hệ thống", "Xem dữ liệu phân tích tổng thể doanh thu, đơn hàng, biểu đồ tăng trưởng và xu hướng bán hàng.")
    ]
    for fn, desc in admin_funcs:
        add_bullet(f": {desc}", bold_prefix=fn, level=1)

    add_bullet("Đối với Quản lý (Manager):", bold_prefix="b) ")
    mgr_funcs = [
        ("Quản lý nguồn dữ liệu", "Tải lên tệp Excel/CSV, kết nối Google Sheets, xem danh sách và xóa nguồn dữ liệu."),
        ("Đồng bộ hóa dữ liệu", "Kích hoạt xử lý ETL, xem thông báo kết quả số dòng nạp thành công và danh sách cảnh báo Outlier (Z-Score)."),
        ("Tạo & Xem báo cáo", "Tạo báo cáo chi tiết theo Tháng, Quý, Năm hoặc Toàn thời gian; xem lại các báo cáo đã lưu trong lịch sử."),
        ("Dự báo nâng cao", "Xem biểu đồ Hồi quy Đa thức bậc 4, dải tin cậy 95% và danh sách các ngày có biến động doanh thu dị thường."),
        ("Trợ lý dữ liệu ảo", "Gửi các câu hỏi kinh doanh mẫu và nhận câu trả lời phân tích bằng ngôn ngữ tự nhiên kèm bảng số liệu.")
    ]
    for fn, desc in mgr_funcs:
        add_bullet(f": {desc}", bold_prefix=fn, level=1)

    add_bullet("Đối với Nhân viên (Employee):", bold_prefix="c) ")
    emp_funcs = [
        ("Đăng nhập & Đổi mật khẩu", "Xác thực danh tính an toàn và tự đổi mật khẩu cá nhân."),
        ("Theo dõi Dashboard", "Xem các chỉ số KPI cơ bản và theo dõi trạng thái đồng bộ của các nguồn dữ liệu.")
    ]
    for fn, desc in emp_funcs:
        add_bullet(f": {desc}", bold_prefix=fn, level=1)

    add_h3("1.3. Yêu cầu phi chức năng")
    add_bullet("Thời gian xử lý nạp tệp dữ liệu hàng chục nghìn dòng và tính toán phân tích không quá 3 giây. Thời gian phản hồi API trung bình dưới 500ms.", bold_prefix="Về hiệu năng: ")
    add_bullet("Bảo mật mật khẩu người dùng bằng giải thuật băm Bcrypt Salted; bảo vệ endpoint API bằng JWT Access Token; phân quyền RBAC chặt chẽ theo vai trò (Admin, Manager, Employee).", bold_prefix="Về bảo mật: ")
    add_bullet("Đảm bảo cơ chế Transaction trong SQLAlchemy, nếu quá trình ETL gặp lỗi ở giữa thì Rollback dữ liệu, không để dữ liệu rác tồn tại.", bold_prefix="Về độ tin cậy: ")
    add_bullet("Giao diện Desktop hiện đại với Dark Mode cao cấp; xử lý đa luồng ngầm tránh gây giật lag giao diện người dùng.", bold_prefix="Về trải nghiệm UX/UI: ")

    add_h3("1.4. Biểu đồ Use Case tổng quát")
    add_p("Dưới đây là sơ đồ ca sử dụng tổng quát thể hiện mối quan hệ giữa 3 tác nhân (Admin, Manager, Employee) với toàn bộ các phân hệ chức năng của hệ thống:")

    add_fig_image("report_assets/fig_3_usecase.png", "Hình 3. Biểu đồ Use Case tổng quát của hệ thống", width=Inches(6.2))

    add_h3("1.5. Đặc tả Use Case chi tiết")
    add_p("Dưới đây là bảng đặc tả chi tiết cho 2 Use Case cốt lõi nhất của hệ thống: Đăng nhập và Đồng bộ hóa dữ liệu ETL:")

    # UC Spec 1: Login
    tbl_uc1 = doc.add_table(rows=7, cols=2)
    tbl_uc1.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r in tbl_uc1.rows:
        r.cells[0].width = Inches(2.0)
        r.cells[1].width = Inches(4.3)

    uc1_data = [
        ("Tên Use Case", "Đăng nhập hệ thống (UC-AUTH-01)"),
        ("Tác nhân", "Admin, Manager, Employee"),
        ("Mô tả", "Cho phép người dùng đã được cấp tài khoản đăng nhập vào hệ thống để sử dụng các tính năng tương ứng với quyền hạn."),
        ("Điều kiện tiên quyết", "Người dùng đã có tài khoản và ở trạng thái hoạt động (is_active = True)."),
        ("Luồng sự kiện chính", "1. Người dùng mở ứng dụng, giao diện Đăng nhập hiển thị.\n2. Người dùng nhập Email và Mật khẩu, sau đó bấm nút 'Đăng nhập'.\n3. Client gửi POST /auth/login (form-urlencoded) đến FastAPI Server.\n4. Server truy vấn User theo email, so khớp mật khẩu bằng Bcrypt.\n5. Nếu chính xác, Server sinh JWT Access Token và trả về HTTP 200 kèm User Profile.\n6. Client lưu Token vào UserSession, điều hướng người dùng vào Dashboard tương ứng."),
        ("Luồng sự kiện phụ / Lỗi", "4a. Nếu email không tồn tại hoặc mật khẩu sai: Server trả lỗi HTTP 401 Unauthorized; Client hiển thị Alert 'Email hoặc mật khẩu không chính xác'.\n4b. Nếu tài khoản bị khóa (is_active = False): Server trả lỗi HTTP 403 Forbidden."),
        ("Kết quả sau cùng", "Người dùng đăng nhập thành công và truy cập vào không gian làm việc của mình.")
    ]
    for idx, (k, v) in enumerate(uc1_data):
        c0 = tbl_uc1.cell(idx, 0)
        p0 = c0.paragraphs[0]
        p0.text = k
        p0.runs[0].font.bold = True
        c1 = tbl_uc1.cell(idx, 1)
        p1 = c1.paragraphs[0]
        p1.text = v
        set_cell_margins(c0); set_cell_margins(c1)
        if idx == 0:
            set_cell_background(c0, "1E3A8A")
            c0.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
            set_cell_background(c1, "1E3A8A")
            c1.paragraphs[0].runs[0].font.bold = True
            c1.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        elif idx % 2 == 1:
            set_cell_background(c0, "F8FAFC")
            set_cell_background(c1, "F8FAFC")

    add_p("Bảng 5.1: Đặc tả Use Case 'Đăng nhập hệ thống'", indent=0)

    # UC Spec 2: Sync
    tbl_uc2 = doc.add_table(rows=7, cols=2)
    tbl_uc2.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r in tbl_uc2.rows:
        r.cells[0].width = Inches(2.0)
        r.cells[1].width = Inches(4.3)

    uc2_data = [
        ("Tên Use Case", "Đồng bộ hóa nguồn dữ liệu ETL (UC-DATA-03)"),
        ("Tác nhân", "Admin, Manager"),
        ("Mô tả", "Thực hiện đọc tệp dữ liệu bán hàng (Excel/CSV hoặc Google Sheets), tự động ánh xạ cột, làm sạch, kiểm tra ngoại lai Z-Score và nạp vào bảng NormalizedOrders."),
        ("Điều kiện tiên quyết", "Người dùng đã tải lên tệp hoặc thiết lập nguồn dữ liệu thành công."),
        ("Luồng sự kiện chính", "1. Người dùng chọn 1 nguồn dữ liệu trên TableView và bấm 'Đồng bộ ngay'.\n2. Desktop Client gửi yêu cầu POST /api/v1/data-sources/{id}/sync kèm JWT Token.\n3. Server đọc tệp tính qua Pandas, kích hoạt thuật toán Dynamic Alias Mapping.\n4. Thực hiện kiểm tra toàn vẹn chéo giữa các tệp (Cross-file Duplicate) và kiểm tra Outliers Z-Score.\n5. Thực hiện Transaction lưu hàng loạt các bản ghi đơn hàng chuẩn hóa vào bảng normalized_orders.\n6. Cập nhật trạng thái nguồn dữ liệu thành 'synced' kèm thời gian last_synced_at.\n7. Server trả về kết quả tổng số dòng nạp và danh sách các cảnh báo vi phạm.\n8. Client hiển thị hộp thoại thông báo thành công và danh sách Outliers phát hiện."),
        ("Luồng sự kiện phụ / Lỗi", "3a. Nếu tệp nguồn thiếu một trong các cột bắt buộc không thể map: Server cập nhật status='error', trả thông báo chi tiết danh sách cột thiếu; Client hiển thị lỗi vi phạm cấu trúc tệp."),
        ("Kết quả sau cùng", "Toàn bộ dữ liệu bán hàng được chuẩn hóa và lưu trữ an toàn trong MySQL Database.")
    ]
    for idx, (k, v) in enumerate(uc2_data):
        c0 = tbl_uc2.cell(idx, 0)
        p0 = c0.paragraphs[0]
        p0.text = k
        p0.runs[0].font.bold = True
        c1 = tbl_uc2.cell(idx, 1)
        p1 = c1.paragraphs[0]
        p1.text = v
        set_cell_margins(c0); set_cell_margins(c1)
        if idx == 0:
            set_cell_background(c0, "1E3A8A")
            c0.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
            set_cell_background(c1, "1E3A8A")
            c1.paragraphs[0].runs[0].font.bold = True
            c1.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        elif idx % 2 == 1:
            set_cell_background(c0, "F8FAFC")
            set_cell_background(c1, "F8FAFC")

    add_p("Bảng 5.2: Đặc tả Use Case 'Đồng bộ hóa nguồn dữ liệu'", indent=0)

    add_h2("2. Mô hình hóa hành vi")
    add_h3("2.1. Biểu đồ hoạt động (Activity Diagrams)")
    add_p("Biểu đồ hoạt động thể hiện trình tự các bước luồng công việc giữa Người dùng, Hệ thống xử lý và Cơ sở dữ liệu:")

    add_fig_image("report_assets/fig_4_1_act_login.png", "Hình 4.1. Biểu đồ hoạt động cho chức năng 'Đăng nhập'")
    add_fig_image("report_assets/fig_4_2_act_sync.png", "Hình 4.2. Biểu đồ hoạt động cho chức năng 'Đồng bộ hóa dữ liệu ETL'")
    add_fig_image("report_assets/fig_4_3_act_report.png", "Hình 4.3. Biểu đồ hoạt động cho chức năng 'Tạo và Xem Báo cáo'")

    add_h3("2.2. Biểu đồ tuần tự (Sequence Diagrams)")
    add_p("Biểu đồ tuần tự mô tả các thông điệp trao đổi giữa các thành phần phần mềm (UI Controller, FastAPI Router, Business Service và Database Layer) theo trục thời gian:")

    add_fig_image("report_assets/fig_5_1_seq_login.png", "Hình 5.1. Biểu đồ tuần tự cho chức năng 'Đăng nhập và xác thực JWT'")
    add_fig_image("report_assets/fig_5_2_seq_sync.png", "Hình 5.2. Biểu đồ tuần tự cho chức năng 'Kích hoạt Đồng bộ hóa dữ liệu'")

    add_h2("3. Mô hình hóa cấu trúc tĩnh (Class Diagram)")
    add_p("Biểu đồ lớp thực thể cốt lõi mô tả các đối tượng dữ liệu trong miền nghiệp vụ (Domain Entities) bao gồm User, DataSource, NormalizedOrder, Report, AlertHistory và AuditLog cùng các mối quan hệ sở hữu:")

    add_fig_image("report_assets/fig_6_class_diagram.png", "Hình 6. Biểu đồ Lớp Thực thể cốt lõi (Class Diagram / Domain Model)", width=Inches(6.2))

    add_h2("4. Thiết kế Cơ sở dữ liệu (Database Schema / ERD)")
    add_p("Cơ sở dữ liệu được chuẩn hóa ở dạng chuẩn 3NF, thiết lập các chỉ mục (Index) trên các cột thường xuyên lọc và tính toán (order_date, product_name) nhằm tối ưu tốc độ truy vấn:")

    add_fig_image("report_assets/fig_7_database_erd.png", "Hình 7. Sơ đồ Quan hệ Thực thể Cơ sở dữ liệu (Database Schema / ERD)", width=Inches(6.2))

    add_p("Chi tiết cấu trúc các trường trong bảng NormalizedOrders (bảng dữ liệu trọng tâm):")
    add_bullet("id: Khóa chính tự tăng (INT, Primary Key).", level=0)
    add_bullet("order_id: Mã đơn hàng chuẩn duy nhất (VARCHAR 100, Unique Index).", level=0)
    add_bullet("order_date: Ngày phát sinh đơn hàng (DATE, Index).", level=0)
    add_bullet("product_name: Tên mặt hàng sản phẩm (VARCHAR 255, Index).", level=0)
    add_bullet("quantity: Số lượng sản phẩm bán ra (FLOAT, >= 0).", level=0)
    add_bullet("unit_price: Đơn giá bán tại thời điểm giao dịch (FLOAT, >= 0).", level=0)
    add_bullet("total_amount: Thành tiền tính toán = quantity * unit_price (FLOAT).", level=0)
    add_bullet("customer_name: Tên đối tác/khách hàng mua hàng (VARCHAR 255, Nullable).", level=0)
    add_bullet("source_sheet: Tên trang tính hoặc sheet nguồn dữ liệu (VARCHAR 255, Nullable).", level=0)

    add_h2("5. Tổng kết chương 3")
    add_p("Chương 3 đã hoàn thành toàn diện việc phân tích và thiết kế hệ thống từ yêu cầu chức năng, phi chức năng, đặc tả Use Case, biểu đồ hoạt động, biểu đồ tuần tự, biểu đồ lớp đến lược đồ quan hệ thực thể cơ sở dữ liệu MySQL chuẩn mực.")

    doc.add_page_break()

    # ==========================================
    # 14. CHƯƠNG 4: TRIỂN KHAI VÀ HIỆN THỰC HÓA
    # ==========================================
    add_h1("CHƯƠNG 4: TRIỂN KHAI VÀ HIỆN THỰC HÓA HỆ THỐNG", centered=True)

    add_h2("1. Phân hệ Desktop Application (JavaFX 21)")
    add_p("Ứng dụng Desktop được xây dựng trên nền tảng JavaFX 21 với giao diện Dark Theme sang trọng, được thiết kế chuyên biệt cho nhân viên và quản lý vận hành văn phòng.")

    add_h3("1.1. Giao diện Đăng nhập hệ thống (Login Screen)")
    add_bullet("Tất cả người dùng (Admin, Manager, Employee)", bold_prefix="Đối tượng sử dụng: ")
    add_bullet("Cung cấp giao diện đồ họa phân chia 2 nửa: Banner đồ họa công nghệ bên trái và Khung nhập liệu email/password kèm nút Đăng nhập bên phải.", bold_prefix="Chức năng giao diện: ")
    add_bullet("Người dùng nhập email, mật khẩu; nhấn nút 'Đăng nhập'. Hệ thống gọi API POST /auth/login, nhận JWT token và điều hướng vào Dashboard.", bold_prefix="Các thao tác thực hiện: ")

    if os.path.exists("desktop-app/src/main/resources/images/banner.png"):
        add_fig_image("desktop-app/src/main/resources/images/banner.png", "Hình 8.1. Banner đồ họa và Giao diện Đăng nhập hệ thống (Desktop JavaFX)", width=Inches(5.5))

    add_h3("1.2. Giao diện Bảng điều khiển (Dashboard KPI Screen)")
    add_bullet("Admin, Manager, Employee", bold_prefix="Đối tượng sử dụng: ")
    add_bullet("Hiển thị 3 thẻ chỉ số KPI tổng quan (Tổng doanh thu, Tổng đơn hàng, Giá trị TB đơn AOV); Biểu đồ biến động doanh thu kết hợp đường trung bình động (Moving Average) và bảng Top 5 sản phẩm bán chạy nhất.", bold_prefix="Chức năng giao diện: ")
    add_bullet("Xem số liệu cập nhật tự động của toàn hệ thống theo tài khoản đang đăng nhập.", bold_prefix="Các thao tác thực hiện: ")

    add_fig_image("report_assets/fig_8_2_ui_dashboard.png", "Hình 8.2. Giao diện Bảng điều khiển tổng quan (Dashboard KPI & Moving Average)")

    add_h3("1.3. Giao diện Quản lý Nguồn dữ liệu (Data Source Screen)")
    add_bullet("Admin, Manager", bold_prefix="Đối tượng sử dụng: ")
    add_bullet("Hiển thị danh sách các nguồn dữ liệu đang kết nối với các badge trạng thái màu sắc: SYNCED (Xanh lá), ERROR (Đỏ), PENDING (Xám). Cung cấp nút Tải lên file Excel/CSV và Kết nối Google Sheets.", bold_prefix="Chức năng giao diện: ")
    add_bullet("Bấm 'Tải lên Excel/CSV' để chọn file từ máy tính; chọn dòng nguồn dữ liệu và bấm 'Đồng bộ ngay' để chạy ETL; bấm 'Xóa' để xóa nguồn dữ liệu.", bold_prefix="Các thao tác thực hiện: ")

    add_h3("1.4. Giao diện Dự báo Nâng cao và Cảnh báo Ngoại lai (Prediction Screen)")
    add_bullet("Admin, Manager", bold_prefix="Đối tượng sử dụng: ")
    add_bullet("Hiển thị mô hình Hồi quy Đa thức bậc 4 trên chuỗi dữ liệu 90 ngày với 4 đường đồ họa: Thực tế (Xanh lá), Xu hướng (Xanh dương), Cận trên (+2σ), Cận dưới (-2σ). Đồng thời hiển thị hộp thoại cảnh báo danh sách các ngày rơi ra ngoài dải tin cậy 95%.", bold_prefix="Chức năng giao diện: ")
    add_bullet("Rê chuột theo dõi biến động doanh thu từng ngày; đọc thông tin cảnh báo ngày nào có doanh số tăng hoặc giảm đột biến so với kỳ vọng.", bold_prefix="Các thao tác thực hiện: ")

    add_fig_image("report_assets/fig_2_3_prediction_math.png", "Hình 8.7. Giao diện Dự báo Hồi quy Đa thức & Cảnh báo Outliers")

    add_h3("1.5. Giao diện Trợ lý Dữ liệu ảo (Data Assistant Screen)")
    add_bullet("Tất cả người dùng", bold_prefix="Đối tượng sử dụng: ")
    add_bullet("Giao diện hỏi đáp kinh doanh thông minh với 5 câu hỏi nghiệp vụ thực tế được thiết kế sẵn (Doanh thu tháng này, Top sản phẩm bán chạy, Xu hướng dự báo, Nguồn dữ liệu lỗi, Cảnh báo dị thường gần đây).", bold_prefix="Chức năng giao diện: ")
    add_bullet("Nhấp chọn câu hỏi ở cột bên trái; hệ thống gọi API /insights/answer và hiển thị câu trả lời bằng ngôn ngữ tự nhiên cùng bảng số liệu minh họa ở khung bên phải.", bold_prefix="Các thao tác thực hiện: ")

    add_fig_image("report_assets/fig_8_8_ui_assistant.png", "Hình 8.8. Giao diện Trợ lý Dữ liệu ảo (Data Assistant)")

    add_h2("2. Phân hệ Mobile Application (Android Jetpack Compose)")
    add_p("Ứng dụng Android được phát triển bằng ngôn ngữ Kotlin theo chuẩn Material 3 hiện đại, đóng vai trò là giải pháp tra cứu dữ liệu di động tiện lợi cho cấp quản lý:")
    add_bullet("Đăng nhập và Quản lý phiên: Lưu JWT Token trong SharedPreferences ở chế độ bảo mật riêng tư (MODE_PRIVATE), tự động phục hồi phiên đăng nhập khi mở ứng dụng.", level=0)
    add_bullet("Dashboard giám sát: Hiển thị thông tin người dùng, vai trò phụ trách và các chỉ dẫn thao tác nhanh.", level=0)
    add_bullet("Quản lý nguồn dữ liệu: Cho phép theo dõi trạng thái các nguồn dữ liệu và kích hoạt đồng bộ hóa từ xa.", level=0)
    add_bullet("Lịch sử báo cáo: Tra cứu nhanh các báo cáo doanh thu đã được hệ thống kết xuất theo thời gian thực.", level=0)

    add_h2("3. Phân hệ Dịch vụ tự động hóa ngầm (Backend Automation Services)")
    add_p("Vận hành tự động hoàn toàn thông qua bộ lập lịch APScheduler ngầm trên FastAPI Server:")
    add_bullet("Dịch vụ xuất Excel định dạng chuẩn (OpenPyXL): Tự động tạo tệp với bảng màu chuyên nghiệp (#1F4E78), căn lề và định dạng số tiền VND tự động.", bold_prefix="Tác vụ 8h00 sáng: ")
    add_bullet("Dịch vụ gửi Email tự động: Tự động đính kèm file Excel vừa xuất và gửi đến hòm thư Ban Giám đốc.", bold_prefix="Tác vụ gửi Mail: ")
    add_bullet("Dịch vụ giám sát sụt giảm doanh thu: Chạy vào các khung giờ 9h, 12h, 15h, 18h mỗi ngày để kịp thời cảnh báo khi doanh thu giảm >30% so với trung bình 7 ngày trước trong cùng khung giờ.", bold_prefix="Tác vụ kiểm tra Anomaly: ")

    add_h2("4. Tổng kết chương 4")
    add_p("Chương 4 đã trình bày chi tiết về kết quả triển khai toàn diện của hệ thống trên cả 3 phân hệ: Desktop JavaFX, Mobile Android Jetpack Compose và Dịch vụ tự động hóa ngầm Backend.")

    doc.add_page_break()

    # ==========================================
    # 15. CHƯƠNG 5: KIỂM THỬ VÀ ĐÁNH GIÁ
    # ==========================================
    add_h1("CHƯƠNG 5: KIỂM THỬ VÀ ĐÁNH GIÁ HỆ THỐNG", centered=True)

    add_h2("1. Kế hoạch và phương pháp kiểm thử")
    add_p("Hệ thống được tiến hành kiểm thử toàn diện qua 3 giai đoạn:")
    add_bullet("Kiểm thử đơn vị (Unit Testing): Kiểm thử các module độc lập như thuật toán Alias Mapping, hàm tính Z-Score, giải thuật khử Gauss.", level=0)
    add_bullet("Kiểm thử tích hợp (Integration Testing): Kiểm thử giao tiếp giữa FastAPI với CSDL MySQL và các cổng ngoại vi (Google Sheets, SMTP).", level=0)
    add_bullet("Kiểm thử đầu - cuối (End-to-End Testing): Thực hiện trực tiếp trên giao diện Desktop và Backend với các bộ dữ liệu bán hàng thực tế 3 tháng (orders_3months.csv).", level=0)

    add_h2("2. Bảng các kịch bản kiểm thử End-to-End thực tế")

    test_cases_data = [
        ("TC-01", "Đăng nhập tài khoản hợp lệ", "Email: admin@company.com\nPass: 123456", "Trả về HTTP 200, JWT token, giao diện Desktop chuyển sang Dashboard chính", "PASS"),
        ("TC-02", "Đăng nhập sai mật khẩu", "Email: admin@company.com\nPass: sai_pass", "Trả về HTTP 401, hiển thị thông báo lỗi trên giao diện", "PASS"),
        ("TC-03", "Nạp file Excel bị lệch tên cột", "File có cột: 'Mã ĐH', 'Ngày', 'Tên SP', 'SL', 'Giá bán'", "Thuật toán Alias Mapping tự động nhận diện và đổi về cột chuẩn, nạp 100% bản ghi", "PASS"),
        ("TC-04", "Phát hiện ngoại lai Z-Score", "Bản ghi có đơn giá 50.000.000 đ (TB lịch sử: 5.000.000 đ)", "Hệ thống nạp dữ liệu và gắn cảnh báo Outlier (Z > 3) chi tiết mã đơn trên giao diện", "PASS"),
        ("TC-05", "Kiểm tra trùng lặp mã đơn giữa các tệp", "Nạp tệp mới chứa order_id đã tồn tại trong cơ sở dữ liệu", "Hệ thống phát hiện vi phạm toàn vẹn và thông báo cảnh báo trùng lặp mã đơn hàng", "PASS"),
        ("TC-06", "Tạo và lưu trữ báo cáo tháng", "Chọn kỳ 'Theo tháng', nhập '08/2026'", "Tính toán chính xác tổng doanh thu, tỷ lệ tăng trưởng %, lưu JSON vào DB và vẽ biểu đồ", "PASS"),
        ("TC-07", "Dự báo Hồi quy Đa thức bậc 4", "Nạp chuỗi dữ liệu doanh thu 90 ngày trên Desktop", "Vẽ mượt mà 4 đường (Thực tế, Xu hướng, Cận trên, Cận dưới) và trích xuất đúng ngày bất thường", "PASS"),
        ("TC-08", "Truy vấn Trợ lý Dữ liệu ảo", "Chọn câu hỏi: 'Sản phẩm nào bán chạy nhất tháng này?'", "Phản hồi câu trả lời tự nhiên kèm bảng số liệu Top 5 sản phẩm bán chạy nhất thời gian thực", "PASS"),
        ("TC-09", "Tác vụ tự động xuất Excel & Mail", "Scheduler kích hoạt lúc 8h00", "Tạo file Excel định dạng đẹp và gửi đính kèm thành công tới hòm thư quản trị viên", "PASS")
    ]

    tbl_tests = doc.add_table(rows=len(test_cases_data)+1, cols=5)
    tbl_tests.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r in tbl_tests.rows:
        r.cells[0].width = Inches(0.8)
        r.cells[1].width = Inches(1.8)
        r.cells[2].width = Inches(1.8)
        r.cells[3].width = Inches(1.8)
        r.cells[4].width = Inches(0.7)

    headers_tc = ["Mã TC", "Tên kịch bản", "Dữ liệu đầu vào", "Kết quả kỳ vọng", "Kết quả"]
    for i, h in enumerate(headers_tc):
        c = tbl_tests.cell(0, i)
        c.paragraphs[0].text = h
        c.paragraphs[0].runs[0].font.bold = True
        c.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_background(c, "1E3A8A")

    for idx, (tc_id, tc_name, tc_in, tc_exp, tc_res) in enumerate(test_cases_data):
        tbl_tests.cell(idx+1, 0).paragraphs[0].text = tc_id
        tbl_tests.cell(idx+1, 0).paragraphs[0].runs[0].font.bold = True
        tbl_tests.cell(idx+1, 1).paragraphs[0].text = tc_name
        tbl_tests.cell(idx+1, 2).paragraphs[0].text = tc_in
        tbl_tests.cell(idx+1, 3).paragraphs[0].text = tc_exp
        
        c_res = tbl_tests.cell(idx+1, 4)
        c_res.paragraphs[0].text = tc_res
        c_res.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        c_res.paragraphs[0].runs[0].font.bold = True
        c_res.paragraphs[0].runs[0].font.color.rgb = RGBColor(16, 185, 129) # Green

        for c_idx in range(5):
            set_cell_margins(tbl_tests.cell(idx+1, c_idx))
            if idx % 2 == 1:
                set_cell_background(tbl_tests.cell(idx+1, c_idx), "F8FAFC")

    add_p("Bảng 8: Kịch bản kiểm thử tích hợp đầu - cuối (End-to-End Test Cases)", indent=0)

    add_h2("3. Đánh giá kết quả kiểm thử")
    add_p("Toàn bộ 9 kịch bản kiểm thử chính đều đạt kết quả PASS (100%), hệ thống hoạt động ổn định, dữ liệu đồng bộ chính xác và không có hiện tượng xung đột dữ liệu hay rò rỉ bộ nhớ.")

    doc.add_page_break()

    # ==========================================
    # 16. KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN
    # ==========================================
    add_h1("KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN", centered=True)

    add_p("Sau quá trình tìm hiểu, nghiên cứu và trực tiếp phát triển tại Công ty TNHH Tự Động Hóa Nhật Tri, đề tài 'Xây Dựng Hệ Thống Tự Động Hóa Quy Trình Đồng Bộ Dữ Liệu, Báo Cáo Và Dự Báo Đa Nền Tảng' đã hoàn thành toàn diện các mục tiêu đề ra đúng thời hạn quy định.")

    add_h2("1. Kết quả đạt được")
    add_bullet("Về mặt lý thuyết:", bold_prefix="a) ")
    add_bullet("Nắm vững kiến thức chuyên sâu về thiết kế kiến trúc phần mềm phân tán đa nền tảng (3-Tier Architecture) kết hợp RESTful API.", level=1)
    add_bullet("Làm chủ các thuật toán toán học thống kê và khoa học dữ liệu ứng dụng: chuẩn hóa Z-Score phát hiện ngoại lai, mô hình Hồi quy Đa thức bậc 4 giải bằng thuật toán Khử Gauss với dải tin cậy ±2σ.", level=1)
    add_bullet("Hiểu rõ quy trình phát triển phần mềm chuẩn công nghiệp theo mô hình Scrum/Agile trong môi trường doanh nghiệp thực tế.", level=1)

    add_bullet("Về mặt thực nghiệm:", bold_prefix="b) ")
    add_bullet("Xây dựng hoàn chỉnh hệ sinh thái gồm: Backend FastAPI (Python), Desktop App (JavaFX 21) và Mobile App (Android Jetpack Compose).", level=1)
    add_bullet("Giải quyết triệt để vấn đề sai lệch dữ liệu phân tán bằng cơ chế ETL Dynamic Alias Mapping và Cross-file Duplicate Check.", level=1)
    add_bullet("Tự động hóa hoàn toàn quy quy trình lập báo cáo Excel và gửi email hàng ngày lúc 8h00 sáng, đồng thời giám sát sụt giảm doanh thu tức thời qua APScheduler.", level=1)
    add_bullet("Xây dựng thành công Trợ lý Dữ liệu ảo (Data Assistant) giúp tối ưu hóa việc truy vấn số liệu kinh doanh cho người dùng.", level=1)

    add_h2("2. Hạn chế và hướng phát triển")
    add_bullet("Hạn chế hiện tại:", bold_prefix="a) ")
    add_bullet("Mô hình Hồi quy Đa thức hiện tại chủ yếu nắm bắt xu hướng tổng thể theo chuỗi thời gian, chưa xử lý được các biến số ngoại sinh phức tạp (như lễ tết, sự kiện khuyến mại đột biến).", level=1)
    add_bullet("Hệ thống mới hỗ trợ nguồn dữ liệu từ tệp Excel/CSV và Google Sheets, chưa tích hợp kết nối Webhook trực tiếp từ các sàn thương mại điện tử.", level=1)

    add_bullet("Hướng phát triển trong tương lai:", bold_prefix="b) ")
    add_bullet("Tích hợp Trí tuệ nhân tạo tạo sinh (GenAI / Large Language Models) qua Gemini API: Cho phép Trợ lý ảo trả lời câu hỏi tự do bằng ngôn ngữ tự nhiên thông qua kỹ thuật Text-to-SQL.", level=1)
    add_bullet("Nâng cấp mô hình dự báo chuỗi thời gian: Áp dụng các mô hình học máy nâng cao như Prophet hoặc mạng nơ-ron hồi quy LSTM để tăng độ chính xác dự báo theo tính chu kỳ mùa vụ.", level=1)
    add_bullet("Mở rộng cổng kết nối Webhook API đồng bộ trực tiếp với các phần mềm bán hàng POS phổ biến (KiotViet, Sapo, Haravan).", level=1)

    doc.add_page_break()

    # ==========================================
    # 17. TÀI LIỆU THAM KHẢO
    # ==========================================
    add_h1("TÀI LIỆU THAM KHẢO", centered=True)

    references = [
        "Tiêu chuẩn xây dựng RESTful API với FastAPI Framework, Tài liệu chính thức: https://fastapi.tiangolo.com/",
        "Lập trình giao diện Desktop hiện đại với JavaFX 21 và FXML, OpenJFX Documentation: https://openjfx.io/",
        "Phát triển ứng dụng Android hiện đại với Jetpack Compose và Material Design 3, Google Developer: https://developer.android.com/jetpack/compose",
        "Xử lý và phân tích dữ liệu dạng bảng với thư viện Pandas và NumPy, https://pandas.pydata.org/",
        "Tự động hóa thao tác và định dạng tệp bảng tính với OpenPyXL: https://openpyxl.readthedocs.io/",
        "Cơ sở dữ liệu quan hệ và ORM với SQLAlchemy & Alembic: https://www.sqlalchemy.org/",
        "Tự động hóa tác vụ ngầm trong Python với APScheduler: https://apscheduler.readthedocs.io/",
        "Mô hình hóa hệ thống phần mềm với Unified Modeling Language (UML) - Sách giáo trình phân tích thiết kế hệ thống thông tin, NXB Khoa học và Kỹ thuật.",
        "Quy trình phát triển phần mềm linh hoạt theo hướng dẫn Scrum Guide: https://scrumguides.org/",
        "Giới thiệu và hồ sơ năng lực Công ty TNHH Tự Động Hóa Nhật Tri: https://nhattri.vn/"
    ]
    for i, ref in enumerate(references, 1):
        add_p(ref, bold_prefix=f"{i}. ", indent=0)

    # Output file path
    output_path = "d:\\DoAn\\DoAnThucTapThucTe\\BaoCao_ThucTapThucTe_HeThongTuDongHoaBaoCao.docx"
    doc.save(output_path)
    print("SUCCESS: File saved at: " + output_path)

if __name__ == "__main__":
    create_report_word()
