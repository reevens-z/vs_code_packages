import fitz  # PyMuPDF
from PIL import Image
import os
import io

def process_pdf(pdf_path, output_dir):
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 打开PDF文档
    doc = fitz.open(pdf_path)
    
    # 遍历每一页
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        print(f"Processing page {page_num+1}...")
        
        # 1. 提取图片并保存
        image_list = page.get_images(full=True)
        for img_idx, img in enumerate(image_list):
            xref = img[0]  # 图片xref编号
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            
            # 保存图片
            img_path = f"{output_dir}/page{page_num+1}_img{img_idx}.png"
            with open(img_path, "wb") as f:
                f.write(image_bytes)
            print(f"Saved image: {img_path}")
        
        # 2. 定位表格区域
        blocks = page.get_text("blocks")  # 获取所有文本块
        tables = []
        for block in blocks:
            x0, y0, x1, y1, text, block_type = block
            if block_type == 1:  # 图片块
                continue
            if is_table_block(block):  # 自定义表格识别逻辑
                tables.append((x0, y0, x1, y1))
        
        # 3. 提取纯文本（排除表格/图片区域）
        text = page.get_text()
        clean_text = remove_blocks_from_text(text, tables)
        text_path = f"{output_dir}/page{page_num+1}.txt"
        with open(text_path, "w", encoding="utf-8") as f:
            f.write(clean_text)
        print(f"Saved text: {text_path}")
    
    doc.close()

def is_table_block(block):
    """通过文本密度判断是否为表格"""
    x0, y0, x1, y1, text, _ = block
    words = text.split()
    if len(words) < 3:  # 单元格通常包含多个单词
        return False
    # 计算文本密度（字符数/区域面积）
    area = (x1 - x0) * (y1 - y0)
    char_density = len(text) / area
    return char_density > 0.5  # 阈值可调整

def remove_blocks_from_text(text, blocks):
    """根据区域坐标过滤文本"""
    lines = text.split("\n")
    filtered_lines = []
    for line in lines:
        line_y = get_line_y(line)  # 需实现行坐标检测
        if not is_line_in_blocks(line_y, blocks):
            filtered_lines.append(line)
    return "\n".join(filtered_lines)

# 示例调用
process_pdf("input.pdf", "output")