from typing import List, OrderedDict
import re
from retrying import retry
import json
import json5
from utils.app_types import BaseQuestion, AssetItem
from utils.llm import call_gpt_v, LLMHandler


IMAGE_PROMPT = """
You are a wonderful architectural designer. Based on the image, fill the following JSON questionaire about architecture design:
```json
{questionaire}
```
"""

TEXT_PROMPT = """
You are a wonderful architectural designer. Based on the text, fill the following JSON questionaire about architecture design. If not applicable, leave it empty.
```json
{questionaire}
```

Your text:
{content}
"""

@retry(wait_fixed=2000, stop_max_attempt_number=3)
def image_inqury(image_path: str, 
                 questions: List[BaseQuestion],
                 case_id: int,
                 ) -> AssetItem:
    
    # add a question
    questions.append(BaseQuestion("category", "Category of this image. Choose from: facade, interior, floorplan, section, detail, birdview, other"))

    # prepare the prompt
    questionaire = {q.theme: q.content for q in questions}
    prompt = IMAGE_PROMPT.format(questionaire=questionaire)

    # call the model
    response = call_gpt_v(image_path, prompt)
    json_text = re.findall(r'```json(.*)```', response, re.DOTALL)[-1]
    json_dict = json.loads(json_text)

    # prepare the result
    answers = OrderedDict()
    for idx, item in enumerate(json_dict.items()):
        answers[questions[idx]] = item[1]
    category = json_dict["category"]
    return AssetItem(case_id, str(image_path), category, answers)


@retry(wait_fixed=2000, stop_max_attempt_number=3)
def text_inquiry(text_path: str, 
                 questions: List[BaseQuestion],
                 case_id: int,
                 ) -> AssetItem:
    
    # read the text file using utf-8 encoding
    with open(text_path, "r", encoding="utf-8") as f:
        text = f.read()

    # prepare the prompt
    questionaire = {q.theme: q.content for q in questions}
    prompt = TEXT_PROMPT.format(questionaire=questionaire, content=text)

    # call the model
    llm_handler = LLMHandler()
    response = llm_handler.chat_with_gpt(prompt)
    json_text = re.findall(r'```json(.*)```', response, re.DOTALL)[-1]
    json_dict = json5.loads(json_text)

    # prepare the result
    answers = OrderedDict()
    for idx, item in enumerate(json_dict.items()):
        answers[questions[idx]] = item[1]
    return AssetItem(case_id, str(text_path), "text", answers)



if __name__ == "__main__":
    questions = [BaseQuestion("highlights", "What is the highlight of this design?"),
                 BaseQuestion("shape", "What form does it use? "),
                 BaseQuestion("spatial design", "What is the highlight of its shape and form? "),
                 BaseQuestion("material design", "What is the highlight in its spatial and material design?"),
                 ]

    image_path = r"D:\Code\RecArch\static\database\China\Shanghai IAG Art Museum\detail.jpg"
    text_path = r"D:\Code\RecArch\static\database\China\Shanghai IAG Art Museum\description.txt"
    case_id = 1
    # result = image_inqury(image_path, questions, case_id)
    result = text_inquiry(text_path, questions, case_id)
    print(result)
