import os
import json
import numpy as np
import pylab as pl
import datetime
import operator

CURRENT_DIRECTORY = os.getcwd()
#analyze this many chats
NUMBER_TO_ANALYZE = 1000
#a chat must have this many messages to be analyzed
MESSAGE_THRESHOLD = 20

def get_json_data(chat):
    try:
        json_location = CURRENT_DIRECTORY + "/messages/" + chat + "/message.json"
        with open(json_location) as json_file:
            json_data = json.load(json_file)
            return json_data
    except IOError:
        pass # some things the directory aren't messages (DS_Store, stickers_used, etc.)

#chats is a list of the names of the chats
chats = os.listdir(CURRENT_DIRECTORY + "/messages")[:NUMBER_TO_ANALYZE]
#sorted_chats is a list of tuples which include all information about each chat
sorted_chats = []
#maps from chat index to dicts of each person and how many msgs they sent
final_data_messages = {}
#maps from chat index to dicts of each person and how many times of the msgs they sent
final_data_times = {}
#maps from chat index to dicts of each person and words per msg they sent
final_data_words = {}
#maps from chat index to dicts of each person and most common words used
final_data_content = {}
invalid_message_count = 0

print('Analyzing ' + str(len(chats)) + ' chats...')

for chat in chats:
    json_data = get_json_data(chat)
    if json_data != None:
        messages = json_data["messages"]
        if len(messages) >= MESSAGE_THRESHOLD:
            sorted_chats.append((len(messages), chat, messages))

#list of tuples with #msgs in chat, name of chat, all chat info
sorted_chats.sort(reverse=True)

print('Finished processing chats...')

for i, (messages, chat, messages) in enumerate(sorted_chats):
    number_messages = {}
    person_to_times = {}
    number_words = {}
    chat_content = {}

    print(str(i) + " - " + str(len(messages)) + " messages - " + str(chat))

    for message in messages:
        try:
            name = message["sender_name"]
            time = message["timestamp_ms"]
            message_content = message["content"]

            number_messages[name] = number_messages.get(name, 0)
            number_messages[name] += 1

            person_to_times[name] = person_to_times.get(name, [])
            person_to_times[name].append(datetime.datetime.fromtimestamp(time/1000.0))

            number_words[name] = number_words.get(name, [])
            number_words[name].append(len(message_content.split()))
            
            for word in message_content.split():
                chat_content[word] = chat_content.get(word, 0)
                chat_content[word] += 1
            
            
        except KeyError:
            # happens for special cases like users who deactivated, unfriended, blocked
            invalid_message_count += 1
    
    final_data_messages[i] = number_messages
    final_data_times[i] = person_to_times
    final_data_words[i] = number_words
    final_data_content[i] = chat_content

print('Found ' + str(invalid_message_count) + ' invalid messages...')
print('Found ' + str(len(sorted_chats)) + ' chats with ' + str(MESSAGE_THRESHOLD) + ' messages or more')

def plot_num_messages(chat_number):
    plotted_data = final_data_messages[chat_number]
    X = np.arange(len(plotted_data))
    pl.bar(X, list(plotted_data.values()), align='center', width=0.5, color = 'r', bottom = 0.3)
    pl.xticks(X, plotted_data.keys(), rotation = 90)
    pl.title('Number of Messages Sent')
    pl.tight_layout()
    pl.show()

def plot_histogram_time(chat_number):
    person_to_times = final_data_times[chat_number]
    pl.xlabel('Time')
    pl.ylabel('Number of Messages')
    pl.title('# of Messages Over Time')
    colors = ['b', 'r', 'c', 'm', 'y', 'k', 'w', 'g']
    for i , person in enumerate(person_to_times):
        plotted_data = person_to_times[person]
        pl.hist(plotted_data, 100, alpha=0.3, label=person, facecolor=colors[i % len(colors)])
    pl.legend()
    pl.xticks(rotation=90)
    pl.tight_layout()
    pl.show()

def plot_histogram_words(chat_number):
    temp = {}
    for person in final_data_words[chat_number]:
        temp[person] = np.average(final_data_words[chat_number][person])
    plotted_data = temp
    X = np.arange(len(plotted_data))
    pl.bar(X, list(plotted_data.values()), align='center', width=0.5, color = 'r', bottom = 0.3)
    pl.xticks(X, plotted_data.keys(), rotation = 90)
    pl.title('Average Word Count')
    pl.tight_layout()
    pl.show()
    
def plot_time_of_day(chat_number):
    times = {'Morning' : 0, 'Afternoon' : 0, 'Evening':  0, 'Night' : 0}
    for person in final_data_times[chat_number]:
        for time in final_data_times[chat_number][person]:
            if time.hour >= 0 and time.hour < 6:
                times['Morning'] += 1
            if time.hour >= 6 and time.hour < 12:
                times['Afternoon'] += 1
            if time.hour >= 12 and time.hour < 18:
                times['Evening'] += 1
            else:
                times['Night'] += 1
    X = np.arange(len(times))
    pl.bar(X, list(times.values()), align='center', width=0.5, color = 'r', bottom = 0.3)
    pl.xticks(X, times.keys(), rotation = 90)
    pl.title('Number of Messages')
    pl.tight_layout()
    pl.show()

def plot_most_common_words(chat_number):
    sorted_words = sorted(final_data_content[chat_number].items(), key=lambda x: x[1], reverse = True)
    sorted_words = sorted_words[:10]
    most_common_words = dict(sorted_words)
    X = np.arange(len(most_common_words))
    pl.bar(X, list(most_common_words.values()), align='center', width=0.5, color = 'r', bottom = 0.3)
    pl.xticks(X, most_common_words.keys(), rotation = 90)
    pl.title('Number of Messages')
    pl.tight_layout()
    pl.show()
  
    
def plot(chat_number):
    plot_num_messages(chat_number)
    plot_histogram_time(chat_number)
    plot_histogram_words(chat_number)
    plot_time_of_day(chat_number)
    plot_most_common_words(chat_number)
    
plot(4)