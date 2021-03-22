from skcriteria.madm import simple
from skcriteria import Data, MAX
import pandas as pd


def ranking_calculator(json_array):
    data_frame = pd.DataFrame(json_array)
    data_frame_copy = data_frame.copy()
    user_ids = list(data_frame['user_id'])
    del data_frame['user_id']
    data_frame = Data(data_frame, [MAX, MAX, MAX, MAX], weights=[50, 15, 15, 20], anames=user_ids, cnames=data_frame.columns)
    dm = simple.WeightedSum(mnorm="sum")
    data_frame_ranked = dm.decide(data_frame)
    data_frame_copy["rank"] = data_frame_ranked.rank_
    data_frame_copy = data_frame_copy.sort_values(by="rank", ascending=True)
    data_frame_copy = data_frame_copy['user_id'].tolist()
    return data_frame_copy

