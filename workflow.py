import luigi
import random
import logging
import json
from tasks import LikeLatest


logger = logging.getLogger(__name__)


class RandomBatchFromAuthorities(luigi.WrapperTask):

    authority_accounts = luigi.Parameter()
    credentials_file = luigi.Parameter()

    def requires(self):
        authority_followers = [GetFollowers(
            credentials_file=self.credentials_file,
            account=acc)
                               for acc in self.authority_accounts]

        return authority_followers

    def get_batch(self, k):
        # first gather followers
        all_followers = [*task.get_followers()
                         for task in self.requires()]
        total_len = len(all_followers)
        if k > total_len:
            logger.warning(f'Trying to get {k} followers from a list'
                           ' of length {total_len}, reducing number')
            k = total_len
        sample = random.sample(all_followers, k)
        return sample


@inherits(RandomBatchFromAuthorities)
class LikeMany(luigi.WrapperTask):

    number_accounts = luigi.IntParameter()

    def requires(self):
        # First make sure the all authorites have had there followers
        # read
        batch_task = self.clone(RandomBatchFromAuthorities)
        yield batch_task
        # Next, get the accounts
        account_batch = batch_job.get_batch(self.number_accounts)
        like_tasks = [LikeLatest(credentials_file=self.credentials_file,
                                 profile=acc)
                      for acc in account_batch]
        return like_tasks
        
        
if __name__ == '__main__':
    logging_config = 'logging.json'
    with open(logging_config, 'r') as f:
        logging_dict = json.load(f)
    logging.dictConfig(logging_dict)
    authority_accounts = ['juliakbrou', 'datajackson_',
                          'sergilehkyi', 'likethereisnobox',
                          'robievilhelm', 'erikgeddaa',
                          'felipefenerich']
    number_accounts = 10

    credentials_file = './credentials.json'

    like_many = LikeMany(authority_accounts=authority_accounts,
                         credentials_file=credentials_file,
                         number_accounts=number_accounts)

    luigi.build([like_many], local_scheduler=True, workers=1)
                           
                           
