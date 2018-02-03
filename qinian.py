# -*- coding: utf-8 -*-
"""
@author: Sirius5783
@license: None
@contact: markdan@foxmail.com
@file: ASM自动模拟.py.py
@time: 2018/2/3 0003 14:11
@desc:Windows 10,Python3.6
"""
"""

"""
import tkinter as tk
from tkinter.filedialog import *
from tkinter import messagebox
import random

class asmTk:
    def __init__(self,):
        self.root = tk.Tk()
        self.root.title('AutoSimC-master窗口版 by NGA月神之韧')
        self.root.geometry('480x600+635+295')

        self.select = tk.Button(text='我是一个无聊的按钮',width = 20,command=self.boring)
        self.select.place(x=80,y=15)

        self.boom = tk.Button(text='die! die! die!!!',width = 20,command=self.write_inputs)
        self.boom.place(x=245, y=15)

        self.entry = tk.Text(width=50,height=30)
        self.entry.insert(tk.INSERT,'请输入您通过/SimPermut插件AutoSimc-Export按键获得的角色字符串\n然后粘贴并覆盖此文本框内容')
        self.entry.place(x=65,y=60)

        self.status = tk.Label(text='震惊:',relief=RIDGE,anchor=W)
        self.status.config(text='震惊:', fg='red')
        self.status.place(x=65,y=470)

        self.info = tk.Label(text='这是啥软件?\nAutoSimC是一个把你选择的装备和附魔宝石等组合,\n批量输入Simulationcraft中进行伤害模拟,\n然后输出DPS最高的装备组合以供参考.\n源码来自github/AutoSimC' ,
                               justify=LEFT)
        self.info.place(x=65, y=500)

        #self.check()
        tk.mainloop()

    # def file_open(self,):
    #     filename = askopenfilename()
    #     if filename:
    #         #print(f'filename:{filename}',type(filename))
    #         if filename[-8:] == 'simc.exe':
    #             self.status.config(text='状态:已选择的simc程序'+filename,fg='black')
    #             self.write_settings(filename)
    #         else:
    #             self.status.config(text='状态:您选择的不是simc.exe程序!请重新选择', fg='black')
    #     else:
    #         self.status.config(text='状态:未选择simc程序!', fg='red')
    #         #print(filename)


    # def write_settings(self,filename):
    #     settings = open('settings.py','r',encoding='utf-8')  # settings.py
    #     content = settings.readlines()
    #     #print(f'ORI content[9]:{content[9]}')
    #     settings.close()
    #
    #     content[9] = '    simc_path = r' + "'" + filename + "'\n"
    #     content[9] = content[9].replace('/','\\')
    #     #print(f'EDITED content[9]:{content[9]}')
    #
    #     settings = open('settings.py', 'w',encoding='utf-8')
    #     settings.writelines(content)
    #     settings.close()

    def write_inputs(self):
        strings = self.entry.get('1.0',END)
        if strings != '这是啥软件?\nAutoSimC是一个把你选择的装备和附魔宝石等组合,\n批量输入Simulationcraft中进行输出模拟,\n然后输出DPS最高的装备组合以供参考.\n源码来自github/AutoSimC'\
                and '[Profile]' in strings:
            #print(strings,'\n',type(strings))
            settings = open('input.txt', 'w',encoding='utf-8')
            settings.write(strings)
            settings.close()

            messagebox.showinfo(title='觉醒!',message='模拟即将在身后那个黑乎乎的窗口开始了哦!')
            messagebox.showinfo(title='POWER OVERWHELMING!', message='请根据黑窗内提示操作~~~')
            self.root.destroy()
            import main
            main.runs()
            input('按回车键关闭这个黑乎乎的窗口.')
        else:
            messagebox.showerror(title='错误提示',message='您输入的不是合法的角色字符串,请重新输入~')


    # def check(self):
    #     settings = open('settings.py', 'r',encoding='utf-8')  # settings.py
    #     content = settings.readlines()
    #     settings.close()
    #     if 'simc.exe' in content[9]:
    #         self.status.config(text='状态:已选择的simc程序' + content[9][18:], fg='black')
    #     else:
    #         self.status.config(text='状态:未选择simc程序!', fg='red')

    abilities_dict = {0: '大象无形', 1: '卑鄙的下毒', 2: '小无相功', 3: '吸精大法', 4: '撩阴腿', 5: '人品激光', 6: '优美的歌声', 7: '抠脚大法', 8: '缩阳入腹', 9: '无上道德审判', 10: '末日降临',
                      11: '浮生万刃', 12: '永恒零度', 13: '半月斩', 14: '咫尺天涯', 15: '八卦游龙掌', 16: '崂山蛇白水', 17: '不动明王', 18: '炽修罗', 19: '唯我独尊', 20: '霸天造化掌',
                      21: '武动乾坤', 22: '斗破苍穹', 23: '吞噬星空', 24: '神罗天征', 25: '太极云手', 26: '开赛露加冰', 27: '罗汉翻天印', 28: '大虚帝子印'}

    ends_dict = {0: '伟大的爱情', 1: '卑鄙的手段', 2: '撩人的外貌', 3: '充盈的精气', 4: '可怕的口臭', 5: '丑陋的歌喉', 6: '无敌的人品', 7: '硕大的巨根', 8: '深不见底的黑洞', 9: '一根烟的功夫', 10: '做白日梦'}

    name_dict = {1: '彭万里', 2: '高大山', 3: '谢大海', 4: '马宏宇', 5: '林莽', 6: '黄强辉', 7: '章汉夫', 8: '范长江', 9: '林君雄', 10: '谭平山', 11: '朱希亮', 12: '李四光', 13: '甘铁生', 14: '张伍绍祖', 15: '马继祖',
                 16: '程孝先', 17: '宗敬先', 18: '年广嗣', 19: '汤绍箕', 20: '吕显祖', 21: '何光宗', 22: '孙念祖', 23: '马建国', 24: '节振国', 25: '冯兴国', 26: '郝爱民', 27: '于学忠', 28: '马连良',
                 29: '胡宝善', 30: '李宗仁', 31: '洪学智', 32: '余克勤', 33: '吴克俭', 34: '杨惟义', 35: '李文信', 36: '王德茂', 37: '李书诚', 38: '杨勇', 39: '高尚德', 40: '刁富贵', 41: '汤念祖',
                 42: '吕奉先', 43: '何光宗', 44: '冷德友', 45: '安怡孙', 46: '贾德善', 47: '蔡德霖', 48: '关仁', 49: '郑义贾怡孙天民', 50: '赵大华', 51: '赵进喜', 52: '赵德荣', 53: '赵德茂',
                 54: '钱汉祥', 55: '钱运高', 56: '钱生禄', 57: '孙寿康', 58: '孙应吉', 59: '孙顺达', 60: '李秉贵', 61: '李厚福', 62: '李开富', 63: '王子久', 64: '刘永生', 65: '刘宝瑞',
                 66: '关玉和', 67: '王仁兴', 68: '李际泰', 69: '罗元发', 70: '刘造时', 71: '刘乃超', 72: '刘长胜', 73: '张成基', 74: '张国柱', 75: '张志远', 76: '张广才', 77: '吕德榜', 78: '吕文达',
                 79: '吴家栋', 80: '吴国梁', 81: '吴立功李大江', 82: '张石山', 83: '王海'}

    def boring(self):
        random_text = '震惊:' + self.name_dict[random.randint(1,83)] + '用' + self.abilities_dict[random.randint(0,28)] \
                      + '残忍的杀死了' + self.name_dict[random.randint(1,83)] + '!' + self.ends_dict[random.randint(0,10)]+'!'
        color = ['red','black','purple','pink','blue']
        self.status.config(text=random_text, fg=color[random.randint(0,4)])

if __name__ == '__main__':
    user = asmTk()
