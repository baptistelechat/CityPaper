import os
from pathlib import Path
from huggingface_hub import HfApi, HfFileSystem
from .config import HF_TOKEN, HF_REPO_ID

class HuggingFaceClient:
    def __init__(self):
        if not HF_TOKEN:
            print("⚠️  HF_TOKEN missing. Uploads will be skipped.")
            self.api = None
            return
        
        self.api = HfApi(token=HF_TOKEN)
        self.repo_id = HF_REPO_ID
        self.fs = HfFileSystem(token=HF_TOKEN)

        # Check if repo exists, if not create it (private by default to start)
        try:
            self.api.repo_info(repo_id=self.repo_id, repo_type="dataset")
        except Exception:
            print(f"⚠️  Repo {self.repo_id} not found. Creating it...")
            try:
                self.api.create_repo(repo_id=self.repo_id, repo_type="dataset", exist_ok=True)
                print(f"✅ Repo {self.repo_id} created.")
            except Exception as e:
                print(f"❌ Failed to create repo: {e}")
                self.api = None

    def upload_file(self, file_path: Path, object_name: str = None) -> str:
        """Upload a file to HF Dataset and return the public URL."""
        if not self.api:
            return None

        if object_name is None:
            object_name = file_path.name

        try:
            print(f"☁️  Uploading {file_path.name} to Hugging Face {self.repo_id}...")
            
            self.api.upload_file(
                path_or_fileobj=file_path,
                path_in_repo=object_name,
                repo_id=self.repo_id,
                repo_type="dataset"
            )
            
            # Construct public URL (resolve pointer if needed, but direct link usually works)
            # Standard HF Dataset URL pattern:
            # https://huggingface.co/datasets/{USER}/{REPO}/resolve/main/{PATH}
            url = f"https://huggingface.co/datasets/{self.repo_id}/resolve/main/{object_name}"
            
            print(f"✅ Uploaded: {url}")
            return url
            
        except FileNotFoundError:
            print(f"❌ The file was not found: {file_path}")
            return None
        except Exception as e:
            print(f"❌ Upload error: {e}")
            return None

    def upload_directory(self, directory: Path, prefix: str = "", commit_message: str = None) -> dict:
        """
        Recursively upload a directory to HF.
        Returns a dictionary mapping relative paths to public URLs.
        """
        if not self.api:
            return {}

        uploaded_files = {}
        
        # Ensure prefix ends with slash if not empty
        if prefix and not prefix.endswith('/'):
            prefix += '/'

        try:
            print(f"☁️  Uploading directory {directory} to {self.repo_id}/{prefix}...")
            
            self.api.upload_folder(
                folder_path=directory,
                path_in_repo=prefix,
                repo_id=self.repo_id,
                repo_type="dataset",
                commit_message=commit_message
            )
            
            # Generate URLs for all files
            for root, _, files in os.walk(directory):
                for file in files:
                    file_path = Path(root) / file
                    relative_path = file_path.relative_to(directory)
                    object_key = f"{prefix}{relative_path.as_posix()}"
                    url = f"https://huggingface.co/datasets/{self.repo_id}/resolve/main/{object_key}"
                    uploaded_files[str(relative_path)] = url
            
            print(f"✅ Directory uploaded successfully.")
            return uploaded_files

        except Exception as e:
            print(f"❌ Directory upload error: {e}")
            return {}
