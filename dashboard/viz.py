import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
import pdb
import numpy as np
from .utils import *

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

    fig = px.bar(user_score_df, x="index", y="freq", text_auto=True)
    custom_width = 1230 #800
    # if len(user_score.index) > 10:
    #     custom_width = 1230

    fig.update_layout(
        width=custom_width, # default 700
        paper_bgcolor='#FFFFFF',
        xaxis=dict(
            type='category',
            title=dict(text="Điểm")
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
        margin=dict(l=20, r=10) 
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
