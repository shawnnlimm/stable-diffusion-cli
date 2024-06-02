import os
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


def get_page_text(text_file):
    f = open(text_file, "r")
    l = f.readlines()
    l = [item.strip().strip('"') for item in l if item.strip()]
    keep = []

    for page_text in l:
        if "title" in page_text.lower():
            continue
        if "page" in page_text.lower():
            page_text = page_text.split(":")
            if len(page_text) > 1 and page_text[-1]:
                page_text = page_text[1].strip()
                keep.append(page_text)
        else:
            keep.append(page_text)
    return keep


if __name__ == "__main__":
    path_to_stories = "C:\\Users\\shawn\\Desktop\\krux\\stable-diffusion-cli\\stories"
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
            page_text = get_page_text(story_path)
            insert_story_text(df, story, page_text, i)
            insert_image_paths(df, story_dir, i)
            print(df)
    
    df.to_csv("illustrator.csv", index=False)
