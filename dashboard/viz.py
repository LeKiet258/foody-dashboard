import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
import pdb
import numpy as np
from .utils import *
import textwrap

def compare_component_score(vendor):
    vendor1 = vendor.iloc[[0]]
    vendor2 = vendor.iloc[[1]]

    df1 = vendor1[['LocationScore', 'PriceScore', 'QualityScore', 'ServingScore', 'SpaceScore']].T.rename(index={
        'LocationScore': 'Điểm vị trí', 'PriceScore': 'Điểm giá cả', 'QualityScore': 'Điểm chất lượng',
        'ServingScore': 'Điểm phục vụ', 'SpaceScore': 'Điểm không gian'
    }).reset_index()
    df1.rename(columns={df1.columns[1]: 'score'}, inplace=True)
    df2 = vendor2[['LocationScore', 'PriceScore', 'QualityScore', 'ServingScore', 'SpaceScore']].T.rename(index={
        'LocationScore': 'Điểm vị trí', 'PriceScore': 'Điểm giá cả', 'QualityScore': 'Điểm chất lượng',
        'ServingScore': 'Điểm phục vụ', 'SpaceScore': 'Điểm không gian'
    }).reset_index()
    df2.rename(columns={df2.columns[1]: 'score'}, inplace=True)

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=df1['score'], theta=df1['index'], fill='toself', hovertemplate="%{r}<extra></extra>", 
                                name=vendor1['Name'].iloc[0]))
    fig.add_trace(go.Scatterpolar(r=df2['score'], theta=df2['index'], fill='toself', hovertemplate="%{r}<extra></extra>", 
                                name=vendor2['Name'].iloc[0]))
    fig.update_layout(
        width=750,
        showlegend=True,
        legend = dict(itemclick='toggleothers'), # click legend nào thì chỉ legend đó visible
        title = {
            'text': "<b>So sánh điểm thành phần</b>",
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 23, 'family': 'Arial'}
        },
        margin=dict(t=100) # nới space between title & chart
    )

    return fig

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def compare_user_score(vendor):
    reviews = vendor['Reviews'].to_list() # len: 2
    user_scores = []

    for i in range(2):
        review = eval(reviews[i])

        # chuẩn bị dataframe lquan tới review từ data JSON 
        review_dict ={'Usernames': [], 'Date': [], 'Title': [], 'Body': [], 'is_returned': [], 'User_score': []}
        for single_rv in review:
            for k in review_dict.keys():
                review_dict[k].append(single_rv[k])

        review_df = pd.DataFrame.from_dict(review_dict)
        review_df['User_score'] = review_df['User_score'].astype(float)
        review_df['is_returned'] = review_df['is_returned'].astype(bool)
        review_df = review_df[review_df['User_score'] != 0] # loại các review có đánh giá 0.0 vì đa fần là qc
        user_score = review_df['User_score'].value_counts()#.sort_index()
        user_scores.append(user_score)
    intervals = [[1, 2], [2,3], [3, 4], [4,5], [5, 6], [6,7], [7, 8], [8,9], [9, 10]]
    scores = list(set(user_scores[0].index).union(set(user_scores[1].index)).union(set(np.arange(1,11))))
    res_names = [vendor.iloc[0,3], vendor.iloc[1,3]]
    tmp_dict = {'score': scores, res_names[0]: [], res_names[1]: []}
    for score in scores:
        for i in range(2):
            freq = user_scores[i][score] if score in user_scores[i].index else 0
            tmp_dict[res_names[i]].append(freq)
    user_score_df = pd.DataFrame.from_dict(tmp_dict).sort_values(by=['score'])

    tmp_dict = {'group': [], 'label': [], 'value': []}
    for score in scores:
        for i in range(2):
            tmp_dict['group'].append(i+1)
            tmp_dict['label'].append(score)
            freq = user_scores[i][score] if score in user_scores[i].index else 0
            tmp_dict['value'].append(freq)
    user_score_df = pd.DataFrame.from_dict(tmp_dict)#.sort_values(by=['group'], kind='stable')

    score_interval_df = pd.DataFrame()
    for interval in intervals[:-1]:
        tmp_df = user_score_df[(interval[0] <= user_score_df['label']) & (user_score_df['label'] < interval[1])].groupby('group')[['value']].sum().reset_index()
        tmp_df['label'] = f"[{interval[0]}, {interval[1]})"
        score_interval_df = pd.concat([score_interval_df, tmp_df])
    # final range
    interval = intervals[-1]
    tmp_df = user_score_df[(interval[0] <= user_score_df['label']) & (user_score_df['label'] <= interval[1])].groupby('group')[['value']].sum().reset_index()
    tmp_df['label'] = str(interval)
    score_interval_df = pd.concat([score_interval_df, tmp_df])

    # final process
    score_interval_df = score_interval_df.sort_values(by=['group'], kind='stable')
    score_interval_df['group'] = score_interval_df['group'].astype(str)

    fig = px.bar(
        score_interval_df,
        y="label",
        x="value",
        facet_col="group",
        facet_col_spacing=10 ** -9,
        color="group",
        color_discrete_sequence=["#4472c4", "#ed7d31"],
    )

    # add hovertemplate
    for i in range(2):
        fig.data[i]['hovertemplate'] = process_review_px(vendor['Reviews'].iloc[i])

    fig.update_layout(
        width=750,
        height=450,
        margin=dict(t=120), 
        yaxis2={"side": "right", "matches": None, "showticklabels": False},
        yaxis={"showticklabels": True, 'title': "Khoảng điểm"}, # tune this
        xaxis={"autorange": "reversed", 'range': [0, score_interval_df['value'].max()], 
            "title": {"text": ""}},
        xaxis2={"matches": None, 'range': [0, score_interval_df['value'].max()], 'title': ''},
        showlegend=False,
        title = {
            'text': "<b>So sánh điểm của 2 quán ăn</b>",
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 23, 'family': 'Arial'}
        },
    )

    res_names = [None, vendor.iloc[0,3], vendor.iloc[1,3]]
    fig.for_each_annotation(lambda a: a.update(text = res_names[int(a.text[-1])]))

    # x_base, y_base = 0.06, 0 #0.05, 0.15
    fig.add_annotation(dict(
        font=dict(size=15),
        x=0.45,
        y=-0.15,
        showarrow=False,
        text="Số người",
        textangle=0,
        xanchor='left',
        xref="paper",
        yref="paper"))

    return fig

def compare_seeding(vendor):
    res_name1, res_name2 = vendor.iloc[0,3], vendor.iloc[1,3]
    vendor = vendor[['seeding_pct', 'TotalReviews']]
    vendor.rename(index={vendor.index[0]: res_name1,
                         vendor.index[1]: res_name2}, 
              inplace=True)
    seeding_reviews = round(vendor['seeding_pct'] * vendor['TotalReviews'])
    y_data = [] 
    for i, vendor_name in enumerate(vendor.index):
        y_data.append('<br>'.join(textwrap.wrap(vendor.index[i], 33)))

    fig = go.Figure([go.Bar(
        y=y_data, 
        x=vendor['seeding_pct'],
        orientation='h',
        marker=dict(color='rgb(33,102,172)'),
        customdata= seeding_reviews,
        hovertemplate="%{customdata} đánh giá<extra></extra>"
    )])

    fig.update_layout(
        # annotations=annotations,
        xaxis=dict(
            tickformat=".0%",
            domain=[0.15, 1]
        ),
        title = {
            'text': "<b>So sánh tỷ lệ quảng cáo trong phần đánh giá</b>",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 23, 'family': 'Arial'}
        },
        yaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            zeroline=False,
        ),
        margin=dict(l=120, r=10, t=140, b=80) # set margin của figure bự ra
    )

    annotations = []
    for yd, xd in zip(y_data, vendor['seeding_pct']):
        # labeling the y-axis
        annotations.append(dict(xref='paper', yref='y',
                                x=0.14, y=yd, # x càng tăng chữ càng sít vào bar
                                xanchor='right', # right alignment
                                text=str(yd),
                                font=dict(family='Arial', size=14,
                                        color='rgb(67, 67, 67)'),
                                showarrow=False, align='right'))
    fig.update_layout(annotations=annotations, width=750)
    
    return fig

def compare_review_type(vendor):
    res_name1, res_name2 = vendor.iloc[0,3], vendor.iloc[1,3]
    vendor = vendor[["nExcellentReviews", "nGoodReviews", "nAverageReviews", "nBadReviews"]]
    total_reviews = vendor.sum(axis=1)
    for column in vendor.columns:
        vendor[f'{column}_pct'] = round(vendor[f'{column}'] / total_reviews * 100, 2)
    vendor.rename(index={vendor.index[0]: res_name1,
                         vendor.index[1]: res_name2},
                  inplace=True)
    top_labels = vendor.columns
    colors = ['rgba(244,165,130, 0.8)', 'rgba(214,96,77, 0.8)', 'rgba(178,24,43, 0.8)', 'rgba(103,0,31, 0.85)']
    x_data = vendor[['nExcellentReviews_pct', 'nGoodReviews_pct', 'nAverageReviews_pct', 'nBadReviews_pct']].to_numpy()
    hoverinfo_ls = vendor[['nExcellentReviews', 'nGoodReviews', 'nAverageReviews', 'nBadReviews']].to_numpy()
    y_data = [] 
    for i, vendor_name in enumerate(vendor.index):
        y_data.append('<br>'.join(textwrap.wrap(vendor.index[i], 33)))
            
    fig = go.Figure()

    for i, col in enumerate(['Tuyệt vời', 'Tốt', 'Trung bình', 'Tệ']): # range(0,4)
        for j, (xd, yd) in enumerate(zip(x_data, y_data)): # loop through 2 vendor
            fig.add_trace(go.Bar(
                x=[xd[i]], y=[yd],
                orientation='h',
                marker=dict(
                    color=colors[i],
                    line=dict(color='rgb(248, 248, 249)', width=1) # seperate line
                ),
                customdata = [[hoverinfo_ls[j,i], col]], # shape: 1,2
                hovertemplate = "%{customdata[0]} đánh giá <b>%{customdata[1]}</b> <extra></extra>",
                showlegend = True if j == 0 else False,
                name= col if j==0 else None,
                textposition='inside', texttemplate=f'{xd[i]}%', insidetextanchor='middle'
            ))
            # if xd[i] > 5:
            #     print(xd[i])
            #     fig.update_traces(textposition='inside', texttemplate=f'{xd[i]}%', insidetextanchor='middle')

    fig.update_layout(
        xaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            zeroline=False,
            domain=[0.15, 1]
        ),
        yaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            zeroline=False,
        ),
        barmode='stack',
        paper_bgcolor='rgb(255, 255, 255)',
        plot_bgcolor='rgb(228, 235, 247)',
        margin=dict(l=120, r=10, t=140, b=80),
        showlegend=True,
    )

    annotations = []

    for yd, xd in zip(y_data, x_data):
        # labeling the y-axis
        annotations.append(dict(xref='paper', yref='y',
                                x=0.14, y=yd, # x càng tăng chữ càng sít vào bar
                                xanchor='right', # right alignment
                                text=str(yd),
                                font=dict(family='Arial', size=14,
                                        color='rgb(67, 67, 67)'),
                                showarrow=False, align='right'))

    fig.update_layout(
        annotations=annotations,
        width=750,
        title = {
            'text': "<b>So sánh tỷ lệ từng loại đánh giá</b>",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 23, 'family': 'Arial'}
        },
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    return fig              

def component_score(vendor):
    df = vendor[['LocationScore', 'PriceScore', 'QualityScore', 'ServingScore', 'SpaceScore']].T.rename(index={
        'LocationScore': 'Điểm vị trí', 'PriceScore': 'Điểm giá', 'QualityScore': 'Điểm chất lượng',
        'ServingScore': 'Điểm phục vụ', 'SpaceScore': 'Điểm không gian'
    }).reset_index()
    df.rename(columns={df.columns[1]: 'score'}, inplace=True)

    fig = px.line_polar(df, r='score', theta='index', line_close=True)
    fig.update_traces(hovertemplate="%{r}")
    fig.update_layout(
        width=500,
        title = {
            'text': "<b>Điểm thành phần</b>",
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 23, 'family': 'Arial'}
        },
        margin=dict(t=100) # nới space between title & chart
    )
    return fig

def user_score_bar(vendor):
    review = vendor['Reviews'].to_list()
    if pd.isnull(review[0]):
        return -1

    review = eval(review[0])
    review_dict ={'Usernames': [], 'Date': [], 'Title': [], 'Body': [], 'is_returned': [], 'User_score': []}
    for single_rv in review:
        for k in review_dict.keys():
            review_dict[k].append(single_rv[k])

    review_df = pd.DataFrame.from_dict(review_dict)
    review_df['User_score'] = review_df['User_score'].astype(float)
    review_df['is_returned'] = review_df['is_returned'].astype(bool)
    review_df = review_df[review_df['User_score'] != 0] # loại các review có đánh giá 0.0 vì đa fần là qc
    user_score = review_df['User_score'].value_counts().sort_index()
    
    user_score_ix = [int(i) for i in user_score.index]
    visible_scores = user_score
    if len(user_score_ix) < 10:
        ten_scores = [i for i in range(11)]
        visible_score = set(ten_scores).difference(set(user_score_ix))
        visible_score_dict = {}
        for s in visible_score:
            visible_score_dict[s] = 0

        visible_scores = pd.concat([user_score, pd.Series(data=visible_score_dict)]).sort_index()

    user_score_df = pd.DataFrame.from_dict({'freq': visible_scores}).reset_index()
    user_score_df['index'] = user_score_df['index'].astype(str)
    review_df['Body'] = review_df['Body'].apply(normalize_review)
    review_df = review_df.drop_duplicates("Body")
    # Mỗi điểm lấy 3 comment mới đây nhất làm đại diện
    review_df = review_df.groupby('User_score').head(3).sort_values(['User_score', 'Date'], ascending=False)
    review_df = review_df.sort_values('User_score')

    scores = user_score_df['index'].astype(float).to_list()
    hoverinfo_ls = [np.nan] * len(scores)
    for j, sc in enumerate(scores):
        tmp = review_df.loc[review_df['User_score'] == sc, 'Body']
        if not tmp.empty:
            tmp = tmp.to_list()
            for i in range(len(tmp)):
                if len(tmp[i]) > 1500:
                    tmp[i] = tmp[i][:1500] + "..(còn nữa)"
                tmp[i] = '<br>'.join(textwrap.wrap(tmp[i], 150))
            hoverinfo_ls[j] = '<br><br>'.join(tmp)

    fig = go.Figure()
    color=np.array(['#007bff'] * visible_scores.index.size)
    color[visible_scores.index < 6]='#EB1A14'
    fig.add_trace(go.Bar(
        x=user_score_df['index'],
        y=user_score_df['freq'],
        textposition='auto', textangle=0, texttemplate="%{y}",
        marker_color=color,
        customdata=hoverinfo_ls,
        hovertemplate="%{customdata}<extra></extra>",
    ))

    fig.update_layout(
        showlegend=False,
        hovermode='closest', # siết hover box vào nội bộ bên trong fig
        width=1000,
        xaxis=dict(
            title=dict(text="Điểm"),
        ), 
        yaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            zeroline=False,
            title=dict(text="Số đánh giá")
        ),
        title = {
            'text': f"<b>Điểm số đánh giá của {user_score.sum()} người</b>",
            'y':0.97,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 23, 'family': 'Arial'}
        },
        margin=dict(l=20, r=10, t=50, b=30),
    )
    return fig

def menu_bar(dish_price_df):
    # df = dish_price_df
    # pdb.set_trace()
    hoverinfo_df = dish_price_df.copy()
    dish_price_df = dish_price_df.groupby('dish_type_name').agg({'dish_price_value': ['min', 'max']})['dish_price_value'].sort_index()
    dif = dish_price_df['max'] - dish_price_df['min']
    ix_dif_0 = dif[dif == 0].index
    dish_price_df.loc[ix_dif_0, 'max'] = dish_price_df.loc[ix_dif_0, 'max'] + 200 # tránh TH max-min = 0

    # preprocess hoverinfo_df
    hoverinfo_ls = []
    dish_type_ls = list(hoverinfo_df['dish_type_name'].unique())

    for dish_type in sorted(dish_type_ls):
        s = ""
        info_df = hoverinfo_df.loc[hoverinfo_df['dish_type_name'] == dish_type, ['dish_name', 'dish_price_value']].sort_values('dish_price_value')
        for k, v in info_df['dish_name'].to_dict().items():
            price = reduce_price(info_df['dish_price_value'][k])
            s += f"{v}: {price}<br>"
        hoverinfo_ls.append(s)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        orientation='h', x=dish_price_df['max'] - dish_price_df['min'], y=dish_price_df.index, base=dish_price_df['min'],
        customdata = hoverinfo_ls,
        hovertemplate='%{customdata}<extra></extra>',
    ))
    fig.update_layout(
        width=850, # size of chart
        margin=dict(t=90, b=10, l=5, r=20), # size of figure
        paper_bgcolor='#FFFFFF',
        title = {
            'text': "<b>Thực đơn</b>",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 23, 'family': 'Arial'}
        },
    )

    return fig

def review_seeding_ratio(vendor):
    # prepare data
    fig = make_subplots(rows=1, cols=2, subplot_titles=['<b>Tỷ lệ từng loại đánh giá<br>của quán</b>', '<b>Tỷ lệ quảng cáo</b>'], 
                    specs=[[{"type": "pie"}, {"type": "pie"}]])
    pie_left_colors = ['rgb(244,165,130)', 'rgb(214,96,77)', 'rgb(178,24,43)', 'rgb(103,0,31)']
    pie_right_colors = ['rgb(33,102,172)', 'rgb(146,197,222)']

    # REVIEW RATE
    df = vendor[["nExcellentReviews", "nGoodReviews", "nAverageReviews", "nBadReviews"]]
    df = df.T
    df.rename(index={'nExcellentReviews': 'Tuyệt vời', 
                    'nGoodReviews': 'Tốt',
                    'nAverageReviews': 'Trung bình',
                    'nBadReviews': 'Tệ'}, inplace=True)
    df = df.reset_index()
    df.rename(columns={"index": "loại review", df.columns[1]: "số người"}, inplace=True)
    df['pct'] = (round(df['số người'] / df['số người'].sum(), 2) * 100)
    df['pct'] = df['pct'].apply(lambda val: np.nan if val==0 else str(int(val))+'%')

    fig.add_trace(go.Pie(
            labels=df['loại review'], 
            values=df['số người'], 
            hovertemplate = "Đánh giá <b>%{label}</b><extra></extra>" + 
                            "<br>%{value} đánh giá", 
            sort=False, # plotly ko resort theo ý nó dc
            marker=dict(colors=pie_left_colors), # src: px.colors.sequential.RdBu
            text = df['pct'],
            textinfo = 'text'
        ),
        row=1, col=1
    )

    # SEEDING RATE
    df_seeding = vendor[["seeding_pct"]]
    df_seeding = df_seeding.T#[[1]]#.iloc[0,0]
    df_seeding = df_seeding.rename(index={'seeding_pct': 'Quảng cáo'}, 
                                columns={df_seeding.columns[0]: "Tỷ lệ"})\
                            .reset_index().rename(columns={'index': 'Loại'})
    df_seeding.loc[1] = ["Trung thực", 1 - df_seeding.iloc[0, 1]]
    hoverinfo_ls = round(vendor['TotalReviews'].iloc[0] * df_seeding['Tỷ lệ']).to_list() # [qc, trung thực]
    fig.add_trace(go.Pie(
            labels=df_seeding['Loại'], 
            values=df_seeding['Tỷ lệ'], 
            customdata=hoverinfo_ls,
            hovertemplate = "%{customdata} đánh giá <b>%{label}</b><extra></extra>", 
            sort=False,
            marker=dict(colors=pie_right_colors)
        ),
        row=1, col=2
    )

    # đặt annotation cho pie trái
    x_base, y_base = 0.04, 0 #0.05, 0.15
    for i, lbl in enumerate(df['loại review']):
        fig.add_annotation({
            'x': x_base, 'y': y_base,
            'text': f"<b>▉</b> <span style='color:black'>{lbl}: {int(df.iloc[i,1])} đánh giá</span>", 'font': {'color': pie_left_colors[i], 'size':12}, #▇ ▉
            'xanchor': 'left', 'yanchor': 'middle', 'showarrow': False,
        })
        y_base -= 0.06

    # đặt annotation cho pie fải
    x_base, y_base = 0.62, 0 #0.05, 0.15
    for i, lbl in enumerate(df_seeding['Loại']):
        fig.add_annotation({
            'x': x_base, 'y': y_base,
            'text': f"<b>▉</b> <span style='color:black'>{lbl}: {int(hoverinfo_ls[i])}/{int(df['số người'].sum())} đánh giá</span>", 'font': {'color': pie_right_colors[i], 'size':12}, #▇ ▉
            'xanchor': 'left', 'yanchor': 'middle', 'showarrow': False,
        })
        y_base -= 0.06

    fig.update_layout(
        showlegend=False, 
        width=690, 
        height=450, 
        # paper_bgcolor='#B9B5B4',
        uniformtext_minsize=10, uniformtext_mode='hide',
    ) 
    return fig
