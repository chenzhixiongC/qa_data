
from ann_search import FaissSearch
import pandas as pd
import sys
sys.path.append("../tools")
sys.path.insert(0, '..')
import faiss
from faiss import normalize_L2
from config import *
from time import time
import json

def load_js(path):
    dct = json.load(open(path, 'r', encoding='utf8'))
    return dct
print("Loading Data. Just once!")
start_time = time()
# id2answer = load_js(id2answer_json_path)
id2titles_df = pd.read_csv(id2title_path, sep=',')
qids = id2titles_df['qid'].tolist()
titles = id2titles_df['title'].tolist()
id2title = dict(zip(qids, titles))
index2id = load_js(index2id_path)
# id2category = pd.read_csv(id2category_path, sep=',')
print("Loading data Finished.")
print('Load Data. Cost:{:.3f}s'.format(time() - start_time))

def re_rank(candidate_indexes, candidate_distances, query_text, query_id=''):
    start_time = time()
    if verbose:
        print("re_rank")
    candidate_indexes = candidate_indexes[0]
    candidate_distances = candidate_distances[0]
    candidate_items = {}
    candidates = []
    if len(query_id.strip()) > 0:
        query_category = id2category[id2category['qid'] == query_id]['category'].values[0]
        for i, candidate_index in enumerate(candidate_indexes[:10]):
            candidate_qid = index2id[str(candidate_index)]
            candidate_category = id2category[id2category['qid'] == candidate_qid]['category'].values[0]
            candidate_answer = id2answer[candidate_qid]
            # 这里可以设置阈值，但是这里是过滤了跟问题不是同一个category的问题，所以如果还设置阈值的话可能导致返回的数据太少
            if candidate_category == query_category:
                if Set_threshold:
                    if candidate_distances[i] >= threshold:
                        candidate_items.update(
                            {candidate_qid: {'category': candidate_category, 'answer': candidate_answer,
                                             'sim': candidate_distances[i]}})
                else:
                    candidate_items.update({candidate_qid: {'category': candidate_category, 'answer': candidate_answer,
                                                            'sim': candidate_distances[i]}})
    else:
        candidate_qids = [index2id[str(item)] for item in candidate_indexes]

        for i, candidate_qid in enumerate(candidate_qids):
            if candidate_qid in qids:
                # candidate_answer = id2answer[candidate_qid]
                # candidate_category = id2category[id2category['qid'] == candidate_qid]['category'].values[0]
                sim = candidate_distances[i]
                candidate_title = id2title[candidate_qid]
                candidates.append((candidate_title, sim))
            else:
                assert False
                # break
    print('Re-rank. Cost:{:.3f}s'.format(time() - start_time))
    return candidates

if __name__ == '__main__':
    # pass
    fs = FaissSearch(ann_path=ann_path)
    # fs.train_ann_model(training_vectors=vector_path, dim=768, saved_path=ann_path)
    # id2answer = pd.read_csv(id2answer_path, skiprows=2)
    # id2answer = pd.read_csv(open(id2answer_path, 'rU'), encoding='utf-8', engine='c')

    # fs = FaissSearch(ann_path=ann_path)
    # vectors = np.load(vector_path)
    # bvg = BertVectorGenerator()
    # query_vector = bvg.sentence_embedding(['人站在地球上为什么没有头朝下的感觉'])


    data = pd.read_csv("test.csv")
    questions = list(data["原始问题"])
    target = list(data["Query"])
    # print(questions)
    # print(target)
    # for q in questions:
    #     print(q)
    # for q in target:
    #     print(q)
    # assert False
    result, target_site, sims, target_sim = [], [-1]*len(target), [],  [-1]*len(target)
    collect = []
    cnt = 0
    N = 5
    for i, query_text in enumerate(questions):
        # query_text = '人站在地球上为什么没有头朝下的感觉'
        # qid, flag, answer = check_query(query_text)
        candidate_indexes, distance_set = fs.ann_search_faiss(query=query_text,topn=N)
        # candidates = []
        # print(candidate_indexes, distance_set)
        # distance_set = distance_set[0]
        # candidate_qids = [index2id[str(item)] for item in candidate_indexes[0]]
        #
        # for i, candidate_qid in enumerate(candidate_qids):
        #     if candidate_qid in qids:
        #         # candidate_answer = id2answer[candidate_qid]
        #         # candidate_category = id2category[id2category['qid'] == candidate_qid]['category'].values[0]
        #         sim = distance_set[i]
        #         candidate_title = id2title[candidate_qid]
        #         candidates.append((candidate_title, sim))
        #     else:
        #         assert False


        print(candidate_indexes, distance_set)
        candidates = re_rank(candidate_indexes, distance_set, query_text)
        print(query_text)
        print(candidates)

        for j, c in enumerate(candidates):
            if target[i] == c[0]:
                target_site[i] = j
                target_sim[i] = c[1]
                cnt += 1
                break
        result.append(';'.join(['(' + str(x[0]) + ',' + str(x[1])+')' for x in candidates]))
    data["命中情况"] = result
    data["目标相似度"] = target_sim
    data["目标位置"] = target_site
    data.to_csv(f"top{N}result.csv")
    print(cnt/len(target))