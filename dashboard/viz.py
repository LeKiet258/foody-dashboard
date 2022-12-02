import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
import pdb

def review_seeding_ratio(vendor):
    # prepare data
    # res_id = 90018
    # vendor = data_hcm.loc[data_hcm['RestaurantId'] == res_id]
    fig = make_subplots(rows=1, cols=2, subplot_titles=['Tỷ lệ từng loại đánh giá của quán', 'Tỷ lệ quảng cáo'], 
                        specs=[[{"type": "pie"}, {"type": "pie"}]])
    pie_left_colors = ['rgb(244,165,130)', 'rgb(214,96,77)', 'rgb(178,24,43)', 'rgb(103,0,31)']
    pie_right_colors = ['rgb(33,102,172)', 'rgb(146,197,222)']

    # REVIEW RATE
    df = vendor[["nExcellentReviews", "nGoodReviews", "nAverageReviews", "nBadReviews"]]
    # pdb.set_trace()
    df = df.T#[[1]]
    df.rename(index={'nExcellentReviews': 'Tuyệt vời', 
                    'nGoodReviews': 'Tốt',
                    'nAverageReviews': 'Trung bình',
                    'nBadReviews': 'Tệ'}, inplace=True)
    df = df.reset_index()
    df.rename(columns={"index": "loại review", df.columns[1]: "số người"}, inplace=True)

    fig.add_trace(go.Pie(
            labels=df['loại review'], 
            values=df['số người'], 
            hovertemplate = "Đánh giá <b>%{label}</b><extra></extra>" + 
                            "<br>%{value} đánh giá", 
            sort=False, # plotly ko resort theo ý nó dc
            marker=dict(colors=pie_left_colors) # src: px.colors.sequential.RdBu
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
    fig.add_trace(go.Pie(
            labels=df_seeding['Loại'], 
            values=df_seeding['Tỷ lệ'], 
            hovertemplate = "%{label}<extra></extra>", 
            sort=False,
            marker=dict(colors=pie_right_colors)
        ),
        row=1, col=2
    )

    # đặt annotation cho pie trái
    x_base, y_base = 0.06, 0 #0.05, 0.15
    for i, lbl in enumerate(df['loại review']):
        fig.add_annotation({
            'x': x_base, 'y': y_base,
            'text': f"<b>▉</b> <span style='color:black'>{lbl}: {int(df.iloc[i,1])} đánh giá</span>", 'font': {'color': pie_left_colors[i], 'size':12}, #▇ ▉
            'xanchor': 'left', 'yanchor': 'middle', 'showarrow': False,
        })
        y_base -= 0.05

    # đặt annotation cho pie fải
    x_base, y_base = 0.62, 0 #0.05, 0.15
    for i, lbl in enumerate(df_seeding['Loại']):
        fig.add_annotation({
            'x': x_base, 'y': y_base,
            'text': f"<b>▉</b> <span style='color:black'>{lbl}: {int(df_seeding.iloc[i,1] * df['số người'].sum())}/{int(df['số người'].sum())} đánh giá</span>", 'font': {'color': pie_right_colors[i], 'size':12}, #▇ ▉
            'xanchor': 'left', 'yanchor': 'middle', 'showarrow': False,
        })
        y_base -= 0.05

    fig.update_layout(showlegend=False, width=800, height=510) 
    return fig
