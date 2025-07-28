from typing import List,Dict
from ..data_info import Datadic,Promptdic
from tqdm import tqdm
import re
def format_line_gsm8k(line: Dict) -> Dict:
    """
    从 GSM-8K 解析一条样本，提取 “#### <答案>” 的数字。

    Parameters
    ----------
    line : {"question": str, "answer": str, ...}

    Returns
    -------
    {"question": str, "answer": str}
    """
    _PATTERN = re.compile(r"^####\s*(-*[\d\.]+)\b", flags=re.M)
    m = _PATTERN.search(line["answer"])
    if m is None:
        raise ValueError("答案段落缺少以 '#### <number>' 结尾的行：\n" + line["answer"])

    return {
        "question": line["question"].strip(),
        "answer":   m.group(1).strip(),     # 只保留数字 / 小数
    }   
def format_line_math500(line:Dict) -> Dict:
    rec_=dict(
        question=line['question'],
        answer=line['answer']
        )
    return rec_

def format_line_aime(line:Dict) -> Dict:
    rec_=dict(
        question=line['question'],
        answer=line['answer']
        )
    return rec_

def format_line_gpqa(line:Dict) -> Dict:
    rec_=dict(
        question=line["question"],
        answer=line['choices'][0]
    )
    return rec_

def format_line_difficult(line:Dict) -> Dict:
    rec_=dict(
        question=line['question'],
        answer=line['answer']
        )
    return rec_

def form_question_line(title, description, input_format, output_format, note, examples, zero_shot=True):
    
    question = "Problem Title: " + title + '\n'
    question += "<Problem Description> " + description + '\n'
    if input_format is not None:
        question += "<input format> " + input_format + '\n'
    else:
        print(f"empty input_format {title}")
    if output_format is not None:
        question += "<output format> " + output_format + '\n'
    else:
        print(f"empty output_format {title}")

    if not zero_shot and examples:
        for i, ex in enumerate(examples):
            question += f"<example {i+1}>\nInput:\n{ex['input']}\nOutput:\n{ex['output']}\n"

    if note:
        question += "<notes> " + note + '\n'
    return question
def format_line_cf(line: Dict) -> Dict:
    rec_ = dict()
    rec_["extra_info"] = dict()
    

    for key, v in line.items():
        if key in ["contest_id", "rating", "tags", "testset_size", "input_mode", "executable"]:
            rec_["extra_info"][key]=v
        elif key == 'official_tests':
            rec_['answer'] = v

    rec_['question'] = form_question_line(
        line['title'],
        line['description'],
        line['input_format'],
        line['output_format'],
        line.get('note', ''),
        line.get('examples', []),
        zero_shot=True  # 或 False，看你是否想启用 example
    )
    return rec_



##这里注册
def data_format(name:str,records:List[Dict]) -> List[Dict]:
    records_formatted=[]
    match name:
        case 'aime24' | 'aime25':
            for idx,line in tqdm(enumerate(records),desc=f'loading from dataset: {name}'):
                rec_f=format_line_aime(line)
                rec_f['id']=idx
                records_formatted.append(rec_f)
        case 'math500':
            for idx,line in tqdm(enumerate(records),desc=f'loading from dataset: {name}'):
                rec_f=format_line_math500(line)
                rec_f['id']=idx
                records_formatted.append(rec_f)
        case 'gsm8k':
            for idx,line in tqdm(enumerate(records),desc=f'loading from dataset: {name}'):
                rec_f=format_line_gsm8k(line)
                rec_f['id']=idx
                records_formatted.append(rec_f)
        case 'gpqa_diamond'| 'gpqa':
            for idx,line in tqdm(enumerate(records),desc=f'loading from dataset: {name}'):
                rec_f=format_line_gpqa(line)
                rec_f['id']=idx
                records_formatted.append(rec_f)
        case 'merged_top90_filtered':
            for idx,line in tqdm(enumerate(records),desc=f'loading from dataset: {name}'):
                rec_f=format_line_difficult(line)
                rec_f['id']=idx
                records_formatted.append(rec_f)
        case 'deduped_questions_00_of_03':
            for idx,line in tqdm(enumerate(records),desc=f'loading from dataset: {name}'):
                rec_f=format_line_difficult(line)
                rec_f['id']=idx
                records_formatted.append(rec_f)
        case 'codeforces' :
            for idx,line in tqdm(enumerate(records),desc=f'loading from dataset: {name}'):
                rec_f=format_line_cf(line)
                if rec_f["question"] == None:
                    continue
                rec_f['id']=idx
                records_formatted.append(rec_f)
        case 'Post_Dataset_1':
            for idx,line in tqdm(enumerate(records),desc=f'loading from dataset: {name}'):
                rec_f=format_line_math500(line)  ## reuse preprocess function
                if rec_f["question"] == None:
                    continue
                rec_f['id']=idx
                records_formatted.append(rec_f)
        case _:
            raise NotImplementedError
        
    print(f"dataset: {name} formatted, proceed to the next stage")
    return records_formatted
        