import requests
import time
from pathlib import Path

def print_to_file_and_console(*args, file_path='log.txt', **kwargs):
    # 打开文件用于追加内容
    with open(file_path, 'a', encoding='utf-8') as f:
        # 先将内容输出到文件
        print(*args, file=f, **kwargs)
        # 再将内容输出到控制台
        print(*args, **kwargs)

def download(id):
    # 错误码
    error_code = 0 # success
    # 下载链接
    # download_url = f'https://dl.wenku8.com/down.php?type=txt&node=1&id={id}'
    download_url = f'https://dl.wenku8.com/down.php?type=utf8&node=1&id={id}'
    print_to_file_and_console(f'{id}: 下载链接 {download_url}')

    # 设置请求头，模拟浏览器访问
    #  headers = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    headers = {
        'User-Agent': 'MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1'}

    try:
        # 发送 GET 请求
        # 设置超时时间 15 秒
        response = requests.get(download_url, headers=headers, timeout=15)
        # 检查响应状态码
        response.raise_for_status()

        # 提取文件名
        file_name = f'{id}.txt'
        print_to_file_and_console(f'{id}: 文件名 {file_name}')

        # 保存文件
        with open(file_name, 'wb') as file:
            file.write(response.content)
        print_to_file_and_console(f'{id}: 小说已成功下载到 {file_name}')
        # 返回错误码
        return error_code

    except requests.exceptions.Timeout:
        print_to_file_and_console(f'{id}: !!!超时错误发生: 请求超时')
        error_code =  3 # Timeout，需要重试
        # 返回错误码
        return error_code
    except requests.exceptions.HTTPError as http_err:
        print_to_file_and_console(f'{id}: !!!HTTP 错误发生: {http_err}')
        http_err_str = str(http_err)
        if http_err_str.startswith('404'):
            print_to_file_and_console(f'{id}: !!!文件不存在')
            error_code =  1 # Not Found，不用重试
        elif http_err_str.startswith('429'):
            print_to_file_and_console(f"{id}: !!!请求过多，需要重试")
            error_code = 2 # Too Many Requests，需要重试
        else:
            error_code = 5 # 其他错误
        # 返回错误码
        return error_code
    except Exception as err:
        print_to_file_and_console(f'{id}: !!!其他错误发生: {err}')
        err_str = str(err)
        if 'HTTPSConnectionPool' in err_str:
            if 'Read timed out' in err_str:
                error_code = 3 # Timeout，超时，需要重试
            elif 'Max retries exceeded' in err_str:
                error_code = 4 # Max retries exceeded, 超过最大重试次数，需要重试
            else:
                error_code = 5 # 其他错误
        else:
            error_code = 5 # 其他错误
        # 返回错误码
        return error_code

# 记录开始时间
start_time = time.time()

# 起始的 id 编号
start_id = 1
# 循环次数 3863
loop_count = 4000
# 清空日志
with open('log.txt', 'w', encoding='utf-8') as f:
    pass

for i in range(loop_count):
    file_id = i + start_id
    print_to_file_and_console(f'{file_id}: ————————————————————开始————————————————————')
    # 下载
    ret = download(file_id)
    #出错
    if ret == 2 or ret == 3 or ret == 4:
        # 最大重试 3 次
        for j in range(3):
            print_to_file_and_console(f'{file_id}: ——————第{j+1}次重试——————')
            time.sleep(10)
            # 重试下载
            ret = download(file_id)
            # 成功或者文件不存在
            if ret == 0 or ret == 1:
                break
            # 重试次数用完
            if j == 2:
                print_to_file_and_console(f'{file_id}: ###文件{file_id}下载重试超过最大次数###')
    
    file_path = Path(f'{file_id}.txt')
    if file_path.is_file(): # 本地文件存在
        print_to_file_and_console(f'{file_id}: ————————————————————成功————————————————————\n\n')
    elif ret == 1: # 本地文件不存在，远程文件也不存在
        print_to_file_and_console(f'{file_id}: ————————————————————不存在————————————————————\n\n')
    else: # 本地文件不存在，错误码为失败
        print_to_file_and_console(f'{file_id}: ————————————————————失败————————————————————\n\n')

# 记录结束时间
end_time = time.time()

# 计算运行时间
run_time = end_time - start_time
print(f"程序运行时间: {int(run_time)} 秒")
