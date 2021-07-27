import copy
import sys
import os
import json
import shutil
import time


class Game:
    """
    nw  ne
    sw  se
    这是方位
    """
    def __init__(self, square: [int, int, int, int]):  # [northeast, southeast, southwest, northwest]
        os.makedirs('last_result', exist_ok=True)
        os.makedirs('result', exist_ok=True)
        # 注意起始的这两个文件夹必须是空的
        self.step = 1  # 统计步数用的
        self.position_list = ['nw', 'ne', 'sw', 'se']  # 每次有这四种情况，每种情况都搞
        self.dic = {  # 这是起始值，下面所有字典都是这样的，就是值在变化
            'ne': square[0],
            'se': square[1],
            'sw': square[2],
            'nw': square[3],
        }
        """
        为了减少内存，我将每一步的结果存储为文件
        （一开始用的列表存储，内存炸裂。）内存不够，存储来凑。
        这里对存储的内容说明：
            每个文件时一种情况，共两行。
            第一行是用 '.' 连接的列表的字符串，就是这种情况是在初始状态点了哪些位置得到现在的情况的
            第二行就是现在的情况，把字典转成了json字符串来保存
            这些文件其实就是所有结果的树状图
        """
        with open(f'last_result/{time.time()}', 'w') as f:
            f.write('.'.join([]))  # 存储列表，用join转成字符串
            f.write('\n')  # 换行，方便读取的使用split('\n')
            f.write(json.dumps(self.dic))  # 存储字典，用json转成字符串
        # 下面是一开始用列表来存储结果，内存会炸。但是原理和文件存储一样
        # self.last_result = [([], self.dic)]  # 起始数据，不断被中间数据替换
        # self.result = []  # 中间数据

    @staticmethod  # 这个staticmethod单纯是为了不想看到那个唯一的浅灰色感叹号
    def add(value):
        """
        这是用了计数的，每次+1,4+1是1
        """
        if value == 4:
            return 1
        else:
            return value + 1

    def click(self, position: str, step_dic):
        """
        这是每次点击一个地方，数据的变化
        """
        if position == 'ne':
            step_dic['ne'] = self.add(step_dic['ne'])
            step_dic['nw'] = self.add(step_dic['nw'])
            step_dic['se'] = self.add(step_dic['se'])
        if position == 'se':
            step_dic['ne'] = self.add(step_dic['ne'])
            step_dic['sw'] = self.add(step_dic['sw'])
            step_dic['se'] = self.add(step_dic['se'])
        if position == 'sw':
            step_dic['nw'] = self.add(step_dic['nw'])
            step_dic['sw'] = self.add(step_dic['sw'])
            step_dic['se'] = self.add(step_dic['se'])
        if position == 'nw':
            step_dic['ne'] = self.add(step_dic['ne'])
            step_dic['nw'] = self.add(step_dic['nw'])
            step_dic['sw'] = self.add(step_dic['sw'])

    def each_step(self, _list: [str], dic: dict):
        """
        这是每一步需要的操作
        """
        for position in self.position_list:  # 这里是将他分为四个分支，四种点击的情况
            # 防止数据变动，这里直接复制了，四种情况互不干扰
            step_list = copy.deepcopy(_list)
            step_dic = copy.deepcopy(dic)
            self.click(position, step_dic)  # 执行操作
            step_list.append(position)  # 将操作添加的列表，这个列表包含所有的操作
            # 每次判断一下，如果找到答案了，管你那么多，直接打印步骤并退出，后面我好心加了个删除文件的，免得自己删
            if step_dic['nw'] == step_dic['ne'] == step_dic['se'] == step_dic['sw'] == 1:
                print(step_list)
                shutil.rmtree('last_result')
                shutil.rmtree('result')
                sys.exit()
            # 不是答案就保存到result文件夹，继续下一个，
            with open(f'result/{time.time()}', 'w') as f:
                f.write('.'.join(step_list))
                f.write('\n')
                f.write(json.dumps(step_dic))

    def run(self):
        """
        将每一步连接起来
        """
        print(self.step)  # 打印步数，后面会+1，第几步就是4的几次方
        for step in os.listdir('last_result'):
            # 上一次的结果都在last_result文件夹，读取他，进行树状图的下一次操作
            with open(f'last_result/{step}') as f:
                data = f.read().split('\n')
                step_list = data[0].split('.')
                step_dic = json.loads(data[1])
            self.each_step(step_list, step_dic)
            # 这里操作完就删除这个文件，免得占用太多地方，也避免下一次操作出现重复
            os.remove(f'last_result/{step}')
        """
        这里操作完了last_result，结果全在result中，此时last_result是空文件夹
        然后我把last_result删掉，把result改名为last_result，这样他就成了last_result
        最后再添加一个result文件夹，就完成了一次更新迭代，
        其实这整个原理就是细菌的二分裂一样，只是这是四分裂，有点大，得忍忍
        """
        os.rmdir('last_result')
        os.rename('result', 'last_result')
        os.mkdir('result')
        self.step += 1
        # 更新迭代完了再继续运行他，就能实现循环，直到找到答案
        self.run()


# g = Game([1, 4, 4, 4])  # 这是测试用例，用最简单的情况找到之前代码的错误
g = Game([1, 4, 3, 2])
g.run()
