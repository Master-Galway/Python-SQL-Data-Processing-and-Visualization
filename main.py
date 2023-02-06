import pandas as pd
import numpy as np
import os
import glob
import dash
from dash import dcc
from dash import html
import plotly.express as px
import plotly.graph_objects as go
from pandasql import sqldf
import re
from IPython.core.display_functions import display

#sql function
def pysqldf(q):
    return sqldf(q,globals());

#Fucntion to determine if there is Chinese in a string
def is_chinese(string):
  for ch in string:
    if u'\u4e00' <= ch <= u'\u9fff':
      return True
  return False

#Print working directory
cwd = os.getcwd()
print("Current working directory: {0}".format(cwd))

#assign all csv files in dataframe
path = os.getcwd()
csv_files = glob.glob(os.path.join(path, "*.csv"))
split_char = '\\'
for f in csv_files:
    # f is a directory name originally. Cutting everything before the last "\"
    fileName = f.split(split_char)[-1]
    # Cutting everything after the first "."
    fileName = fileName.split('.')[0]
    # all files read into csv, with their assigned name as their actual file name
    df = fileName
    df = pd.read_csv(f)

    # Process UserProfile
    if fileName == 'UserProfile':

        #用户性别比例
        male = 0
        female = 0
        for x in df['gender']:
            if x == '男':
                male += 1
        for x in df['gender']:
            if x == '女':
                female += 1
        x_Axis = [male, female, (len(df.index) - male - female)]
        Names = ['男', '女', '其它']
        fig = px.pie(values = x_Axis, names = Names, title = '性别比例')
        fig.show()

        #用户年龄分布
        birthList = []
        for x in df['birthday__iso']:
            x = x.split('-')[0]
            birthList.append(int(x))
        yearCount = [0,0,0,0,0,0,0,0]
        labels = ['1950-1959', '1960-1969','1970-1979','1980-1989','1990-1999','2000-2009','2010-2019','2020-2022']
        for x in birthList:
            if 1950 <= x < 1960:
                yearCount[0] = yearCount[0] + 1
            elif 1960 <= x < 1970:
                yearCount[1] = yearCount[1] + 1
            elif 1970 <= x < 1980:
                yearCount[2] = yearCount[2] + 1
            elif 1980 <= x < 1990:
                yearCount[3] = yearCount[3] + 1
            elif 1990 <= x < 2000:
                yearCount[4] = yearCount[4] + 1
            elif 2000 <= x < 2010:
                yearCount[5] = yearCount[5] + 1
            elif 2010 <= x < 2020:
                yearCount[6] = yearCount[6] + 1
            elif 2020 <= x < 2022:
                yearCount[7] = yearCount[7] + 1
        zipped = list(zip(labels, yearCount))
        dataframe = pd.DataFrame(zipped, columns = ['用户年龄', '数量'])
        fig = px.bar(dataframe, x = '用户年龄', y = '数量', text_auto='.2s', title = '用户年龄分布')
        fig.show()

        #用户造型选择
        fig = px.histogram(df, x="avatar", text_auto='.2s', title = '用户造型选择')
        fig.show()

    # Process Checkin data
    if fileName == 'Checkin':

        #用户心情（1-5）
        fig = px.histogram(df, x="mood", text_auto='.2s', title='用户心情统计')
        fig.show()

        #用户留下随笔比例
        noteCount = 0;
        for x in df['quicknote']:
            if is_chinese(str(x)):
                noteCount += 1

        x_Axis = [noteCount, len(df.index) - noteCount]
        Names = ['Left a Note', 'No Note']
        fig = px.pie(values = x_Axis, names = Names, title ='用户留下快速笔记比例')
        fig.show()

    # Process Journal Record data
    if fileName == 'JournalRecord':

        #用户情绪被什么影响
        fig = px.pie(df, values=df['tags__-'].value_counts().values, names=df['tags__-'].value_counts().index, title = '用户情绪被什么影响')
        fig.update_traces(hoverinfo='label+percent', textinfo='value')
        fig.show()

        #用户情绪统计
        fig = px.histogram(df, x="emotions__-", text_auto='.2s', title='用户情绪统计')
        fig.show()

        #聊一聊发生的事
        noteCount = 0;
        for x in df['elaborateContent']:
            if pd.isnull(x) == False:
                noteCount += 1
        x_Axis = [noteCount, len(df.index) - noteCount]
        Names = ['聊一聊', '不想聊']
        fig = px.pie(values=x_Axis, names=Names, title = '用户在记录情绪后有没有选择聊一聊发生的事')
        fig.show()

        #引导练习评价
        helpful = 0
        no = 0
        for x in df['exerciseHelpful']:
            if x == 'yes':
                helpful += 1
        for x in df['exerciseHelpful']:
            if x == 'no':
                no += 1
        x_Axis = [helpful, no, (len(df.index) - helpful - no)]
        Names = ['有用', '没用', '跳过了引导练习']
        fig = px.pie(values=x_Axis, names=Names, title='用户对引导练习的评价比例')
        fig.show()

        # JournalRecord字数排行（取前五）
        q_wordcount = """
                    SELECT r.userProfileId, sum(CASE WHEN length(r.elaborateContent) is NULL THEN 0 ELSE length(r.elaborateContent) END) as wordcount
                    FROM df r
                    GROUP BY r.userProfileId
                    ORDER BY wordcount desc LIMIT 10;
                """
        dataframe = pysqldf(q_wordcount)
        fig = px.bar(dataframe, y='wordcount', x='userProfileId',
                     title='JournalRecord字数排行，最高十个用户', labels=dict(wordcount="字数", userProfileId="用户id"))
        fig.show()

    # Process Journal Exercise data
    if fileName == 'JournalExercise':

        #用户写下随笔日记比例
        noteCount = 0;
        for x in df['response']:
            if is_chinese(str(x)):
                noteCount += 1

        x_Axis = [noteCount, len(df.index) - noteCount]
        Names = ['Left a Response', 'No Response']
        fig = px.pie(values=x_Axis, names=Names, title= '用户在日记中写下随笔比例')
        fig.show()

        #用户是否选择完成推荐的练习
        df2 = pd.read_csv('JournalRecord.0.csv')
        df2 = df2[['objectId', 'suggestedExercise']]
        df2['suggestedExercise'].replace(' ', np.nan, inplace=True)
        df2.dropna(inplace=True)
        df2.rename(columns={'objectId': 'journalRecordId'}, inplace=True)
        df3 = df[['journalRecordId', 'completedExercise']]
        mergedDF = pd.merge(df3, df2)
        index = 0
        count = 0
        for x in mergedDF['suggestedExercise']:
            if x != mergedDF['completedExercise'][index]:
                count += 1
            index += 1
        x_Axis = [count, len(mergedDF.index) - count]
        Names = ['完成其它练习', '完成推荐练习']
        fig = px.pie(values=x_Axis, names=Names, title='用户完成了推荐练习 vs 选择了其它练习')
        fig.show()

        # JournalExercise字数排行（取前五）
        q_wordcount = """
                    SELECT e.userProfileId, sum(CASE WHEN length(e.response) is NULL THEN 0 ELSE length(e.response) END) as wordcount
                    FROM df e
                    GROUP BY e.userProfileId
                    ORDER BY wordcount desc LIMIT 10
                """
        dataframe = pysqldf(q_wordcount)
        fig = px.bar(dataframe, y='wordcount', x='userProfileId',
                     title='JournalExercise字数排行，最高十个用户', labels=dict(wordcount="字数", userProfileId="用户id"))
        fig.show()

    #Process Discussion Post Data
    if fileName == 'DiscussionPost':
        # 获赞最多用户ranking
        q_likes_dstr = """
            SELECT userprofileid, nickname, sum(likes) likes_sum
                FROM df
                GROUP BY userprofileid,nickname
                ORDER BY likes_sum desc;
        """

        dataframe = pysqldf(q_likes_dstr)
        fig = px.bar(dataframe, x='nickname', y='likes_sum', title="获赞最多用户ranking",
                     labels=dict(nickname="昵称", likes_sum="总获赞数"))
        fig.show()

        # 发帖最多用户ranking
        q_post_dstr = """
            SELECT nickname, count(1) post_num 
                FROM df
                GROUP BY nickname
                ORDER BY post_num desc;
        """

        dataframe = pysqldf(q_post_dstr)
        fig = px.bar(dataframe, x='nickname', y='post_num', title="发帖最多用户ranking",
                     labels=dict(nickname="昵称", post_num="发帖数"))
        fig.show()

#Graphing functions for dashboard
def checkin_time():
    df = pd.read_csv('Checkin.0.csv')
    meditationTime = []
    for x in df['timestamp__iso']:
        x = x.split('T')[1]
        x = x.split(':')[0]
        x = int(x) + 8  # time zone shift for 8 hours from ISO to Beijing Time
        if x > 23:
            x = x - 24
        meditationTime.append(x)
    histogram = dcc.Graph(figure=go.Figure(layout=layout).add_trace(
        go.Histogram(x=meditationTime, marker=dict(color='#351e15'))).update_layout(
        title='用户第一次登陆时间（24小时）', plot_bgcolor='rgba(0,0,0,0)'),
        style={'width': '50%', 'height': '40vh', 'display': 'inline-block'})
    return histogram

def meditation_time():
    df = pd.read_csv('Meditation.0.csv')
    meditationTime = []
    for x in df['timestamp__iso']:
        x = x.split('T')[1]
        x = x.split(':')[0]
        x = int(x) + 8  # time zone shift for 8 hours from ISO to Beijing Time
        if x > 23:
            x = x - 24
        meditationTime.append(x)
    histogram = dcc.Graph(figure=go.Figure(layout=layout).add_trace(
        go.Histogram(x=meditationTime, marker=dict(color='#351e15'))).update_layout(
        title='用户开始冥想的时间（24小时）', plot_bgcolor='rgba(0,0,0,0)'),
        style={'width': '50%', 'height': '40vh', 'display': 'inline-block'})
    return histogram

def discovery_time():
    df = pd.read_csv('Discovery.0.csv')
    discoveryTime = []
    for x in df['timestamp__iso']:
        x = x.split('T')[1]
        x = x.split(':')[0]
        x = int(x) + 8  # time zone shift for 8 hours from ISO to Beijing Time
        if x > 23:
            x = x - 24
        discoveryTime.append(x)
    histogram = dcc.Graph(figure=go.Figure(layout=layout).add_trace(go.Histogram(x=discoveryTime, marker=dict(color='#351e15'))).update_layout(
        title='用户开始探索的时间（24小时）', plot_bgcolor='rgba(0,0,0,0)'),
        style={'width': '50%', 'height': '40vh', 'display': 'inline-block'})
    return histogram

layout = go.Layout(
    margin=go.layout.Margin(
        l=40,  # left margin
        r=40,  # right margin
        b=10,  # bottom margin
        t=35  # top margin
    )
)
# ======================== Dash App
app = dash.Dash(__name__)
# ======================== App Layout
app.layout = html.Div([
    html.H1('Website Analytics Dashboard', style={'text-align': 'center', 'background-color': '#ede9e8'}),
    checkin_time(),
    meditation_time(),
    discovery_time()
])
if __name__ == '__main__':
    app.run_server()








