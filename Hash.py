import struct
import time


import base

min_num = 10000

class Hash:
    def __init__(self,code_list,message_byte):
        self.message_byte = message_byte
        self.code = code_list
        code_length = len(self.code)
        #if语句防止计算的素数个数不够   如果不够置0
        self.h0 = self.code[0] if code_length >= 1 else 0
        self.h1 = self.code[1] if code_length >= 2 else 0
        self.h2 = self.code[2] if code_length >= 3 else 0
        self.h3 = self.code[3] if code_length >= 4 else 0
        self.h4 = self.code[4] if code_length >= 5 else 0
        self.h5 = self.code[5] if code_length >= 6 else 0
        self.h6 = self.code[6] if code_length >= 7 else 0
        self.h7 = self.code[7] if code_length >= 8 else 0
        self.k = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
    0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
    0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
    0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
    0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
    0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
    0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
    0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
]#这里利用了sha256中的固定常量K

    def padding(self, goal_length):
        length = len(self.message_byte) * 8
        pad_length = length & 0xffffffffffffffff
        self.message_byte += b'\x80'  # 加0x80
        new_length = length + 8  # 已填充8位
        # 计算需要填充的0字节数（单位：字节）
        zero_bytes = (goal_length - new_length) // 8
        self.message_byte += b'\x00' * zero_bytes  # 一次性填充
        # 追加长度
        self.message_byte += struct.pack('>Q', pad_length)
        return self.message_byte

    #F,G,H,I 函数分别参与4次16轮迭代的临时值
    #F(x,y,z) = x^y + y^(~z)
    def F(self, x: int, y: int, z: int):
        x &= 0xffffffff
        y &= 0xffffffff
        z &= 0xffffffff
        return ((x ^ y) + (y ^ ((~z) & 0xffffffff))) & 0xffffffff
    #G(x,y,z) = (~x)&y + y&z
    def G(self, x: int, y: int, z: int) :
        x &= 0xffffffff
        y &= 0xffffffff
        z &= 0xffffffff
        return (((~x) & 0xffffffff) & y + y & z) & 0xffffffff
    #H(x,y,z) = (x^~y) & (~y^z)
    def H(self, x: int, y: int, z: int):
        x &= 0xffffffff
        y &= 0xffffffff
        z &= 0xffffffff
        return (x ^ ((~y) & 0xffffffff)) & (((~y) & 0xffffffff) ^ z)
    #I(x,y,z)= (~x & y) ^ (y & ~z)
    def I(self, x: int, y: int, z: int) :
        x &= 0xffffffff
        y &= 0xffffffff
        z &= 0xffffffff
        return (((~x) & 0xffffffff) & y) ^ (y & ((~z) & 0xffffffff))

    #每轮迭代的计算  参数n 为F,G,H,I,函数的结果
    def cycle(self,a,b,c,d,e,f,g,h,w,i,n,k):
        h1 = (g + n) & 0xffffffff
        g1 = f
        f1 = e
        # maj Ch   sigmod1 sigmod2 用于实现T1 T2，T1 T2是用来实现每轮迭代的计算的
        # sigmod2(x) = x<<26 ^ x <<21 ^ x <<7
        sigmod2_a = (((a << 26) | (a >> 6)) & 0xffffffff) ^ (((a << 21) | (a >> 11)) & 0xffffffff) ^ (
                    ((a << 7) | (a >> 25)) & 0xffffffff)
        #maj_abc = (a&b) ^ (b&c) ^ (a&c)
        maj_abc = (a & b) ^ (b & c) ^ (a & c)
        # T1 = sigmod2(a) + k[i] + w[i] + maj(a,b,c)
        T1 = (sigmod2_a + k[i] + w[i] + maj_abc) & 0xffffffff
        e1 = (d + T1) & 0xffffffff
        d1 = c
        c1 = b
        b1 = a
        # sigmod1(x) = x<<30 ^ x <<19 ^ x <<10
        sigmod1_e = (((e << 30) | (e >> 2)) & 0xffffffff) ^ (((e << 19) | (e >> 13)) & 0xffffffff) ^ (((e << 10) | (e >> 22)) & 0xffffffff)
        e_not = (~e) & 0xffffffff
        ch = (e & h1) ^ (e_not & g1)
        # T2 = sigmod1(e) + w[i] + I(h,g,e)
        T2 = (sigmod1_e + w[i] + ch) & 0xffffffff
        a1 = (T1 + T2) & 0xffffffff
        return a1,b1,c1,d1,e1,f1,g1,h1
    #块处理  这里的n表示第n块
    def process_block(self,message_byte,n):
        a,b,c,d,e,f,g,h = self.h0,self.h1,self.h2,self.h3,self.h4,self.h5,self.h6,self.h7
        k = self.k
        w = list(struct.unpack('>16L', message_byte)) + 48 *[0] #将消息扩展为64块

        # gamma_1: left_rotate(27)^29^31
        def gamma1(d):
            r17 = ((d << 17) | (d >> 15)) & 0xffffffff  # 32-17=15
            r19 = ((d << 19) | (d >> 13)) & 0xffffffff
            r23 = ((d << 23) | (d >> 9)) & 0xffffffff
            return r17 ^ r19 ^ r23

        # gamma_2: left_rotate(27)^29^31
        def gamma2(d):
            r27 = ((d << 27) | (d >> 5)) & 0xffffffff  # 32-27=5
            r29 = ((d << 29) | (d >> 3)) & 0xffffffff
            r31 = ((d << 31) | (d >> 1)) & 0xffffffff
            return r27 ^ r29 ^ r31

        for i in range(16, 64):
            x = gamma1(w[i - 2]) ^ gamma2(w[i - 3])
            y = gamma1(w[i - 11]) ^ gamma2(w[i - 13])
            w[i] = (x + y) & 0xffffffff

        f1 = self.F(a, b, c)
        #第一次16个循环迭代
        for i in range(16):
            a,b,c,d,e,f,g,h = self.cycle(a,b,c,d,e,f,g,h,w,i,f1,k=k)
        g1 = self.G(c, d, e)
        #第二次16个循环
        for i in range(16,32):
            a, b, c, d, e, f, g, h = self.cycle(a, b, c, d, e, f, g, h, w, i, g1,k=k)
        h1 = self.H(f, e, d)
        #第三次16个循环
        for i in range(32, 48):
            a, b, c, d, e, f, g, h = self.cycle(a, b, c, d, e, f, g, h, w, i, h1,k=k)
        #第四次16个循环
        i1 = self.I(h, g, f)
        for i in range(48,64):
            a, b, c, d, e, f, g, h = self.cycle(a, b, c, d, e, f, g, h, w, i, i1,k=k)

        #与上一轮的寄存器进行加法
        self.h0 = (self.h0 + a + self.code[n]) & 0xffffffff
        self.h1 = (self.h1+ b) & 0xffffffff
        self.h2 = (self.h2 + c) & 0xffffffff
        self.h3 = (self.h3 + d) & 0xffffffff
        self.h4 = (self.h4 + e) & 0xffffffff
        self.h5 = (self.h5 + f) & 0xffffffff
        self.h6 = (self.h6 + g) & 0xffffffff
        self.h7 = (self.h7 + h + self.code[n]) & 0xffffffff
        #同时保存的素数参与每轮的寄存器输出的产生

    def value(self):
        #计算要分成多少组512bit
        block_count = len(self.message_byte) // 64
        for i in range(block_count):
            self.process_block(self.message_byte[64 * i :64 * i + 64],i)
        return ''.join(f'{x:08x}' for x in [self.h0, self.h1, self.h2, self.h3, self.h4,self.h5,self.h6,self.h7])
def prepare(message):
    message_byte = message.encode('utf8')
    length = len(message_byte) * 8
    target_mod = 448 - 8 #如果填充了第一个0x80后导致超出448 所以这里直接用448 - 8作为判断条件
    remainder = length % 512
    if remainder <= target_mod:  #-8 是为了把加入的0x80扣除
        # 余数≤440  填充到当前512的448位
        target_length = length + (448 - remainder)
    else:
        # 余数>440  填充到下一个512的448位
        target_length = length + (512 - remainder) + 448
    return message_byte,target_length


#至少取min_num个个编码来保证 多次计算哈希值时不用多次读取数据
def judge_length(length,code_list):
    global min_num
    if len(code_list )== 0: #第一次得到素数编码列表
        if length <= min_num: #如果少于
            return base.extract_decimals_bytes(min_num)
        else:
            min_num = length*2
            return base.extract_decimals_bytes(min_num)
    else:#目标长度长 要计算新的素数
        if len(code_list) < length:
            min_num = length * 2
            return base.extract_decimals_bytes(min_num)
        else:#之前取过了直接返回code_list
            return code_list


if __name__ == "__main__":
    epoch = 100000
    hash_list = []
    crushed_time = 0
    #通过循环来检测冲突性
    code_list = []

    for i in range(epoch):
        message = format(i,'X')
        message_byte, goal_length = prepare(message)
        group_count = (goal_length + 64) // 512  # +64 是padding最后拼接的原始长度位
        code_list = judge_length(group_count,code_list)

        _hash = Hash(code_list,message_byte)
        pad_data = _hash.padding(goal_length)
        Hash_value = _hash.value()
        if Hash_value in hash_list:
            crushed_time +=1
        hash_list.append(Hash_value)
        print(i)

    message = '123456'
    message_byte, goal_length = prepare(message)
    group_count = (goal_length + 64) // 512  # +64 是padding最后拼接的原始长度位
    code_list = judge_length(group_count, code_list)
    start = time.perf_counter()
    _hash = Hash(code_list, message_byte)
    pad_data = _hash.padding(goal_length)
    Hash_value = _hash.value()
    end = time.perf_counter()
    costtime = (end - start) * 1e6

    print(costtime)

    print(crushed_time)