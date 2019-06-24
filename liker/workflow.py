import luigi
import random
import logging
from logging.config import dictConfig
import yaml
from liker.tasks import LikeLatest, GetFollowers
from liker import credentials_file


logger = logging.getLogger(__name__)


class RandomBatchFromAuthorities(luigi.WrapperTask):

    authority_profiles = luigi.Parameter()
    credentials_file = luigi.Parameter()

    def requires(self):
        authority_followers = [GetFollowers(
            credentials_file=self.credentials_file,
            profile=prof)
                               for prof in self.authority_profiles]

        return authority_followers

    def get_batch(self, k):
        # first gather followers
        all_followers = []
        for task in self.requires():
            all_followers.extend(task.get_followers())
        
        total_len = len(all_followers)
        if k > total_len:
            logger.warning('Trying to get {} followers from a list'
                           ' of length {}, reducing number'
                           .format(k, total_len))
            k = total_len
        sample = random.sample(all_followers, k)
        return sample


if __name__ == '__main__':
    authority_profiles = ['juliakbrou', 'datajackson_',
                          'sergilehkyi', 'likethereisnobox',
                          'robievilhelm', 'felipefenerich']

    number_profiles = 8

    batch_task = RandomBatchFromAuthorities(
        authority_profiles=authority_profiles,
        credentials_file=credentials_file)

    luigi.build([batch_task], local_scheduler=True, workers=1)

    profile_batch = batch_task.get_batch(number_profiles)
    like_tasks = [LikeLatest(credentials_file=credentials_file,
                             profile=acc)
                  for acc in profile_batch]
    luigi.build(like_tasks, local_scheduler=True, workers=1)
