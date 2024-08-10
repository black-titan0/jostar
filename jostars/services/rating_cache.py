import math

from Jostar import settings
from proxies.redis import RedisProxy


def get_rating_weight(jostar_id):
    rating_weight_redis_key = f"jrw:{jostar_id}"
    number_of_ratings_in_past_hour = \
        RedisProxy.get_cached_value(rating_weight_redis_key)
    if number_of_ratings_in_past_hour:
        n = int(number_of_ratings_in_past_hour)
        RedisProxy.increment_key(key=rating_weight_redis_key)
        weight = ((1 / (math.exp(settings.RATING_WEIGHT_DOWNGRADING_FACTOR * (n - settings.
                                                                              MAX_NORMAL_RATING_COUNT_IN_ONE_HOUR)))) / settings.
                  RATING_WEIGHT_NORMALIZER_FACTOR)
        return weight
    else:
        RedisProxy.cache_with_ttl(key=rating_weight_redis_key, value=1, ttl=60 * 60)
        return 1


def get_should_effect_average(share_token):
    if share_token:
        share_token_redis_key = f"stc:{share_token}"
        number_of_ratings_from_this_share_link = \
            RedisProxy.get_cached_value(share_token_redis_key)
        if number_of_ratings_from_this_share_link:
            number_of_ratings_from_this_share_link = int(number_of_ratings_from_this_share_link)
            RedisProxy.increment_key(key=share_token_redis_key)
            if number_of_ratings_from_this_share_link > settings.MAX_NORMAL_RATING_FROM_SAME_SHARE_LINK:
                return False
        else:
            RedisProxy.cache_with_ttl(key=share_token_redis_key, value=1, ttl=60 * 60)
    return True
