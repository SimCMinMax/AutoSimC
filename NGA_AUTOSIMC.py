# -*- coding: utf-8 -*-
"""
@author: Sirius5783
@license: None
@contact: markdan@foxmail.com
@file: NGA_AUTOSIMC.py
@time: 2018/2/19 0019 11:19
@desc:Windows 10,Python3.6
"""
"""

"""
import tkinter as tk
from tkinter.filedialog import *
from tkinter import messagebox
import random
from settings import settings
#from stdsupo import redirectedGuiFunc

class asmTk:
    def __init__(self, ):
        self.root = tk.Tk()
        self.root.title('AutoSimC-master窗口版V2 by NGA月神之韧')
        self.root.geometry('490x740+635+120')


        self.select = tk.Button(text='Simc路径选择', width=20, command=self.file_open)
        self.select.place(x=80, y=15)

        self.boom = tk.Button(text='DIE! DIE! DIE!!!', width=20, command=self.write_inputs)
        self.boom.place(x=245, y=15)

        tk.Label(self.root,text='最大装备橙装数:',fg='blue').place(x=60, y=65)
        self.max_leg = tk.IntVar()
        self.max_leg.set(2)
        tk.Radiobutton(self.root,text='2',variable=self.max_leg,value=2,command=self.leg_spe).place(x=160, y=55)
        tk.Radiobutton(self.root, text='3',variable=self.max_leg,value=3,command=self.leg_spe).place(x=160, y=75)

        tk.Label(self.root,text='Boss类型选择:',fg='blue').place(x=245, y=60)
        self.boss_types={"帕奇维克(木桩单体)":"Default_Patchwerk","轻移动战":"Default_LightMovement","奥特拉赛恩(周期性击晕)":"Default_Ultraxion",
                         "兽王(刷新2种小怪,移动战,结果会误差)":"Default_Beastlord","2个重叠的帕奇维克":"Two Patchwerks, stacked",
                         "2个相隔27码的帕奇维克":"Two Patchwerks, 27 yards away from each other"}
        self.boss_type = tk.StringVar()
        self.boss_type.set('帕奇维克(木桩单体)')
        tk.OptionMenu(self.root,self.boss_type,*self.boss_types,command=self.options_spe).place(x=245,y=80)

        tk.Label(self.root, text='模拟程序运行优先级:', fg='blue').place(x=245, y=120)
        self.priorities = {'低(推荐)':'low', '中下':'below_normal', '中等':'normal', '中上':'above_normal', '最高(可能使你的系统失去响应)':'highest'}
        self.priority = tk.StringVar()
        self.priority.set('低(推荐)')
        tk.OptionMenu(self.root, self.priority, *self.priorities, command=self.options_spe).place(x=245, y=140)

        tk.Label(self.root, text='最少装备T21套装数:', fg='blue').place(x=60, y=110)
        self.min_T21 = tk.IntVar()
        self.min_T21.set(6)
        tk.Radiobutton(self.root, text='4', variable=self.min_T21, value=4, command=self.T21_spe).place(x=180, y=100)
        tk.Radiobutton(self.root, text='6', variable=self.min_T21, value=6, command=self.T21_spe).place(x=180, y=120)

        tk.Label(self.root, text='模拟模式选择:', fg='blue').place(x=60, y=150)
        self.mode = tk.IntVar()
        self.mode.set(2)
        tk.Radiobutton(self.root, text='静态(耗时少)', variable=self.mode, value=1, command=self.sta_spe).place(x=142, y=148)
        tk.Radiobutton(self.root, text='动态(更精准)', variable=self.mode, value=2, command=self.sta_spe).place(x=142, y=168)

        self.entry = tk.Text(width=50, height=30)
        self.entry.insert(tk.INSERT, '请输入您通过/SimPermut插件获得的角色字符串\n然后粘贴并覆盖此文本框内容')
        self.entry.place(x=65, y=198)

        self.status = tk.Label(relief=RIDGE, anchor=W)
        self.status.config(text='状态:', fg='red')
        self.status.place(x=65, y=608)

        self.news = tk.Label(relief=RIDGE, anchor=W)
        self.news.config(text='CCAV新闻轮播中...', fg='black')
        self.news.place(x=65, y=630)

        self.info = tk.Label(text='AutoSimC介绍:\n将您身上的装备宝石等自动输入Simulationcraft中进行组合\n'
                                  '然后批量进行伤害模拟最后输出DPS最高的配装以供参考\n开源https://github.com/Sirius5783/AutoSimC',
                             justify=LEFT)
        self.info.place(x=65, y=655)

        if os.path.exists(settings.simc_path):
            self.filename = settings.simc_path
            self.status.config(text='状态:已选择的simc.exe路径' + self.filename, fg='blue')
        else:
            self.filename = None
            self.status.config(text='状态:未选择simc程序的路径!', fg='red')

        tk.mainloop()

    def file_open(self):
        self.boring()
        self.filename = askopenfilename()
        if self.filename:
            #print(f'filename:{self.filename}',type(self.filename))
            if self.filename[-8:] == 'simc.exe':
                self.status.config(text='状态:已选择的simc.exe路径'+self.filename,fg='blue')
                settings.simc_path = self.filename
            else:
                self.status.config(text='状态:您选择的不是simc.exe程序!请重新选择', fg='red')

        else:
            self.status.config(text='状态:未选择simc程序的路径!', fg='red')
        #print(f'filename:{repr(self.filename)}',type(self.filename))


    def write_inputs(self):
        self.boring()
        strings = self.entry.get('1.0', END)
        if strings != '这是啥软件?' and '[Profile]' in strings:
            if self.filename == None:
                messagebox.showerror(title='错误提示', message='未选择simc程序的路径!~')
            elif self.filename[-8:] == 'simc.exe':
                # print(strings,'\n',type(strings))

                personal_input = open('input.txt', 'w', encoding='utf-8')
                personal_input.write(strings)
                personal_input.close()

                messagebox.showinfo(title='觉醒!', message='模拟即将在身后那个黑乎乎的窗口开始了哦!')
                self.start_autosimc()
            else:
                messagebox.showerror(title='错误提示', message='您选择的不是simc.exe程序!请重新选择~')
        else:
            messagebox.showerror(title='错误提示', message='您输入的不是合法的角色字符串,请重新输入~')

    def start_autosimc(self):
        self.save_location()
        self.root.destroy()
        import main
        main.runs()
        input('现在可以按回车关闭程序啦.')

    # print(self.max_leg.get(),self.min_T21.get(),self.boss_types[self.boss_type.get()],self.priorities[self.priority.get()])
    def leg_spe(self,*args):
        settings.default_leg_max = int(self.max_leg.get())
        self.boring()

    def T21_spe(self,*args):
        settings.default_equip_t21_min = int(self.min_T21.get())
        self.boring()

    def options_spe(self,*args):
        settings.default_fightstyle = self.boss_types[self.boss_type.get()]
        settings.simc_priority = self.priorities[self.priority.get()]
        self.boring()

    def sta_spe(self,*args):
        #print('mode=',self.mode.get())
        settings.auto_choose_static_or_dynamic = self.mode.get()
        self.boring()


    def boring(self):
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

        random_text = '新闻:' + name_dict[random.randint(1, 83)] + '用' + abilities_dict[random.randint(0, 28)] \
                      + '残忍的杀死了' + name_dict[random.randint(1, 83)] + '!' + ends_dict[random.randint(0, 10)] + '!'
        color = ['red', 'black', 'purple', 'pink', 'blue']
        self.news.config(text=random_text, fg=color[random.randint(0, 4)])

    def save_location(self):
        with open('settings.py','r',encoding='utf-8') as file:
            content = file.readlines()

        content[9] = f"    simc_path ='{self.filename}'\n"
        with open('settings.py', 'w',encoding='utf-8') as file:
            file.writelines(content)

# def runPackDialog_Wrapped():            # callback to run in mytools.py
#     redirectedGuiFunc(runn)


if __name__ == '__main__':
#def runn():
    user = asmTk()

#runPackDialog_Wrapped()




