#импортируем модули
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pymongo

#присоединяемся к монго и спотифай
client = pymongo.MongoClient("mongodb+srv://Pavel:aig4Chei@cluster0.kye1d.mongodb.net/charts?retryWrites=true&w=majority")
#db = client.test
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

mydb = client['songs']
mycol = mydb['songs1']

#первые буквы для запроса
letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N",
           "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]


a = 0
id_list = []
#errors = 0
#отправляем запросы, комбинируя первые две буквы
while a<len(letters):
    b = 0
    while b<len(letters):
        results = sp.search(q=letters[a] + letters[b] + '*', type="track")
        for result in results['tracks']['items']:
            track_id = result['uri']
            label = sp.album(result['album']['uri'])['label']
            popularity = result['popularity']
            duration = result['duration_ms']
            if result['explicit'] == False:
                track_explicit = 0
            else: track_explicit = 1
            features = sp.audio_features(track_id)
            if type(features[0]) == dict:
                track_acousticness = features[0]['acousticness']
                track_danceability = features[0]['danceability']
                track_energy = features[0]['energy']
                track_instrumentalness = features[0]['instrumentalness']
                #track_key = str(features[0]['key'])
                track_liveness = features[0]['liveness']
                track_loudness = features[0]['loudness']
                track_mode = features[0]['mode']
                track_speechiness = features[0]['speechiness']
                track_tempo = features[0]['tempo']
                track_valence = features[0]['valence']
                my_dict = {"id": track_id, "label": label, "popularity": popularity, "duration": duration, "acousticness": track_acousticness, 'danceability': track_danceability, 'energy': track_energy, 'instrumentalness': track_instrumentalness, 'liveness': track_liveness, 'loudness': track_loudness, 'mode': track_mode, 'speechiness': track_speechiness, 'tempo': track_tempo, 'valence': track_valence, 'explicit': track_explicit}
                if my_dict['id'] not in id_list:
                    k = mycol.insert_one(my_dict)
                    id_list.append(my_dict['id'])
        b += 1
        print(b*10)
    a += 1
    print(a*26*10)
    
    
    