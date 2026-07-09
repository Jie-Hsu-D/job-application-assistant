from pypdf import PdfReader

# 读取 PDF 文件
reader = PdfReader("resume.pdf")

# PDF 是分页的，逐页把文字提取出来、拼在一起
full_text = ""
for page in reader.pages:
    full_text += page.extract_text() + "\n"

# 打印出来看看提取的效果
print(full_text)