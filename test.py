import luigi
from tasks import LikeLatest
# First follow, then unfollow
profile = 'pauuii'
credentials_file = 'credentials.json'

like_task = LikeLatest(credentials_file=credentials_file,
                       profile=profile)

luigi.build([like_task], local_scheduler=True)

