import json


def write_json(new_data, filename='test1.json'):
    with open(filename, 'r+') as file:
        file_data = json.load(file)
        highest_ID = max(file_data["posts"], key=lambda ev: ev["postID"])
        keys = file_data["posts"]
        new_post_ID = highest_ID["postID"] + 1
        print(new_post_ID)
        new_data["postID"] = new_post_ID
        print(new_data)
        file_data["posts"].append(new_data)
        file.seek(0)
        json.dump(file_data, file, indent=4)


write_json({"postID": 'post_ID', "number posts by this account": 0, "account name": "anonymous", "postContents": 'Try number 4: Epic style'})