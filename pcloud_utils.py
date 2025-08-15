import os
import requests
from pcloud import PyCloud
from dotenv import load_dotenv
load_dotenv()

PCLOUD_EMAIL = os.getenv("PCLOUD_EMAIL")
PCLOUD_PASSWORD = os.getenv("PCLOUD_PASSWORD")

# Log in to pCloud
pc = PyCloud(PCLOUD_EMAIL, PCLOUD_PASSWORD)

def list_root():
    print("📂 Files in your root folder:")
    result = pc.listfolder(folderid=27208374529)
    files = result['metadata']['contents']
    for item in files:
        if not item.get('isfolder'):
            print(f" - {item['name']} (fileid: {item['fileid']})")
        else:
            print(f" 📁 {item['name']} (folder)")
    return files

def create_folder(folder_name):
    full_path = f"/{folder_name}"
    response = pc.createfolder(path=full_path)
    if response['result'] == 0:
        folder_id = response['metadata']['folderid']
        print(f"📁 Folder created: {folder_name} (ID: {folder_id})")
    elif response['result'] == 2004:  # Folder already exists
        list_resp = pc.listfolder(path=full_path)
        if list_resp.get("result") == 0 and "metadata" in list_resp:
            folder_id = list_resp['metadata']['folderid']
            print(f"📁 Folder already exists: {folder_name} (ID: {folder_id})")
        else:
            raise Exception(f"❌ Failed to list existing folder: {list_resp}")
    else:
        raise Exception(f"❌ Failed to create/access folder: {response}")
    return folder_id

def upload_file(folder_id, local_file_path):
    try:
        if not os.path.exists(local_file_path):
            raise Exception("File not found for upload")

        # Use standard upload instead of chunked upload
        result = pc.uploadfile(files=[local_file_path], folderid=folder_id)
        if result.get('result') != 0:
            raise Exception(f"Upload failed: {result.get('error', 'Unknown error')}")

        file = result['metadata'][0]
        print(f"✅ Uploaded: {file['name']} (fileid: {file['fileid']})")
        return file['fileid']
    except Exception as e:
        print(f"❌ Upload failed: {str(e)}")
        raise

def generate_share_link(file_id):
    resp = pc.session.get("https://api.pcloud.com/getfilepublink",
                          params={"fileid": file_id, "shortlink": 1})
    data = resp.json()
    if resp.status_code == 200 and data.get("result") == 0:
        link = data.get("link")
        linkid = data.get("linkid")
        if data.get("shortlink"):
            shortlink = data.get("shortlink")
        else:
            resp = pc.session.get("https://api.pcloud.com/changepublink",
                                  params={"linkid": linkid, "shortlink": 1})
            shortlink = resp.json().get("shortlink")
        link_data = {
            "link": link,
            "shortlink": shortlink,
            "linkid": linkid
        }
        return link_data
    else:
        raise Exception(f"❌ Failed to create public link: {data}")

def force_shortlink(linkid):
    resp = pc.session.get("https://api.pcloud.com/changepublink",
                          params={"linkid": linkid, "shortlink": 1})
    return resp.json().get("shortlink")

def delete_file(file_id):
    resp = pc.deletefile(fileid=file_id)
    if resp.get("result") == 0:
        print(f"🗑️ File deleted: fileid={file_id}")
    else:
        print(f"❌ Failed to delete: {resp}")

