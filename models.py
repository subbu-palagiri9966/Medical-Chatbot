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

entity_indentification_tokenizer = joblib.load('entity_identification_tokenizer.joblib')
disease_finding_tokenizer = joblib.load('disease_finding_tokenizer.joblib')
entity_indentification_model = load_model('entity_detection_model')
disease_model = load_model('tensorflow_model')
id_to_label = joblib.load('id_to_label.joblib')