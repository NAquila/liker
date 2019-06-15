import luigi
from luigi.util import inherits
import random
import logging
from logging.config import dictConfig
import yaml
from tasks import LikeLatest, GetFollowers


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
            all_followers.append(task.get_followers())
        
        total_len = len(all_followers)
        if k > total_len:
            logger.warning(f'Trying to get {k} followers from a list'
                           ' of length {total_len}, reducing number')
            k = total_len
        sample = random.sample(all_followers, k)
        return sample


@inherits(RandomBatchFromAuthorities)
class LikeMany(luigi.Task):

    number_profiles = luigi.IntParameter()
    is_complete = False

    def requires(self):
        # First make sure the all authorites have had there followers
        # read
        batch_task = self.clone(RandomBatchFromAuthorities)
        return batch_task
    def run(self):
        # Next, get the profiles
        batch_task = self.requires()
        profile_batch = batch_task.get_batch(self.number_profiles)
        like_tasks = [LikeLatest(credentials_file=self.credentials_file,
                                 profile=acc)
                      for acc in profile_batch]
        for task in like_tasks:
            yield task
        self.is_complete = True
        
    def complete(self):
        return self.is_complete
        
        
if __name__ == '__main__':
    # logging_config = 'logging_config.yaml'
    # with open(logging_config, 'r') as f:
    #     logging_dict = yaml.safe_load(f)
    # dictConfig(logging_dict)
    authority_profiles = ['juliakbrou', 'datajackson_',
                          'sergilehkyi', 'likethereisnobox',
                          'robievilhelm', 'erikgeddaa',
                          'felipefenerich']
    authority_profiles = ['erikgeddaa',
                          'felipefenerich']

    number_profiles = 10
    

    credentials_file = './credentials.json'

    like_many = LikeMany(authority_profiles=authority_profiles,
                         credentials_file=credentials_file,
                         number_profiles=number_profiles)

    luigi.build([like_many], local_scheduler=True, workers=1)
                           
                           
