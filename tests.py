from TikTokApi import TikTokApi
import pandas as pd
from timeit import default_timer as timer

verifyFp = 'verify_kvfvyfh1_273CrYie_8lVQ_4p5v_BN6J_S3zGN19jmYWI'

api = TikTokApi.get_instance(custom_verifyFp=verifyFp, use_test_endponts = True)

