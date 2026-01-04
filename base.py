import os
import math
import time
import struct



#把整数保存到至bin文件
def save_int_list_to_bin(int_list,path,append=False):
    mode = 'ab' if append else 'wb' #根据append 来追加还是重写
    with open(path,mode) as f:
        pack_data = struct.pack(f'>{len(int_list)}I', *int_list)
        f.write(pack_data)

#把存到bin里的整数提取出来
def load_int_list_from_bin(path,length = None):
    int_list = []
    if not os.path.isfile(path):
        return int_list  # 文件不存在返回空列表
    with open(path, 'rb') as f:
        all_data = f.read()  # 一次性读全部字节
        num_count = len(all_data) // 4  # 计算有多少个4字节整数
        if num_count == 0:
            return int_list

        unpack_data = struct.unpack(f'>{num_count}I', all_data)
        int_list = list(unpack_data)  # 元组转列表
        if length and len(int_list) > length:
            int_list = int_list[:length]
    return int_list

#把bool的list保存至bin文件
def save_bool_list_to_bin(bool_list, path,append=False):
    mode = 'ab' if append else 'wb'
    with open(path, mode) as f:
        # 布尔转字节数组，批量写
        byte_data = bytes([1 if b_val else 0 for b_val in bool_list])
        f.write(byte_data)

#把保存到bin的bool的list提取出来
def load_bool_list_from_bin(path, length=None):
    bool_list = []
    if not os.path.isfile(path):
        return bool_list
    with open(path, 'rb') as f:
        all_data = f.read()
        bool_list = [b == 1 for b in all_data]
        if length and len(bool_list) > length:
            bool_list = bool_list[:length]
    return bool_list



#用欧拉筛得到素数
def get_prime(max_num:int,prime_list =None,is_prime = None):
    #假如是第一次计算没有保存则建立列表
    if prime_list is None:
        prime_list = []
    if is_prime is None:
        is_prime = []

    if len(prime_list) == 0: #判断是不是第一次计算素数
        begin = 2 #从下标2开始
        is_prime = [True] * (max_num + 1)
        is_prime[0] = is_prime[1] = False
    else:
        begin = max(prime_list) + 1 #从下标 max(prime_list) + 1开始

        if len(is_prime) < max_num + 1: #假如计算中的len小于max_num
            extend_len = max_num + 1 - len(is_prime)
            is_prime += [True] * extend_len

    for num in range(begin,max_num+1):
        if is_prime[num]:
            prime_list.append(num) #未被标记的是素数

        for i in prime_list:
            produce = i * num
            if produce > max_num:
                break           #超出范围停止
            is_prime[produce] = False #标记为不是素数

            if num % i == 0:
                break

    return prime_list,is_prime


#得到保存的素数
def get_save_prime(maxnum = 10000):
    primes_bin_path = "primes.bin"
    is_prime_bin_path = "is_prime.bin"

    if os.path.isfile(primes_bin_path) and os.path.isfile(is_prime_bin_path):

        #将已保存的提取出来
        primes = load_int_list_from_bin(primes_bin_path)

        is_prime = load_bool_list_from_bin(is_prime_bin_path,maxnum+1)

        primes_len = len(primes)
        is_prime_len = len(is_prime)
        if is_prime_len < maxnum + 1:

            primes, is_prime = get_prime(maxnum, primes, is_prime)

            new_primes = primes[primes_len:]  # 新增的素数
            new_is_prime = is_prime[is_prime_len:]  # 新增的布尔值

            save_int_list_to_bin(new_primes, primes_bin_path,append = True)
            save_bool_list_to_bin(new_is_prime, is_prime_bin_path,append = True)

    else:
        primes, is_prime = get_prime(maxnum)  # 把保存的素数以及素数的大小
        save_int_list_to_bin(primes,primes_bin_path)
        save_bool_list_to_bin(is_prime,is_prime_bin_path)

    return primes,is_prime


#提取出素数平方根的小数部分的32位
def extract_decimals_bytes(length:int):
    extract_bin_path = 'extract_list.bin'

    #如果已经有保存的文件就把已经保存的提取出来
    if os.path.isfile(extract_bin_path):

        extract_32_list = load_int_list_from_bin(extract_bin_path)
        list_num = len(extract_32_list)
        # 如果保存的个数小于需求个数则要计算新的
        if list_num < length:
            primes, is_prime = get_save_prime()

            primes_num = len(primes)
            judged_num = len(is_prime) - 1
            # 假如要求的个数没到需要的就会不断循环计算素数直到 素数个数到了要求的个数
            expand = 1000  # 一次计算步长为1000
            while length > primes_num:
                judged_num += expand
                primes = get_save_prime(judged_num)[0]
                primes_num = len(primes)

            # 仅计算[list_num, length)区间的素数
            extra_primes = primes[list_num:length]
            extra = []
            for p in extra_primes:
                sqrt_num = math.sqrt(p)
                frac_part = sqrt_num - int(sqrt_num)
                extract_32 = int(frac_part * (2 ** 32))
                extra.append(extract_32)

            extract_32_list += extra

            save_int_list_to_bin(extra,extract_bin_path,append = True)
    else:
        #没保存文件时 先生成足够的素数
        init_maxnum = length * 20
        primes = get_save_prime(init_maxnum)[0]
        primes = primes[:length]
        extract_32_list = []
        for i in primes:
            sqrt_num = math.sqrt(i)
            frac_part = sqrt_num - int(sqrt_num)
            extract_32 = int(frac_part * (2 ** 32))  # 提取出的小数32位
            extract_32_list.append(extract_32)

        save_int_list_to_bin(extract_32_list,extract_bin_path)

    return extract_32_list


if __name__ == "__main__":
    # 测试os.path.isfile耗时
    start = time.perf_counter()
    a = extract_decimals_bytes(1000)
    end = time.perf_counter()
    print(f"os.path.isfile (第一次)耗时：{(end - start) * 1e6:.2f}μs")

    # 测试os.path.isfile耗时
    start = time.perf_counter()
    a = extract_decimals_bytes(1000)
    end = time.perf_counter()
    print(f"os.path.isfile（第二次）耗时：{(end - start) * 1e6:.2f}μs")


