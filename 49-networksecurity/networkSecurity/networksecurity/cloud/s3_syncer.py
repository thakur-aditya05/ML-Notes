

# these are the few lines of the code to sync the local folder to the s3 bucket and vice versa
# used in the training pipeline to push the artifact and final model to the s3 bucket                                                   







import os


class S3Sync:
    def sync_folder_to_s3(self,folder,aws_bucket_url):
        command = f"aws s3 sync {folder} {aws_bucket_url} "
        os.system(command)

    def sync_folder_from_s3(self,folder,aws_bucket_url):
        command = f"aws s3 sync  {aws_bucket_url} {folder} "
        os.system(command)



# aws_bucket_url --->cloud folder path
# folder  ---> local folder path
# aws s3 sync this is the command folder name and aws bucket url to sync the folder from local to s3 bucket and vice versa
# os.system(command) ---> to run the command in the terminal from python script