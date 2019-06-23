import luigi
from liker import credentials_file
from liker.tasks import LikeLatest


def test_tasks():
    profile = 'donnid28'
    like_task = LikeLatest(credentials_file=credentials_file,
                           profile=profile)
    return [like_task]


if __name__ == '__main__':
    luigi.build(test_tasks(), local_scheduler=True)

