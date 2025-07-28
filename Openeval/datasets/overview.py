# load_data.py
import re, json, glob
from tqdm import tqdm

def contains_chinese(text):
    return bool(re.search(r'[\u4e00-\u9fff]', text))

def load_summary(path_pattern="Openeval/datasets/test_data/*.jsonl"):
    Summarizer = {}
    file_list = glob.glob(path_pattern)
    for file_path in file_list:
        if 'overview' in file_path:
            continue
        with open(file_path, mode='r', encoding='utf-8') as f:
            details, count = [], 0
            has_chinese = False
            for i, line in tqdm(enumerate(f), desc=f"Scanning {file_path}"):
                obj = json.loads(line)
                details.append(obj)
                has_chinese |= contains_chinese(str(obj))
                count += bool(obj)
            name = file_path.split('/')[-1].split('.jsonl')[0]
            if name in Summarizer:
                raise ValueError(f"Duplicated filename: {name}")
            Summarizer[name] = dict(
                Dataset_Name=name,
                file_path=file_path,
                length=len(details),
                attr=list(details[0].keys()) if details else [],
                detail=details,
                Not_Null=count,
                Chinese=has_chinese,
            )
    return Summarizer
# Summarizer=load_summary()
if __name__ == "__main__":
    summary = load_summary()  # 运行脚本时生成
    idx=0
    
    with open("Openeval/datasets/overview.jsonl",mode="w",encoding="utf-8") as f:
        for name,attr in summary.items():
            f.write(json.dumps(attr['detail'][0],indent=4)+'\n')
            attr.pop('detail')
            f.write(json.dumps(attr)+'\n')
            idx+=1
            
        
    print('summarized done')