from pymongo import MongoClient
import pandas as pd

client = MongoClient('mongodb://localhost:27017/')
patent_db = client['patent_db']
patent_col = patent_db['patent_col']

pipeline = [{
    '$unwind': '$applicantName'
}, {
    '$group': {
        "_id": {
            "patentType": "$patentType",
            "applicantName": "$applicantName",
            "year": {
                "$year": "$pubDate"
            },
            "month": {
                "$month": "$pubDate"
            }
        },
        "count": {
            "$sum": 1
        }
    }
}]

res_list = list(patent_col.aggregate(pipeline))
for i in res_list:
  i['_id'].update({'count': i['count']})
  # if i['count'] >1:
  #   break
res_parsed_list = [i['_id'] for i in res_list]
res_df = pd.DataFrame(res_parsed_list)[[
    'patentType', 'applicantName', 'year', 'month', 'count'
]]
res_df.to_csv('sample.csv', index=False)
