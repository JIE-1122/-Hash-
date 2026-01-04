
import  base
import Hash
import time
#检测冲突

def test_clash(times):
    hash_set = set()
    crushed_time = 0
    # 通过循环来检测冲突性
    code_list = []
    time_list = []
    for i in range(times):
        #通过对i的叠加来得到新的消息
        message = format(i,'X')
        message_byte, goal_length = Hash.prepare(message)
        group_count = (goal_length + 64) // 512  # +64 是padding最后拼接的原始长度位
        code_list = Hash.judge_length(group_count,code_list)

        #计算时间
        start = time.perf_counter()
        _hash = Hash.Hash(code_list,message_byte)
        pad_data = _hash.padding(goal_length)

        Hash_value = _hash.value()
        end = time.perf_counter()
        costtime = (end - start) * 1e6
        time_list.append(costtime)
        #如果计算出来的哈希值已经在列表中了 碰撞次数+1
        if Hash_value in hash_set:
            crushed_time += 1
        hash_set.add(Hash_value)
    #计算平均时间
    ave_time = sum(time_list) / len(time_list)
    return crushed_time,ave_time

#检测消息的哈希值以及所花费的时间
def test_time_hash(message_list):
    code_list = []
    for message in message_list:
        message_byte, goal_length = Hash.prepare(message)
        group_count = (goal_length + 64) // 512  # +64 是padding最后拼接的原始长度位
        code_list = Hash.judge_length(group_count, code_list)
        #计算时间
        start = time.perf_counter()
        _hash = Hash.Hash(code_list, message_byte)
        pad_data = _hash.padding(goal_length)
        Hash_value = _hash.value()
        end = time.perf_counter()
        costtime = (end - start) * 1e6
        print("输入的消息为:",message,f'所花的时间为:{costtime}μs',message,'对应的哈希值为',Hash_value)

if __name__ == "__main__":
    message_list = ['1145','hello world','你好','世界']
    test_time_hash(message_list)
    times = 1000000
    crush_times , ave_time = test_clash(times)
    print(f"测试的次数为{times},冲突的次数为{crush_times},平均花费的时间为:{ave_time}μs")