from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from googleplaces import GooglePlaces, types
import streamlit as st
import folium
from streamlit_chat import message
from tensorflow.keras.models import load_model
import joblib
from deep_translator import GoogleTranslator
import tensorflow as tf
import wikipedia
from precautions import precautions
from disease_symptoms import dataset
from langdetect import detect
from models import entity_indentification_model, disease_finding_tokenizer, disease_model, id_to_label

from conversational_classifier import ConversationalClassifier

# entity_indentification_tokenizer = joblib.load('entity_identification_tokenizer.joblib')
# disease_finding_tokenizer = joblib.load('disease_finding_tokenizer.joblib')
# entity_indentification_model = load_model('entity_detection_model')
# disease_model = load_model('tensorflow_model')
# id_to_label = joblib.load('id_to_label.joblib')


locator = Nominatim(user_agent='Geopy Library')
API_KEY = 'AIzaSyCCO2d1ACM_ZpUZYrNP2qstF568e5kgzIc'
google_places = GooglePlaces(API_KEY)

classifier = ConversationalClassifier()


# Location Part

if 'mapper' not in st.session_state:
    st.session_state['mapper'] = []

if 'language' not in st.session_state:
    st.session_state['language'] = 'en'

@st.cache_data()
def get_location_latitude_longitude(location_name, button_state):
    if button_state:
        getLoc = locator.geocode(location_name)
        print(getLoc.address)
        return getLoc.latitude, getLoc.longitude

@st.cache_data()
def find_hospital(latitude, longitude, button_state):
    if button_state:
        query_result = google_places.nearby_search(
            lat_lng={'lat': latitude, 'lng': longitude},
            radius=2500,
            types=[types.TYPE_HOSPITAL]
        )

        place_lat, place_lng, place_name = 0, 0, ''

        for place in query_result.places:
            place_name = place.name
            place_lat = place.geo_location['lat']
            place_lng = place.geo_location['lng']
            break

        st.session_state['mapper'] = [place_lat, place_lng, place_name]
        print("Mapper Updated:", st.session_state['mapper'])
        return place_lat, place_lng, place_name


# Chat Part

def get_text():
    input_text = st.text_input("You: ", placeholder="Enter your message here", key="input")
    return input_text

# def disease_from_symptoms(text):
#     tokens = disease_finding_tokenizer.texts_to_sequences([text])
#     padded_tokens = tf.keras.preprocessing.sequence.pad_sequences(tokens, maxlen=4)
#     prediction = disease_model.predict(padded_tokens)
#     predicted_id = tf.argmax(prediction).numpy()[0]
#     predicted_label = id_to_label[predicted_id]
#     return predicted_label

# def match_disease(symptoms):
#     for disease, disease_symptoms in dataset.items():
#         if set(symptoms) == set(disease_symptoms):
#             print(disease)
#             return disease

def find_disease(sentence):
    matched_diseases = []

    # Convert the sentence to lowercase for case-insensitive comparison
    sentence = sentence.lower()
    # print(sentence)
    # Iterate through each disease and its symptoms in the dataset
    for disease, symptoms in dataset.items():
        print(sentence)
        # Count the number of symptoms present in the sentence
        matched_symptoms = sum(symptom.lower() in sentence for symptom in symptoms)

        # If at least three symptoms are matched, consider it a potential match
        if matched_symptoms >= 3:
            matched_diseases.append(disease)
    try:
        if matched_diseases:
            return matched_diseases[0]
        else:
            print("No disease found based on symptoms.")
    except IndexError as e:
        return str(e)

    # return matched_diseases[0]

def identify_entity(text):
    tokens = entity_indentification_tokenizer.texts_to_sequences([text])
    padded_tokens = tf.keras.preprocessing.sequence.pad_sequences(tokens, maxlen=4)
    prediction = entity_indentification_model(padded_tokens)
    if prediction[0][0] > prediction[0][1]:
        return 'disease'
    else:
        return 'symptoms'

def process_input(text, target_language):
    translated_text = GoogleTranslator(source='auto', target='en').translate(text)
    disease_or_symptoms = identify_entity(translated_text)
    print(disease_or_symptoms)
    disease = ''
    if disease_or_symptoms == 'symptoms':
        disease = find_disease(translated_text)
        print(disease)
        if disease:
            print(disease)
            get_details_and_precaution = f"The predicted Disease is {disease}. " + precautions[disease]
        else:
            get_details_and_precaution = "No specific disease found based on the given symptoms and try with more symptoms"
        # get_details_and_precaution = f"The predicted Disease is {disease}. "+precautions[disease]
    else:
        disease = translated_text.strip().split(' ')[-1]
        print(disease)
        if disease:
            get_details_and_precaution = wikipedia.summary(disease)
        else:
            print("hii")
    if(get_details_and_precaution):
        print(get_details_and_precaution)
    else:
        print("please try with other name")
    re_translate_response = GoogleTranslator(source='auto', target = target_language).translate(get_details_and_precaution[:4997])
    return re_translate_response

# def get_response(text, language):
#     # response = process_input(text, language)
#     # return response
#     classification_result = classifier.classify_text(text)

#     if classification_result != "Unknown":
#         return classification_result

#     # Continue with the previous logic for medical-related responses
#     response = process_input(text, language)
#     return response
def get_response(user_input, target_language):
    # Detect the language of the user's input
    input_language = detect(user_input)

    # Translate the user's input to English if it's not already in English
    if input_language != 'en':
        translated_input = GoogleTranslator(source=input_language, target='en').translate(user_input)
    else:
        translated_input = user_input

    # Classify the translated input using ConversationalClassifier
    classification_result = classifier.classify_text(translated_input)

    if classification_result != "Unknown":
        # Translate the classification result to the desired language
        translated_result = GoogleTranslator(source='en', target=target_language).translate(classification_result)
        return translated_result

    # Continue with the previous logic for medical-related responses
    response = process_input(translated_input, target_language)

    # Translate the medical-related response to the desired language
    translated_response = GoogleTranslator(source='en', target=target_language).translate(response)
    return translated_response


st.title('Medical Chatbot')

language = st.selectbox("Select Language: ", ['english', 'hindi', 'telegu'])
language_btn = st.button('Update Language', key='Lang BTN')

if language_btn:
    st.session_state['language'] = 'en' if language == 'english' else 'hi' if language == 'hindi' else 'te'
    st.success(f'language updated to {st.session_state["language"]}')

place_input = st.text_input('Enter Location Name: ')
place_input_btn = st.button('Search hospital', key='place_input_btn')

if 'generated' not in st.session_state:
    st.session_state.generated = []
    st.session_state.generated.append('Hi')

if 'past' not in st.session_state:
    st.session_state.past = []

if st.session_state.generated:
    for i in range(0, len(st.session_state.generated)):
        message(st.session_state.generated[i], key=str(i))
        try:
            message(st.session_state.past[i], is_user=True, key=str(i) + '_user')
        except:
            pass

user_input = get_text()
user_btn = st.button('Send', key='user_input_btn')

if user_btn:
    try:
        st.session_state.past.append(user_input)
        response = get_response(user_input, st.session_state['language'])
        st.session_state.generated.append(response + '...')
    # st.rerun()
        st.experimental_rerun()
    except Exception as e:
        st.session_state.generated.append("Please tr with other name")
        


if place_input_btn:
    try:
        lat, lng = get_location_latitude_longitude(place_input, place_input_btn)
        hsp_lat, hsp_lng, hsp_name = find_hospital(lat, lng, place_input_btn)
    except:
        pass

if 'mapper' in st.session_state and len(st.session_state['mapper']) == 3:
    m = folium.Map(location=[st.session_state['mapper'][0], st.session_state['mapper'][1]], zoom_start=15)
    st_folium(m, width=600)


