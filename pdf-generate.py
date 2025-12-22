import os
def generate_100mb_pdf(file_path):
    # 100MB换算为字节数
    file_size_bytes = 1024 * 1024 * 100
    with open(file_path, 'wb') as file:
        file.write(os.urandom(file_size_bytes))
    print(f"100MB的PDF文件已生成至：{file_path}")
if __name__ == '__main__':
    # 可修改为自己想要的保存路径，如'D:\\test.pdf'
    generate_100mb_pdf('test.pdf')
