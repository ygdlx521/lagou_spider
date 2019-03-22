import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from wordcloud import WordCloud
from scipy.misc import imread
import jieba
from pylab import mpl

# 使matplotlib模块能显示中文
mpl.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
mpl.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题
avg_salary = []


def get_experience_histogram(df):
    df['position_experience'] = df['work_year'].str.findall('\d+')
    avg_work_year = []
    for i in df['position_experience']:
        # 如果工作经验为'不限'或'应届毕业生',那么匹配值为空,工作年限为0
        if len(i) == 0:
            avg_work_year.append(0)
        # 如果匹配值为一个数值,那么返回该数值
        elif len(i) == 1:
            avg_work_year.append(int(''.join(i)))
        # 如果匹配值为一个区间,那么取平均值
        else:
            num_list = list(range(int(i[0]), int(i[1]) + 1))
            avg_work_year.extend(num_list)
    # 绘制频率直方图并保存
    plt.hist(avg_work_year, bins=10)  # bins的含义是分成几份
    plt.xlabel('工作经验 (年)')
    plt.ylabel('人数')
    plt.title("工作经验需求直方图")
    plt.savefig('工作经验需求直方图.jpg')
    plt.show()


def get_salary_histogram(df):
    # 将字符串转化为列表,再取区间的前25%，比较贴近现实
    df['salary'] = df['position_salary'].str.findall('\d+')
    for k in df['salary']:
        int_list = [int(n) for n in k]
        try:
            avg_wage = (int_list[0] + int_list[1]) / 2
        except Exception as err:
            print(err)
            print(k)
            avg_wage = int_list[0]
        avg_salary.append(avg_wage)
    df['月工资'] = avg_salary
    # 将清洗后的数据保存,以便检查
    df.to_csv('draft.csv', index=False)
    # 描述统计
    print('Python职位工资描述：\n{}'.format(df['月工资'].describe()))
    # 绘制频率直方图并保存
    plt.hist(df['月工资'], bins=10)  # bins的含义是分成几份
    plt.xlabel('工资 (千元)')
    plt.ylabel('人数')
    plt.title("工资分布直方图")
    plt.savefig('工资分布直方图.jpg')
    plt.show()


def get_city_pie(df):
    # 绘制饼图并保存
    all_city = df['position_city'].value_counts()
    series1 = all_city[all_city > 5]
    series2 = pd.Series({'其他': all_city[all_city < 5].sum()})
    result = pd.concat([series1, series2])
    plt.pie(result, labels=result.keys(), labeldistance=1.1, autopct='%d%%')
    plt.axis('equal')  # 使饼图为正圆形
    plt.legend(loc='upper left', bbox_to_anchor=(-0.1, 1))
    plt.savefig('工作城市占比饼图.jpg')
    plt.show()


def get_beijing_location_pie(df):
    # 绘制饼图并保存
    all_location = df['position_area'].where(df['position_city'] == '北京').value_counts()
    series1 = all_location[all_location > 3]
    series2 = pd.Series({'其他': all_location[all_location < 3].sum()})
    result = pd.concat([series1, series2])
    plt.pie(result, labels=result.keys(), labeldistance=1.1, autopct='%d%%')
    plt.axis('equal')  # 使饼图为正圆形
    plt.legend(loc='upper left', bbox_to_anchor=(-0.1, 1))
    plt.savefig('北京工作地点占比饼图.jpg')
    plt.show()


def get_word_cloud(df):
    text = ""
    for line in df['position_desc']:
        text += line
    cut_text = ' '.join(jieba.cut(text))
    print(cut_text)
    color_mask = imread('cloud.jpg')  # 设置背景图
    cloud = WordCloud(
        font_path='simhei.ttf',
        background_color='white',
        mask=color_mask,
        max_words=1000,
        max_font_size=100
    )
    word_cloud = cloud.generate(cut_text)
    # 保存词云图片
    word_cloud.to_file('公司福利词云.jpg')
    plt.imshow(word_cloud)
    plt.axis('off')
    plt.show()


if __name__ == "__main__":
    print("read in csv data...")
    # 读取数据
    df = pd.read_csv('out.csv', encoding='gbk')
    # 数据清洗,剔除实习岗位
    df.drop(df[df['position_name'].str.contains('实习')].index, inplace=True)
    print(df)
    get_salary_histogram(df)
    get_experience_histogram(df)
    get_city_pie(df)
    get_beijing_location_pie(df)
    get_word_cloud(df)

# def test(df):
#     # 实证统计,将学历不限的职位要求认定为最低学历:大专
#     df['education'] = df['education'].replace('不限', '大专')
#
#     # 学历分为大专\本科\硕士,将它们设定为虚拟变量
#     dummy_edu = pd.get_dummies(df['education'], prefix='学历')
#     #print(dummy_edu)
#     # 构建回归数组
#     df['salary'] = pd.Series(avg_salary)
#     df_with_dummy = pd.concat([df['salary'], df['work_year'], dummy_edu], axis=1)
#
#     # 建立多元回归模型
#     y = df_with_dummy['salary']
#     X = df_with_dummy[['学历_大专', '学历_本科', '学历_硕士']]
#     X = sm.add_constant(X)
#     model = sm.OLS(y, X)
#     results = model.fit()
#     print('回归方程的参数：\n{}\n'.format(results.params))
#     print('回归结果：\n{}'.format(results.summary()))
