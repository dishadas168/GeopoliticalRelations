import json
import os
import sys
import logging
from models import EventDict
from petrarch2 import petrarch2


cwd = os.path.abspath(os.path.dirname(__file__))

config = petrarch2.utilities._get_data('data/config/','PETR_config.ini')
petrarch2.PETRreader.parse_Config(config)
petrarch2.read_dictionaries()

# # Prevent multiprocessing warning in AWS logs
# warnings.filterwarnings(action='ignore')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):

    events_data = event #type dict
    logger.info('Received request body: {}'.format(events_data))

    # Check features are provided
    if "body" not in events_data.keys():
        return {
            "statusCode": 400,
            "body": json.dumps(
                {
                    "message": "Invalid request. Missing parameters in body",
                }
            )
        }
    else:
        response = get_event_data(event['body'])
        logger.info('Received request body: {}'.format(response))
        return {
            "statusCode": 200,
            "body" : json.dumps(response).encode('utf8')
        }

        

def get_event_data(events: EventDict):
    event_dict = events["events"]

    try:
        event_dict_updated = petrarch2.do_coding(event_dict)
    except Exception as e:
        logger.info("An error occurred with PETR. {}\n".format(e))
        event_dict_updated = event_dict

    story_id = str(list(event_dict_updated.keys())[0])

    if not event_dict_updated[story_id]['sents']:
        return event_dict_updated

    for sent in event_dict_updated[story_id]["sents"]:
        sent = str(sent)
        try:
            temp_meta = event_dict_updated[story_id]["sents"][sent]["meta"]
        except:
            continue

        try:
            temp_meta["actortext"] = list(temp_meta["actortext"].values())
        except:
            temp_meta["actortext"] = [[]]
        try:
            temp_meta["eventtext"] = list(temp_meta["eventtext"].values())
        except:
            temp_meta["eventtext"] = [[]]
        try:
            temp_meta["actorroot"] = list(temp_meta["actorroot"].values())
        except:
            temp_meta["actorroot"] = [[]]
        try:
            temp_meta["nouns"] = temp_meta["nouns"]
        except:
            temp_meta["nouns"] = []

        #Removing event tuples as we don't need them
        to_be_deleted = []
        for key in event_dict_updated[story_id]["sents"][sent]["meta"].keys():
            if key not in ["nouns", "actorroot", "eventtext", "actortext"]:
                to_be_deleted.append(key)

        for key in to_be_deleted:
            del event_dict_updated[story_id]["sents"][sent]["meta"][key]

    return event_dict_updated


