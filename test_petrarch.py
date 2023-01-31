"""
Test 

Given a text, extract political entities from the text and print actors and event
Prerequisites: Docker run Petrarch and CoreNLP
"""


from entity_extraction import get_cameo_mappings, parse_sentence, tokenize, format_parsed_str, send_to_petr
import nltk

config_path = "config.ini"

map_dict = get_cameo_mappings(config_path)

STORYID = '10'

text = """
World Cup Captains Want To Wear Rainbow Armbands In Qatar. FIFA has come under pressure from several European soccer federations who want to support a human rights campaign against discrimination at the World Cup.

"""
# text="4 Russian-Controlled Ukrainian Regions Schedule Votes This Week To Join Russia. The concerted and quickening Kremlin-backed efforts to swallow up four regions could set the stage for Moscow to escalate the war."
# text = "Las Vegas Aces Win First WNBA Title, Chelsea Gray Named MVP. Las Vegas never had a professional sports champion — until Sunday."
DATE = '202209230908'

event_dict = {STORYID: {}}
event_dict[STORYID]['sents'] = {}
event_dict[STORYID]['meta'] = {}
event_dict[STORYID]['meta']['date'] = DATE

sentences = nltk.sent_tokenize(text)

for i, _ in enumerate(sentences):
    sent = sentences[i]
    event_dict[STORYID]['sents'][str(i)] = {}
    event_dict[STORYID]['sents'][str(i)]['content'] = ' '.join(tokenize(sent))
    corenlp_parsed = parse_sentence(sent)
    event_dict[STORYID]['sents'][str(i)]['parsed'] = format_parsed_str(corenlp_parsed)

event_updated = send_to_petr(event_dict)
# print("OUTPUT : ", event_updated)

info = event_updated[STORYID]['sents']['0']['meta']

#Get Goldstein score
if 'events' in event_updated[STORYID]['sents']['0']:
    event = event_updated[STORYID]['sents']['0']['events'][0]
    print("EVENT :", event)
    print("GOLDSTEIN SCORE :", map_dict[event[2]])


print("ACTORS: ", info['actorroot'])
print("WHAT HAPPENED: ", info['eventtext'])

