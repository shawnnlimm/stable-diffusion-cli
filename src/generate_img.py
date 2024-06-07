from txt2img import txt2img
from kdiffusion import samplers_k_diffusion
import os
import json
import re
from pathlib import Path

'''
samplers = [
    "Euler a",
    "Euler",
    "LMS",
    "Heun", # very similar
    "DPM2",
    "DPM2 a", # very similar
    "DPM++ 2S a",
    "DPM++ 2M",
    "DPM++ SDE", 
    "DPM++ 2M SDE",
    "DPM fast", # very similar
    "DPM adaptive",
    "LMS Karras",
    "DPM2 Karras",
    "DPM2 a Karras", # TODO: completely different
    "DPM++ 2S a Karras",
    "DPM++ 2M Karras",
    "DPM++ SDE Karras", # very similar
    "DPM++ 2M SDE Karras",
]
'''

def run_generation(params):
        # Generate image
        model_name = params["sd_checkpoint"]
        prompt = params["prompt"]
        negative_prompt = params["negative_prompt"] 
        sampling_steps= params["sampling_steps"]
        cfg_scale = params["cfg_scale"]
        width = params["width"]
        height = params["height"]
        sampling_method = params["sampling_method"]
        seed = params["seed"]

        image = txt2img(
            checkpoint=model_name,
            positive=prompt,
            negative=negative_prompt,
            steps=sampling_steps,
            width=width,
            height=height,
            cfg_scale=cfg_scale,
            sampler_name=sampling_method,
            seed=seed,
            randn_source="gpu"
        )

        return image


def save_image(image, story_name, page_name):
    cwd = os.getcwd()
    Path(".\\output").mkdir(parents=True, exist_ok=True)

    # Save to output folder if not generating for stories
    if not story_name: 
        image_path = os.path.join(cwd, "output\\sample.png") 
        image.save(image_path)

    # Save to stories folder
    else:
        image_path = os.path.join(cwd, f"stories\\{story_name}\\{page_name}.png")
        # Save only if image has not been generated before
        if not os.path.exists(image_path):
            image.save(image_path)


def generate_story_images(params, story_name, story_path):
    f = open(story_path, "r")
    l = f.read()
    l = re.sub("'", '"', l)
    parsed_lines = re.findall(r'"(.*?)"', l)
    story_name = story_name.replace("_prompt", "")
    LORA_NAME = "<lora:COOLKIDS_MERGE_V2.5:1>"
    fixed_prompt = "3 years old, (solo:1.5), black_hair"

    for i in range(len(parsed_lines)):
        image_path = os.path.join(cwd, "stories", story_name, f"@P{i + 1}.png")
        if os.path.exists(image_path):
            continue
        prompt = parsed_lines[i]
        prompt += " " + fixed_prompt # + LORA_NAME
        params["prompt"] = prompt
        params["page_name"] = f"@P{i + 1}"
        params["story_name"] = story_name 

        with open("params.json", "w") as f:
            json.dump(params, f, indent=4)
        
        result = run_generation(params)
        save_image(result, params["story_name"], params["page_name"])


def run(dir):
    with open("params.json", "r") as f:
        params = json.load(f)
    
    stories = os.listdir(dir)
    if not stories:
        results = run_generation(params)
        save_image(results, "", "")
    for story in stories:
        story_path = os.path.join(dir, story)
        if os.path.isdir(story_path):
            for f in os.listdir(story_path):
                if f.endswith(".txt") and "_prompt" in f:
                    generate_story_images(params, os.path.splitext(f)[0], os.path.join(story_path, f))


if __name__ == "__main__":
    path_to_downloads = "C:\\Users\\shawn\\Downloads"
    path_to_stories = "C:\\Users\\shawn\\Desktop\\krux\\stable-diffusion-cli\\stories"
    # path_to_downloads = "C:\\Users\\User\\Downloads"
    # path_to_stories = "C:\\Users\\User\\Desktop\\stable-diffusion-cli\\stories"
    cwd = os.getcwd()

    # Move any prompts and stories in downloads folder to new folder
    for f in os.listdir(path_to_downloads):
        if f.endswith(".txt") and ("_prompt" in f or "_story" in f):
            path = os.path.join(path_to_downloads, f)
            base = f.split("_")[0]
            story_dir = os.path.join(path_to_stories, base)
            if not os.path.exists(story_dir):
               os.makedirs(story_dir)
            os.replace(path, os.path.join(story_dir, f))

    story_dir = "C:\\Users\\shawn\\Desktop\\krux\\stable-diffusion-cli\\stories"
    #story_dir = "C:\\Users\\User\\Desktop\\stable-diffusion-cli\\stories"

    run(story_dir)

