import os
from openai import OpenAI
import pandas as pd

def insert_image_paths(df, story_dir, idx):
    cwd = os.getcwd()
    files = os.listdir(story_dir)
    for f in files:
        if f.endswith("png"):
            page_name = f.split(".")[0]
            full_path = os.path.join(os.path.join(cwd, story_dir),
            f"{page_name}.png")
            df.at[idx, page_name] = full_path


def insert_story_text(df, story, items, idx):
    df.at[idx, "TITLE"] = story
    df.at[idx, "VALUE1"] = "Resilience"
    df.at[idx, "VALUE2"] = "Courage"
    df.at[idx, "WRITER"] = "[Jane Doe]"
    df.at[idx, "TXT_BACK"] = items[-1]

    for i in range(len(items) - 1):
        if i < 9:
            df.at[idx, f"TXT0{i + 1}"] = items[i]
        else:
            df.at[idx, f"TXT{i + 1}"] = items[i]


def create_df(num_pages):
    # Define the column names
    columns = [
        "TITLE", "VALUE1", "VALUE2", "WRITER", "@COVER"
    ]

    # Add columns for images and text
    for i in range(num_pages):
        columns.append(f"@P{i + 1}")
    columns.append("@BACK")
    for i in range(num_pages):
        if i < 9:
            columns.append(f"TXT0{i + 1}")
        else:
            columns.append(f"TXT{i + 1}")
    columns.append(f"TXT_BACK")

    df = pd.DataFrame(columns=columns)
    return df


def reformat(text_file):
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("API key not found!")

    client = OpenAI(api_key=api_key)
    f = open(text_file, "r")
    l = f.read()
    content = "Hello! I need you to help me reformat the following text file. Specifically, I need you to help me format it by removing the lines containing the page number, keeping only the lines containing the page text. There should be no empty line between each lines. Remove the line containing the title if it exists. Do not include any characters such as * and _. Add a line called: The End if it does not already exist. Do not include any additional response. I only need the story. Here is the text to format:\n" + l
    
    completion = client.chat.completions.create(
            model = "gpt-4o",
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": content},
            ]
    )

    response = completion.choices[0].message.content
    result = response.splitlines()
    return result


if __name__ == "__main__":
    # path_to_stories = "C:\\Users\\shawn\\Desktop\\krux\\stable-diffusion-cli\\stories"
    path_to_stories = "C:\\Users\\User\\Desktop\\stable-diffusion-cli\\stories"
    df = create_df(12)
    stories = os.listdir(path_to_stories)
    story_count = len(stories)

    for i in range(story_count):
        story = stories[i]
        story_dir = os.path.join(path_to_stories, story)
        if os.path.isdir(story_dir):
            story_path = os.path.join(story_dir, f"{story}_story.txt")
            # Check if _story.txt exist
            if not os.path.isfile(story_path):
                raise ValueError("Story text file is missing!")
            formatted_text = reformat(story_path)
            insert_story_text(df, story, formatted_text, i)
            insert_image_paths(df, story_dir, i)
            
    df.to_csv("illustrator.csv", index=False)

