import os
import json
from openai import OpenAI
from create_pdf import CustomPDF
from collections import defaultdict

def request(reference_text, prompt):
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("API key not found!")

    client = OpenAI(api_key=api_key)
    
    completion = client.chat.completions.create(
            model = "gpt-4o",
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt + reference_text},
            ]
    )

    response = completion.choices[0].message.content

    return response


def create_new_template(page_count, template_name):
    data = {}

    for i in range(page_count):
        data[i + 1] = {}
        data[i + 1]["content"] = []
    
    with open(template_name, "w") as f:
        json.dump(data, f)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    path_to_stories = "..\\stories"
    stories = os.listdir(path_to_stories)
    story_count = len(stories)
    template_name = "..\\template_1.json"
    sample_pdf = "..\\templates\\template_1.pdf"
    num_pages = CustomPDF(sample_pdf).get_num_pages()
    FRONT_MATTER_COUNT = 5
    BACK_MATTER_COUNT = 5

    create_new_template(num_pages, template_name)

    reformat_prompt = "Hello! I need you to help me reformat the following story lines. Specifically, I need you to help me format it by removing the lines containing the page number, keeping only the lines containing the page text. There should be no empty line between each lines. Remove the line containing the title if it exists. If the last line contains: The End, remove it too. Do not include any characters such as * and _. Do not include any additional response. I only need the story. For example, if the story contains 12 pages, you should only return me 12 lines. Here is the text to format:\n"

    questions_prompt = "You are a storybook writer, create me 4 short questions that can be asked to children aged 5 - 6 from this story to encourage good values. Structure in this format: Question <number>. For example, Question 1: What do you think... Just give me the 4 questions and do not include any additional information. Base it on this story:"

    back_page_prompt = "Give me a back page description for this story that is short, straightforward and engaging. The story is catered for 3 - 5 year olds. This description is for parents to learn what this story is about. Make it only 1 paragraph short."

    with open(template_name, "r") as f:
        data = json.load(f)

    with open("..\\misc_text.txt", "r") as f:
        l = f.readlines()
        misc_text = defaultdict(list)
        for item in l:
            item = item.strip()
            key = int(item[0])
            value = item.split(":")[1].strip()
            misc_text[key].append(value)
    
    for i in range(story_count):
        story = stories[i]
        story_dir = os.path.join(path_to_stories, story)
        if os.path.isdir(story_dir):
            data_path = os.path.join(story_dir, f"{story}.json")
            if not os.path.isfile(data_path):
                raise ValueError("Story json data file is missing!")
            with open(data_path, "r") as f:
                story_data = json.load(f)
            story_text = story_data["storyText"]
            formatted_text = request(story_text, reformat_prompt).splitlines()
            for page in range(num_pages):
                if page + 1 in misc_text:
                    for item in misc_text[page + 1]:
                        item = item.replace("\\n", "\n")
                        if "{NAME}" in item:
                            item = item.replace("{NAME}", story_data["inputs"]["characterName"])
                        if "{VALUE}" in item:
                            item = item.replace("{VALUE}", story_data["inputs"]["intendedValue"])
                        data[str(page + 1)]["content"].append({"type": "text", "data": item})

                if page == 0:
                    data[str(page + 1)]["content"].append({"type": "text", "data": story})
                    image_path = os.path.join(story_dir, "@P1.png")
                    data[str(page + 1)]["content"].append({"type": "image", "data": image_path})
                    data[str(page + 1)]["content"].append({"type": "image", "data": "..\\assets\\Title Circle.png"})
                    data[str(page + 1)]["content"].append({"type": "image", "data": "..\\assets\\Picolibo.png"})

                if page == 3:
                    data[str(page + 1)]["content"].append({"type": "image", "data":"..\\assets\\Blue Value Paint Stroke.png"})
                
                if 5 <= page <= 28:
                    if page % 2 == 1:
                        text = formatted_text[(page - FRONT_MATTER_COUNT) // 2]
                        data[str(page + 1)]["content"].append({"type": "text", "data": text})
                    else:
                        image_path = os.path.join(story_dir, f"@P{(page - FRONT_MATTER_COUNT + 1) // 2}.png")
                        data[str(page + 1)]["content"].append({"type": "image", "data": image_path})
                
                if page == 29:
                    questions = request(story_text, questions_prompt)
                    data[str(page + 1)]["content"].append({"type": "image", "data": "..\\assets\\Thinking Caps.png"})
                    data[str(page + 1)]["content"].append({"type": "text", "data": questions})

                if page == num_pages - 1:
                    back_text = request(story_text, back_page_prompt)
                    data[str(page + 1)]["content"].append({"type": "text", "data": back_text})
                    image_path = os.path.join(story_dir, "@P12.png")
                    data[str(page + 1)]["content"].append({"type": "image", "data": image_path})
                    data[str(page + 1)]["content"].append({"type": "image", "data": "..\\assets\\Back Page Circle.png"})
                    data[str(page + 1)]["content"].append({"type": "image", "data": "..\\assets\\Picolibo.png"})

            data["story_name"] = story
                  
            with open(template_name, "w") as f:
                json.dump(data, f, indent=4)
