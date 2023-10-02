# __________                  __             __     ________             .___ 
# \______   \  ____    ____  |  | __  ____ _/  |_  /  _____/   ____    __| _/ 
#  |       _/ /  _ \ _/ ___\ |  |/ /_/ __ \\   __\/   \  ___  /  _ \  / __ |  
#  |    |   \(  <_> )\  \___ |    < \  ___/ |  |  \    \_\  \(  <_> )/ /_/ |  
#  |____|_  / \____/  \___  >|__|_ \ \___  >|__|   \______  / \____/ \____ |  
#         \/              \/      \/     \/               \/              \/  
#
# Rekognition photo analysis and face comparison Discord bot by RocketGod
# https://github.com/RocketGod-git/rekognition-bot

import os
import json
import discord
import boto3
from discord import Embed
import asyncio
import logging

logging.basicConfig(level=logging.DEBUG)

# Load keys from config.json
with open("config.json", "r") as file:
    config = json.load(file)
    TOKEN = config["TOKEN"]
    ACCESS_KEY = config["AWS_ACCESS_KEY"]
    SECRET_KEY = config["AWS_SECRET_KEY"]

# Ensure the photos directory exists
if not os.path.exists('./photos'):
    os.makedirs('./photos')


# ------ Functions for Image Analysis and Comparison ------


def load_image_bytes(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return image_file.read()
    except Exception as e:
        print(f"Error reading image: {e}")
        return None

def analyze_image(image_bytes, access_key, secret_key):
    client = boto3.client('rekognition', 
                          aws_access_key_id=access_key,
                          aws_secret_access_key=secret_key,
                          region_name='us-west-1')

    response_labels = client.detect_labels(Image={'Bytes': image_bytes})
    response_celebs = client.recognize_celebrities(Image={'Bytes': image_bytes})
    response_faces = client.detect_faces(Image={'Bytes': image_bytes}, Attributes=['ALL'])
    response_text = detect_text_in_image(image_bytes, access_key, secret_key)
    
    return response_labels, response_celebs, response_faces, response_text

def compare_faces_in_images(source_bytes, target_bytes, access_key, secret_key):
    client = boto3.client('rekognition', 
                          aws_access_key_id=access_key,
                          aws_secret_access_key=secret_key,
                          region_name='us-west-1')

    response = client.compare_faces(
        SourceImage={'Bytes': source_bytes},
        TargetImage={'Bytes': target_bytes}
    )
    return response

def detect_text_in_image(image_bytes, access_key, secret_key):
    client = boto3.client('rekognition', 
                          aws_access_key_id=access_key,
                          aws_secret_access_key=secret_key,
                          region_name='us-west-1')
    
    response = client.detect_text(Image={'Bytes': image_bytes})
    return response


# ------ Function to process the API response and create the embed for Discord ------


def build_embed(**data):
    embed = Embed(title="Photo Results")

    # Process Face Details (common for both comparison and analysis)
    face_details = data.get('FaceDetails', [])
    if face_details:
        face_detail = face_details[0]  # We'll focus on the first face for simplicity. Adjust as needed.
        
        # Gender & Age Range
        gender = face_detail.get('Gender', {}).get('Value', 'Unknown')
        gender_confidence = face_detail.get('Gender', {}).get('Confidence', 0)
        age_range = f"{face_detail.get('AgeRange', {}).get('Low', 'Unknown')} - {face_detail.get('AgeRange', {}).get('High', 'Unknown')}"
        embed.add_field(name="Gender", value=f"{gender} (Confidence: {gender_confidence:.2f}%)")
        embed.add_field(name="Age Range", value=age_range)
        
        # Emotions
        emotions = '\n'.join([f"{emotion.get('Type')} ({emotion.get('Confidence', 0):.2f}%)" for emotion in face_detail.get('Emotions', [])])
        if emotions:
            embed.add_field(name="Emotions", value=emotions)

        # Attributes: Sunglasses, Eyeglasses, Beard, Mustache, Smile
        attributes = []
        for attribute in ['Sunglasses', 'Eyeglasses', 'Beard', 'Mustache', 'Smile']:
            value = face_detail.get(attribute, {}).get('Value', False)
            confidence = face_detail.get(attribute, {}).get('Confidence', 0)
            attributes.append(f"{attribute}: {'Yes' if value else 'No'} (Confidence: {confidence:.2f}%)")
        embed.add_field(name="Attributes", value='\n'.join(attributes))

    # Process labels (for analysis)
    labels = ', '.join([label['Name'] for label in data.get('Labels', [])])
    if labels:
        embed.add_field(name="Objects Detected", value=labels)

    # Process celebrities (for analysis)
    celebrities = ', '.join([celebrity['Name'] for celebrity in data.get('CelebrityFaces', []) if 'Name' in celebrity])
    if celebrities:
        embed.add_field(name="Celebrities", value=celebrities)

    # Process Face Match Status and Similarity
    face_match_status = data.get('FaceMatchStatus')
    similarity = data.get('Similarity')
    if face_match_status:
        embed.add_field(name="Match Status", value=face_match_status)
    if similarity:
        embed.add_field(name="Similarity", value=similarity)

    # Process detected text
    detected_texts = ', '.join([text['DetectedText'] for text in data.get('TextDetections', [])])
    if detected_texts:
        embed.add_field(name="Detected Text", value=detected_texts[:1024])  # Limit to 1024 characters for a field value in Discord embed

    return embed


# ------ Discord bot ------


class RekognitionClient(discord.Client):
    def __init__(self) -> None:
        super().__init__(intents=discord.Intents.default())
        self.rekognition = boto3.client('rekognition', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY, region_name='us-west-1')
        self.tree = discord.app_commands.CommandTree(self)
        self.activity = discord.Activity(type=discord.ActivityType.watching, name="faces")

    async def handle_errors(self, interaction, error, error_type="Error"):
        # Log the error to the terminal
        print(f"{error_type}: {error}")
        
        error_message = f"{error_type}: {error}"
        embed = Embed(description=error_message, color=0xFF0000)
        await interaction.followup.send(embed=embed)

    @property
    def tree(self):
        return self._tree

    @tree.setter
    def tree(self, value):
        self._tree = value

def run_rekognition_bot(token):
    client = RekognitionClient()

    @client.event
    async def on_ready():
        await client.tree.sync()
        print(f'{client.user} is connected!')
        await client.change_presence(activity=client.activity)

    @client.tree.command(
        name="photos",
        description="Analyze a photo or optionally compare faces in two photos."
    )
    async def photos(interaction: discord.Interaction, first_photo: discord.Attachment, second_photo: discord.Attachment = None):
        try:
            await interaction.response.defer(ephemeral=False)

            if not first_photo:
                raise ValueError("You must attach at least one photo.")

            first_photo_path = f"./photos/{first_photo.filename}" 
            await first_photo.save(fp=first_photo_path)
            await asyncio.sleep(1)
            first_image_bytes = load_image_bytes(first_photo_path)

            files_to_send = [discord.File(first_photo_path)]

            if second_photo:
                second_photo_path = f"./photos/{second_photo.filename}"  
                await second_photo.save(fp=second_photo_path)
                await asyncio.sleep(1)
                second_image_bytes = load_image_bytes(second_photo_path)

                files_to_send.append(discord.File(second_photo_path))

                # Check for None bytes
                if first_image_bytes is None or second_image_bytes is None:
                    raise ValueError("Failed to read image bytes.")

                comparison_response = compare_faces_in_images(first_image_bytes, second_image_bytes, ACCESS_KEY, SECRET_KEY)
                
                # Check if 'FaceMatches' in comparison_response has values.
                if comparison_response.get('FaceMatches'):
                    face_match = comparison_response['FaceMatches'][0]
                    similarity = face_match['Similarity']
                else:
                    # No matches found.
                    similarity = 0

                # Building embed data based on similarity.
                if similarity > 90:  # this threshold can be adjusted
                    match_status = "Likely the same person"
                else:
                    match_status = "Likely different people"
                
                embed_data = {
                    'FaceMatchStatus': match_status,
                    'Similarity': f"{similarity:.2f}%"
                }

            else:
                labels, celebrities, faces, texts = analyze_image(first_image_bytes, ACCESS_KEY, SECRET_KEY)
                embed_data = {
                    'Labels': labels['Labels'],
                    'CelebrityFaces': celebrities['CelebrityFaces'],
                    'FaceDetails': faces['FaceDetails'],
                    'TextDetections': texts['TextDetections'] 
                }

            await interaction.followup.send(files=files_to_send)  
            embed = build_embed(**embed_data)
            await interaction.followup.send(embed=embed)

        except boto3.exceptions.Boto3Error as boto_error:
            await client.handle_errors(interaction, str(boto_error), "AWS Service Error")
        except Exception as e:
            await client.handle_errors(interaction, str(e))

    client.run(token)

if __name__ == "__main__":
    run_rekognition_bot(TOKEN)
